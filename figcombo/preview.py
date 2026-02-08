"""Preview window for real-time figure visualization (placeholder for Phase 3)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure as MplFigure


def show_preview(fig: "MplFigure") -> None:
    """Show an interactive preview window for the figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The rendered figure to preview.
    """
    import matplotlib.pyplot as plt

    # For now, use matplotlib's built-in show
    # Phase 3 will implement a proper Qt-based preview
    plt.show(block=False)
    plt.pause(0.1)


def show_preview_blocking(fig: "MplFigure") -> None:
    """Show preview and block until window is closed."""
    import matplotlib.pyplot as plt
    plt.show(block=True)
