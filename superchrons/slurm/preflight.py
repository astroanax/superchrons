#!/usr/bin/env python3
"""Preflight gate for XSHELLS runs (review round 2: structured readiness).

Three case tiers (manifest field `case_status`, required):
  benchmark            — stock-code reference run (geodynamo benchmark etc.).
                         Par + binary presence only; checksums recorded but
                         acceptance logs not required.
  development          — uncalibrated pilot (W02/Y21, P00, ...). Requires full
                         manifest + checksums + par schema, but NO launch
                         beyond short smoke tests. Calibration blockers stay
                         machine-readable in `calibration_status`.
  validated            — calibrated scientific experiment. Additionally
                         requires calibration_status=calibrated with reference,
                         acceptance logs that EXIST and contain a PASS marker,
                         verified checkpoint set for restarts, and par/solver
                         restart-flag agreement.

Removing a TODO comment never promotes a case: tier lives in `case_status`,
not in comment text. No AUDIT/TODO scanning is performed at all.
Acceptance-log PASS marker convention: a line matching
  RESULT: PASS <test-name>
written by the test procedure (see tools/record_acceptance.sh). A log that
exists without the marker is a failure, not an acceptance.
Checkpoint verification (--expect-restart): outdir must contain >=1 field
backup (field* or backup*) AND the input copy xshells.par.<job> (or the
manifest-recorded input name); a bare directory is refused.
Restart agreement: launcher RESTART=1 requires the par file to set
`restart = 1`; RESTART=0 requires `restart = 0`. Mismatch is refused.

Usage: preflight.py --mode bench|science|smoke --manifest MANIFEST --par PAR
         --binary BIN [--expect-restart|--no-restart] [--outdir DIR]
         [--max-walltime-min N]
Modes: bench = tier benchmark; smoke = tier development but only a short
launch check (no acceptance needed); science = tier validated (full gate).
Exit 0 = go, 2 = refused (reasons on stdout).
"""
import argparse
import hashlib
import os
import re
import sys

REQUIRED_PAR_KEYS = ["nu", "eta", "kappa", "Omega0", "R_U", "R_T", "R_B",
                     "BC_U", "BC_T", "u", "b", "tp", "tp0", "phi0",
                     "NR", "Lmax", "Mmax", "Mres", "job"]
REQUIRED_MANIFEST_FIELDS = ["date", "protocol/cell", "xshells commit",
                            "shtns commit", "binary", "binary sha256",
                            "xshells.par sha256", "build dir",
                            "slurm layout", "input files (checksums)",
                            "seeds (and what they actually perturb)",
                            "slurm job id", "output units"]
ACCEPTANCE_KEYS = ["benchmark log", "free-decay log", "imposed-map log",
                   "restart-comparison log"]
