"""PlotPanel - render data-driven plots with optional registered plot types."""

from __future__ import annotations

from typing import Any, Callable, Optional

from matplotlib.axes import Axes

from figcombo.panels.base import BasePanel

# Global registry for custom plot types
_PLOT_TYPE_REGISTRY: dict[str, Callable] = {}


def register_plot_type(name: str, func: Callable | None = None) -> Callable:
    """Register a custom plot type function.

    Can be used as a decorator or called directly.

    Parameters
    ----------
    name : str
        Name for this plot type (e.g. 'volcano', 'kaplan_meier').
    func : callable, optional
        The plot function with signature func(ax, data, **kwargs).
        If not provided, returns a decorator.

    Returns
    -------
    callable
        The original function (when used as decorator) or the registered function.

    Examples
    --------
    As a decorator::

        @register_plot_type('volcano')
        def volcano_plot(ax, data, fc_col='log2FC', p_col='pvalue', **kwargs):
            ...

    As a function call::

        register_plot_type('survival', my_km_function)
    """
    if func is not None:
        _PLOT_TYPE_REGISTRY[name] = func
        return func

    # Used as decorator
    def decorator(fn: Callable) -> Callable:
        _PLOT_TYPE_REGISTRY[name] = fn
        return fn

    return decorator


def list_plot_types() -> list[str]:
    """List all registered plot type names (built-in + custom)."""
    return sorted(_PLOT_TYPE_REGISTRY.keys())


def get_plot_type(name: str) -> Callable:
    """Get a registered plot function by name."""
    if name not in _PLOT_TYPE_REGISTRY:
        available = ', '.join(list_plot_types()) or '(none)'
        raise ValueError(
            f"Unknown plot type '{name}'. Available types: {available}"
        )
    return _PLOT_TYPE_REGISTRY[name]


class PlotPanel(BasePanel):
    """Panel that renders a data-driven plot.

    Can accept either:
    - A callable plot function: `plot_func(ax, data, **kwargs)`
    - A registered plot type name (string)

    Parameters
    ----------
    plot_func : callable or str
        Either a function with signature (ax, data, **kwargs),
        or a string name of a registered plot type.
    data : any, optional
        Data to pass to the plot function.
    aspect_ratio : float, optional
        Preferred width/height ratio. If None, uses the default
        for the plot type if registered.
    **kwargs
        Additional keyword arguments passed to the plot function.

    Examples
    --------
    With a custom function::

        def my_plot(ax, data):
            ax.bar(data['x'], data['y'])

        panel = PlotPanel(my_plot, data=df)

    With a registered type::

        panel = PlotPanel('volcano', data=deseq_results, fc_col='log2FC')
    """

    def __init__(
        self,
        plot_func: Callable | str,
        data: Any = None,
        aspect_ratio: float | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        if isinstance(plot_func, str):
            self._plot_type_name = plot_func
            self._plot_func = None  # resolved at render time
        else:
            self._plot_type_name = None
            self._plot_func = plot_func

        self.data = data
        self._aspect_ratio = aspect_ratio
        self._plot_kwargs = kwargs

    def _resolve_func(self) -> Callable:
        """Resolve the plot function (from registry if needed)."""
        if self._plot_func is not None:
            return self._plot_func
        if self._plot_type_name is not None:
            return get_plot_type(self._plot_type_name)
        raise RuntimeError("No plot function or type name specified")

    def render(self, ax: Axes) -> None:
        """Render the plot onto the axes."""
        func = self._resolve_func()
        if self.data is not None:
            func(ax, self.data, **self._plot_kwargs)
        else:
            func(ax, **self._plot_kwargs)

    def get_preferred_aspect(self) -> Optional[float]:
        """Return preferred aspect ratio if set."""
        if self._aspect_ratio is not None:
            return self._aspect_ratio

        # Try to get from knowledge base
        if self._plot_type_name is not None:
            from figcombo.knowledge.panel_constraints import ASPECT_RATIOS
            ratio = ASPECT_RATIOS.get(self._plot_type_name)
            if ratio is not None:
                return ratio[0] / ratio[1]

        return None

    def validate(self) -> list[str]:
        errors = []
        if self._plot_func is None and self._plot_type_name is not None:
            if self._plot_type_name not in _PLOT_TYPE_REGISTRY:
                errors.append(
                    f"Plot type '{self._plot_type_name}' is not registered. "
                    f"Use register_plot_type() to register it first."
                )
        if self._plot_func is None and self._plot_type_name is None:
            errors.append("No plot function or type name provided")
        return errors

    @classmethod
    def from_type(cls, name: str, **kwargs: Any) -> 'PlotPanel':
        """Create a PlotPanel from a registered plot type name.

        Parameters
        ----------
        name : str
            Registered plot type name.
        **kwargs
            Arguments passed to PlotPanel constructor.
        """
        return cls(plot_func=name, **kwargs)

    def __repr__(self) -> str:
        if self._plot_type_name:
            return f"PlotPanel('{self._plot_type_name}')"
        func_name = getattr(self._plot_func, '__name__', '?')
        return f"PlotPanel({func_name})"
