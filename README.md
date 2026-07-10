# MACE + Phonopy Phonon Workflow

Compute phonon dispersions using forces from a trained [MACE](https://github.com/ACEsuit/mace) potential instead of DFT, driven through [phonopy](https://phonopy.github.io/phonopy/).

phonopy generates displaced supercells -> MACE computes forces on them -> phonopy builds `FORCE_SETS` and the phonon dispersion.

## Setup

No conda needed:

```bash
git clone https://github.com/Amrt4696/mace-phonopy-workflow.git
cd mace-phonopy-workflow
./setup.sh
source .venv/bin/activate
```

Or with conda, if you prefer it:

```bash
conda env create -f environment.yml
conda activate mace-phonopy
```

## Real example: MgSiO3 bridgmanite

A real, result -- 2x2x2 supercell, polar material so it includes the LO-TO splitting correction (`BORN` + `--nac`). Everything is already committed (inputs, forces, plots), so you can just look at it or reproduce it:

```bash
cd examples/bridgmanite-MgSiO3
phonopy -d --dim="2 2 2" -c POSCAR
python ../../scripts/make_force_sets.py --model ../../models/mace-mpa-0-medium.model --yaml phonopy_disp.yaml --sposcar SPOSCAR --output FORCE_SETS
phonopy -s band.conf -c POSCAR --nac
python plot.py
```

More detail in `examples/bridgmanite-MgSiO3/README.md`.

## Using your own model

Drop your `.model` file in `models/` (or fetch it with `models/download_model.sh` if it's hosted elsewhere), then:

```bash
phonopy -d --dim="a b c" -c POSCAR-unitcell
python scripts/make_force_sets.py --model models/your_model.model --yaml phonopy_disp.yaml --sposcar SPOSCAR --output FORCE_SETS
phonopy -s band.conf -c POSCAR-unitcell
```

`python scripts/make_force_sets.py --help` for all the options (foundation models, GPU, dtype, etc).
