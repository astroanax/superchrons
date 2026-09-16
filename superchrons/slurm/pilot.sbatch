#!/bin/bash
# Production-pilot template (shortq example, single node). Paper main-29 §F7.
# SCIENCE MODE (case_status=validated): full gate — complete manifest,
# matching checksums, calibration_status=calibrated, acceptance logs with
# PASS markers, verified checkpoints, par/solver restart agreement.
# Run dir must be prepared with tools/prepare_run.sh. RESTART comes from the
# preparer; the par-file restart flag must already agree (preflight enforces).
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
source ./env.sh   # staged by prepare_run.sh: modules + MKL path + OMP binding
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
MANIFEST="${MANIFEST:-MANIFEST.md}"
PREFLIGHT="${PREFLIGHT:-/home/rehan/workspaces/ceas-iisc/superchrons/slurm/preflight.py}"
if [[ "${RESTART:-0}" == "1" ]]; then RFLAG="--expect-restart"; else RFLAG="--no-restart"; fi
python3 "$PREFLIGHT" --mode science --manifest "$MANIFEST" \
  --par ./xshells.par --binary ./xsbig_hyb "$RFLAG" --outdir ./output \
  || exit 2
srun --cpu-bind=verbose,cores ./xsbig_hyb
