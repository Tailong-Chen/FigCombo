"""Validation rules for checking figures against journal specifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # for future Figure type hint


class Severity(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    severity: Severity
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.message}"


@dataclass
class ValidationReport:
    """Complete validation report for a figure."""
    results: list[ValidationResult] = field(default_factory=list)

    def add(self, severity: Severity, rule: str, message: str) -> None:
        self.results.append(ValidationResult(severity, rule, message))

    def passed(self, rule: str, message: str) -> None:
        self.add(Severity.PASS, rule, message)

    def warned(self, rule: str, message: str) -> None:
        self.add(Severity.WARN, rule, message)

    def failed(self, rule: str, message: str) -> None:
        self.add(Severity.FAIL, rule, message)

    @property
    def has_failures(self) -> bool:
        return any(r.severity == Severity.FAIL for r in self.results)

    @property
    def has_warnings(self) -> bool:
        return any(r.severity == Severity.WARN for r in self.results)

    @property
    def is_clean(self) -> bool:
        return not self.has_failures and not self.has_warnings

    def __str__(self) -> str:
        lines = []
        for r in self.results:
            lines.append(str(r))
        summary_parts = []
        passes = sum(1 for r in self.results if r.severity == Severity.PASS)
        warns = sum(1 for r in self.results if r.severity == Severity.WARN)
        fails = sum(1 for r in self.results if r.severity == Severity.FAIL)
        if passes:
            summary_parts.append(f"{passes} passed")
        if warns:
            summary_parts.append(f"{warns} warnings")
        if fails:
            summary_parts.append(f"{fails} failures")
        lines.append(f"\nSummary: {', '.join(summary_parts)}")
        return "\n".join(lines)

    def print(self) -> None:
        """Print the validation report."""
        print(str(self))


def validate_figure(
    figure_width_mm: float,
    figure_height_mm: float,
    journal_spec: dict[str, Any],
    panels: list[dict[str, Any]] | None = None,
    font_family: str | None = None,
    font_size: float | None = None,
) -> ValidationReport:
    """Validate figure parameters against journal specifications.

    Parameters
    ----------
    figure_width_mm : float
        Total figure width in mm.
    figure_height_mm : float
        Total figure height in mm.
    journal_spec : dict
        Resolved journal specification from get_journal_spec().
    panels : list of dict, optional
        Panel info dicts with keys: 'label', 'width_mm', 'height_mm', 'type'.
    font_family : str, optional
        Font family being used.
    font_size : float, optional
        Base font size in pt.

    Returns
    -------
    ValidationReport
    """
    report = ValidationReport()
    journal_name = journal_spec.get('name', 'Unknown')

    # --- Figure width check ---
    widths = journal_spec.get('widths', {})
    valid_widths = sorted(widths.values())
    width_names = {v: k for k, v in widths.items()}
    tolerance = 1.0  # mm tolerance

    width_match = None
    for w in valid_widths:
        if abs(figure_width_mm - w) <= tolerance:
            width_match = w
            break

    if width_match is not None:
        col_name = width_names.get(width_match, '?')
        report.passed(
            'figure_width',
            f"Figure width {figure_width_mm:.0f}mm matches "
            f"{journal_name} {col_name} column ({width_match}mm)"
        )
    else:
        report.failed(
            'figure_width',
            f"Figure width {figure_width_mm:.0f}mm does not match any "
            f"{journal_name} column width: {widths}"
        )

    # --- Figure height check ---
    max_height = journal_spec.get('max_height', 250)
    if figure_height_mm <= max_height:
        report.passed(
            'figure_height',
            f"Figure height {figure_height_mm:.0f}mm <= max {max_height}mm"
        )
    else:
        report.failed(
            'figure_height',
            f"Figure height {figure_height_mm:.0f}mm exceeds "
            f"max {max_height}mm for {journal_name}"
        )

    # --- Font family check ---
    if font_family is not None:
        allowed_fonts = journal_spec.get('font', {}).get('family', [])
        if allowed_fonts:
            if font_family in allowed_fonts:
                report.passed(
                    'font_family',
                    f"Font '{font_family}' is in {journal_name} allowed list"
                )
            else:
                report.warned(
                    'font_family',
                    f"Font '{font_family}' not in {journal_name} "
                    f"recommended list: {allowed_fonts}"
                )

    # --- Font size check ---
    if font_size is not None:
        font_spec = journal_spec.get('font', {})
        min_size = font_spec.get('min_size', 5)
        if font_size >= min_size:
            report.passed(
                'font_size',
                f"Font size {font_size}pt >= minimum {min_size}pt"
            )
        else:
            report.failed(
                'font_size',
                f"Font size {font_size}pt is below minimum {min_size}pt "
                f"for {journal_name}"
            )

    # --- Panel size checks ---
    if panels:
        from figcombo.knowledge.panel_constraints import check_panel_size

        for panel_info in panels:
            label = panel_info.get('label', '?')
            pw = panel_info.get('width_mm', 0)
            ph = panel_info.get('height_mm', 0)
            ptype = panel_info.get('type', 'plot')

            warnings = check_panel_size(pw, ph, ptype)
            if warnings:
                for w in warnings:
                    report.warned('panel_size', f"Panel '{label}': {w}")
            else:
                report.passed(
                    'panel_size',
                    f"Panel '{label}' size {pw:.0f}x{ph:.0f}mm OK"
                )

    return report
