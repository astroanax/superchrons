#!/usr/bin/env bash
# SLURM template for XSHELLS pilots on madhava (single-node only: MaxNodes=1).
# Partitions: testq (1h, smoke tests) / shortq (7d) / mediumq (14d) / longq (30d).
# Nodes: 40 CPUs, ~169 GB each. Request --mem explicitly (1 GB/CPU default).
#SBATCH --job-name=xshells_W00
#SBATCH --partition=shortq
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --mem=150G
#SBATCH --time=7-00:00:00
#SBATCH --output=run_%j.log

set -euo pipefail
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
cd "$SLURM_SUBMIT_DIR"
mpirun -n 40 ~/superchrons/src/xshells/xsbig_mpi
