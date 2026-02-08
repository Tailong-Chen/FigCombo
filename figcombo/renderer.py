"""Renderer - compose all panels into a single matplotlib Figure."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure as MplFigure

from figcombo.layout.types import LayoutGrid
from figcombo.layout.grid import compute_grid_spec, SubplotSpec
from figcombo.panels.base import BasePanel
from figcombo.styles.manager import StyleManager
from figcombo.utils import mm_to_inch


class Renderer:
    """Renders a composite figure from layout, panels, and style.

    Parameters
    ----------
    layout : LayoutGrid
        The parsed layout grid.
    panels : dict
        Mapping of panel label to BasePanel instance.
    style : StyleManager
        Style configuration.
    figure_width_mm : float
        Total figure width in mm.
    figure_height_mm : float
        Total figure height in mm.
    spacing_mm : float
        Gap between panels in mm. Default 1.5 (tight like real Nature figures).
    auto_label : bool
        Whether to automatically add panel labels.
    """

    def __init__(
        self,
        layout: LayoutGrid,
        panels: dict[str, BasePanel],
        style: StyleManager,
        figure_width_mm: float,
        figure_height_mm: float,
        spacing_mm: float = 1.5,
        auto_label: bool = True,
    ):
        self.layout = layout
        self.panels = panels
        self.style = style
        self.figure_width_mm = figure_width_mm
        self.figure_height_mm = figure_height_mm
        self.spacing_mm = spacing_mm
        self.auto_label = auto_label

        self._mpl_figure: MplFigure | None = None
        self._axes: dict[str, Any] = {}

    def render(self) -> MplFigure:
        """Render the complete composite figure.

        Returns
        -------
        matplotlib.figure.Figure
            The rendered figure.
        """
        # Apply global style
        self.style.apply()

        # Compute figure size in inches
        fig_w = mm_to_inch(self.figure_width_mm)
        fig_h = mm_to_inch(self.figure_height_mm)

        # Create figure with constrained layout for tight packing
        self._mpl_figure = plt.figure(
            figsize=(fig_w, fig_h),
            constrained_layout=True,
        )

        # Tight padding - minimal whitespace like real Nature figures
        spacing_inch = mm_to_inch(self.spacing_mm)
        self._mpl_figure.set_constrained_layout_pads(
            w_pad=spacing_inch * 0.3,
            h_pad=spacing_inch * 0.3,
            wspace=spacing_inch * 0.4 / fig_w,
            hspace=spacing_inch * 0.4 / fig_h,
        )

        # Create GridSpec
        gs = self._mpl_figure.add_gridspec(
            nrows=self.layout.nrows,
            ncols=self.layout.ncols,
            height_ratios=self.layout.row_ratios,
            width_ratios=self.layout.col_ratios,
        )

        # Build subplot specs
        subplot_specs: dict[str, SubplotSpec] = {}
        for label, panel_pos in self.layout.panels.items():
            subplot_specs[label] = SubplotSpec(
                label=label,
                row_slice=slice(panel_pos.row, panel_pos.row_end),
                col_slice=slice(panel_pos.col, panel_pos.col_end),
            )

        # Render each panel
        for label in self.layout.labels:
            if label not in self.panels:
                continue

            spec = subplot_specs[label]
            panel = self.panels[label]

            # Check if this is a sub-panel container
            from figcombo.panels.composite_panel import CompositePanel
            if isinstance(panel, CompositePanel):
                # Create a nested GridSpec for sub-panels
                sub_gs = gs[spec.row_slice, spec.col_slice].subgridspec(
                    panel.nrows, panel.ncols,
                    wspace=0.05, hspace=0.05,
                )
                panel.render_into_gridspec(self._mpl_figure, sub_gs)
                # Add panel label to the first sub-axes
                if self.auto_label and panel.axes:
                    first_ax = list(panel.axes.values())[0]
                    self._add_panel_label(first_ax, label)
                self._axes[label] = panel.axes
            else:
                ax = self._mpl_figure.add_subplot(
                    gs[spec.row_slice, spec.col_slice]
                )
                self._axes[label] = ax
                panel.render(ax)

                if self.auto_label:
                    self._add_panel_label(ax, label)

        return self._mpl_figure

    def _add_panel_label(self, ax: Any, label: str) -> None:
        """Add a panel label (a, b, c...) to the top-left of the axes.

        Positioned tightly at the top-left corner, matching Nature style.
        """
        formatted = self.style.format_label(label)
        label_kwargs = self.style.get_label_kwargs()

        # Tight positioning: just outside the top-left corner
        ax.text(
            -0.05, 1.05,
            formatted,
            transform=ax.transAxes,
            va='bottom',
            ha='right',
            **label_kwargs,
        )

    @property
    def figure(self) -> MplFigure | None:
        """The rendered matplotlib Figure, or None if not yet rendered."""
        return self._mpl_figure

    @property
    def axes(self) -> dict[str, Any]:
        """Dict of panel label -> matplotlib Axes."""
        return self._axes
