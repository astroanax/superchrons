# Partial xshells.par — Protocol K pilot (§F3)
# DECISION (audit fix §2): K is FLUX-CONTROLLED. The pilot searches a bottom
# (inner) scalar flux for a sustained dipolar neutral state and freezes it
# before treatments; the comparison holds that flux fixed. Fixed-temperature
# inner (BC_T = 1,x) would be a different experiment and is rejected here.
# Flux control requires, beyond the selector: matching background scalar
# gradients and signs, a global scalar-balance check (volume mean / compensating
# source for zero-outer-flux cases), and buoyancy-power bookkeeping across
# layer cases. Changing the selector alone is NOT a complete fix — the TODO
# items below must be filled before any science launch (preflight refuses
# fragments with TODO markers).
# Launched with the hybrid binary (§F7):
#   srun --cpu-bind=verbose,cores ./xsbig_hyb

nu = 1.0
eta = 0.2
kappa = 1.0
Omega0 = 10000.0
R_U = 7/13 : 20/13
R_T = 7/13 : 20/13
R_B = 7/13 : 20/13
BC_U = 2,2
BC_T = 2,2
# TODO(audit): bottom-flux search procedure + frozen value, background scalar
#   gradients/signs for flux-type inner AND outer boundaries, global scalar
#   balance implementation + check, stratification-layer construction
#   (Hs/L × Nmax/Omega matrix) with maintaining term, N^2(r) measurement,
#   power bookkeeping across layer cases.
