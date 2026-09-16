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


def detect_events(t, Dsurf, Dref, lo=0.25, hi=0.6, main=0.4, tau_u=None):
    """Polarity-set event detector (fix §5: implemented, not a stub).

    Committed sets: |Dsurf| > main*Dref sustained for tau_u. A reversal is a
    committed-set to opposite committed-set transition; an excursion returns
    to the origin set; anything never committing elsewhere is 'multipolar/
    uncommitted'. Returns dict with committed intervals, reversals, excursions,
    uncommitted count, and the same catalog at lo/hi thresholds. Timestamps
    required (no interpolation of missing data — drop NaN samples explicitly).
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

    def catalog(thr):
        committed = []  # (sign, t_enter, t_exit)
        i, n = 0, len(t)
        while i < n:
            if np.isnan(D[i]) or abs(D[i]) <= thr * Dref:
                i += 1
                continue
            s = 1 if D[i] > 0 else -1
            j = i
            while (j + 1 < n and not np.isnan(D[j + 1])
                   and np.sign(D[j + 1]) == s and abs(D[j + 1]) > thr * Dref):
                j += 1
            if t[j] - t[i] >= tau_u:
                committed.append((s, float(t[i]), float(t[j])))
            i = j + 1
        reversals, excursions = [], []
        for (s0, _, e0), (s1, b1, e1) in zip(committed, committed[1:]):
            (reversals if s1 != s0 else excursions).append((float(e0), float(b1)))
        return {"committed": committed, "reversals": reversals,
                "excursions": excursions}

    out = {"main": catalog(main), "lo": catalog(lo), "hi": catalog(hi)}
    out["uncommitted_intervals"] = max(0, len(out["main"]["committed"]) - 1
                                       - len(out["main"]["reversals"])
                                       - len(out["main"]["excursions"]))
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
    print("toy + hardening checks pass")
