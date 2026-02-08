"""Panel types for figure composition."""

from figcombo.panels.base import BasePanel
from figcombo.panels.image_panel import ImagePanel
from figcombo.panels.plot_panel import PlotPanel, register_plot_type, list_plot_types
from figcombo.panels.text_panel import TextPanel
from figcombo.panels.composite_panel import CompositePanel

__all__ = [
    'BasePanel',
    'ImagePanel',
    'PlotPanel',
    'TextPanel',
    'CompositePanel',
    'register_plot_type',
    'list_plot_types',
]
