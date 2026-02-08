"""Pre-defined layout templates for common multi-panel figure arrangements."""

from __future__ import annotations

from typing import Any

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
}


def list_templates(num_panels: int | None = None) -> str:
    """List available layout templates.

    Parameters
    ----------
    num_panels : int, optional
        If given, filter templates to only show those with this many panels.

    Returns
    -------
    str
        Formatted string listing available templates.
    """
    lines = []
    for key, tmpl in sorted(LAYOUT_TEMPLATES.items()):
        if num_panels is not None and tmpl.get('panels', 0) != num_panels:
            continue
        desc = tmpl.get('description', '')
        n = tmpl.get('panels', '?')
        size = tmpl.get('recommended_size', '?')
        lines.append(f"  {key:30s} [{n} panels, {size}] {desc}")

    header = "Available layout templates"
    if num_panels is not None:
        header += f" ({num_panels} panels)"
    header += ":"

    return header + "\n" + "\n".join(lines) if lines else f"No templates found for {num_panels} panels."


def get_template(name: str) -> dict[str, Any]:
    """Get a layout template by name.

    Raises ValueError if template not found.
    """
    if name not in LAYOUT_TEMPLATES:
        raise ValueError(
            f"Unknown template '{name}'. Use list_templates() to see available templates."
        )
    return LAYOUT_TEMPLATES[name].copy()
