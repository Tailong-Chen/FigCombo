# FigCombo

**Python tool for composing publication-ready multi-panel scientific figures.**

Designed for Nature, Science, Cell and other journal specifications. Replace your Adobe Illustrator figure assembly workflow with reproducible Python code.

## Features

- **ASCII Art Layout** — Define panel arrangements intuitively
- **Mixed Panel Types** — Combine imported images (microscopy, blots) with data-driven plots
- **Journal Presets** — Built-in specs for 85+ journals including Nature, Science, Cell, PNAS, Lancet, NEJM, etc.
- **Unified Styling** — One-place font, size, color configuration applied globally
- **Auto Panel Labels** — Automatic a/b/c or A/B/C labeling per journal convention
- **Validation** — Pre-export checks for size, DPI, font compliance
- **Built-in Plot Types** — 18+ scientific plot types (volcano, KM curves, heatmaps, etc.)
- **Web Interface** — Drag-and-drop GUI for server deployment
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

## Web Interface

FigCombo includes a full-featured web interface for drag-and-drop figure composition:

```bash
cd web
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

**Web Interface Features:**
- Drag-and-drop layout builder with 40+ templates
- Upload images and arrange in panels
- Built-in plot types with live parameter editing
- Upload custom Python plotting code
- Real-time preview
- Export to PDF/PNG/SVG/TIFF
- Project save/load

See [web/README_WEB.md](web/README_WEB.md) for detailed documentation.

## Layout Templates

```python
from figcombo import list_templates

# See all available templates
print(list_templates())

# See Nature-optimized templates with details
print(list_templates(category='specialized', show_details=True))

# Use a template
fig = Figure(journal='nature', template='4_grid')
```

### Available Template Categories

- **Grid layouts**: `nature_2x2`, `nature_3x2`, `nature_4x2`, `4_grid`, `6_grid_3x2`
- **Complex layouts**: `nature_l_shape`, `nature_vertical_split`, `nature_main_with_insets`
- **Specialized layouts**: `nature_western_blot`, `nature_microscopy_grid`, `nature_figure1`

## Built-in Plot Types

```python
from figcombo import PlotPanel
from figcombo.plot_types import volcano_plot, kaplan_meier, heatmap

# Use built-in plot types
fig['a'] = PlotPanel('volcano_plot', data=de_results, gene_col='gene')
fig['b'] = PlotPanel('kaplan_meier', data=survival_df, time_col='months', event_col='death')
fig['c'] = PlotPanel('heatmap', data=expression_matrix, cluster=True)
```

### Available Plot Types

**Statistics**: `bar_plot`, `box_plot`, `violin_plot`, `scatter_plot`, `histogram`, `cdf_plot`

**Bioinformatics**: `volcano_plot`, `ma_plot`, `heatmap`, `pca_plot`, `enrichment_plot`

**Survival**: `kaplan_meier`, `cumulative_incidence`

**Imaging**: `intensity_profile`, `colocalization_plot`, `roi_quantification`

**Molecular**: `sequence_logo`, `domain_architecture`

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

## ImagePanel Features

```python
from figcombo import ImagePanel

