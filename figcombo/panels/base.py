"""Base panel abstract class defining the common interface for all panel types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes


class BasePanel(ABC):
    """Abstract base class for all panel types.

    All panels must implement `render(ax)` to draw their content
    onto a matplotlib Axes object.

    Parameters
    ----------
    padding : tuple of float, optional
        Internal padding (left, right, top, bottom) in points.
        Default is (0, 0, 0, 0).
    """

    def __init__(self, padding: tuple[float, ...] = (0, 0, 0, 0), **kwargs: Any):
        self.padding = padding
        self._extra_kwargs = kwargs

    @abstractmethod
    def render(self, ax: Axes) -> None:
        """Render this panel's content onto the given Axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to draw on. The panel should draw all its content
            within this axes area.
        """
        ...

    def get_preferred_aspect(self) -> Optional[float]:
        """Return preferred width/height aspect ratio, or None for flexible.

        Returns
        -------
        float or None
            Aspect ratio (width / height). None means the panel will
            adapt to whatever size is given by the layout.
        """
        return None

    def validate(self) -> list[str]:
        """Validate panel configuration.

        Returns
        -------
        list of str
            List of warning/error messages. Empty list if valid.
        """
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
