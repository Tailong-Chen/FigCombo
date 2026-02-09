"""Bioinformatics plot types for scientific figures.

This module provides specialized visualizations for bioinformatics analysis
including volcano plots, MA plots, heatmaps, PCA plots, and enrichment plots.
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


@register_plot_type('volcano_plot')
def volcano_plot(
    ax: 'Axes',
    data: Any,
    fc_col: str = 'log2FoldChange',
    p_col: str = 'pvalue',
    padj_col: str | None = None,
    fc_threshold: float = 1.0,
    p_threshold: float = 0.05,
    highlight: Sequence[str] | None = None,
    highlight_col: str | None = None,
    gene_col: str | None = None,
    annotate_genes: Sequence[str] | None = None,
    annotate_top_n: int = 0,
    colors: dict[str, str] | None = None,
    alpha: float = 0.6,
    point_size: float = 20,
    **kwargs: Any,
) -> None:
    """Create a volcano plot for differential expression analysis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Differential expression results with fold change and p-values.
    fc_col : str, default 'log2FoldChange'
        Column name for log2 fold change values.
    p_col : str, default 'pvalue'
        Column name for p-values.
    padj_col : str, optional
        Column name for adjusted p-values. If provided, uses this instead of p_col.
    fc_threshold : float, default 1.0
        Absolute log2 fold change threshold for significance.
    p_threshold : float, default 0.05
        P-value threshold for significance.
    highlight : sequence of str, optional
        List of gene IDs to highlight regardless of thresholds.
    highlight_col : str, optional
        Column name containing gene IDs for highlighting.
    gene_col : str, optional
        Column name for gene names/IDs (for annotations).
    annotate_genes : sequence of str, optional
        Specific genes to annotate with labels.
    annotate_top_n : int, default 0
        Number of top significant genes to annotate.
    colors : dict, optional
        Custom colors for categories: {'up', 'down', 'ns'}.
        Defaults use Okabe-Ito palette.
    alpha : float, default 0.6
        Point transparency.
    point_size : float, default 20
        Size of scatter points.
    **kwargs
        Additional arguments passed to ax.scatter().

    Examples
    --------
    >>> volcano_plot(ax, deseq_results)

    >>> volcano_plot(ax, results, fc_col='logFC', padj_col='padj',
    ...              annotate_genes=['TP53', 'BRCA1'])

    >>> volcano_plot(ax, results, annotate_top_n=10)
    """
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    # Use adjusted p-values if available
    p_values = data[padj_col] if padj_col and padj_col in data.columns else data[p_col]

    # Calculate -log10(p)
    log_p = -np.log10(p_values.replace(0, p_values[p_values > 0].min() * 0.1))
    fc = data[fc_col]

    # Determine significance categories
    sig_up = (fc > fc_threshold) & (p_values < p_threshold)
    sig_down = (fc < -fc_threshold) & (p_values < p_threshold)

    # Default colors using Okabe-Ito
    default_colors = {
        'up': '#D55E00',      # vermillion
        'down': '#0072B2',    # blue
        'ns': '#999999',      # gray
        'highlight': '#E69F00',  # orange
    }
    colors = {**default_colors, **(colors or {})}

    # Plot non-significant first
    ns_mask = ~(sig_up | sig_down)
    ax.scatter(
        fc[ns_mask],
        log_p[ns_mask],
        c=colors['ns'],
        alpha=alpha * 0.5,
        s=point_size * 0.5,
        label='Not significant',
        **kwargs
    )

    # Plot significant down
    ax.scatter(
        fc[sig_down],
        log_p[sig_down],
        c=colors['down'],
        alpha=alpha,
        s=point_size,
        label=f'Down (log2FC < -{fc_threshold})',
        **kwargs
    )

    # Plot significant up
    ax.scatter(
        fc[sig_up],
        log_p[sig_up],
        c=colors['up'],
        alpha=alpha,
        s=point_size,
        label=f'Up (log2FC > {fc_threshold})',
        **kwargs
    )

    # Highlight specific genes
    if highlight is not None and highlight_col is not None:
        highlight_mask = data[highlight_col].isin(highlight)
        ax.scatter(
            fc[highlight_mask],
            log_p[highlight_mask],
            facecolors='none',
            edgecolors=colors['highlight'],
            linewidths=2,
            s=point_size * 2,
        )

    # Add threshold lines
    ax.axhline(-np.log10(p_threshold), color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.axvline(-fc_threshold, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.axvline(fc_threshold, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)

    # Annotations
    genes_to_annotate = []
    if annotate_genes is not None and gene_col is not None:
        genes_to_annotate.extend(annotate_genes)

    if annotate_top_n > 0 and gene_col is not None:
        # Select top N by significance
        top_indices = log_p.nlargest(annotate_top_n).index
        top_genes = data.loc[top_indices, gene_col].tolist()
        genes_to_annotate.extend(top_genes)

    genes_to_annotate = list(set(genes_to_annotate))  # Remove duplicates

    if genes_to_annotate and gene_col is not None:
        for gene in genes_to_annotate:
            if gene in data[gene_col].values:
                idx = data[data[gene_col] == gene].index[0]
                ax.annotate(
                    gene,
                    (fc.loc[idx], log_p.loc[idx]),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=7,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3),
                )

    ax.set_xlabel('log2 Fold Change')
    ax.set_ylabel('-log10(p-value)')
    ax.legend(loc='best', frameon=False, fontsize=6)


@register_plot_type('ma_plot')
def ma_plot(
    ax: 'Axes',
    data: Any,
    fc_col: str = 'log2FoldChange',
    base_mean_col: str = 'baseMean',
    p_col: str = 'pvalue',
    padj_col: str | None = None,
    p_threshold: float = 0.05,
    colors: dict[str, str] | None = None,
    alpha: float = 0.5,
    point_size: float = 15,
    **kwargs: Any,
) -> None:
    """Create an MA plot (log ratio vs mean abundance) for DE analysis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Differential expression results.
    fc_col : str, default 'log2FoldChange'
        Column name for log2 fold change (M values).
    base_mean_col : str, default 'baseMean'
        Column name for mean expression (A values).
    p_col : str, default 'pvalue'
        Column name for p-values.
    padj_col : str, optional
        Column name for adjusted p-values.
    p_threshold : float, default 0.05
        P-value threshold for highlighting significant genes.
    colors : dict, optional
        Custom colors: {'sig', 'ns'}.
    alpha : float, default 0.5
        Point transparency.
    point_size : float, default 15
        Size of scatter points.
    **kwargs
        Additional arguments passed to ax.scatter().

    Examples
    --------
    >>> ma_plot(ax, deseq_results)

    >>> ma_plot(ax, results, base_mean_col='AveExpr', fc_col='logFC')
    """
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    # Get values
    m_values = data[fc_col]
    a_values = np.log2(data[base_mean_col] + 1)

    # Determine significance
    p_values = data[padj_col] if padj_col and padj_col in data.columns else data[p_col]
    sig_mask = p_values < p_threshold

    # Default colors
    default_colors = {
        'sig': '#D55E00',
        'ns': '#999999',
    }
    colors = {**default_colors, **(colors or {})}

    # Plot non-significant
    ax.scatter(
        a_values[~sig_mask],
        m_values[~sig_mask],
        c=colors['ns'],
        alpha=alpha * 0.5,
        s=point_size * 0.5,
        label='Not significant',
        **kwargs
    )

    # Plot significant
    ax.scatter(
        a_values[sig_mask],
        m_values[sig_mask],
        c=colors['sig'],
        alpha=alpha,
        s=point_size,
        label=f'p < {p_threshold}',
        **kwargs
    )

    # Add horizontal line at y=0
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

    ax.set_xlabel(f'log2({base_mean_col})')
    ax.set_ylabel(f'{fc_col} (M)')
    ax.legend(loc='best', frameon=False, fontsize=6)


@register_plot_type('heatmap')
def heatmap(
    ax: 'Axes',
    data: Any,
    row_labels: Sequence[str] | None = None,
    col_labels: Sequence[str] | None = None,
    cmap: str = 'RdBu_r',
    center: float | None = 0,
    vmin: float | None = None,
    vmax: float | None = None,
    cluster_rows: bool = False,
    cluster_cols: bool = False,
    annotate: bool = False,
    fmt: str = '.2f',
    cbar_label: str = '',
    **kwargs: Any,
) -> None:
    """Create a heatmap with optional hierarchical clustering.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or array-like
        2D data matrix to visualize.
    row_labels : sequence of str, optional
        Labels for rows. Uses data index if DataFrame.
    col_labels : sequence of str, optional
        Labels for columns. Uses data columns if DataFrame.
    cmap : str, default 'RdBu_r'
        Colormap name.
    center : float, optional
        Value to center colormap at. Default 0 for diverging data.
    vmin, vmax : float, optional
        Minimum and maximum values for colormap.
    cluster_rows : bool, default False
        Whether to perform hierarchical clustering on rows.
    cluster_cols : bool, default False
        Whether to perform hierarchical clustering on columns.
    annotate : bool, default False
        Whether to annotate cells with values.
    fmt : str, default '.2f'
        Format string for annotations.
    cbar_label : str, default ''
        Label for colorbar.
    **kwargs
        Additional arguments passed to seaborn.heatmap().

    Examples
    --------
    >>> heatmap(ax, expression_matrix, cmap='viridis')

    >>> heatmap(ax, df, cluster_rows=True, cluster_cols=True, annotate=True)

    >>> heatmap(ax, corr_matrix, center=0, vmin=-1, vmax=1)
    """
    import pandas as pd

    try:
        import seaborn as sns
    except ImportError:
        raise ImportError("seaborn is required for heatmap. Install with: pip install seaborn")

    # Convert to DataFrame if needed
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Perform clustering if requested
    if cluster_rows or cluster_cols:
        try:
            from scipy.cluster.hierarchy import linkage, dendrogram
            from scipy.spatial.distance import pdist

            # Cluster rows
            if cluster_rows and len(data) > 1:
                row_linkage = linkage(pdist(data), method='average')
                row_order = dendrogram(row_linkage, no_plot=True)['leaves']
                data = data.iloc[row_order]

            # Cluster columns
            if cluster_cols and len(data.columns) > 1:
                col_linkage = linkage(pdist(data.T), method='average')
                col_order = dendrogram(col_linkage, no_plot=True)['leaves']
                data = data.iloc[:, col_order]
        except ImportError:
            pass

    # Create heatmap
    sns.heatmap(
        data,
        ax=ax,
        cmap=cmap,
        center=center,
        vmin=vmin,
        vmax=vmax,
        annot=annotate,
        fmt=fmt,
        cbar_kws={'label': cbar_label} if cbar_label else {},
        **kwargs
    )

    # Set labels
    if row_labels:
        ax.set_yticklabels(row_labels, rotation=0)
    if col_labels:
        ax.set_xticklabels(col_labels, rotation=45, ha='right')


@register_plot_type('pca_plot')
def pca_plot(
    ax: 'Axes',
    data: Any,
    labels: Sequence[str] | None = None,
    hue: str | None = None,
    style: str | None = None,
    components: tuple[int, int] = (1, 2),
    scale: bool = True,
    explained_variance: bool = True,
    color: str | Sequence[str] | None = None,
    alpha: float = 0.8,
    point_size: float = 50,
    **kwargs: Any,
) -> None:
    """Create a PCA (Principal Component Analysis) scatter plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame or array-like
        Input data matrix (samples x features).
    labels : sequence of str, optional
        Sample labels. Uses data index if DataFrame.
    hue : str, optional
        Column name for color grouping (DataFrame input).
    style : str, optional
        Column name for marker style grouping.
    components : tuple of int, default (1, 2)
        Which principal components to plot (1-indexed).
    scale : bool, default True
        Whether to standardize features before PCA.
    explained_variance : bool, default True
        Whether to show explained variance on axis labels.
    color : str or list of str, optional
        Point color(s). Uses Okabe-Ito palette by default.
    alpha : float, default 0.8
        Point transparency.
    point_size : float, default 50
        Size of scatter points.
    **kwargs
        Additional arguments passed to scatter plot.

    Examples
    --------
    >>> pca_plot(ax, expression_matrix, labels=sample_names)

    >>> pca_plot(ax, df, hue='condition', components=(1, 2))

    >>> pca_plot(ax, df, hue='condition', style='timepoint', components=(2, 3))
    """
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # Convert to DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Prepare feature matrix
    X = data.select_dtypes(include=[np.number]).values

    # Scale if requested
    if scale:
        X = StandardScaler().fit_transform(X)

    # Perform PCA
    n_components = max(components)
    pca = PCA(n_components=n_components)
    pcs = pca.fit_transform(X)

    # Get component indices (0-indexed)
    pc_x, pc_y = components[0] - 1, components[1] - 1

    # Prepare labels
    if labels is None:
        labels = data.index.tolist()

    # Determine colors
    if color is None:
        colors = OKABE_ITO
    elif isinstance(color, str):
        colors = [color]
    else:
        colors = list(color)

    # Plot
    if hue is not None and hue in data.columns:
        groups = data[hue].unique()
        for i, group in enumerate(groups):
            mask = data[hue] == group
            ax.scatter(
                pcs[mask, pc_x],
                pcs[mask, pc_y],
                c=colors[i % len(colors)],
                alpha=alpha,
                s=point_size,
                label=str(group),
                **kwargs
            )
        ax.legend(title=hue, frameon=False, loc='best')
    else:
        ax.scatter(
            pcs[:, pc_x],
            pcs[:, pc_y],
            c=colors[0],
            alpha=alpha,
            s=point_size,
            **kwargs
        )

    # Set axis labels
    if explained_variance:
        var_explained = pca.explained_variance_ratio_ * 100
        ax.set_xlabel(f'PC{components[0]} ({var_explained[pc_x]:.1f}%)')
        ax.set_ylabel(f'PC{components[1]} ({var_explained[pc_y]:.1f}%)')
    else:
        ax.set_xlabel(f'PC{components[0]}')
        ax.set_ylabel(f'PC{components[1]}')

    # Add sample labels if provided
    if labels is not None:
        for i, label in enumerate(labels):
            ax.annotate(
                str(label),
                (pcs[i, pc_x], pcs[i, pc_y]),
                xytext=(3, 3),
                textcoords='offset points',
                fontsize=6,
                alpha=0.7
            )


@register_plot_type('enrichment_plot')
def enrichment_plot(
    ax: 'Axes',
    data: Any,
    term_col: str = 'term',
    p_col: str = 'pvalue',
    padj_col: str | None = None,
    gene_ratio_col: str | None = None,
    count_col: str | None = None,
    top_n: int = 10,
    color_by: str = 'pvalue',
    cmap: str = 'Reds',
    horizontal: bool = True,
    **kwargs: Any,
) -> None:
    """Create a gene enrichment analysis plot (bar or dot plot).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    data : pandas.DataFrame
        Enrichment results with terms and statistics.
    term_col : str, default 'term'
        Column name for pathway/GO terms.
    p_col : str, default 'pvalue'
        Column name for p-values.
    padj_col : str, optional
        Column name for adjusted p-values.
    gene_ratio_col : str, optional
        Column name for gene ratio (enriched genes / total genes).
    count_col : str, optional
        Column name for enriched gene counts (for dot size).
    top_n : int, default 10
        Number of top significant terms to show.
    color_by : str, default 'pvalue'
        Column to use for coloring bars/dots.
    cmap : str, default 'Reds'
        Colormap for coloring.
    horizontal : bool, default True
        Whether to plot horizontally (bars) or vertically (dots).
    **kwargs
        Additional arguments passed to plotting functions.

    Examples
    --------
    >>> enrichment_plot(ax, go_results, top_n=15)

    >>> enrichment_plot(ax, kegg_results, term_col='Description',
    ...                 gene_ratio_col='GeneRatio', count_col='Count')

    >>> enrichment_plot(ax, results, horizontal=False, cmap='Blues')
    """
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    # Use adjusted p-values if available
    p_values = data[padj_col] if padj_col and padj_col in data.columns else data[p_col]

    # Select top N terms
    df_plot = data.copy()
    df_plot['_p'] = p_values
    df_plot = df_plot.nsmallest(top_n, '_p')
    df_plot = df_plot.sort_values('_p', ascending=False)  # For plotting order

    terms = df_plot[term_col]
    colors = -np.log10(df_plot[color_by].replace(0, 1e-300))

    if horizontal:
        # Horizontal bar plot
        y_pos = np.arange(len(terms))

        bars = ax.barh(
            y_pos,
            -np.log10(df_plot['_p']),
            color=colors,
            cmap=cmap,
            **kwargs
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(terms, fontsize=7)
        ax.set_xlabel('-log10(p-value)')

        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=colors.min(), vmax=colors.max()))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label(f'-log10({color_by})')

    else:
        # Dot plot
        if count_col and count_col in df_plot.columns:
            sizes = df_plot[count_col]
        else:
            sizes = 50

        y_pos = np.arange(len(terms))

        scatter = ax.scatter(
            -np.log10(df_plot['_p']),
            y_pos,
            c=colors,
            s=sizes if isinstance(sizes, (int, float)) else sizes * 5,
            cmap=cmap,
            alpha=0.8,
            **kwargs
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(terms, fontsize=7)
        ax.set_xlabel('-log10(p-value)')

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(f'-log10({color_by})')


# Need to import matplotlib for enrichment_plot colorbar
import matplotlib.pyplot as plt
