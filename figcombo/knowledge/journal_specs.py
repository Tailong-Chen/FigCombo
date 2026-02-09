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

    # Nature Reviews series
    'nature_reviews_molecular_cell_biology': {
        'parent': 'nature',
        'name': 'Nature Reviews Molecular Cell Biology',
    },

    'nature_reviews_genetics': {
        'parent': 'nature',
        'name': 'Nature Reviews Genetics',
    },

    'nature_reviews_immunology': {
        'parent': 'nature',
        'name': 'Nature Reviews Immunology',
    },

    'nature_reviews_cancer': {
        'parent': 'nature',
        'name': 'Nature Reviews Cancer',
    },

    'nature_reviews_drug_discovery': {
        'parent': 'nature',
        'name': 'Nature Reviews Drug Discovery',
    },

    'nature_reviews_clinical_oncology': {
        'parent': 'nature',
        'name': 'Nature Reviews Clinical Oncology',
    },

    'nature_reviews_endocrinology': {
        'parent': 'nature',
        'name': 'Nature Reviews Endocrinology',
    },

    'nature_reviews_gastroenterology_hepatology': {
        'parent': 'nature',
        'name': 'Nature Reviews Gastroenterology & Hepatology',
    },

    'nature_reviews_neuroscience': {
        'parent': 'nature',
        'name': 'Nature Reviews Neuroscience',
    },

    'nature_reviews_microbiology': {
        'parent': 'nature',
        'name': 'Nature Reviews Microbiology',
    },

    'nature_reviews_cardiology': {
        'parent': 'nature',
        'name': 'Nature Reviews Cardiology',
    },

    'nature_reviews_rheumatology': {
        'parent': 'nature',
        'name': 'Nature Reviews Rheumatology',
    },

    'nature_reviews_nephrology': {
        'parent': 'nature',
        'name': 'Nature Reviews Nephrology',
    },

    'nature_reviews_urology': {
        'parent': 'nature',
        'name': 'Nature Reviews Urology',
    },

    # Other Nature journals
    'nature_protocols': {
        'parent': 'nature',
        'name': 'Nature Protocols',
    },

    'nature_structural_molecular_biology': {
        'parent': 'nature',
        'name': 'Nature Structural & Molecular Biology',
    },

    'nature_chemical_biology': {
        'parent': 'nature',
        'name': 'Nature Chemical Biology',
    },

    'nature_metabolism': {
        'parent': 'nature',
        'name': 'Nature Metabolism',
    },

    'nature_microbiology': {
        'parent': 'nature',
        'name': 'Nature Microbiology',
    },

    'nature_plants': {
        'parent': 'nature',
        'name': 'Nature Plants',
    },

    'nature_cancer': {
        'parent': 'nature',
        'name': 'Nature Cancer',
    },

    'nature_aging': {
        'parent': 'nature',
        'name': 'Nature Aging',
    },

    'nature_biomedical_engineering': {
        'parent': 'nature',
        'name': 'Nature Biomedical Engineering',
    },

    'nature_human_behaviour': {
        'parent': 'nature',
        'name': 'Nature Human Behaviour',
    },

    'nature_sustainability': {
        'parent': 'nature',
        'name': 'Nature Sustainability',
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

    # Additional Cell Press journals
    'cancer_cell': {
        'parent': 'cell',
        'name': 'Cancer Cell',
    },

    'neuron': {
        'parent': 'cell',
        'name': 'Neuron',
    },

    'developmental_cell': {
        'parent': 'cell',
        'name': 'Developmental Cell',
    },

    'cell_metabolism': {
        'parent': 'cell',
        'name': 'Cell Metabolism',
    },

    'cell_host_microbe': {
        'parent': 'cell',
        'name': 'Cell Host & Microbe',
    },

    'cell_systems': {
        'parent': 'cell',
        'name': 'Cell Systems',
    },

    'cell_genomics': {
        'parent': 'cell',
        'name': 'Cell Genomics',
    },

    'cell_chemical_biology': {
        'parent': 'cell',
        'name': 'Cell Chemical Biology',
    },

    'molecular_therapy': {
        'parent': 'cell',
        'name': 'Molecular Therapy',
    },

    'joule': {
        'parent': 'cell',
        'name': 'Joule',
    },

    'matter': {
        'parent': 'cell',
        'name': 'Matter',
    },

    'chem': {
        'parent': 'cell',
        'name': 'Chem',
    },

    'one_earth': {
        'parent': 'cell',
        'name': 'One Earth',
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

    # EMBO Press journals
    'embo_journal': {
        'name': 'The EMBO Journal',
        'widths': {
            'single': 85,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'embo_reports': {
        'parent': 'embo_journal',
        'name': 'EMBO Reports',
    },

    'embo_molecular_medicine': {
        'parent': 'embo_journal',
        'name': 'EMBO Molecular Medicine',
    },

    'embo_journal_open_access': {
        'parent': 'embo_journal',
        'name': 'EMBO Journal Open Access',
    },

    # Cold Spring Harbor Laboratory Press
    'genes_development': {
        'name': 'Genes & Development',
        'widths': {
            'single': 86,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'genome_research': {
        'parent': 'genes_development',
        'name': 'Genome Research',
    },

    'rna': {
        'parent': 'genes_development',
        'name': 'RNA',
    },

    # Rockefeller University Press
    'journal_cell_biology': {
        'name': 'Journal of Cell Biology',
        'widths': {
            'single': 85,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'journal_experimental_medicine': {
        'name': 'Journal of Experimental Medicine',
        'widths': {
            'single': 85,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'journal_general_physiology': {
        'name': 'Journal of General Physiology',
        'widths': {
            'single': 85,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF'],
        'dpi': {
            'line_art': 1200,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    # American Society of Hematology
    'blood': {
        'name': 'Blood',
        'widths': {
            'single': 88,
            'mid': 120,
            'double': 180,
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
        'colorblind_required': True,
    },

    'blood_advances': {
        'parent': 'blood',
        'name': 'Blood Advances',
    },

    # PLoS journals
    'plos_biology': {
        'name': 'PLOS Biology',
        'widths': {
            'single': 83,
            'mid': 120,
            'double': 174,
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
        'formats': ['PDF', 'EPS', 'TIFF', 'PNG'],
        'dpi': {
            'line_art': 1000,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'plos_genetics': {
        'parent': 'plos_biology',
        'name': 'PLOS Genetics',
    },

    'plos_pathogens': {
        'parent': 'plos_biology',
        'name': 'PLOS Pathogens',
    },

    'plos_computational_biology': {
        'parent': 'plos_biology',
        'name': 'PLOS Computational Biology',
    },

    'plos_medicine': {
        'parent': 'plos_biology',
        'name': 'PLOS Medicine',
    },

    # BMC/BioMed Central journals
    'bmc_biology': {
        'name': 'BMC Biology',
        'widths': {
            'single': 85,
            'mid': 120,
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
        'label_style': 'uppercase_bold',
        'label_position': 'top_left',
        'formats': ['PDF', 'EPS', 'TIFF', 'PNG'],
        'dpi': {
            'line_art': 1000,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'bmc_cell_biology': {
        'parent': 'bmc_biology',
        'name': 'BMC Cell Biology',
    },

    'bmc_developmental_biology': {
        'parent': 'bmc_biology',
        'name': 'BMC Developmental Biology',
    },

    'bmc_genomics': {
        'parent': 'bmc_biology',
        'name': 'BMC Genomics',
    },

    'genome_biology': {
        'parent': 'bmc_biology',
        'name': 'Genome Biology',
    },

    # Royal Society journals
    'open_biology': {
        'name': 'Open Biology',
        'widths': {
            'single': 84,
            'mid': 120,
            'double': 176,
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
        'formats': ['PDF', 'EPS', 'TIFF', 'PNG'],
        'dpi': {
            'line_art': 1000,
            'halftone': 300,
            'combination': 600,
        },
        'colorblind_required': True,
    },

    'philosophical_transactions_b': {
        'parent': 'open_biology',
        'name': 'Philosophical Transactions of the Royal Society B',
    },

    'proceedings_b': {
        'parent': 'open_biology',
        'name': 'Proceedings of the Royal Society B',
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