fig['a'] = ImagePanel(
    'microscopy.tif',
    # Basic adjustments
    trim=True,                    # Auto-trim white borders
    brightness=1.2,               # Brightness factor
    contrast=1.1,                 # Contrast factor
    gamma=0.8,                    # Gamma correction

    # Transformations
    rotation=90,                  # Rotate 90/180/270 degrees
    flip_h=True,                  # Horizontal flip
    flip_v=False,                 # Vertical flip

    # Pseudo-coloring
    colormap='viridis',           # Apply colormap to grayscale

    # Multi-channel
    channel='red',                # Select specific channel

    # Scale bar
    scale_bar='50 μm',
    pixel_size=0.5,               # μm per pixel
    scale_bar_style='bar',        # 'bar' or 'line'
    scale_bar_position='bottom_right',
    scale_bar_color='white',
    scale_bar_bg=True,            # Semi-transparent background

    # Annotations
    annotations=[
        {'type': 'arrow', 'x': 0.5, 'y': 0.5, 'text': 'Nucleus'},
        {'type': 'circle', 'x': 0.3, 'y': 0.3, 'radius': 0.1},
    ],

    # ROI highlighting
    roi={'x': 0.2, 'y': 0.2, 'width': 0.3, 'height': 0.3,
         'style': 'rectangle', 'color': 'yellow'},
)
```

## Supported Journals

### Major Publishers

| Journal | Key | Single | Double |
|---------|-----|--------|--------|
| Nature | `nature` | 89 mm | 183 mm |
| Science | `science` | 55 mm | 175 mm |
| Cell | `cell` | 85 mm | 178 mm |
| PNAS | `pnas` | 87 mm | 178 mm |
| The Lancet | `lancet` | 80 mm | 170 mm |
| NEJM | `nejm` | 84 mm | 175 mm |
| JAMA | `jama` | 86 mm | 178 mm |
| eLife | `elife` | 85 mm | 178 mm |

### Nature Portfolio (40+ journals)

All Nature sub-journals inherit from the main Nature specs:
- `nature_methods`, `nature_communications`, `nature_medicine`
- `nature_genetics`, `nature_biotechnology`, `nature_cell_biology`
- `nature_immunology`, `nature_neuroscience`, `nature_protocols`
- `nature_structural_molecular_biology`, `nature_chemical_biology`
- `nature_metabolism`, `nature_microbiology`, `nature_plants`
- `nature_cancer`, `nature_aging`, `nature_biomedical_engineering`
- `nature_reviews_*` series (13 review journals)

### Cell Press (15+ journals)

- `cancer_cell`, `neuron`, `developmental_cell`, `cell_metabolism`
- `cell_host_microbe`, `cell_systems`, `cell_genomics`
- `immunity`, `molecular_cell`, `cell_reports`, `cell_stem_cell`

### Other Publishers

- **EMBO Press**: `embo_journal`, `embo_reports`, `embo_molecular_medicine`
- **CSHL Press**: `genes_development`, `genome_research`, `rna`
- **Rockefeller**: `journal_cell_biology`, `journal_experimental_medicine`
- **ASH**: `blood`, `blood_advances`
- **PLOS**: `plos_biology`, `plos_genetics`, `plos_pathogens`
- **BMC**: `bmc_biology`, `genome_biology`, `bmc_genomics`
- **Royal Society**: `open_biology`, `proceedings_b`

## Validation

```python
# Validate figure against journal specifications
report = fig.validate()
report.print()

# Check specific aspects
from figcombo.knowledge.validators import (
    validate_colorblind_friendly,
    validate_font_size,
    validate_dpi,
)

# Check color palette
report = validate_colorblind_friendly(['#E69F00', '#56B4E9', '#009E73'])

# Get recommendations
from figcombo.knowledge.validators import get_recommendations
rec = get_recommendations('nature')
print(rec['fonts'])  # Recommended fonts for Nature
print(rec['dpi'])    # Recommended DPI settings
```

## Project Structure

```
figcombo/
├── __init__.py              # Main exports
├── figure.py                # Figure class
├── renderer.py              # Rendering engine
├── export.py                # Export functions
├── preview.py               # Interactive preview
├── panels/                  # Panel types
│   ├── base.py
│   ├── image_panel.py       # Image display
│   ├── plot_panel.py        # Data plots
│   ├── text_panel.py        # Text annotations
│   └── composite_panel.py   # Nested sub-panels
├── layout/                  # Layout engine
│   ├── parser.py            # ASCII layout parser
│   ├── grid.py              # Grid calculations
│   └── types.py             # Type definitions
├── styles/                  # Styling
│   └── manager.py           # StyleManager
├── knowledge/               # Journal specifications
│   ├── journal_specs.py     # 85+ journal specs
│   ├── layout_templates.py  # 40+ templates
│   ├── validators.py        # Validation system
│   └── panel_constraints.py # Panel constraints
├── plot_types/              # Built-in plot types
│   ├── statistics.py        # bar, box, violin, etc.
│   ├── bioinformatics.py    # volcano, heatmap, etc.
│   ├── survival.py          # KM curves
│   ├── imaging.py           # microscopy plots
│   └── molecular.py         # sequence logos
└── utils.py                 # Utilities

web/                         # Web interface
├── app.py                   # Flask backend
├── templates/               # HTML templates
├── static/                  # CSS, JS, uploads
└── README_WEB.md            # Web interface docs

examples/                    # Example scripts
├── basic_example.py
├── nature_style_example.py
├── nature_full_example.py
└── nature_mega_example.py
```

## Requirements

- Python >= 3.9
- matplotlib >= 3.7
- numpy >= 1.24
- Pillow >= 10.0
- seaborn >= 0.13

For web interface:
- Flask >= 2.3
- Werkzeug >= 2.3

## License

MIT
