"""FigCombo - Compose publication-ready multi-panel scientific figures.

Designed for Nature, Science, Cell and other journal specifications.

Quick Start
-----------
>>> from figcombo import Figure, ImagePanel, PlotPanel
>>> fig = Figure(journal='nature', size='double_column', layout='''
...     aab
...     aac
...     ddd
... ''')
>>> fig['a'] = ImagePanel('microscopy.tif')
>>> fig['b'] = PlotPanel(my_barplot, data=df)
>>> fig['c'] = PlotPanel(my_boxplot, data=df)
>>> fig['d'] = ImagePanel('blot.png', trim=True)
>>> fig.save('Figure1.pdf')
"""

__version__ = '0.1.0'

from figcombo.figure import Figure
from figcombo.panels.base import BasePanel
from figcombo.panels.image_panel import ImagePanel
from figcombo.panels.plot_panel import PlotPanel, register_plot_type, list_plot_types
from figcombo.panels.text_panel import TextPanel
from figcombo.knowledge.layout_templates import list_templates

__all__ = [
    'Figure',
    'BasePanel',
    'ImagePanel',
    'PlotPanel',
    'TextPanel',
    'register_plot_type',
    'list_plot_types',
    'list_templates',
]
