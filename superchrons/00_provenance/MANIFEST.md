# Run manifest — copy into every run directory, fill in, never edit after.
# Paper main-29 §F1 + §F7: archive immutable copies before production.

- date:
- protocol/cell: (e.g. W02)
- xshells commit (pinned 2.13-series revision):
- patches applied:
- compilers: gcc 8.3.0 / openmpi 3.1.4 (madhava modules gnu8, openmpi3)
- binary: xsbig_hyb (hybrid; record `make` log excerpt)
- slurm layout: nodes / ntasks-per-node / cpus-per-task / mem / partition
- thread binding: OMP_NUM_THREADS / OMP_PLACES / OMP_PROC_BIND / cpu-bind log
- precision / grid / time integrator:
- input files (checksums):
- restart provenance + segment identifiers + absolute sim times:
- seeds (and what they actually perturb):
- slurm job id:
- output units:
- peak memory / sec-per-step / checkpoint cost:
