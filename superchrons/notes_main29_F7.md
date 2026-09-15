# Notes on main-29 Appendix F (reading notes, not the paper)

Source is the author's own main-29.pdf — untouched. These are my notes only.

## What changed main-28 → main-29 in Appendix F
- New §F7 (Madhava hardware plan) added; F6 evaluation text kept.
- Build target corrected: primary is hybrid `xsbig_hyb`. `xsbig_mpi` is
  MPI-only (threads env will not make it hybrid); `xsbig_hyb2` is a different
  decomposition, no substitution without measuring.
- All builds/runs must go in Slurm allocations, never the login node.
- Partitions share one 31-node × 40-CPU pool (scheduler mem field 169000
  units); per-job CPU ceilings 120 (mediumq, ≤3 nodes) / 320 (longq, ≤8 nodes).
  Ceilings are not entitlements; QOS/fairshare/memory still gate admission.
- 45-min testq benchmark template: 2 tasks × 20 cpus, `--hint=nomultithread`,
  80000M provisional mem, OMP_PLACES=cores, OMP_PROC_BIND=close,
  `srun --cpu-bind=verbose,cores ./xsbig_hyb`.
- Layouts to compare: 2 ranks × 20 threads vs 4 ranks × 10 threads; verify
  socket placement/binding/actual CPU use; no hyperthread oversubscription first.
- Benchmarks before production: unmodified dynamo benchmark + §F1 checks,
  uninterrupted-vs-restart comparison, then full pilot with diagnostics.
  Nr=200/ℓmax=100 measures performance, not resolution. Larger E ≠ cheaper.
- Campaign arithmetic Eqs. F9–F11: tn = Tneed/vn + toverhead; Cn = n·tn;
  en = vn/(n·v1). Debugging batch first (4 parents × 2 clones × 2 arms = 16);
  full 16×8×2 design (256 runs) only after manipulation + budget checks pass.
- Scratch purged 30 days after timestamp — copy checkpoints/manifests/
  diagnostics to persistent storage sooner, verify checksums, keep >1 gen.
- MagIC deferred to one informative contrast after first XSHELLS validation.

## Madhava environment (verified live, not from the paper)
- gcc/gfortran 8.3, OpenMPI 3.1.4, cmake 3.21, FFTW3 header+static lib,
  LAPACK/OpenBLAS/MKL modules, Singularity 3.4.1. System python 3.6 (no
  matplotlib); python 3.8/3.9 modules exist.
- madhava git lacks `remote-https` → fetch SHTns/XSHELLS/MagIC off-machine,
  pin the 2.13-series commit, scp to `~/superchrons/src/`.
- Risk: gcc 8.3 vs 2026 code (C++ standard). Settles at `make test` time;
  fallbacks are Intel compiler modules or a Singularity container.

## Audit blockers (yours to decide)
1. Pin the 2.13-series XSHELLS revision.
2. Lab source inputs (PARODY-JA / Aubert code / Majumder–Sreenivasan files)
   or accept independent XSHELLS realizations.
3. Custom interventions (projector damping, δu, parity-block tracers) get
   written only after anchors reproduce.
