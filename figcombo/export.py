"""Export engine for saving figures in publication-ready formats."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from matplotlib.figure import Figure as MplFigure


# Format-specific defaults
FORMAT_DEFAULTS: dict[str, dict[str, Any]] = {
    'pdf': {'dpi': 300, 'transparent': False},
    'eps': {'dpi': 300, 'transparent': False},
    'png': {'dpi': 300, 'transparent': False},
    'tiff': {'dpi': 600, 'transparent': False, 'pil_kwargs': {'compression': 'tiff_lzw'}},
    'tif': {'dpi': 600, 'transparent': False, 'pil_kwargs': {'compression': 'tiff_lzw'}},
    'svg': {'dpi': 300, 'transparent': True},
}


def save_figure(
    fig: MplFigure,
    path: str | Path,
    dpi: int | None = None,
    formats: list[str] | None = None,
    **kwargs: Any,
) -> list[Path]:
    """Save a figure to one or more formats.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to save.
    path : str or Path
        Output path. If no extension, saves in all specified formats.
        If has extension, saves in that format only.
    dpi : int, optional
        Override DPI. If None, uses format-specific defaults.
    formats : list of str, optional
        Formats to save in (e.g. ['pdf', 'png']). Only used when
        path has no extension.
    **kwargs
        Additional kwargs passed to fig.savefig().

    Returns
    -------
    list of Path
        Paths to saved files.
    """
    path = Path(path)
    saved: list[Path] = []

    # Determine formats
    if path.suffix:
        fmt = path.suffix.lstrip('.')
        save_paths = [(path, fmt)]
    else:
        if formats is None:
            formats = ['pdf']
        save_paths = [(path.with_suffix(f'.{fmt}'), fmt) for fmt in formats]

    for save_path, fmt in save_paths:
        save_kwargs = FORMAT_DEFAULTS.get(fmt, {}).copy()
        if dpi is not None:
            save_kwargs['dpi'] = dpi
        save_kwargs.update(kwargs)

        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if figure uses constrained_layout — if so, disable
        # before saving to prevent re-computation that can collapse
        # small axes.
        uses_cl = getattr(fig, 'get_constrained_layout', lambda: False)()
        if uses_cl:
            fig.set_constrained_layout(False)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            fig.savefig(
                str(save_path),
                format=fmt,
                **save_kwargs,
            )

        if uses_cl:
            fig.set_constrained_layout(True)

        saved.append(save_path)

    return saved


def save_for_journal(
    fig: MplFigure,
    path: str | Path,
    journal_spec: dict[str, Any],
    figure_type: str = 'combination',
) -> list[Path]:
    """Save figure using journal-specific settings.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    path : str or Path
        Output path (without extension).
    journal_spec : dict
        Resolved journal specification.
    figure_type : str
        One of 'line_art', 'halftone', 'combination'.

    Returns
    -------
    list of Path
        Paths to saved files.
    """
    dpi_spec = journal_spec.get('dpi', {})
    dpi = dpi_spec.get(figure_type, 300)

    formats = journal_spec.get('formats', ['PDF'])
    formats = [f.lower() for f in formats]

    return save_figure(fig, path, dpi=dpi, formats=formats)
