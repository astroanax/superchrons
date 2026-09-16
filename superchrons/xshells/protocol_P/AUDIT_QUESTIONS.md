# Protocol P — audit questions (must resolve before launch)
1. Ra/Rac = 25: Rac ≈ 55.87 is the benchmark's m = 4 onset at E = 1e-3;
   confirm the source's Rac definition (their onset may differ) before
   treating Ra = 1400 as the anchor.
2. Half-range dq = 0.0175: confirm the Y10+Y30 amplitude convention against
   the PARODY-JA source; current value is the pilot placeholder.
3. Stratified cells (Hs/L = 0.12, 0.24): custom stratified-tp0 profile +
   maintaining term + N^2(r) measurement are custom code, written only after
   P00 reproduces. No stratified launch with stock tp0.
4. Conductivity-vs-flow separation (passive replay with changed top-region
   diffusivity) needs the passive-tracer extension; same post-anchor gate.
5. Amplitude brackets dq = 0.01/0.0175/0.03 and symmetric-pattern control:
   clone P00, change job + dq + map file.
