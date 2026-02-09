"""Pre-defined layout templates for common multi-panel figure arrangements."""

from __future__ import annotations

from typing import Any

# Nature journal standard width (mm)
NATURE_DOUBLE_COLUMN = 183  # mm
NATURE_SINGLE_COLUMN = 89  # mm

LAYOUT_TEMPLATES: dict[str, dict[str, Any]] = {
    # ---- 2 panel layouts ----
    '2_side_by_side': {
        'ascii': 'a b',
        'description': 'Two panels side by side',
        'panels': 2,
        'recommended_size': 'double',
    },
    '2_stacked': {
        'ascii': 'a\nb',
        'description': 'Two panels stacked vertically',
        'panels': 2,
        'recommended_size': 'single',
    },

    # ---- 3 panel layouts ----
    '3_top1_bottom2': {
        'ascii': 'aa\nbc',
        'description': 'Wide top panel + two bottom panels',
        'panels': 3,
        'recommended_size': 'double',
    },
    '3_left1_right2': {
        'ascii': 'ab\nac',
        'description': 'Large left panel + two right panels',
        'panels': 3,
        'recommended_size': 'double',
    },
    '3_row': {
        'ascii': 'a b c',
        'description': 'Three panels in a row',
        'panels': 3,
        'recommended_size': 'double',
    },
    '3_bottom1_top2': {
        'ascii': 'ab\ncc',
        'description': 'Two top panels + wide bottom panel',
        'panels': 3,
        'recommended_size': 'double',
    },

    # ---- 4 panel layouts ----
    '4_grid': {
        'ascii': 'ab\ncd',
        'description': 'Classic 2x2 grid',
        'panels': 4,
        'recommended_size': 'double',
    },
    '4_top1_bottom3': {
        'ascii': 'aaa\nbcd',
        'description': 'Wide top panel + three bottom panels',
        'panels': 4,
        'recommended_size': 'double',
    },
    '4_left1_right3': {
        'ascii': 'ab\nac\nad',
        'description': 'Large left panel + three stacked right panels',
        'panels': 4,
        'recommended_size': 'double',
    },
    '4_row': {
        'ascii': 'a b c d',
        'description': 'Four panels in a row',
        'panels': 4,
        'recommended_size': 'double',
    },
    '4_column': {
        'ascii': 'a\nb\nc\nd',
        'description': 'Four panels in a column',
        'panels': 4,
        'recommended_size': 'single',
    },

    # ---- 5 panel layouts ----
    '5_top2_bottom3': {
        'ascii': 'aabb.\ncdeff',
        'description': 'Two large top panels + three bottom panels',
        'panels': 5,
        'recommended_size': 'double',
    },
    '5_mixed': {
        'ascii': 'aab\naac\ndde',
        'description': 'Large top-left + two right + two bottom panels',
        'panels': 5,
        'recommended_size': 'double',
    },
    '5_top1_mid2_bottom2': {
        'ascii': 'aa\nbc\nde',
        'description': 'Wide top + 2 middle + 2 bottom panels',
        'panels': 5,
        'recommended_size': 'double',
    },

    # ---- 6 panel layouts ----
    '6_grid_3x2': {
        'ascii': 'ab\ncd\nef',
        'description': '3x2 grid (classic Nature 6-panel)',
        'panels': 6,
        'recommended_size': 'double',
    },
    '6_grid_2x3': {
        'ascii': 'abc\ndef',
        'description': '2x3 wide grid',
        'panels': 6,
        'recommended_size': 'double',
    },
    '6_top2_bottom4': {
        'ascii': 'aabb\ncdef',
        'description': 'Two large top + four bottom panels',
        'panels': 6,
        'recommended_size': 'double',
    },

    # ---- 8 panel layouts ----
    '8_grid_2x4': {
        'ascii': 'abcd\nefgh',
        'description': '2x4 grid',
        'panels': 8,
        'recommended_size': 'double',
    },
    '8_grid_4x2': {
        'ascii': 'ab\ncd\nef\ngh',
        'description': '4x2 grid',
        'panels': 8,
        'recommended_size': 'double',
    },

    # ---- Complex mixed layouts (Nature classics) ----
    'nature_classic_5': {
        'ascii': 'aabc\naade',
        'description': 'Nature classic: large left + 2x2 right',
        'panels': 5,
        'recommended_size': 'double',
    },
    'nature_classic_7': {
        'ascii': 'aabcc\nddeef\nddeeg',
        'description': 'Nature classic: three columns, mixed heights',
        'panels': 7,
        'recommended_size': 'double',
    },
    'nature_image_quant': {
        'ascii': 'aab\naac\naad',
        'description': 'Large image left + three quantifications right',
        'panels': 4,
        'recommended_size': 'double',
    },

    # ==== Nature Journal Advanced Templates (183mm double column) ====

    # ---- Grid layouts ----
    'nature_2x2': {
        'name': 'nature_2x2',
        'description': 'Standard 2x2 grid for Nature double column (183mm)',
        'ascii': """
+--------+--------+
|   A    |   B    |
|        |        |
+--------+--------+
|   C    |   D    |
|        |        |
+--------+--------+""",
        'panels': 4,
        'recommended_size': 'double',
        'category': 'grid',
        'recommended_panels': 'Four equal-sized panels ideal for related experiments, time series, or condition comparisons. Each panel approximately 88mm wide.',
    },
    'nature_3x2': {
        'name': 'nature_3x2',
        'description': '3 columns x 2 rows grid for comprehensive data presentation',
        'ascii': """
+-------+-------+-------+
|   A   |   B   |   C   |
|       |       |       |
+-------+-------+-------+
|   D   |   E   |   F   |
|       |       |       |
+-------+-------+-------+""",
        'panels': 6,
        'recommended_size': 'double',
        'category': 'grid',
        'recommended_panels': 'Six panels for extensive condition screening, dose-response series, or multi-timepoint experiments. Each panel approximately 58mm wide.',
    },
    'nature_4x2': {
        'name': 'nature_4x2',
        'description': '4 columns x 2 rows for high-density data presentation',
        'ascii': """
+------+------+------+------+
|  A   |  B   |  C   |  D   |
|      |      |      |      |
+------+------+------+------+
|  E   |  F   |  G   |  H   |
|      |      |      |      |
+------+------+------+------+""",
        'panels': 8,
        'recommended_size': 'double',
        'category': 'grid',
        'recommended_panels': 'Eight compact panels for comprehensive screens, library analysis, or extensive controls. Each panel approximately 43mm wide.',
    },

    # ---- Complex layouts ----
    'nature_l_shape': {
        'name': 'nature_l_shape',
        'description': 'L-shaped layout with large main panel and side panels',
        'ascii': """
+--------------+-------+
|              |   B   |
|              +-------+
|      A       |-------|
|              |   C   |
|              +-------+
|              |-------|
|              |   D   |
+--------------+-------+""",
        'panels': 4,
        'recommended_size': 'double',
        'category': 'complex',
        'recommended_panels': 'Large main panel (A) for primary data (e.g., microscopy, Western blot) with three smaller panels (B-D) for quantification, controls, or related analyses.',
    },
    'nature_vertical_split': {
        'name': 'nature_vertical_split',
        'description': 'Vertical split with two large equal panels side by side',
        'ascii': """
+----------------+----------------+
|                |                |
|       A        |       B        |
|                |                |
|                |                |
|                |                |
+----------------+----------------+""",
        'panels': 2,
        'recommended_size': 'double',
        'category': 'complex',
        'recommended_panels': 'Two large panels for comparing major experimental conditions, before/after treatments, or wild-type vs mutant. Each panel approximately 89mm wide.',
    },
    'nature_horizontal_split': {
        'name': 'nature_horizontal_split',
        'description': 'Horizontal split with two large stacked panels',
        'ascii': """
+---------------------------+
|                           |
|             A             |
|                           |
+---------------------------+
|                           |
|             B             |
|                           |
+---------------------------+""",
        'panels': 2,
        'recommended_size': 'double',
        'category': 'complex',
        'recommended_panels': 'Two full-width panels for sequential data presentation, experimental workflow stages, or related high-resolution images.',
    },
    'nature_main_with_insets': {
        'name': 'nature_main_with_insets',
        'description': 'Main panel with multiple inset panels for detail views',
        'ascii': """
+------------------+------+------+
|                  |  B   |  C   |
|                  +------+------+
|        A         |------|------|
|                  |  D   |  E   |
|                  +------+------+
|                  |------|------|
|                  |  F   |  G   |
+------------------+------+------+""",
        'panels': 7,
        'recommended_size': 'double',
        'category': 'complex',
        'recommended_panels': 'Large main panel with up to six inset panels for zoomed regions, channel splits, quantification, or orthogonal views. Ideal for microscopy with detailed analysis.',
    },
    'nature_multi_row': {
        'name': 'nature_multi_row',
        'description': 'Multi-row complex layout for 6-8 subpanels with hierarchy',
        'ascii': """
+--------+--------+----------------+
|   A    |   B    |       C        |
+--------+--------+--------+-------+
|   D    |   E    |   F    |   G   |
+--------+--------+--------+-------+
|              H                 |
+--------------------------------+""",
        'panels': 8,
        'recommended_size': 'double',
        'category': 'complex',
        'recommended_panels': 'Hierarchical layout with mixed panel sizes. Top row for primary data, middle row for supporting experiments, bottom for summary/quantification.',
    },

    # ---- Specialized layouts ----
    'nature_western_blot': {
        'name': 'nature_western_blot',
        'description': 'Optimized layout for Western blot figures with quantification',
        'ascii': """
+--------------------------------+
|                                |
|          BLOT PANEL A          |
|      (Multiple lanes/bands)    |
|                                |
+--------------------------------+
+--------------------------------+
|                                |
|          BLOT PANEL B          |
|      (Loading control)         |
|                                |
+--------------------------------+
+--------+--------+--------+-----+
| Quant A| Quant B| Quant C| ... |
+--------+--------+--------+-----+""",
        'panels': 5,
        'recommended_size': 'double',
        'category': 'specialized',
        'recommended_panels': 'Dedicated Western blot layout: full-width blot panels with molecular weight markers, followed by quantification bar charts. Supports multiple blots with their controls.',
    },
    'nature_microscopy_grid': {
        'name': 'nature_microscopy_grid',
        'description': 'Microscopy-optimized grid with scale bars and labels',
        'ascii': """
2x2 Configuration:
+--------------+--------------+
|   A (DAPI)   |  B (Channel) |
|              |              |
+--------------+--------------+
|  C (Channel) |  D (Merge)   |
|              |              |
+--------------+--------------+

3x3 Configuration:
+--------+--------+--------+
|   A    |   B    |   C    |
|        |        |        |
+--------+--------+--------+
|   D    |   E    |   F    |
|        |        |        |
+--------+--------+--------+
|   G    |   H    |   I    |
|        |        |        |
+--------+--------+--------+""",
        'panels': 9,
        'recommended_size': 'double',
        'category': 'specialized',
        'recommended_panels': 'Microscopy-specific layout supporting 2x2 (4 panels) or 3x3 (9 panels) configurations. Optimized for multi-channel fluorescence with consistent scale bars and channel labels.',
    },
    'nature_figure1': {
        'name': 'nature_figure1',
        'description': 'Classic Figure 1 layout with schematic and key data',
        'ascii': """
+--------------------------------+
|                                |
|     SCHEMATIC / OVERVIEW       |
|                                |
|             (A)                |
|                                |
+--------------------------------+
+--------------+-----------------+
|              |                 |
|      B       |        C        |
|  (Key Exp)   |   (Validation)  |
|              |                 |
+--------------+-----------------+
+--------+--------+--------+------+
|   D    |   E    |   F    |  G   |
+--------+--------+--------+------+""",
        'panels': 7,
        'recommended_size': 'double',
        'category': 'specialized',
        'recommended_panels': 'Typical Figure 1 layout: large schematic/overview at top, key experimental data in middle, supporting panels at bottom. Perfect for introducing study system and main findings.',
    },
    'nature_supplementary': {
        'name': 'nature_supplementary',
        'description': 'Supplementary figure layout with uniform panel sizes',
        'ascii': """
+--------+--------+--------+--------+
|   A    |   B    |   C    |   D    |
|        |        |        |        |
+--------+--------+--------+--------+
|   E    |   F    |   G    |   H    |
|        |        |        |        |
+--------+--------+--------+--------+
|   I    |   J    |   K    |   L    |
|        |        |        |        |
+--------+--------+--------+--------+""",
        'panels': 12,
        'recommended_size': 'double',
        'category': 'specialized',
        'recommended_panels': 'Dense uniform grid optimized for supplementary figures with many panels. Supports 12+ panels in compact 4x3 or 3x4 arrangements. Ideal for extended data, additional controls, or replicate experiments.',
    },
}


