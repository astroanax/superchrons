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


def trajectory_hours(Tneed, vn, toverhead=0.0):
    if vn <= 0 or Tneed < 0 or toverhead < 0:
        raise ValueError("vn > 0, Tneed/toverhead >= 0 required")
    return Tneed / vn + toverhead


def node_hours(n, tn):
    return n * tn


def efficiency(vn, n, v1):
    return vn / (n * v1)


def campaign_hours(Nrun, m, n, tn):
    if n <= 0 or m < n or Nrun <= 0:
        raise ValueError("need 0 < n <= m, Nrun > 0")
    k = m // n
    return math.ceil(Nrun / k) * tn, k


if __name__ == "__main__":
    # Self-check with placeholder numbers (not a measurement).
    v1, v2 = 1.0, 1.7
    tn = trajectory_hours(20.0, v2, toverhead=0.5)
    assert math.isclose(tn, 20.0 / 1.7 + 0.5)
    assert math.isclose(node_hours(2, tn), 2 * tn)
    assert math.isclose(efficiency(v2, 2, v1), 0.85)
    camp, k = campaign_hours(16, m=4, n=2, tn=tn)
    assert k == 2 and math.isclose(camp, 8 * tn)
    print("budget checks pass")
