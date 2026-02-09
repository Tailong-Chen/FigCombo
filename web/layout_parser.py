#!/usr/bin/env python3
"""
FigCombo Layout Code Parser - Hierarchical Layout System

This module implements a comprehensive layout code parser that supports:
1. Basic grid layouts: aab/aac/ddd
2. Named sections: [header:ab/cd]
3. Sub-panels: a[i,ii,iii] or a.1, a.2
4. Insets: a{x,y,w,h} or a<inner_grid>

The parser outputs a JSON-serializable tree structure suitable for both
frontend and backend consumption.
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Union
from enum import Enum, auto


class NodeType(Enum):
    """Types of layout nodes."""
    ROOT = "root"
    SECTION = "section"
    PANEL = "panel"
    SUB_PANEL = "sub_panel"
    INSET = "inset"
    GRID = "grid"


class LayoutError(Exception):
    """Base exception for layout parsing errors."""
    pass


class LayoutSyntaxError(LayoutError):
    """Raised when layout code has syntax errors."""
    pass


class LayoutValidationError(LayoutError):
    """Raised when layout fails validation."""
    pass


@dataclass
class LayoutNode:
    """
    A node in the layout tree structure.

    This is the core data structure representing any element in the layout,
    from the root down to individual panels, sub-panels, and insets.

    Attributes
    ----------
    node_type : NodeType
        The type of this node.
    id : str
        Unique identifier for this node (e.g., 'a', 'header', 'a.i').
    label : str, optional
        Display label for this node.
    row : int, optional
        Starting row position in the grid (0-based).
    col : int, optional
        Starting column position in the grid (0-based).
    rowspan : int, optional
        Number of rows this node spans.
    colspan : int, optional
        Number of columns this node spans.
    children : list[LayoutNode]
        Child nodes (for hierarchical structures like sections/sub-panels).
    metadata : dict[str, Any]
        Additional node-specific data (inset bounds, sub-panel indices, etc.).
    parent : str, optional
        Reference to parent node ID.

    Examples
    --------
    >>> node = LayoutNode(
    ...     node_type=NodeType.PANEL,
    ...     id='a',
    ...     label='Panel A',
    ...     row=0, col=0,
    ...     rowspan=2, colspan=2
    ... )
    """
    node_type: NodeType
    id: str
    label: Optional[str] = None
    row: Optional[int] = None
    col: Optional[int] = None
    rowspan: int = 1
    colspan: int = 1
    children: list['LayoutNode'] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    parent: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary (JSON-serializable)."""
        result = {
            'node_type': self.node_type.value,
            'id': self.id,
            'label': self.label,
            'row': self.row,
            'col': self.col,
            'rowspan': self.rowspan,
            'colspan': self.colspan,
            'children': [child.to_dict() for child in self.children],
            'metadata': self.metadata,
            'parent': self.parent,
        }
        # Remove None values for cleaner JSON
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LayoutNode':
        """Create a LayoutNode from a dictionary."""
        node_type = NodeType(data.get('node_type', 'panel'))
        children_data = data.pop('children', [])
        node = cls(
            node_type=node_type,
            id=data['id'],
            label=data.get('label'),
            row=data.get('row'),
            col=data.get('col'),
            rowspan=data.get('rowspan', 1),
            colspan=data.get('colspan', 1),
            metadata=data.get('metadata', {}),
            parent=data.get('parent'),
        )
        node.children = [cls.from_dict(child) for child in children_data]
        return node

    def get_descendant(self, node_id: str) -> Optional['LayoutNode']:
        """Find a descendant node by ID."""
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.get_descendant(node_id)
            if result:
                return result
        return None

    def get_all_panel_ids(self) -> list[str]:
        """Get all panel IDs in this subtree."""
        ids = []
        if self.node_type in (NodeType.PANEL, NodeType.SUB_PANEL):
            ids.append(self.id)
        for child in self.children:
            ids.extend(child.get_all_panel_ids())
        return ids

    def __repr__(self) -> str:
        pos = f"[{self.row}:{self.row+self.rowspan}, {self.col}:{self.col+self.colspan}]" \
              if self.row is not None and self.col is not None else ""
        children_info = f", {len(self.children)} children" if self.children else ""
        return f"LayoutNode({self.node_type.value}, '{self.id}'{pos}{children_info})"


@dataclass
class LayoutTree:
    """
    Complete layout tree with metadata.

    Attributes
    ----------
    root : LayoutNode
        The root node of the layout tree.
    nrows : int
        Total number of rows in the layout grid.
    ncols : int
        Total number of columns in the layout grid.
    row_ratios : list[float]
        Relative height ratios for each row.
    col_ratios : list[float]
        Relative width ratios for each column.
    raw_code : str
        The original layout code string.
    version : str
        Parser version for compatibility.

    Examples
    --------
    >>> tree = LayoutTree(
    ...     root=LayoutNode(NodeType.ROOT, 'root'),
    ...     nrows=2, ncols=2,
    ...     raw_code='ab/cd'
    ... )
    """
    root: LayoutNode
    nrows: int = 0
    ncols: int = 0
    row_ratios: list[float] = field(default_factory=list)
    col_ratios: list[float] = field(default_factory=list)
    raw_code: str = ""
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert tree to dictionary (JSON-serializable)."""
        return {
            'root': self.root.to_dict(),
            'nrows': self.nrows,
            'ncols': self.ncols,
            'row_ratios': self.row_ratios,
            'col_ratios': self.col_ratios,
            'raw_code': self.raw_code,
            'version': self.version,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert tree to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LayoutTree':
        """Create a LayoutTree from a dictionary."""
        return cls(
            root=LayoutNode.from_dict(data['root']),
            nrows=data.get('nrows', 0),
            ncols=data.get('ncols', 0),
            row_ratios=data.get('row_ratios', []),
            col_ratios=data.get('col_ratios', []),
            raw_code=data.get('raw_code', ''),
            version=data.get('version', '1.0'),
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'LayoutTree':
        """Create a LayoutTree from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    def get_panel(self, panel_id: str) -> Optional[LayoutNode]:
        """Get a panel by ID."""
        return self.root.get_descendant(panel_id)

    def get_all_panel_ids(self) -> list[str]:
        """Get all panel IDs in the layout."""
        return self.root.get_all_panel_ids()


