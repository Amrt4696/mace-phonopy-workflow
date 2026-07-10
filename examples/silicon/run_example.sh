#!/usr/bin/env bash
# End-to-end toy example: Si phonon dispersion from a MACE foundation model.
# No local trained model needed -- mace_mp downloads a small pretrained model
# on first use. This only demonstrates the *mechanics* of the pipeline; the
# band path/settings here are illustrative, not curated for publication.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1. Generate displaced supercells with phonopy =="
phonopy -d --dim="2 2 2" -c POSCAR-unitcell

echo "== 2. Compute forces with a MACE foundation model and build FORCE_SETS =="
python ../../scripts/make_force_sets.py \
    --foundation small \
    --yaml phonopy_disp.yaml \
    --sposcar SPOSCAR \
    --output FORCE_SETS

echo "== 3. Compute phonon band structure =="
phonopy --dim="2 2 2" -c POSCAR-unitcell -p band.conf -s

echo "Done. band.pdf (and band.yaml) written to $(pwd)"
