# Partial xshells.par — Protocol W transport/rotation/fluid boundaries (§F1, §F2)
# Viscous units L = 1. NOT a complete dynamo: still supply gravity/buoyancy
# conversion, base profile, flux map (heteroflux problem), grid, restarts.
# Anchors: EMS = 1.2e-5 → E_omega = 2.4e-5 → Omega0 ≈ 41666.7;
# Pr = Pm = 1; RaV = 2500. Launched with the hybrid binary (§F7):
#   export OMP_NUM_THREADS=20 OMP_PLACES=cores OMP_PROC_BIND=close
#   srun --cpu-bind=verbose,cores ./xsbig_hyb

nu = 1.0
eta = 1.0
kappa = 1.0
Omega0 = 41666.6667
R_U = 7/13 : 20/13
R_T = 7/13 : 20/13
R_B = 7/13 : 20/13
BC_U = 0,0
BC_T = 1,2
# TODO(audit): gravity/buoyancy coefficient conversion from RaV = 2500,
#   basal thermal driving profile, Y21/Y22 heteroflux maps at q* = 17/18/20
#   with the source heat-flux normalization, grid + restart provenance.