PASS_MARKER = re.compile(r"^RESULT:\s*PASS\s+\S+", re.M)
CASE_STATUS = {"benchmark", "development", "validated"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_manifest(path):
    fields = {}
    for line in open(path):
        m = re.match(r"-\s*([^:]+):\s*(.*)$", line.strip())
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def par_value(text, key):
    m = re.search(rf"^\s*{key}\s*=\s*(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["bench", "smoke", "science"],
                    required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--par", required=True)
    ap.add_argument("--binary", required=True)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--max-walltime-min", type=float, default=None)
    restart = ap.add_mutually_exclusive_group(required=False)
    restart.add_argument("--expect-restart", action="store_true")
    restart.add_argument("--no-restart", action="store_true")
    a = ap.parse_args()
    problems = []

    # --- manifest schema ---
    if not os.path.isfile(a.manifest):
        problems.append(f"manifest missing: {a.manifest}")
        fields = {}
    else:
        fields = read_manifest(a.manifest)
        missing = [k for k in REQUIRED_MANIFEST_FIELDS if k not in fields]
        if missing:
            problems.append(f"manifest missing required fields: {missing}")
        empty = [k for k, v in fields.items() if not v]
        if empty:
            problems.append(f"manifest has empty fields: {empty}")
        status = fields.get("case_status", "")
        if status not in CASE_STATUS:
            problems.append(
                f"case_status must be one of {sorted(CASE_STATUS)}, "
                f"got {status!r}")
        elif a.mode == "bench" and status != "benchmark":
            problems.append(f"bench mode requires case_status=benchmark, "
                            f"got {status!r}")
        elif a.mode == "science" and status != "validated":
            problems.append(f"science mode requires case_status=validated, "
                            f"got {status!r} — uncalibrated cases stay in "
                            f"development and never launch as science")
        if a.mode == "science":
            if fields.get("calibration_status") != "calibrated":
                problems.append(
                    "science requires calibration_status=calibrated with "
                    "a calibration reference; got "
                    f"{fields.get('calibration_status', '')!r}")
            if not fields.get("calibration reference"):
                problems.append("science requires a calibration reference")

    # --- par schema (all modes: physics completeness, not comment text) ---
    if not os.path.isfile(a.par):
        problems.append(f"par missing: {a.par}")
        par_text = ""
    else:
        code_lines = [l for l in open(a.par).read().splitlines()
                      if not l.strip().startswith(("#", "%"))]
        par_text = "\n".join(code_lines)
        missing = [k for k in REQUIRED_PAR_KEYS
                   if not re.search(rf"^\s*{k}\s*=", par_text, re.M)]
        if missing:
            problems.append(f"par missing physics keys: {missing}")

    # --- checksums: mandatory whenever the manifest carries them, and
    # always mandatory in science mode ---
    if not (os.path.isfile(a.binary) and os.access(a.binary, os.X_OK)):
        problems.append(f"binary not executable: {a.binary}")
    else:
        if a.mode == "science" or fields.get("binary sha256"):
            if not fields.get("binary sha256"):
                problems.append("manifest lacks binary sha256 record")
            elif sha256(a.binary) != fields["binary sha256"]:
                problems.append("binary checksum != manifest record")
        if a.mode == "science" or fields.get("xshells.par sha256"):
            if not fields.get("xshells.par sha256"):
                problems.append("manifest lacks xshells.par sha256 record")
            elif par_text and sha256(a.par) != fields["xshells.par sha256"]:
                problems.append("par checksum != manifest record")

    # --- acceptance: existence AND PASS marker (science only) ---
    if a.mode == "science":
        for key in ACCEPTANCE_KEYS:
            p = fields.get(key, "")
            if not p:
                problems.append(f"manifest missing acceptance record: {key}")
            elif not os.path.isfile(p):
                problems.append(f"acceptance log absent: {key} -> {p}")
            elif not PASS_MARKER.search(open(p).read()):
                problems.append(
                    f"acceptance log lacks PASS marker: {key} -> {p} "
                    f"(convention: 'RESULT: PASS <test-name>')")

    # --- restart: verified artifacts + par/solver agreement ---
    if a.outdir:
        if a.expect_restart:
            if not os.path.isdir(a.outdir):
                problems.append(f"expected restart dir absent: {a.outdir}")
            else:
                files = os.listdir(a.outdir)
                has_fields = any(
                    f.startswith(("field", "backup", "restart"))
                    for f in files)
                has_parcopy = any(
                    f.startswith("xshells.par.") for f in files)
                if not has_fields:
                    problems.append(
                        f"restart dir has no checkpoint artifacts "
                        f"(field*/backup*/restart*): {a.outdir}")
                if not has_parcopy:
                    problems.append(
                        f"restart dir has no input copy "
                        f"(xshells.par.<job>): {a.outdir}")
        if a.no_restart and os.path.isdir(a.outdir) and os.listdir(a.outdir):
            problems.append(f"outdir not unique/non-empty: {a.outdir}")
    if par_text:
        rst = par_value(par_text, "restart")
        if a.expect_restart and rst != "1":
            problems.append(
                f"launcher expects restart but par sets restart={rst}; "
                f"make intent agree (review finding §7)")
        if a.no_restart and rst not in (None, "0"):
            problems.append(f"fresh launch but par sets restart={rst}")

    if problems:
        print("PREFLIGHT REFUSED:")
        for p in problems:
            print(f"  - {p}")
        return 2
    print(f"PREFLIGHT GO ({a.mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
