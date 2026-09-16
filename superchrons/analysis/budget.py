"""Campaign budget from measured throughput. Paper main-29 §F7, Eqs. (F9)–(F11).

vn = measured sim-time units per wall hour on n nodes.
Tneed = equilibration + analyzed exposure, same units.
  tn  = Tneed/vn + toverhead          (F9)   wall hours for one trajectory
  Cn  = n * tn                        (F10)  node-hours per trajectory
  en  = vn/(n*v1)                     (F11)  parallel efficiency vs one node
For equal-duration jobs with m granted nodes and n per trajectory:
  k = floor(m/n) at once; campaign ~= ceil(Nrun/k)*tn + queues/failures.
Prefer high vn/n when node-hours limit; more nodes when memory or elapsed
time justifies the efficiency cost. If target is 20*tau_u, convert tau_u = L/U
into code time with a stated reference velocity first.
"""
import math


def _check_int(name, v):
    if isinstance(v, bool) or not isinstance(v, (int,)) or v <= 0:
        raise ValueError(f"{name} must be a positive integer, got {v!r}")
    return v


def _check_num(name, v, minimum=0.0, strict=False):
    if isinstance(v, bool) or not isinstance(v, (int, float)) \
            or not math.isfinite(v):
        raise ValueError(f"{name} must be finite, got {v!r}")
    if strict and not v > minimum:
        raise ValueError(f"{name} must be > {minimum}, got {v!r}")
    if not strict and not v >= minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {v!r}")
    return float(v)


def trajectory_hours(Tneed, vn, toverhead=0.0):
    Tneed = _check_num("Tneed", Tneed, 0.0)
    vn = _check_num("vn", vn, 0.0, strict=True)
    toverhead = _check_num("toverhead", toverhead, 0.0)
    return Tneed / vn + toverhead


def node_hours(n, tn):
    _check_int("n", n)
    tn = _check_num("tn", tn, 0.0)
    return n * tn


def efficiency(vn, n, v1):
    vn = _check_num("vn", vn, 0.0, strict=True)
    _check_int("n", n)
    v1 = _check_num("v1", v1, 0.0, strict=True)
    return vn / (n * v1)


def campaign_hours(Nrun, m, n, tn):
    _check_int("Nrun", Nrun)
    _check_int("m", m)
    _check_int("n", n)
    tn = _check_num("tn", tn, 0.0)
    if m < n:
        raise ValueError(f"granted nodes m={m} < per-trajectory n={n}")
    k = m // n
    return math.ceil(Nrun / k) * tn, k


if __name__ == "__main__":
    # Placeholder self-check (not a measurement).
    v1, v2 = 1.0, 1.7
    tn = trajectory_hours(20.0, v2, toverhead=0.5)
    assert math.isclose(tn, 20.0 / 1.7 + 0.5)
    assert math.isclose(node_hours(2, tn), 2 * tn)
    assert math.isclose(efficiency(v2, 2, v1), 0.85)
    camp, k = campaign_hours(16, m=4, n=2, tn=tn)
    assert k == 2 and math.isclose(camp, 8 * tn)
    # Rejection checks (fix §6): NaN/inf/negative/fractional/zero-work.
    bad = [lambda: trajectory_hours(20.0, 0.0),
           lambda: trajectory_hours(-1.0, 1.0),
           lambda: trajectory_hours(float("nan"), 1.0),
           lambda: trajectory_hours(20.0, float("inf")),
           lambda: node_hours(0, 1.0), lambda: node_hours(2.5, 1.0),
           lambda: node_hours(2, -1.0),
           lambda: efficiency(1.7, 2, 0.0),
           lambda: campaign_hours(16, m=1, n=2, tn=1.0),
           lambda: campaign_hours(0, m=4, n=2, tn=1.0),
           lambda: campaign_hours(16, m=4, n=2, tn=float("nan"))]
    for i, fn in enumerate(bad):
        try:
            fn()
            raise SystemExit(f"rejection check {i} FAILED")
        except ValueError:
            pass
    # Zero-work request is valid and costs only overhead.
    assert trajectory_hours(0.0, 1.5, toverhead=0.5) == 0.5
    print("budget checks pass")
