"""Molecular biology plot types for scientific figures.

This module provides visualizations for molecular biology analysis
including sequence logos and protein domain architecture diagrams.
All functions use colorblind-friendly default palettes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

import numpy as np

from figcombo.panels.plot_panel import register_plot_type

if TYPE_CHECKING:
    from matplotlib.axes import Axes


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

# Standard amino acid colors (hydrophobicity-based)
AA_COLORS = {
    'A': '#E6E600',  # Alanine - hydrophobic
    'C': '#E6E600',  # Cysteine - hydrophobic
    'D': '#E60A0A',  # Aspartic acid - acidic
    'E': '#E60A0A',  # Glutamic acid - acidic
    'F': '#3232AA',  # Phenylalanine - aromatic
    'G': '#EBEBEB',  # Glycine - neutral
    'H': '#3232AA',  # Histidine - basic
    'I': '#E6E600',  # Isoleucine - hydrophobic
    'K': '#145AFF',  # Lysine - basic
    'L': '#E6E600',  # Leucine - hydrophobic
    'M': '#E6E600',  # Methionine - hydrophobic
    'N': '#00DCDC',  # Asparagine - polar
    'P': '#DC9682',  # Proline - special
    'Q': '#00DCDC',  # Glutamine - polar
    'R': '#145AFF',  # Arginine - basic
    'S': '#FA9600',  # Serine - polar
    'T': '#FA9600',  # Threonine - polar
    'V': '#E6E600',  # Valine - hydrophobic
    'W': '#B45AB4',  # Tryptophan - aromatic
    'Y': '#3232AA',  # Tyrosine - aromatic
}

# Standard nucleotide colors
NT_COLORS = {
    'A': '#E69F00',  # Adenine - orange
    'C': '#0072B2',  # Cytosine - blue
    'G': '#009E73',  # Guanine - green
    'T': '#D55E00',  # Thymine - red
    'U': '#D55E00',  # Uracil - red
}


@register_plot_type('sequence_logo')
def sequence_logo(
    ax: 'Axes',
    data: Any,
    alphabet: str = 'dna',
    show_x_labels: bool = True,
    y_label: str = 'Bits',
    colors: dict[str, str] | None = None,
    font_name: str = 'sans-serif',
    stack_order: str = 'frequency',
    **kwargs: Any,
) -> None:
    """Create a sequence logo showing position-specific sequence conservation.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame, dict, or array-like
        Position-specific frequency matrix.
        - DataFrame: rows are positions, columns are letters
        - Dict: keys are positions, values are letter frequency dicts
        - Array: 2D array (positions x alphabet)
    alphabet : str, default 'dna'
        Type of sequence: 'dna', 'rna', 'protein', or custom string of characters.
    show_x_labels : bool, default True
        Whether to show position labels on x-axis.
    y_label : str, default 'Bits'
        Label for y-axis (typically 'Bits' for information content).
    colors : dict, optional
        Custom colors for each letter. Uses defaults if not specified.
    font_name : str, default 'sans-serif'
        Font family for letters.
    stack_order : str, default 'frequency'
        Order to stack letters: 'frequency' (high to low) or 'fixed' (alphabetical).
    **kwargs
        Additional arguments passed to text rendering.

    Examples
    --------
    >>> # With frequency matrix
    >>> freqs = {'A': [0.9, 0.1, 0.1], 'C': [0.1, 0.8, 0.1], ...}
    >>> sequence_logo(ax, freqs, alphabet='dna')

    >>> # With aligned sequences
    >>> sequences = ['ATGC', 'ATGA', 'ATTC', ...]
    >>> sequence_logo(ax, sequences, alphabet='dna')

    >>> # Custom protein logo
    >>> sequence_logo(ax, pwm_matrix, alphabet='protein', y_label='Probability')
    """
    import pandas as pd

    # Determine alphabet and colors
    if alphabet == 'dna':
        letters = list('ACGT')
        letter_colors = NT_COLORS
    elif alphabet == 'rna':
        letters = list('ACGU')
        letter_colors = NT_COLORS
    elif alphabet == 'protein':
        letters = list('ACDEFGHIKLMNPQRSTVWY')
        letter_colors = AA_COLORS
    else:
        letters = list(alphabet)
        letter_colors = {l: OKABE_ITO[i % len(OKABE_ITO)] for i, l in enumerate(letters)}

    if colors:
        letter_colors.update(colors)

    # Process input data
    if isinstance(data, pd.DataFrame):
        # DataFrame input
        freq_matrix = data[letters].values if all(l in data.columns for l in letters) else data.values
        positions = range(len(freq_matrix))
    elif isinstance(data, dict):
        # Dict of frequencies
        if isinstance(list(data.values())[0], dict):
            # {position: {letter: freq}}
            positions = sorted(data.keys())
            freq_matrix = np.array([[data[p].get(l, 0) for l in letters] for p in positions])
        else:
            # {letter: [freqs]}
            freq_matrix = np.array([data.get(l, [0]) for l in letters]).T
            positions = range(len(freq_matrix))
    elif isinstance(data, (list, tuple)) and isinstance(data[0], str):
        # List of sequences - calculate frequencies
        seqs = data
        seq_len = len(seqs[0])
        positions = range(seq_len)
        freq_matrix = np.zeros((seq_len, len(letters)))

        for seq in seqs:
            for i, char in enumerate(seq.upper()):
                if char in letters:
                    freq_matrix[i, letters.index(char)] += 1

        # Normalize
        freq_matrix = freq_matrix / len(seqs)
    else:
        # Array-like
        freq_matrix = np.asarray(data)
        positions = range(len(freq_matrix))

    # Ensure frequencies sum to 1
    freq_matrix = freq_matrix / freq_matrix.sum(axis=1, keepdims=True)

    # Calculate information content (bits)
    n_letters = len(letters)
    info_content = np.zeros(len(freq_matrix))
    for i in range(len(freq_matrix)):
        for j in range(n_letters):
            p = freq_matrix[i, j]
            if p > 0:
                info_content[i] += p * np.log2(p)
        info_content[i] = np.log2(n_letters) + info_content[i]

    # Scale frequencies by information content
    scaled_heights = freq_matrix * info_content[:, np.newaxis]

    # Plot each position
    for pos_idx in range(len(positions)):
        x = pos_idx
        y_bottom = 0

        # Get letter heights for this position
        heights = scaled_heights[pos_idx]

        # Sort letters by height
        if stack_order == 'frequency':
            letter_order = np.argsort(heights)[::-1]
        else:
            letter_order = range(len(letters))

        # Draw letters
        for letter_idx in letter_order:
            height = heights[letter_idx]
            if height > 0.001:  # Skip negligible heights
                letter = letters[letter_idx]
                color = letter_colors.get(letter, '#333333')

                # Draw letter as text, scaled by height
                ax.text(
                    x,
                    y_bottom + height / 2,
                    letter,
                    ha='center',
                    va='center',
                    fontsize=height * 20,  # Scale font size by height
                    color=color,
                    fontweight='bold',
                    fontfamily=font_name,
                    **kwargs
                )
                y_bottom += height

    # Formatting
    ax.set_xlim(-0.5, len(positions) - 0.5)
    ax.set_ylim(0, np.log2(n_letters) * 1.1)
    ax.set_xticks(range(len(positions)))
    if show_x_labels:
        ax.set_xticklabels([str(p + 1) for p in positions])
    else:
        ax.set_xticklabels([])
    ax.set_xlabel('Position')
    ax.set_ylabel(y_label)
    ax.set_yticks([0, 1, 2])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


@register_plot_type('domain_architecture')
def domain_architecture(
    ax: 'Axes',
    data: Any,
    protein_name: str | None = None,
    length: int | None = None,
    domain_col: str = 'domain',
    start_col: str = 'start',
    end_col: str = 'end',
    color_col: str | None = None,
    colors: dict[str, str] | None = None,
    show_labels: bool = True,
    label_size: float = 8,
    line_thickness: float = 4,
    domain_height: float = 0.6,
    **kwargs: Any,
) -> None:
    """Create a protein domain architecture diagram.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or list of dict
        Domain information with start, end, and domain names.
    protein_name : str, optional
        Name of protein to display as title.
    length : int, optional
        Total protein length. Inferred from domains if not provided.
    domain_col : str, default 'domain'
        Column name for domain names.
    start_col : str, default 'start'
        Column name for domain start positions.
    end_col : str, default 'end'
        Column name for domain end positions.
    color_col : str, optional
        Column name for custom domain colors.
    colors : dict, optional
        Mapping of domain names to colors. Uses Okabe-Ito palette by default.
    show_labels : bool, default True
        Whether to show domain name labels.
    label_size : float, default 8
        Font size for domain labels.
    line_thickness : float, default 4
        Thickness of the protein backbone line.
    domain_height : float, default 0.6
        Height of domain boxes (relative to axis).
    **kwargs
        Additional arguments passed to rectangle patches.

    Examples
    --------
    >>> # With DataFrame
    >>> domains = pd.DataFrame({
    ...     'domain': ['Kinase', 'SH2', 'SH3'],
    ...     'start': [1, 150, 250],
    ...     'end': [140, 220, 300]
    ... })
    >>> domain_architecture(ax, domains, protein_name='SRC', length=536)

    >>> # With list of dicts
    >>> domains = [
    ...     {'name': 'TM1', 'start': 10, 'end': 30, 'type': 'transmembrane'},
    ...     {'name': 'TM2', 'start': 50, 'end': 70, 'type': 'transmembrane'},
    ... ]
    >>> domain_architecture(ax, domains, length=100)

    >>> # Custom colors
    >>> colors = {'Kinase': '#E69F00', 'SH2': '#56B4E9', 'SH3': '#009E73'}
    >>> domain_architecture(ax, domains, colors=colors)
    """
    import pandas as pd
    from matplotlib.patches import FancyBboxPatch, Rectangle

    # Convert to DataFrame if needed
    if isinstance(data, list):
        data = pd.DataFrame(data)

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a DataFrame or list of dicts")

    # Determine protein length
    if length is None:
        length = data[end_col].max() if end_col in data.columns else data['end'].max()

    # Default colors
    if colors is None:
        # Use Okabe-Ito palette cycling through domains
        unique_domains = data[domain_col].unique() if domain_col in data.columns else data['domain'].unique()
        colors = {d: OKABE_ITO[i % len(OKABE_ITO)] for i, d in enumerate(unique_domains)}

    # Draw protein backbone
    ax.plot([0, length], [0, 0], color='black', linewidth=line_thickness, solid_capstyle='round')

    # Draw domains
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0] if ax.get_ylim() != (0, 1) else 1
    box_height = domain_height

    for idx, row in data.iterrows():
        domain = row[domain_col] if domain_col in row else row.get('name', f'Domain {idx}')
        start = row[start_col] if start_col in row else row.get('start', 0)
        end = row[end_col] if end_col in row else row.get('end', start + 50)

        # Get color
        if color_col and color_col in row:
            color = row[color_col]
        else:
            color = colors.get(domain, OKABE_ITO[idx % len(OKABE_ITO)])

        # Draw domain box
        width = end - start
        rect = FancyBboxPatch(
            (start, -box_height / 2),
            width,
            box_height,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            **kwargs
        )
        ax.add_patch(rect)

        # Add label
        if show_labels:
            label_text = str(domain)
            # Truncate long labels
            if len(label_text) > 10:
                label_text = label_text[:8] + '...'

            ax.text(
                (start + end) / 2,
                0,
                label_text,
                ha='center',
                va='center',
                fontsize=label_size,
                fontweight='bold',
                color='white' if _is_dark_color(color) else 'black'
            )

    # Add scale bar
    scale_length = _nice_round(length / 5)
    ax.plot([length - scale_length, length], [-box_height - 0.3, -box_height - 0.3],
           color='black', linewidth=2)
    ax.text(length - scale_length / 2, -box_height - 0.5, f'{int(scale_length)} aa',
           ha='center', va='top', fontsize=7)

    # Formatting
    ax.set_xlim(-length * 0.02, length * 1.02)
    ax.set_ylim(-box_height - 0.6, box_height + 0.3)
    ax.set_xlabel('Amino Acid Position')
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    if protein_name:
        ax.set_title(protein_name, fontsize=10, fontweight='bold')


def _is_dark_color(color: str) -> bool:
    """Determine if a color is dark (for text color selection)."""
    # Convert hex to RGB
    color = color.lstrip('#')
    if len(color) == 3:
        color = ''.join([c*2 for c in color])
    r = int(color[0:2], 16) / 255
    g = int(color[2:4], 16) / 255
    b = int(color[4:6], 16) / 255

    # Calculate luminance
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < 0.5


def _nice_round(x: float) -> float:
    """Round to a nice number for scale bars."""
    if x >= 100:
        return round(x, -2)
    elif x >= 10:
        return round(x, -1)
    else:
        return round(x)
