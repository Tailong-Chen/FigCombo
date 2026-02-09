#!/usr/bin/env python3
"""
FigCombo Flask API Backend

A comprehensive REST API for the FigCombo scientific figure composition tool.
Provides endpoints for layout management, plot types, figure generation,
asset handling, and project management.
"""

import os
import sys
import json
import base64
import io
import uuid
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from functools import wraps

# Add parent directory to path to import figcombo
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_file, send_from_directory, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# FigCombo imports
from figcombo import (
    Figure, ImagePanel, PlotPanel, TextPanel,
    list_templates, list_plot_types, register_plot_type
)
from figcombo.panels.plot_panel import get_plot_type, _PLOT_TYPE_REGISTRY
from figcombo.layout.parser import parse_ascii_layout, layout_from_explicit
from figcombo.layout.types import LayoutGrid, PanelPosition
from figcombo.knowledge.journal_specs import JOURNAL_SPECS, get_journal_spec, list_journals
from figcombo.knowledge.layout_templates import (
    LAYOUT_TEMPLATES, get_template, get_templates_by_category, get_nature_templates
)
from figcombo.knowledge.validators import (
    validate_figure, ValidationReport, Severity,
    validate_colorblind_friendly, validate_font_size, validate_dpi,
    validate_file_size, validate_panel_spacing, get_recommendations
)
from figcombo.export import save_figure, save_for_journal, FORMAT_DEFAULTS

# Import advanced layout parser
try:
    from layout_parser import LayoutCodeParser, LayoutTree
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    ADVANCED_PARSER_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent / 'outputs'
PROJECT_FOLDER = Path(__file__).parent / 'projects'
CODE_FOLDER = Path(__file__).parent / 'code_uploads'

