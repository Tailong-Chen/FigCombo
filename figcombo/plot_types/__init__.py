"""Built-in plot types for scientific figure composition.

This module provides ready-to-use plot functions for common scientific
visualizations. All functions are registered with the @register_plot_type
decorator and can be used with PlotPanel.

Quick Start
-----------
>>> from figcombo import Figure, PlotPanel
>>> from figcombo.plot_types import bar_plot, volcano_plot
>>>
>>> fig = Figure(journal='nature', layout='ab')
>>> fig['a'] = PlotPanel('bar_plot', data=df, x='group', y='value')
>>> fig['b'] = PlotPanel('volcano_plot', data=de_results)

Categories
----------
- statistics: bar_plot, box_plot, violin_plot, scatter_plot, histogram, cdf_plot
- bioinformatics: volcano_plot, ma_plot, heatmap, pca_plot, enrichment_plot
- survival: kaplan_meier, cumulative_incidence
- imaging: intensity_profile, colocalization_plot, roi_quantification
- molecular: sequence_logo, domain_architecture
"""

from figcombo.plot_types.statistics import (
    bar_plot,
    box_plot,
    violin_plot,
    scatter_plot,
    histogram,
    cdf_plot,
)
from figcombo.plot_types.bioinformatics import (
    volcano_plot,
    ma_plot,
    heatmap,
    pca_plot,
    enrichment_plot,
)
from figcombo.plot_types.survival import (
    kaplan_meier,
    cumulative_incidence,
)
from figcombo.plot_types.imaging import (
    intensity_profile,
    colocalization_plot,
    roi_quantification,
)
from figcombo.plot_types.molecular import (
    sequence_logo,
    domain_architecture,
)

__all__ = [
    # Statistics
    'bar_plot',
    'box_plot',
    'violin_plot',
    'scatter_plot',
    'histogram',
    'cdf_plot',
    # Bioinformatics
    'volcano_plot',
    'ma_plot',
    'heatmap',
    'pca_plot',
    'enrichment_plot',
    # Survival
    'kaplan_meier',
    'cumulative_incidence',
    # Imaging
    'intensity_profile',
    'colocalization_plot',
    'roi_quantification',
    # Molecular
    'sequence_logo',
    'domain_architecture',
]