def list_templates(
    num_panels: int | None = None,
    category: str | None = None,
    show_details: bool = False,
) -> str:
    """List available layout templates.

    Parameters
    ----------
    num_panels : int, optional
        If given, filter templates to only show those with this many panels.
    category : str, optional
        If given, filter templates by category ('grid', 'complex', 'specialized').
    show_details : bool, default False
        If True, include ASCII art and recommended panel descriptions.

    Returns
    -------
    str
        Formatted string listing available templates.
    """
    lines = []
    categories_found = set()

    for key, tmpl in sorted(LAYOUT_TEMPLATES.items()):
        # Filter by number of panels
        if num_panels is not None and tmpl.get('panels', 0) != num_panels:
            continue
        # Filter by category
        tmpl_category = tmpl.get('category', 'basic')
        categories_found.add(tmpl_category)
        if category is not None and tmpl_category != category:
            continue

        desc = tmpl.get('description', '')
        n = tmpl.get('panels', '?')
        size = tmpl.get('recommended_size', '?')
        cat = tmpl.get('category', 'basic')

        lines.append(f"  {key:35s} [{n} panels, {size:7s}, {cat:12s}] {desc}")

        if show_details:
            # Add ASCII art
            ascii_art = tmpl.get('ascii', '')
            if ascii_art:
                lines.append('')
                for line in ascii_art.strip().split('\n'):
                    lines.append(f"      {line}")
                lines.append('')

            # Add recommended panels description
            rec_panels = tmpl.get('recommended_panels', '')
            if rec_panels:
                lines.append(f"      Recommended use: {rec_panels}")
                lines.append('')

    # Build header
    header_parts = ["Available layout templates"]
    if num_panels is not None:
        header_parts.append(f"({num_panels} panels)")
    if category is not None:
        header_parts.append(f"[category: {category}]")
    header = " ".join(header_parts) + ":"

    # Add category summary if no specific category filter
    if category is None and not show_details:
        lines.append('')
        lines.append(f"  Categories: {', '.join(sorted(categories_found))}")
        lines.append("  Use category='name' to filter, show_details=True for full info")

    return header + "\n" + "\n".join(lines) if lines else f"No templates found matching criteria."


def get_templates_by_category(category: str) -> dict[str, dict[str, Any]]:
    """Get all templates belonging to a specific category.

    Parameters
    ----------
    category : str
        Category name ('grid', 'complex', 'specialized', 'basic').

    Returns
    -------
    dict
        Dictionary of template names to template data.
    """
    return {
        key: tmpl.copy()
        for key, tmpl in LAYOUT_TEMPLATES.items()
        if tmpl.get('category', 'basic') == category
    }


def get_nature_templates() -> dict[str, dict[str, Any]]:
    """Get all Nature journal optimized templates.

    Returns
    -------
    dict
        Dictionary of Nature template names to template data.
    """
    return {
        key: tmpl.copy()
        for key, tmpl in LAYOUT_TEMPLATES.items()
        if key.startswith('nature_')
    }


def get_template(name: str) -> dict[str, Any]:
    """Get a layout template by name.

    Raises ValueError if template not found.
    """
    if name not in LAYOUT_TEMPLATES:
        raise ValueError(
            f"Unknown template '{name}'. Use list_templates() to see available templates."
        )
    return LAYOUT_TEMPLATES[name].copy()
