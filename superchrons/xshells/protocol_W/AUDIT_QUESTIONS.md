# Protocol W — audit questions (must resolve before launch)
1. q*-to-dqo conversion: confirm against the lab implementation (or the
   published q* definition) what outer-flux multiplier reproduces q* = 18.
   Current dqo = -0.018 is a pilot placeholder in the stock-file convention.
2. RaV = 2500 mapping: confirm the paper's RaV definition against XSHELLS
   phi0 = radial*Ra/E (benchmark convention). Sign and factor of E checked
   against the geodynamo benchmark; Ra-definition equivalence still open.
3. b-seed scaling bench2001*5/sqrt(Pm*Eom): same Elsasser convention as the
   benchmark; confirm it yields a saturated-dipole start at E = 2.4e-5 and
   not a blow-up (short smoke test, not a full run).
4. Resolution NR = 192 / Lmax = 159: pilot choice; 1.5x refinement check on
   one cell before production (paper §F1).
5. Remaining cells W00/W01/W03-W06: clone this file, change job + tp map
   (uniform: drop the heteroflux segment; Y22: cmb_Y22.txt) + dqo per q*.
