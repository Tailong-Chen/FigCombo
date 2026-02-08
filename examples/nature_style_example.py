"""Nature-style example: asymmetric layout with 5 panels.

Demonstrates:
- Non-uniform panel sizes (large image + small quantifications)
- Nature lowercase bold labels
- Violin plot, survival curve, bar chart
- Custom registered plot type
- Validation and export
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

from figcombo import Figure, PlotPanel, register_plot_type


# ============================================================
# Register custom plot types
# ============================================================

@register_plot_type('survival')
def survival_curve(ax, data, **kwargs):
    """Kaplan-Meier style survival curve."""
    for label, time, surv, color in zip(
        data['labels'], data['times'], data['survivals'], data['colors']
    ):
        ax.step(time, surv, where='post', label=label, color=color, linewidth=1.2)
        # Add censoring marks
        censor_idx = np.random.choice(len(time), size=3, replace=False)
        ax.plot(
            time[censor_idx], surv[censor_idx],
            '|', color=color, markersize=6, markeredgewidth=1.5,
        )
    ax.set_xlabel('Time (months)')
    ax.set_ylabel('Overall survival')
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, None)
    ax.legend(frameon=False, loc='lower left')
    # Add p-value annotation
    ax.text(
        0.95, 0.95, 'P = 0.003',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=7, fontstyle='italic',
    )


@register_plot_type('violin_comparison')
def violin_comparison(ax, data, **kwargs):
    """Split violin plot for group comparison."""
    positions = []
    for i, (label, group_data) in enumerate(zip(data['labels'], data['groups'])):
        parts = ax.violinplot(
            group_data, positions=[i], showmeans=True,
            showextrema=False, showmedians=False,
        )
        for pc in parts['bodies']:
            pc.set_alpha(0.7)
        # Overlay individual points with jitter
        jitter = np.random.normal(0, 0.04, size=len(group_data))
        ax.scatter(
            np.full_like(group_data, i) + jitter, group_data,
            s=8, alpha=0.4, color='black', zorder=3,
        )
        positions.append(i)

    ax.set_xticks(positions)
    ax.set_xticklabels(data['labels'])
    ax.set_ylabel(data.get('ylabel', 'Value'))

    # Add significance brackets
    if 'comparisons' in data:
        y_max = max(max(g) for g in data['groups'])
        for comp in data['comparisons']:
            i1, i2, pval = comp
            y = y_max * 1.05 + (comp == data['comparisons'][-1]) * y_max * 0.08
            ax.plot([i1, i1, i2, i2], [y, y + y_max * 0.02, y + y_max * 0.02, y],
                    'k-', linewidth=0.8)
            ax.text((i1 + i2) / 2, y + y_max * 0.03, pval,
                    ha='center', va='bottom', fontsize=6)


# ============================================================
# Generate synthetic data
# ============================================================

np.random.seed(2026)

# Panel a: "microscopy" placeholder - colored noise image
def microscopy_placeholder(ax, data, **kwargs):
    """Fake microscopy image as placeholder."""
    img = np.zeros((200, 300, 3))
    # Green channel (GFP-like)
    for _ in range(15):
        cx, cy = np.random.randint(20, 180), np.random.randint(20, 280)
        yy, xx = np.ogrid[-cx:200-cx, -cy:300-cy]
        r = np.random.randint(8, 25)
        mask = xx**2 + yy**2 <= r**2
        intensity = np.random.uniform(0.4, 1.0)
        img[:, :, 1] = np.clip(img[:, :, 1] + mask * intensity, 0, 1)
    # Add some blue (DAPI-like)
    for _ in range(25):
        cx, cy = np.random.randint(10, 190), np.random.randint(10, 290)
        yy, xx = np.ogrid[-cx:200-cx, -cy:300-cy]
        r = np.random.randint(4, 10)
        mask = xx**2 + yy**2 <= r**2
        img[:, :, 2] = np.clip(img[:, :, 2] + mask * 0.6, 0, 1)
    # Background noise
    img += np.random.normal(0, 0.02, img.shape)
    img = np.clip(img, 0, 1)

    ax.imshow(img)
    ax.set_axis_off()
    # Scale bar
    bar_y = 185
    ax.plot([220, 280], [bar_y, bar_y], 'w-', linewidth=2)
    ax.text(250, bar_y - 8, '50 μm', color='white', ha='center',
            fontsize=6, fontweight='bold')


# Panel b: survival data
n_time = 50
time_ctrl = np.sort(np.random.exponential(20, n_time))
time_treat = np.sort(np.random.exponential(35, n_time))
surv_ctrl = np.linspace(1, 0.15, n_time)
surv_treat = np.linspace(1, 0.45, n_time)
survival_data = {
    'labels': ['Control', 'Treatment'],
    'times': [time_ctrl, time_treat],
    'survivals': [surv_ctrl, surv_treat],
    'colors': ['#D55E00', '#0072B2'],
}

# Panel c: violin comparison
violin_data = {
    'labels': ['WT', 'KO', 'KO+Rescue'],
    'groups': [
        np.random.normal(5, 1.2, 30),
        np.random.normal(2.5, 1.5, 30),
        np.random.normal(4.8, 1.0, 30),
    ],
    'ylabel': 'Expression (AU)',
    'comparisons': [(0, 1, '***'), (1, 2, '**')],
}

# Panel d: bar chart with individual points
bar_groups = ['Ctrl', 'Low', 'Med', 'High']
bar_means = [1.0, 1.8, 2.9, 4.2]
bar_raw = [np.random.normal(m, 0.5, 8) for m in bar_means]

def dose_response(ax, data, **kwargs):
    """Bar chart with individual data points."""
    colors = ['#999999', '#56B4E9', '#009E73', '#E69F00']
    for i, (grp, raw, color) in enumerate(
        zip(data['groups'], data['raw'], colors)
    ):
        mean = np.mean(raw)
        sem = np.std(raw) / np.sqrt(len(raw))
        ax.bar(i, mean, yerr=sem, capsize=3,
               color=color, edgecolor='black', linewidth=0.5, alpha=0.7)
        jitter = np.random.normal(0, 0.08, size=len(raw))
        ax.scatter(np.full_like(raw, i) + jitter, raw,
                   s=12, color='black', alpha=0.5, zorder=3)
    ax.set_xticks(range(len(data['groups'])))
    ax.set_xticklabels(data['groups'])
    ax.set_ylabel('Fold change')
    ax.set_xlabel('Dose')

dose_data = {'groups': bar_groups, 'raw': bar_raw}

# Panel e: heatmap
n_genes, n_samples = 10, 6
gene_names = [f'Gene{i+1}' for i in range(n_genes)]
sample_names = ['Ctrl1', 'Ctrl2', 'Ctrl3', 'KO1', 'KO2', 'KO3']
expr_matrix = np.random.randn(n_genes, n_samples)
expr_matrix[:5, 3:] += 2  # upregulated in KO
expr_matrix[5:, 3:] -= 1.5  # downregulated in KO

def expression_heatmap(ax, data, **kwargs):
    """Gene expression heatmap."""
    sns.heatmap(
        data['matrix'], ax=ax,
        cmap='RdBu_r', center=0,
        xticklabels=data['samples'],
        yticklabels=data['genes'],
        linewidths=0.3,
        cbar_kws={'shrink': 0.6, 'label': 'Z-score', 'pad': 0.02},
    )
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='y', rotation=0)

heatmap_data = {
    'matrix': expr_matrix,
    'genes': gene_names,
    'samples': sample_names,
}


# ============================================================
# Compose figure
# ============================================================

fig = Figure(
    journal='nature',
    size='double',           # 183 mm wide
    height_mm=160,           # slightly shorter than square
    layout="""
    aabc
    aade
    """,
)

fig['a'] = PlotPanel(microscopy_placeholder, data=None)
fig['b'] = PlotPanel('survival', data=survival_data)
fig['c'] = PlotPanel('violin_comparison', data=violin_data)
fig['d'] = PlotPanel(dose_response, data=dose_data)
fig['e'] = PlotPanel(expression_heatmap, data=heatmap_data)

# Validate
print("=== Validation Report ===")
fig.validate().print()

# Save
fig.save('output/nature_style.pdf')
fig.save('output/nature_style.png', dpi=300)

print(f"\n{fig.info()}")
print("\nSaved to output/nature_style.pdf and .png")
