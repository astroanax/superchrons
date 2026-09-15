# Superchron numerical experiments — setup for audit (no runs yet)

Source paper: main-29.pdf (plaintext `main-29.txt` alongside it in the
attachments dir). Appendix F (§F1–F7) is the plan implemented here — a proposed
plan, not a claim that runs exist.

## What this folder holds

- `00_provenance/` — manifest template. Every run gets its own directory with
  an immutable manifest copy (§F1: commit, patches, compiler/MPI versions,
  grid, inputs, restart provenance, seeds; plus §F7: hybrid binary, task/thread
  layout, binding).
- `xshells/` — hybrid build script + per-protocol native input fragments
  (`protocol_W/`, `protocol_K/`, `protocol_P/`). XSHELLS 2.13 is the primary
  implementation (§F1); MagIC 6.3 is the contrast after first validation (§F7).
- `magic/` — MagIC counterpart notes (independent setup, not translated names).
- `analysis/` — `f5_prototype.py` (paper §F5 toy checks) + `budget.py`
  (§F7 Eqs. F9–F11 campaign arithmetic). Solver-independent; run anywhere.
- `slurm/` — `bench.sbatch` (45-min testq benchmark), `pilot.sbatch`
  (production-pilot template). Both launch `xsbig_hyb` via `srun`.
- `run_matrix.md` — pilot cells per protocol + §F7 staged-allocation order.

## Common physics (§F1)

Shell ratio ri/ro = 0.35. Viscous units L = ro − ri = 1, time L²/ν = 1:

    ν = 1, η = 1/Pm, κT = 1/Pr, Ω = 1/E_omega        (F1)

E_omega = ν/(ΩL²). Majumder–Sreenivasan use EMS = ν/(2ΩL²), so
E_omega = 2·EMS. XSHELLS `Omega0` takes the E_omega convention.
Magnetic fields in Alfvén-speed units. Never paste a source Rayleigh number
into another code without this conversion.

Boundary-flux maps for matched comparisons (§F1, F2):

    q(θ,φ) = qbar + qa·H(θ,φ),  <H>S = 0, <H²>S = 1      (F2)

Report qa, both extrema, mean, and total-vs-superadiabatic denominator.

## Madhava execution (§F7)

- Primary binary `xsbig_hyb` (CPU hybrid MPI/OpenMP). `xsbig_mpi` is MPI-only;
  `xsbig_hyb2` is a different decomposition — no substitution without measuring.
- Nothing computational on the login node; builds and runs go in allocations.
- Layouts to compare on one full node: 2 ranks × 20 threads vs 4 ranks × 10
  threads; verify socket placement/binding/actual CPU use; no hyperthread
  oversubscription initially (`--hint=nomultithread`).
- Partitions share 31×40-CPU nodes (scheduler mem field 169000 units); CPU
  ceilings are 120/job (mediumq, ≤3 nodes) and 320/job (longq, ≤8 nodes) —
  ceilings, not entitlements. Multinode only if size/throughput justifies it.
- Request memory explicitly (site default 1 GB/CPU). The 80000M in the bench
  template is a provisional pilot allowance, not a measured requirement.
- Benchmarks before production: unmodified dynamo benchmark + §F1 checks,
  uninterrupted-vs-restart comparison, then a full pilot with diagnostics.
  Nr=200/ℓmax=100 measures performance, not resolution. Larger E is not
  automatically cheaper.
- Record sim-time advance per wall hour from output timestamps (not iteration
  counts), sec/step, peak mem, startup/checkpoint cost, output bytes, CPU use.
- Go/no-go: complete config, passing numerical+restart tests, validated
  diagnostics, fitting memory, measured throughput supporting fixed exposure
  in budget — else cut cases or report bounds, never silently weaken resolution
  or count correlated clones as evidence.

## What needs your audit decision

1. Fetch + pin the 2.13-series XSHELLS revision (off-madhava, then scp up).
2. Reproduce one anchor per protocol before any intervention.
3. Interventions (projector damping, δu upwelling, parity-block α) are custom
   code against the pinned revision — not switches.
4. Prespecified primary contrast per mechanism + one common train/test split
   before production (§F6). Debugging batch first: 4 parents × 2 clones × 2
   arms = 16 short continuations; the 16×8×2 design (256 runs) only after
   manipulation and budget checks pass.
