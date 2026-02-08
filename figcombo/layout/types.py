"""Data structures for layout representation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PanelPosition:
    """Position and span of a single panel in the grid.

    Attributes
    ----------
    label : str
        Panel label character (e.g. 'a', 'b', 'c').
    row : int
        Starting row index (0-based).
    col : int
        Starting column index (0-based).
    rowspan : int
        Number of rows this panel spans.
    colspan : int
        Number of columns this panel spans.
    """
    label: str
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1

    @property
    def row_end(self) -> int:
        """Exclusive end row index."""
        return self.row + self.rowspan

    @property
    def col_end(self) -> int:
        """Exclusive end column index."""
        return self.col + self.colspan

    @property
    def area(self) -> int:
        """Grid area in cells."""
        return self.rowspan * self.colspan

    def __repr__(self) -> str:
        span = ""
        if self.rowspan > 1 or self.colspan > 1:
            span = f", span={self.rowspan}x{self.colspan}"
        return f"PanelPosition('{self.label}', row={self.row}, col={self.col}{span})"


@dataclass
class LayoutGrid:
    """Complete grid layout containing all panel positions.

    Attributes
    ----------
    panels : dict mapping label -> PanelPosition
    nrows : int
        Total number of grid rows.
    ncols : int
        Total number of grid columns.
    row_ratios : list of float
        Relative height ratios for each row.
    col_ratios : list of float
        Relative width ratios for each column.
    """
    panels: dict[str, PanelPosition] = field(default_factory=dict)
    nrows: int = 0
    ncols: int = 0
    row_ratios: list[float] = field(default_factory=list)
    col_ratios: list[float] = field(default_factory=list)

    @property
    def labels(self) -> list[str]:
        """Panel labels in sorted order."""
        return sorted(self.panels.keys())

    @property
    def num_panels(self) -> int:
        return len(self.panels)

    def get_panel(self, label: str) -> PanelPosition:
        """Get panel position by label."""
        if label not in self.panels:
            raise KeyError(f"Panel '{label}' not found. Available: {self.labels}")
        return self.panels[label]

    def __repr__(self) -> str:
        return (
            f"LayoutGrid({self.nrows}x{self.ncols}, "
            f"panels=[{', '.join(self.labels)}])"
        )
