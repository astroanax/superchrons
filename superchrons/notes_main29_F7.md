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

## Launch log (running notes, newest last)

### 15 Sep 2026 ~21:00 — simple launch test begins
- Goal: prove XSHELLS builds and launches on madhava (no science yet).
- Pre-state: smoke job 115398 proved scheduler+modules+srun+MPI on compute02.
  FFTW hunt found headers at /opt/apps/libs/fftw3/.../3.3.9 (login-node
  /usr/local invisible on compute nodes); build script updated. Sources staged:
  xshells-2.13-f20010b.tar.gz (v2.13 f20010b) + shtns-3.7.5.tar.gz, extracted.
- Plan: submit slurm/build.sbatch CASE=benchmark (testq, 1h) → SHTns build →
  XSHELLS configure --with-shtns → make test → make xsbig_hyb xspp.
- 20:57 scp hiccup: first copy appeared empty (filtered output hid the
  transfer); re-ran scp cleanly, both files verified on madhava
  (build_madhava.sh 3945 B, build.sbatch 745 B).
- 20:58 build job SUBMITTED as 115402 (testq, CASE=benchmark).
  Note: build.sbatch does `bash xshells/build_madhava.sh`, so the script was
  also placed at ~/superchrons/build/xshells/build_madhava.sh.
- ~21:00 job 115402 PENDING: "Nodes required for job are DOWN, DRAINED or
  reserved for jobs in higher priority partitions". Waiting for a slot.
- ~21:10 cluster state: testq has 1 draining + 8 mixed + 22 allocated; whole
  queue is backed up (many PENDING jobs across partitions, several Priority).
  Our job is queued normally — nothing wrong with the submission, just waiting.
- ~21:15 still PENDING. Queue totals: 36 pending / 43 running. Running jobs
  are normal 4–6h multi-CPU jobs (no single hog; oldest ~6h). Scheduler
  estimates our start 2026-09-21 — i.e. cluster is simply full, testq does
  not preempt. Options if it sits: leave it (build needs only one slot),
  or resubmit to shortq (same nodes, 7d limit, no real advantage for a 1h
  build). No action taken yet; keep polling.
- Clarification on "1 hour": --time=01:00:00 is the max walltime requested
  from testq, not the expected build duration (likely 10–20 min). Configure
  the input to finish well inside it; walltime is not a checkpoint.
- ~21:20 per user: submitted duplicate build to shortq as 115403
  (CASE=benchmark_sq, separate build dir to avoid collision with 115402).
  Both pending on the same node pool. If shortq also sits, user authorized
  a login-node attempt (against site policy) — next step then would be a
  minimal configure-only check on login, not a full make.
- ~21:25 toolchain check on login (seconds, not a compute job): gcc 8.3
  present, OpenMP hello prints threads=4 (OMP_OK). XSHELLS configure exposes
  --with-shtns (matches build script). SHTns configure offers --prefix etc.;
  --enable-openmp/--with-fftw still to be confirmed at build time. Both Slurm
  jobs still PENDING. User confirmed: launch test itself should be minutes
  once a slot is granted — agreed, the 1h is only the walltime cap.
- ~21:35 user asked: does XSHELLS need C/C++ code or just a config file?
  Checked the 2.13 user manual Ch1 (nschaeff.bitbucket.io/xshells/Ch1.html),
  confirmed via deepwiki astroanax/xshells (indexed): BOTH.
  xshells.par = runtime options (name = value, read at startup, no recompile);
  xshells.hpp = compile-time options (#defines, edit → recompile, embedded
  into binary as hex). Workflow: cp problems/geodynamo/xshells.{par,hpp} .,
  edit, make xsbig_hyb, launch; make test runs python test.py. So right now
  we run NO custom C++ — the queued build jobs compile stock SHTns + stock
  XSHELLS only. Custom C++ comes later (paper §F1: xshells_init.cpp /
  xshells_big.cpp / xshells_physics.cpp extensions for background profiles,
  wave projector, parity-block tracers) — after anchors reproduce.
- ~21:40 queue audit: 37 PENDING total. Ahead of us across partitions:
  p240506ch (120cpu), p250143cy (36+24+18+10+8cpu), m250851ce (2×40cpu),
  m230741cy (4×30cpu), m251146cy (3×24cpu + 1×24 longq), p250584ph
  (32+100cpu), m241190cy (3×8cpu), b241437ed (24+8+8cpu), p220034bt/p230131bt
  (32cpu each), sajith, minimol, pnbala, p240247mt, p230674mt, p240165mt jobs
  at Priority / Resources / QOSMaxJobs limits. Ours: 115401+115402 (testq 40cpu)
  + 115403 (shortq 40cpu), all same DOWN/DRAINED reason. Only 1 node draining
  (compute20); rest allocated/mixed. Everyone waits on the same pool.

