"""Executable paper code from Appendix F §F5 + hardened analysis helpers.

projected_drag / poisson_rate_interval follow the manuscript; the hardening
(Hermitian PD check, shape/finite validation, time weighting, abs+normalized
errors, implemented event detector) addresses audit fixes §5. Solver-independent.
"""
import numpy as np
from scipy.stats import chi2

_COMPLEX_OK = "complex-ok"  # sentinel for documented complex convention


def _as_vector(x, name):
    a = np.asarray(x)
    if a.ndim != 1:
        raise ValueError(f"{name} must be 1-D, got shape {a.shape}")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must be finite")
    return a


def _as_matrix(Q, name="Q"):
    A = np.asarray(Q)
    if A.ndim != 2 or 0 in A.shape:
        raise ValueError(f"{name} must be a non-empty 2-D matrix")
    if not np.all(np.isfinite(A)):
        raise ValueError(f"{name} must be finite")
    return A


def _check_hermitian_pd(W):
    W = np.asarray(W)
    if W.ndim != 2 or W.shape[0] != W.shape[1]:
        raise ValueError("W must be square")
    if not np.all(np.isfinite(W)):
        raise ValueError("W must be finite")
    if not np.allclose(W, W.conj().T):
        raise ValueError("W must be Hermitian")
    eig = np.linalg.eigvalsh(W if np.isrealobj(W)
                             else (W + W.conj().T) / 2).real
    if not np.all(eig > 0):
        raise ValueError("W must be positive-definite")
    return W


def projected_drag(u, Q, W, gamma, convention="real"):
    """Energy-metric projection drag. convention: 'real' or 'complex-ok'
    (complex inputs only with documented complex spherical-harmonic handling)."""
    if not np.isscalar(gamma) or not np.isfinite(gamma) or gamma < 0:
        raise ValueError("gamma must be a finite scalar >= 0")
    u = _as_vector(u, "u")
    Q = _as_matrix(Q)
    W = _check_hermitian_pd(W)
    if Q.shape[0] != W.shape[0] or u.shape[0] != W.shape[0]:
        raise ValueError(
            f"shape mismatch: W {W.shape}, Q {Q.shape}, u {u.shape}")
    if convention != _COMPLEX_OK and (
            np.iscomplexobj(u) or np.iscomplexobj(Q) or np.iscomplexobj(W)):
        raise ValueError("complex inputs need convention='complex-ok'")
    gram = Q.conj().T @ W @ Q
    if not np.allclose(gram, np.eye(Q.shape[1])):
        raise ValueError("Q must be W-orthonormal (Q^H W Q = I)")
    amp = Q.conj().T @ (W @ u)
    force = -gamma * (Q @ amp)
    power = np.vdot(u, W @ force).real
    if not np.isfinite(power):
        raise ValueError("non-finite power")
    return force, power


def poisson_rate_interval(n, exposure, a=0.05):
    if (not isinstance(n, (int, np.integer)) or n < 0
            or not np.isfinite(exposure) or exposure <= 0
            or not np.isfinite(a) or not 0 < a < 1):
        raise ValueError("need integer n >= 0, finite exposure > 0, 0 < a < 1")
    low = 0.0 if n == 0 else (chi2.ppf(a / 2, 2 * n) / (2 * exposure))
    high = chi2.ppf(1 - a / 2, 2 * (n + 1)) / (2 * exposure)
    return low, high


def _rms(a, t=None):
    """RMS; with timestamps t uses trapezoidal time-weighting (fix §5:
    irregular sampling must not silently use sample averaging)."""
    a = np.asarray(a, dtype=float)
    if t is None:
        return float(np.sqrt(np.mean(a ** 2)))
    t = np.asarray(t, dtype=float)
    if a.shape != t.shape:
        raise ValueError(f"shape mismatch: data {a.shape} vs t {t.shape}")
    if np.any(np.diff(t) <= 0):
        raise ValueError("t must be strictly increasing")
    return float(np.sqrt(np.trapezoid(a ** 2, t) / (t[-1] - t[0])))


def dipole_budget_error(d_surf_dot, AD, OD, t=None):
    """Eq. (F3). Returns (eps_normalized, abs_residual_rms). When the
    denominator is zero the normalized error is inf AND the absolute residual
    is returned for interpretation (fix §5). Shapes must match exactly —
    no broadcasting."""
    d = np.asarray(d_surf_dot, dtype=float)
    A = np.asarray(AD, dtype=float)
    O = np.asarray(OD, dtype=float)
    if not (d.shape == A.shape == O.shape):
        raise ValueError(f"shape mismatch: {d.shape} vs {A.shape} vs {O.shape}")
    for name, a in [("d_surf_dot", d), ("AD", A), ("OD", O)]:
        if not np.all(np.isfinite(a)):
            raise ValueError(f"{name} must be finite")
    if t is not None:
        t = np.asarray(t, dtype=float)
        if t.shape != d.shape:
            raise ValueError(f"shape mismatch: data {d.shape} vs t {t.shape}")
        if np.any(np.diff(t) <= 0):
            raise ValueError("t must be strictly increasing")
    abs_err = _rms(d - A - O, t)
    den = _rms(A, t) + _rms(O, t)
    if den == 0:
        return np.inf, abs_err
    return abs_err / den, abs_err


