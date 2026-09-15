"""Executable paper code from Appendix F §F5 + event/budget check stubs.

projected_drag and poisson_rate_interval are transcribed from the manuscript
(including its toy checks). Everything else is a stub marked TODO until the
solver adapters exist. Solver-independent: runs anywhere with numpy/scipy.
"""
import numpy as np
from scipy.stats import chi2


def projected_drag(u, Q, W, gamma):
    assert gamma >= 0
    gram = Q.conj().T @ W @ Q
    assert np.allclose(gram, np.eye(Q.shape[1]))
    amp = Q.conj().T @ (W @ u)
    force = -gamma * (Q @ amp)
    power = np.vdot(u, W @ force).real
    return force, power


def poisson_rate_interval(n, exposure, a=0.05):
    if n < 0 or int(n) != n or exposure <= 0:
        raise ValueError("Invalid count/exposure")
    if not 0 < a < 1:
        raise ValueError("Invalid significance")
    low = 0.0 if n == 0 else (chi2.ppf(a / 2, 2 * n) / (2 * exposure))
    high = chi2.ppf(1 - a / 2, 2 * (n + 1))
    return low, high / (2 * exposure)


def dipole_budget_error(d_surf_dot, AD, OD):
    """Eq. (F3): rms(Ddotsurf - AD - OD) / (rms(AD) + rms(OD)). Target < 0.01."""
    num = np.sqrt(np.mean((np.asarray(d_surf_dot) - np.asarray(AD)
                           - np.asarray(OD)) ** 2))
    den = (np.sqrt(np.mean(np.asarray(AD) ** 2))
           + np.sqrt(np.mean(np.asarray(OD) ** 2)))
    if den == 0:
        return np.inf  # report absolute error instead (paper §F1)
    return num / den


def detect_events(t, Dsurf, Dref, lo=0.25, hi=0.6, main=0.4, tau_u=None):
    """TODO: event detector stub. Polarity sets at |Dsurf| > main*Dref with
    persistence tau_u; reversal = committed-set to committed-set; excursion =
    return to origin set; multipolar occupancy counted separately. Sensitivity
    at thresholds lo/hi applied identically to every treatment. Test on
    synthetic excursions, persistent reversals, irregular sampling, truncated
    runs before production (paper §F5)."""
    raise NotImplementedError


if __name__ == "__main__":
    # Toy checks from the manuscript (not geodynamo measurements).
    W = np.diag([2.0, 3.0])
    Q = np.array([[1 / np.sqrt(2)], [0.0]])
    u = np.array([2.0, 1.0])
    _, power = projected_drag(u, Q, W, 0.3)
    assert np.isclose(power, -2.4)
    lo, hi = poisson_rate_interval(0, 10.0)
    assert lo == 0.0 and np.isclose(hi, 0.3688879454)
    print("toy checks pass")
