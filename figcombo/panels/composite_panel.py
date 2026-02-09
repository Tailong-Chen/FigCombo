"""CompositePanel - a panel containing sub-panels (i), (ii), etc."""

from __future__ import annotations

from typing import Any, Optional

from matplotlib.axes import Axes
from matplotlib.figure import Figure as MplFigure
from matplotlib.gridspec import SubplotSpec as MplSubplotSpec

from figcombo.panels.base import BasePanel


class CompositePanel(BasePanel):
    """A panel that contains multiple sub-panels arranged in a grid.

    Use this for panels like Q(i), Q(ii) or R(i), R(ii) where one
    logical panel contains multiple images or plots side by side.

    Parameters
    ----------
    nrows : int
        Number of rows in the sub-panel grid.
    ncols : int
        Number of columns in the sub-panel grid.
    sub_labels : list of str, optional
        Labels for sub-panels, e.g. ['(i)', '(ii)'] or ['i', 'ii'].
        If None, no sub-labels are added.
    show_sub_labels : bool
        Whether to show sub-panel labels. Default True.

    Examples
    --------
    >>> comp = CompositePanel(1, 2, sub_labels=['(i)', '(ii)'])
    >>> comp[0] = ImagePanel('sem_before.tif')
    >>> comp[1] = ImagePanel('sem_after.tif')
    >>> fig['q'] = comp

    Or using the helper:

    >>> fig['q'] = CompositePanel.from_panels(
    ...     ImagePanel('before.tif'),
    ...     ImagePanel('after.tif'),
    ...     sub_labels=['(i)', '(ii)'],
    ... )
    """

    def __init__(
        self,
        nrows: int = 1,
        ncols: int = 2,
        sub_labels: list[str] | None = None,
        show_sub_labels: bool = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.nrows = nrows
        self.ncols = ncols
        self.sub_labels = sub_labels
        self.show_sub_labels = show_sub_labels
        self._sub_panels: dict[int, BasePanel] = {}
        self._axes_dict: dict[int, Axes] = {}

    def __setitem__(self, index: int, panel: BasePanel) -> None:
        """Set a sub-panel by index."""
        self._sub_panels[index] = panel

    def __getitem__(self, index: int) -> BasePanel:
        """Get a sub-panel by index."""
        return self._sub_panels[index]

    @classmethod
    def from_panels(
        cls,
        *panels: BasePanel,
        nrows: int | None = None,
        ncols: int | None = None,
        sub_labels: list[str] | None = None,
        **kwargs: Any,
    ) -> 'CompositePanel':
        """Create a CompositePanel from a sequence of panels.

        If nrows/ncols not specified, arranges horizontally (1 row).
        """
        n = len(panels)
        if nrows is None and ncols is None:
            nrows = 1
            ncols = n
        elif nrows is None:
            nrows = (n + ncols - 1) // ncols
        elif ncols is None:
            ncols = (n + nrows - 1) // nrows

        comp = cls(nrows=nrows, ncols=ncols, sub_labels=sub_labels, **kwargs)
        for i, panel in enumerate(panels):
            comp[i] = panel
        return comp

    def render(self, ax: Axes) -> None:
        """Render sub-panels into a single axes using inset_axes.

        This is the fallback when not using render_into_gridspec.
        """
        ax.set_axis_off()

        total = self.nrows * self.ncols
        for idx in range(total):
            if idx not in self._sub_panels:
                continue

            r = idx // self.ncols
            c = idx % self.ncols

            # Calculate position within the axes
            gap = 0.03
            w = (1.0 - gap * (self.ncols - 1)) / self.ncols
            h = (1.0 - gap * (self.nrows - 1)) / self.nrows
            x0 = c * (w + gap)
            y0 = 1.0 - (r + 1) * h - r * gap

            sub_ax = ax.inset_axes([x0, y0, w, h])
            self._sub_panels[idx].render(sub_ax)
            self._axes_dict[idx] = sub_ax

            # Sub-label
            if self.show_sub_labels and self.sub_labels and idx < len(self.sub_labels):
                sub_ax.set_title(
                    self.sub_labels[idx],
                    fontsize=6, fontweight='bold',
                    loc='left', pad=1,
                )

    def render_into_gridspec(self, fig: MplFigure, sub_gs: Any) -> None:
        """Render sub-panels into a matplotlib SubGridSpec.

        Called by the Renderer when it detects a CompositePanel.
        After rendering, if a sub-panel turned off its axes (e.g. SEM
        images), we strip any residual ticks/spines so they don't leak
        into the layout engine.
        """
        total = self.nrows * self.ncols
        for idx in range(total):
            if idx not in self._sub_panels:
                continue

            r = idx // self.ncols
            c = idx % self.ncols

            ax = fig.add_subplot(sub_gs[r, c])
            self._sub_panels[idx].render(ax)
            self._axes_dict[idx] = ax

            # If the plot function turned off the axes, make sure all
            # tick labels / spines are truly gone so constrained_layout
            # doesn't reserve space for them.
            if not ax.axison:
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

            if self.show_sub_labels and self.sub_labels and idx < len(self.sub_labels):
                ax.set_title(
                    self.sub_labels[idx],
                    fontsize=6, fontweight='bold',
                    loc='left', pad=1,
                )

    @property
    def axes(self) -> dict[int, Axes]:
        """Dict of sub-panel index -> matplotlib Axes."""
        return self._axes_dict

    def validate(self) -> list[str]:
        errors = []
        if not self._sub_panels:
            errors.append("CompositePanel has no sub-panels assigned")
        for idx, panel in self._sub_panels.items():
            sub_errors = panel.validate()
            for e in sub_errors:
                label = ''
                if self.sub_labels and idx < len(self.sub_labels):
                    label = self.sub_labels[idx]
                else:
                    label = str(idx)
                errors.append(f"Sub-panel {label}: {e}")
        return errors

    def __repr__(self) -> str:
        n = len(self._sub_panels)
        return f"CompositePanel({self.nrows}x{self.ncols}, {n} sub-panels)"
