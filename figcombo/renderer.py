"""Renderer - compose all panels into a single matplotlib Figure."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure as MplFigure

from figcombo.layout.types import LayoutGrid
from figcombo.layout.grid import compute_grid_spec, GridSpecParams, SubplotSpec
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
        Gap between panels in mm.
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
        spacing_mm: float = 3.0,
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

        # Create figure
        self._mpl_figure = plt.figure(figsize=(fig_w, fig_h))

        # Compute grid spec
        gs_params, subplot_specs = compute_grid_spec(
            self.layout,
            self.figure_width_mm,
            self.figure_height_mm,
            self.spacing_mm,
        )

        # Create GridSpec
        gs = gridspec.GridSpec(**gs_params.to_dict(), figure=self._mpl_figure)

        # Render each panel
        for label in self.layout.labels:
            if label not in self.panels:
                continue

            spec = subplot_specs[label]
            ax = self._mpl_figure.add_subplot(
                gs[spec.row_slice, spec.col_slice]
            )
            self._axes[label] = ax

            # Render panel content
            panel = self.panels[label]
            panel.render(ax)

            # Add panel label
            if self.auto_label:
                self._add_panel_label(ax, label)

        return self._mpl_figure

    def _add_panel_label(self, ax: Any, label: str) -> None:
        """Add a panel label (a, b, c...) to the top-left of the axes."""
        formatted = self.style.format_label(label)
        label_kwargs = self.style.get_label_kwargs()

        ax.text(
            -0.1, 1.1,
            formatted,
            transform=ax.transAxes,
            va='top',
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
