"""Mega Nature-style figure: 20 panels (A-T) mimicking a biosensor paper.

Demonstrates all FigCombo features:
- Dense 20-panel layout across 5 rows
- CompositePanel with (i)/(ii) sub-panels
- Inset bar charts inside curve panels
- Tight Nature-style spacing
- Mixed: schematics, curves, bar charts, SEM, photos, heatmaps
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import seaborn as sns

from figcombo import Figure, PlotPanel, CompositePanel


np.random.seed(42)
COLORS = ['#E69F00', '#56B4E9', '#009E73', '#D55E00', '#0072B2', '#CC79A7', '#F0E442']


# ================================================================
# Row 1: A(schematic) B(curves) C(curves+SEM inset) D(calibration) E(selectivity)
# ================================================================

def panel_a_schematic(ax, data):
    """Synthesis schematic (simplified block diagram)."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_axis_off()

    steps = [
        (1.2, 3, 'Substrate\nPreparation', '#56B4E9'),
        (3.7, 3, 'Polymer\nCoating', '#009E73'),
        (6.2, 3, 'Template\nImprinting', '#E69F00'),
        (8.7, 3, 'Template\nRemoval', '#D55E00'),
    ]
    for x, y, label, color in steps:
        rect = mpatches.FancyBboxPatch(
            (x - 0.9, y - 0.8), 1.8, 1.6,
            boxstyle='round,pad=0.1', facecolor=color, alpha=0.3,
            edgecolor=color, linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=5, fontweight='bold')

    # Arrows
    for x in [2.3, 4.8, 7.3]:
        ax.annotate('', xy=(x + 0.4, 3), xytext=(x, 3),
                     arrowprops=dict(arrowstyle='->', color='black', lw=1.2))

    ax.set_title('MIP Synthesis', fontsize=6, fontweight='bold', pad=2)


def panel_b_response_curves(ax, data):
    """Amperometric response curves at different concentrations."""
    time = np.linspace(0, 100, 200)
    concentrations = ['1 nM', '10 nM', '100 nM', '1 μM', '10 μM']
    baselines = [1.8, 1.6, 1.3, 0.9, 0.4]

    for i, (conc, base) in enumerate(zip(concentrations, baselines)):
        signal = base + 0.15 * np.exp(-time / 30) + np.random.normal(0, 0.01, len(time))
        ax.plot(time, signal, color=COLORS[i % len(COLORS)], linewidth=0.8, label=conc)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False, loc='upper right', ncol=1)
    ax.set_title('MIP', fontsize=6, pad=2)


def panel_c_nip_curves(ax, data):
    """NIP control curves (non-imprinted)."""
    time = np.linspace(0, 100, 200)
    concentrations = ['1 nM', '10 nM', '100 nM', '1 μM', '10 μM']

    for i, conc in enumerate(concentrations):
        signal = 0.15 + 0.02 * i + np.random.normal(0, 0.008, len(time))
        ax.plot(time, signal, color=COLORS[i % len(COLORS)], linewidth=0.8, label=conc)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False, loc='upper right')
    ax.set_title('NIP', fontsize=6, pad=2)


def panel_d_calibration(ax, data):
    """Calibration curve with log scale."""
    conc = np.logspace(0, 4, 20)
    signal_mip = 0.25 * np.log10(conc) + 0.3 + np.random.normal(0, 0.03, len(conc))
    signal_nip = 0.02 * np.log10(conc) + 0.05 + np.random.normal(0, 0.01, len(conc))

    ax.plot(conc, signal_mip, 'o-', color='#D55E00', markersize=3, linewidth=1, label='MIP')
    ax.plot(conc, signal_nip, 's--', color='#0072B2', markersize=3, linewidth=1, label='NIP')
    ax.set_xscale('log')
    ax.set_xlabel('Concentration (nM)')
    ax.set_ylabel('ΔI (μA)')
    ax.legend(fontsize=5, frameon=False)

    # Linear fit annotation
    ax.text(0.05, 0.95, 'y = 0.245 log(x) + 0.31\nR² = 0.993',
            transform=ax.transAxes, fontsize=4.5, va='top')


