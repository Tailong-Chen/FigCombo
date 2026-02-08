"""Utility functions: unit conversions, DPI calculations, etc."""

from __future__ import annotations

# Conversion constants
MM_PER_INCH = 25.4
PT_PER_INCH = 72.0


def mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / MM_PER_INCH


def inch_to_mm(inch: float) -> float:
    """Convert inches to millimeters."""
    return inch * MM_PER_INCH


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points."""
    return mm * (PT_PER_INCH / MM_PER_INCH)


def pt_to_mm(pt: float) -> float:
    """Convert points to millimeters."""
    return pt * (MM_PER_INCH / PT_PER_INCH)


def figure_size_mm(width_mm: float, height_mm: float) -> tuple[float, float]:
    """Convert figure dimensions from mm to inches (for matplotlib).

    Parameters
    ----------
    width_mm : float
        Width in millimeters.
    height_mm : float
        Height in millimeters.

    Returns
    -------
    tuple of float
        (width_inches, height_inches)
    """
    return (mm_to_inch(width_mm), mm_to_inch(height_mm))


def compute_figure_height(
    width_mm: float,
    layout_nrows: int,
    layout_ncols: int,
    row_ratios: list[float] | None = None,
    col_ratios: list[float] | None = None,
    spacing_mm: float = 3.0,
    margin_mm: float = 2.0,
) -> float:
    """Estimate figure height from width and layout proportions.

    Assumes equal cell aspect ratio (1:1 cells) unless ratios suggest otherwise.

    Parameters
    ----------
    width_mm : float
        Figure width in mm.
    layout_nrows : int
    layout_ncols : int
    row_ratios : list of float, optional
    col_ratios : list of float, optional
    spacing_mm : float
    margin_mm : float

    Returns
    -------
    float
        Estimated height in mm.
    """
    if row_ratios is None:
        row_ratios = [1.0] * layout_nrows
    if col_ratios is None:
        col_ratios = [1.0] * layout_ncols

    # Available width for content
    usable_w = width_mm - 2 * margin_mm - spacing_mm * (layout_ncols - 1)
    cell_w = usable_w / sum(col_ratios)

    # Compute height
    total_row = sum(row_ratios)
    usable_h = cell_w * total_row
    height_mm = usable_h + 2 * margin_mm + spacing_mm * (layout_nrows - 1)

    return height_mm