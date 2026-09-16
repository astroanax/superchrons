# Run manifest — copy into every run directory, fill in, never edit after.
# Paper main-29 §F1 + §F7. Preflight (slurm/preflight.py) enforces this
# schema: EVERY field below must be present and non-empty; case_status gates
# the launch tier (benchmark | development | validated — review round 2:
# tier lives here, never in comment text). Science launches additionally
# require calibration_status=calibrated + a calibration reference.

- date:
- protocol/cell: (e.g. W02)
- case_status: (benchmark | development | validated)
- calibration_status: (calibrated | uncalibrated)
- calibration reference: (source definition + imposed-flux derivation, or blank if uncalibrated)
- xshells commit (pinned 2.13-series revision):
- shtns commit:
- patches applied:
- compilers: gcc 8.3.0 / openmpi 3.1.4 (madhava modules gnu8, openmpi3)
- binary: xsbig_hyb (hybrid; record `make` log excerpt)
- binary sha256:
- xshells.par sha256:
- build dir: (per-case build dir; benchmark and experiments never share one)
- slurm layout: nodes / ntasks-per-node / cpus-per-task / mem / partition
- thread binding: OMP_NUM_THREADS / OMP_PLACES / OMP_PROC_BIND / cpu-bind log
- precision / grid / time integrator:
- input files (checksums):
- restart provenance + segment identifiers + absolute sim times:
- seeds (and what they actually perturb):
- slurm job id:
- output units:
- peak memory / sec-per-step / checkpoint cost:
- benchmark log:
- free-decay log:
- imposed-map log:
- restart-comparison log:
