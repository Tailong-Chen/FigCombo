"""Figure - the main entry point for creating composite figures."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from matplotlib.figure import Figure as MplFigure

from figcombo.knowledge.journal_specs import get_journal_spec
from figcombo.knowledge.layout_templates import get_template
from figcombo.knowledge.validators import validate_figure
from figcombo.layout.parser import parse_ascii_layout, layout_from_explicit
from figcombo.layout.grid import compute_panel_sizes_mm
from figcombo.layout.types import LayoutGrid
from figcombo.panels.base import BasePanel
from figcombo.renderer import Renderer
from figcombo.styles.manager import StyleManager
from figcombo.export import save_figure, save_for_journal
from figcombo.utils import mm_to_inch, compute_figure_height


class Figure:
    """Main class for composing multi-panel scientific figures.

    Parameters
    ----------
    journal : str, optional
        Target journal key (e.g. 'nature', 'science', 'cell').
        Default 'nature'.
    size : str, optional
        Column size: 'single', 'mid', 'double'. Default 'double'.
    layout : str, optional
        ASCII art layout string defining panel arrangement.
    template : str, optional
        Name of a pre-defined layout template (alternative to layout).
    width_mm : float, optional
        Override figure width in mm (ignores journal/size).
    height_mm : float, optional
        Override figure height in mm. If None, auto-calculated.
    font_family : str, optional
        Override font family.
    font_size : float, optional
        Override base font size in pt.
    spacing_mm : float, optional
        Gap between panels in mm. Default 3.0.
    auto_label : bool, optional
        Automatically add panel labels (a, b, c...). Default True.

    Examples
    --------
    >>> fig = Figure(journal='nature', size='double_column', layout='''
    ...     aab
    ...     aac
    ...     ddd
    ... ''')
    >>> fig['a'] = ImagePanel('image.tif')
    >>> fig['b'] = PlotPanel(my_plot, data=df)
    >>> fig.save('Figure1.pdf')
    """

    def __init__(
        self,
        journal: str = 'nature',
        size: str = 'double',
        layout: str | None = None,
        template: str | None = None,
        width_mm: float | None = None,
        height_mm: float | None = None,
        font_family: str | None = None,
        font_size: float | None = None,
        spacing_mm: float = 3.0,
        auto_label: bool = True,
        **kwargs: Any,
    ):
        # Resolve journal spec
        self._journal_key = journal
        self._journal_spec = get_journal_spec(journal)

        # Resolve figure width
        if width_mm is not None:
            self._width_mm = width_mm
        else:
            widths = self._journal_spec.get('widths', {})
            # Normalize size name
            size_key = size.replace('_column', '').replace('-column', '')
            if size_key == 'double':
                size_key = 'double'
            elif size_key == 'single':
                size_key = 'single'
            elif size_key in ('1.5', 'mid', 'middle'):
                size_key = 'mid'
            self._width_mm = widths.get(size_key, widths.get('double', 183))

        # Parse layout
        self._layout: LayoutGrid | None = None
        if layout is not None:
            self._layout = parse_ascii_layout(layout)
        elif template is not None:
            tmpl = get_template(template)
            self._layout = parse_ascii_layout(tmpl['ascii'])

        # Resolve figure height
        if height_mm is not None:
            self._height_mm = height_mm
        elif self._layout is not None:
            self._height_mm = compute_figure_height(
                self._width_mm,
                self._layout.nrows,
                self._layout.ncols,
                self._layout.row_ratios,
                self._layout.col_ratios,
                spacing_mm,
            )
        else:
            # Default to golden ratio
            self._height_mm = self._width_mm / 1.618

        # Cap height to journal max
        max_h = self._journal_spec.get('max_height', 250)
        if self._height_mm > max_h:
            self._height_mm = max_h

        # Style
        self._style = StyleManager(
            journal_spec=self._journal_spec,
            font_family=font_family,
            font_size=font_size,
            **kwargs,
        )

        # State
        self._panels: dict[str, BasePanel] = {}
        self._spacing_mm = spacing_mm
        self._auto_label = auto_label
        self._rendered_figure: MplFigure | None = None

    # -- Layout setup --

    def set_layout(
        self,
        layout: str | None = None,
        template: str | None = None,
        rows: int | None = None,
        cols: int | None = None,
    ) -> 'Figure':
        """Set or change the layout.

        Parameters
        ----------
        layout : str, optional
            ASCII art layout string.
        template : str, optional
            Template name.
        rows : int, optional
            Number of rows (for explicit grid, use with add_panel).
        cols : int, optional
            Number of columns.

        Returns
        -------
        self
        """
        if layout is not None:
            self._layout = parse_ascii_layout(layout)
        elif template is not None:
            tmpl = get_template(template)
            self._layout = parse_ascii_layout(tmpl['ascii'])
        elif rows is not None and cols is not None:
            self._layout = LayoutGrid(
                panels={},
                nrows=rows,
                ncols=cols,
                row_ratios=[1.0] * rows,
                col_ratios=[1.0] * cols,
            )
        return self

    def add_panel(
        self,
        label: str,
        row: int,
        col: int,
        rowspan: int = 1,
        colspan: int = 1,
    ) -> 'Figure':
        """Add a panel position to an explicit grid layout.

        Parameters
        ----------
        label : str
            Panel label.
        row : int
            Starting row (0-based).
        col : int
            Starting column (0-based).
        rowspan : int
            Number of rows to span.
        colspan : int
            Number of columns to span.

        Returns
        -------
        self
        """
        from figcombo.layout.types import PanelPosition

        if self._layout is None:
            raise RuntimeError("Set layout first with set_layout(rows=, cols=)")

        self._layout.panels[label] = PanelPosition(
            label=label,
            row=row,
            col=col,
            rowspan=rowspan,
            colspan=colspan,
        )
        return self

    # -- Panel assignment --

    def __setitem__(self, label: str, panel: BasePanel) -> None:
        """Assign a panel by label: fig['a'] = ImagePanel(...)."""
        if not isinstance(panel, BasePanel):
            raise TypeError(
                f"Expected a BasePanel instance, got {type(panel).__name__}. "
                f"Use ImagePanel, PlotPanel, or TextPanel."
            )
        self._panels[label] = panel

    def __getitem__(self, label: str) -> BasePanel:
        """Get a panel by label."""
        return self._panels[label]

    def __contains__(self, label: str) -> bool:
        return label in self._panels

    # -- Rendering --

    def render(self) -> MplFigure:
        """Render the composite figure.

        Returns
        -------
        matplotlib.figure.Figure
        """
        if self._layout is None:
            raise RuntimeError(
                "No layout defined. Use layout= in constructor, "
                "set_layout(), or template=."
            )

        renderer = Renderer(
            layout=self._layout,
            panels=self._panels,
            style=self._style,
            figure_width_mm=self._width_mm,
            figure_height_mm=self._height_mm,
            spacing_mm=self._spacing_mm,
            auto_label=self._auto_label,
        )

        self._rendered_figure = renderer.render()
        return self._rendered_figure

    # -- Preview --

    def preview(self, block: bool = False) -> None:
        """Show an interactive preview of the figure.

        Parameters
        ----------
        block : bool
            If True, block until the preview window is closed.
        """
        if self._rendered_figure is None:
            self.render()

        from figcombo.preview import show_preview, show_preview_blocking
        if block:
            show_preview_blocking(self._rendered_figure)
        else:
            show_preview(self._rendered_figure)

    # -- Export --

    def save(
        self,
        path: str | Path,
        dpi: int | None = None,
        formats: list[str] | None = None,
        **kwargs: Any,
    ) -> list[Path]:
        """Save the figure to file(s).

        Parameters
        ----------
        path : str or Path
            Output path. Without extension saves in all formats.
        dpi : int, optional
            Override DPI.
        formats : list of str, optional
            Formats to save (e.g. ['pdf', 'png']).
        **kwargs
            Additional kwargs for savefig.

        Returns
        -------
        list of Path
            Paths to saved files.
        """
        if self._rendered_figure is None:
            self.render()

        return save_figure(
            self._rendered_figure,
            path,
            dpi=dpi,
            formats=formats,
            **kwargs,
        )

    def save_for_journal(
        self,
        path: str | Path,
        figure_type: str = 'combination',
    ) -> list[Path]:
        """Save using journal-specific settings.

        Parameters
        ----------
        path : str or Path
            Output path (without extension).
        figure_type : str
            'line_art', 'halftone', or 'combination'.
        """
        if self._rendered_figure is None:
            self.render()

        return save_for_journal(
            self._rendered_figure,
            path,
            self._journal_spec,
            figure_type,
        )

    # -- Validation --

    def validate(self) -> 'ValidationReport':
        """Validate the figure against journal specifications.

        Returns
        -------
        ValidationReport
        """
        panels_info = None
        if self._layout is not None and self._panels:
            sizes = compute_panel_sizes_mm(
                self._layout,
                self._width_mm,
                self._height_mm,
                self._spacing_mm,
            )
            panels_info = []
            for label, (w, h) in sizes.items():
                ptype = 'image' if hasattr(self._panels.get(label), 'path') else 'plot'
                panels_info.append({
                    'label': label,
                    'width_mm': w,
                    'height_mm': h,
                    'type': ptype,
                })

        return validate_figure(
            figure_width_mm=self._width_mm,
            figure_height_mm=self._height_mm,
            journal_spec=self._journal_spec,
            panels=panels_info,
            font_family=self._style.font_family,
            font_size=self._style.font_size,
        )

    # -- Convenience --

    def auto_label(self, enabled: bool = True) -> 'Figure':
        """Enable/disable automatic panel labeling."""
        self._auto_label = enabled
        return self

    @property
    def width_mm(self) -> float:
        return self._width_mm

    @property
    def height_mm(self) -> float:
        return self._height_mm

    @property
    def layout(self) -> LayoutGrid | None:
        return self._layout

    @property
    def panels(self) -> dict[str, BasePanel]:
        return self._panels

    @property
    def style(self) -> StyleManager:
        return self._style

    @property
    def mpl_figure(self) -> MplFigure | None:
        return self._rendered_figure

    def info(self) -> str:
        """Return a summary string of the figure configuration."""
        lines = [
            f"FigCombo Figure",
            f"  Journal:  {self._journal_spec.get('name', self._journal_key)}",
            f"  Size:     {self._width_mm:.0f} x {self._height_mm:.0f} mm",
            f"  Font:     {self._style.font_family} {self._style.font_size}pt",
            f"  Labels:   {self._style.label_style}",
            f"  Layout:   {self._layout}",
            f"  Panels:   {list(self._panels.keys()) or '(none assigned)'}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        journal = self._journal_spec.get('name', self._journal_key)
        n = len(self._panels)
        return f"Figure(journal='{journal}', {self._width_mm:.0f}x{self._height_mm:.0f}mm, {n} panels)"
