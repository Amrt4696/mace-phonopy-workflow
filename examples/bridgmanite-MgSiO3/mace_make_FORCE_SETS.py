import os
import re
import glob
import yaml
import numpy as np
import torch

from ase.io import read
from mace.calculators import MACECalculator

# =========================
# User settings
# =========================
model_path = "/dss/dsshome1/00/ra45nuj/amrt/VASP_test/phono3py/bridgmaniteQHA/training_all/1_small_light_allgpa/training/bridgmanite_allgpa_smalllight_v1_compiled.model"
yaml_file = "phonopy_disp.yaml"
sposcar_file = "SPOSCAR"
disp_pattern = "POSCAR-*"
output_file = "FORCE_SETS"

device = "cpu"
default_dtype = "float64"

subtract_residual_forces = True

cell_tol = 1e-8
disp_tol = 1e-6   # Angstrom
# =========================


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def load_phonopy_displacements(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    if "displacements" not in data:
        raise RuntimeError(f"'{yaml_path}' does not contain 'displacements'.")

    disp_data = data["displacements"]

    if not isinstance(disp_data, list) or len(disp_data) == 0:
        raise RuntimeError(f"No displacements found in '{yaml_path}'.")

    parsed = []

    for i, entry in enumerate(disp_data, start=1):
        if isinstance(entry, dict) and "atom" in entry and "displacement" in entry:
            atom = int(entry["atom"])
            disp = np.array(entry["displacement"], dtype=float)
            parsed.append({
                "index": i,
                "atom": atom,
                "displacement": disp,
            })
        else:
            raise RuntimeError(
                "This phonopy_disp.yaml is not the standard single-displacement "
                "dataset from 'phonopy -d'. Type-1 FORCE_SETS is not suitable."
            )

    return parsed


def find_disp_files(pattern, expected_n):
    files = sorted(glob.glob(pattern), key=natural_key)
    if len(files) != expected_n:
        raise RuntimeError(
            f"Expected {expected_n} displaced supercell files from YAML, "
            f"but found {len(files)} files matching '{pattern}'."
        )
    return files


def check_structure_compatibility(atoms_ref, atoms, fname):
    if len(atoms) != len(atoms_ref):
        raise RuntimeError(f"{fname}: natom mismatch ({len(atoms)} != {len(atoms_ref)})")

    if atoms.get_chemical_symbols() != atoms_ref.get_chemical_symbols():
        raise RuntimeError(f"{fname}: chemical symbol order mismatch with SPOSCAR")

    if not np.allclose(atoms.cell.array, atoms_ref.cell.array, atol=cell_tol):
        raise RuntimeError(f"{fname}: cell mismatch with SPOSCAR")


def get_actual_displacement(atoms_ref, atoms):
    s_ref = atoms_ref.get_scaled_positions(wrap=True)
    s_new = atoms.get_scaled_positions(wrap=True)

    ds = s_new - s_ref
    ds -= np.round(ds)
    dR = ds @ atoms_ref.cell.array
    norms = np.linalg.norm(dR, axis=1)

    moved = np.where(norms > disp_tol)[0]
    return dR, norms, moved


def main():
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing model file: {model_path}")
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"Missing {yaml_file}")
    if not os.path.exists(sposcar_file):
        raise FileNotFoundError(f"Missing {sposcar_file}")

    torch.set_num_threads(int(os.environ.get("SLURM_CPUS_PER_TASK", "1")))

    print("Loading MACE model...")
    calc = MACECalculator(
        model_paths=model_path,
        default_dtype=default_dtype,
        device=device,
    )

    print(f"Reading reference supercell: {sposcar_file}")
    atoms_ref = read(sposcar_file)
    natom = len(atoms_ref)

    print(f"Reading displacement dataset from: {yaml_file}")
    disp_entries = load_phonopy_displacements(yaml_file)
    ndisp = len(disp_entries)

    disp_files = find_disp_files(disp_pattern, ndisp)

    print(f"Found natom = {natom}")
    print(f"Found ndisplacements = {ndisp}")

    residual_forces = None
    if subtract_residual_forces:
        print("Calculating residual forces on SPOSCAR...")
        atoms_ref.calc = calc
        residual_forces = atoms_ref.get_forces()
        max_res = np.abs(residual_forces).max()
        print(f"Max |residual force| on SPOSCAR = {max_res:.6e} eV/Ang")

    with open(output_file, "w") as fout:
        fout.write(f"{natom}\n")
        fout.write(f"{ndisp}\n\n")

        for i, (entry, disp_file) in enumerate(zip(disp_entries, disp_files), start=1):
            atoms = read(disp_file)
            check_structure_compatibility(atoms_ref, atoms, disp_file)

            yaml_atom = entry["atom"]
            yaml_disp = entry["displacement"]

            dR, norms, moved = get_actual_displacement(atoms_ref, atoms)

            if len(moved) == 0:
                raise RuntimeError(f"{disp_file}: no displacement detected relative to SPOSCAR")

            if len(moved) != 1:
                moved_1based = [m + 1 for m in moved]
                raise RuntimeError(
                    f"{disp_file}: detected {len(moved)} displaced atoms {moved_1based}. "
                    "Type-1 FORCE_SETS expects one displaced atom per supercell."
                )

            actual_atom = moved[0] + 1
            actual_disp = dR[moved[0]]

            if actual_atom != yaml_atom:
                raise RuntimeError(
                    f"{disp_file}: displaced atom mismatch. "
                    f"YAML says atom {yaml_atom}, structure comparison says atom {actual_atom}"
                )

            if not np.allclose(actual_disp, yaml_disp, atol=5e-6):
                raise RuntimeError(
                    f"{disp_file}: displacement mismatch.\n"
                    f"YAML  : {yaml_disp}\n"
                    f"Actual: {actual_disp}"
                )

            atoms.calc = calc
            forces = atoms.get_forces()

            if residual_forces is not None:
                forces = forces - residual_forces

            fout.write(f"{yaml_atom}\n")
            fout.write(
                f"{yaml_disp[0]:22.16f} {yaml_disp[1]:22.16f} {yaml_disp[2]:22.16f}\n"
            )
            for fx, fy, fz in forces:
                fout.write(f"{fx:22.16f} {fy:22.16f} {fz:22.16f}\n")

            if i != ndisp:
                fout.write("\n")

            print(
                f"[{i}/{ndisp}] OK  {disp_file}  atom={yaml_atom}  "
                f"disp=({yaml_disp[0]:.6f}, {yaml_disp[1]:.6f}, {yaml_disp[2]:.6f})"
            )

    print(f"\nDone. Wrote {output_file}")


if __name__ == "__main__":
    main()
