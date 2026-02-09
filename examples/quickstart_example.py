"""FigCombo Quickstart Example

This example demonstrates the basic usage of FigCombo for creating
publication-ready multi-panel figures.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from figcombo import Figure, ImagePanel, PlotPanel
from figcombo.plot_types import bar_plot, scatter_plot


def create_sample_data():
    """Create sample data for demonstration."""
    np.random.seed(42)

    # Bar chart data
    bar_data = pd.DataFrame({
        'group': ['Control', 'Treatment A', 'Treatment B', 'Treatment C'],
        'value': [100, 145, 132, 178],
        'error': [10, 15, 12, 18]
    })

    # Scatter plot data
    scatter_data = pd.DataFrame({
        'x': np.random.normal(50, 15, 50),
        'y': np.random.normal(50, 15, 50),
        'group': np.random.choice(['A', 'B'], 50)
    })

    return bar_data, scatter_data


def example_1_basic_layout():
    """Example 1: Basic 2x2 grid layout."""
    print("=" * 60)
    print("Example 1: Basic 2x2 Grid Layout")
    print("=" * 60)

    bar_data, scatter_data = create_sample_data()

    # Create figure with 2x2 grid layout
    fig = Figure(
        journal='nature',
        size='double',
        layout="""
        ab
        cd
        """
    )

    # Panel a: Bar plot using built-in plot type
    def plot_with_title(ax, data):
        bar_plot(ax, data, x='group', y='value', error='error')
        ax.set_title('Treatment Effects')

    fig['a'] = PlotPanel(plot_with_title, data=bar_data)

    # Panel b: Scatter plot
    def scatter_with_title(ax, data):
        scatter_plot(ax, data, x='x', y='y', hue='group')
        ax.set_title('Correlation Analysis')

    fig['b'] = PlotPanel(scatter_with_title, data=scatter_data)

    # Panel c: Custom function plot
    def plot_histogram(ax, data=None):
        ax.hist(np.random.normal(0, 1, 1000), bins=30, edgecolor='black')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution')

    fig['c'] = PlotPanel(plot_histogram)

    # Panel d: Another custom plot
    def plot_box(ax, data=None):
        bp = ax.boxplot([np.random.normal(0, 1, 100) for _ in range(4)],
                        labels=['A', 'B', 'C', 'D'])
        ax.set_ylabel('Measurement')
        ax.set_title('Box Plot Comparison')

    fig['d'] = PlotPanel(plot_box)

    # Validate and show info
    print(fig.info())
    print()

    # Validate
    report = fig.validate()
    report.print()

    # Save
    output = fig.save('/home/ctl/code/Figure_combination/output/example1_basic.pdf')
    print(f"\nSaved to: {output}")

    return fig


def example_2_nature_template():
    """Example 2: Using Nature-optimized template."""
    print("\n" + "=" * 60)
    print("Example 2: Nature-Optimized Template")
    print("=" * 60)

    bar_data, scatter_data = create_sample_data()

    # Create figure using Nature template
    from figcombo import list_templates
    print("\nAvailable Nature templates:")
    print(list_templates(category='specialized'))

    # Use the L-shape template
    fig = Figure(
        journal='nature',
        size='double',
        template='nature_l_shape'
    )

    # Panel a: Large main panel
    def main_experiment(ax, data=None):
        x = np.linspace(0, 10, 100)
        for i in range(4):
            y = np.sin(x + i * 0.5) * (1 + i * 0.2)
            ax.plot(x, y, label=f'Condition {chr(65+i)}')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Response')
        ax.legend(loc='upper right', frameon=False)
        ax.set_title('Time Course Analysis')

    fig['a'] = PlotPanel(main_experiment)

    # Panels b, c, d: Supporting data
    fig['b'] = PlotPanel('bar_plot', data=bar_data, x='group', y='value')
    fig['c'] = PlotPanel('scatter_plot', data=scatter_data, x='x', y='y')

    def summary_stats(ax, data=None):
        categories = ['Mean', 'Median', 'SD', 'SEM']
        values = [50, 48, 12, 3]
        colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442']
        ax.bar(categories, values, color=colors, edgecolor='black')
        ax.set_ylabel('Value')
        ax.set_title('Summary Statistics')

    fig['d'] = PlotPanel(summary_stats)

    # Save
    output = fig.save('/home/ctl/code/Figure_combination/output/example2_nature_template.pdf')
    print(f"\nSaved to: {output}")

    return fig


def example_3_different_journals():
    """Example 3: Same figure for different journals."""
    print("\n" + "=" * 60)
    print("Example 3: Same Layout for Different Journals")
    print("=" * 60)

    bar_data, _ = create_sample_data()

    journals = ['nature', 'science', 'cell', 'pnas']

    for journal in journals:
        print(f"\nCreating figure for {journal.upper()}...")

        fig = Figure(
            journal=journal,
            size='double',
            layout="""
            ab
            cd
            """
        )

        fig['a'] = PlotPanel('bar_plot', data=bar_data, x='group', y='value')
        fig['b'] = PlotPanel('bar_plot', data=bar_data, x='group', y='value')
        fig['c'] = PlotPanel('bar_plot', data=bar_data, x='group', y='value')
        fig['d'] = PlotPanel('bar_plot', data=bar_data, x='group', y='value')

        # Validate
        report = fig.validate()
        if report.pass_count > 0:
            print(f"  ✓ {report.pass_count} checks passed")
        if report.warn_count > 0:
            print(f"  ⚠ {report.warn_count} warnings")

        # Save
        output = fig.save(f'/home/ctl/code/Figure_combination/output/example3_{journal}.pdf')
        print(f"  Saved: {output[0].name}")


def example_4_validation():
    """Example 4: Validation features."""
    print("\n" + "=" * 60)
    print("Example 4: Validation Features")
    print("=" * 60)

    from figcombo.knowledge.validators import (
        validate_colorblind_friendly,
        validate_font_size,
        get_recommendations
    )

    # Get recommendations for Nature
    print("\nNature Journal Recommendations:")
    rec = get_recommendations('nature')
    print(f"  Font family: {rec['font']['recommended_family']}")
    print(f"  Min font size: {rec['font']['min_size']}pt")
    print(f"  Recommended font size: {rec['font']['recommended_size']}pt")
    print(f"  Line art DPI: {rec['dpi']['line_art']}")
    print(f"  Halftone DPI: {rec['dpi']['halftone']}")

    # Check color palette
    print("\nColor Palette Validation:")
    colors = ['#E69F00', '#56B4E9', '#009E73']  # Okabe-Ito palette
    report = validate_colorblind_friendly(colors)
    print(f"  Colors: {colors}")
    print(f"  Pass count: {report.pass_count}")
    print(f"  Warn count: {report.warn_count}")

    # Check font size
    print("\nFont Size Validation:")
    from figcombo.knowledge.journal_specs import get_journal_spec
    nature_spec = get_journal_spec('nature')
    report = validate_font_size(6, nature_spec)
    print(f"  Font size: 6pt")
    print(f"  Result: {report.pass_count} passed, {report.warn_count} warnings")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("FigCombo Quickstart Examples")
    print("=" * 60)

    # Run examples
    example_1_basic_layout()
    example_2_nature_template()
    example_3_different_journals()
    example_4_validation()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("Check the output/ directory for generated figures.")
    print("=" * 60)