def detect_events(t, Dsurf, Dref, lo=0.25, hi=0.6, main=0.4, tau_u=None,
                    max_gap_dt=None):
    """Polarity-set event detector (review round 2: gap-safe, censoring-aware).

    Rules:
    - Non-finite Dsurf values are SPLIT points, never bridged. A NaN gap
      between +polarity samples does NOT make an excursion; the two sides
      become separate committed spans with an unresolved gap between them.
    - Time gaps longer than max_gap_dt (default: tau_u) also split the
      record. Two samples 100 time units apart never form one "sustained"
      interval.
    - inf values are rejected outright (ValueError): a committed interval
      must be built from finite samples only.
    - Committed span reports (sign, t_enter, t_satisfied, t_exit): t_enter
      is first threshold crossing; t_satisfied is when the dwell
      requirement is met. Never conflate the two.
    - uncommitted_spans lists record portions (leading, inter-commit,
      trailing tail) never assigned to a committed set, each >= tau_u or a
      trailing tail of any length, with a reason ('weak-field',
      'missing-data', 'tail'). These are NOT called reversals, excursions,
      or multipolar states — they are unresolved record, counted honestly.
    - Sensitivity catalogs at lo/hi use the identical procedure.
    """
    t = np.asarray(t, dtype=float)
    D = np.asarray(Dsurf, dtype=float)
    if t.shape != D.shape or t.ndim != 1:
        raise ValueError("t and Dsurf must be matching 1-D arrays")
    if np.any(np.diff(t) <= 0):
        raise ValueError("t must be strictly increasing")
    if not np.isfinite(Dref) or Dref <= 0:
        raise ValueError("Dref must be finite and > 0")
    if tau_u is None or not np.isfinite(tau_u) or tau_u <= 0:
        raise ValueError("tau_u must be finite and > 0")
    if np.any(np.isinf(D)):
        raise ValueError("Dsurf contains inf: committed intervals require "
                         "finite samples only")
    if max_gap_dt is None:
        max_gap_dt = tau_u
    if not np.isfinite(max_gap_dt) or max_gap_dt <= 0:
        raise ValueError("max_gap_dt must be finite and > 0")

    def split_segments():
        """Split record at NaN samples and at time gaps > max_gap_dt.
        Returns list of (idx_array,) segments of finite, well-sampled data."""
        finite = np.isfinite(D)
        segs, cur = [], []
        for i in range(len(t)):
            if not finite[i]:
                if cur:
                    segs.append(np.array(cur))
                    cur = []
                continue
            if cur and t[i] - t[cur[-1]] > max_gap_dt:
                segs.append(np.array(cur))
                cur = []
            cur.append(i)
        if cur:
            segs.append(np.array(cur))
        return segs

    def catalog(thr):
        committed = []  # (sign, t_enter, t_satisfied, t_exit)
        for seg in split_segments():
            i = 0
            while i < len(seg):
                k = seg[i]
                if abs(D[k]) <= thr * Dref:
                    i += 1
                    continue
                s = 1 if D[k] > 0 else -1
                j = i
                while (j + 1 < len(seg)
                       and np.sign(D[seg[j + 1]]) == s
                       and abs(D[seg[j + 1]]) > thr * Dref):
                    j += 1
                # dwell: satisfied at first index with t - t_enter >= tau_u
                sat = None
                for m in range(i, j + 1):
                    if t[seg[m]] - t[seg[i]] >= tau_u:
                        sat = m
                        break
                if sat is not None:
                    committed.append((s, float(t[seg[i]]),
                                      float(t[seg[sat]]), float(t[seg[j]])))
                i = j + 1
        committed.sort(key=lambda c: c[1])
        reversals, excursions, extra_spans = [], [], []
        pairs = list(zip(committed, committed[1:]))
        for (s0, _, _, e0), (s1, b1, _, _) in pairs:
            # A transition links two spans ONLY across well-sampled record:
            # a missing-data or over-long gap between them is unresolved
            # record, never a reversal/excursion (review round-2 case a).
            if _gap_has_nan(e0, b1) or (b1 - e0) > max_gap_dt:
                extra_spans.append((float(e0), float(b1), "missing-data"
                                    if _gap_has_nan(e0, b1) else "gap"))
            elif s1 != s0:
                reversals.append((float(e0), float(b1)))
            else:
                excursions.append((float(e0), float(b1)))
        # Uncommitted spans: leading, inter-commit, trailing tail. A span
        # counts if it reaches tau_u, or if it is the trailing tail (a
        # truncated tail is censored record however short).
        spans = []
        bounds = [(c[1], c[3]) for c in committed]
        t_first = float(t[np.isfinite(D)][0])
        edges = [(t_first, bounds[0][0])] if bounds else []
        edges += [(bounds[k][1], bounds[k + 1][0])
                  for k in range(len(bounds) - 1)]
        for (a, b) in edges:
            reason = ("missing-data" if _gap_has_nan(a, b)
                      else "weak-field")
            if b - a >= tau_u:
                spans.append((a, b, reason))
        if bounds:
            tail_t0 = bounds[-1][1]
            if tail_t0 < t[np.isfinite(D)][-1]:
                spans.append((float(tail_t0),
                              float(t[np.isfinite(D)][-1]), "tail"))
        elif np.any(np.isfinite(D)):
            spans.append((float(t[np.isfinite(D)][0]),
                          float(t[np.isfinite(D)][-1]), "uncommitted-record"))
        spans.extend(extra_spans)
        return {"committed": committed, "reversals": reversals,
                "excursions": excursions, "uncommitted_spans": spans}

    def _gap_has_nan(a, b):
        if a is None:
            lo_i = 0
        else:
            lo_i = np.searchsorted(t, a, side="right")
        hi_i = np.searchsorted(t, b, side="left")
        return bool(np.any(~np.isfinite(D[lo_i:hi_i])))

    out = {"main": catalog(main), "lo": catalog(lo), "hi": catalog(hi)}
    out["uncommitted_intervals"] = len(out["main"]["uncommitted_spans"])
    return out


