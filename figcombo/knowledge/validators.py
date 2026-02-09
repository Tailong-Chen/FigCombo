"""Validation rules for checking figures against journal specifications."""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity.value,
            "rule": self.rule,
            "message": self.message,
        }


@dataclass
class ValidationReport:
    """Complete validation report for a figure."""
    results: list[ValidationResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def add(self, severity: Severity, rule: str, message: str) -> None:
        self.results.append(ValidationResult(severity, rule, message))

    def passed(self, rule: str, message: str) -> None:
        self.add(Severity.PASS, rule, message)

    def warned(self, rule: str, message: str) -> None:
        self.add(Severity.WARN, rule, message)

    def failed(self, rule: str, message: str) -> None:
        self.add(Severity.FAIL, rule, message)

    def add_warning(self, message: str) -> None:
        """Add a non-fatal warning suggestion."""
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        """Add an improvement suggestion."""
        self.suggestions.append(message)

    @property
    def has_failures(self) -> bool:
        return any(r.severity == Severity.FAIL for r in self.results)

    @property
    def has_warnings(self) -> bool:
        return any(r.severity == Severity.WARN for r in self.results)

    @property
    def is_clean(self) -> bool:
        return not self.has_failures and not self.has_warnings

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.PASS)

    @property
    def warn_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.WARN)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.FAIL)

    def __str__(self) -> str:
        lines = []
        for r in self.results:
            lines.append(str(r))
        summary_parts = []
        if self.pass_count:
            summary_parts.append(f"{self.pass_count} passed")
        if self.warn_count:
            summary_parts.append(f"{self.warn_count} warnings")
        if self.fail_count:
            summary_parts.append(f"{self.fail_count} failures")
        lines.append(f"\nSummary: {', '.join(summary_parts)}")

        if self.warnings:
            lines.append("\nAdditional Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        if self.suggestions:
            lines.append("\nSuggestions:")
            for s in self.suggestions:
                lines.append(f"  - {s}")

        return "\n".join(lines)

    def print(self) -> None:
        """Print the validation report with formatted output."""
        # Header
        print("=" * 60)
        print("FIGURE VALIDATION REPORT")
        print("=" * 60)

        # Results by severity
        if self.results:
            print("\n[VALIDATION CHECKS]")
            print("-" * 40)
            for r in self.results:
                icon = ""
                if r.severity == Severity.PASS:
                    icon = "[OK]"
                elif r.severity == Severity.WARN:
                    icon = "[!]"
                elif r.severity == Severity.FAIL:
                    icon = "[X]"
                print(f"{icon} {r.rule}: {r.message}")

        # Summary
        print("\n[SUMMARY]")
        print("-" * 40)
        print(f"  Passed:   {self.pass_count}")
        print(f"  Warnings: {self.warn_count}")
        print(f"  Failures: {self.fail_count}")

        if self.warnings:
            print("\n[WARNINGS]")
            print("-" * 40)
            for w in self.warnings:
                print(f"  - {w}")

        if self.suggestions:
            print("\n[SUGGESTIONS]")
            print("-" * 40)
            for s in self.suggestions:
                print(f"  - {s}")

        # Final status
        print("\n" + "=" * 60)
        if self.has_failures:
            print("STATUS: FAILED - Please address the errors above")
        elif self.has_warnings or self.warnings:
            print("STATUS: PASSED WITH WARNINGS")
        else:
            print("STATUS: PASSED")
        print("=" * 60)

    def to_dict(self) -> dict[str, Any]:
        """Export the validation report as a dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "summary": {
                "passed": self.pass_count,
                "warnings": self.warn_count,
                "failures": self.fail_count,
                "is_clean": self.is_clean,
                "has_failures": self.has_failures,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Export the validation report as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def check_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate the contrast ratio between two colors.

    Uses WCAG 2.0 formula for contrast ratio calculation.
    Ratio of 4.5:1 is recommended for normal text, 3:1 for large text.

    Parameters
    ----------
    color1 : str
        First color in hex format (e.g., '#FFFFFF').
    color2 : str
        Second color in hex format (e.g., '#000000').

    Returns
    -------
    float
        Contrast ratio (1-21).
    """
    def hex_to_luminance(hex_color: str) -> float:
        """Convert hex color to relative luminance."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])

        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        # Apply gamma correction
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = hex_to_luminance(color1)
    l2 = hex_to_luminance(color2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def estimate_file_size(
    width_px: int,
    height_px: int,
    dpi: int,
    format: str,
    color_depth: int = 24,
    compression_ratio: float = 0.3,
) -> dict[str, Any]:
    """Estimate the output file size for a figure.

    Parameters
    ----------
    width_px : int
        Width in pixels.
    height_px : int
        Height in pixels.
    dpi : int
        Resolution in DPI.
    format : str
        Output format ('TIFF', 'PNG', 'PDF', 'EPS').
    color_depth : int, optional
        Color depth in bits (default 24 for RGB).
    compression_ratio : float, optional
        Estimated compression ratio for lossless formats (default 0.3).

    Returns
    -------
    dict
        Dictionary with size estimates in bytes, MB, and human-readable format.
    """
    format = format.upper()
    uncompressed_size = (width_px * height_px * color_depth) / 8

    if format in ('TIFF', 'TIF'):
        # TIFF can be uncompressed or use LZW
        estimated_size = uncompressed_size * compression_ratio
    elif format == 'PNG':
        # PNG uses lossless compression
        estimated_size = uncompressed_size * compression_ratio
    elif format in ('JPEG', 'JPG'):
        # JPEG uses lossy compression
        estimated_size = uncompressed_size * 0.1
    elif format in ('PDF', 'EPS'):
        # Vector formats - size depends on complexity, estimate based on pixel dimensions
        estimated_size = uncompressed_size * 0.15
    else:
        estimated_size = uncompressed_size

    size_bytes = int(estimated_size)
    size_mb = size_bytes / (1024 * 1024)

    # Human readable format
    if size_mb >= 1000:
        human = f"{size_mb / 1024:.2f} GB"
    elif size_mb >= 1:
        human = f"{size_mb:.2f} MB"
    else:
        human = f"{size_bytes / 1024:.2f} KB"

    return {
        "bytes": size_bytes,
        "mb": round(size_mb, 2),
        "human": human,
        "format": format,
        "dpi": dpi,
        "dimensions": f"{width_px}x{height_px}",
    }


def get_recommendations(journal_key: str) -> dict[str, Any]:
    """Get recommendations for a specific journal.

    Parameters
    ----------
    journal_key : str
        Journal identifier (e.g., 'nature', 'science', 'cell').

    Returns
    -------
    dict
        Dictionary with recommendations for the journal.
    """
    from figcombo.knowledge.journal_specs import get_journal_spec

    try:
        spec = get_journal_spec(journal_key)
    except ValueError:
        return {
            "error": f"Unknown journal: {journal_key}",
            "available_journals": [],
        }

    font_spec = spec.get('font', {})
    dpi_spec = spec.get('dpi', {})

    recommendations = {
        "journal_name": spec.get('name', journal_key),
        "figure_widths": spec.get('widths', {}),
        "max_height_mm": spec.get('max_height', 250),
        "recommended_height": spec.get('recommended_height', {}),
        "font": {
            "recommended_family": font_spec.get('family', ['Arial'])[0],
            "recommended_size": font_spec.get('recommended_size', 8),
            "min_size": font_spec.get('min_size', 6),
            "max_size": font_spec.get('max_size', 12),
            "label_size": font_spec.get('label_size', 10),
        },
        "dpi": {
            "line_art": dpi_spec.get('line_art', 1200),
            "halftone": dpi_spec.get('halftone', 300),
            "combination": dpi_spec.get('combination', 600),
        },
        "formats": spec.get('formats', ['PDF', 'EPS', 'TIFF']),
        "colorblind_required": spec.get('colorblind_required', False),
        "label_style": spec.get('label_style', 'lowercase_bold'),
        "label_position": spec.get('label_position', 'top_left'),
    }

    return recommendations


def validate_colorblind_friendly(
    colors: list[str],
    require_patterns: bool = False,
) -> ValidationReport:
    """Validate that a color palette is colorblind-friendly.

    Parameters
    ----------
    colors : list of str
        List of colors in hex format.
    require_patterns : bool, optional
        Whether patterns/textures are required for differentiation.

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()

    if not colors:
        report.failed("colorblind_check", "No colors provided for validation")
        return report

    # Okabe-Ito colorblind-safe palette
    okabe_ito = [
        '#E69F00',  # orange
        '#56B4E9',  # sky blue
        '#009E73',  # bluish green
        '#F0E442',  # yellow
        '#0072B2',  # blue
        '#D55E00',  # vermillion
        '#CC79A7',  # reddish purple
        '#000000',  # black
    ]

    # Problematic color pairs for colorblind users
    problematic_pairs = [
        ('#FF0000', '#00FF00'),  # Red-Green
        ('#FF0000', '#0000FF'),  # Red-Blue (some types)
        ('#00FF00', '#FFFF00'),  # Green-Yellow
        ('#800080', '#008000'),  # Purple-Green
    ]

    # Check if using Okabe-Ito palette
    normalized_colors = [c.upper() for c in colors]
    okabe_matches = sum(1 for c in normalized_colors if c in [o.upper() for o in okabe_ito])

    if okabe_matches == len(colors):
        report.passed(
            "colorblind_palette",
            "Using Okabe-Ito colorblind-safe palette"
        )
    elif okabe_matches >= len(colors) * 0.5:
        report.passed(
            "colorblind_palette",
            f"Using {okabe_matches}/{len(colors)} Okabe-Ito colors"
        )
        report.add_suggestion(
            "Consider using only Okabe-Ito colors for better accessibility"
        )
    else:
        report.warned(
            "colorblind_palette",
            f"Only {okabe_matches}/{len(colors)} colors are from colorblind-safe palette"
        )
        report.add_suggestion(
            "Consider using the Okabe-Ito palette for colorblind-friendly figures"
        )

    # Check for problematic color pairs
    for c1, c2 in problematic_pairs:
        if c1.upper() in normalized_colors and c2.upper() in normalized_colors:
            report.warned(
                "colorblind_red_green",
                f"Potentially problematic color pair detected: {c1}-{c2}"
            )
            report.add_warning(
                "Red-green color combinations can be indistinguishable for deuteranopia/protanopia"
            )

    # Check contrast between colors
    if len(colors) >= 2:
        min_contrast = float('inf')
        min_pair = None
        for i, c1 in enumerate(colors):
            for c2 in colors[i + 1:]:
                contrast = check_contrast_ratio(c1, c2)
                if contrast < min_contrast:
                    min_contrast = contrast
                    min_pair = (c1, c2)

        if min_contrast < 2.0:
            report.warned(
                "colorblind_contrast",
                f"Low contrast between colors: {min_pair[0]} and {min_pair[1]} (ratio: {min_contrast:.2f})"
            )
        else:
            report.passed(
                "colorblind_contrast",
                f"Minimum color contrast ratio: {min_contrast:.2f}"
            )

    # Pattern recommendation
    if require_patterns:
        report.add_suggestion(
            "Using patterns or textures in addition to colors improves accessibility"
        )

    return report


def validate_font_size(
    font_size: float,
    journal_spec: dict[str, Any],
    check_max: bool = True,
) -> ValidationReport:
    """Validate font size against journal requirements.

    Parameters
    ----------
    font_size : float
        Font size in points.
    journal_spec : dict
        Journal specification dictionary.
    check_max : bool, optional
        Whether to check maximum font size.

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()
    journal_name = journal_spec.get('name', 'Unknown')
    font_spec = journal_spec.get('font', {})

    min_size = font_spec.get('min_size', 6)
    recommended_size = font_spec.get('recommended_size', 8)
    max_size = font_spec.get('max_size', 12)
    label_size = font_spec.get('label_size', 10)

    # Check minimum
    if font_size >= min_size:
        report.passed(
            "font_size_minimum",
            f"Font size {font_size}pt meets minimum requirement ({min_size}pt)"
        )
    else:
        report.failed(
            "font_size_minimum",
            f"Font size {font_size}pt is below minimum {min_size}pt for {journal_name}"
        )
        report.add_suggestion(f"Increase font size to at least {min_size}pt")

    # Check recommended
    if font_size == recommended_size:
        report.passed(
            "font_size_recommended",
            f"Using recommended font size ({recommended_size}pt)"
        )
    elif abs(font_size - recommended_size) <= 1:
        report.passed(
            "font_size_recommended",
            f"Font size {font_size}pt is close to recommended ({recommended_size}pt)"
        )
    else:
        report.warned(
            "font_size_recommended",
            f"Font size {font_size}pt differs from recommended {recommended_size}pt"
        )
        report.add_suggestion(f"Consider using {recommended_size}pt for optimal readability")

    # Check maximum
    if check_max and font_size > max_size:
        report.warned(
            "font_size_maximum",
            f"Font size {font_size}pt exceeds maximum {max_size}pt"
        )
        report.add_suggestion(f"Consider reducing font size to {max_size}pt or less")
    elif check_max:
        report.passed(
            "font_size_maximum",
            f"Font size {font_size}pt is within acceptable range"
        )

    # Label size guidance
    if font_size < label_size:
        report.add_suggestion(
            f"Panel labels should be larger than body text (suggested: {label_size}pt)"
        )

    return report


def validate_dpi(
    dpi: int,
    image_type: str,
    journal_spec: dict[str, Any],
) -> ValidationReport:
    """Validate DPI setting against journal requirements.

    Parameters
    ----------
    dpi : int
        Resolution in dots per inch.
    image_type : str
        Type of image ('line_art', 'halftone', 'combination').
    journal_spec : dict
        Journal specification dictionary.

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()
    journal_name = journal_spec.get('name', 'Unknown')
    dpi_spec = journal_spec.get('dpi', {})

    required_dpi = dpi_spec.get(image_type, 300)

    if dpi >= required_dpi:
        report.passed(
            "dpi_check",
            f"DPI {dpi} meets {journal_name} requirement for {image_type} ({required_dpi} DPI)"
        )
    else:
        report.failed(
            "dpi_check",
            f"DPI {dpi} is below {journal_name} requirement for {image_type} ({required_dpi} DPI)"
        )
        report.add_suggestion(f"Increase DPI to at least {required_dpi}")

    # Check if DPI is unnecessarily high
    if dpi > required_dpi * 2:
        report.warned(
            "dpi_excessive",
            f"DPI {dpi} is significantly higher than required ({required_dpi})"
        )
        report.add_suggestion(
            f"High DPI increases file size without visible quality improvement"
        )

    # Provide guidance on image types
    report.add_suggestion(
        f"{image_type} images require {required_dpi} DPI minimum"
    )

    return report


def validate_file_size(
    file_path: str | Path | None = None,
    width_mm: float | None = None,
    height_mm: float | None = None,
    dpi: int | None = None,
    format: str | None = None,
    max_size_mb: float = 50.0,
) -> ValidationReport:
    """Validate output file size.

    Parameters
    ----------
    file_path : str or Path, optional
        Path to existing file to check.
    width_mm : float, optional
        Figure width in mm (for estimation).
    height_mm : float, optional
        Figure height in mm (for estimation).
    dpi : int, optional
        Resolution in DPI (for estimation).
    format : str, optional
        Output format (for estimation).
    max_size_mb : float, optional
        Maximum acceptable file size in MB.

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()

    if file_path is not None:
        # Check existing file
        path = Path(file_path)
        if not path.exists():
            report.failed("file_size", f"File not found: {file_path}")
            return report

        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        format = path.suffix.upper().lstrip('.')

        if size_mb <= max_size_mb:
            report.passed(
                "file_size",
                f"File size {size_mb:.2f} MB is within limit ({max_size_mb} MB)"
            )
        else:
            report.failed(
                "file_size",
                f"File size {size_mb:.2f} MB exceeds limit ({max_size_mb} MB)"
            )

        # TIFF-specific warnings
        if format in ('TIFF', 'TIF') and size_mb > 10:
            report.warned(
                "file_size_tiff",
                f"Large TIFF file ({size_mb:.2f} MB) may cause submission issues"
            )
            report.add_suggestion("Consider using LZW compression for TIFF files")

    elif width_mm is not None and height_mm is not None and dpi is not None and format is not None:
        # Estimate file size
        width_px = int(width_mm * dpi / 25.4)
        height_px = int(height_mm * dpi / 25.4)

        estimate = estimate_file_size(width_px, height_px, dpi, format)
        size_mb = estimate["mb"]

        if size_mb <= max_size_mb:
            report.passed(
                "file_size_estimate",
                f"Estimated file size: {estimate['human']} (within {max_size_mb} MB limit)"
            )
        else:
            report.failed(
                "file_size_estimate",
                f"Estimated file size {estimate['human']} exceeds {max_size_mb} MB limit"
            )
            report.add_suggestion("Consider reducing DPI or using a compressed format like PNG")

        report.add_suggestion(
            f"Estimated dimensions: {estimate['dimensions']} at {dpi} DPI"
        )
    else:
        report.failed(
            "file_size",
            "Insufficient information to check file size"
        )
        report.add_suggestion("Provide either file_path or dimensions + dpi + format")

    return report


def validate_panel_spacing(
    horizontal_gap_mm: float,
    vertical_gap_mm: float,
    min_gap_mm: float = 2.0,
    max_gap_mm: float = 10.0,
) -> ValidationReport:
    """Validate panel spacing.

    Parameters
    ----------
    horizontal_gap_mm : float
        Horizontal gap between panels in mm.
    vertical_gap_mm : float
        Vertical gap between panels in mm.
    min_gap_mm : float, optional
        Minimum acceptable gap in mm.
    max_gap_mm : float, optional
        Maximum acceptable gap in mm.

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()

    # Check horizontal gap
    if horizontal_gap_mm < min_gap_mm:
        report.failed(
            "panel_spacing_horizontal",
            f"Horizontal gap ({horizontal_gap_mm}mm) is below minimum ({min_gap_mm}mm)"
        )
        report.add_suggestion("Increase horizontal gap to prevent panels from touching")
    elif horizontal_gap_mm > max_gap_mm:
        report.warned(
            "panel_spacing_horizontal",
            f"Horizontal gap ({horizontal_gap_mm}mm) is larger than typical ({max_gap_mm}mm)"
        )
    else:
        report.passed(
            "panel_spacing_horizontal",
            f"Horizontal gap ({horizontal_gap_mm}mm) is appropriate"
        )

    # Check vertical gap
    if vertical_gap_mm < min_gap_mm:
        report.failed(
            "panel_spacing_vertical",
            f"Vertical gap ({vertical_gap_mm}mm) is below minimum ({min_gap_mm}mm)"
        )
        report.add_suggestion("Increase vertical gap to prevent panels from touching")
    elif vertical_gap_mm > max_gap_mm:
        report.warned(
            "panel_spacing_vertical",
            f"Vertical gap ({vertical_gap_mm}mm) is larger than typical ({max_gap_mm}mm)"
        )
    else:
        report.passed(
            "panel_spacing_vertical",
            f"Vertical gap ({vertical_gap_mm}mm) is appropriate"
        )

    # Check if gaps are balanced
    ratio = max(horizontal_gap_mm, vertical_gap_mm) / max(min(horizontal_gap_mm, vertical_gap_mm), 0.1)
    if ratio > 2:
        report.warned(
            "panel_spacing_balance",
            f"Uneven spacing: H={horizontal_gap_mm}mm, V={vertical_gap_mm}mm"
        )
        report.add_suggestion("Consider using similar horizontal and vertical gaps for consistency")
    else:
        report.passed(
            "panel_spacing_balance",
            "Horizontal and vertical gaps are balanced"
        )

    return report


def validate_label_placement(
    labels: list[dict[str, Any]],
    figure_width_mm: float,
    figure_height_mm: float,
    label_style: str = "lowercase_bold",
) -> ValidationReport:
    """Validate panel label placement.

    Parameters
    ----------
    labels : list of dict
        List of label info dicts with keys: 'text', 'x', 'y', 'panel_width', 'panel_height'.
    figure_width_mm : float
        Total figure width in mm.
    figure_height_mm : float
        Total figure height in mm.
    label_style : str, optional
        Label style (e.g., 'lowercase_bold', 'uppercase_bold').

    Returns
    -------
    ValidationReport
        Report with validation results.
    """
    report = ValidationReport()

    if not labels:
        report.failed("label_placement", "No labels provided")
        return report

    expected_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                       'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']

    for i, label_info in enumerate(labels):
        text = label_info.get('text', '')
        x = label_info.get('x', 0)
        y = label_info.get('y', 0)
        panel_w = label_info.get('panel_width', figure_width_mm)
        panel_h = label_info.get('panel_height', figure_height_mm)

        # Check label format
        if 'uppercase' in label_style and text.islower():
            report.warned(
                "label_format",
                f"Label '{text}' should be uppercase for this journal"
            )
        elif 'lowercase' in label_style and text.isupper():
            report.warned(
                "label_format",
                f"Label '{text}' should be lowercase for this journal"
            )
        else:
            report.passed("label_format", f"Label '{text}' format is correct")

        # Check label sequence
        expected = expected_labels[i] if i < len(expected_labels) else '?'
        if text.lower() != expected:
            report.warned(
                "label_sequence",
                f"Label '{text}' at position {i + 1} - expected '{expected}'"
            )

        # Check label position (should be near top-left of panel)
        if x < 0 or x > panel_w * 0.5:
            report.warned(
                "label_position_x",
                f"Label '{text}' x-position ({x:.1f}mm) may be too far from panel edge"
            )
        if y < panel_h * 0.5 or y > panel_h:
            report.warned(
                "label_position_y",
                f"Label '{text}' y-position ({y:.1f}mm) may be too low"
            )

    report.passed("label_placement", f"Validated {len(labels)} panel labels")

    return report


