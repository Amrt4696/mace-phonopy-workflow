#!/usr/bin/env python3

import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
import yaml
import time
import os

t0 = time.time()
print("Starting plot script...")

yaml_file = "band.yaml"
out_png = "bridgmanite_paper_style.png"
use_cm1 = True

print(f"Reading {yaml_file} ...")
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)
print(f"YAML loaded in {time.time()-t0:.2f} s")

phonon = data["phonon"]
segment_nqpoint = data["segment_nqpoint"]

print("Extracting distances and frequencies...")
distances = np.array([q["distance"] for q in phonon])
freqs = np.array([[b["frequency"] for b in q["band"]] for q in phonon])

if use_cm1:
    freqs = freqs * 33.35641
    ylabel = r"Frequency (cm$^{-1}$)"
else:
    ylabel = "Frequency (THz)"

nbands = freqs.shape[1]
print(f"Number of q-points = {len(distances)}")
print(f"Number of bands    = {nbands}")

tick_labels = [r"$Y$", r"$\Gamma$", r"$X$", r"$S$", r"$\Gamma$", r"$Z$"]

segments = []
tick_positions = []

idx = 0
for i, nq in enumerate(segment_nqpoint):
    start = idx
    end = idx + nq
    segments.append((start, end))

    d0 = distances[start]
    d1 = distances[end - 1]

    if i == 0:
        tick_positions.append(d0)
    tick_positions.append(d1)

    idx = end

print("Making figure...")
fig, ax = plt.subplots(figsize=(8.2, 5.8))

print("Plotting branches segment by segment...")
for start, end in segments:
    x = distances[start:end]
    y = freqs[start:end, :]
    for b in range(nbands):
        ax.plot(x, y[:, b], color="red", linewidth=1.0)

for x in tick_positions:
    ax.axvline(x, color="black", linewidth=0.8)

ax.axhline(0.0, color="black", linewidth=0.8)

ax.set_xlim(distances[0], distances[-1])
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, fontsize=13)
ax.set_ylabel(ylabel, fontsize=14)

ax.tick_params(axis="x", length=0)
ax.tick_params(axis="y", labelsize=12)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

print("Saving PNG...")
plt.tight_layout()
plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {out_png}")
print(f"Total time: {time.time()-t0:.2f} s")
