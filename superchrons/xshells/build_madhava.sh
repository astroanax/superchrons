#!/usr/bin/env bash
# Build SHTns + XSHELLS 2.13 hybrid (xsbig_hyb) on madhava.
# Paper main-29 §F1 + §F7: primary build is the CPU hybrid MPI/OpenMP target
# xsbig_hyb. xsbig_mpi is MPI-only (OMP_NUM_THREADS will NOT make it hybrid);
# xsbig_hyb2 is a different decomposition — do not substitute without measuring.
# All compile steps run inside a Slurm allocation (testq), NEVER on the login
# node (site policy). Fetch must happen off-madhava (madhava git lacks
# remote-https): clone + pin there, scp the trees up.
set -euo pipefail

# --- 0. fetch (off-madhava machine with working git/https) ---
#   git clone https://github.com/nschaeff/shtns.git
#   git clone https://bitbucket.org/nschaeff/xshells.git
#   cd xshells && git checkout <PINNED_2.13_REVISION> && git log -1 --format=%H > REVISION
#   scp -r shtns xshells madhava:~/superchrons/src/
# Record the pinned commit in 00_provenance/MANIFEST.md.
SRC=$HOME/superchrons/src
test -d "$SRC/shtns" || { echo "MISSING $SRC/shtns (fetch off-madhava first)"; exit 1; }
test -d "$SRC/xshells" || { echo "MISSING $SRC/xshells (fetch off-madhava first)"; exit 1; }

# --- 1. environment: site-tested modules, recorded in MANIFEST.md ---
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export CC=mpicc CXX=mpicxx FC=mpif90
FFTW_INC=/usr/local/include   # fftw3.h verified on master node
FFTW_LIB=/usr/local/lib       # libfftw3.a verified; add LAPACK module if link needs it

# --- 2. SHTns (OpenMP enabled — required for the hybrid target) ---
cd "$SRC/shtns"
./configure --prefix="$SRC/shtns-install" --enable-openmp --with-fftw="$FFTW_INC"
make -j40 && make install

# --- 3. XSHELLS hybrid ---
cd "$SRC/xshells"
./configure SHTNS="$SRC/shtns-install"
cp problems/geodynamo/xshells.hpp ./xshells.hpp   # adapt + validate first
cp problems/geodynamo/xshells.par ./xshells.par
make test                    # must pass before production
make xsbig_hyb xspp          # PRIMARY target; do NOT build only xsbig_mpi

echo "BUILD OK. Primary binary: $SRC/xshells/xsbig_hyb (+ xspp)"
echo "Verify now (inside same allocation):"
echo "  test -x ./xsbig_hyb && test -f xshells.par"
echo "  export OMP_NUM_THREADS=20 OMP_PLACES=cores OMP_PROC_BIND=close"
echo "  srun --cpu-bind=verbose,cores ./xsbig_hyb   # short benchmark input"
