"""Pre-defined knowledge base for journal specifications, panel constraints, and layout templates."""

from figcombo.knowledge.journal_specs import JOURNAL_SPECS, get_journal_spec
from figcombo.knowledge.panel_constraints import (
    ASPECT_RATIOS,
    PANEL_MIN_SIZE,
    PANEL_RECOMMENDED_SIZE,
    SPACING,
)
from figcombo.knowledge.layout_templates import LAYOUT_TEMPLATES, list_templates
from figcombo.knowledge.validators import validate_figure

__all__ = [
    'JOURNAL_SPECS',
    'get_journal_spec',
    'ASPECT_RATIOS',
    'PANEL_MIN_SIZE',
    'PANEL_RECOMMENDED_SIZE',
    'SPACING',
    'LAYOUT_TEMPLATES',
    'list_templates',
    'validate_figure',
]