def validate_figure(
    figure_width_mm: float,
    figure_height_mm: float,
    journal_spec: dict[str, Any],
    panels: list[dict[str, Any]] | None = None,
    font_family: str | None = None,
    font_size: float | None = None,
    colors: list[str] | None = None,
    output_format: str | None = None,
    dpi: int | None = None,
    horizontal_gap_mm: float | None = None,
    vertical_gap_mm: float | None = None,
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
    colors : list of str, optional
        Color palette used in the figure.
    output_format : str, optional
        Output file format.
    dpi : int, optional
        Resolution in DPI.
    horizontal_gap_mm : float, optional
        Horizontal gap between panels in mm.
    vertical_gap_mm : float, optional
        Vertical gap between panels in mm.

    Returns
    -------
    ValidationReport
        Complete validation report.
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
        # Suggest closest match
        if valid_widths:
            closest = min(valid_widths, key=lambda w: abs(w - figure_width_mm))
            report.add_suggestion(f"Consider using width {closest}mm ({width_names.get(closest, '?')})")

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
        report.add_suggestion(f"Reduce height to {max_height}mm or less")

    # --- Recommended height range check ---
    recommended_height = journal_spec.get('recommended_height', {})
    if recommended_height and width_match:
        col_type = width_names.get(width_match, 'single')
        if col_type in recommended_height:
            min_h, max_h = recommended_height[col_type]
            if min_h <= figure_height_mm <= max_h:
                report.passed(
                    'figure_height_recommended',
                    f"Figure height {figure_height_mm:.0f}mm is within recommended range "
                    f"({min_h}-{max_h}mm for {col_type} column)"
                )
            elif figure_height_mm < min_h:
                report.warned(
                    'figure_height_recommended',
                    f"Figure height {figure_height_mm:.0f}mm is below recommended minimum "
                    f"({min_h}mm for {col_type} column)"
                )
            else:
                report.warned(
                    'figure_height_recommended',
                    f"Figure height {figure_height_mm:.0f}mm exceeds recommended maximum "
                    f"({max_h}mm for {col_type} column)"
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
                report.add_suggestion(f"Consider using {allowed_fonts[0]} for {journal_name}")

    # --- Font size check with enhanced validation ---
    if font_size is not None:
        font_spec = journal_spec.get('font', {})
        min_size = font_spec.get('min_size', 6)
        recommended_size = font_spec.get('recommended_size', 8)
        max_size = font_spec.get('max_size', 12)

        # Check minimum
        if font_size >= min_size:
            report.passed(
                'font_size_minimum',
                f"Font size {font_size}pt >= minimum {min_size}pt"
            )
        else:
            report.failed(
                'font_size_minimum',
                f"Font size {font_size}pt is below minimum {min_size}pt "
                f"for {journal_name}"
            )
            report.add_suggestion(f"Increase font size to at least {min_size}pt")

        # Check recommended
        if abs(font_size - recommended_size) <= 1:
            report.passed(
                'font_size_recommended',
                f"Font size {font_size}pt is close to recommended {recommended_size}pt"
            )
        else:
            report.warned(
                'font_size_recommended',
                f"Font size {font_size}pt differs from recommended {recommended_size}pt"
            )

        # Check maximum
        if font_size > max_size:
            report.warned(
                'font_size_maximum',
                f"Font size {font_size}pt exceeds maximum {max_size}pt"
            )

    # --- Color configuration check ---
    if colors is not None:
        color_report = validate_colorblind_friendly(colors)
        report.results.extend(color_report.results)
        report.warnings.extend(color_report.warnings)
        report.suggestions.extend(color_report.suggestions)

        # Check if journal requires colorblind-friendly figures
        if journal_spec.get('colorblind_required', False):
            if color_report.has_warnings or color_report.warnings:
                report.warned(
                    'colorblind_required',
                    f"{journal_name} recommends colorblind-friendly figures"
                )
            else:
                report.passed(
                    'colorblind_required',
                    f"Color palette meets {journal_name} accessibility requirements"
                )

    # --- Output format check ---
    if output_format is not None:
        supported_formats = journal_spec.get('formats', ['PDF', 'EPS', 'TIFF'])
        fmt_upper = output_format.upper()
        if fmt_upper in [f.upper() for f in supported_formats]:
            report.passed(
                'output_format',
                f"Format '{output_format}' is supported by {journal_name}"
            )
        else:
            report.failed(
                'output_format',
                f"Format '{output_format}' is not in {journal_name} supported formats: "
                f"{supported_formats}"
            )
            report.add_suggestion(f"Use one of: {', '.join(supported_formats)}")

    # --- DPI check ---
    if dpi is not None:
        dpi_spec = journal_spec.get('dpi', {})
        min_dpi = min(dpi_spec.values()) if dpi_spec else 300
        if dpi >= min_dpi:
            report.passed(
                'dpi_minimum',
                f"DPI {dpi} meets minimum requirement ({min_dpi})"
            )
        else:
            report.failed(
                'dpi_minimum',
                f"DPI {dpi} is below minimum {min_dpi}"
            )

    # --- Panel spacing check ---
    if horizontal_gap_mm is not None and vertical_gap_mm is not None:
        spacing_report = validate_panel_spacing(horizontal_gap_mm, vertical_gap_mm)
        report.results.extend(spacing_report.results)
        report.warnings.extend(spacing_report.warnings)
        report.suggestions.extend(spacing_report.suggestions)

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
