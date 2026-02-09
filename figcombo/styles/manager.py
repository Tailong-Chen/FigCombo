"""StyleManager - unified font, size, and color management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt


# Okabe-Ito colorblind-safe palette
OKABE_ITO = [
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#F0E442',  # yellow
    '#0072B2',  # blue
    '#D55E00',  # vermillion
    '#CC79A7',  # reddish purple
    '#000000',  # black
]

MPLSTYLE_DIR = Path(__file__).parent / 'mplstyles'


class StyleManager:
    """Manages global figure styling based on journal specifications.

    Parameters
    ----------
    journal_spec : dict
        Resolved journal specification from get_journal_spec().
    font_family : str, optional
        Override font family.
    font_size : float, optional
        Override base font size in pt.
    label_style : str, optional
        Override panel label style.
    palette : list of str, optional
        Override color palette.
    """

    def __init__(
        self,
        journal_spec: dict[str, Any],
        font_family: str | None = None,
        font_size: float | None = None,
        label_style: str | None = None,
        palette: list[str] | None = None,
    ):
        self.journal_spec = journal_spec
        self._font_spec = journal_spec.get('font', {})

        # Resolve settings (user override > journal default)
        self.font_family = font_family or self._font_spec.get('family', ['Arial'])[0]
        self.font_size = font_size or self._font_spec.get('recommended_size', 7)
        self.label_style = label_style or journal_spec.get('label_style', 'lowercase_bold')
        self.palette = palette or OKABE_ITO.copy()

        # Derived sizes
        self.label_size = self._font_spec.get('label_size', self.font_size + 1)
        self.tick_size = max(self.font_size - 1, self._font_spec.get('min_size', 5))
        self.title_size = self.font_size + 1

    def apply(self) -> None:
        """Apply style settings to matplotlib rcParams."""
        mpl.rcParams.update({
            # Font
            'font.family': 'sans-serif',
            'font.sans-serif': [self.font_family, 'Arial', 'Helvetica', 'DejaVu Sans'],
            'font.size': self.font_size,
            'axes.labelsize': self.font_size,
            'axes.titlesize': self.title_size,
            'xtick.labelsize': self.tick_size,
            'ytick.labelsize': self.tick_size,
            'legend.fontsize': self.tick_size,

            # Lines and markers
            'lines.linewidth': 1.0,
            'lines.markersize': 4,

            # Axes
            'axes.linewidth': 0.8,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.prop_cycle': plt.cycler(color=self.palette),

            # Ticks
            'xtick.major.width': 0.8,
            'ytick.major.width': 0.8,
            'xtick.major.size': 3,
            'ytick.major.size': 3,
            'xtick.direction': 'out',
            'ytick.direction': 'out',

            # Legend
            'legend.frameon': False,
            'legend.borderpad': 0.3,

            # Figure
            'figure.dpi': 150,
            'savefig.dpi': 300,
            'savefig.transparent': False,
            # NOTE: Do NOT set savefig.bbox='tight' here — it conflicts
            # with constrained_layout and can collapse small axes.
            'savefig.pad_inches': 0.02,

            # PDF
            'pdf.fonttype': 42,  # TrueType (editable text in Illustrator)
            'ps.fonttype': 42,
        })

    def apply_mplstyle(self, journal: str) -> None:
        """Apply journal-specific matplotlib style file if available."""
        style_file = MPLSTYLE_DIR / f'{journal}.mplstyle'
        if style_file.exists():
            plt.style.use(str(style_file))

    def format_label(self, label: str) -> str:
        """Format a panel label according to the journal's label style.

        Parameters
        ----------
        label : str
            Raw label character (e.g. 'a').

        Returns
        -------
        str
            Formatted label.
        """
        if 'uppercase' in self.label_style:
            return label.upper()
        return label.lower()

    @property
    def label_fontweight(self) -> str:
        """Font weight for panel labels."""
        if 'bold' in self.label_style:
            return 'bold'
        return 'normal'

    @property
    def label_fontstyle(self) -> str:
        """Font style for panel labels."""
        if 'italic' in self.label_style:
            return 'italic'
        return 'normal'

    def get_label_kwargs(self) -> dict[str, Any]:
        """Get matplotlib text kwargs for panel labels."""
        return {
            'fontsize': self.label_size,
            'fontweight': self.label_fontweight,
            'fontstyle': self.label_fontstyle,
            'fontfamily': self.font_family,
        }

    def __repr__(self) -> str:
        journal = self.journal_spec.get('name', '?')
        return (
            f"StyleManager(journal='{journal}', "
            f"font='{self.font_family}' {self.font_size}pt, "
            f"label='{self.label_style}')"
        )
