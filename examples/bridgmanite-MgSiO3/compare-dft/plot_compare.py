#!/usr/bin/env python3
"""
Compare phonon band structures from two band.yaml files (e.g. DFT vs MACE).
Y-axis: energy in meV   (1 THz = 4.13567 meV)
Usage:  python plot_compare.py
Output: phonon_compare.png
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import yaml
import sys
import os

# ── User settings ────────────────────────────────────────────────────────────
YAML_A      = "band_dft.yaml"
YAML_B      = "band_mace.yaml"
LABEL_A     = "DFT"
LABEL_B     = "MACE"
COLOR_A     = "#1f77b4"   # blue
COLOR_B     = "#d62728"   # red
ALPHA_A     = 0.85
ALPHA_B     = 0.75
LW          = 0.55        # thin lines for dense band structures
OUT_PNG     = "phonon_compare.png"
DPI         = 250

# High-symmetry point labels (edit to match your path)
TICK_LABELS = [r"$Y$", r"$\Gamma$", r"$X$", r"$S$", r"$\Gamma$", r"$Z$"]

# Conversion: THz → meV
THZ2MEV = 4.13567
# ─────────────────────────────────────────────────────────────────────────────


def load_band(yaml_file):
    """Return distances (1-D), freqs_meV (2-D: nq × nbands), tick_positions."""
    if not os.path.isfile(yaml_file):
        sys.exit(f"ERROR: '{yaml_file}' not found.")
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    phonon          = data["phonon"]
    segment_nqpoint = data["segment_nqpoint"]

    distances = np.array([q["distance"] for q in phonon])
    freqs_thz = np.array([[b["frequency"] for b in q["band"]] for q in phonon])
    freqs_mev = freqs_thz * THZ2MEV

    tick_positions = []
    idx = 0
    for i, nq in enumerate(segment_nqpoint):
        start = idx
        end   = idx + nq
        if i == 0:
            tick_positions.append(distances[start])
        tick_positions.append(distances[end - 1])
        idx = end

    return distances, freqs_mev, tick_positions


def plot_bands(ax, distances, freqs, color, alpha, lw, label):
    """Plot all bands; attach label only to the first line for the legend."""
    nbands = freqs.shape[1]
    for b in range(nbands):
        ax.plot(
            distances, freqs[:, b],
            color=color, linewidth=lw, alpha=alpha,
            label=label if b == 0 else "_nolegend_",
            rasterized=True,   # keeps PDF/SVG file sizes small
        )


# ── Load ─────────────────────────────────────────────────────────────────────
print(f"Loading {YAML_A} …")
dist_a, freqs_a, ticks_a = load_band(YAML_A)
print(f"Loading {YAML_B} …")
dist_b, freqs_b, ticks_b = load_band(YAML_B)

# Sanity check: same number of q-points & bands
if dist_a.shape != dist_b.shape:
    print("WARNING: q-point count differs between the two files.")
if freqs_a.shape[1] != freqs_b.shape[1]:
    print(f"WARNING: band count differs ({freqs_a.shape[1]} vs {freqs_b.shape[1]}).")

tick_positions = ticks_a   # use DFT grid as reference

# ── Figure ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.5, 5.2))

# Plot DFT first (behind), then MACE on top
plot_bands(ax, dist_a, freqs_a, color=COLOR_A, alpha=ALPHA_A, lw=LW, label=LABEL_A)
plot_bands(ax, dist_b, freqs_b, color=COLOR_B, alpha=ALPHA_B, lw=LW, label=LABEL_B)

# ── Zero line & segment dividers ─────────────────────────────────────────────
ax.axhline(0.0, color="black", linewidth=0.8, zorder=3)
for x in tick_positions:
    ax.axvline(x, color="black", linewidth=0.7, zorder=3)

# ── Axes formatting ───────────────────────────────────────────────────────────
ax.set_xlim(dist_a[0], dist_a[-1])
ax.set_xticks(tick_positions)
ax.set_xticklabels(TICK_LABELS, fontsize=13)
ax.tick_params(axis="x", length=0, pad=6)

ax.set_ylabel(r"Energy (meV)", fontsize=13)
ax.tick_params(axis="y", labelsize=11)
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

# Clean spine style
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_linewidth(0.8)
ax.spines["left"].set_linewidth(0.8)

# ── Legend ───────────────────────────────────────────────────────────────────
legend = ax.legend(
    frameon=True,
    framealpha=0.9,
    edgecolor="0.75",
    fontsize=11,
    loc="upper right",
    handlelength=1.8,
    handleheight=0.8,
)
# Make legend lines thicker so they're visible
for handle in legend.legend_handles:
    handle.set_linewidth(2.0)
    handle.set_alpha(1.0)

# ── Save ─────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
plt.savefig(OUT_PNG, dpi=DPI, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {OUT_PNG}")
