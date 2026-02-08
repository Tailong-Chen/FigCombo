"""InsetMixin - add inset plots inside any panel."""

from __future__ import annotations

from typing import Any, Callable

from matplotlib.axes import Axes


class InsetMixin:
    """Mixin to add inset plot capability to PlotPanel.

    Allows embedding small plots (bar charts, zoom views, etc.)
    inside a larger plot panel, like real Nature figures often do.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._insets: list[dict[str, Any]] = []

    def add_inset(
        self,
        plot_func: Callable,
        bounds: tuple[float, float, float, float] = (0.6, 0.6, 0.35, 0.35),
        data: Any = None,
        border: bool = True,
        **kwargs: Any,
    ) -> 'InsetMixin':
        """Add an inset plot to this panel.

        Parameters
        ----------
        plot_func : callable
            Function with signature func(ax, data, **kwargs) or func(ax, **kwargs).
        bounds : tuple of float
            (x, y, width, height) in axes fraction coordinates.
            Default (0.6, 0.6, 0.35, 0.35) = upper-right corner.
        data : any, optional
            Data to pass to plot_func.
        border : bool
            Whether to draw a border around the inset. Default True.
        **kwargs
            Additional kwargs passed to plot_func.

        Returns
        -------
        self
        """
        self._insets.append({
            'plot_func': plot_func,
            'bounds': bounds,
            'data': data,
            'border': border,
            'kwargs': kwargs,
        })
        return self

    def _render_insets(self, parent_ax: Axes) -> list[Axes]:
        """Render all insets onto the parent axes.

        Should be called at the end of the panel's render() method.
        """
        inset_axes = []
        for inset in self._insets:
            ax_inset = parent_ax.inset_axes(inset['bounds'])
            func = inset['plot_func']
            data = inset['data']

            import inspect
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            if len(params) >= 2 and data is not None:
                func(ax_inset, data, **inset['kwargs'])
            elif len(params) >= 2:
                func(ax_inset, data, **inset['kwargs'])
            else:
                func(ax_inset, **inset['kwargs'])

            if inset['border']:
                for spine in ax_inset.spines.values():
                    spine.set_linewidth(0.8)
                    spine.set_edgecolor('black')

            inset_axes.append(ax_inset)

        return inset_axes
