"""Layout engine for parsing ASCII art layouts and computing grid positions."""

from figcombo.layout.types import PanelPosition, LayoutGrid
from figcombo.layout.parser import parse_ascii_layout
from figcombo.layout.grid import compute_grid_spec

__all__ = [
    'PanelPosition',
    'LayoutGrid',
    'parse_ascii_layout',
    'compute_grid_spec',
]
