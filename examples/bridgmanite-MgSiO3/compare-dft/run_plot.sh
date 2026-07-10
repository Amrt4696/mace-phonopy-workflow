#!/bin/bash
#SBATCH -J mace_fc3
#SBATCH -D ./
#SBATCH -o ./%x.%j.%N.out
#SBATCH -e ./%x.%j.%N.err
#SBATCH --get-user-env
#SBATCH --export=NONE
#SBATCH --clusters=serial
#SBATCH --partition=serial_std
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --time=02:00:00

module load slurm_setup
module load python/3.10.12-extended
source ~/packages/mace-venv-py310/bin/activate

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

python plot_compare.py > job_status.log 2>&1

