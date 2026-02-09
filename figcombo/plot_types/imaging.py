"""Imaging analysis plot types for scientific figures.

This module provides visualizations for microscopy and imaging analysis
including intensity profiles, colocalization plots, and ROI quantification.
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


@register_plot_type('intensity_profile')
def intensity_profile(
    ax: 'Axes',
    data: Any,
    channels: Sequence[str] | None = None,
    x_positions: Sequence[float] | None = None,
    normalize: bool = False,
    smooth: bool = False,
    smooth_window: int = 5,
    color: str | Sequence[str] | None = None,
    linewidth: float = 1.5,
    show_peaks: bool = False,
    peak_prominence: float | None = None,
    **kwargs: Any,
) -> None:
    """Plot intensity profiles across a line or region of interest.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame, dict, or array-like
        Intensity values. Can be:
        - DataFrame with columns for each channel
        - Dict mapping channel names to intensity arrays
        - 2D array (channels x positions)
    channels : sequence of str, optional
        Channel names. Uses data keys/columns if not specified.
    x_positions : sequence of float, optional
        X-axis positions (e.g., distance in microns).
    normalize : bool, default False
        Whether to normalize intensities to 0-1 range.
    smooth : bool, default False
        Whether to apply smoothing to profiles.
    smooth_window : int, default 5
        Window size for smoothing (must be odd).
    color : str or list of str, optional
        Line color(s). Uses Okabe-Ito palette by default.
    linewidth : float, default 1.5
        Width of profile lines.
    show_peaks : bool, default False
        Whether to mark peak positions.
    peak_prominence : float, optional
        Minimum prominence for peak detection.
    **kwargs
        Additional arguments passed to ax.plot().

    Examples
    --------
    >>> intensity_profile(ax, {'GFP': gfp_profile, 'RFP': rfp_profile})

    >>> intensity_profile(ax, df, channels=['DAPI', 'Cy3', 'Cy5'],
    ...                   x_positions=distances, normalize=True)

    >>> intensity_profile(ax, profiles, smooth=True, show_peaks=True)
    """
    import pandas as pd

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    # Extract data into channel arrays
    channel_data = {}

    if isinstance(data, pd.DataFrame):
        if channels is None:
            channels = data.columns.tolist()
        for ch in channels:
            if ch in data.columns:
                channel_data[ch] = data[ch].values
    elif isinstance(data, dict):
        channel_data = {k: np.asarray(v) for k, v in data.items()}
        if channels is None:
            channels = list(channel_data.keys())
    else:
        # Assume 2D array
        arr = np.asarray(data)
        if channels is None:
            channels = [f'Channel {i+1}' for i in range(arr.shape[0])]
        for i, ch in enumerate(channels):
            if i < arr.shape[0]:
                channel_data[ch] = arr[i]

    # Generate x positions if not provided
    if x_positions is None:
        max_len = max(len(v) for v in channel_data.values()) if channel_data else 0
        x_positions = np.arange(max_len)

    # Smoothing function
    def _smooth(y, window):
        """Apply moving average smoothing."""
        if window % 2 == 0:
            window += 1
        half = window // 2
        smoothed = np.convolve(y, np.ones(window)/window, mode='same')
        # Fix edges
        smoothed[:half] = y[:half]
        smoothed[-half:] = y[-half:]
        return smoothed

    # Plot each channel
    for i, (ch, values) in enumerate(channel_data.items()):
        y = values.copy()

        # Normalize if requested
        if normalize:
            y_min, y_max = y.min(), y.max()
            if y_max > y_min:
                y = (y - y_min) / (y_max - y_min)

        # Smooth if requested
        if smooth:
            y = _smooth(y, smooth_window)

        # Plot
        ax.plot(
            x_positions[:len(y)],
            y,
            color=colors[i % len(colors)],
            linewidth=linewidth,
            label=str(ch),
            **kwargs
        )

        # Detect and mark peaks
        if show_peaks:
            try:
                from scipy.signal import find_peaks
                peaks, properties = find_peaks(y, prominence=peak_prominence)
                ax.scatter(
                    x_positions[peaks],
                    y[peaks],
                    color=colors[i % len(colors)],
                    s=50,
                    zorder=5,
                    marker='^'
                )
            except ImportError:
                pass

    ax.set_xlabel('Position')
    ax.set_ylabel('Intensity' + (' (normalized)' if normalize else ''))
    ax.legend(loc='best', frameon=False)


@register_plot_type('colocalization_plot')
def colocalization_plot(
    ax: 'Axes',
    data: Any,
    channel_x: str = 'channel1',
    channel_y: str = 'channel2',
    x_col: str | None = None,
    y_col: str | None = None,
    color: str | None = None,
    alpha: float = 0.5,
    point_size: float = 10,
    show_density: bool = False,
    show_regression: bool = True,
    show_pearson: bool = True,
    show_manders: bool = False,
    bins: int = 50,
    **kwargs: Any,
) -> None:
    """Create a scatter plot for colocalization analysis between two channels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or array-like
        Pixel intensity values for two channels.
    channel_x : str, default 'channel1'
        Name of x-axis channel (for labeling).
    channel_y : str, default 'channel2'
        Name of y-axis channel (for labeling).
    x_col : str, optional
        Column name for x values (DataFrame input).
    y_col : str, optional
        Column name for y values (DataFrame input).
    color : str, optional
        Point color. Uses default palette if not specified.
    alpha : float, default 0.5
        Point transparency.
    point_size : float, default 10
        Size of scatter points.
    show_density : bool, default False
        Whether to show density coloring instead of uniform color.
    show_regression : bool, default True
        Whether to show linear regression line.
    show_pearson : bool, default True
        Whether to display Pearson correlation coefficient.
    show_manders : bool, default False
        Whether to display Manders' colocalization coefficients.
    bins : int, default 50
        Number of bins for density estimation.
    **kwargs
        Additional arguments passed to scatter plot.

    Examples
    --------
    >>> colocalization_plot(ax, df, x_col='GFP', y_col='RFP')

    >>> colocalization_plot(ax, pixel_data, show_density=True, show_manders=True)

    >>> colocalization_plot(ax, df, channel_x='DAPI', channel_y='EdU',
    ...                     show_regression=False)
    """
    import pandas as pd

    # Extract x and y values
    if isinstance(data, pd.DataFrame):
        x = data[x_col].values if x_col else data.iloc[:, 0].values
        y = data[y_col].values if y_col else data.iloc[:, 1].values
    else:
        arr = np.asarray(data)
        x, y = arr[:, 0], arr[:, 1]

    # Remove NaN and Inf values
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    # Determine color
    if color is None:
        color = OKABE_ITO[0]

    # Plot scatter
    if show_density:
        try:
            from scipy.stats import gaussian_kde
            xy = np.vstack([x, y])
            density = gaussian_kde(xy)(xy)
            scatter = ax.scatter(x, y, c=density, s=point_size, alpha=alpha,
                               cmap='viridis', **kwargs)
            plt.colorbar(scatter, ax=ax, label='Density')
        except ImportError:
            ax.scatter(x, y, c=color, s=point_size, alpha=alpha, **kwargs)
    else:
        ax.scatter(x, y, c=color, s=point_size, alpha=alpha, **kwargs)

    # Add regression line
    if show_regression and len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), '--', color='red', linewidth=1.5, alpha=0.7)

    # Calculate and display statistics
    stats_text = []

    if show_pearson and len(x) > 1:
        from scipy.stats import pearsonr
        r, p = pearsonr(x, y)
        stats_text.append(f'Pearson r = {r:.3f}')
        stats_text.append(f'p = {p:.2e}' if p < 0.001 else f'p = {p:.3f}')

    if show_manders and len(x) > 1:
        # Manders' M1 and M2 coefficients
        threshold_x = np.percentile(x, 5)
        threshold_y = np.percentile(y, 5)

        m1 = np.sum(x[y > threshold_y]) / np.sum(x) if np.sum(x) > 0 else 0
        m2 = np.sum(y[x > threshold_x]) / np.sum(y) if np.sum(y) > 0 else 0

        stats_text.append(f"Manders' M1 = {m1:.3f}")
        stats_text.append(f"Manders' M2 = {m2:.3f}")

    if stats_text:
        ax.text(0.05, 0.95, '\n'.join(stats_text),
               transform=ax.transAxes, fontsize=7,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel(f'{channel_x} Intensity')
    ax.set_ylabel(f'{channel_y} Intensity')


@register_plot_type('roi_quantification')
def roi_quantification(
    ax: 'Axes',
    data: Any,
    roi_col: str = 'roi',
    value_col: str = 'intensity',
    channel_col: str | None = None,
    group_col: str | None = None,
    plot_type: str = 'bar',
    color: str | Sequence[str] | None = None,
    error: str | None = 'sem',
    **kwargs: Any,
) -> None:
    """Create a plot for ROI (Region of Interest) quantification.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        ROI quantification data.
    roi_col : str, default 'roi'
        Column name for ROI identifiers.
    value_col : str, default 'intensity'
        Column name for measured values.
    channel_col : str, optional
        Column name for channel grouping.
    group_col : str, optional
        Column name for condition/group grouping.
    plot_type : str, default 'bar'
        Type of plot: 'bar', 'box', 'violin', or 'dot'.
    color : str or list of str, optional
        Color(s) for plot elements. Uses Okabe-Ito palette by default.
    error : str, optional
        Error type for bar plots: 'sem', 'std', or None.
    **kwargs
        Additional arguments passed to plotting functions.

    Examples
    --------
    >>> roi_quantification(ax, roi_data, value_col='mean_intensity')

    >>> roi_quantification(ax, df, channel_col='channel', group_col='condition',
    ...                    plot_type='box')

    >>> roi_quantification(ax, df, plot_type='dot', error='std')
    """
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    # Prepare data
    if channel_col and group_col:
        # Multiple channels and groups
        df_plot = data.groupby([channel_col, group_col])[value_col].agg(['mean', 'std', 'count']).reset_index()
    elif channel_col:
        # Multiple channels
        df_plot = data.groupby(channel_col)[value_col].agg(['mean', 'std', 'count']).reset_index()
        df_plot['group'] = 'All'
    elif group_col:
        # Multiple groups
        df_plot = data.groupby(group_col)[value_col].agg(['mean', 'std', 'count']).reset_index()
        df_plot['channel'] = 'All'
        channel_col = 'channel'
    else:
        # Single group
        df_plot = pd.DataFrame({
            'channel': ['All'],
            'mean': [data[value_col].mean()],
            'std': [data[value_col].std()],
            'count': [len(data)]
        })
        channel_col = 'channel'

    # Calculate error bars
    if error == 'sem':
        df_plot['error'] = df_plot['std'] / np.sqrt(df_plot['count'])
    elif error == 'std':
        df_plot['error'] = df_plot['std']
    else:
        df_plot['error'] = 0

    # Create plot
    if plot_type == 'bar':
        if channel_col and len(df_plot[channel_col].unique()) > 1:
            # Grouped bar plot
            channels = df_plot[channel_col].unique()
            groups = df_plot[group_col].unique() if group_col else ['All']
            x = np.arange(len(channels))
            width = 0.8 / len(groups)

            for i, group in enumerate(groups):
                if group_col:
                    group_data = df_plot[df_plot[group_col] == group]
                else:
                    group_data = df_plot
                offset = (i - len(groups) / 2 + 0.5) * width
                ax.bar(x + offset, group_data['mean'], width, yerr=group_data['error'],
                      color=colors[i % len(colors)], label=str(group), capsize=3)

            ax.set_xticks(x)
            ax.set_xticklabels(channels)
            if len(groups) > 1:
                ax.legend(title=group_col, frameon=False)
        else:
            # Simple bar plot
            ax.bar(range(len(df_plot)), df_plot['mean'], yerr=df_plot['error'],
                  color=colors[0], capsize=3)
            ax.set_xticks(range(len(df_plot)))
            ax.set_xticklabels(df_plot[channel_col] if channel_col else df_plot.index)

    elif plot_type == 'box':
        try:
            import seaborn as sns
            if channel_col and group_col:
                sns.boxplot(data=data, x=channel_col, y=value_col, hue=group_col,
                           palette=colors, ax=ax)
            elif channel_col:
                sns.boxplot(data=data, x=channel_col, y=value_col,
                           palette=colors, ax=ax)
            else:
                sns.boxplot(data=data, y=value_col, color=colors[0], ax=ax)
        except ImportError:
            ax.boxplot([data[data[channel_col] == ch][value_col].values
                       for ch in data[channel_col].unique()])

    elif plot_type == 'violin':
        try:
            import seaborn as sns
            if channel_col and group_col:
                sns.violinplot(data=data, x=channel_col, y=value_col, hue=group_col,
                              palette=colors, ax=ax, split=True)
            elif channel_col:
                sns.violinplot(data=data, x=channel_col, y=value_col,
                              palette=colors, ax=ax)
            else:
                sns.violinplot(data=data, y=value_col, color=colors[0], ax=ax)
        except ImportError:
            raise ImportError("seaborn is required for violin plots")

    elif plot_type == 'dot':
        if channel_col and group_col:
            groups = data[group_col].unique()
            channels = data[channel_col].unique()
            for i, group in enumerate(groups):
                group_data = data[data[group_col] == group]
                x_pos = [list(channels).index(ch) + i * 0.2 - 0.1
                        for ch in group_data[channel_col]]
                ax.scatter(x_pos, group_data[value_col], color=colors[i % len(colors)],
                          alpha=0.6, label=str(group))
            ax.set_xticks(range(len(channels)))
            ax.set_xticklabels(channels)
            ax.legend(title=group_col, frameon=False)
        else:
            ax.scatter(range(len(data)), data[value_col], color=colors[0], alpha=0.6)

    ax.set_ylabel(value_col.replace('_', ' ').title())


# Need to import matplotlib for colocalization_plot colorbar
import matplotlib.pyplot as plt
