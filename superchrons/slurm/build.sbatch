#!/bin/bash
# Build allocation for SHTns + XSHELLS (fix §4). Submit from login; the compile
# itself runs on the node with allocation-derived worker counts. Sources are
# pinned and staged (see xshells/build_madhava.sh header): XSHELLS v2.13
# commit f20010b, SHTns 3.7.5.
#SBATCH --job-name=xs-build
#SBATCH --partition=testq
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --hint=nomultithread
#SBATCH --mem=40000M
#SBATCH --time=01:00:00
#SBATCH --output=build-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
# CASE selects the per-case build dir.
# Usage: sbatch --export=CASE=benchmark slurm/build.sbatch
: "${CASE:?set CASE=benchmark|W|K|P...}"
export SLURM_CPUS_PER_TASK
bash xshells/build_madhava.sh "$CASE"
