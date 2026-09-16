#!/bin/bash
# 45-minute hybrid benchmark, testq, single node. Paper main-29 §F7 template.
# BENCHMARK MODE: preflight checks binary+par presence only (no manifest,
# no acceptance logs). Never reuse this script for science runs.
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
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OMP_PLACES=cores
export OMP_PROC_BIND=close
# Manifest path is required as an argument even in bench mode so the run is
# traceable; acceptance fields are not enforced here.
MANIFEST="${MANIFEST:-MANIFEST.md}"
python3 slurm/preflight.py --mode bench --manifest "$MANIFEST" \
  --par ./xshells.par --binary ./xsbig_hyb --no-restart --outdir ./output \
  || exit 2
# If the site MPI needs an explicit Slurm plugin or site-supported mpirun
# launch instead of srun, use that tested method. Do not guess a plugin name.
srun --cpu-bind=verbose,cores ./xsbig_hyb
