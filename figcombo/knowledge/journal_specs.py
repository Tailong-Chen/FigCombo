"""Journal-specific figure specifications for major scientific publishers."""

from __future__ import annotations

from typing import Any

JOURNAL_SPECS: dict[str, dict[str, Any]] = {
    'nature': {
        'name': 'Nature',
        'widths': {
            'single': 89,    # mm
            'mid': 120,       # mm (1.5 column)
            'double': 183,    # mm (full width)
        },
        'max_height': 247,    # mm
        'recommended_height': {
            'single': (50, 150),
            'double': (80, 200),
        },
        'font': {
            'family': ['Arial', 'Helvetica'],
            'min_size': 5,
            'recommended_size': 7,
            'label_size': 8,
            'max_size': 10,
        },
        'label_style': 'lowercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'nature_methods': {
        'parent': 'nature',
        'name': 'Nature Methods',
    },

    'nature_communications': {
        'parent': 'nature',
        'name': 'Nature Communications',
    },

    'nature_medicine': {
        'parent': 'nature',
        'name': 'Nature Medicine',
    },

    'nature_genetics': {
        'parent': 'nature',
        'name': 'Nature Genetics',
    },

    'nature_biotechnology': {
        'parent': 'nature',
        'name': 'Nature Biotechnology',
    },

    'nature_cell_biology': {
        'parent': 'nature',
        'name': 'Nature Cell Biology',
    },

    'nature_immunology': {
        'parent': 'nature',
        'name': 'Nature Immunology',
    },

    'nature_neuroscience': {
        'parent': 'nature',
        'name': 'Nature Neuroscience',
    },

    'science': {
        'name': 'Science',
        'widths': {
            'single': 55,
            'mid': 120,
            'double': 175,
        },
        'max_height': 235,
        'recommended_height': {
            'single': (40, 120),
            'double': (70, 180),
        },
        'font': {
            'family': ['Helvetica', 'Arial'],
            'min_size': 6,
            'recommended_size': 8,
            'label_size': 10,
            'max_size': 12,
        },
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'science_advances': {
        'parent': 'science',
        'name': 'Science Advances',
    },

    'science_immunology': {
        'parent': 'science',
        'name': 'Science Immunology',
    },

    'cell': {
        'name': 'Cell',
        'widths': {
            'single': 85,
            'mid': 114,
            'double': 178,
        },
        'max_height': 230,
        'recommended_height': {
            'single': (50, 140),
            'double': (70, 190),
        },
        'font': {
            'family': ['Arial', 'Helvetica'],
            'min_size': 6,
            'recommended_size': 7,
            'label_size': 9,
            'max_size': 11,
        },
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1000,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'cell_reports': {
        'parent': 'cell',
        'name': 'Cell Reports',
    },

    'cell_stem_cell': {
        'parent': 'cell',
        'name': 'Cell Stem Cell',
    },

    'immunity': {
        'parent': 'cell',
        'name': 'Immunity',
    },

    'molecular_cell': {
        'parent': 'cell',
        'name': 'Molecular Cell',
    },

    'pnas': {
        'name': 'PNAS',
        'widths': {
            'single': 87,
            'mid': 114,
            'double': 178,
        },
        'max_height': 230,
        'recommended_height': {
            'single': (50, 140),
            'double': (70, 190),
        },
        'font': {
            'family': ['Arial', 'Helvetica'],
            'min_size': 6,
            'recommended_size': 8,
            'label_size': 10,
            'max_size': 12,
        },
        'label_style': 'uppercase_italic',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': False,
    },

    'lancet': {
        'name': 'The Lancet',
        'widths': {
            'single': 80,
            'double': 170,
        },
        'max_height': 230,
        'recommended_height': {
            'single': (50, 140),
            'double': (70, 190),
        },
        'font': {
            'family': ['Arial'],
            'min_size': 6,
            'recommended_size': 9,
            'label_size': 10,
            'max_size': 12,
        },
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': False,
    },

    'nejm': {
        'name': 'New England Journal of Medicine',
        'widths': {
            'single': 84,
            'double': 175,
        },
        'max_height': 230,
        'recommended_height': {
            'single': (50, 140),
            'double': (70, 190),
        },
        'font': {
            'family': ['Arial', 'Helvetica'],
            'min_size': 6,
            'recommended_size': 8,
            'label_size': 10,
            'max_size': 12,
        },
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': False,
    },

    'jama': {
        'name': 'JAMA',
        'widths': {
            'single': 86,
            'double': 178,
        },
        'max_height': 230,
        'font': {
            'family': ['Arial'],
            'min_size': 6,
            'recommended_size': 8,
            'label_size': 10,
        },
        'label_style': 'uppercase_bold',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
    },

    'elife': {
        'name': 'eLife',
        'widths': {
            'single': 85,
            'mid': 120,
            'double': 178,
        },
        'max_height': 230,
        'font': {
            'family': ['Arial', 'Helvetica'],
            'min_size': 6,
            'recommended_size': 8,
            'label_size': 10,
        },
        'label_style': 'uppercase_bold',
        'formats': ['PDF', 'EPS', 'TIFF', 'PNG'],
        'dpi': {
            'line_art': 900,
            'halftone': 300,
            'combination': 600,
        },
    },
}


def _resolve_spec(journal_key: str) -> dict[str, Any]:
    """Resolve a journal spec, merging with parent if applicable."""
    spec = JOURNAL_SPECS.get(journal_key)
    if spec is None:
        raise ValueError(
            f"Unknown journal '{journal_key}'. "
            f"Available: {', '.join(sorted(JOURNAL_SPECS.keys()))}"
        )

    if 'parent' in spec:
        parent = _resolve_spec(spec['parent'])
        merged = {**parent, **spec}
        merged.pop('parent', None)
        # Deep merge for nested dicts
        for key in ('widths', 'font', 'dpi', 'recommended_height'):
            if key in parent and key in spec:
                merged[key] = {**parent[key], **spec[key]}
            elif key in parent:
                merged[key] = parent[key].copy()
        return merged

    return spec.copy()


def get_journal_spec(journal: str) -> dict[str, Any]:
    """Get the full resolved specification for a journal.

    Parameters
    ----------
    journal : str
        Journal key, e.g. 'nature', 'science', 'cell', 'nature_methods'.

    Returns
    -------
    dict
        Complete specification dictionary with all fields resolved.

    Raises
    ------
    ValueError
        If the journal key is not recognized.
    """
    return _resolve_spec(journal.lower().replace(' ', '_').replace('-', '_'))


def list_journals() -> list[str]:
    """Return sorted list of available journal keys."""
    return sorted(JOURNAL_SPECS.keys())
