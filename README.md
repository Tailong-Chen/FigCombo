# FigCombo

**Python tool for composing publication-ready multi-panel scientific figures.**

Designed for Nature, Science, Cell and other journal specifications. Replace your Adobe Illustrator figure assembly workflow with reproducible Python code.

## Features

- **ASCII Art Layout** — Define panel arrangements intuitively
- **Mixed Panel Types** — Combine imported images (microscopy, blots) with data-driven plots
- **Journal Presets** — Built-in specs for Nature, Science, Cell, PNAS, Lancet, NEJM, etc.
- **Unified Styling** — One-place font, size, color configuration applied globally
- **Auto Panel Labels** — Automatic a/b/c or A/B/C labeling per journal convention
- **Validation** — Pre-export checks for size, DPI, font compliance
- **Extensible** — Register custom plot types for reuse

## Quick Start

```bash
pip install -e .
```

```python
from figcombo import Figure, ImagePanel, PlotPanel
import pandas as pd

# Define a plot function
def my_barplot(ax, data):
    ax.bar(data['group'], data['value'])
    ax.set_ylabel('Value (AU)')

# Compose the figure
fig = Figure(
    journal='nature',
    size='double',
    layout="""
    aab
    aac
    ddd
    """
)

fig['a'] = ImagePanel('confocal.tif', scale_bar='50 μm')
fig['b'] = PlotPanel(my_barplot, data=df)
fig['c'] = PlotPanel(my_boxplot, data=df)
fig['d'] = ImagePanel('western_blot.png', trim=True)

# Validate, preview, and save
fig.validate().print()
fig.preview()
fig.save('Figure1.pdf')
```

## Layout Templates

```python
from figcombo import list_templates

# See all available templates
print(list_templates())

# Use a template
fig = Figure(journal='nature', template='4_grid')
```

## Custom Plot Types

```python
from figcombo import register_plot_type, PlotPanel

@register_plot_type('volcano')
def volcano_plot(ax, data, fc_col='log2FC', p_col='pvalue', **kwargs):
    sig = data[data[p_col] < 0.05]
    nonsig = data[data[p_col] >= 0.05]
    ax.scatter(nonsig[fc_col], -np.log10(nonsig[p_col]), c='grey', s=5)
    ax.scatter(sig[fc_col], -np.log10(sig[p_col]), c='red', s=5)

# Reuse anywhere
fig['b'] = PlotPanel('volcano', data=deseq_results)
```

## Supported Journals

| Journal | Key | Single | Double |
|---------|-----|--------|--------|
| Nature | `nature` | 89 mm | 183 mm |
| Science | `science` | 55 mm | 175 mm |
| Cell | `cell` | 85 mm | 178 mm |
| PNAS | `pnas` | 87 mm | 178 mm |
| Lancet | `lancet` | 80 mm | 170 mm |
| NEJM | `nejm` | 84 mm | 175 mm |
| eLife | `elife` | 85 mm | 178 mm |

Nature sub-journals (Nature Methods, Nature Communications, etc.) inherit the main Nature specs.

## Requirements

- Python >= 3.9
- matplotlib >= 3.7
- numpy >= 1.24
- Pillow >= 10.0
- seaborn >= 0.13

## License

MIT
