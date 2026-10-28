"""R16 (28/10 02:18, designer: 'điều chỉnh kerning chữ và số cho phù hợp'): figures are SPACED, not kerned, to one
optical white: every side of every figure leaves the same depth-limited white (depth 40, the house spacing measure)
as the 0's side in the same weight (0 keeps its R14 sidebearing). Before: sides ranged +11..+57 over H's white
(5's left +57, 3's left +35, 2's left +30). Interactions (7 over 4 ...) are left to the kerning pass."""
import numpy as np
import booleng
import flare

D = 40.0


def _profile(g, y0=0, y1=700, step=5):
    """left / right ink extremes per row (glyph body coordinates), NaN where the row is empty."""
    polys = flare._flat(booleng.evaluate(g.ops))
    L, R = [], []
    for y in np.arange(y0 + step / 2, y1, step):
        xs = []
        for P in polys:
            n = len(P)
            for i in range(n):
                (x1, y1_), (x2, y2) = P[i], P[(i + 1) % n]
                if (y1_ > y) != (y2 > y):
                    xs.append(x1 + (y - y1_) * (x2 - x1) / (y2 - y1_))
        L.append(min(xs) if xs else np.nan); R.append(max(xs) if xs else np.nan)
    return np.array(L), np.array(R)


def _side_white(prof, sb):
    w = prof + sb
    m = np.nanmin(w)
    w = np.where(np.isnan(w), m + D, w)
    return np.minimum(w, m + D).mean()


def apply(out, figs='0123456789', ref='0'):
    z = out[ref]
    zl, zr = _profile(z)
    target = _side_white(zl, z.lsb)          # the 0's left white (= its right white: 0 is symmetric)
    for d in figs:
        if d == ref or d not in out:
            continue
        g = out[d]
        L, R = _profile(g)
        wl = _side_white(L, 0.0)                         # white with lsb 0: the ink's own depth profile
        wr = _side_white(g.body - R, 0.0)
        g.lsb = round(target - wl)
        g.rsb = round(target - wr)
    return target
