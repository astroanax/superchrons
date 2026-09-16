#!/bin/bash
# SMOKE TEST (<1 min compute): proves the Slurm launch path works end to end.
# Does NOT build or run science — just scheduler + module + srun + MPI.
#SBATCH --job-name=xs-smoke
#SBATCH --partition=testq
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --hint=nomultithread
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=smoke-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
echo "SMOKE node=$(hostname) cpus=$SLURM_CPUS_PER_TASK job=$SLURM_JOB_ID"
srun --cpu-bind=verbose,cores hostname
mpirun -n 1 hostname
ls /usr/local/include/fftw3.h && echo "SMOKE GO: scheduler+modules+srun+mpi+fftw all live"
