"""Renderer - compose all panels into a single matplotlib Figure."""

from __future__ import annotations

import warnings
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure as MplFigure
from matplotlib.ticker import MaxNLocator

from figcombo.layout.types import LayoutGrid
from figcombo.layout.grid import SubplotSpec
from figcombo.panels.base import BasePanel
from figcombo.styles.manager import StyleManager
from figcombo.utils import mm_to_inch


class Renderer:
    """Renders a composite figure from layout, panels, and style."""

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
        """Render the complete composite figure."""
        self.style.apply()
        self._apply_tight_rc()

        fig_w = mm_to_inch(self.figure_width_mm)
        fig_h = mm_to_inch(self.figure_height_mm)

        # Adaptive margins based on font size:
        # Larger font → more margin needed for labels
        fs = self.style.font_size
        # Left margin needs room for panel labels + y-axis labels
        left_margin = 0.045 + fs * 0.003
        right_margin = 0.015
        top_margin = 0.015
        bottom_margin = 0.035 + fs * 0.002

        # wspace/hspace: fraction of average subplot size
        # More columns → need proportionally more spacing for labels
        ncols = self.layout.ncols
        nrows = self.layout.nrows
        # Each y-axis label set needs ~8mm; as fraction of panel width
        avg_panel_w_mm = self.figure_width_mm / ncols
        avg_panel_h_mm = self.figure_height_mm / nrows
        wspace = max(0.3, 10.0 / avg_panel_w_mm)  # ~10mm per gap
        hspace = max(0.3, 10.0 / avg_panel_h_mm)   # ~10mm per gap

        self._mpl_figure = plt.figure(figsize=(fig_w, fig_h))

        gs = gridspec.GridSpec(
            nrows=nrows,
            ncols=ncols,
            figure=self._mpl_figure,
            height_ratios=self.layout.row_ratios,
            width_ratios=self.layout.col_ratios,
            left=left_margin,
            right=1.0 - right_margin,
            top=1.0 - top_margin,
            bottom=bottom_margin,
            wspace=wspace,
            hspace=hspace,
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

            from figcombo.panels.composite_panel import CompositePanel
            if isinstance(panel, CompositePanel):
                sub_gs = gs[spec.row_slice, spec.col_slice].subgridspec(
                    panel.nrows, panel.ncols,
                    wspace=0.08, hspace=0.08,
                )
                panel.render_into_gridspec(self._mpl_figure, sub_gs)
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

        # Post-render: auto-adjust small panels
        self._auto_adjust_axes()

        return self._mpl_figure

    def _apply_tight_rc(self) -> None:
        """Override rcParams for ultra-tight spacing."""
        import matplotlib as mpl
        mpl.rcParams.update({
            'axes.labelpad': 1.5,
            'axes.titlepad': 2,
            'xtick.major.pad': 1.5,
            'ytick.major.pad': 1.5,
            'xtick.minor.pad': 1,
            'ytick.minor.pad': 1,
            'legend.borderpad': 0.2,
            'legend.labelspacing': 0.25,
            'legend.handlelength': 0.8,
            'legend.handletextpad': 0.3,
            'legend.columnspacing': 0.4,
        })

    def _auto_adjust_axes(self) -> None:
        """Post-render: reduce tick density and label size on small panels."""
        if self._mpl_figure is None:
            return

        fig_w_inch = self._mpl_figure.get_figwidth()
        fig_w_mm = fig_w_inch * 25.4
        fig_h_inch = self._mpl_figure.get_figheight()
        fig_h_mm = fig_h_inch * 25.4
        tick_size_small = max(4, self.style.tick_size - 1)

        for label, ax_or_dict in self._axes.items():
            if isinstance(ax_or_dict, dict):
                axes_list = list(ax_or_dict.values())
            else:
                axes_list = [ax_or_dict]

            for ax in axes_list:
                if not ax.axison:
                    continue

                bbox = ax.get_position()
                panel_w_mm = bbox.width * fig_w_mm
                panel_h_mm = bbox.height * fig_h_mm

                if panel_w_mm < 35:
                    # Reduce tick count and font
                    try:
                        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
                    except Exception:
                        pass
                    try:
                        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
                    except Exception:
                        pass
                    ax.tick_params(axis='both', labelsize=tick_size_small)

                if panel_w_mm < 25:
                    # Very small: strip axis labels entirely
                    ax.set_xlabel('')
                    ax.set_ylabel('')
                    ax.tick_params(axis='both', labelsize=max(3, tick_size_small - 1))

    def _add_panel_label(self, ax: Any, label: str) -> None:
        """Add panel label at top-left following Nature style.

        Nature style: Bold, uppercase/lowercase letter positioned at top-left
        of panel, slightly outside the plot area.
        """
        formatted = self.style.format_label(label)
        label_kwargs = self.style.get_label_kwargs()

        # Nature-style positioning: top-left, slightly outside
        # Use axes coordinates for consistent positioning across all panel sizes
        # Fixed offset in points for consistent appearance
        ax.annotate(
            formatted,
            xy=(0, 1),  # Top-left corner of axes
            xycoords='axes fraction',
            xytext=(-8, 8),  # Offset: 8 points left, 8 points up
            textcoords='offset points',
            va='bottom',
            ha='right',
            **label_kwargs,
        )

    @property
    def figure(self) -> MplFigure | None:
        return self._mpl_figure

    @property
    def axes(self) -> dict[str, Any]:
        return self._axes
