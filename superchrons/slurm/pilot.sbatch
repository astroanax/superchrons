#!/bin/bash
# Production-pilot template (shortq example, single node). Paper main-29 §F7.
# Second layout candidate: --ntasks-per-node=4 --cpus-per-task=10.
# Compare 2x20 vs 4x10 first; verify socket placement, thread binding, actual
# CPU use; neither is guaranteed optimal. Start without hyperthread
# oversubscription. Multinode (mediumq 2-3 nodes, longq 4-8) only if the case
# size or measured throughput justifies it; hold physics/resolution/accuracy/
# output frequency fixed during strong-scaling comparisons.
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
# module load gnu8/8.3.0 openmpi3/3.1.4   # must match the recorded build
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OMP_PLACES=cores
export OMP_PROC_BIND=close
test -x ./xsbig_hyb
test -f xshells.par
srun --cpu-bind=verbose,cores ./xsbig_hyb
