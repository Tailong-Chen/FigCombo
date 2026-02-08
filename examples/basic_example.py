"""Basic example: create a 4-panel figure with synthetic data."""

import numpy as np
import matplotlib.pyplot as plt

from figcombo import Figure, PlotPanel


# -- Define plot functions --

def scatter_plot(ax, data):
    """Panel a: scatter plot with regression line."""
    x, y = data['x'], data['y']
    ax.scatter(x, y, s=15, alpha=0.6)
    # Fit line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(sorted(x), p(sorted(x)), 'r-', linewidth=1)
    ax.set_xlabel('Variable X')
    ax.set_ylabel('Variable Y')


def bar_plot(ax, data):
    """Panel b: grouped bar chart."""
    groups = data['groups']
    values = data['values']
    errors = data['errors']
    colors = ['#E69F00', '#56B4E9', '#009E73', '#D55E00']
    bars = ax.bar(groups, values, yerr=errors, capsize=3,
                  color=colors[:len(groups)], edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Expression (AU)')


def line_plot(ax, data):
    """Panel c: time series with error bands."""
    time = data['time']
    for i, (label, mean, std) in enumerate(
        zip(data['labels'], data['means'], data['stds'])
    ):
        ax.plot(time, mean, label=label, linewidth=1.2)
        ax.fill_between(time, mean - std, mean + std, alpha=0.2)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Signal (mV)')
    ax.legend(frameon=False, fontsize=6)


def heatmap_plot(ax, data):
    """Panel d: correlation heatmap."""
    import seaborn as sns
    sns.heatmap(
        data['matrix'],
        ax=ax,
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.7, 'label': 'Correlation'},
        xticklabels=data.get('labels', True),
        yticklabels=data.get('labels', True),
    )


# -- Generate synthetic data --

np.random.seed(42)

scatter_data = {
    'x': np.random.randn(50),
    'y': np.random.randn(50) * 0.5 + np.random.randn(50),
}

bar_data = {
    'groups': ['Control', 'Drug A', 'Drug B', 'Combo'],
    'values': [1.0, 2.3, 1.8, 3.5],
    'errors': [0.2, 0.4, 0.3, 0.5],
}

time = np.linspace(0, 24, 50)
line_data = {
    'time': time,
    'labels': ['Control', 'Treatment'],
    'means': [
        np.sin(time / 4) + 1,
        np.sin(time / 4) * 1.5 + 2,
    ],
    'stds': [
        np.ones_like(time) * 0.3,
        np.ones_like(time) * 0.4,
    ],
}

n_genes = 6
gene_labels = [f'Gene {i+1}' for i in range(n_genes)]
corr_matrix = np.corrcoef(np.random.randn(n_genes, 20))
heatmap_data = {'matrix': corr_matrix, 'labels': gene_labels}


# -- Compose figure --

fig = Figure(
    journal='nature',
    size='double',
    layout="""
    ab
    cd
    """,
)

fig['a'] = PlotPanel(scatter_plot, data=scatter_data)
fig['b'] = PlotPanel(bar_plot, data=bar_data)
fig['c'] = PlotPanel(line_plot, data=line_data)
fig['d'] = PlotPanel(heatmap_plot, data=heatmap_data)

# Validate
report = fig.validate()
report.print()

# Render and save
fig.save('output/basic_example.pdf')
fig.save('output/basic_example.png', dpi=300)

print("\nFigure info:")
print(fig.info())
print("\nSaved to output/basic_example.pdf and .png")
