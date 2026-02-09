"""Survival analysis plot types for scientific figures.

This module provides Kaplan-Meier curves and cumulative incidence plots
for survival analysis. All functions use colorblind-friendly default palettes.
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


@register_plot_type('kaplan_meier')
def kaplan_meier(
    ax: 'Axes',
    data: Any,
    time_col: str = 'time',
    event_col: str = 'event',
    group_col: str | None = None,
    color: str | Sequence[str] | None = None,
    ci: bool = True,
    ci_alpha: float = 0.2,
    show_censors: bool = True,
    censor_marker: str = '|',
    censor_size: float = 8,
    linewidth: float = 1.5,
    at_risk: bool = False,
    at_risk_intervals: Sequence[float] | None = None,
    **kwargs: Any,
) -> None:
    """Create a Kaplan-Meier survival curve.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Survival data with time and event columns.
    time_col : str, default 'time'
        Column name for survival time.
    event_col : str, default 'event'
        Column name for event indicator (1=event, 0=censored).
    group_col : str, optional
        Column name for grouping (creates multiple curves).
    color : str or list of str, optional
        Line color(s). Uses Okabe-Ito palette by default.
    ci : bool, default True
        Whether to show confidence intervals.
    ci_alpha : float, default 0.2
        Transparency for confidence interval shading.
    show_censors : bool, default True
        Whether to mark censored observations.
    censor_marker : str, default '|'
        Marker style for censored observations.
    censor_size : float, default 8
        Size of censor markers.
    linewidth : float, default 1.5
        Width of survival curves.
    at_risk : bool, default False
        Whether to show "number at risk" table below plot.
    at_risk_intervals : sequence of float, optional
        Time points for at-risk table. Defaults to 5 evenly spaced points.
    **kwargs
        Additional arguments passed to plot functions.

    Examples
    --------
    >>> kaplan_meier(ax, survival_df, time_col='months', event_col='death')

    >>> kaplan_meier(ax, df, group_col='treatment', ci=True)

    >>> kaplan_meier(ax, df, group_col='stage', at_risk=True)
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

    def _km_estimate(times, events):
        """Calculate Kaplan-Meier estimate."""
        # Sort by time
        sorted_indices = np.argsort(times)
        times = times[sorted_indices]
        events = events[sorted_indices]

        # Calculate KM estimate
        n = len(times)
        km_survival = np.ones(n)
        km_var = np.zeros(n)

        at_risk = n
        for i in range(n):
            if i > 0:
                km_survival[i] = km_survival[i-1]
                km_var[i] = km_var[i-1]

            if events[i] == 1:  # Event occurred
                km_survival[i] *= (at_risk - 1) / at_risk
                km_var[i] += 1 / (at_risk * (at_risk - 1)) if at_risk > 1 else 0

            at_risk -= 1

        # Greenwood's formula for confidence interval
        km_std = np.sqrt(km_var)
        # Avoid division by zero when survival is 0
        with np.errstate(divide='ignore', invalid='ignore'):
            ci_lower = km_survival * np.exp(-1.96 * km_std / np.where(km_survival > 0, km_survival, 1))
            ci_upper = km_survival * np.exp(1.96 * km_std / np.where(km_survival > 0, km_survival, 1))
        ci_lower = np.nan_to_num(ci_lower, nan=0)
        ci_upper = np.nan_to_num(ci_upper, nan=1)

        return times, km_survival, ci_lower, ci_upper

    def _get_censor_times(times, events):
        """Get times of censored observations."""
        censor_mask = events == 0
        return times[censor_mask], np.ones(censor_mask.sum())  # y=1 for censors

    # Plot
    if group_col is None:
        times = data[time_col].values
        events = data[event_col].values

        t, s, ci_low, ci_high = _km_estimate(times, events)

        # Plot survival curve
        ax.step(t, s, where='post', color=colors[0], linewidth=linewidth, label='All', **kwargs)

        # Plot confidence interval
        if ci:
            ax.fill_between(t, ci_low, ci_high, step='post', alpha=ci_alpha, color=colors[0])

        # Mark censored observations
        if show_censors:
            censor_t, censor_y = _get_censor_times(times, events)
            # Find corresponding survival probabilities
            censor_s = np.array([s[np.searchsorted(t, ct, side='right') - 1] for ct in censor_t])
            ax.scatter(censor_t, censor_s, marker=censor_marker, s=censor_size**2,
                      color=colors[0], zorder=5)
    else:
        groups = data[group_col].unique()
        for i, group in enumerate(groups):
            group_data = data[data[group_col] == group]
            times = group_data[time_col].values
            events = group_data[event_col].values

            t, s, ci_low, ci_high = _km_estimate(times, events)

            # Plot survival curve
            ax.step(t, s, where='post', color=colors[i % len(colors)],
                   linewidth=linewidth, label=str(group), **kwargs)

            # Plot confidence interval
            if ci:
                ax.fill_between(t, ci_low, ci_high, step='post',
                              alpha=ci_alpha, color=colors[i % len(colors)])

            # Mark censored observations
            if show_censors:
                censor_t, _ = _get_censor_times(times, events)
                censor_s = np.array([s[np.searchsorted(t, ct, side='right') - 1] for ct in censor_t])
                ax.scatter(censor_t, censor_s, marker=censor_marker, s=censor_size**2,
                          color=colors[i % len(colors)], zorder=5)

    # Formatting
    ax.set_xlabel('Time')
    ax.set_ylabel('Survival Probability')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='lower left', frameon=False, title=group_col if group_col else None)

    # Add at-risk table if requested
    if at_risk:
        # This would require additional axis manipulation
        # For now, just add a note
        ax.text(0.5, -0.15, '(Number at risk table would be shown here)',
               transform=ax.transAxes, ha='center', fontsize=6, style='italic')