class LayoutCodeParser:
    """
    Parser for hierarchical layout codes.

    Supports the following syntax:

    1. Basic Grid:
       - Single character panels: 'ab/cd' -> 2x2 grid
       - Multi-cell panels: 'aab/aac/ddd' -> panel 'a' spans 2x2

    2. Named Sections:
       - [header:ab/cd] -> creates a named section 'header'
       - Sections can be nested: [outer:[inner:ab]]

    3. Sub-panels:
       - Bracket notation: a[i,ii,iii] -> panel 'a' with 3 sub-panels
       - Dot notation: a.1, a.2, a.3 -> alternative sub-panel syntax
       - Grid notation: a[2x3] -> 2x3 grid of sub-panels

    4. Insets:
       - Absolute bounds: a{0.6,0.6,0.35,0.35} -> inset at (x,y,w,h)
       - Grid notation: a<ab/cd> -> inset with grid layout

    Examples
    --------
    >>> parser = LayoutCodeParser()
    >>> tree = parser.parse('aab/aac/ddd')
    >>> tree = parser.parse('[header:ab/cd]')
    >>> tree = parser.parse('a[i,ii]b/cde')
    >>> tree = parser.parse('a{0.6,0.6,0.3,0.3}bc/def')

    Parameters
    ----------
    validate : bool, default True
        Whether to validate the layout after parsing.
    strict_mode : bool, default False
        If True, raises errors for warnings like overlapping panels.
    """

    # Regular expressions for parsing
    SECTION_PATTERN = re.compile(
        r'\[(?P<name>[a-zA-Z_][a-zA-Z0-9_]*):(?P<content>[^\]]+)\]'
    )
    SUB_PANEL_BRACKET_PATTERN = re.compile(
        r'(?P<panel>[a-zA-Z])(?P<notation>\[(?P<items>[^\]]+)\])'
    )
    SUB_PANEL_DOT_PATTERN = re.compile(
        r'(?P<panel>[a-zA-Z])\.(?P<index>[0-9]+|[ivx]+|[a-z])'
    )
    INSET_ABSOLUTE_PATTERN = re.compile(
        r'(?P<panel>[a-zA-Z])\{(?P<x>[0-9.]+),(?P<y>[0-9.]+),(?P<w>[0-9.]+),(?P<h>[0-9.]+)\}'
    )
    INSET_GRID_PATTERN = re.compile(
        r'(?P<panel>[a-zA-Z])<(?P<grid>[^>]+)>'
    )
    GRID_SIZE_PATTERN = re.compile(
        r'^(?P<rows>\d+)x(?P<cols>\d+)$'
    )

    def __init__(self, validate: bool = True, strict_mode: bool = False):
        self.validate = validate
        self.strict_mode = strict_mode
        self._validator = LayoutTreeValidator()
        self._parse_context: dict[str, Any] = {}

    def parse(self, layout_code: str) -> LayoutTree:
        """
        Parse a layout code string into a LayoutTree.

        Parameters
        ----------
        layout_code : str
            The layout code to parse.

        Returns
        -------
        LayoutTree
            The parsed layout tree.

        Raises
        ------
        LayoutSyntaxError
            If the layout code has syntax errors.
        LayoutValidationError
            If validation is enabled and the layout is invalid.
        """
        if not layout_code or not layout_code.strip():
            raise LayoutSyntaxError("Layout code cannot be empty")

        # Store original code
        raw_code = layout_code.strip()

        # Reset parse context
        self._parse_context = {
            'sections': {},
            'sub_panels': {},
            'insets': {},
            'panel_counter': 0,
        }

        # Step 1: Extract and process sections
        code, sections = self._extract_sections(raw_code)

        # Step 2: Extract sub-panel definitions
        code, sub_panels = self._extract_sub_panels(code)

        # Step 3: Extract inset definitions
        code, insets = self._extract_insets(code)

        # Step 4: Parse the remaining grid structure
        grid_node = self._parse_grid(code)

        # Step 5: Build the tree structure
        root = LayoutNode(
            node_type=NodeType.ROOT,
            id='root',
            children=[]
        )

        # Process grid children - convert section placeholders to section nodes
        section_map = self._parse_context.get('section_map', {})
        for child in grid_node.children:
            if child.id in section_map:
                # This is a section placeholder - replace with actual section
                section_name = section_map[child.id]
                section_content = sections[section_name]
                section_node = self._create_section_node(
                    section_name, section_content, grid_node
                )
                # Copy position info from placeholder
                section_node.row = child.row
                section_node.col = child.col
                section_node.rowspan = child.rowspan
                section_node.colspan = child.colspan
                root.children.append(section_node)
            else:
                # Regular panel
                root.children.append(child)

        # Step 6: Attach sub-panels and insets to their parent panels
        self._attach_sub_panels(root, sub_panels)
        self._attach_insets(root, insets)

        # Step 7: Create the layout tree
        tree = LayoutTree(
            root=root,
            nrows=grid_node.metadata.get('nrows', 0),
            ncols=grid_node.metadata.get('ncols', 0),
            row_ratios=grid_node.metadata.get('row_ratios', [1.0]),
            col_ratios=grid_node.metadata.get('col_ratios', [1.0]),
            raw_code=raw_code,
        )

        # Step 8: Validate if requested
        if self.validate:
            errors = self._validator.validate(tree)
            if errors:
                if self.strict_mode:
                    raise LayoutValidationError(
                        f"Layout validation failed: {'; '.join(errors)}"
                    )
                else:
                    # Store warnings in tree metadata
                    tree.root.metadata['validation_warnings'] = errors

        return tree

    def _extract_sections(self, code: str) -> tuple[str, dict[str, str]]:
        """
        Extract named sections from the layout code.

        Handles nested brackets by counting open/close bracket pairs.

        Returns
        -------
        tuple[str, dict]
            The code with sections replaced by single-char markers, and a dict of sections.
        """
        sections = {}
        section_count = 0

        # Find all sections manually to handle nested brackets
        i = 0
        while i < len(code):
            if code[i] == '[':
                # Find the section name
                colon_idx = code.find(':', i)
                if colon_idx == -1:
                    i += 1
                    continue

                name = code[i+1:colon_idx]
                if not name or not name[0].isalpha():
                    i += 1
                    continue

                # Find matching close bracket by counting
                content_start = colon_idx + 1
                bracket_count = 1
                j = content_start
                while j < len(code) and bracket_count > 0:
                    if code[j] == '[':
                        bracket_count += 1
                    elif code[j] == ']':
                        bracket_count -= 1
                    j += 1

                if bracket_count == 0:
                    # Found matching bracket
                    content = code[content_start:j-1]
                    sections[name] = content
                    section_count += 1

                    # Replace section with placeholder
                    placeholder = chr(0xE000 + section_count - 1)
                    code = code[:i] + placeholder + code[j:]
                    # Continue from after the placeholder
                    i = i + 1
                else:
                    i += 1
            else:
                i += 1

        # Store section mapping in parse context
        self._parse_context['section_map'] = {
            chr(0xE000 + i): name for i, name in enumerate(sections.keys())
        }

        return code, sections

    def _extract_sub_panels(self, code: str) -> tuple[str, dict[str, dict]]:
        """
        Extract sub-panel definitions from the layout code.

        Returns
        -------
        tuple[str, dict]
            The code with sub-panel definitions removed, and a dict of sub-panel specs.
        """
        sub_panels = {}

        def process_bracket(match: re.Match) -> str:
            panel = match.group('panel')
            items_str = match.group('items')

            # Check if it's a grid size spec (e.g., "2x3")
            grid_match = self.GRID_SIZE_PATTERN.match(items_str)
            if grid_match:
                rows = int(grid_match.group('rows'))
                cols = int(grid_match.group('cols'))
                sub_panels[panel] = {
                    'type': 'grid',
                    'nrows': rows,
                    'ncols': cols,
                    'labels': [f"{panel}.{i}" for i in range(rows * cols)]
                }
            else:
                # Parse comma-separated list
                items = [item.strip() for item in items_str.split(',')]
                sub_panels[panel] = {
                    'type': 'list',
                    'labels': [f"{panel}.{item}" for item in items],
                    'items': items
                }

            return panel

        # Process bracket notation
        code = self.SUB_PANEL_BRACKET_PATTERN.sub(process_bracket, code)

        return code, sub_panels

    def _extract_insets(self, code: str) -> tuple[str, dict[str, list]]:
        """
        Extract inset definitions from the layout code.

        Returns
        -------
        tuple[str, dict]
            The code with inset definitions removed, and a dict of inset specs.
        """
        insets = {}

        # Pattern to match a panel letter followed by one or more inset definitions
        # This handles multiple insets like a{0.1,0.1,0.2,0.2}{0.7,0.7,0.25,0.25}
        MULTI_INSET_PATTERN = re.compile(
            r'(?P<panel>[a-zA-Z])'
            r'(?P<insets>(?:\{[0-9.]+,[0-9.]+,[0-9.]+,[0-9.]+\})+)'
        )

        def process_multi_inset(match: re.Match) -> str:
            panel = match.group('panel')
            insets_str = match.group('insets')

            # Extract all individual inset bounds
            inset_pattern = re.compile(r'\{([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+)\}')
            for inset_match in inset_pattern.finditer(insets_str):
                x = float(inset_match.group(1))
                y = float(inset_match.group(2))
                w = float(inset_match.group(3))
                h = float(inset_match.group(4))

                if panel not in insets:
                    insets[panel] = []
                insets[panel].append({
                    'type': 'absolute',
                    'bounds': (x, y, w, h)
                })

            return panel

        def process_grid_inset(match: re.Match) -> str:
            panel = match.group('panel')
            grid_code = match.group('grid')

            if panel not in insets:
                insets[panel] = []
            insets[panel].append({
                'type': 'grid',
                'grid_code': grid_code
            })

            return panel

        # Process multiple absolute insets first
        code = MULTI_INSET_PATTERN.sub(process_multi_inset, code)

        # Process single absolute insets (for backward compatibility)
        code = self.INSET_ABSOLUTE_PATTERN.sub(process_multi_inset, code)

        # Process grid insets
        code = self.INSET_GRID_PATTERN.sub(process_grid_inset, code)

        return code, insets

    def _parse_grid(self, code: str) -> LayoutNode:
        """
        Parse a basic grid layout from cleaned code.

        The code should be in the format:
        - Rows separated by '/' or newlines
        - Each row contains panel identifiers (single characters)
        - Same characters forming a rectangle are merged into one panel

        Returns
        -------
        LayoutNode
            A GRID node containing PANEL children.
        """
        # Clean the code
        lines = self._clean_grid_code(code)

        if not lines:
            raise LayoutSyntaxError("Empty grid after cleaning")

        nrows = len(lines)
        ncols = len(lines[0]) if lines else 0

        if ncols == 0:
            raise LayoutSyntaxError("Grid has zero columns")

        # Find all unique panel labels (including section markers from Private Use Area)
        labels = set()
        section_chars = set(self._parse_context.get('section_map', {}).keys())
        for line in lines:
            for ch in line:
                if ch not in (' ', '.') and (ch.isalnum() or ch in section_chars):
                    labels.add(ch)

        # Create panel nodes
        panels: dict[str, LayoutNode] = {}

        for label in sorted(labels):
            positions = []
            for r, line in enumerate(lines):
                for c, ch in enumerate(line):
                    if ch == label:
                        positions.append((r, c))

            if not positions:
                continue

            min_r = min(r for r, c in positions)
            max_r = max(r for r, c in positions)
            min_c = min(c for r, c in positions)
            max_c = max(c for r, c in positions)

            # Validate rectangular shape
            expected_cells = (max_r - min_r + 1) * (max_c - min_c + 1)
            if len(positions) != expected_cells:
                raise LayoutSyntaxError(
                    f"Panel '{label}' does not form a rectangle. "
                    f"Found {len(positions)} cells but expected {expected_cells}."
                )

            panel_node = LayoutNode(
                node_type=NodeType.PANEL,
                id=label,
                label=label.upper(),
                row=min_r,
                col=min_c,
                rowspan=max_r - min_r + 1,
                colspan=max_c - min_c + 1,
            )
            panels[label] = panel_node

        # Create grid node
        grid_node = LayoutNode(
            node_type=NodeType.GRID,
            id='grid',
            children=list(panels.values()),
            metadata={
                'nrows': nrows,
                'ncols': ncols,
                'row_ratios': [1.0] * nrows,
                'col_ratios': [1.0] * ncols,
            }
        )

        return grid_node

    def _clean_grid_code(self, code: str) -> list[str]:
        """
        Clean and normalize grid code.

        - Removes leading/trailing whitespace
        - Handles both '/' and newline as row separators
        - Removes empty lines
        - Pads rows to equal length
        """
        # Replace '/' with newlines for consistent handling
        code = code.replace('/', '\n')

        # Split into lines
        lines = code.split('\n')

        # Remove empty lines and strip whitespace
        lines = [line.strip() for line in lines if line.strip()]

        if not lines:
            return []

        # Pad to equal length
        max_len = max(len(line) for line in lines)
        lines = [line.ljust(max_len) for line in lines]

        return lines

    def _create_section_node(
        self,
        section_name: str,
        section_content: str,
        parent_grid: LayoutNode
    ) -> LayoutNode:
        """
        Create a section node from section content.

        The section content is parsed as its own mini-layout, including
        sub-panels and insets.
        """
        # Extract sub-panels and insets from section content
        code, sub_panels = self._extract_sub_panels(section_content)
        code, insets = self._extract_insets(code)

        # Parse the cleaned content as a grid
        section_grid = self._parse_grid(code)

        # Create section node
        section_node = LayoutNode(
            node_type=NodeType.SECTION,
            id=section_name,
            label=section_name.replace('_', ' ').title(),
            children=section_grid.children,
            metadata={
                'nrows': section_grid.metadata.get('nrows', 1),
                'ncols': section_grid.metadata.get('ncols', 1),
            }
        )

        # Attach sub-panels and insets to panels within the section
        self._attach_sub_panels_to_node(section_node, sub_panels)
        self._attach_insets_to_node(section_node, insets)

        return section_node

    def _attach_sub_panels_to_node(
        self,
        node: LayoutNode,
        sub_panels: dict[str, dict]
    ) -> None:
        """Attach sub-panel definitions to panels within a node."""
        for panel_id, spec in sub_panels.items():
            panel_node = node.get_descendant(panel_id)
            if not panel_node:
                continue

            if spec['type'] == 'grid':
                # Create grid of sub-panels
                nrows = spec['nrows']
                ncols = spec['ncols']
                labels = spec['labels']

                for idx, label in enumerate(labels):
                    r = idx // ncols
                    c = idx % ncols

                    sub_node = LayoutNode(
                        node_type=NodeType.SUB_PANEL,
                        id=label,
                        label=label.split('.')[-1],
                        row=r,
                        col=c,
                        rowspan=1,
                        colspan=1,
                        parent=panel_id,
                    )
                    panel_node.children.append(sub_node)

                panel_node.metadata['sub_panel_grid'] = {
                    'nrows': nrows,
                    'ncols': ncols,
                }

            elif spec['type'] == 'list':
                # Create sub-panels in a row
                for i, label in enumerate(spec['labels']):
                    sub_node = LayoutNode(
                        node_type=NodeType.SUB_PANEL,
                        id=label,
                        label=spec['items'][i],
                        row=0,
                        col=i,
                        rowspan=1,
                        colspan=1,
                        parent=panel_id,
                    )
                    panel_node.children.append(sub_node)

                panel_node.metadata['sub_panel_grid'] = {
                    'nrows': 1,
                    'ncols': len(spec['labels']),
                }

    def _attach_insets_to_node(
        self,
        node: LayoutNode,
        insets: dict[str, list]
    ) -> None:
        """Attach inset definitions to panels within a node."""
        for panel_id, inset_list in insets.items():
            panel_node = node.get_descendant(panel_id)
            if not panel_node:
                continue

            for i, inset_spec in enumerate(inset_list):
                inset_id = f"{panel_id}_inset_{i}"

                inset_node = LayoutNode(
                    node_type=NodeType.INSET,
                    id=inset_id,
                    label=f"Inset {i+1}",
                    parent=panel_id,
                    metadata=inset_spec
                )

                # If it's a grid inset, parse the grid
                if inset_spec['type'] == 'grid':
                    grid_node = self._parse_grid(inset_spec['grid_code'])
                    inset_node.children = grid_node.children
                    inset_node.metadata.update({
                        'nrows': grid_node.metadata.get('nrows', 1),
                        'ncols': grid_node.metadata.get('ncols', 1),
                    })

                panel_node.children.append(inset_node)

    def _attach_sub_panels(
        self,
        root: LayoutNode,
        sub_panels: dict[str, dict]
    ) -> None:
        """Attach sub-panel definitions to their parent panels."""
        self._attach_sub_panels_to_node(root, sub_panels)

    def _attach_insets(
        self,
        root: LayoutNode,
        insets: dict[str, list]
    ) -> None:
        """Attach inset definitions to their parent panels."""
        self._attach_insets_to_node(root, insets)


