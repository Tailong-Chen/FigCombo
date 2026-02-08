"""Realistic Nature-style full figure: 10 panels (a-j).

Mimics a typical immunology/cancer biology paper figure with:
- Microscopy images (a, b)
- Flow cytometry dot plots (c, d)
- Quantification bar charts (e, f)
- Survival curve (g)
- Heatmap (h)
- Violin + significance (i)
- Western blot (j)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from figcombo import Figure, PlotPanel, register_plot_type


np.random.seed(2026)


# ============================================================
# Helper: fake microscopy images
# ============================================================

def _make_fluorescence_image(h=150, w=200, n_cells=20, channels='green'):
    """Generate synthetic fluorescence microscopy image."""
    img = np.zeros((h, w, 3))
    # Background noise
    img += np.random.normal(0.02, 0.01, img.shape).clip(0)

    ch_map = {'green': 1, 'red': 0, 'blue': 2, 'cyan': (1, 2), 'magenta': (0, 2)}

    for _ in range(n_cells):
        cx = np.random.randint(10, h - 10)
        cy = np.random.randint(10, w - 10)
        r = np.random.randint(5, 18)
        yy, xx = np.ogrid[-cx:h - cx, -cy:w - cy]
        dist = np.sqrt(xx ** 2 + yy ** 2)
        mask = np.exp(-dist ** 2 / (2 * (r / 2) ** 2))
        intensity = np.random.uniform(0.3, 1.0)

        ch = ch_map.get(channels, 1)
        if isinstance(ch, tuple):
            for c in ch:
                img[:, :, c] += mask * intensity * 0.7
        else:
            img[:, :, ch] += mask * intensity

    # DAPI (blue nuclei)
    for _ in range(n_cells + 10):
        cx = np.random.randint(5, h - 5)
        cy = np.random.randint(5, w - 5)
        r = np.random.randint(3, 7)
        yy, xx = np.ogrid[-cx:h - cx, -cy:w - cy]
        dist = np.sqrt(xx ** 2 + yy ** 2)
        mask = np.exp(-dist ** 2 / (2 * (r / 2) ** 2))
        img[:, :, 2] += mask * np.random.uniform(0.2, 0.5)

    return img.clip(0, 1)


def _add_scale_bar(ax, img_w, label='50 μm'):
    """Add scale bar to image axes."""
    bar_len = int(img_w * 0.2)
    x0 = img_w - bar_len - 10
    y0 = 140
    ax.plot([x0, x0 + bar_len], [y0, y0], 'w-', linewidth=2.5)
    ax.text(x0 + bar_len / 2, y0 - 6, label, color='white',
            ha='center', fontsize=5.5, fontweight='bold')


# ============================================================
# Panel functions
# ============================================================

def panel_a_microscopy_ctrl(ax, data):
    """Panel a: Control group fluorescence microscopy."""
    img = _make_fluorescence_image(n_cells=18, channels='green')
    ax.imshow(img)
    ax.set_axis_off()
    _add_scale_bar(ax, 200)
    ax.set_title('Control', fontsize=7, pad=3)


def panel_b_microscopy_treat(ax, data):
    """Panel b: Treatment group fluorescence microscopy."""
    img = _make_fluorescence_image(n_cells=35, channels='green')
    # Make it brighter to show "more expression"
    img[:, :, 1] *= 1.4
    img = img.clip(0, 1)
    ax.imshow(img)
    ax.set_axis_off()
    _add_scale_bar(ax, 200)
    ax.set_title('Treatment', fontsize=7, pad=3)


def panel_c_flow_ctrl(ax, data):
    """Panel c: Flow cytometry - Control."""
    n = 5000
    x = np.random.lognormal(1.5, 0.8, n)
    y = np.random.lognormal(1.2, 0.9, n)
    # Gate quadrants
    ax.scatter(x, y, s=0.3, alpha=0.3, c='#0072B2', rasterized=True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.5, 500)
    ax.set_ylim(0.5, 500)
    ax.set_xlabel('CD4', fontsize=6)
    ax.set_ylabel('CD8', fontsize=6)
    ax.set_title('Control', fontsize=7, pad=3)
    # Quadrant lines
    ax.axhline(10, color='grey', linewidth=0.5, linestyle='--')
    ax.axvline(10, color='grey', linewidth=0.5, linestyle='--')
    # Percentages
    q_ur = np.sum((x > 10) & (y > 10)) / n * 100
    q_ul = np.sum((x <= 10) & (y > 10)) / n * 100
    q_lr = np.sum((x > 10) & (y <= 10)) / n * 100
    q_ll = np.sum((x <= 10) & (y <= 10)) / n * 100
    ax.text(0.95, 0.95, f'{q_ur:.1f}%', transform=ax.transAxes, ha='right', va='top', fontsize=5.5)
    ax.text(0.05, 0.95, f'{q_ul:.1f}%', transform=ax.transAxes, ha='left', va='top', fontsize=5.5)
    ax.text(0.95, 0.05, f'{q_lr:.1f}%', transform=ax.transAxes, ha='right', va='bottom', fontsize=5.5)
    ax.text(0.05, 0.05, f'{q_ll:.1f}%', transform=ax.transAxes, ha='left', va='bottom', fontsize=5.5)


def panel_d_flow_treat(ax, data):
    """Panel d: Flow cytometry - Treatment."""
    n = 5000
    x = np.random.lognormal(2.0, 0.7, n)
    y = np.random.lognormal(1.8, 0.8, n)
    ax.scatter(x, y, s=0.3, alpha=0.3, c='#D55E00', rasterized=True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.5, 500)
    ax.set_ylim(0.5, 500)
    ax.set_xlabel('CD4', fontsize=6)
    ax.set_ylabel('CD8', fontsize=6)
    ax.set_title('Treatment', fontsize=7, pad=3)
    ax.axhline(10, color='grey', linewidth=0.5, linestyle='--')
    ax.axvline(10, color='grey', linewidth=0.5, linestyle='--')
    q_ur = np.sum((x > 10) & (y > 10)) / n * 100
    q_ul = np.sum((x <= 10) & (y > 10)) / n * 100
    q_lr = np.sum((x > 10) & (y <= 10)) / n * 100
    q_ll = np.sum((x <= 10) & (y <= 10)) / n * 100
    ax.text(0.95, 0.95, f'{q_ur:.1f}%', transform=ax.transAxes, ha='right', va='top', fontsize=5.5)
    ax.text(0.05, 0.95, f'{q_ul:.1f}%', transform=ax.transAxes, ha='left', va='top', fontsize=5.5)
    ax.text(0.95, 0.05, f'{q_lr:.1f}%', transform=ax.transAxes, ha='right', va='bottom', fontsize=5.5)
    ax.text(0.05, 0.05, f'{q_ll:.1f}%', transform=ax.transAxes, ha='left', va='bottom', fontsize=5.5)


def panel_e_quant_bar(ax, data):
    """Panel e: Quantification of microscopy (fluorescence intensity)."""
    groups = ['Ctrl', 'Treatment']
    means = [1.0, 2.8]
    sems = [0.15, 0.25]
    raw = [np.random.normal(m, s * 3, 12) for m, s in zip(means, sems)]
    colors = ['#999999', '#009E73']

    for i, (m, se, r, c) in enumerate(zip(means, sems, raw, colors)):
        ax.bar(i, m, yerr=se, capsize=3, color=c, edgecolor='black',
               linewidth=0.5, alpha=0.7, width=0.6)
        jitter = np.random.normal(0, 0.06, len(r))
        ax.scatter(np.full(len(r), i) + jitter, r, s=10, c='black', alpha=0.4, zorder=3)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(groups)
    ax.set_ylabel('MFI (fold change)')
    # Significance bracket
    y_max = max(max(r) for r in raw) * 1.05
    ax.plot([0, 0, 1, 1], [y_max, y_max + 0.1, y_max + 0.1, y_max], 'k-', lw=0.8)
    ax.text(0.5, y_max + 0.15, '***', ha='center', fontsize=7)


def panel_f_quant_flow(ax, data):
    """Panel f: Quantification of flow cytometry (% CD4+CD8+)."""
    groups = ['Ctrl', 'Treatment']
    raw_ctrl = np.random.normal(12, 3, 8)
    raw_treat = np.random.normal(28, 5, 8)
    raw = [raw_ctrl, raw_treat]
    colors = ['#0072B2', '#D55E00']

    for i, (r, c) in enumerate(zip(raw, colors)):
        m = np.mean(r)
        se = np.std(r) / np.sqrt(len(r))
        ax.bar(i, m, yerr=se, capsize=3, color=c, edgecolor='black',
               linewidth=0.5, alpha=0.7, width=0.6)
        jitter = np.random.normal(0, 0.06, len(r))
        ax.scatter(np.full(len(r), i) + jitter, r, s=10, c='black', alpha=0.4, zorder=3)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(groups)
    ax.set_ylabel('CD4⁺CD8⁺ (%)')
    y_max = max(max(r) for r in raw) * 1.05
    ax.plot([0, 0, 1, 1], [y_max, y_max + 1, y_max + 1, y_max], 'k-', lw=0.8)
    ax.text(0.5, y_max + 1.5, '**', ha='center', fontsize=7)


def panel_g_survival(ax, data):
    """Panel g: Kaplan-Meier survival curves (3 groups)."""
    colors = ['#999999', '#0072B2', '#D55E00']
    labels = ['Vehicle', 'Drug A', 'Drug A + Anti-PD1']

    for label, color, scale in zip(labels, colors, [15, 25, 40]):
        n = 40
        t = np.sort(np.random.exponential(scale, n))
        s = np.linspace(1, np.random.uniform(0.05, 0.3), n)
        # Add some flat steps
        for _ in range(5):
            idx = np.random.randint(5, n - 5)
            s[idx:idx + 3] = s[idx]
        ax.step(t, s, where='post', label=label, color=color, linewidth=1.2)

    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Overall survival')
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, None)
    ax.legend(frameon=False, fontsize=5.5, loc='upper right')
    ax.text(0.95, 0.6, 'Log-rank\nP < 0.001', transform=ax.transAxes,
            ha='right', va='top', fontsize=5.5, fontstyle='italic')


def panel_h_heatmap(ax, data):
    """Panel h: Gene expression heatmap (12 genes x 8 samples)."""
    n_genes, n_samples = 12, 8
    genes = [f'{g}' for g in [
        'IL-2', 'IFN-γ', 'TNF-α', 'Granzyme B', 'Perforin',
        'PD-1', 'CTLA-4', 'TIM-3', 'LAG-3', 'FOXP3', 'IL-10', 'TGF-β'
    ]]
    samples = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4']

    mat = np.random.randn(n_genes, n_samples) * 0.5
    # Activation genes up in treatment
    mat[:5, 4:] += np.random.uniform(1.5, 3.0, (5, 4))
    # Exhaustion markers mixed
    mat[5:9, 4:] += np.random.uniform(-0.5, 1.0, (4, 4))
    # Treg genes down in treatment
    mat[9:, 4:] -= np.random.uniform(1.0, 2.0, (3, 4))

    sns.heatmap(
        mat, ax=ax, cmap='RdBu_r', center=0,
        xticklabels=samples, yticklabels=genes,
        linewidths=0.3, linecolor='white',
        cbar_kws={'shrink': 0.5, 'label': 'Z-score', 'pad': 0.02},
    )
    ax.tick_params(axis='y', rotation=0, labelsize=5.5)
    ax.tick_params(axis='x', rotation=45, labelsize=5.5)
    # Group labels
    ax.text(2, -0.8, 'Vehicle', ha='center', fontsize=5.5, transform=ax.transData)
    ax.text(6, -0.8, 'Drug A', ha='center', fontsize=5.5, transform=ax.transData)


def panel_i_violin(ax, data):
    """Panel i: Tumor volume violin plot (3 groups)."""
    groups = ['Vehicle', 'Drug A', 'Combo']
    data_groups = [
        np.random.lognormal(3.0, 0.5, 25),   # Vehicle - large tumors
        np.random.lognormal(2.3, 0.6, 25),   # Drug A - smaller
        np.random.lognormal(1.5, 0.8, 25),   # Combo - smallest
    ]
    colors = ['#999999', '#0072B2', '#D55E00']

    parts = ax.violinplot(data_groups, positions=[0, 1, 2],
                          showmeans=False, showextrema=False, showmedians=False)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.6)

    # Box plot inside
    bp = ax.boxplot(data_groups, positions=[0, 1, 2], widths=0.15,
                    patch_artist=True, showfliers=False,
                    medianprops={'color': 'black', 'linewidth': 1.5},
                    boxprops={'facecolor': 'white', 'linewidth': 0.8},
                    whiskerprops={'linewidth': 0.8},
                    capprops={'linewidth': 0.8})

    # Individual points
    for i, d in enumerate(data_groups):
        jitter = np.random.normal(0, 0.04, len(d))
        ax.scatter(np.full(len(d), i) + jitter, d, s=6, c='black', alpha=0.3, zorder=3)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(groups, fontsize=6)
    ax.set_ylabel('Tumor volume (mm³)')

    # Significance
    y_top = max(max(d) for d in data_groups) * 1.05
    for (i1, i2, sig), dy in zip([(0, 1, '*'), (0, 2, '***')], [0, y_top * 0.08]):
        y = y_top + dy
        ax.plot([i1, i1, i2, i2], [y, y + y_top * 0.02, y + y_top * 0.02, y], 'k-', lw=0.8)
        ax.text((i1 + i2) / 2, y + y_top * 0.03, sig, ha='center', fontsize=6)


def panel_j_western(ax, data):
    """Panel j: Simulated Western blot."""
    n_lanes = 6
    lane_labels = ['V1', 'V2', 'V3', 'A1', 'A2', 'A3']
    proteins = ['p-STAT3', 'STAT3', 'β-actin']

    img = np.ones((120, 200)) * 0.95  # light grey background

    for p_idx, (protein, base_y) in enumerate(zip(proteins, [15, 50, 85])):
        for lane_idx in range(n_lanes):
            x_center = 20 + lane_idx * 30
            # Band intensity
            if protein == 'β-actin':
                intensity = np.random.uniform(0.15, 0.25)
            elif protein == 'p-STAT3':
                intensity = np.random.uniform(0.1, 0.2) if lane_idx < 3 else np.random.uniform(0.4, 0.7)
            else:
                intensity = np.random.uniform(0.2, 0.35)

            # Draw band (gaussian blob)
            for dy in range(-8, 9):
                for dx in range(-10, 11):
                    y, x = base_y + dy, x_center + dx
                    if 0 <= y < 120 and 0 <= x < 200:
                        band = np.exp(-(dy ** 2 / 18 + dx ** 2 / 50))
                        img[y, x] -= intensity * band * (1 + np.random.normal(0, 0.05))

    img = img.clip(0, 1)
    ax.imshow(img, cmap='gray', vmin=0, vmax=1, aspect='auto')
    ax.set_axis_off()

    # Lane labels at bottom
    for i, label in enumerate(lane_labels):
        ax.text(20 + i * 30, 115, label, ha='center', va='top', fontsize=4.5)

    # Protein labels on left
    for protein, y in zip(proteins, [15, 50, 85]):
        ax.text(-5, y, protein, ha='right', va='center', fontsize=5, fontstyle='italic')

    # Group brackets
    ax.text(50, -5, 'Vehicle', ha='center', fontsize=5.5)
    ax.text(140, -5, 'Drug A', ha='center', fontsize=5.5)


# ============================================================
# Compose figure: 10 panels
# ============================================================

fig = Figure(
    journal='nature',
    size='double',           # 183 mm wide
    height_mm=230,           # tall figure for 10 panels
    layout="""
    aabbccdd
    aabbccdd
    eeffgggg
    hhhhiijj
    hhhhiijj
    """,
)

fig['a'] = PlotPanel(panel_a_microscopy_ctrl, data=None)
fig['b'] = PlotPanel(panel_b_microscopy_treat, data=None)
fig['c'] = PlotPanel(panel_c_flow_ctrl, data=None)
fig['d'] = PlotPanel(panel_d_flow_treat, data=None)
fig['e'] = PlotPanel(panel_e_quant_bar, data=None)
fig['f'] = PlotPanel(panel_f_quant_flow, data=None)
fig['g'] = PlotPanel(panel_g_survival, data=None)
fig['h'] = PlotPanel(panel_h_heatmap, data=None)
fig['i'] = PlotPanel(panel_i_violin, data=None)
fig['j'] = PlotPanel(panel_j_western, data=None)

# Validate
print("=== Validation ===")
fig.validate().print()

# Save
fig.save('output/nature_full.png', dpi=300)
fig.save('output/nature_full.pdf')

print(f"\n{fig.info()}")
print("\nSaved to output/nature_full.pdf and .png")
