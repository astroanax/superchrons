#!/usr/bin/env bash
# Build SHTns + XSHELLS 2.13 on madhava. Run INTERACTIVELY on a testq
# allocation or the login node for the configure step only; the compile
# itself should go through slurm (see slurm/build.sh).
# Paper §F1: pin revisions, archive immutable copies before production.
set -euo pipefail

# --- 0. environment (madhava module stack) ---
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export CC=mpicc CXX=mpicxx FC=mpif90
FFTW_INC=/usr/local/include   # verified: fftw3.h present on master node

# --- 1. fetch (BLOCKER workaround: madhava git lacks remote-https) ---
# Do this on a machine with working git/https, then scp the trees up:
#   git clone https://github.com/nschaeff/shtns.git
#   git clone https://bitbucket.org/nschaeff/xshells.git
#   cd xshells && git checkout <PINNED_REVISION> && git log -1 --format=%H > REVISION
# then: scp -r shtns xshells madhava:~/superchrons/src/
#
# Record the pinned XSHELLS 2.13-series commit in 00_provenance/MANIFEST.md.
SRC=$HOME/superchrons/src
test -d "$SRC/shtns" || { echo "MISSING $SRC/shtns (see fetch note above)"; exit 1; }
test -d "$SRC/xshells" || { echo "MISSING $SRC/xshells (see fetch note above)"; exit 1; }

# --- 2. SHTns ---
cd "$SRC/shtns"
./configure --prefix="$SRC/shtns-install" --enable-openmp --with-fftw="$FFTW_INC"
make -j40 && make install

# --- 3. XSHELLS ---
cd "$SRC/xshells"
./configure SHTNS="$SRC/shtns-install"
cp problems/geodynamo/xshells.hpp ./xshells.hpp   # adapt + validate first
cp problems/geodynamo/xshells.par ./xshells.par
make test                    # must pass before production
make xsbig_mpi xspp

echo "BUILD OK. Binaries: $SRC/xshells/xsbig_mpi, xspp"
echo "Record commit + compiler/MPI versions in 00_provenance/MANIFEST.md"
mpirun -n 4 ./xsbig_mpi --version 2>&1 | head -3 || true
