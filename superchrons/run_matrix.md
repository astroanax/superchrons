# Pilot run matrix (all pilot choices from paper Appendix F, not Earth values)

## W — slow-MAC-wave (§F2)
Anchor: EMS = 1.2e-5 → E_omega = 2.4e-5 → Omega0 = 1/2.4e-5 ≈ 41666.7.
Pr = Pm = 1 → eta = 1.0, kappa = 1.0. Basal thermal driving, no-slip (BC_U = 0,0),
insulating inner/outer magnetic boundaries, source heat-flux normalization.

| cell | pattern | q* | role |
|------|---------|----|------|
| W00 | uniform | 0 | baseline |
| W01 | Y21 | 17 | dipolar anchor |
| W02 | Y21 | 18 | reversing anchor |
| W03 | Y21 | 20 | multipolar anchor |
| W04 | Y22 | 17 | symmetric control |
| W05 | Y22 | 18 | symmetric control |
| W06 | Y22 | 20 | symmetric control |

Follow-ups: reflected forcing, paired initial polarities, mixed Y21+Y22.
Four statistically independent continuations per production cell.
Intervention pilot: 16 parent states × 8 clones per arm, horizon 20·τu.

## K — upwelling vs circulation (§F3)
Pilot: E_omega = 1e-4 → Omega0 = 1e4. Pr = 1, Pm = 5 → eta = 0.2, kappa = 1.0.
Bottom-driven buoyancy, stress-free impenetrable (BC_U = 2,2).
Baseline: pilot-only bottom-flux search for sustained dipolar neutral state;
freeze forcing before treatments.

Layer matrix: neutral top + Hs/L ∈ {0.05, 0.10} × Nmax/Ω ∈ {0.5, 1, 2}.
Keep bottom flux + diffusivities fixed first; report changed buoyancy power.
Selected cells: bottom forcing ±20%.

## P — stratified dipole–quadrupole (§F4)
Anchor: E_omega = 1e-3 → Omega0 = 1e3. Pr = 1, Pm = 10 → eta = 0.1, kappa = 1.0.
Ra/Rac = 25. Pattern Y10 + Y30, δq = 0.0175 (half-range convention).
Hs/L = 0, 0.12, 0.24; at Hs/L > 0 start Nmax/Ω = 10.
Amplitude brackets δq = 0.01, 0.0175, 0.03; add symmetric-pattern control.

## Common acceptance (§F1)
- Dynamo benchmark + free-decay test + imposed-map test pass first.
- Resolution: ≥10 points across mechanical/stratification layers; 1.5× radial
  + angular refinement check with halved dt on selected cases; <5% change in
  energy/flow/wave/budget diagnostics.
- Dipole-budget error εD = rms(Ḋsurf − AD − OD)/(rms(AD) + rms(OD)) < 0.01.
- Sampling: ordinary diagnostics ≤ 0.02·τu; wave bursts ≥20 samples per
  shortest resolved period, windows ≥10 slow periods.
- Events: polarity sets at |Dsurf| > 0.4·Dref (Dref from training only),
  persistence τu; reversal = committed-set to committed-set; sensitivity at
  0.25 and 0.6. Parent state (not sample) is the resampling unit.