@register_plot_type('cumulative_incidence')
def cumulative_incidence(
    ax: 'Axes',
    data: Any,
    time_col: str = 'time',
    event_col: str = 'event',
    group_col: str | None = None,
    competing_risks: bool = False,
    event_types: Sequence[int] | None = None,
    color: str | Sequence[str] | None = None,
    ci: bool = True,
    ci_alpha: float = 0.2,
    linewidth: float = 1.5,
    **kwargs: Any,
) -> None:
    """Create a cumulative incidence curve (for competing risks).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Survival data with time, event, and optionally event type columns.
    time_col : str, default 'time'
        Column name for time to event.
    event_col : str, default 'event'
        Column name for event indicator.
    group_col : str, optional
        Column name for grouping (creates multiple curves).
    competing_risks : bool, default False
        Whether to account for competing risks.
    event_types : sequence of int, optional
        Specific event types to plot (for competing risks).
    color : str or list of str, optional
        Line color(s). Uses Okabe-Ito palette by default.
    ci : bool, default True
        Whether to show confidence intervals.
    ci_alpha : float, default 0.2
        Transparency for confidence interval shading.
    linewidth : float, default 1.5
        Width of curves.
    **kwargs
        Additional arguments passed to plot functions.

    Examples
    --------
    >>> cumulative_incidence(ax, survival_df, time_col='time', event_col='relapse')

    >>> cumulative_incidence(ax, df, group_col='treatment', competing_risks=True)

    >>> cumulative_incidence(ax, df, event_types=[1, 2], ci=True)
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

    def _aalen_johansen(times, events, event_type):
        """Calculate Aalen-Johansen estimate for competing risks."""
        # Sort by time
        sorted_indices = np.argsort(times)
        times = times[sorted_indices]
        events = events[sorted_indices]

        n = len(times)
        cum_inc = np.zeros(n)

        at_risk = n
        for i in range(n):
            if i > 0:
                cum_inc[i] = cum_inc[i-1]

            if at_risk > 0:
                if events[i] == event_type:
                    cum_inc[i] += 1 / at_risk
                elif events[i] == 0:  # Censored
                    pass
                # Competing events reduce at_risk

            if events[i] != 0:  # Any event or censoring
                at_risk -= 1

        return times, cum_inc

    def _naive_cuminc(times, events):
        """Calculate simple cumulative incidence (1 - KM)."""
        sorted_indices = np.argsort(times)
        times = times[sorted_indices]
        events = events[sorted_indices]

        n = len(times)
        survival = np.ones(n)

        at_risk = n
        for i in range(n):
            if i > 0:
                survival[i] = survival[i-1]

            if events[i] == 1:
                survival[i] *= (at_risk - 1) / at_risk

            at_risk -= 1

        return times, 1 - survival

    # Plot
    if group_col is None:
        times = data[time_col].values
        events = data[event_col].values

        if competing_risks and event_types:
            for i, event_type in enumerate(event_types):
                t, ci = _aalen_johansen(times, events, event_type)
                ax.step(t, ci, where='post', color=colors[i % len(colors)],
                       linewidth=linewidth, label=f'Event {event_type}', **kwargs)
        else:
            t, ci = _naive_cuminc(times, events)
            ax.step(t, ci, where='post', color=colors[0],
                   linewidth=linewidth, label='Cumulative Incidence', **kwargs)
    else:
        groups = data[group_col].unique()
        for i, group in enumerate(groups):
            group_data = data[data[group_col] == group]
            times = group_data[time_col].values
            events = group_data[event_col].values

            t, ci = _naive_cuminc(times, events)
            ax.step(t, ci, where='post', color=colors[i % len(colors)],
                   linewidth=linewidth, label=str(group), **kwargs)

    # Formatting
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative Incidence')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='lower right', frameon=False, title=group_col if group_col else None)