def panel_e_selectivity(ax, data):
    """Selectivity bar chart."""
    analytes = ['Target', 'Analog1', 'Analog2', 'Analog3', 'PBS']
    values = [4.2, 0.3, 0.25, 0.15, 0.05]
    colors_sel = ['#D55E00', '#56B4E9', '#009E73', '#E69F00', '#999999']

    bars = ax.bar(range(len(analytes)), values, color=colors_sel,
                  edgecolor='black', linewidth=0.5, width=0.6)
    ax.set_xticks(range(len(analytes)))
    ax.set_xticklabels(analytes, rotation=30, ha='right', fontsize=5)
    ax.set_ylabel('Current (μA)')
    ax.set_title('C = 1 μM', fontsize=5, pad=2)


# ================================================================
# Row 2: F(schematic) G(regen curves+inset) H(reuse+inset) I(stability) J(batch)
# ================================================================

def panel_f_workflow(ax, data):
    """Measurement workflow schematic."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_axis_off()

    steps = ['Measure', 'Regenerate', 'Re-measure']
    xs = [1.5, 5.0, 8.5]
    for x, step, color in zip(xs, steps, ['#0072B2', '#D55E00', '#009E73']):
        circle = mpatches.Circle((x, 2), 1.0, facecolor=color, alpha=0.25, edgecolor=color, lw=1.2)
        ax.add_patch(circle)
        ax.text(x, 2, step, ha='center', va='center', fontsize=5, fontweight='bold')

    ax.annotate('', xy=(3.5, 2), xytext=(2.8, 2),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.annotate('', xy=(7.0, 2), xytext=(6.3, 2),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))


def _inset_method_comparison(ax, data):
    """Inset: method comparison bar chart."""
    methods = ['CV', 'DPV', 'ECA']
    vals = [85, 110, 125]
    ax.bar(range(3), vals, color=['#56B4E9', '#009E73', '#E69F00'],
           edgecolor='black', linewidth=0.4, width=0.6)
    ax.set_xticks(range(3))
    ax.set_xticklabels(methods, fontsize=4)
    ax.set_ylabel('Time (s)', fontsize=4)
    ax.tick_params(labelsize=4)


def panel_g_regeneration(ax, data):
    """Regeneration curves (before/after)."""
    time = np.linspace(0, 100, 200)
    # PBS baseline
    ax.plot(time, np.ones_like(time) * 0.1 + np.random.normal(0, 0.005, len(time)),
            color='grey', linewidth=0.8, label='PBS')
    # Before regen
    ax.plot(time, 1.5 * np.exp(-time / 20) + 0.2 + np.random.normal(0, 0.01, len(time)),
            color='#D55E00', linewidth=0.8, label='Pre-regen')
    # After regen
    ax.plot(time, 0.15 + np.random.normal(0, 0.008, len(time)),
            '--', color='#0072B2', linewidth=0.8, label='Post-regen')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False)
    ax.set_title('C = 0.1 μM', fontsize=5, pad=2)


def _inset_reuse_bar(ax, data):
    """Inset: relative signal across reuse cycles."""
    cycles = range(1, 11)
    signals = [100, 99, 98, 97, 96, 95, 93, 92, 90, 88]
    ax.bar(cycles, signals, color='#009E73', edgecolor='black', linewidth=0.3, width=0.6)
    ax.set_xlabel('Reuse #', fontsize=4)
    ax.set_ylabel('Signal (%)', fontsize=4)
    ax.set_ylim(80, 105)
    ax.tick_params(labelsize=3.5)


def panel_h_reuse_curves(ax, data):
    """Reuse response curves overlaid."""
    time = np.linspace(0, 100, 200)
    for i in range(10):
        decay = (1.0 - i * 0.01)
        signal = decay * (1.2 * np.exp(-time / 25) + 0.2) + np.random.normal(0, 0.008, len(time))
        ax.plot(time, signal, linewidth=0.6, alpha=0.7)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.set_title('C = 0.1 μM', fontsize=5, pad=2)


def panel_i_stability(ax, data):
    """Long-term stability time series."""
    cycles = np.arange(1, 11)
    conc_1nm = np.ones(10) * 1.2 + np.random.normal(0, 0.03, 10)
    conc_1um = np.ones(10) * 0.3 + np.random.normal(0, 0.02, 10)
    ax.plot(cycles, conc_1nm, 'o-', color='#0072B2', markersize=3, linewidth=1, label='1 nM')
    ax.plot(cycles, conc_1um, 's-', color='#D55E00', markersize=3, linewidth=1, label='1 μM')
    ax.set_xlabel('Regeneration cycle')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False)
    ax.set_ylim(0, 1.5)


def panel_j_batch(ax, data):
    """Batch reproducibility."""
    batches = ['Batch 1', 'Batch 2', 'Batch 3']
    means = [0.55, 0.53, 0.56]
    sems = [0.03, 0.04, 0.03]
    colors_b = ['#E69F00', '#CC79A7', '#009E73']

    ax2 = ax.twinx()
    bars = ax.bar(range(3), means, yerr=sems, capsize=2,
                  color=colors_b, edgecolor='black', linewidth=0.5, width=0.5)
    ax.set_xticks(range(3))
    ax.set_xticklabels(batches, fontsize=5)
    ax.set_ylabel('Current (μA)')

    # Relative signal on right axis
    rel = [100, 96, 102]
    ax2.plot(range(3), rel, 'ko-', markersize=4, linewidth=1)
    ax2.set_ylabel('Relative (%)', fontsize=5)
    ax2.set_ylim(85, 115)
    ax2.tick_params(labelsize=5)


# ================================================================
# Row 3: K(device schematic, wide) L(stability time series) M(stability time series)
# ================================================================

def panel_k_device(ax, data):
    """Device schematic (wide panel)."""
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 5)
    ax.set_axis_off()

    # Simplified device diagram
    components = [
        (2.5, 2.5, 'Electrode\nSubstrate', '#56B4E9', 3.5, 2.5),
        (7.5, 2.5, 'MIP\nRecognition', '#E69F00', 3.5, 2.5),
        (12.5, 2.5, 'Signal\nTransduction', '#009E73', 3.5, 2.5),
        (17.5, 2.5, 'Wireless\nReadout', '#CC79A7', 3.5, 2.5),
    ]
    for x, y, label, color, w, h in components:
        rect = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle='round,pad=0.15', facecolor=color, alpha=0.2,
            edgecolor=color, linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=5.5, fontweight='bold')

    for x in [4.5, 9.5, 14.5]:
        ax.annotate('', xy=(x + 0.7, 2.5), xytext=(x, 2.5),
                     arrowprops=dict(arrowstyle='->', color='black', lw=1.5))


def panel_l_longterm(ax, data):
    """Long-term current stability (1 nM)."""
    time = np.linspace(0, 840, 100)
    signal = 1.25 + np.random.normal(0, 0.02, 100)
    signal[50:] = 1.23 + np.random.normal(0, 0.02, 50)
    ax.plot(time, signal, '-', color='#0072B2', linewidth=0.8)
    ax.axhline(1.25, color='grey', linewidth=0.5, linestyle='--')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.set_title('1 nM', fontsize=5, pad=2)
    ax.set_ylim(0.8, 1.5)


def panel_m_longterm_high(ax, data):
    """Long-term current stability (10 μM)."""
    time = np.linspace(0, 840, 100)
    signal = 0.2 + np.random.normal(0, 0.015, 100)
    ax.plot(time, signal, '-', color='#D55E00', linewidth=0.8)
    ax.axhline(0.2, color='grey', linewidth=0.5, linestyle='--')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.set_title('10 μM', fontsize=5, pad=2)
    ax.set_ylim(0, 0.5)


# ================================================================
# Row 4: N(photo) O(bending curves) P(bending bar) Q(SEM (i)(ii))
# ================================================================

def panel_n_photo(ax, data):
    """Device photo (simulated)."""
    img = np.zeros((100, 150, 3))
    # Blue "glove" background
    img[:, :, 2] = 0.5
    img[:, :, 0] = 0.1
    # White "device" rectangle in center
    img[20:80, 30:120, :] = 0.9
    # Some features on device
    for y in range(30, 70, 10):
        img[y:y + 5, 50:100, 1] = 0.4
        img[y:y + 5, 50:100, 0] = 0.2
    img = img.clip(0, 1) + np.random.normal(0, 0.02, img.shape)
    img = img.clip(0, 1)
    ax.imshow(img)
    ax.set_axis_off()


def panel_o_bending(ax, data):
    """Bending test response curves."""
    time = np.linspace(0, 100, 200)
    for i, (n, c) in enumerate(zip(['0×', '250×', '500×', '750×', '1000×'],
                                     COLORS[:5])):
        signal = 1.4 + np.random.normal(0, 0.01, len(time)) - i * 0.01
        ax.plot(time, signal, color=c, linewidth=0.7, label=n)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False, title='C = 0.1 μM', title_fontsize=4)


def panel_p_bending_bar(ax, data):
    """Bending cycle bar chart."""
    cycles = ['0×', '250×', '500×', '750×', '1000×']
    signals = [100, 99.5, 99.2, 98.8, 98.0]
    ax.bar(range(5), signals, color=COLORS[:5], edgecolor='black', linewidth=0.4, width=0.6)
    ax.set_xticks(range(5))
    ax.set_xticklabels(cycles, fontsize=4.5, rotation=30, ha='right')
    ax.set_ylabel('Relative signal (%)')
    ax.set_ylim(90, 105)


def sem_before(ax, data):
    """SEM image (i) - before."""
    img = np.random.normal(0.5, 0.15, (120, 160))
    # Add some spherical features
    for _ in range(30):
        cx, cy = np.random.randint(10, 110), np.random.randint(10, 150)
        r = np.random.randint(3, 12)
        yy, xx = np.ogrid[-cx:120 - cx, -cy:160 - cy]
        mask = xx ** 2 + yy ** 2 <= r ** 2
        img[mask] = np.random.uniform(0.6, 0.85)
    img = img.clip(0, 1)
    ax.imshow(img, cmap='gray')
    ax.set_axis_off()


def sem_after(ax, data):
    """SEM image (ii) - after."""
    img = np.random.normal(0.55, 0.12, (120, 160))
    for _ in range(50):
        cx, cy = np.random.randint(10, 110), np.random.randint(10, 150)
        r = np.random.randint(2, 8)
        yy, xx = np.ogrid[-cx:120 - cx, -cy:160 - cy]
        mask = xx ** 2 + yy ** 2 <= r ** 2
        img[mask] = np.random.uniform(0.7, 0.95)
    img = img.clip(0, 1)
    ax.imshow(img, cmap='gray')
    ax.set_axis_off()


# ================================================================
# Row 5: R(env stability (i)(ii)) S(sweat curves+inset) T(on-body+inset)
# ================================================================

def env_photos(ax, data):
    """Environmental stability photo (chips at different days)."""
    img = np.ones((60, 180, 3)) * 0.92
    days = [1, 5, 9, 13, 17, 21]
    for i, d in enumerate(days):
        x0 = 5 + i * 29
        img[10:50, x0:x0 + 22, :] = 0.7 + np.random.normal(0, 0.05, (40, 22, 3))
        ax.text(x0 + 11, 55, str(d), ha='center', fontsize=4, transform=ax.transData)
    img = img.clip(0, 1)
    ax.imshow(img)
    ax.set_axis_off()


def env_stability_line(ax, data):
    """Environmental stability over 21 days."""
    days = [1, 7, 14, 21]
    recovery = [100, 99, 97, 95]
    errors = [2, 3, 3, 4]
    ax.errorbar(days, recovery, yerr=errors, fmt='o-', color='black',
                markersize=4, capsize=3, linewidth=1)
    ax.set_xlabel('Days')
    ax.set_ylabel('Recovery (%)')
    ax.set_ylim(80, 110)
    ax.set_xticks(days)


def _inset_volume_bar(ax, data):
    """Inset: volume density bar."""
    vols = [0.5, 1, 2, 5, 10]
    sigs = [4.8, 4.5, 4.0, 3.2, 2.5]
    ax.bar(range(5), sigs, color='#56B4E9', edgecolor='black', linewidth=0.3, width=0.5)
    ax.set_xticks(range(5))
    ax.set_xticklabels([str(v) for v in vols], fontsize=3.5)
    ax.set_ylabel('Signal', fontsize=3.5)
    ax.set_xlabel('Vol (μL/min)', fontsize=3.5)
    ax.tick_params(labelsize=3.5)


def panel_s_sweat(ax, data):
    """Sweat sensing curves at different concentrations."""
    time = np.linspace(0, 100, 200)
    concs = ['0.1', '0.075', '0.05', '0.025']
    for i, c in enumerate(concs):
        signal = (4 - i * 0.8) * np.exp(-time / 40) + 1 + np.random.normal(0, 0.03, len(time))
        ax.plot(time, signal, linewidth=0.7, label=f'{c} μM')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.legend(fontsize=4, frameon=False, title='Concentration', title_fontsize=4)


def _inset_onbody_bar(ax, data):
    """Inset: on-body relative signals."""
    subjects = ['S1', 'S2', 'S3', 'S4', 'S5']
    sigs = [100, 95, 102, 98, 97]
    colors_s = ['#E69F00', '#56B4E9', '#009E73', '#D55E00', '#CC79A7']
    ax.bar(range(5), sigs, color=colors_s, edgecolor='black', linewidth=0.3, width=0.5)
    ax.set_xticks(range(5))
    ax.set_xticklabels(subjects, fontsize=3.5)
    ax.set_ylabel('Rel. (%)', fontsize=3.5)
    ax.set_ylim(85, 110)
    ax.tick_params(labelsize=3.5)


def panel_t_onbody(ax, data):
    """On-body measurement curves."""
    time = np.linspace(0, 100, 200)
    for i in range(5):
        signal = 0.8 + np.random.normal(0, 0.02, len(time))
        ax.plot(time, signal, linewidth=0.7, alpha=0.7)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (μA)')
    ax.set_title('C = 10 nM, n = 5', fontsize=5, pad=2)


# ================================================================
# Compose the full figure: 20 panels
# ================================================================

fig = Figure(
    journal='nature',
    size='double',           # 183 mm
    height_mm=245,           # near max (247mm)
    layout="""
    AABBCCDDEE
    FFFFGGHHJJ
    KKKKKKLLMM
    NNOOPPQQqq
    RRrrSSSSTT
    """,
    font_size=6,
)

# Row 1
fig['A'] = PlotPanel(panel_a_schematic, data=None)
fig['B'] = PlotPanel(panel_b_response_curves, data=None)
fig['C'] = PlotPanel(panel_c_nip_curves, data=None)
fig['D'] = PlotPanel(panel_d_calibration, data=None)
fig['E'] = PlotPanel(panel_e_selectivity, data=None)

# Row 2
fig['F'] = PlotPanel(panel_f_workflow, data=None)

# G with inset bar chart
panel_g = PlotPanel(panel_g_regeneration, data=None)
panel_g.add_inset(_inset_method_comparison, bounds=(0.55, 0.55, 0.4, 0.4), data=None)
fig['G'] = panel_g

# H with inset reuse bar
panel_h = PlotPanel(panel_h_reuse_curves, data=None)
panel_h.add_inset(_inset_reuse_bar, bounds=(0.55, 0.55, 0.4, 0.4), data=None)
fig['H'] = panel_h

# I and J removed (layout uses I position for something else)
# Actually, in our layout we have F(4 cols), G(2), H(2), J(2)
fig['J'] = PlotPanel(panel_j_batch, data=None)

# Row 3: K(wide), L, M
fig['K'] = PlotPanel(panel_k_device, data=None)
fig['L'] = PlotPanel(panel_l_longterm, data=None)
fig['M'] = PlotPanel(panel_m_longterm_high, data=None)

# Row 4: N(photo) O(bending) P(bar) Q(SEM composite (i)(ii))
fig['N'] = PlotPanel(panel_n_photo, data=None)
fig['O'] = PlotPanel(panel_o_bending, data=None)
fig['P'] = PlotPanel(panel_p_bending_bar, data=None)

# Q: CompositePanel with (i) and (ii) SEM images
q_panel = CompositePanel(1, 2, sub_labels=['(i)', '(ii)'])
q_panel[0] = PlotPanel(sem_before, data=None)
q_panel[1] = PlotPanel(sem_after, data=None)
fig['Q'] = q_panel

# Row 5: R(composite (i)(ii)), S(curves+inset), T(on-body+inset)
# R: CompositePanel with photos and line chart
r_panel = CompositePanel(1, 2, sub_labels=['(i)', '(ii)'])
r_panel[0] = PlotPanel(env_photos, data=None)
r_panel[1] = PlotPanel(env_stability_line, data=None)
fig['R'] = r_panel

# S with inset
panel_s = PlotPanel(panel_s_sweat, data=None)
panel_s.add_inset(_inset_volume_bar, bounds=(0.58, 0.55, 0.38, 0.4), data=None)
fig['S'] = panel_s

# T with inset
panel_t = PlotPanel(panel_t_onbody, data=None)
panel_t.add_inset(_inset_onbody_bar, bounds=(0.55, 0.55, 0.4, 0.4), data=None)
fig['T'] = panel_t

# --- Validate & Save ---
print("=== Validation ===")
fig.validate().print()

fig.save('output/nature_mega.png', dpi=300)
fig.save('output/nature_mega.pdf')

print(f"\n{fig.info()}")
print("\nSaved to output/nature_mega.pdf and .png")
