#!/bin/bash
# 45-minute hybrid benchmark, testq, single node. Paper main-29 §F7 template.
# Provisional 80000M allowance, NOT a measured requirement. Submit from a
# dedicated prepared run dir holding xsbig_hyb + complete validated inputs.
# Different jobs must not share mutable output/restart files. Configure the
# input to terminate well inside the allocation — walltime is not a checkpoint.
#SBATCH --job-name=xs-bench
#SBATCH --partition=testq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=20
#SBATCH --hint=nomultithread
#SBATCH --mem=80000M
#SBATCH --time=00:45:00
#SBATCH --output=bench-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
# Load the site-tested compiler/MPI modules here; they must match the build.
# module load gnu8/8.3.0 openmpi3/3.1.4
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OMP_PLACES=cores
export OMP_PROC_BIND=close
test -x ./xsbig_hyb
test -f xshells.par
# If the site MPI needs an explicit Slurm plugin or site-supported mpirun
# launch instead of srun, use that tested method. Do not guess a plugin name.
srun --cpu-bind=verbose,cores ./xsbig_hyb
