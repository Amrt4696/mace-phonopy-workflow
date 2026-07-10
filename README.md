# MACE + Phonopy Phonon Dispersion Workflow

Compute phonon dispersions using forces from a trained [MACE](https://github.com/ACEsuit/mace) machine-learning interatomic potential instead of DFT single-point calculations, driven through [phonopy](https://phonopy.github.io/phonopy/).

Pipeline:

1. **phonopy** generates displaced supercells from your unit cell (`phonopy -d`).
2. **MACE** evaluates forces on each displaced supercell (`scripts/make_force_sets.py`).
3. **phonopy** assembles those forces into `FORCE_SETS` and computes the phonon dispersion.

## Install

```bash
git clone https://github.com/<your-username>/mace-phonopy-workflow.git
cd mace-phonopy-workflow
conda env create -f environment.yml
conda activate mace-phonopy
```

GPU users: install a CUDA build of PyTorch first following [pytorch.org/get-started](https://pytorch.org/get-started/locally/), then create the environment — `mace-torch` will use whatever PyTorch is already installed.

## Quick start — toy example (no model training/download required)

This runs the full pipeline on bulk silicon using a MACE-MP pretrained "foundation" model, which downloads automatically on first use. It exists to prove the pipeline works on your machine, not as a physically curated phonon result.

```bash
cd examples/silicon
./run_example.sh
```

This runs, in order: `phonopy -d` to make displaced supercells, `make_force_sets.py --foundation small` to get `FORCE_SETS`, then `phonopy --band` to produce `band.yaml` / `band.pdf`.

## Full reference example — MgSiO3 bridgmanite

`examples/bridgmanite-MgSiO3/` is a real, paper-referenced result (not a toy): a 2x2x2-supercell phonon dispersion of Pbnm bridgmanite, forces from a self-trained MACE potential, with the non-analytical (LO-TO splitting) correction via a `BORN` file since the material is polar. All generated artifacts (`FORCE_SETS`, `band.yaml`, the paper-style plot, DFT comparison data) are committed as-is so the result is inspectable without rerunning anything — see `examples/bridgmanite-MgSiO3/README.md` for the exact commands and how to reproduce it.

## Using your own trained MACE model

1. Get your model file. Either:
   - `bash models/download_model.sh` after editing the URL in that script to point at wherever you've hosted the model (Zenodo/HuggingFace — model files are usually too large to commit to git directly), or
   - copy your own `.model` file into `models/`.
2. In a working directory, generate displacements for your structure:
   ```bash
   phonopy -d --dim="2 2 2" -c POSCAR-unitcell
   ```
   This produces `POSCAR-001`, `POSCAR-002`, ..., `SPOSCAR`, and `phonopy_disp.yaml`.
3. Compute forces and build `FORCE_SETS`:
   ```bash
   python /path/to/mace-phonopy-workflow/scripts/make_force_sets.py \
       --model /path/to/models/your_model.model \
       --yaml phonopy_disp.yaml \
       --sposcar SPOSCAR \
       --output FORCE_SETS
   ```
4. Compute the dispersion:
   ```bash
   phonopy --dim="2 2 2" -c POSCAR-unitcell -p band.conf -s
   ```
   (write your own `band.conf` — see `examples/silicon/band.conf` for the format.)

### `make_force_sets.py` options

| Flag | Meaning |
|---|---|
| `--model PATH` | Local `.model` file (mutually exclusive with `--foundation`) |
| `--foundation {small,medium,large}` | Use a pretrained MACE-MP foundation model instead |
| `--yaml` | phonopy displacement YAML (default `phonopy_disp.yaml`) |
| `--sposcar` | Reference undisplaced supercell (default `SPOSCAR`) |
| `--disp-glob` | Glob for displaced supercell files (default `POSCAR-*`) |
| `--output` | Output path (default `FORCE_SETS`) |
| `--device` | `cpu` or `cuda` |
| `--dtype` | `float32` or `float64` (default, recommended for phonons) |
| `--no-subtract-residual` | Skip subtracting SPOSCAR's own residual forces from each result |

Run `python scripts/make_force_sets.py --help` for the full list.

## Repo layout

```
scripts/make_force_sets.py       # forces (MACE) -> phonopy FORCE_SETS
examples/silicon/                # toy end-to-end example, foundation model, no training needed
examples/bridgmanite-MgSiO3/     # full reference example (paper result), incl. polar/NAC handling
models/download_model.sh         # fetches the trained potential (edit the URL first)
environment.yml                  # conda environment
```

## Notes / caveats

- `make_force_sets.py` assumes a standard **Type-1** phonopy displacement dataset (one displaced atom per supercell), i.e. what `phonopy -d` produces by default. It is not set up for Type-2 (all-atoms-displaced-per-supercell) datasets.
- The script checks each displaced supercell against `phonopy_disp.yaml` (atom index, displacement vector) before using it, and raises an error on mismatch rather than silently writing bad forces.
- `--dtype float64` is recommended for phonon work — small numerical noise in forces shows up directly as artifacts (e.g. imaginary frequencies) in the dispersion.
- TODO (repo owner): add the Zenodo/HuggingFace link for the trained model in `models/download_model.sh`, and update `examples/` with your real structure(s) if you want more than the silicon toy case.

## License

MIT — see [LICENSE](LICENSE).
