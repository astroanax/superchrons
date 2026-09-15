# Partial xshells.par — Protocol K pilot (§F3)
# E_omega = 1e-4, Pr = 1, Pm = 5 (eta = 0.2), bottom-driven buoyancy,
# stress-free impenetrable velocity boundaries. Magnetic domain + scalar
# forcing need a separate physical setup; baseline bottom flux found by
# pilot-only search for a sustained dipolar neutral state, then frozen.
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
BC_T = 1,2
# TODO(audit): bottom-flux search procedure, stratification-layer construction
#   (Hs/L × Nmax/Omega matrix) with maintaining term, N^2(r) measurement,
#   power bookkeeping across layer cases.
