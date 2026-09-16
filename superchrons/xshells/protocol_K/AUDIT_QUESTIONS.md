# Protocol K — audit questions (must resolve before launch)
1. Baseline Ra: 1.5e8 is inherited from the Frasson E1e-4 setup (which used a
   thermochem base state). Confirm the thermal-only bottom-flux value that
   sustains a dipolar neutral state; freeze it before treatments.
2. tp0 = delta*-1 with flux-type BCs: confirm the background scalar gradient
   signs and the global scalar-balance implementation (volume mean /
   compensating source for zero-outer-flux cases) per paper §F1.
3. Seed fields (rands) match across treatment arms per §F7 debugging-batch
   rules; document what the seed perturbs.
4. b = rands*1e-3 start: confirm growth to a dipole (not decay) in a short
   smoke test, not a full run.
5. Old fragment xshells.par.K (with TODO markers) is superseded by this file;
   preflight correctly refuses fragments — this file uses AUDIT: notes so the
   gate checks structure while the questions above stay visible.
