#!/bin/bash
# 45-minute hybrid benchmark, testq, single node. Paper main-29 §F7 template.
# BENCHMARK MODE (case_status=benchmark): preflight checks par schema +
# binary presence/checksum; no acceptance logs. Never reuse for science runs.
# Run dir must be prepared with tools/prepare_run.sh (self-contained: binary,
# input, env.sh staged; preflight resolved via absolute path). RESTART is set
# by the preparer, not hand-edited here.
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
source ./env.sh   # staged by prepare_run.sh: modules + MKL path + OMP binding
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
MANIFEST="${MANIFEST:-MANIFEST.md}"
PREFLIGHT="${PREFLIGHT:-/home/rehan/workspaces/ceas-iisc/superchrons/slurm/preflight.py}"
if [[ "${RESTART:-0}" == "1" ]]; then RFLAG="--expect-restart"; else RFLAG="--no-restart"; fi
python3 "$PREFLIGHT" --mode bench --manifest "$MANIFEST" \
  --par ./xshells.par --binary ./xsbig_hyb "$RFLAG" --outdir ./output \
  || exit 2
# If the site MPI needs an explicit Slurm plugin or site-supported mpirun
# launch instead of srun, use that tested method. Do not guess a plugin name.
srun --cpu-bind=verbose,cores ./xsbig_hyb