# Create directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, PROJECT_FOLDER, CODE_FOLDER]:
    folder.mkdir(exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB upload limit
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.gif', '.bmp', '.webp'}
ALLOWED_CODE_EXTENSIONS = {'.py', '.txt', '.json', '.yaml', '.yml'}

# In-memory session storage (use Redis/database in production)
sessions = {}


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file has an allowed extension."""
    return Path(filename).suffix.lower() in allowed_extensions


def generate_id() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8]


def create_error_response(message: str, status_code: int = 400, details: dict = None) -> tuple:
    """Create a standardized error response."""
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    if details:
        response['details'] = details
    return jsonify(response), status_code


def create_success_response(data: dict = None, message: str = None) -> dict:
    """Create a standardized success response."""
    response = {
        'success': True,
        'timestamp': datetime.now().isoformat()
    }
    if message:
        response['message'] = message
    if data:
        response.update(data)
    return response


def fig_to_base64(fig, dpi: int = 150, format: str = 'png') -> str:
    """Convert matplotlib figure to base64 encoded string."""
    buf = io.BytesIO()
    # Use higher quality settings
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none',
                pil_kwargs={'quality': 95} if format == 'jpeg' else {})
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64


def get_plot_type_schema(plot_type_name: str) -> dict:
    """Extract JSON schema-like info from a plot type function."""
    import inspect

    try:
        func = get_plot_type(plot_type_name)
        sig = inspect.signature(func)

        parameters = []
        required = []

        for name, param in sig.parameters.items():
            if name == 'ax':
                continue

            param_info = {
                'name': name,
                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'any',
                'default': None
            }

            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
            else:
                required.append(name)

            parameters.append(param_info)

        # Get docstring for description
        doc = inspect.getdoc(func) or ""
        description = doc.split('\n')[0] if doc else f"{plot_type_name} plot"

        return {
            'name': plot_type_name,
            'description': description,
            'parameters': parameters,
            'required': required
        }
    except Exception as e:
        return {
            'name': plot_type_name,
            'description': f"Error loading schema: {str(e)}",
            'parameters': [],
            'required': []
        }


# =============================================================================
# Layout Endpoints
# =============================================================================

@app.route('/api/layout/parse', methods=['POST'])
def parse_layout():
    """
    POST /api/layout/parse

    Parse ASCII layout code to a structured tree representation.

    Request body:
        {
            "layout": "aab\\nccd"  // ASCII art layout string
        }

    Returns:
        {
            "success": true,
            "grid": {
                "nrows": 2,
                "ncols": 3,
                "panels": {
                    "a": {"row": 0, "col": 0, "rowspan": 1, "colspan": 2},
                    "b": {"row": 0, "col": 2, "rowspan": 1, "colspan": 1},
                    ...
                }
            }
        }
    """
    try:
        data = request.get_json()
        if not data or 'layout' not in data:
            return create_error_response("Missing 'layout' field in request body")

        layout_str = data['layout']

        # Try advanced parser first (supports named sections, sub-panels, insets)
        if ADVANCED_PARSER_AVAILABLE and ('[' in layout_str or '{' in layout_str or '<' in layout_str):
            parser = LayoutCodeParser()
            tree = parser.parse(layout_str)
            # Convert tree to grid format for frontend compatibility
            grid_data = tree.to_dict()
            # Extract panels from tree structure
            panels_dict = {}
            max_row, max_col = 0, 0

            def extract_panels(node, row_offset=0, col_offset=0):
                """Recursively extract panels from tree."""
                nonlocal max_row, max_col
                node_type = node.get('node_type')

                if node_type == 'panel':
                    label = node.get('id', '')
                    row = node.get('row', 0)
                    col = node.get('col', 0)
                    rowspan = node.get('rowspan', 1)
                    colspan = node.get('colspan', 1)
                    panels_dict[label] = {
                        'row': row + row_offset,
                        'col': col + col_offset,
                        'rowspan': rowspan,
                        'colspan': colspan,
                        'area': rowspan * colspan
                    }
                    max_row = max(max_row, row + row_offset + rowspan)
                    max_col = max(max_col, col + col_offset + colspan)

                elif node_type == 'section':
                    # Get section grid dimensions from metadata
                    metadata = node.get('metadata', {})
                    section_nrows = metadata.get('nrows', 1)
                    section_ncols = metadata.get('ncols', 1)
                    # For now, place sections side by side
                    for child in node.get('children', []):
                        extract_panels(child, row_offset, col_offset)

                elif node_type == 'root':
                    for child in node.get('children', []):
                        extract_panels(child, row_offset, col_offset)

            if 'root' in grid_data:
                extract_panels(grid_data['root'])

            # Calculate actual grid size from panel positions
            nrows = max_row if max_row > 0 else 1
            ncols = max_col if max_col > 0 else 1

            return jsonify(create_success_response({
                'grid': {
                    'nrows': nrows,
                    'ncols': ncols,
                    'panels': panels_dict,
                    'labels': sorted(panels_dict.keys()),
                    'num_panels': len(panels_dict)
                },
                'advanced_features': True
            }))

        # Convert / to newlines for compact notation
        if '/' in layout_str and '\n' not in layout_str:
            layout_str = layout_str.replace('/', '\n')
        grid = parse_ascii_layout(layout_str)

        # Convert to serializable format
        panels_dict = {}
        for label, pos in grid.panels.items():
            panels_dict[label] = {
                'row': pos.row,
                'col': pos.col,
                'rowspan': pos.rowspan,
                'colspan': pos.colspan,
                'area': pos.area
            }

        return jsonify(create_success_response({
            'grid': {
                'nrows': grid.nrows,
                'ncols': grid.ncols,
                'panels': panels_dict,
                'labels': grid.labels,
                'num_panels': grid.num_panels
            },
            'advanced_features': False
        }))

    except ValueError as e:
        return create_error_response(f"Invalid layout: {str(e)}")
    except Exception as e:
        return create_error_response(f"Error parsing layout: {str(e)}", 500)


@app.route('/api/layout/validate', methods=['POST'])
def validate_layout_endpoint():
    """
    POST /api/layout/validate

    Validate layout code and return detailed validation results.

    Request body:
        {
            "layout": "aab\\nccd",
            "journal": "nature",      // optional
            "size": "double"          // optional
        }

    Returns:
        {
            "success": true,
            "valid": true,
            "checks": {
                "rectangular": true,
                "labels_valid": true,
                "no_overlaps": true
            },
            "warnings": [],
            "suggestions": []
        }
    """
    try:
        data = request.get_json()
        if not data or 'layout' not in data:
            return create_error_response("Missing 'layout' field in request body")

        layout_str = data['layout']
        journal = data.get('journal', 'nature')
        size = data.get('size', 'double')

        # Parse layout
        try:
            grid = parse_ascii_layout(layout_str)
            valid = True
            parse_error = None
        except ValueError as e:
            valid = False
            parse_error = str(e)
            grid = None

        response = {
            'valid': valid,
            'checks': {
                'rectangular': grid is not None,
                'labels_valid': grid is not None and len(grid.labels) > 0,
                'no_overlaps': True  # Parser ensures no overlaps
            }
        }

        if parse_error:
            response['error'] = parse_error

        if grid:
            # Add journal-specific validation
            try:
                journal_spec = get_journal_spec(journal)
                widths = journal_spec.get('widths', {})
                size_key = size.replace('_column', '').replace('-column', '')
                if size_key not in widths:
                    response['warnings'] = [f"Size '{size}' not recognized for {journal}"]
                else:
                    response['width_mm'] = widths.get(size_key)
                    response['journal'] = journal_spec.get('name', journal)
            except ValueError:
                response['warnings'] = [f"Unknown journal: {journal}"]

            response['panel_count'] = grid.num_panels
            response['labels'] = grid.labels

        return jsonify(create_success_response(response))

    except Exception as e:
        return create_error_response(f"Error validating layout: {str(e)}", 500)


@app.route('/api/layout/templates', methods=['GET'])
def get_layout_templates():
    """
    GET /api/layout/templates

    Get all built-in layout templates with optional filtering.

    Query parameters:
        - panels: Filter by number of panels (e.g., ?panels=4)
        - category: Filter by category (grid, complex, specialized, basic)
        - details: Include full details (true/false)

    Returns:
        {
            "success": true,
            "templates": [
                {
                    "name": "4_grid",
                    "description": "Classic 2x2 grid",
                    "panels": 4,
                    "recommended_size": "double",
                    "category": "basic",
                    "ascii": "ab\\ncd"
                },
                ...
            ]
        }
    """
    try:
        num_panels = request.args.get('panels', type=int)
        category = request.args.get('category')
        show_details = request.args.get('details', 'false').lower() == 'true'

        templates = []
        for key, tmpl in LAYOUT_TEMPLATES.items():
            # Filter by panel count
            if num_panels is not None and tmpl.get('panels', 0) != num_panels:
                continue

            # Filter by category
            tmpl_category = tmpl.get('category', 'basic')
            if category is not None and tmpl_category != category:
                continue

            template_info = {
                'name': key,
                'description': tmpl.get('description', ''),
                'panels': tmpl.get('panels', 0),
                'recommended_size': tmpl.get('recommended_size', 'double'),
                'category': tmpl_category
            }

            if show_details:
                template_info['ascii'] = tmpl.get('ascii', '')
                template_info['recommended_panels'] = tmpl.get('recommended_panels', '')

            templates.append(template_info)

        # Sort by panel count, then by name
        templates.sort(key=lambda x: (x['panels'], x['name']))

        return jsonify(create_success_response({
            'templates': templates,
            'count': len(templates),
            'categories': list(set(t.get('category', 'basic') for t in LAYOUT_TEMPLATES.values()))
        }))

    except Exception as e:
        return create_error_response(f"Error fetching templates: {str(e)}", 500)


@app.route('/api/layout/templates/<name>', methods=['GET'])
def get_layout_template(name):
    """
    GET /api/layout/templates/<name>

    Get a specific layout template by name.

    Returns:
        {
            "success": true,
            "template": {
                "name": "4_grid",
                "description": "...",
                "ascii": "ab\\ncd",
                ...
            }
        }
    """
    try:
        if name not in LAYOUT_TEMPLATES:
            return create_error_response(f"Template '{name}' not found", 404)

        template = LAYOUT_TEMPLATES[name].copy()
        template['name'] = name

        return jsonify(create_success_response({'template': template}))

    except Exception as e:
        return create_error_response(f"Error fetching template: {str(e)}", 500)


# =============================================================================
# Plot Type Endpoints
# =============================================================================

PLOT_TYPE_CATEGORIES = {
    'statistics': ['bar_plot', 'box_plot', 'violin_plot', 'scatter_plot', 'histogram', 'cdf_plot'],
    'bioinformatics': ['volcano_plot', 'ma_plot', 'heatmap', 'pca_plot', 'enrichment_plot'],
    'survival': ['kaplan_meier', 'cumulative_incidence'],
    'imaging': ['intensity_profile', 'colocalization_plot', 'roi_quantification'],
    'molecular': ['sequence_logo', 'domain_architecture']
}


def get_plot_category(plot_type: str) -> str:
    """Get the category for a plot type."""
    for category, plots in PLOT_TYPE_CATEGORIES.items():
        if plot_type in plots:
            return category
    return 'other'


@app.route('/api/plot-types', methods=['GET'])
def get_all_plot_types():
    """
    GET /api/plot-types

    List all available plot types with metadata.

    Query parameters:
        - category: Filter by category
        - include_schema: Include parameter schemas (true/false)

    Returns:
        {
            "success": true,
            "plot_types": [
                {
                    "name": "bar_plot",
                    "category": "statistics",
                    "description": "Create a bar plot with optional error bars",
                    "schema": { ... }  // if include_schema=true
                },
                ...
            ],
            "categories": ["statistics", "bioinformatics", ...]
        }
    """
    try:
        category_filter = request.args.get('category')
        include_schema = request.args.get('include_schema', 'false').lower() == 'true'

        plot_types = []
        all_types = list_plot_types()

        for plot_name in all_types:
            plot_category = get_plot_category(plot_name)

            if category_filter and plot_category != category_filter:
                continue

            plot_info = {
                'name': plot_name,
                'category': plot_category
            }

            if include_schema:
                plot_info['schema'] = get_plot_type_schema(plot_name)
            else:
                # Just get description
                schema = get_plot_type_schema(plot_name)
                plot_info['description'] = schema.get('description', '')

            plot_types.append(plot_info)

        return jsonify(create_success_response({
            'plot_types': plot_types,
            'count': len(plot_types),
            'categories': list(PLOT_TYPE_CATEGORIES.keys())
        }))

    except Exception as e:
        return create_error_response(f"Error fetching plot types: {str(e)}", 500)


@app.route('/api/plot-types/<category>', methods=['GET'])
def get_plot_types_by_category(category):
    """
    GET /api/plot-types/<category>

    Get plot types filtered by category.

    Categories: statistics, bioinformatics, survival, imaging, molecular

    Returns:
        {
            "success": true,
            "category": "statistics",
            "plot_types": [...]
        }
    """
    try:
        if category not in PLOT_TYPE_CATEGORIES:
            return create_error_response(
                f"Unknown category '{category}'. "
                f"Available: {', '.join(PLOT_TYPE_CATEGORIES.keys())}",
                404
            )

        plot_types = []
        for plot_name in PLOT_TYPE_CATEGORIES[category]:
            schema = get_plot_type_schema(plot_name)
            plot_types.append({
                'name': plot_name,
                'description': schema.get('description', ''),
                'parameters': [p['name'] for p in schema.get('parameters', [])]
            })

        return jsonify(create_success_response({
            'category': category,
            'plot_types': plot_types
        }))

    except Exception as e:
        return create_error_response(f"Error fetching category: {str(e)}", 500)


@app.route('/api/plot-types/<name>/schema', methods=['GET'])
def get_plot_schema(name):
    """
    GET /api/plot-types/<name>/schema

    Get JSON schema for a specific plot type including all parameters.

    Returns:
        {
            "success": true,
            "schema": {
                "name": "bar_plot",
                "description": "Create a bar plot with optional error bars",
                "parameters": [
                    {"name": "data", "type": "Any", "default": null},
                    {"name": "x", "type": "str", "default": null},
                    ...
                ],
                "required": ["data"]
            }
        }
    """
    try:
        all_types = list_plot_types()
        if name not in all_types:
            return create_error_response(
                f"Unknown plot type '{name}'. Available: {', '.join(all_types)}",
                404
            )

        schema = get_plot_type_schema(name)
        schema['category'] = get_plot_category(name)

        return jsonify(create_success_response({'schema': schema}))

    except Exception as e:
        return create_error_response(f"Error fetching schema: {str(e)}", 500)


@app.route('/api/plot-types/<name>/preview', methods=['GET', 'POST'])
def get_plot_preview(name):
    """
    GET/POST /api/plot-types/<name>/preview

    Generate a placeholder preview of a plot type.

    Query/Body parameters:
        - width: Image width in pixels (default: 400)
        - height: Image height in pixels (default: 300)
        - dpi: DPI for rendering (default: 100)

    Returns:
        {
            "success": true,
            "preview": "data:image/png;base64,iVBORw0KGgo...",
            "plot_type": "bar_plot"
        }
    """
    try:
        all_types = list_plot_types()
        if name not in all_types:
            return create_error_response(
                f"Unknown plot type '{name}'. Available: {', '.join(all_types)}",
                404
            )

        # Get parameters
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args

        width = data.get('width', 400, type=int) if hasattr(data, 'get') else data.get('width', 400)
        height = data.get('height', 300, type=int) if hasattr(data, 'get') else data.get('height', 300)
        dpi = data.get('dpi', 100, type=int) if hasattr(data, 'get') else data.get('dpi', 100)

        # Create figure
        fig_width = width / dpi
        fig_height = height / dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

        # Generate sample data and plot
        np.random.seed(42)

        if name == 'bar_plot':
            categories = ['A', 'B', 'C', 'D']
            values = np.random.randint(10, 100, 4)
            ax.bar(categories, values, color='#56B4E9')
            ax.set_ylabel('Values')

        elif name == 'box_plot':
            data_groups = [np.random.normal(0, 1, 100) for _ in range(4)]
            bp = ax.boxplot(data_groups, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('#56B4E9')
            ax.set_xticklabels(['A', 'B', 'C', 'D'])

        elif name == 'violin_plot':
            data_groups = [np.random.normal(0, 1, 100) for _ in range(3)]
            parts = ax.violinplot(data_groups, showmeans=True)
            for pc in parts['bodies']:
                pc.set_facecolor('#56B4E9')
            ax.set_xticks([1, 2, 3])
            ax.set_xticklabels(['A', 'B', 'C'])

        elif name == 'scatter_plot':
            x = np.random.randn(50)
            y = np.random.randn(50)
            ax.scatter(x, y, alpha=0.6, s=50, c='#56B4E9')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

        elif name == 'histogram':
            data = np.random.randn(1000)
            ax.hist(data, bins=30, color='#56B4E9', edgecolor='white', alpha=0.7)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')

        elif name == 'cdf_plot':
            data = np.random.randn(100)
            sorted_data = np.sort(data)
            cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            ax.plot(sorted_data, cdf, linewidth=2, color='#56B4E9')
            ax.set_ylabel('Cumulative Probability')
            ax.set_ylim(0, 1.05)

        elif name == 'volcano_plot':
            x = np.random.randn(1000)
            y = -np.log10(np.random.uniform(0.001, 1, 1000))
            ax.scatter(x, y, alpha=0.5, s=10, c='#56B4E9')
            ax.axhline(y=-np.log10(0.05), color='red', linestyle='--', linewidth=1)
            ax.set_xlabel('log2 Fold Change')
            ax.set_ylabel('-log10(p-value)')

        elif name == 'heatmap':
            data = np.random.randn(10, 10)
            im = ax.imshow(data, cmap='viridis', aspect='auto')
            ax.set_xticks([])
            ax.set_yticks([])
            plt.colorbar(im, ax=ax, fraction=0.046)

        elif name == 'kaplan_meier':
            time = np.linspace(0, 100, 100)
            survival = np.exp(-time / 50)
            ax.step(time, survival, where='post', linewidth=2, color='#56B4E9')
            ax.set_xlabel('Time')
            ax.set_ylabel('Survival Probability')
            ax.set_ylim(0, 1.05)

        else:
            # Default placeholder
            ax.text(0.5, 0.5, f'{name}\nPreview',
                   ha='center', va='center', fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        ax.set_title(name.replace('_', ' ').title(), fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Convert to base64
        img_base64 = fig_to_base64(fig, dpi=dpi)
        plt.close(fig)

        return jsonify(create_success_response({
            'preview': f'data:image/png;base64,{img_base64}',
            'plot_type': name,
            'width': width,
            'height': height
        }))

    except Exception as e:
        import traceback
        return create_error_response(f"Error generating preview: {str(e)}", 500, {
            'traceback': traceback.format_exc()
        })


# =============================================================================
# Figure Endpoints
# =============================================================================

@app.route('/api/figure/generate', methods=['POST'])
def generate_figure():
    """
    POST /api/figure/generate

    Generate a complete figure from configuration.

    Request body:
        {
            "layout": "aab\\nccd",
            "journal": "nature",
            "size": "double",
            "panels": {
                "a": {"type": "image", "filename": "abc123.png"},
                "b": {"type": "plot", "plot_type": "bar_plot"},
                "c": {"type": "text", "text": "Sample text"},
                "d": {"type": "plot", "plot_type": "scatter_plot"}
            },
            "label_style": "lowercase_bold",
            "font_size": 8
        }

    Returns:
        {
            "success": true,
            "output_id": "abc123",
            "preview_url": "/api/outputs/abc123.png",
            "base64_image": "data:image/png;base64,...",
            "download_url": "/api/download/abc123.png",
            "validation": { ... }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")

        # Get configuration
        layout = data.get('layout', 'ab/cd')
        journal = data.get('journal', 'nature')
        size = data.get('size', 'double')
        panels_config = data.get('panels', {})
        label_style = data.get('label_style', 'lowercase_bold')
        font_size = data.get('font_size')

        # Create figure
        fig = Figure(
            journal=journal,
            size=size,
            layout=layout,
            label_style=label_style,
            font_size=font_size
        )

        # Add panels
        for panel_id, panel_config in panels_config.items():
            panel_type = panel_config.get('type', 'image')

            if panel_type == 'image':
                filename = panel_config.get('filename')
                if filename:
                    filepath = UPLOAD_FOLDER / filename
                    if filepath.exists():
                        fig[panel_id] = ImagePanel(
                            str(filepath),
                            label=panel_config.get('label'),
                            crop=panel_config.get('crop'),
                            scale=panel_config.get('scale', 1.0),
                            auto_contrast=panel_config.get('auto_contrast', False),
                            colormap=panel_config.get('colormap')
                        )

            elif panel_type == 'plot':
                plot_type = panel_config.get('plot_type', 'bar_plot')
                plot_data = panel_config.get('data')

                # Generate sample data if none provided
                if plot_data is None:
                    np.random.seed(42)
                    if plot_type == 'bar_plot':
                        plot_data = {'A': 10, 'B': 20, 'C': 15}
                    elif plot_type == 'scatter_plot':
                        # Use numpy array format
                        plot_data = np.column_stack([
                            np.random.randn(50),
                            np.random.randn(50)
                        ])
                    elif plot_type == 'histogram':
                        plot_data = np.random.randn(1000)
                    elif plot_type == 'box_plot':
                        plot_data = [np.random.randn(100) for _ in range(4)]
                    elif plot_type == 'cdf_plot':
                        plot_data = np.random.randn(100)
                    else:
                        plot_data = {'A': 10, 'B': 20}

                # Note: label is handled by the figure auto-labeling system,
                # not passed to the plot function
                fig[panel_id] = PlotPanel(plot_type, data=plot_data)

            elif panel_type == 'text':
                fig[panel_id] = TextPanel(
                    text=panel_config.get('text', ''),
                    label=panel_config.get('label')
                )

        # Render figure
        fig_combo = fig.render()

        # Save output
        output_id = generate_id()
        output_path = OUTPUT_FOLDER / f"{output_id}.png"

        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')

        # Convert to base64
        with open(output_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')

        # Validate figure
        validation_report = fig.validate()

        return jsonify(create_success_response({
            'output_id': output_id,
            'preview_url': f'/api/outputs/{output_id}.png',
            'base64_image': f'data:image/png;base64,{img_data}',
            'download_url': f'/api/download/{output_id}.png',
            'validation': validation_report.to_dict() if hasattr(validation_report, 'to_dict') else {},
            'figure_info': {
                'width_mm': fig.width_mm,
                'height_mm': fig.height_mm,
                'panels': list(fig.panels.keys())
            }
        }))

    except Exception as e:
        import traceback
        return create_error_response(f"Error generating figure: {str(e)}", 500, {
            'traceback': traceback.format_exc()
        })


# Nature-style colors (Okabe-Ito colorblind-friendly palette)
NATURE_COLORS = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']

def nature_style_bar(ax):
    """Nature-style bar plot with error bars."""
    categories = ['Control', 'Treatment A', 'Treatment B']
    values = [12.5, 18.3, 15.7]
    errors = [1.2, 1.8, 1.5]
    x = np.arange(len(categories))
    bars = ax.bar(x, values, yerr=errors, capsize=3, color=NATURE_COLORS[1],  # Use blue instead of orange
                  edgecolor='black', linewidth=0.5, error_kw={'elinewidth': 1, 'capthick': 1})
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=7)
    ax.set_ylabel('Value (units)', fontsize=7)
    ax.set_ylim(0, 25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_scatter(ax):
    """Nature-style scatter plot with regression line."""
    np.random.seed(42)
    x = np.random.randn(50)
    y = 0.5 * x + np.random.randn(50) * 0.5
    ax.scatter(x, y, c=NATURE_COLORS[1], s=20, alpha=0.7, edgecolors='black', linewidth=0.3)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p(x_line), '--', color=NATURE_COLORS[5], linewidth=1)
    ax.set_xlabel('Variable X', fontsize=7)
    ax.set_ylabel('Variable Y', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_histogram(ax):
    """Nature-style histogram."""
    np.random.seed(42)
    data = np.random.randn(1000)
    ax.hist(data, bins=30, color=NATURE_COLORS[2], edgecolor='black',
            linewidth=0.3, alpha=0.8)
    ax.set_xlabel('Value', fontsize=7)
    ax.set_ylabel('Frequency', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_box(ax):
    """Nature-style box plot."""
    np.random.seed(42)
    data = [np.random.normal(0, 1, 100),
            np.random.normal(2, 1.5, 100),
            np.random.normal(-1, 0.8, 100)]
    bp = ax.boxplot(data, patch_artist=True)
    for patch, color in zip(bp['boxes'], NATURE_COLORS[:3]):
        patch.set_facecolor(color)
        patch.set_edgecolor('black')
        patch.set_linewidth(0.5)
    for whisker in bp['whiskers']:
        whisker.set_linewidth(0.5)
    for cap in bp['caps']:
        cap.set_linewidth(0.5)
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(1)
    ax.set_xticklabels(['Group 1', 'Group 2', 'Group 3'], fontsize=7)
    ax.set_ylabel('Value', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_violin(ax):
    """Nature-style violin plot."""
    np.random.seed(42)
    data = [np.random.normal(0, 1, 200), np.random.normal(1.5, 1.2, 200)]
    parts = ax.violinplot(data, positions=[1, 2], showmeans=True, showmedians=False)
    for pc, color in zip(parts['bodies'], NATURE_COLORS[:2]):
        pc.set_facecolor(color)
        pc.set_edgecolor('black')
        pc.set_linewidth(0.5)
        pc.set_alpha(0.7)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Control', 'Treatment'], fontsize=7)
    ax.set_ylabel('Expression Level', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_line(ax):
    """Nature-style line plot."""
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x) + np.random.normal(0, 0.1, 50)
    y2 = np.cos(x) + np.random.normal(0, 0.1, 50)
    ax.plot(x, y1, '-o', color=NATURE_COLORS[0], linewidth=1, markersize=3,
            markeredgecolor='black', markeredgewidth=0.3, label='Series A')
    ax.plot(x, y2, '-s', color=NATURE_COLORS[1], linewidth=1, markersize=3,
            markeredgecolor='black', markeredgewidth=0.3, label='Series B')
    ax.set_xlabel('Time (hours)', fontsize=7)
    ax.set_ylabel('Signal', fontsize=7)
    ax.legend(loc='best', frameon=False, fontsize=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_volcano(ax):
    """Nature-style volcano plot."""
    np.random.seed(42)
    x = np.random.randn(1000) * 2
    y = -np.log10(np.random.uniform(0.001, 1, 1000))
    colors = [NATURE_COLORS[0] if abs(xi) > 1 and yi > 2 else '#999999'
              for xi, yi in zip(x, y)]
    ax.scatter(x, y, c=colors, s=10, alpha=0.6, edgecolors='none')
    ax.axhline(y=2, color='gray', linestyle='--', linewidth=0.5)
    ax.axvline(x=1, color='gray', linestyle='--', linewidth=0.5)
    ax.axvline(x=-1, color='gray', linestyle='--', linewidth=0.5)
    ax.set_xlabel('log2(Fold Change)', fontsize=7)
    ax.set_ylabel('-log10(p-value)', fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_heatmap(ax):
    """Nature-style heatmap."""
    np.random.seed(42)
    data = np.random.randn(10, 8)
    im = ax.imshow(data, cmap='RdBu_r', aspect='auto', vmin=-3, vmax=3)
    ax.set_xticks(range(8))
    ax.set_yticks(range(10))
    ax.set_xticklabels([f'S{i+1}' for i in range(8)], fontsize=6)
    ax.set_yticklabels([f'G{i+1}' for i in range(10)], fontsize=6)
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=5)

def nature_style_pca(ax):
    """Nature-style PCA plot."""
    np.random.seed(42)
    x = np.random.randn(100)
    y = np.random.randn(100)
    groups = np.random.choice(['A', 'B', 'C'], 100)
    group_colors = {g: c for g, c in zip(['A', 'B', 'C'], NATURE_COLORS[:3])}
    for g in ['A', 'B', 'C']:
        mask = groups == g
        ax.scatter(x[mask], y[mask], c=group_colors[g], s=20,
                   label=f'Group {g}', edgecolors='black', linewidth=0.3)
    ax.set_xlabel('PC1', fontsize=7)
    ax.set_ylabel('PC2', fontsize=7)
    ax.legend(loc='best', frameon=False, fontsize=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)

def nature_style_kaplan_meier(ax):
    """Nature-style Kaplan-Meier survival curve."""
    time = np.linspace(0, 100, 100)
    surv1 = np.exp(-time / 50)
    surv2 = np.exp(-time / 30)
    ax.step(time, surv1, where='post', color=NATURE_COLORS[0],
            linewidth=1.5, label='Group A')
    ax.step(time, surv2, where='post', color=NATURE_COLORS[1],
            linewidth=1.5, label='Group B')
    ax.set_xlabel('Time (months)', fontsize=7)
    ax.set_ylabel('Survival Probability', fontsize=7)
    ax.legend(loc='lower left', frameon=False, fontsize=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=6)
    ax.set_ylim(-0.05, 1.05)

# Map plot types to Nature-style functions
NATURE_PLOT_FUNCTIONS = {
    'bar_plot': nature_style_bar,
    'scatter_plot': nature_style_scatter,
    'histogram': nature_style_histogram,
    'box_plot': nature_style_box,
    'violin_plot': nature_style_violin,
    'line_plot': nature_style_line,
    'volcano_plot': nature_style_volcano,
    'heatmap': nature_style_heatmap,
    'pca_plot': nature_style_pca,
    'kaplan_meier': nature_style_kaplan_meier,
}

def get_nature_plot_function(plot_type: str):
    """Get the appropriate Nature-style plot function."""
    return NATURE_PLOT_FUNCTIONS.get(plot_type, nature_style_bar)


def draw_image_placeholder(ax, panel_id: str = ''):
    """Draw a placeholder rectangle for image panels without uploaded images.

    Shows a dashed rectangle filling the panel, matching data plot size.
    """
    from matplotlib.patches import Rectangle

    # Set axis limits to create consistent padding like data plots
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Draw dashed rectangle border filling most of the panel
    rect = Rectangle((0.08, 0.12), 0.84, 0.76, fill=False,
                     edgecolor='#999999', linewidth=1.5, linestyle='--',
                     transform=ax.transAxes)
    ax.add_patch(rect)

    # Add placeholder text in center
    ax.text(0.5, 0.5, f'📷 Image {panel_id.upper()}',
            transform=ax.transAxes,
            ha='center', va='center',
            fontsize=9, color='#666666',
            fontweight='bold')

    # Hide all axes elements but keep the frame for consistent sizing
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)


@app.route('/api/figure/preview', methods=['POST'])
def preview_figure():
    """
    POST /api/figure/preview

    Generate a quick preview (lower quality) for rapid iteration.

    Request body: Same as /api/figure/generate

    Returns:
        {
            "success": true,
            "preview": "data:image/png;base64,...",
            "output_id": "abc123"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")

        # Use lower DPI for preview
        layout = data.get('layout', 'ab/cd')
        journal = data.get('journal', 'nature')
        size = data.get('size', 'double')
        panels_config = data.get('panels', {})

        # Create figure with preview settings
        fig = Figure(
            journal=journal,
            size=size,
            layout=layout,
            label_style=data.get('label_style', 'lowercase_bold'),
            font_size=data.get('font_size', 8)
        )

        # Add panels (simplified for preview)
        for panel_id, panel_config in panels_config.items():
            panel_type = panel_config.get('type', 'image')

            if panel_type == 'image':
                filename = panel_config.get('filename')
                if filename:
                    filepath = UPLOAD_FOLDER / filename
                    if filepath.exists():
                        fig[panel_id] = ImagePanel(str(filepath))
                    else:
                        # Show placeholder rectangle if image not found
                        fig[panel_id] = PlotPanel(lambda ax: draw_image_placeholder(ax, panel_id))
                else:
                    # Show placeholder rectangle if no filename provided
                    fig[panel_id] = PlotPanel(lambda ax: draw_image_placeholder(ax, panel_id))

            elif panel_type == 'plot':
                plot_type = panel_config.get('plot_type', 'bar_plot')
                # Get the appropriate Nature-style plot function
                plot_func = get_nature_plot_function(plot_type)
                fig[panel_id] = PlotPanel(plot_func)

            elif panel_type == 'text':
                fig[panel_id] = TextPanel(text=panel_config.get('text', ''))

        # Render with higher DPI for better quality
        fig_combo = fig.render()

        # Generate preview with 150 DPI for better clarity
        img_base64 = fig_to_base64(fig_combo, dpi=150)
        plt.close()

        output_id = generate_id()

        return jsonify(create_success_response({
            'preview': f'data:image/png;base64,{img_base64}',
            'output_id': output_id,
            'quality': 'preview',
            'dpi': 72
        }))

    except Exception as e:
        import traceback
        return create_error_response(f"Error generating preview: {str(e)}", 500, {
            'traceback': traceback.format_exc()
        })


@app.route('/api/figure/export', methods=['POST'])
def export_figure():
    """
    POST /api/figure/export

    Export figure to specific format with journal-quality settings.

    Request body:
        {
            "output_id": "abc123",
            "format": "pdf",           // pdf, png, tiff, eps, svg
            "dpi": 300,                // optional
            "figure_type": "combination"  // line_art, halftone, combination
        }

    Returns:
        {
            "success": true,
            "download_url": "/api/download/abc123.pdf",
            "format": "pdf",
            "file_size": 12345
        }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")

        output_id = data.get('output_id')
        if not output_id:
            return create_error_response("Missing 'output_id'")

        format = data.get('format', 'pdf').lower()
        dpi = data.get('dpi')
        figure_type = data.get('figure_type', 'combination')

        # Validate format
        allowed_formats = ['pdf', 'png', 'tiff', 'tif', 'eps', 'svg']
        if format not in allowed_formats:
            return create_error_response(
                f"Unsupported format '{format}'. Allowed: {', '.join(allowed_formats)}"
            )

        # Find source PNG
        source_path = OUTPUT_FOLDER / f"{output_id}.png"
        if not source_path.exists():
            return create_error_response(f"Source figure not found: {output_id}", 404)

        # Load and re-export
        from matplotlib.figure import Figure as MplFigure
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        img = Image.open(source_path)
        fig = plt.figure(figsize=(img.width / 100, img.height / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img)
        ax.axis('off')

        # Determine DPI
        if dpi is None:
            format_defaults = {'pdf': 300, 'png': 300, 'tiff': 600, 'tif': 600, 'eps': 300, 'svg': 300}
            dpi = format_defaults.get(format, 300)

        # Export
        output_path = OUTPUT_FOLDER / f"{output_id}.{format}"

        save_kwargs = {'dpi': dpi, 'facecolor': 'white', 'edgecolor': 'none'}
        if format in ('tiff', 'tif'):
            save_kwargs['pil_kwargs'] = {'compression': 'tiff_lzw'}

        fig.savefig(output_path, format=format, **save_kwargs)
        plt.close(fig)

        file_size = output_path.stat().st_size

        return jsonify(create_success_response({
            'download_url': f'/api/download/{output_id}.{format}',
            'format': format,
            'dpi': dpi,
            'file_size': file_size,
            'file_size_human': f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"
        }))

    except Exception as e:
        return create_error_response(f"Error exporting figure: {str(e)}", 500)


# =============================================================================
# Asset Endpoints
# =============================================================================

@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """
    POST /api/upload/image

    Upload an image file for use in figures.

    Form data:
        - file: Image file (required)
        - metadata: Optional JSON metadata

    Returns:
        {
            "success": true,
            "file_id": "abc123",
            "filename": "abc123.png",
            "original_name": "image.png",
            "width": 1024,
            "height": 768,
            "mode": "RGB",
            "url": "/api/uploads/abc123.png"
        }
    """
    try:
        if 'file' not in request.files:
            return create_error_response("No file provided")

        file = request.files['file']
        if file.filename == '':
            return create_error_response("Empty filename")

        # Validate extension
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return create_error_response(
                f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )

        # Generate unique filename
        file_id = generate_id()
        ext = Path(file.filename).suffix.lower()
        filename = f"{file_id}{ext}"
        filepath = UPLOAD_FOLDER / filename

        # Save file
        file.save(filepath)

        # Get image info
        with Image.open(filepath) as img:
            width, height = img.size
            mode = img.mode

        # Store metadata
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except json.JSONDecodeError:
                pass

        sessions[file_id] = {
            'type': 'image',
            'filename': filename,
            'original_name': file.filename,
            'width': width,
            'height': height,
            'mode': mode,
            'uploaded_at': datetime.now().isoformat(),
            'metadata': metadata
        }

        return jsonify(create_success_response({
            'file_id': file_id,
            'filename': filename,
            'original_name': file.filename,
            'width': width,
            'height': height,
            'mode': mode,
            'url': f'/api/uploads/{filename}'
        }))

    except Exception as e:
        return create_error_response(f"Error uploading image: {str(e)}", 500)


@app.route('/api/upload/code', methods=['POST'])
def upload_code():
    """
    POST /api/upload/code

    Upload Python code for custom plot functions.

    Form data:
        - file: Python file (.py) or text content
        - code: Direct code string (alternative to file)

    Returns:
        {
            "success": true,
            "code_id": "abc123",
            "filename": "custom_plot.py",
            "functions": ["my_plot", "my_other_plot"]
        }
    """
    try:
        code_content = None
        original_filename = 'unnamed.py'

        # Get code from file or direct input
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                original_filename = file.filename
                if not allowed_file(file.filename, ALLOWED_CODE_EXTENSIONS):
                    return create_error_response(
                        f"Invalid file type. Allowed: {', '.join(ALLOWED_CODE_EXTENSIONS)}"
                    )
                code_content = file.read().decode('utf-8')

        elif 'code' in request.form:
            code_content = request.form['code']

        elif request.is_json:
            data = request.get_json()
            code_content = data.get('code')
            original_filename = data.get('filename', 'unnamed.py')

        if not code_content:
            return create_error_response("No code provided (use 'file' or 'code' field)")

        # Generate ID and save
        code_id = generate_id()
        ext = Path(original_filename).suffix.lower() or '.py'
        filename = f"{code_id}{ext}"
        filepath = CODE_FOLDER / filename

        with open(filepath, 'w') as f:
            f.write(code_content)

        # Parse for function definitions
        import ast
        functions = []
        try:
            tree = ast.parse(code_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except SyntaxError:
            pass

        sessions[code_id] = {
            'type': 'code',
            'filename': filename,
            'original_name': original_filename,
            'functions': functions,
            'uploaded_at': datetime.now().isoformat()
        }

        return jsonify(create_success_response({
            'code_id': code_id,
            'filename': filename,
            'original_name': original_filename,
            'functions': functions,
            'lines': len(code_content.splitlines())
        }))

    except Exception as e:
        return create_error_response(f"Error uploading code: {str(e)}", 500)


@app.route('/api/assets/list', methods=['GET'])
def list_assets():
    """
    GET /api/assets/list

    List all uploaded assets with optional filtering.

    Query parameters:
        - type: Filter by type (image, code, all)
        - limit: Maximum number of results (default: 100)

    Returns:
        {
            "success": true,
            "assets": [
                {
                    "id": "abc123",
                    "type": "image",
                    "filename": "abc123.png",
                    "original_name": "image.png",
                    "uploaded_at": "2024-01-15T10:30:00"
                }
            ],
            "total": 5
        }
    """
    try:
        asset_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 100, type=int)

        assets = []

        # Scan upload folder
        for filepath in UPLOAD_FOLDER.iterdir():
            if filepath.is_file():
                file_id = filepath.stem
                stat = filepath.stat()

                asset_info = sessions.get(file_id, {
                    'original_name': filepath.name,
                    'type': 'image'
                })

                if asset_type != 'all' and asset_info.get('type') != asset_type:
                    continue

                assets.append({
                    'id': file_id,
                    'type': asset_info.get('type', 'image'),
                    'filename': filepath.name,
                    'original_name': asset_info.get('original_name', filepath.name),
                    'size': stat.st_size,
                    'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        # Scan code folder
        for filepath in CODE_FOLDER.iterdir():
            if filepath.is_file():
                file_id = filepath.stem
                stat = filepath.stat()

                asset_info = sessions.get(file_id, {})

                if asset_type != 'all' and asset_type != 'code':
                    continue

                assets.append({
                    'id': file_id,
                    'type': 'code',
                    'filename': filepath.name,
                    'original_name': asset_info.get('original_name', filepath.name),
                    'functions': asset_info.get('functions', []),
                    'size': stat.st_size,
                    'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        # Sort by upload time (newest first)
        assets.sort(key=lambda x: x['uploaded_at'], reverse=True)

        total = len(assets)
        assets = assets[:limit]

        return jsonify(create_success_response({
            'assets': assets,
            'total': total,
            'limit': limit
        }))

    except Exception as e:
        return create_error_response(f"Error listing assets: {str(e)}", 500)


@app.route('/api/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/outputs/<filename>')
def serve_output(filename):
    """Serve generated output files."""
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download a file with proper headers."""
    filepath = OUTPUT_FOLDER / filename
    if not filepath.exists():
        # Try upload folder
        filepath = UPLOAD_FOLDER / filename

    if filepath.exists():
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"figcombo_{filename}"
        )

    return create_error_response(f"File not found: {filename}", 404)


# =============================================================================
# Project Endpoints
# =============================================================================

@app.route('/api/project/save', methods=['POST'])
def save_project():
    """
    POST /api/project/save

    Save a project configuration.

    Request body:
        {
            "name": "MyFigure",
            "config": {
                "layout": "aab\\nccd",
                "journal": "nature",
                "panels": { ... }
            },
            "overwrite": false
        }

    Returns:
        {
            "success": true,
            "project_name": "MyFigure",
            "saved_at": "2024-01-15T10:30:00",
            "version": 1
        }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")

        name = data.get('name')
        if not name:
            return create_error_response("Project name is required")

        # Sanitize name
        name = secure_filename(name)
        if not name:
            return create_error_response("Invalid project name")

        config = data.get('config', {})
        overwrite = data.get('overwrite', False)

        project_path = PROJECT_FOLDER / f"{name}.json"

        # Check for existing
        version = 1
        if project_path.exists():
            if not overwrite:
                return create_error_response(
                    f"Project '{name}' already exists. Set overwrite=true to replace.",
                    409
                )
            # Load existing to get version
            try:
                with open(project_path) as f:
                    existing = json.load(f)
                    version = existing.get('version', 0) + 1
            except:
                pass

        # Save project
        project_data = {
            'name': name,
            'config': config,
            'version': version,
            'saved_at': datetime.now().isoformat(),
            'api_version': '1.0'
        }

        with open(project_path, 'w') as f:
            json.dump(project_data, f, indent=2)

        return jsonify(create_success_response({
            'project_name': name,
            'saved_at': project_data['saved_at'],
            'version': version,
            'path': str(project_path)
        }, message=f"Project '{name}' saved successfully"))

    except Exception as e:
        return create_error_response(f"Error saving project: {str(e)}", 500)


@app.route('/api/project/load/<name>', methods=['GET'])
def load_project(name):
    """
    GET /api/project/load/<name>

    Load a saved project configuration.

    Returns:
        {
            "success": true,
            "project": {
                "name": "MyFigure",
                "config": { ... },
                "version": 1,
                "saved_at": "2024-01-15T10:30:00"
            }
        }
    """
    try:
        # Sanitize name
        name = secure_filename(name)
        if not name:
            return create_error_response("Invalid project name", 400)

        project_path = PROJECT_FOLDER / f"{name}.json"

        if not project_path.exists():
            return create_error_response(f"Project '{name}' not found", 404)

        with open(project_path) as f:
            project_data = json.load(f)

        return jsonify(create_success_response({
            'project': project_data
        }))

    except json.JSONDecodeError:
        return create_error_response(f"Invalid project file format", 500)
    except Exception as e:
        return create_error_response(f"Error loading project: {str(e)}", 500)


@app.route('/api/project/list', methods=['GET'])
def list_projects():
    """
    GET /api/project/list

    List all saved projects.

    Query parameters:
        - limit: Maximum number of results (default: 100)

    Returns:
        {
            "success": true,
            "projects": [
                {
                    "name": "MyFigure",
                    "version": 1,
                    "saved_at": "2024-01-15T10:30:00",
                    "preview": "aab/ccd"
                }
            ],
            "total": 5
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)

        projects = []
        for project_file in PROJECT_FOLDER.glob('*.json'):
            try:
                with open(project_file) as f:
                    data = json.load(f)

                config = data.get('config', {})
                projects.append({
                    'name': data.get('name', project_file.stem),
                    'version': data.get('version', 1),
                    'saved_at': data.get('saved_at', ''),
                    'layout_preview': config.get('layout', '')[:50] if isinstance(config.get('layout'), str) else ''
                })
            except:
                # Skip invalid files
                continue

        # Sort by saved time (newest first)
        projects.sort(key=lambda x: x['saved_at'], reverse=True)

        total = len(projects)
        projects = projects[:limit]

        return jsonify(create_success_response({
            'projects': projects,
            'total': total,
            'limit': limit
        }))

    except Exception as e:
        return create_error_response(f"Error listing projects: {str(e)}", 500)


@app.route('/api/project/delete/<name>', methods=['DELETE'])
def delete_project(name):
    """
    DELETE /api/project/delete/<name>

    Delete a saved project.

    Returns:
        {
            "success": true,
            "message": "Project 'MyFigure' deleted"
        }
    """
    try:
        name = secure_filename(name)
        if not name:
            return create_error_response("Invalid project name", 400)

        project_path = PROJECT_FOLDER / f"{name}.json"

        if not project_path.exists():
            return create_error_response(f"Project '{name}' not found", 404)

        project_path.unlink()

        return jsonify(create_success_response(
            message=f"Project '{name}' deleted successfully"
        ))

    except Exception as e:
        return create_error_response(f"Error deleting project: {str(e)}", 500)


# =============================================================================
# Additional Utility Endpoints
# =============================================================================

@app.route('/api/journals', methods=['GET'])
def get_journals():
    """
    GET /api/journals

    Get all supported journals with specifications.

    Returns:
        {
            "success": true,
            "journals": [
                {
                    "id": "nature",
                    "name": "Nature",
                    "widths": {"single": 89, "double": 183},
                    "dpi": 300
                }
            ]
        }
    """
    try:
        journals = []
        for key in sorted(JOURNAL_SPECS.keys()):
            spec = get_journal_spec(key)
            journals.append({
                'id': key,
                'name': spec.get('name', key),
                'widths': spec.get('widths', {}),
                'max_height': spec.get('max_height', 250),
                'dpi': spec.get('dpi', {}),
                'formats': spec.get('formats', ['PDF']),
                'label_style': spec.get('label_style', 'lowercase_bold')
            })

        return jsonify(create_success_response({'journals': journals}))

    except Exception as e:
        return create_error_response(f"Error fetching journals: {str(e)}", 500)


@app.route('/api/validate/figure', methods=['POST'])
def validate_figure_endpoint():
    """
    POST /api/validate/figure

    Validate figure parameters against journal specifications.

    Request body:
        {
            "width_mm": 183,
            "height_mm": 120,
            "journal": "nature",
            "font_size": 8,
            "dpi": 300
        }

    Returns:
        {
            "success": true,
            "validation": {
                "passed": 5,
                "warnings": 1,
                "failures": 0,
                "is_clean": true,
                "results": [...]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("No JSON data provided")

        width_mm = data.get('width_mm', 183)
        height_mm = data.get('height_mm', 120)
        journal = data.get('journal', 'nature')

        try:
            journal_spec = get_journal_spec(journal)
        except ValueError:
            return create_error_response(f"Unknown journal: {journal}")

        # Run validation
        report = validate_figure(
            figure_width_mm=width_mm,
            figure_height_mm=height_mm,
            journal_spec=journal_spec,
            font_size=data.get('font_size'),
            dpi=data.get('dpi'),
            colors=data.get('colors'),
            output_format=data.get('output_format')
        )

        return jsonify(create_success_response({
            'validation': report.to_dict()
        }))

    except Exception as e:
        return create_error_response(f"Error validating figure: {str(e)}", 500)


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    GET /api/health

    Health check endpoint.

    Returns:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00",
            "version": "1.0.0",
            "figcombo_available": true
        }
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'figcombo_available': True,
        'endpoints': {
            'layout': ['/api/layout/parse', '/api/layout/validate', '/api/layout/templates'],
            'plot_types': ['/api/plot-types', '/api/plot-types/<category>', '/api/plot-types/<name>/schema'],
            'figure': ['/api/figure/generate', '/api/figure/preview', '/api/figure/export'],
            'assets': ['/api/upload/image', '/api/upload/code', '/api/assets/list'],
            'projects': ['/api/project/save', '/api/project/load/<name>', '/api/project/list']
        }
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return create_error_response("Endpoint not found", 404)


@app.errorhandler(405)
def method_not_allowed(error):
    return create_error_response("Method not allowed", 405)


@app.errorhandler(413)
def too_large(error):
    return create_error_response("File too large (max 100MB)", 413)


@app.errorhandler(500)
def internal_error(error):
    return create_error_response("Internal server error", 500)


def get_local_ip():
    """Get local IP address for display."""
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip == '127.0.0.1':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
            finally:
                s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='FigCombo API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Listen address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Listen port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    local_ip = get_local_ip()

    print("=" * 60)
    print("FigCombo API Server")
    print("=" * 60)
    print(f"Local:    http://127.0.0.1:{args.port}")
    print(f"Network:  http://{local_ip}:{args.port}")
    print("=" * 60)
    print("API Documentation:")
    print(f"  Health:   http://127.0.0.1:{args.port}/api/health")
    print(f"  Layouts:  http://127.0.0.1:{args.port}/api/layout/templates")
    print(f"  Plots:    http://127.0.0.1:{args.port}/api/plot-types")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)
