"""Statistical plot types for scientific figures.

This module provides common statistical visualizations including
bar plots, box plots, violin plots, scatter plots, histograms, and CDF plots.
All functions use colorblind-friendly default palettes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

import numpy as np

from figcombo.panels.plot_panel import register_plot_type

if TYPE_CHECKING:
    from matplotlib.axes import Axes


# Okabe-Ito colorblind-safe palette
OKABE_ITO = [
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#F0E442',  # yellow
    '#0072B2',  # blue
    '#D55E00',  # vermillion
    '#CC79A7',  # reddish purple
    '#000000',  # black
]


@register_plot_type('bar_plot')
def bar_plot(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    error: str | Sequence[float] | None = None,
    capsize: float = 3,
    color: str | Sequence[str] | None = None,
    **kwargs: Any,
) -> None:
    """Create a bar plot with optional error bars.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or dict
        Input data. If dict, keys are categories and values are heights.
    x : str, optional
        Column name for x-axis categories (for DataFrame input).
    y : str, optional
        Column name for y-axis values (for DataFrame input).
    hue : str, optional
        Column name for grouping/coloring bars.
    error : str or array-like, optional
        Error values for error bars. Can be:
        - Column name containing error values
        - Array of same length as data
        - 'sem' to compute standard error of mean
        - 'std' to compute standard deviation
    capsize : float, default 3
        Length of error bar caps in points.
    color : str or list of str, optional
        Bar color(s). Uses Okabe-Ito palette by default.
    **kwargs
        Additional arguments passed to ax.bar().

    Examples
    --------
    >>> # With DataFrame
    >>> bar_plot(ax, df, x='treatment', y='response', error='sem')

    >>> # With dict
    >>> bar_plot(ax, {'A': 10, 'B': 15, 'C': 8}, color='#56B4E9')

    >>> # Grouped bars
    >>> bar_plot(ax, df, x='treatment', y='response', hue='timepoint')
    """
    import pandas as pd

    # Handle dict input
    if isinstance(data, dict):
        categories = list(data.keys())
        values = list(data.values())
        x_pos = np.arange(len(categories))

        bar_color = color if color is not None else OKABE_ITO[0]
        ax.bar(x_pos, values, color=bar_color, **kwargs)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories)
        return

    # Handle DataFrame input
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a DataFrame or dict")

    if x is None or y is None:
        raise ValueError("x and y must be specified for DataFrame input")

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    if hue is None:
        # Simple bar plot
        grouped = data.groupby(x)[y].agg(['mean', 'std', 'count']).reset_index()
        x_pos = np.arange(len(grouped))

        # Calculate error bars
        if error is None:
            yerr = None
        elif error == 'sem':
            yerr = grouped['std'] / np.sqrt(grouped['count'])
        elif error == 'std':
            yerr = grouped['std']
        elif error in data.columns:
            yerr = grouped[error] if error in grouped.columns else None
        else:
            yerr = None

        ax.bar(
            x_pos,
            grouped['mean'],
            yerr=yerr,
            capsize=capsize,
            color=colors[0],
            **kwargs
        )
        ax.set_xticks(x_pos)
        ax.set_xticklabels(grouped[x])
    else:
        # Grouped bar plot
        groups = data[hue].unique()
        n_groups = len(groups)
        grouped = data.groupby([x, hue])[y].agg(['mean', 'std', 'count']).reset_index()
        categories = data[x].unique()
        x_pos = np.arange(len(categories))
        bar_width = 0.8 / n_groups

        for i, group in enumerate(groups):
            group_data = grouped[grouped[hue] == group]
            offset = (i - n_groups / 2 + 0.5) * bar_width

            # Calculate error bars
            if error is None:
                yerr = None
            elif error == 'sem':
                yerr = group_data['std'] / np.sqrt(group_data['count'])
            elif error == 'std':
                yerr = group_data['std']
            else:
                yerr = None

            ax.bar(
                x_pos + offset,
                group_data['mean'],
                width=bar_width,
                yerr=yerr,
                capsize=capsize / 2,
                color=colors[i % len(colors)],
                label=str(group),
                **kwargs
            )

        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories)
        ax.legend(title=hue, frameon=False)


@register_plot_type('box_plot')
def box_plot(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    color: str | Sequence[str] | None = None,
    showfliers: bool = True,
    notch: bool = False,
    **kwargs: Any,
) -> None:
    """Create a box plot (box-and-whisker plot).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame, array-like, or sequence of array-like
        Input data.
    x : str, optional
        Column name for grouping on x-axis.
    y : str, optional
        Column name for values.
    hue : str, optional
        Column name for additional grouping (creates grouped boxes).
    color : str or list of str, optional
        Box color(s). Uses Okabe-Ito palette by default.
    showfliers : bool, default True
        Whether to show outlier points.
    notch : bool, default False
        Whether to draw notches for confidence intervals.
    **kwargs
        Additional arguments passed to ax.boxplot() or seaborn.boxplot().

    Examples
    --------
    >>> box_plot(ax, df, x='treatment', y='expression')

    >>> box_plot(ax, [data1, data2, data3], labels=['A', 'B', 'C'])
    """
    import pandas as pd

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    # Handle sequence of arrays
    if not isinstance(data, pd.DataFrame) and hasattr(data, '__iter__'):
        try:
            # Check if it's a sequence of arrays
            first = next(iter(data))
            if hasattr(first, '__iter__') and not isinstance(first, str):
                labels = kwargs.pop('labels', [f'Group {i+1}' for i in range(len(data))])
                bp = ax.boxplot(
                    data,
                    labels=labels,
                    patch_artist=True,
                    notch=notch,
                    showfliers=showfliers,
                    **kwargs
                )
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                return
        except (TypeError, StopIteration):
            pass

    # Use seaborn for DataFrame input
    try:
        import seaborn as sns

        palette = colors if color is not None else OKABE_ITO

        sns.boxplot(
            data=data,
            x=x,
            y=y,
            hue=hue,
            ax=ax,
            palette=palette,
            showfliers=showfliers,
            notch=notch,
            **kwargs
        )

        if hue is not None:
            ax.legend(title=hue, frameon=False)

    except ImportError:
        # Fallback to matplotlib
        if x is None or y is None:
            raise ValueError("x and y required when seaborn is not installed")

        grouped = data.groupby(x)[y].apply(list)
        bp = ax.boxplot(
            grouped.values,
            labels=grouped.index,
            patch_artist=True,
            notch=notch,
            showfliers=showfliers,
            **kwargs
        )
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)


@register_plot_type('violin_plot')
def violin_plot(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    color: str | Sequence[str] | None = None,
    split: bool = False,
    inner: str = 'box',
    **kwargs: Any,
) -> None:
    """Create a violin plot showing distribution shape.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Input data.
    x : str, optional
        Column name for grouping on x-axis.
    y : str, optional
        Column name for values.
    hue : str, optional
        Column name for additional grouping.
    color : str or list of str, optional
        Violin color(s). Uses Okabe-Ito palette by default.
    split : bool, default False
        When hue has 2 levels, split violins in half.
    inner : str, default 'box'
        Representation inside violin: 'box', 'quartile', 'point', 'stick', or None.
    **kwargs
        Additional arguments passed to seaborn.violinplot().

    Examples
    --------
    >>> violin_plot(ax, df, x='condition', y='expression')

    >>> violin_plot(ax, df, x='condition', y='expression', hue='sex', split=True)
    """
    try:
        import seaborn as sns
    except ImportError:
        raise ImportError("seaborn is required for violin_plot. Install with: pip install seaborn")

    # Determine colors
    if color is None:
        palette = OKABE_ITO
    elif isinstance(color, str):
        palette = [color]
    else:
        palette = list(color)

    sns.violinplot(
        data=data,
        x=x,
        y=y,
        hue=hue,
        split=split,
        inner=inner,
        palette=palette,
        ax=ax,
        **kwargs
    )

    if hue is not None:
        ax.legend(title=hue, frameon=False)


@register_plot_type('scatter_plot')
def scatter_plot(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    size: str | None = None,
    style: str | None = None,
    color: str | None = None,
    alpha: float = 0.6,
    add_regression: bool = False,
    ci: int = 95,
    **kwargs: Any,
) -> None:
    """Create a scatter plot with optional regression line.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or array-like
        Input data. If array-like, provide x and y as column indices.
    x : str or int
        Column name (DataFrame) or index (array) for x values.
    y : str or int
        Column name (DataFrame) or index (array) for y values.
    hue : str, optional
        Column name for color grouping.
    size : str, optional
        Column name for point sizes.
    style : str, optional
        Column name for marker styles.
    color : str, optional
        Point color when hue is not specified.
    alpha : float, default 0.6
        Point transparency (0-1).
    add_regression : bool, default False
        Whether to add a linear regression line.
    ci : int, default 95
        Confidence interval for regression (set to None to disable).
    **kwargs
        Additional arguments passed to scatter or regplot.

    Examples
    --------
    >>> scatter_plot(ax, df, x='gene_a', y='gene_b')

    >>> scatter_plot(ax, df, x='x', y='y', hue='condition', add_regression=True)
    """
    import pandas as pd

    # Determine default color
    if color is None:
        color = OKABE_ITO[0]

    # Handle simple array input
    if not isinstance(data, pd.DataFrame):
        if x is not None and y is not None:
            x_vals = data[x] if hasattr(data, 'shape') and len(data.shape) > 1 else data
            y_vals = data[y] if hasattr(data, 'shape') and len(data.shape) > 1 else y
        else:
            x_vals = data[:, 0] if hasattr(data, 'shape') and len(data.shape) > 1 else data[0]
            y_vals = data[:, 1] if hasattr(data, 'shape') and len(data.shape) > 1 else data[1]

        if add_regression:
            try:
                import seaborn as sns
                sns.regplot(x=x_vals, y=y_vals, ax=ax, color=color, ci=ci, **kwargs)
            except ImportError:
                ax.scatter(x_vals, y_vals, c=color, alpha=alpha, **kwargs)
                # Add simple regression line
                z = np.polyfit(x_vals, y_vals, 1)
                p = np.poly1d(z)
                x_line = np.linspace(min(x_vals), max(x_vals), 100)
                ax.plot(x_line, p(x_line), '--', color=color, linewidth=1)
        else:
            ax.scatter(x_vals, y_vals, c=color, alpha=alpha, **kwargs)
        return

    # DataFrame input
    if x is None or y is None:
        raise ValueError("x and y must be specified for DataFrame input")

    if add_regression and hue is None:
        try:
            import seaborn as sns
            sns.regplot(
                data=data,
                x=x,
                y=y,
                ax=ax,
                color=color,
                ci=ci,
                scatter_kws={'alpha': alpha},
                **kwargs
            )
        except ImportError:
            ax.scatter(data[x], data[y], c=color, alpha=alpha, **kwargs)
    else:
        try:
            import seaborn as sns
            sns.scatterplot(
                data=data,
                x=x,
                y=y,
                hue=hue,
                size=size,
                style=style,
                palette=OKABE_ITO if hue else None,
                alpha=alpha,
                ax=ax,
                **kwargs
            )
            if hue is not None:
                ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left')
        except ImportError:
            if hue is not None:
                groups = data[hue].unique()
                for i, group in enumerate(groups):
                    mask = data[hue] == group
                    ax.scatter(
                        data.loc[mask, x],
                        data.loc[mask, y],
                        c=OKABE_ITO[i % len(OKABE_ITO)],
                        alpha=alpha,
                        label=str(group),
                        **kwargs
                    )
                ax.legend(title=hue, frameon=False)
            else:
                ax.scatter(data[x], data[y], c=color, alpha=alpha, **kwargs)


@register_plot_type('histogram')
def histogram(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    hue: str | None = None,
    bins: int | str = 'auto',
    color: str | Sequence[str] | None = None,
    alpha: float = 0.7,
    density: bool = False,
    cumulative: bool = False,
    **kwargs: Any,
) -> None:
    """Create a histogram showing data distribution.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame, array-like, or sequence of array-like
        Input data.
    x : str, optional
        Column name for values (DataFrame input).
    hue : str, optional
        Column name for grouping (DataFrame input).
    bins : int or str, default 'auto'
        Number of bins or binning strategy.
    color : str or list of str, optional
        Bar color(s). Uses Okabe-Ito palette by default.
    alpha : float, default 0.7
        Bar transparency (0-1).
    density : bool, default False
        If True, plot probability density instead of counts.
    cumulative : bool, default False
        If True, plot cumulative distribution.
    **kwargs
        Additional arguments passed to ax.hist().

    Examples
    --------
    >>> histogram(ax, df, x='expression', bins=30)

    >>> histogram(ax, df, x='expression', hue='condition', alpha=0.5)
    """
    import pandas as pd

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    # Handle array-like input
    if not isinstance(data, pd.DataFrame):
        ax.hist(
            data,
            bins=bins,
            color=colors[0],
            alpha=alpha,
            density=density,
            cumulative=cumulative,
            **kwargs
        )
        return

    # DataFrame input
    if hue is None:
        values = data[x] if x else data.iloc[:, 0]
        ax.hist(
            values,
            bins=bins,
            color=colors[0],
            alpha=alpha,
            density=density,
            cumulative=cumulative,
            **kwargs
        )
    else:
        groups = data[hue].unique()
        for i, group in enumerate(groups):
            values = data[data[hue] == group][x] if x else data[data[hue] == group].iloc[:, 0]
            ax.hist(
                values,
                bins=bins,
                color=colors[i % len(colors)],
                alpha=alpha,
                density=density,
                cumulative=cumulative,
                label=str(group),
                **kwargs
            )
        ax.legend(title=hue, frameon=False)


@register_plot_type('cdf_plot')
def cdf_plot(
    ax: 'Axes',
    data: Any,
    x: str | None = None,
    hue: str | None = None,
    color: str | Sequence[str] | None = None,
    linewidth: float = 1.5,
    marker: str | None = None,
    markersize: float = 4,
    **kwargs: Any,
) -> None:
    """Create a cumulative distribution function (CDF) plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame, array-like, or sequence of array-like
        Input data.
    x : str, optional
        Column name for values (DataFrame input).
    hue : str, optional
        Column name for grouping (DataFrame input).
    color : str or list of str, optional
        Line color(s). Uses Okabe-Ito palette by default.
    linewidth : float, default 1.5
        Line width.
    marker : str, optional
        Marker style for data points.
    markersize : float, default 4
        Marker size.
    **kwargs
        Additional arguments passed to ax.plot().

    Examples
    --------
    >>> cdf_plot(ax, df, x='expression')

    >>> cdf_plot(ax, [group1, group2, group3], labels=['A', 'B', 'C'])
    """
    import pandas as pd

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    def _plot_cdf(values, label=None, color=None, **plot_kwargs):
        """Plot CDF for a single dataset."""
        values = np.asarray(values)
        values = values[~np.isnan(values)]
        sorted_vals = np.sort(values)
        cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
        ax.plot(
            sorted_vals,
            cdf,
            color=color,
            linewidth=linewidth,
            marker=marker,
            markersize=markersize,
            markevery=max(1, len(sorted_vals) // 20),
            label=label,
            **plot_kwargs
        )

    # Handle array-like input
    if not isinstance(data, pd.DataFrame):
        if hasattr(data, '__iter__') and not isinstance(data[0], (int, float)):
            # Sequence of arrays
            labels = kwargs.pop('labels', [f'Sample {i+1}' for i in range(len(data))])
            for i, values in enumerate(data):
                _plot_cdf(values, label=labels[i], color=colors[i % len(colors)], **kwargs)
            ax.legend(frameon=False)
        else:
            # Single array
            _plot_cdf(data, color=colors[0], **kwargs)
        return

    # DataFrame input
    if hue is None:
        values = data[x] if x else data.iloc[:, 0]
        _plot_cdf(values, color=colors[0], **kwargs)
    else:
        groups = data[hue].unique()
        for i, group in enumerate(groups):
            values = data[data[hue] == group][x] if x else data[data[hue] == group].iloc[:, 0]
            _plot_cdf(values, label=str(group), color=colors[i % len(colors)], **kwargs)
        ax.legend(title=hue, frameon=False)

    ax.set_ylabel('Cumulative Probability')
    ax.set_ylim(0, 1.05)