## Audit blockers (yours to decide)

1. ~~Pin the 2.13-series XSHELLS revision~~ DONE (no decision needed):
   XSHELLS v2.13 commit f20010b (2026-06-26) + SHTns 3.7.5, both staged as
   tarballs in ~/superchrons/src/ on madhava. Build still untested — that is
   the next step after your audit.
2. Lab source inputs (PARODY-JA / Aubert code / Majumder–Sreenivasan files)
   or accept independent XSHELLS realizations.
3. Custom interventions (projector damping, δu, parity-block tracers) get
   written only after anchors reproduce.

## Fix round (review of commit 12085c5, all applied locally, no runs)
1. Build script no-overwrite: per-case build dirs, refuse-if-exists,
   sha256 of xshells.hpp + binaries recorded.
2. Protocol K flux-controlled: BC_T = 2,2 + documented balance requirements;
   preflight refuses fragments with TODO markers.
3. Preflight gate (slurm/preflight.py): bench vs science modes; bench.sbatch
   and pilot.sbatch both call it. Verified: GO on complete bench input,
   REFUSED on science fragment (TODO + missing acceptance logs).
4. Build inside allocation only: slurm/build.sbatch + SLURM_JOB_ID guard +
   allocation-derived -j. Verified live: smoke job proved scheduler path.
5. Analysis hardened: W Hermitian-PD check, exact-shape checks, time-weighted
   RMS, (eps, abs) budget errors, implemented event detector with synthetic
   reversal/excursion tests. budget.py rejects NaN/inf/negative/fractional.
6. snapshot tool: tools/pack_snapshot.sh (tar.gz + .sha256 + .revision);
   stale repomix-output.xml exists only on GitHub, not locally — flagged for
   regeneration, not used for audit.
7. FFTW path fixed: login-node /usr/local is invisible on compute nodes;
   build uses /opt/apps/libs/fftw3/.../3.3.9 (header verified present on
   compute02 via Slurm job).
- ~00:45 (16 Sep) CONNECTIVITY LOST: session moved to a container running as
  hermeswebui; /home/rehan/.ssh (madhava/aiclub config + keys) is not mounted
  here, so ssh to madhava fails (no hostname resolution). Workspace files are
  intact and readable. Queue status of 115401/115402/115403 UNKNOWN from here.
  To resume: restore ~/.ssh access, or run `squeue -u b231090pe` from a shell
  with the keys and report back.
- ~03:00 (16 Sep) LAUNCH TEST PASSED on login node (direct, no Slurm):
  SHTns 3.7.5 configured (--enable-openmp --enable-mkl) + built (-j4) +
  installed to ~/superchrons/shtns-install-test (two missing-CUDA-header
  touch workarounds: shtns_cuda.h, shtns_cuda.f03 — non-CUDA build quirk).
  XSHELLS v2.13 configured (--enable-mkl --with-shtns=<src> + MKL
  LDFLAGS/CPPFLAGS/CXXFLAGS) in ~/superchrons/build-bench; `make -j4
  xsbig_hyb xspp` OK (xsbig_hyb 4.9 MB, xspp 3.1 MB). Runtime needs
  LD_LIBRARY_PATH=/opt/apps/oneapi-mkl/2025.0.1/lib/intel64.
  Geodynamo benchmark (E=1e-3, Pm=5, Ra=100, NR=96, Lmax=47) launched with
  1 rank × 2 threads: init OK (SHT accuracy 1.19e-14), time-stepping confirmed
  ([it 0] t=0 → [it 2] t=0.04, energies evolving), output files written
  (energy.bench, fieldB/U/T, xshells.hpp.bench). `make test` NOT run (needs
  xsbig/xsbig_mpi/xsbig_hyb2 + python shtns module). Slurm build jobs
  115401/115402/115403 still PENDING — kept for the sanctioned path; direct
  login build was user-authorized for this small test only.
- ~03:10 (16 Sep) per user: scancelled 115401/115402/115403. Queue empty.
  Rationale: direct login build already proved the toolchain; queue shows no
  movement for days. Sanctioned Slurm path revisited when production runs need it.
- ~03:30 (16 Sep) three run files written (no runs): W02 (Y21 q*=18 reversing
  anchor), K00 (flux-controlled neutral-baseline start), P00 (Hs/L=0 screen).
  Flux maps generated+verified by tools/make_fluxmaps.py (stock power
  convention 1/2, Y22 amplitude matches stock file). Par validation passes
  (keys, flux refs, no TODO). Open calibrations (q*/dq, Ra definitions,
  stratification extension) listed per-protocol in AUDIT_QUESTIONS.md.
  build_madhava.sh updated to proven MKL recipe. Analysis suites re-pass
  (fresh container needed pip install numpy/scipy first).
