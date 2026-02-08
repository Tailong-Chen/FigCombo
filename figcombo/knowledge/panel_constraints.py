"""Panel size constraints, aspect ratios, and spacing recommendations."""

from __future__ import annotations

from typing import Optional

# Recommended aspect ratios (width : height) for different plot types
ASPECT_RATIOS: dict[str, Optional[tuple[float, float]]] = {
    'bar':        (1.0, 0.8),
    'bar_h':      (0.8, 1.0),     # horizontal bar
    'box':        (0.8, 1.0),
    'violin':     (0.8, 1.0),
    'scatter':    (1.0, 1.0),
    'line':       (1.5, 1.0),
    'heatmap':    (1.0, 1.0),
    'histogram':  (1.2, 1.0),
    'pie':        (1.0, 1.0),
    'volcano':    (1.0, 1.2),
    'survival':   (1.3, 1.0),
    'forest':     (0.7, 1.0),     # forest plot
    'waterfall':  (1.0, 1.2),
    'dot':        (0.8, 1.0),
    'strip':      (0.8, 1.0),
    'image':      None,           # preserve original aspect ratio
}

# Minimum panel sizes in mm - below these, text becomes unreadable
PANEL_MIN_SIZE = {
    'width': 25,                  # mm - absolute minimum panel width
    'height': 20,                 # mm - absolute minimum panel height
    'plot_min_width': 35,         # mm - minimum for panels containing plots with axes
    'plot_min_height': 30,        # mm - minimum for panels containing plots with axes
    'image_min_width': 20,        # mm - images can be smaller
    'image_min_height': 15,       # mm
}

# Recommended panel sizes in mm
PANEL_RECOMMENDED_SIZE = {
    'small':  (40, 35),           # for simple bar/box plots
    'medium': (60, 50),           # standard plot size
    'large':  (85, 70),           # detailed plots or large images
    'wide':   (90, 40),           # wide panoramic plots (line, time series)
    'tall':   (45, 80),           # tall plots (forest plot, vertical bar)
}

# Spacing defaults in mm
SPACING = {
    'panel_gap_h': 3.0,           # horizontal gap between panels
    'panel_gap_v': 3.0,           # vertical gap between panels
    'label_offset_x': -2.0,      # panel label x offset from panel edge
    'label_offset_y': 2.0,       # panel label y offset from panel top
    'margin_left': 2.0,
    'margin_right': 2.0,
    'margin_top': 3.0,           # extra top margin for panel labels
    'margin_bottom': 2.0,
}


def get_aspect_ratio(plot_type: str) -> Optional[tuple[float, float]]:
    """Get recommended aspect ratio for a plot type.

    Returns None for image type (preserve original ratio).
    Returns (1.0, 1.0) for unknown types.
    """
    return ASPECT_RATIOS.get(plot_type, (1.0, 1.0))


def check_panel_size(width_mm: float, height_mm: float, panel_type: str = 'plot') -> list[str]:
    """Check if panel size meets minimum requirements.

    Returns list of warning messages (empty if OK).
    """
    warnings = []

    if panel_type == 'image':
        min_w = PANEL_MIN_SIZE['image_min_width']
        min_h = PANEL_MIN_SIZE['image_min_height']
    else:
        min_w = PANEL_MIN_SIZE['plot_min_width']
        min_h = PANEL_MIN_SIZE['plot_min_height']

    if width_mm < PANEL_MIN_SIZE['width']:
        warnings.append(
            f"Panel width {width_mm:.1f}mm is below absolute minimum "
            f"{PANEL_MIN_SIZE['width']}mm"
        )
    elif width_mm < min_w:
        warnings.append(
            f"Panel width {width_mm:.1f}mm is below recommended minimum "
            f"{min_w}mm for {panel_type} panels"
        )

    if height_mm < PANEL_MIN_SIZE['height']:
        warnings.append(
            f"Panel height {height_mm:.1f}mm is below absolute minimum "
            f"{PANEL_MIN_SIZE['height']}mm"
        )
    elif height_mm < min_h:
        warnings.append(
            f"Panel height {height_mm:.1f}mm is below recommended minimum "
            f"{min_h}mm for {panel_type} panels"
        )

    return warnings
