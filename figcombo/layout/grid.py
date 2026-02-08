"""Grid computation: convert LayoutGrid to matplotlib GridSpec parameters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from figcombo.layout.types import LayoutGrid, PanelPosition


@dataclass
class GridSpecParams:
    """Parameters for creating a matplotlib GridSpec.

    Attributes
    ----------
    nrows : int
    ncols : int
    height_ratios : list of float
    width_ratios : list of float
    hspace : float
        Horizontal spacing as fraction of average subplot height.
    wspace : float
        Vertical spacing as fraction of average subplot width.
    """
    nrows: int
    ncols: int
    height_ratios: list[float]
    width_ratios: list[float]
    hspace: float = 0.05
    wspace: float = 0.05

    def to_dict(self) -> dict[str, Any]:
        """Convert to kwargs dict for matplotlib.gridspec.GridSpec."""
        return {
            'nrows': self.nrows,
            'ncols': self.ncols,
            'height_ratios': self.height_ratios,
            'width_ratios': self.width_ratios,
            'hspace': self.hspace,
            'wspace': self.wspace,
        }


@dataclass
class SubplotSpec:
    """Specification for a single subplot position in the GridSpec.

    Attributes
    ----------
    label : str
        Panel label.
    row_slice : slice
        Row slice for GridSpec indexing.
    col_slice : slice
        Column slice for GridSpec indexing.
    """
    label: str
    row_slice: slice
    col_slice: slice

    def __repr__(self) -> str:
        return (
            f"SubplotSpec('{self.label}', "
            f"rows={self.row_slice.start}:{self.row_slice.stop}, "
            f"cols={self.col_slice.start}:{self.col_slice.stop})"
        )


def compute_grid_spec(
    layout: LayoutGrid,
    figure_width_mm: float,
    figure_height_mm: float,
    spacing_mm: float = 3.0,
) -> tuple[GridSpecParams, dict[str, SubplotSpec]]:
    """Compute matplotlib GridSpec parameters from a LayoutGrid.

    Parameters
    ----------
    layout : LayoutGrid
        Parsed layout grid.
    figure_width_mm : float
        Total figure width in mm.
    figure_height_mm : float
        Total figure height in mm.
    spacing_mm : float
        Spacing between panels in mm.

    Returns
    -------
    gs_params : GridSpecParams
        Parameters for GridSpec creation.
    subplot_specs : dict
        Mapping of panel label to SubplotSpec.
    """
    # Convert spacing from mm to figure fraction
    hspace = spacing_mm / (figure_height_mm / layout.nrows) if layout.nrows > 1 else 0
    wspace = spacing_mm / (figure_width_mm / layout.ncols) if layout.ncols > 1 else 0

    gs_params = GridSpecParams(
        nrows=layout.nrows,
        ncols=layout.ncols,
        height_ratios=layout.row_ratios,
        width_ratios=layout.col_ratios,
        hspace=hspace,
        wspace=wspace,
    )

    # Create subplot specs for each panel
    subplot_specs: dict[str, SubplotSpec] = {}
    for label, panel in layout.panels.items():
        subplot_specs[label] = SubplotSpec(
            label=label,
            row_slice=slice(panel.row, panel.row_end),
            col_slice=slice(panel.col, panel.col_end),
        )

    return gs_params, subplot_specs


def compute_panel_sizes_mm(
    layout: LayoutGrid,
    figure_width_mm: float,
    figure_height_mm: float,
    spacing_mm: float = 3.0,
    margin_mm: float = 2.0,
) -> dict[str, tuple[float, float]]:
    """Compute actual panel sizes in mm.

    Parameters
    ----------
    layout : LayoutGrid
    figure_width_mm : float
    figure_height_mm : float
    spacing_mm : float
    margin_mm : float

    Returns
    -------
    dict
        Mapping of label to (width_mm, height_mm).
    """
    # Available space after margins
    usable_w = figure_width_mm - 2 * margin_mm
    usable_h = figure_height_mm - 2 * margin_mm

    # Subtract spacing
    total_hgap = spacing_mm * (layout.ncols - 1) if layout.ncols > 1 else 0
    total_vgap = spacing_mm * (layout.nrows - 1) if layout.nrows > 1 else 0

    content_w = usable_w - total_hgap
    content_h = usable_h - total_vgap

    # Compute individual cell sizes based on ratios
    total_col_ratio = sum(layout.col_ratios)
    total_row_ratio = sum(layout.row_ratios)

    col_widths = [(r / total_col_ratio) * content_w for r in layout.col_ratios]
    row_heights = [(r / total_row_ratio) * content_h for r in layout.row_ratios]

    # Compute panel sizes
    sizes: dict[str, tuple[float, float]] = {}
    for label, panel in layout.panels.items():
        # Sum up the columns and rows this panel spans
        w = sum(col_widths[panel.col:panel.col_end])
        if panel.colspan > 1:
            w += spacing_mm * (panel.colspan - 1)

        h = sum(row_heights[panel.row:panel.row_end])
        if panel.rowspan > 1:
            h += spacing_mm * (panel.rowspan - 1)

        sizes[label] = (w, h)

    return sizes
