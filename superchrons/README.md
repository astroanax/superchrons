# Superchron numerical experiments — setup for audit (no runs yet)

Source paper: `~/.hermes/webui/attachments/027552552498/main-28.pdf`
(plaintext: same dir, `main-28.txt`). Appendix F (§F1–F6, txt lines 1737–2183)
is the plan implemented here. It is a proposed plan, not a claim that runs exist.

## What this folder holds

- `00_provenance/` — run-manifest template. Every run gets its own directory
  with an immutable manifest copy (paper §F1: commit, patches, compiler/MPI
  versions, grid, inputs, restart provenance, seeds).
- `xshells/` — build script + per-protocol native input fragments
  (`protocol_W/`, `protocol_K/`, `protocol_P/`). XSHELLS 2.13 is the primary
  implementation (§F1); MagIC 6.3 is the cross-code contrast.
- `magic/` — MagIC counterpart notes (independent setup, not translated names).
- `analysis/` — executable paper code (projected drag, Poisson interval) plus
  stubs for the event detector and dipole-budget check. Runs anywhere.
- `slurm/` — job templates for madhava.
- `run_matrix.md` — pilot cells per protocol.

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

## Protocol anchors

- W (slow-MAC-wave, §F2): EMS = 1.2e-5, Pr = Pm = 1, RaV = 2500;
  Y21 at q* = 17, 18, 20 (dipolar / reversing / multipolar), Y22 symmetric
  control. Seven pilot cells + reflected/mixed patterns.
- K (upwelling vs circulation, §F3): E_omega = 1e-4, Pr = 1, Pm = 5,
  bottom-driven, stress-free impenetrable (BC_U = 2,2); η = 0.2, κT = 1,
  Ω = 1e4 in viscous units. Layer matrix Hs/L × Nmax/Ω + power reporting.
- P (stratified dipole–quadrupole, §F4): E_omega = 1e-3, Pr = 1, Pm = 10,
  Ra/Rac = 25, Y10+Y30 at δq = 0.0175 (half-range); Hs/L = 0, 0.12, 0.24.

## What needs your audit decision

1. Reproduce one anchor per protocol before any intervention.
2. Interventions (projector damping, δu upwelling, parity-block α) are
   custom code to write against the pinned XSHELLS revision — not switches.
3. Prespecified primary contrast per mechanism + one common train/test split
   before production (paper §F6).
