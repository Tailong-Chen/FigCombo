"""Parse ASCII art layout strings into structured LayoutGrid objects."""

from __future__ import annotations

from figcombo.layout.types import PanelPosition, LayoutGrid


def parse_ascii_layout(layout_str: str) -> LayoutGrid:
    """Parse an ASCII art layout string into a LayoutGrid.

    Each character represents a panel. Same characters that form a
    contiguous rectangular region are merged into one panel.
    Spaces and '.' are treated as empty cells.

    Parameters
    ----------
    layout_str : str
        Multi-line ASCII layout, e.g.::

            aab
            aac
            ddd

    Returns
    -------
    LayoutGrid
        Parsed grid layout with panel positions.

    Raises
    ------
    ValueError
        If the layout is invalid (non-rectangular regions, empty, etc.)

    Examples
    --------
    >>> grid = parse_ascii_layout('''
    ...     aab
    ...     aac
    ...     ddd
    ... ''')
    >>> grid.nrows, grid.ncols
    (3, 3)
    >>> grid.get_panel('a')
    PanelPosition('a', row=0, col=0, span=2x2)
    """
    # Clean and split into rows
    lines = _clean_layout_lines(layout_str)
    if not lines:
        raise ValueError("Empty layout string")

    # Validate rectangular grid
    ncols = len(lines[0])
    for i, line in enumerate(lines):
        if len(line) != ncols:
            raise ValueError(
                f"Layout row {i} has {len(line)} columns, "
                f"expected {ncols}. All rows must have equal length."
            )

    nrows = len(lines)

    # Build character grid
    grid = []
    for line in lines:
        row = list(line)
        grid.append(row)

    # Find all unique panel labels (exclude space and dot)
    labels: set[str] = set()
    for row in grid:
        for ch in row:
            if ch not in (' ', '.'):
                labels.add(ch)

    # For each label, find its bounding rectangle
    panels: dict[str, PanelPosition] = {}
    for label in sorted(labels):
        positions = []
        for r in range(nrows):
            for c in range(ncols):
                if grid[r][c] == label:
                    positions.append((r, c))

        if not positions:
            continue

        min_r = min(r for r, c in positions)
        max_r = max(r for r, c in positions)
        min_c = min(c for r, c in positions)
        max_c = max(c for r, c in positions)

        # Validate that the label forms a complete rectangle
        expected_cells = (max_r - min_r + 1) * (max_c - min_c + 1)
        if len(positions) != expected_cells:
            raise ValueError(
                f"Panel '{label}' does not form a rectangle. "
                f"Found {len(positions)} cells but expected {expected_cells} "
                f"for bounding box rows [{min_r}:{max_r+1}] cols [{min_c}:{max_c+1}]."
            )

        panels[label] = PanelPosition(
            label=label,
            row=min_r,
            col=min_c,
            rowspan=max_r - min_r + 1,
            colspan=max_c - min_c + 1,
        )

    # Compute row and column ratios (uniform by default)
    row_ratios = [1.0] * nrows
    col_ratios = [1.0] * ncols

    return LayoutGrid(
        panels=panels,
        nrows=nrows,
        ncols=ncols,
        row_ratios=row_ratios,
        col_ratios=col_ratios,
    )


def _clean_layout_lines(layout_str: str) -> list[str]:
    """Clean a layout string: strip, remove empty lines, dedent, remove borders.

    Returns list of equal-length strings.
    """
    lines = layout_str.split('\n')

    # Remove leading/trailing empty lines
    while lines and lines[0].strip() == '':
        lines.pop(0)
    while lines and lines[-1].strip() == '':
        lines.pop()

    if not lines:
        return []

    # Find minimum indentation
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            stripped = len(line) - len(line.lstrip())
            min_indent = min(min_indent, stripped)

    if min_indent == float('inf'):
        min_indent = 0

    # Strip indentation and remove decorative border characters
    border_chars = '+|─━┄┅┈┉╌═░▒▓█'
    result = []
    for line in lines:
        cleaned = line[int(min_indent):]
        # Remove border characters but keep panel labels and spaces
        cleaned = ''.join(c if c.isalnum() or c in ' .' else ' ' for c in cleaned)
        result.append(cleaned)

    # Pad to equal length
    max_len = max(len(line) for line in result)
    result = [line.ljust(max_len) for line in result]

    return result


def layout_from_explicit(
    nrows: int,
    ncols: int,
    panel_specs: list[dict],
) -> LayoutGrid:
    """Create a LayoutGrid from explicit panel specifications.

    Parameters
    ----------
    nrows : int
        Number of grid rows.
    ncols : int
        Number of grid columns.
    panel_specs : list of dict
        Each dict has keys: 'label', 'row', 'col', and optionally
        'rowspan' (default 1), 'colspan' (default 1).

    Returns
    -------
    LayoutGrid
    """
    panels = {}
    for spec in panel_specs:
        label = spec['label']
        panels[label] = PanelPosition(
            label=label,
            row=spec['row'],
            col=spec['col'],
            rowspan=spec.get('rowspan', 1),
            colspan=spec.get('colspan', 1),
        )

    return LayoutGrid(
        panels=panels,
        nrows=nrows,
        ncols=ncols,
        row_ratios=[1.0] * nrows,
        col_ratios=[1.0] * ncols,
    )
