#!/usr/bin/env python3
"""Verify heteroflux boundary files in PHYSICAL space (review round 2 §4).

The coefficient-power check in make_fluxmaps.py is file consistency only:
SHTns normalization and +/-m handling mean it cannot establish spatial RMS.
This script reconstructs each map on a lat-lon grid with scipy spherical
harmonics (complex basis, orthonormal convention) and measures:
  mean, RMS, min, max, half-range (max-min)/2, equatorial parity
  (corr with equatorial mirror: +1 symmetric, -1 anti-symmetric),
  and the physical boundary flux after the par multiplier is applied.

Conventions: file lines are (re, im) per (l, m>=0), m>0 entries are the
cos-branch real mode with amplitude shared across +/-m; axisymmetric (m=0)
entries are used directly. A map passes when |mean| < 1e-10 (zero-mean,
paper §F1 <H>S = 0) and the report records measured RMS (no claim of 1.0
unless measured).
Usage: python3 tools/verify_fluxmaps.py [--multiplier D] [files...]
"""
import math
import os
import re
import sys

import numpy as np

try:
    from scipy.special import sph_harm_y
    HAVE_SPH = True
except ImportError:
    HAVE_SPH = False


def read_flux(path):
    modes = {}
    header = ""
    for line in open(path):
        if line.startswith("%XS"):
            header = line.strip()
            continue
        if line.startswith("%") or not line.strip():
            continue
        m = re.match(r"\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+#l=(\d+),m=(\d+)",
                     line)
        if not m:
            raise ValueError(f"unparsable line in {path}: {line!r}")
        re_, im_, l, mm = float(m.group(1)), float(m.group(2)), \
            int(m.group(3)), int(m.group(4))
        if re_ or im_:
            modes[(l, mm)] = (re_, im_)
    return header, modes


def reconstruct(modes, nlat=361, nlon=720):
    """Real field on (theta, phi) grid. m>0 file entries are the real
    cos-branch: Y_l^m_real = sqrt(2)*Re[Y_l^m]; m=0 used directly."""
    theta = np.linspace(0, math.pi, nlat)
    phi = np.linspace(0, 2 * math.pi, nlon, endpoint=False)
    TH, PH = np.meshgrid(theta, phi, indexing="ij")
    H = np.zeros_like(TH)
    for (l, m), (re_, im_) in modes.items():
        if m == 0:
            Y = sph_harm_y(l, 0, TH, PH).real
            H += re_ * Y
        else:
            Y = sph_harm_y(l, m, TH, PH)
            H += re_ * math.sqrt(2.0) * Y.real
            H += im_ * math.sqrt(2.0) * Y.imag
    return TH, PH, H


def stats(TH, H, multiplier=1.0):
    w = np.sin(TH)  # area weight; mean over sphere
    w /= w.sum()
    P = H * multiplier
    mean = float((P * w).sum())
    rms = float(math.sqrt((P ** 2 * w).sum()))
    nlat = H.shape[0]
    north = H[:nlat // 2][::-1]
    south = H[nlat // 2 + (nlat % 2):]
    n = min(north.shape[0], south.shape[0])
    parity = float(np.corrcoef(north[:n].ravel(), south[:n].ravel())[0, 1])
    return {"mean": mean, "rms": rms, "min": float(P.min()),
            "max": float(P.max()),
            "half_range": float((P.max() - P.min()) / 2), "parity": parity}


def main(files, multiplier=1.0):
    if not HAVE_SPH:
        print("scipy.special.sph_harm_y unavailable: cannot verify")
        return 2
    ok = True
    for path in files:
        header, modes = read_flux(path)
        TH, _, H = reconstruct(modes)
        s = stats(TH, H, multiplier)
        zero_mean = abs(s["mean"]) < 1e-10 * max(1.0, abs(s["rms"]))
        status = "PASS-ZERO-MEAN" if zero_mean else "FAIL-MEAN-NONZERO"
        ok &= zero_mean
        print(f"{os.path.basename(path)}: {status}")
        print(f"  modes={len(modes)} mult={multiplier} mean={s['mean']:.3e} "
              f"rms={s['rms']:.6f} min={s['min']:.6f} max={s['max']:.6f} "
              f"half_range={s['half_range']:.6f} parity={s['parity']:+.3f}")
    return 0 if ok else 1


if __name__ == "__main__":
    mult = 1.0
    args = sys.argv[1:]
    if args[:1] == ["--multiplier"]:
        mult = float(args[1])
        args = args[2:]
    if not args:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "xshells")
        args = [os.path.join(base, "protocol_W", "cmb_Y21.txt"),
                os.path.join(base, "protocol_W", "cmb_Y22.txt"),
                os.path.join(base, "protocol_P", "cmb_Y10_Y30.txt")]
    sys.exit(main(args, mult))
