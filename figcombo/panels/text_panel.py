"""TextPanel - display text content in a panel."""

from __future__ import annotations

from typing import Any, Optional

from matplotlib.axes import Axes

from figcombo.panels.base import BasePanel


class TextPanel(BasePanel):
    """Panel that displays text content.

    Useful for adding scheme descriptions, figure titles within the
    composite figure, or annotation text blocks.

    Parameters
    ----------
    text : str
        The text content to display.
    fontsize : float, optional
        Font size in points. Default uses the global style.
    fontweight : str, optional
        Font weight ('normal', 'bold'). Default 'normal'.
    ha : str, optional
        Horizontal alignment ('left', 'center', 'right'). Default 'center'.
    va : str, optional
        Vertical alignment ('top', 'center', 'bottom'). Default 'center'.
    wrap : bool, optional
        Whether to wrap long lines. Default True.
    background_color : str or None, optional
        Background color. None for transparent.
    """

    def __init__(
        self,
        text: str,
        fontsize: float | None = None,
        fontweight: str = 'normal',
        ha: str = 'center',
        va: str = 'center',
        wrap: bool = True,
        background_color: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.text = text
        self.fontsize = fontsize
        self.fontweight = fontweight
        self.ha = ha
        self.va = va
        self.wrap = wrap
        self.background_color = background_color

    def render(self, ax: Axes) -> None:
        """Render text content onto the axes."""
        ax.set_axis_off()

        if self.background_color:
            ax.set_facecolor(self.background_color)

        # Position mapping
        x_pos = {'left': 0.05, 'center': 0.5, 'right': 0.95}[self.ha]
        y_pos = {'top': 0.95, 'center': 0.5, 'bottom': 0.05}[self.va]

        text_kwargs: dict[str, Any] = {
            'ha': self.ha,
            'va': self.va,
            'fontweight': self.fontweight,
            'transform': ax.transAxes,
            'wrap': self.wrap,
        }
        if self.fontsize is not None:
            text_kwargs['fontsize'] = self.fontsize

        ax.text(x_pos, y_pos, self.text, **text_kwargs)

    def __repr__(self) -> str:
        preview = self.text[:30] + '...' if len(self.text) > 30 else self.text
        return f"TextPanel('{preview}')"