class LayoutTreeValidator:
    """
    Validator for layout trees.

    Performs various validation checks to ensure the layout is valid
    and can be rendered correctly.

    Parameters
    ----------
    check_overlaps : bool, default True
        Check for overlapping panels.
    check_gaps : bool, default False
        Check for gaps in the layout (unassigned grid cells).
    check_connectivity : bool, default True
        Check that all panels are connected.
    """

    def __init__(
        self,
        check_overlaps: bool = True,
        check_gaps: bool = False,
        check_connectivity: bool = True
    ):
        self.check_overlaps = check_overlaps
        self.check_gaps = check_gaps
        self.check_connectivity = check_connectivity

    def validate(self, tree: LayoutTree) -> list[str]:
        """
        Validate a layout tree.

        Returns
        -------
        list[str]
            List of validation errors (empty if valid).
        """
        errors = []

        # Basic structure validation
        if not tree.root.children:
            errors.append("Layout has no panels")

        if tree.nrows <= 0 or tree.ncols <= 0:
            errors.append(f"Invalid grid dimensions: {tree.nrows}x{tree.ncols}")

        # Check for duplicate panel IDs
        panel_ids = tree.get_all_panel_ids()
        seen = set()
        for pid in panel_ids:
            if pid in seen:
                errors.append(f"Duplicate panel ID: '{pid}'")
            seen.add(pid)

        # Check for overlapping panels
        if self.check_overlaps:
            overlap_errors = self._check_overlaps(tree)
            errors.extend(overlap_errors)

        # Check for gaps
        if self.check_gaps:
            gap_errors = self._check_gaps(tree)
            errors.extend(gap_errors)

        # Validate sub-panels
        sub_panel_errors = self._validate_sub_panels(tree)
        errors.extend(sub_panel_errors)

        # Validate insets
        inset_errors = self._validate_insets(tree)
        errors.extend(inset_errors)

        return errors

    def _check_overlaps(self, tree: LayoutTree) -> list[str]:
        """Check for overlapping panels in the grid."""
        errors = []

        # Get all panel positions
        panels = []
        for child in tree.root.children:
            if child.node_type == NodeType.PANEL:
                panels.append(child)
            elif child.node_type == NodeType.SECTION:
                panels.extend(child.children)

        # Check each pair of panels
        for i, p1 in enumerate(panels):
            for p2 in panels[i+1:]:
                if self._panels_overlap(p1, p2):
                    errors.append(
                        f"Panels '{p1.id}' and '{p2.id}' overlap in the grid"
                    )

        return errors

    def _panels_overlap(self, p1: LayoutNode, p2: LayoutNode) -> bool:
        """Check if two panels overlap."""
        if p1.row is None or p2.row is None:
            return False

        # Check for overlap in both dimensions
        row_overlap = not (
            p1.row + p1.rowspan <= p2.row or
            p2.row + p2.rowspan <= p1.row
        )
        col_overlap = not (
            p1.col + p1.colspan <= p2.col or
            p2.col + p2.colspan <= p1.col
        )

        return row_overlap and col_overlap

    def _check_gaps(self, tree: LayoutTree) -> list[str]:
        """Check for gaps (unassigned cells) in the grid."""
        errors = []

        # Create a grid to track assigned cells
        grid = [[False] * tree.ncols for _ in range(tree.nrows)]

        # Mark cells assigned to panels
        for child in tree.root.children:
            if child.node_type == NodeType.PANEL:
                self._mark_grid_cells(grid, child)
            elif child.node_type == NodeType.SECTION:
                for panel in child.children:
                    if panel.node_type == NodeType.PANEL:
                        self._mark_grid_cells(grid, panel)

        # Check for unassigned cells
        unassigned = []
        for r in range(tree.nrows):
            for c in range(tree.ncols):
                if not grid[r][c]:
                    unassigned.append(f"({r},{c})")

        if unassigned:
            errors.append(f"Unassigned grid cells: {', '.join(unassigned[:5])}")

        return errors

    def _mark_grid_cells(self, grid: list[list[bool]], panel: LayoutNode) -> None:
        """Mark grid cells as assigned for a panel."""
        if panel.row is None:
            return

        for r in range(panel.row, panel.row + panel.rowspan):
            for c in range(panel.col, panel.col + panel.colspan):
                if r < len(grid) and c < len(grid[0]):
                    grid[r][c] = True

    def _validate_sub_panels(self, tree: LayoutTree) -> list[str]:
        """Validate sub-panel configurations."""
        errors = []

        def check_node(node: LayoutNode) -> None:
            if node.node_type == NodeType.PANEL and node.children:
                sub_panels = [c for c in node.children if c.node_type == NodeType.SUB_PANEL]

                if sub_panels:
                    grid_info = node.metadata.get('sub_panel_grid', {})
                    nrows = grid_info.get('nrows', 1)
                    ncols = grid_info.get('ncols', len(sub_panels))

                    # Check that sub-panels fit in the grid
                    expected = nrows * ncols
                    if len(sub_panels) > expected:
                        errors.append(
                            f"Panel '{node.id}' has {len(sub_panels)} sub-panels "
                            f"but grid only fits {expected}"
                        )

                    # Check for duplicate sub-panel positions
                    positions = set()
                    for sp in sub_panels:
                        pos = (sp.row, sp.col)
                        if pos in positions:
                            errors.append(
                                f"Panel '{node.id}' has overlapping sub-panels at {pos}"
                            )
                        positions.add(pos)

            for child in node.children:
                check_node(child)

        check_node(tree.root)
        return errors

    def _validate_insets(self, tree: LayoutTree) -> list[str]:
        """Validate inset configurations."""
        errors = []

        def check_node(node: LayoutNode) -> None:
            if node.node_type == NodeType.PANEL:
                insets = [c for c in node.children if c.node_type == NodeType.INSET]

                for inset in insets:
                    if inset.metadata.get('type') == 'absolute':
                        bounds = inset.metadata.get('bounds', (0, 0, 0, 0))
                        x, y, w, h = bounds

                        # Check bounds are within [0, 1]
                        if not (0 <= x <= 1 and 0 <= y <= 1):
                            errors.append(
                                f"Inset in panel '{node.id}' has position outside [0,1]: ({x}, {y})"
                            )
                        if not (0 < w <= 1 and 0 < h <= 1):
                            errors.append(
                                f"Inset in panel '{node.id}' has invalid size: ({w}, {h})"
                            )
                        if x + w > 1 or y + h > 1:
                            errors.append(
                                f"Inset in panel '{node.id}' extends outside parent bounds"
                            )

            for child in node.children:
                check_node(child)

        check_node(tree.root)
        return errors


