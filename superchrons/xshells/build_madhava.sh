#!/usr/bin/env bash
# Build SHTns + XSHELLS 2.13 hybrid (xsbig_hyb) on madhava.
# Paper main-29 §F1 + §F7. MUST run inside a Slurm allocation (see
# slurm/build.sbatch) — refuses to run on the login node. Fetch happens
# off-madhava (madhava git lacks remote-https): clone + pin there, scp up.
#
# Layout (fix §1): the benchmark and every experiment case get their own
# build directory. This script never copies problem files over an existing
# directory; it refuses overwrites and records sha256 checksums of the
# compile-time configuration (xshells.hpp) and the resulting binary.
set -euo pipefail

# --- allocation guard (fix §4): refuse login-node execution ---
if [[ -z "${SLURM_JOB_ID:-}" ]]; then
  echo "REFUSED: run inside a Slurm allocation (sbatch slurm/build.sbatch), not the login node." >&2
  exit 2
fi
# Derive build concurrency from the allocation, never assume 40 (fix §4).
NJOBS="${SLURM_CPUS_PER_TASK:-${SLURM_CPUS_ON_NODE:-$(nproc)}}"
echo "build workers: $NJOBS (from allocation)"

usage() { echo "usage: build_madhava.sh <case-dir>   e.g. build_madhava.sh benchmark" >&2; exit 2; }
CASE="${1:-}"; [[ -n "$CASE" ]] || usage

# --- pinned sources (fix §8): already staged on madhava ---
# XSHELLS: v2.13 commit f20010bd038446a2bf0e838c266484e556d90b41 (2026-06-26,
#   "v2.13"), fetched from bitbucket (github https is blocked here) as
#   xshells-2.13-f20010b.tar.gz. Validated in-tree: `make xsbig_hyb xspp`
#   and `make test` (python test.py) are real targets; SHTns is NOT bundled
#   (empty shtns/ placeholder) so the separate build below is required.
# SHTns: 3.7.5 sdist from PyPI (github blocked), shtns-3.7.5.tar.gz.
# Both checksums recorded in 00_provenance/MANIFEST.md at build time.
SRC=$HOME/superchrons/src
XS="$SRC/xshells"            # extracted from xshells-2.13-f20010b.tar.gz
SN="$SRC/shtns-3.7.5"        # extracted from shtns-3.7.5.tar.gz
test -f "$XS/configure" || { echo "MISSING $XS (extract xshells tarball)"; exit 1; }
test -f "$SN/configure" || { echo "MISSING $SN (extract shtns tarball)"; exit 1; }

# --- environment: site-tested modules (fix §8: active, not commented) ---
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export CC=mpicc CXX=mpicxx FC=mpif90
# PROVEN 2026-09-16 on login node (see notes launch log): stock FFTW module
# (/opt/apps/libs/fftw3/.../3.3.9) is Intel-built and fails gcc link
# (undefined __intel_* symbols). Use oneapi-mkl 2025.0.1 instead.
MKL=/opt/apps/oneapi-mkl/2025.0.1
export LD_LIBRARY_PATH=$MKL/lib/intel64:${LD_LIBRARY_PATH:-}

# --- SHTns (OpenMP enabled — required for the hybrid target) ---
cd "$SN"
./configure --prefix="$SRC/shtns-install" --enable-openmp --enable-mkl \
  LDFLAGS="-L$MKL/lib/intel64" CPPFLAGS="-I$MKL/include" \
  2>&1 | tee "$SRC/shtns-configure.log"
make -j"$NJOBS" 2>&1 | tee "$SRC/shtns-build.log"
# Quirk (non-CUDA build): install expects shtns_cuda.h / shtns_cuda.f03
# which the sdist omits; empty placeholders satisfy it.
touch shtns_cuda.h shtns_cuda.f03
make install 2>&1 | tee -a "$SRC/shtns-build.log"

# --- XSHELLS hybrid in a per-case build dir (fix §1) ---
BUILDDIR="$SRC/build-$CASE"
if [[ -e "$BUILDDIR" ]]; then
  echo "REFUSED: $BUILDDIR exists — remove it explicitly or choose another case." >&2
  exit 2
fi
mkdir -p "$BUILDDIR"
cd "$BUILDDIR"
PROBLEM="${PROBLEM_DIR:-$XS/problems/geodynamo}"  # explicit source
cp "$PROBLEM/xshells.hpp" ./xshells.hpp
cp "$PROBLEM/xshells.par" ./xshells.par
# Validated flags against v2.13 (proven 2026-09-16): --enable-mkl plus
# --with-shtns pointing at the SHTns SOURCE dir (install prefix alone makes
# configure try to re-configure an empty bundled shtns/ and fail).
# The MKL include paths below supply both mkl_dfti.h and fftw/fftw3_mkl.h.
"$XS/configure" --enable-mkl --with-shtns="$SN" \
  LDFLAGS="-L$MKL/lib/intel64" CPPFLAGS="-I$MKL/include" \
  CXXFLAGS="-I$MKL/include -I$MKL/include/fftw" 2>&1 | tee configure.log
make test 2>&1 | tee make-test.log   # must pass before production (python test.py)
make -j"$NJOBS" xsbig_hyb xspp 2>&1 | tee make.log  # PRIMARY target (MPI-only xsbig_mpi NOT built)

# --- record (fixes §1, §8): checksums + versions, immutable ---
sha256sum xshells.hpp xsbig_hyb xspp > BUILD_CHECKSUMS
{
  echo "xshells_rev: f20010bd038446a2bf0e838c266484e556d90b41 (v2.13, 2026-06-26)"
  echo "shtns: 3.7.5 (PyPI sdist)"
  mpicc --version | head -1; mpirun --version | head -1
  echo "slurm_job: ${SLURM_JOB_ID:-none}"; echo "workers: $NJOBS"
} > BUILD_META
echo "BUILD OK in $BUILDDIR. Checksums in BUILD_CHECKSUMS."
