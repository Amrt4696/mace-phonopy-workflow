# MgSiO3 Bridgmanite (Pbnm) — full reference example

Real, paper-referenced phonon dispersion of MgSiO3 bridgmanite (perovskite, space group Pbnm), computed with forces from a MACE potential instead of DFT. Unlike `examples/silicon`, this example ships its **generated artifacts committed** (`POSCAR-001..017`, `SPOSCAR`, `FORCE_SETS`, `band.yaml`, the paper-style plot, and `compare-dft/`) so the exact result is inspectable/diffable without rerunning anything.

Bridgmanite is **polar**, so this is also the repo's example of applying the non-analytical term correction (NAC / LO-TO splitting) via a `BORN` file — that part is easy to silently get wrong (BORN alone does nothing; you need `--nac` or `NAC = .TRUE.`), so it's called out explicitly below.

## Files

| File | What it is |
|---|---|
| `POSCAR` | Conventional 20-atom Pbnm unit cell (Mg4Si4O12) |
| `BORN` | Born effective charges + dielectric tensor, for NAC/LO-TO splitting |
| `POSCAR-001` .. `POSCAR-017` | phonopy's symmetry-irreducible displaced 2x2x2 supercells |
| `SPOSCAR` | Undisplaced 2x2x2 supercell (160 atoms) |
| `phonopy_disp.yaml`, `phonopy_symcells.yaml` | phonopy displacement metadata |
| `FORCE_SETS` | MACE-computed forces on each displaced supercell, in phonopy Type-1 format |
| `phonopy.yaml` | phonopy run metadata |
| `band.conf` | Band path / NAC settings |
| `band.yaml` | Computed phonon band structure |
| `plot.py`, `bridgmanite_paper_style.png` | Plotting script and the resulting figure |
| `compare-dft/` | DFT reference phonon data, for validating the MACE result |

## Reproducing from scratch

```bash
cd examples/bridgmanite-MgSiO3

# 1. The trained potential ships in the repo directly (models/mace-mpa-0-medium.model,
#    ~76MB, under GitHub's 100MB limit) -- no download step needed.

# 2. Generate the 2x2x2 displaced supercells
phonopy -d --dim="2 2 2" -c POSCAR
# -> creates POSCAR-001..017, SPOSCAR, phonopy_disp.yaml

# 3. Compute forces with MACE and build FORCE_SETS
python ../../scripts/make_force_sets.py \
    --model ../../models/mace-mpa-0-medium.model \
    --yaml phonopy_disp.yaml \
    --sposcar SPOSCAR \
    --output FORCE_SETS

# 4. Phonon dispersion, WITH the non-analytical (LO-TO) correction.
#    BORN must sit in this directory. --nac is required for BORN to actually
#    be used -- without it phonopy silently ignores BORN and you'd get the
#    analytical (un-split) dispersion instead.
phonopy -s band.conf -c POSCAR --nac

# 5. Plot
python plot.py
```

This should reproduce `band.yaml` / `bridgmanite_paper_style.png` already committed here (small numerical differences are expected if you're on a different MACE/PyTorch version — see repo root `environment.yml` for the versions this was validated against).

## Notes

- `--dim="2 2 2"` here matches `DIM = 2 2 2` in `band.conf` — both must agree, since `band.conf`'s `DIM` tells phonopy how to fold `FORCE_SETS` back into force constants for the unit cell in `POSCAR`.
- `FC_SYMMETRY = .TRUE.` in `band.conf` symmetrizes the force constants — helpful for cleaning up small numerical noise from `FORCE_SETS`, especially useful with ML potentials.
- If you retrain your own bridgmanite (or other perovskite) potential and want to redo this: BORN charges/dielectric tensor still need to come from a DFT calculation (e.g. VASP `LEPSILON`/`LCALCEPS`) — MACE forces don't give you Born effective charges.
