"""Interactive preview window for figure visualization.

Provides a Tkinter-based preview with:
- Actual size / fit-to-window display
- Grid overlay toggle
- Panel info on hover
- Keyboard shortcuts (G=grid, F=fit, 1=100%, +/-=zoom, S=save, Q=quit)
- Bottom info bar showing dimensions, journal, zoom level
"""

from __future__ import annotations

import io
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure as MplFigure
    from figcombo.layout.types import LayoutGrid
    from figcombo.styles.manager import StyleManager


class PreviewWindow:
    """Interactive preview window for composite figures.

    Parameters
    ----------
    mpl_figure : matplotlib.figure.Figure
        The rendered figure to display.
    title : str
        Window title.
    figure_width_mm : float
        Figure width in mm (for info display).
    figure_height_mm : float
        Figure height in mm (for info display).
    journal_name : str
        Journal name (for info display).
    layout : LayoutGrid, optional
        Layout grid for panel hover info.
    style : StyleManager, optional
        Style manager for additional info.
    """

    def __init__(
        self,
        mpl_figure: MplFigure,
        title: str = 'FigCombo Preview',
        figure_width_mm: float = 0,
        figure_height_mm: float = 0,
        journal_name: str = '',
        layout: LayoutGrid | None = None,
        style: StyleManager | None = None,
    ):
        self._mpl_figure = mpl_figure
        self._title = title
        self._width_mm = figure_width_mm
        self._height_mm = figure_height_mm
        self._journal_name = journal_name
        self._layout = layout
        self._style = style

        self._zoom = 1.0
        self._grid_visible = False
        self._grid_artists: list[Any] = []

        # References set during show()
        self._root: Any = None
        self._canvas: Any = None
        self._info_var: Any = None
        self._hover_var: Any = None

    def show(self, block: bool = True) -> None:
        """Display the preview window.

        Parameters
        ----------
        block : bool
            If True, block until window is closed. Default True.
        """
        import tkinter as tk
        from tkinter import ttk

        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg,
            NavigationToolbar2Tk,
        )

        # --- Create window ---
        self._root = tk.Tk()
        self._root.title(self._title)
        self._root.geometry('1200x900')
        self._root.minsize(600, 400)

        # --- Main frame ---
        main_frame = ttk.Frame(self._root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Toolbar frame ---
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # --- Canvas with scrollbars ---
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Embed matplotlib figure
        self._canvas = FigureCanvasTkAgg(self._mpl_figure, master=canvas_frame)
        canvas_widget = self._canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Navigation toolbar (zoom, pan, save built-in)
        toolbar = NavigationToolbar2Tk(self._canvas, toolbar_frame)
        toolbar.update()

        # --- Custom button bar ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        ttk.Button(btn_frame, text='Fit Window [F]',
                   command=self._fit_to_window).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='100% [1]',
                   command=self._actual_size).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Zoom In [+]',
                   command=self._zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Zoom Out [-]',
                   command=self._zoom_out).pack(side=tk.LEFT, padx=2)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5)

        self._grid_btn_text = tk.StringVar(value='Show Grid [G]')
        ttk.Button(btn_frame, textvariable=self._grid_btn_text,
                   command=self._toggle_grid).pack(side=tk.LEFT, padx=2)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(btn_frame, text='Save PDF',
                   command=lambda: self._quick_save('pdf')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Save PNG',
                   command=lambda: self._quick_save('png')).pack(side=tk.LEFT, padx=2)

        # --- Info bar ---
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self._info_var = tk.StringVar()
        self._hover_var = tk.StringVar(value='')
        self._update_info_text()

        ttk.Label(info_frame, textvariable=self._info_var,
                  relief=tk.SUNKEN, anchor=tk.W).pack(
                      side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=1)
        ttk.Label(info_frame, textvariable=self._hover_var,
                  relief=tk.SUNKEN, anchor=tk.E, width=40).pack(
                      side=tk.RIGHT, padx=2, pady=1)

        # --- Keyboard shortcuts ---
        self._root.bind('<Key-g>', lambda e: self._toggle_grid())
        self._root.bind('<Key-G>', lambda e: self._toggle_grid())
        self._root.bind('<Key-f>', lambda e: self._fit_to_window())
        self._root.bind('<Key-F>', lambda e: self._fit_to_window())
        self._root.bind('<Key-1>', lambda e: self._actual_size())
        self._root.bind('<Key-plus>', lambda e: self._zoom_in())
        self._root.bind('<Key-equal>', lambda e: self._zoom_in())
        self._root.bind('<Key-minus>', lambda e: self._zoom_out())
        self._root.bind('<Key-q>', lambda e: self._root.destroy())
        self._root.bind('<Key-Q>', lambda e: self._root.destroy())
        self._root.bind('<Key-s>', lambda e: self._save_dialog())
        self._root.bind('<Key-S>', lambda e: self._save_dialog())

        # Mouse motion for panel hover
        self._canvas.mpl_connect('motion_notify_event', self._on_mouse_move)

        # Start with fit-to-window
        self._root.after(100, self._fit_to_window)

        self._canvas.draw()

        if block:
            self._root.mainloop()
        else:
            self._root.update()

    # --- Zoom controls ---

    def _set_zoom(self, zoom: float) -> None:
        """Set zoom level and resize canvas."""
        self._zoom = max(0.25, min(zoom, 5.0))

        # Get figure size in inches
        fig_w, fig_h = self._mpl_figure.get_size_inches()

        # At 100%, display at screen DPI (approx 96)
        screen_dpi = 96
        pixel_w = int(fig_w * screen_dpi * self._zoom)
        pixel_h = int(fig_h * screen_dpi * self._zoom)

        self._mpl_figure.set_dpi(screen_dpi * self._zoom)
        self._canvas.get_tk_widget().config(width=pixel_w, height=pixel_h)
        self._canvas.draw()
        self._update_info_text()

    def _fit_to_window(self) -> None:
        """Fit figure to window size."""
        if self._root is None:
            return

        self._root.update_idletasks()
        # Get available canvas area
        widget = self._canvas.get_tk_widget()
        avail_w = widget.winfo_width() or 800
        avail_h = widget.winfo_height() or 600

        fig_w, fig_h = self._mpl_figure.get_size_inches()
        screen_dpi = 96

        # Calculate zoom to fit
        zoom_w = avail_w / (fig_w * screen_dpi)
        zoom_h = avail_h / (fig_h * screen_dpi)
        zoom = min(zoom_w, zoom_h) * 0.95  # 5% margin

        self._set_zoom(zoom)

    def _actual_size(self) -> None:
        """Display at 100% zoom (1 mm on screen ~ 1 mm printed)."""
        self._set_zoom(1.0)

    def _zoom_in(self) -> None:
        self._set_zoom(self._zoom * 1.25)

    def _zoom_out(self) -> None:
        self._set_zoom(self._zoom / 1.25)

    # --- Grid overlay ---

    def _toggle_grid(self) -> None:
        """Toggle grid overlay showing panel boundaries."""
        self._grid_visible = not self._grid_visible

        if self._grid_visible:
            self._draw_grid()
            self._grid_btn_text.set('Hide Grid [G]')
        else:
            self._remove_grid()
            self._grid_btn_text.set('Show Grid [G]')

        self._canvas.draw()

    def _draw_grid(self) -> None:
        """Draw grid lines on figure to show panel boundaries."""
        self._remove_grid()

        for ax in self._mpl_figure.get_axes():
            # Get axes position in figure coords
            bbox = ax.get_position()

            # Draw rectangle around each panel
            import matplotlib.patches as patches
            rect = patches.FancyBboxPatch(
                (bbox.x0, bbox.y0), bbox.width, bbox.height,
                transform=self._mpl_figure.transFigure,
                fill=False,
                edgecolor='#FF4444',
                linewidth=1.5,
                linestyle='--',
                boxstyle='round,pad=0.005',
                clip_on=False,
            )
            self._mpl_figure.add_artist(rect)
            self._grid_artists.append(rect)

            # Add size info in mm at center
            if self._width_mm > 0 and self._height_mm > 0:
                panel_w_mm = bbox.width * self._width_mm
                panel_h_mm = bbox.height * self._height_mm
                size_text = self._mpl_figure.text(
                    bbox.x0 + bbox.width / 2,
                    bbox.y0 + bbox.height / 2,
                    f'{panel_w_mm:.0f}x{panel_h_mm:.0f}mm',
                    transform=self._mpl_figure.transFigure,
                    ha='center', va='center',
                    fontsize=9, color='#FF4444',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2',
                              facecolor='white', alpha=0.85,
                              edgecolor='#FF4444', linewidth=0.5),
                )
                self._grid_artists.append(size_text)

    def _remove_grid(self) -> None:
        """Remove grid overlay."""
        for artist in self._grid_artists:
            artist.remove()
        self._grid_artists.clear()

    # --- Mouse hover ---

    def _on_mouse_move(self, event: Any) -> None:
        """Handle mouse movement for panel hover info."""
        if event.inaxes is None:
            self._hover_var.set('')
            return

        ax = event.inaxes

        # Find which panel this axes belongs to
        label = '?'
        if self._layout is not None:
            from figcombo.layout.grid import compute_panel_sizes_mm
            sizes = compute_panel_sizes_mm(
                self._layout,
                self._width_mm,
                self._height_mm,
            )

            # Match axes to label via figure axes list
            for i, fig_ax in enumerate(self._mpl_figure.get_axes()):
                if fig_ax is ax:
                    labels = self._layout.labels
                    if i < len(labels):
                        label = labels[i]
                    break

            if label in sizes:
                w, h = sizes[label]
                self._hover_var.set(
                    f'Panel {label}: {w:.0f}x{h:.0f}mm  |  '
                    f'cursor: ({event.xdata:.2f}, {event.ydata:.2f})'
                )
                return

        # Fallback
        if event.xdata is not None:
            self._hover_var.set(f'cursor: ({event.xdata:.2f}, {event.ydata:.2f})')
        else:
            self._hover_var.set('')

    # --- Save ---

    def _quick_save(self, fmt: str) -> None:
        """Quick save in specified format."""
        from tkinter import filedialog

        filetypes = {
            'pdf': [('PDF files', '*.pdf')],
            'png': [('PNG files', '*.png')],
            'tiff': [('TIFF files', '*.tiff')],
            'svg': [('SVG files', '*.svg')],
            'eps': [('EPS files', '*.eps')],
        }

        path = filedialog.asksaveasfilename(
            defaultextension=f'.{fmt}',
            filetypes=filetypes.get(fmt, [('All files', '*.*')]),
            title=f'Save as {fmt.upper()}',
        )

        if path:
            dpi = 300 if fmt in ('png', 'tiff') else 300
            self._mpl_figure.savefig(
                path,
                format=fmt,
                dpi=dpi,
                bbox_inches='tight',
                pad_inches=0.02,
            )
            self._hover_var.set(f'Saved: {path}')

    def _save_dialog(self) -> None:
        """Open save dialog."""
        self._quick_save('pdf')

    # --- Info display ---

    def _update_info_text(self) -> None:
        """Update the info bar text."""
        parts = []
        if self._journal_name:
            parts.append(self._journal_name)
        if self._width_mm > 0:
            parts.append(f'{self._width_mm:.0f}x{self._height_mm:.0f}mm')
        parts.append(f'Zoom: {self._zoom * 100:.0f}%')

        if self._layout:
            parts.append(f'{self._layout.num_panels} panels')

        if self._style:
            parts.append(f'{self._style.font_family} {self._style.font_size}pt')

        shortcuts = 'G=Grid  F=Fit  1=100%  +/-=Zoom  S=Save  Q=Quit'
        self._info_var.set('  |  '.join(parts) + '    [' + shortcuts + ']')