if __name__ == "__main__":
    # Manuscript toy checks (not geodynamo measurements).
    W = np.diag([2.0, 3.0])
    Q = np.array([[1 / np.sqrt(2)], [0.0]])
    u = np.array([2.0, 1.0])
    _, power = projected_drag(u, Q, W, 0.3)
    assert np.isclose(power, -2.4)
    lo, hi = poisson_rate_interval(0, 10.0)
    assert lo == 0.0 and np.isclose(hi, 0.3688879454)

    # Hardening checks (fix §5).
    try:
        projected_drag(u, Q, np.array([[1.0, 2.0], [3.0, 4.0]]), 0.3)
        raise SystemExit("W-Hermitian check FAILED")
    except ValueError:
        pass
    try:
        projected_drag([1.0, 2.0, 3.0], Q, W, 0.3)
        raise SystemExit("shape check FAILED")
    except ValueError:
        pass
    eps, abs_err = dipole_budget_error([1.0, 2.0], [1.0, 2.0], [0.0, 0.0])
    assert eps == 0.0 and abs_err == 0.0
    eps, abs_err = dipole_budget_error([1.0], [0.0], [0.0])
    assert eps == np.inf and abs_err == 1.0
    try:
        dipole_budget_error([1.0, 2.0], [1.0], [0.0, 0.0])
        raise SystemExit("broadcast check FAILED")
    except ValueError:
        pass
    # Synthetic reversal: +polarity then -polarity, tau_u = 1.
    t = np.arange(0.0, 10.0, 0.5)
    D = np.where(t < 5, 1.0, -1.0)
    ev = detect_events(t, D, Dref=1.0, tau_u=1.0)
    assert len(ev["main"]["reversals"]) == 1, ev
    # Synthetic excursion: brief opposite blip never commits (shorter than
    # tau_u), flanked by origin-set committed intervals.
    D2 = np.where(t == 3.0, -1.0, 1.0)
    ev2 = detect_events(t, D2, Dref=1.0, tau_u=1.0)
    assert len(ev2["main"]["excursions"]) == 1 and not ev2["main"]["reversals"], ev2
    # Review round-2 regression cases:
    # (a) +polarity, NaN gap, +polarity: NO excursion across the gap.
    D3 = np.array([1.0, 1.0, 1.0, np.nan, np.nan, 1.0, 1.0, 1.0])
    t3 = np.arange(8.0) * 0.5
    ev3 = detect_events(t3, D3, Dref=1.0, tau_u=1.0)
    assert not ev3["main"]["excursions"] and not ev3["main"]["reversals"], ev3
    assert any(s[2] == "missing-data" for s in ev3["main"]["uncommitted_spans"]), ev3
    # (b) two +samples 100 units apart: never one sustained interval.
    ev4 = detect_events([0.0, 100.0], [1.0, 1.0], Dref=1.0, tau_u=1.0)
    assert not ev4["main"]["committed"], ev4
    # (c) committed span + weak-field tail: tail reported, not zero spans.
    D5 = np.array([1.0, 1.0, 1.0, 0.1, 0.1, 0.05])
    t5 = np.arange(6.0) * 0.5
    ev5 = detect_events(t5, D5, Dref=1.0, tau_u=1.0)
    assert len(ev5["main"]["uncommitted_spans"]) >= 1, ev5
    # (d) inf rejected outright.
    try:
        detect_events([0.0, 0.5, 1.0], [1.0, np.inf, 1.0], Dref=1.0, tau_u=1.0)
        raise SystemExit("inf check FAILED")
    except ValueError:
        pass
    print("toy + hardening checks pass")
