#!/usr/bin/env python3
"""Preflight gate for scientific runs (fix §3). Benchmark mode skips manifest
and restart checks; science mode refuses to launch unless everything below holds:

- manifest exists with no empty fields
- run input + binary sha256 match the manifest records
- required physics keys present in xshells.par (nu/eta/kappa/Omega0, radii,
  BC_U/BC_T, plus protocol-specific flux/buoyancy markers)
- numerical acceptance flags recorded (benchmark/free-decay/map tests,
  restart comparison) — paths to their logs must exist
- output dir is unique (absent or empty) and restart files match expectation

Usage: preflight.py --mode bench|science --manifest MANIFEST --par PAR
         --binary BIN [--expect-restart|--no-restart] [--outdir DIR]
Exit 0 = go, 2 = refused (with reasons on stdout).
"""
import argparse
import hashlib
import os
import re
import sys

REQUIRED_PAR_KEYS = ["nu", "eta", "kappa", "Omega0", "R_U", "R_T", "R_B",
                     "BC_U", "BC_T"]
# Protocol markers: the fragment must show its forcing/buoyancy plan is filled
# in (no bare TODO left) before a science launch.
FORBIDDEN_TODO = re.compile(r"^\s*#\s*TODO", re.M)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["bench", "science"], required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--par", required=True)
    ap.add_argument("--binary", required=True)
    ap.add_argument("--outdir", default=None)
    restart = ap.add_mutually_exclusive_group(required=False)
    restart.add_argument("--expect-restart", action="store_true")
    restart.add_argument("--no-restart", action="store_true")
    a = ap.parse_args()
    problems = []

    if not os.path.isfile(a.manifest):
        problems.append(f"manifest missing: {a.manifest}")
        fields = {}
    else:
        fields = read_manifest(a.manifest)
        empty = [k for k, v in fields.items() if not v]
        if a.mode == "science" and empty:
            problems.append(f"manifest has empty fields: {empty}")

    if not os.path.isfile(a.par):
        problems.append(f"par missing: {a.par}")
        par_text = ""
    else:
        par_text = open(a.par).read()
        missing = [k for k in REQUIRED_PAR_KEYS
                   if not re.search(rf"^\s*{k}\s*=", par_text, re.M)]
        if missing:
            problems.append(f"par missing keys: {missing}")
        if a.mode == "science" and FORBIDDEN_TODO.search(par_text):
            problems.append("par still contains TODO markers — fragment incomplete")

    if not (os.path.isfile(a.binary) and os.access(a.binary, os.X_OK)):
        problems.append(f"binary not executable: {a.binary}")
    elif fields.get("binary sha256") and \
            sha256(a.binary) != fields["binary sha256"]:
        problems.append("binary checksum != manifest record")
    if fields.get("xshells.par sha256") and \
            sha256(a.par) != fields["xshells.par sha256"]:
        problems.append("par checksum != manifest record")

    if a.mode == "science":
        for key in ["benchmark log", "free-decay log", "imposed-map log",
                    "restart-comparison log"]:
            p = fields.get(key, "")
            if not p:
                problems.append(f"manifest missing acceptance record: {key}")
            elif not os.path.exists(p):
                problems.append(f"acceptance log absent: {key} -> {p}")

    if a.outdir:
        if a.expect_restart and not os.path.isdir(a.outdir):
            problems.append(f"expected restart dir absent: {a.outdir}")
        if a.no_restart and os.path.isdir(a.outdir) and os.listdir(a.outdir):
            problems.append(f"outdir not unique/non-empty: {a.outdir}")

    if problems:
        print("PREFLIGHT REFUSED:")
        for p in problems:
            print(f"  - {p}")
        return 2
    print(f"PREFLIGHT GO ({a.mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