# ============================================================================
# Example Layout Codes and Expected Outputs
# ============================================================================

EXAMPLE_LAYOUT_CODES: list[dict[str, Any]] = [
    {
        'name': 'Basic 2x2 Grid',
        'code': 'ab/cd',
        'description': 'Four equal panels in a 2x2 grid',
        'expected': {
            'nrows': 2,
            'ncols': 2,
            'panels': ['a', 'b', 'c', 'd'],
        }
    },
    {
        'name': 'Mixed Size Grid',
        'code': 'aab/aac/ddd',
        'description': 'Panel a spans 2x2, panels b,c on right, panel d spans bottom',
        'expected': {
            'nrows': 3,
            'ncols': 3,
            'panels': ['a', 'b', 'c', 'd'],
            'spans': {
                'a': {'rowspan': 2, 'colspan': 2},
                'd': {'rowspan': 1, 'colspan': 3},
            }
        }
    },
    {
        'name': 'Named Section',
        'code': '[header:ab/cd]',
        'description': 'A named section containing a 2x2 grid',
        'expected': {
            'sections': ['header'],
            'nrows': 2,
            'ncols': 2,
        }
    },
    {
        'name': 'Sub-panels (Bracket Notation)',
        'code': 'a[i,ii,iii]b/cde',
        'description': 'Panel a with 3 sub-panels, panels b,c,d,e in grid',
        'expected': {
            'sub_panels': {
                'a': ['a.i', 'a.ii', 'a.iii']
            },
            'nrows': 2,
            'ncols': 3,
        }
    },
    {
        'name': 'Sub-panels (Grid Notation)',
        'code': 'a[2x3]bc/def',
        'description': 'Panel a with 2x3 grid of sub-panels',
        'expected': {
            'sub_panels': {
                'a': 6  # 2x3 = 6 sub-panels
            },
            'nrows': 2,
            'ncols': 3,
        }
    },
    {
        'name': 'Absolute Inset',
        'code': 'a{0.6,0.6,0.35,0.35}bc/def',
        'description': 'Panel a with an absolute positioned inset',
        'expected': {
            'insets': {
                'a': [{'type': 'absolute', 'bounds': (0.6, 0.6, 0.35, 0.35)}]
            }
        }
    },
    {
        'name': 'Grid Inset',
        'code': 'a<ab/cd>ef/gh',
        'description': 'Panel a with a grid inset (2x2 inside)',
        'expected': {
            'insets': {
                'a': [{'type': 'grid', 'panels': ['a', 'b', 'c', 'd']}]
            },
            'nrows': 2,
            'ncols': 2,
        }
    },
    {
        'name': 'Complex Mixed Layout',
        'code': '[top:aa/bb]/[bottom:c[2x2]/de]',
        'description': 'Two sections with sub-panels and mixed sizes',
        'expected': {
            'sections': ['top', 'bottom'],
            'sub_panels': {
                'c': 4  # 2x2 grid
            }
        }
    },
    {
        'name': 'Nature Classic Layout',
        'code': 'aabc/aade/aaff',
        'description': 'Classic Nature figure with large left panel',
        'expected': {
            'nrows': 3,
            'ncols': 4,
            'spans': {
                'a': {'rowspan': 3, 'colspan': 2},
            }
        }
    },
    {
        'name': 'Multiple Insets',
        'code': 'a{0.1,0.1,0.2,0.2}{0.7,0.7,0.25,0.25}bcd/efgh',
        'description': 'Panel a with two insets at different positions',
        'expected': {
            'insets': {
                'a': 2  # Two insets
            },
            'nrows': 2,
            'ncols': 4,
        }
    },
]


