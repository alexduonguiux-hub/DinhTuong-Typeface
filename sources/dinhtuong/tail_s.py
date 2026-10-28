"""R5c (27/10 16:08 'giảm cong … giảm góc nhọn, chứ không phải như vừa rồi'): the house tail with the SAME reach
(same vertical cut x, same tip y as R5) but a less curved inner edge.

R5: the inner edge leaves the counter at its top point (horizontal tangent) on one compass arc and meets the
vertical cut 35 deg off vertical -> a needle-like tip.
R5c: the inner edge follows the counter a little further round (to S, on the counter's own curve, so the join
stays smooth), then ONE compass arc tangent to the counter at S runs to the SAME tip T. Leaving later, the arc
is shorter and flatter and meets the cut at TIP_ANG (> 35 deg): the tip opens, the tail keeps its length.
S is solved so the angle at T equals TIP_ANG. The counter near its top is taken as its cap circle (radius =
half the counter width), which is exact for the R3 rings (C G) and the S rings' caps.
"""
import math

TIP_ANG = 50.0


def _cubic_arc(cx, cy, r, a0, a1):
    """one cubic for a circular arc a0 -> a1 (radians, |a1-a0| <= 90 deg)."""
    k = 4.0 / 3.0 * math.tan((a1 - a0) / 4.0)
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p3 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    p1 = (p0[0] - k * r * math.sin(a0), p0[1] + k * r * math.cos(a0))
    p2 = (p3[0] + k * r * math.sin(a1), p3[1] - k * r * math.cos(a1))
    return p1, p2, p3


def solve(dx, dy, rc, ang=None, ry=None):
    """local frame: counter top at (0, 0), counter cap circle centre (0, -rc); tip T = (dx, -dy) (dx > 0, dy > 0).
    Returns (beta, S, C, rho, end_angle_deg)."""
    ang = TIP_ANG if ang is None else ang
    T = (dx, -dy)

    rx = rc
    ry = rc if ry is None else ry

    def arc_for(beta):
        S = (rx * math.sin(beta), -ry + ry * math.cos(beta))   # on the counter ellipse (centre (0, -ry))
        nn = (math.sin(beta) / rx, math.cos(beta) / ry)
        ln = math.hypot(*nn)
        n = (nn[0] / ln, nn[1] / ln)                         # counter's outward normal at S
        rcur = (rx * rx * math.cos(beta) ** 2 + ry * ry * math.sin(beta) ** 2) ** 1.5 / (rx * ry)
        d = (S[0] - T[0], S[1] - T[1])
        den = 2 * (n[0] * d[0] + n[1] * d[1])
        if den <= 1e-9:
            return None
        rho = (d[0] ** 2 + d[1] ** 2) / den                  # circle tangent to the counter at S, through T
        if rho < rcur:                                        # must be flatter than the counter (leaves it outward)
            return None
        C = (S[0] - rho * n[0], S[1] - rho * n[1])
        if abs(math.hypot(T[0] - C[0], T[1] - C[1]) - rho) > 1e-6 * max(1, rho):
            return None
        # tangent at T, angle off vertical
        vx, vy = T[0] - C[0], T[1] - C[1]
        e = math.degrees(math.atan2(abs(vy), abs(vx)))         # radius direction off horizontal = tangent off vertical
        return S, C, rho, e

    lo, hi = 0.0, math.radians(80)
    best = None
    for _ in range(60):
        mid = (lo + hi) / 2
        r = arc_for(mid)
        if r is None:
            hi = mid; continue
        best = (mid,) + r
        if r[3] < ang:
            lo = mid
        else:
            hi = mid
    return best


def region(cx, cedge, xt, tip, rc, side, vdir, ang=None, ry=None, ybot=None):
    """the white to remove, as one closed path (absolute coords)."""
    sx = 1 if side == 'r' else -1
    sy = 1 if vdir == 'up' else -1
    dx, dy = abs(xt - cx), abs(cedge - tip)
    beta, S, C, rho, e = solve(dx, dy, rc, ang, ry)
    X = lambda u: cx + sx * u
    Y = lambda w: cedge + sy * w
    wb = -dy if ybot is None else sy * (ybot - cedge)      # like R5's disk, the white runs down to its old centre line
    a0 = math.atan2(S[1] - C[1], S[0] - C[0])
    a1 = math.atan2(-dy - C[1], dx - C[0])
    p1, p2, p3 = _cubic_arc(C[0], C[1], rho, a0, a1)
    path = [('M', X(0), Y(S[1])), ('L', X(S[0]), Y(S[1])),
            ('C', X(p1[0]), Y(p1[1]), X(p2[0]), Y(p2[1]), X(p3[0]), Y(p3[1])),
            ('L', X(dx), Y(wb)), ('L', X(0), Y(wb)), ('Z',)]
    return path, dict(beta=math.degrees(beta), rho=rho, end=e, S=(X(S[0]), Y(S[1])), C=(X(C[0]), Y(C[1])))