# --- Public API functions ---

def create_preview(
    mpl_figure: MplFigure,
    figure_width_mm: float = 0,
    figure_height_mm: float = 0,
    journal_name: str = '',
    layout: LayoutGrid | None = None,
    style: StyleManager | None = None,
) -> PreviewWindow:
    """Create a PreviewWindow instance.

    Parameters
    ----------
    mpl_figure : matplotlib.figure.Figure
    figure_width_mm : float
    figure_height_mm : float
    journal_name : str
    layout : LayoutGrid, optional
    style : StyleManager, optional

    Returns
    -------
    PreviewWindow
    """
    return PreviewWindow(
        mpl_figure=mpl_figure,
        figure_width_mm=figure_width_mm,
        figure_height_mm=figure_height_mm,
        journal_name=journal_name,
        layout=layout,
        style=style,
    )


def show_preview(
    mpl_figure: MplFigure,
    figure_width_mm: float = 0,
    figure_height_mm: float = 0,
    journal_name: str = '',
    layout: LayoutGrid | None = None,
    style: StyleManager | None = None,
) -> None:
    """Show a non-blocking preview window.

    Falls back to matplotlib.pyplot.show() if Tkinter is not available.
    """
    try:
        pw = create_preview(
            mpl_figure, figure_width_mm, figure_height_mm,
            journal_name, layout, style,
        )
        pw.show(block=False)
    except Exception:
        import matplotlib.pyplot as plt
        plt.show(block=False)
        plt.pause(0.1)


def show_preview_blocking(
    mpl_figure: MplFigure,
    figure_width_mm: float = 0,
    figure_height_mm: float = 0,
    journal_name: str = '',
    layout: LayoutGrid | None = None,
    style: StyleManager | None = None,
) -> None:
    """Show a blocking preview window (waits until closed).

    Falls back to matplotlib.pyplot.show() if Tkinter is not available.
    """
    try:
        pw = create_preview(
            mpl_figure, figure_width_mm, figure_height_mm,
            journal_name, layout, style,
        )
        pw.show(block=True)
    except Exception:
        import matplotlib.pyplot as plt
        plt.show(block=True)