# ============================================================================
# Unit Tests
# ============================================================================

def run_tests():
    """Run unit tests for the layout parser."""
    import unittest

    class TestLayoutCodeParser(unittest.TestCase):
        """Test cases for LayoutCodeParser."""

        def setUp(self):
            self.parser = LayoutCodeParser()

        # ---- Basic Grid Tests ----

        def test_basic_2x2_grid(self):
            """Test parsing a basic 2x2 grid."""
            tree = self.parser.parse('ab/cd')

            self.assertEqual(tree.nrows, 2)
            self.assertEqual(tree.ncols, 2)
            self.assertEqual(len(tree.root.children), 4)

            panel_ids = tree.get_all_panel_ids()
            self.assertIn('a', panel_ids)
            self.assertIn('b', panel_ids)
            self.assertIn('c', panel_ids)
            self.assertIn('d', panel_ids)

        def test_mixed_size_grid(self):
            """Test parsing a grid with mixed panel sizes."""
            tree = self.parser.parse('aab/aac/ddd')

            self.assertEqual(tree.nrows, 3)
            self.assertEqual(tree.ncols, 3)

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(panel_a.rowspan, 2)
            self.assertEqual(panel_a.colspan, 2)

            panel_d = tree.get_panel('d')
            self.assertIsNotNone(panel_d)
            self.assertEqual(panel_d.rowspan, 1)
            self.assertEqual(panel_d.colspan, 3)

        def test_row_separator_variants(self):
            """Test different row separators."""
            # Forward slash
            tree1 = self.parser.parse('ab/cd')
            # Newline
            tree2 = self.parser.parse('ab\ncd')

            self.assertEqual(tree1.nrows, tree2.nrows)
            self.assertEqual(tree1.ncols, tree2.ncols)

        # ---- Section Tests ----

        def test_named_section(self):
            """Test parsing a named section."""
            tree = self.parser.parse('[header:ab/cd]')

            self.assertEqual(len(tree.root.children), 1)

            section = tree.root.children[0]
            self.assertEqual(section.node_type, NodeType.SECTION)
            self.assertEqual(section.id, 'header')
            self.assertEqual(len(section.children), 4)

        def test_multiple_sections(self):
            """Test parsing multiple sections."""
            tree = self.parser.parse('[top:ab]/[bottom:cd]')

            self.assertEqual(len(tree.root.children), 2)

            top = tree.root.children[0]
            bottom = tree.root.children[1]

            self.assertEqual(top.id, 'top')
            self.assertEqual(bottom.id, 'bottom')

        # ---- Sub-panel Tests ----

        def test_sub_panel_bracket_list(self):
            """Test sub-panels with bracket list notation."""
            tree = self.parser.parse('a[i,ii,iii]b/cde')

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(len(panel_a.children), 3)

            sub_ids = [c.id for c in panel_a.children]
            self.assertIn('a.i', sub_ids)
            self.assertIn('a.ii', sub_ids)
            self.assertIn('a.iii', sub_ids)

        def test_sub_panel_grid_notation(self):
            """Test sub-panels with grid size notation."""
            tree = self.parser.parse('a[2x3]bc/def')

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(len(panel_a.children), 6)

            # Check grid metadata
            grid_info = panel_a.metadata.get('sub_panel_grid', {})
            self.assertEqual(grid_info.get('nrows'), 2)
            self.assertEqual(grid_info.get('ncols'), 3)

        # ---- Inset Tests ----

        def test_absolute_inset(self):
            """Test absolute positioned inset."""
            tree = self.parser.parse('a{0.6,0.6,0.35,0.35}bc/def')

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(len(panel_a.children), 1)

            inset = panel_a.children[0]
            self.assertEqual(inset.node_type, NodeType.INSET)
            self.assertEqual(inset.metadata['type'], 'absolute')
            self.assertEqual(inset.metadata['bounds'], (0.6, 0.6, 0.35, 0.35))

        def test_grid_inset(self):
            """Test grid-based inset."""
            tree = self.parser.parse('a<ab/cd>ef/gh')

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(len(panel_a.children), 1)

            inset = panel_a.children[0]
            self.assertEqual(inset.node_type, NodeType.INSET)
            self.assertEqual(inset.metadata['type'], 'grid')
            self.assertEqual(len(inset.children), 4)

        def test_multiple_insets(self):
            """Test multiple insets on one panel."""
            tree = self.parser.parse('a{0.1,0.1,0.2,0.2}{0.7,0.7,0.25,0.25}bcd/efgh')

            panel_a = tree.get_panel('a')
            self.assertIsNotNone(panel_a)
            self.assertEqual(len(panel_a.children), 2)

        # ---- Validation Tests ----

        def test_empty_code_raises_error(self):
            """Test that empty code raises an error."""
            with self.assertRaises(LayoutSyntaxError):
                self.parser.parse('')

            with self.assertRaises(LayoutSyntaxError):
                self.parser.parse('   ')

        def test_non_rectangular_panel_raises_error(self):
            """Test that non-rectangular panels raise an error."""
            with self.assertRaises(LayoutSyntaxError):
                self.parser.parse('aab/acc')  # 'a' is not rectangular

        def test_json_serialization(self):
            """Test that tree can be serialized to/from JSON."""
            tree = self.parser.parse('aab/aac/ddd')

            # Serialize
            json_str = tree.to_json()
            self.assertIsInstance(json_str, str)

            # Deserialize
            tree2 = LayoutTree.from_json(json_str)

            self.assertEqual(tree.nrows, tree2.nrows)
            self.assertEqual(tree.ncols, tree2.ncols)
            self.assertEqual(
                tree.get_all_panel_ids(),
                tree2.get_all_panel_ids()
            )

        def test_dict_serialization(self):
            """Test that tree can be serialized to/from dict."""
            tree = self.parser.parse('a[i,ii]b/cde')

            # Serialize
            data = tree.to_dict()
            self.assertIsInstance(data, dict)

            # Deserialize
            tree2 = LayoutTree.from_dict(data)

            self.assertEqual(tree.nrows, tree2.nrows)
            self.assertEqual(tree.ncols, tree2.ncols)

        def test_complex_layout(self):
            """Test a complex mixed layout."""
            # Use a valid layout: top has aa/bb (two panels, each 2x1)
            # bottom has c[2x2]/de (panel c with 2x2 sub-panels)
            tree = self.parser.parse('[top:aa/bb]/[bottom:c[2x2]/de]')

            self.assertEqual(len(tree.root.children), 2)

            # Find sections by id (order may vary)
            section_ids = [child.id for child in tree.root.children]
            self.assertIn('top', section_ids)
            self.assertIn('bottom', section_ids)

            # Check bottom section has sub-panels
            bottom = None
            for child in tree.root.children:
                if child.id == 'bottom':
                    bottom = child
                    break

            self.assertIsNotNone(bottom)
            panel_c = None
            for child in bottom.children:
                if child.id == 'c':
                    panel_c = child
                    break

            if panel_c:
                self.assertEqual(len(panel_c.children), 4)  # 2x2 sub-panels

    class TestLayoutTreeValidator(unittest.TestCase):
        """Test cases for LayoutTreeValidator."""

        def setUp(self):
            self.validator = LayoutTreeValidator()
            self.parser = LayoutCodeParser(validate=False)

        def test_valid_layout_passes(self):
            """Test that a valid layout passes validation."""
            tree = self.parser.parse('ab/cd')
            errors = self.validator.validate(tree)
            self.assertEqual(len(errors), 0)

        def test_empty_layout_fails(self):
            """Test that empty layout fails validation."""
            tree = LayoutTree(
                root=LayoutNode(NodeType.ROOT, 'root'),
                nrows=0,
                ncols=0
            )
            errors = self.validator.validate(tree)
            self.assertTrue(len(errors) > 0)

        def test_overlapping_panels_detected(self):
            """Test that overlapping panels are detected."""
            # Create a tree with overlapping panels manually
            root = LayoutNode(NodeType.ROOT, 'root', children=[
                LayoutNode(NodeType.PANEL, 'a', row=0, col=0, rowspan=2, colspan=2),
                LayoutNode(NodeType.PANEL, 'b', row=1, col=1, rowspan=2, colspan=2),
            ])
            tree = LayoutTree(root=root, nrows=3, ncols=3)

            errors = self.validator.validate(tree)
            overlap_errors = [e for e in errors if 'overlap' in e.lower()]
            self.assertTrue(len(overlap_errors) > 0)

        def test_inset_bounds_validation(self):
            """Test that invalid inset bounds are detected."""
            root = LayoutNode(NodeType.ROOT, 'root', children=[
                LayoutNode(NodeType.PANEL, 'a', row=0, col=0, children=[
                    LayoutNode(
                        NodeType.INSET,
                        'a_inset_0',
                        metadata={'type': 'absolute', 'bounds': (0.8, 0.8, 0.5, 0.5)}
                    )
                ])
            ])
            tree = LayoutTree(root=root, nrows=1, ncols=1)

            errors = self.validator.validate(tree)
            inset_errors = [e for e in errors if 'inset' in e.lower()]
            self.assertTrue(len(inset_errors) > 0)

    # Run the tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestLayoutCodeParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLayoutTreeValidator))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def print_example_outputs():
    """Print example layout codes and their parsed outputs."""
    parser = LayoutCodeParser()

    print("=" * 80)
    print("FigCombo Layout Parser - Example Outputs")
    print("=" * 80)
    print()

    for i, example in enumerate(EXAMPLE_LAYOUT_CODES, 1):
        print(f"{i}. {example['name']}")
        print("-" * 60)
        print(f"Code:    {example['code']}")
        print(f"Desc:    {example['description']}")
        print()

        try:
            tree = parser.parse(example['code'])
            print(f"Parsed:")
            print(f"  Grid:  {tree.nrows}x{tree.ncols}")
            print(f"  Panels: {tree.get_all_panel_ids()}")

            # Show sections if present
            sections = [c for c in tree.root.children if c.node_type == NodeType.SECTION]
            if sections:
                print(f"  Sections: {[s.id for s in sections]}")

            # Show sub-panels
            for panel_id in tree.get_all_panel_ids():
                panel = tree.get_panel(panel_id)
                if panel and panel.children:
                    sub_panels = [c for c in panel.children if c.node_type == NodeType.SUB_PANEL]
                    if sub_panels:
                        print(f"  Sub-panels of '{panel_id}': {[c.id for c in sub_panels]}")

            # Show insets
            for panel_id in tree.get_all_panel_ids():
                panel = tree.get_panel(panel_id)
                if panel and panel.children:
                    insets = [c for c in panel.children if c.node_type == NodeType.INSET]
                    if insets:
                        print(f"  Insets in '{panel_id}': {len(insets)}")
                        for inset in insets:
                            if inset.metadata.get('type') == 'absolute':
                                print(f"    - Absolute: {inset.metadata['bounds']}")

            # Show JSON output (truncated)
            json_output = tree.to_json(indent=2)
            if len(json_output) > 500:
                json_output = json_output[:500] + "\n  ... (truncated)"
            print(f"\nJSON Output:\n{json_output}")

        except LayoutError as e:
            print(f"Error: {e}")

        print()
        print("=" * 80)
        print()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run unit tests
        success = run_tests()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == 'examples':
        # Print example outputs
        print_example_outputs()
    else:
        # Default: show help
        print("""
FigCombo Layout Code Parser
===========================

Usage:
    python layout_parser.py test      # Run unit tests
    python layout_parser.py examples  # Show example layouts

Layout Code Syntax:
-------------------

1. Basic Grid:
   ab/cd          -> 2x2 grid with panels a, b, c, d
   aab/aac/ddd    -> Panel 'a' spans 2x2, 'd' spans full width

2. Named Sections:
   [header:ab/cd] -> Creates section 'header' containing grid

3. Sub-panels:
   a[i,ii,iii]    -> Panel 'a' with 3 sub-panels
   a[2x3]         -> Panel 'a' with 2x3 grid of sub-panels

4. Insets:
   a{0.6,0.6,0.35,0.35} -> Absolute positioned inset at (x,y,w,h)
   a<ab/cd>       -> Grid inset inside panel 'a'

Examples:
---------
""")
        for ex in EXAMPLE_LAYOUT_CODES:
            print(f"  {ex['name']:<30} : {ex['code']}")
        print()
