#!/bin/bash
# Production-pilot template (shortq example, single node). Paper main-29 §F7.
# SCIENCE MODE: refuses launch unless the manifest is complete, checksums
# match, acceptance logs exist, the par fragment has no TODO markers, and the
# output dir state matches the restart expectation. Set RESTART=1 for a
# continuation run, RESTART=0 for a fresh run.
#SBATCH --job-name=xs-pilot
#SBATCH --partition=shortq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=20
#SBATCH --hint=nomultithread
#SBATCH --mem=80000M
#SBATCH --time=7-00:00:00
#SBATCH --output=run_%j.log
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OMP_PLACES=cores
export OMP_PROC_BIND=close
MANIFEST="${MANIFEST:-MANIFEST.md}"
if [[ "${RESTART:-0}" == "1" ]]; then RFLAG="--expect-restart"; else RFLAG="--no-restart"; fi
python3 slurm/preflight.py --mode science --manifest "$MANIFEST" \
  --par ./xshells.par --binary ./xsbig_hyb "$RFLAG" --outdir ./output \
  || exit 2
srun --cpu-bind=verbose,cores ./xsbig_hyb
