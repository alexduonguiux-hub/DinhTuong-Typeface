"""Outline hygiene applied to every finished glyph (after the boolean ops, on the integer grid).

  1. round to integer units (what the font stores) and drop zero-length segments
  2. runs of >=3 short straight segments that turn gently (polygonal arcs left over from
     tessellated shapes) are re-fitted as smooth cubic curves (Schneider-style, error <= 1u)
  3. micro steps: a straight segment shorter than MICRO between two edges it turns away from
     (stair-step / ledge on an edge) is collapsed into the intersection of its neighbours
  4. consecutive collinear lines are merged
The result is drawn into the CFF exactly as before (same segment tuples).
"""
import math

MICRO = 6.5          # units; anything shorter that turns both ways is a defect, not design
CHAIN_SEG = 32.0     # max length of a 'tessellation' segment
CHAIN_TURN = 40.0    # max turn between chain segments (deg)
FIT_ERR = 1.5


def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _add(a, b): return (a[0] + b[0], a[1] + b[1])
def _mul(a, k): return (a[0] * k, a[1] * k)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1]
def _len(a): return math.hypot(a[0], a[1])


def _norm(a):
    l = _len(a)
    return (a[0] / l, a[1] / l) if l > 1e-9 else (0.0, 0.0)


def _ang(a): return math.degrees(math.atan2(a[1], a[0]))
def _turn(a, b): return abs((_ang(b) - _ang(a) + 180) % 360 - 180)


# segment = ['L', p0, p1] or ['C', p0, c1, c2, p1]
def _start_tan(s):
    if s[0] == 'L': return _sub(s[2], s[1])
    for q in (s[2], s[3], s[4]):
        if _len(_sub(q, s[1])) > 1e-6: return _sub(q, s[1])
    return (1, 0)


def _end_tan(s):
    if s[0] == 'L': return _sub(s[2], s[1])
    e = s[4]
    for q in (s[3], s[2], s[1]):
        if _len(_sub(e, q)) > 1e-6: return _sub(e, q)
    return (1, 0)


def _end(s): return s[-1]
def _seglen(s): return _len(_sub(s[-1], s[1]))


def _to_cyc(cont):
    segs, cur, start = [], None, None
    for s in cont:
        if s[0] == 'M':
            cur = start = (float(s[1]), float(s[2]))
        elif s[0] == 'L':
            p = (float(s[1]), float(s[2])); segs.append(['L', cur, p]); cur = p
        elif s[0] == 'C':
            c1, c2, p = (s[1], s[2]), (s[3], s[4]), (float(s[5]), float(s[6]))
            segs.append(['C', cur, c1, c2, p]); cur = p
        elif s[0] == 'Z':
            if start is not None and cur is not None and _len(_sub(cur, start)) > 1e-6:
                segs.append(['L', cur, start])
    return segs


def _from_cyc(segs):
    if not segs: return []
    out = [('M',) + tuple(segs[0][1])]
    for s in segs:
        if s[0] == 'L': out.append(('L',) + tuple(s[2]))
        else: out.append(('C',) + tuple(s[2]) + tuple(s[3]) + tuple(s[4]))
    if out[-1][0] == 'L' and tuple(out[-1][1:]) == tuple(out[0][1:]):
        out.pop()
    out.append(('Z',))
    return out


def _round(segs):
    r = lambda p: (float(round(p[0])), float(round(p[1])))
    out = []
    for s in segs:
        t = [s[0]] + [r(p) for p in s[1:]]
        if t[0] == 'L' and t[1] == t[2]:
            continue
        if t[0] == 'C' and t[1] == t[4] and t[2] == t[1] and t[3] == t[1]:
            continue
        out.append(t)
    # re-link (rounding keeps endpoints shared since they round identically)
    return out


# ---------------------------------------------------------------- curve fitting
def _bez(p0, c1, c2, p3, t):
    mt = 1 - t
    return (mt**3*p0[0] + 3*mt*mt*t*c1[0] + 3*mt*t*t*c2[0] + t**3*p3[0],
            mt**3*p0[1] + 3*mt*mt*t*c1[1] + 3*mt*t*t*c2[1] + t**3*p3[1])


def _fit(pts, t0, t1):
    """one cubic through pts[0]..pts[-1] with unit tangents t0 (out of start), t1 (into end)."""
    d = [0.0]
    for i in range(1, len(pts)): d.append(d[-1] + _len(_sub(pts[i], pts[i - 1])))
    L = d[-1] or 1.0
    u = [x / L for x in d]
    p0, p3 = pts[0], pts[-1]
    C = [[0, 0], [0, 0]]; X = [0, 0]
    for p, t in zip(pts, u):
        b0, b1, b2, b3 = (1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3
        A1, A2 = _mul(t0, b1), _mul(t1, -b2)
        C[0][0] += _dot(A1, A1); C[0][1] += _dot(A1, A2); C[1][1] += _dot(A2, A2)
        tmp = _sub(p, _add(_mul(p0, b0 + b1), _mul(p3, b2 + b3)))
        X[0] += _dot(A1, tmp); X[1] += _dot(A2, tmp)
    C[1][0] = C[0][1]
    det = C[0][0] * C[1][1] - C[0][1] * C[1][0]
    if abs(det) > 1e-9:
        a1 = (X[0] * C[1][1] - X[1] * C[0][1]) / det
        a2 = (C[0][0] * X[1] - C[1][0] * X[0]) / det
    else:
        a1 = a2 = L / 3
    if a1 < L * 0.05 or a2 < L * 0.05:
        a1 = a2 = L / 3
    c1, c2 = _add(p0, _mul(t0, a1)), _sub(p3, _mul(t1, a2))
    err, ei = 0, 0
    for i, (p, t) in enumerate(zip(pts, u)):
        e = _len(_sub(_bez(p0, c1, c2, p3, t), p))
        if e > err: err, ei = e, i
    return (c1, c2), err, ei


def _fit_rec(pts, t0, t1, depth=0):
    (c1, c2), err, ei = _fit(pts, t0, t1)
    # split only if the error is real and both halves stay substantial (no confetti curves)
    if err <= FIT_ERR or len(pts) < 12 or depth > 3:
        return [['C', pts[0], c1, c2, pts[-1]]]
    ei = max(6, min(len(pts) - 7, ei))
    tm = _norm(_sub(pts[ei + 1], pts[ei - 1]))
    return _fit_rec(pts[:ei + 1], t0, tm, depth + 1) + _fit_rec(pts[ei:], tm, t1, depth + 1)


def _smooth_joints(segs):
    """after rounding, make handles at curve-curve joints collinear again (G1), unless the
    joint is a real corner (> 30 deg)."""
    n = len(segs)
    for i in range(n):
        a, b = segs[i], segs[(i + 1) % n]
        if a[0] != 'C' or b[0] != 'C': continue
        P = a[4]
        ta = next((_sub(P, q) for q in (a[3], a[2], a[1]) if _len(_sub(P, q)) >= 4), _sub(P, a[1]))
        tb = next((_sub(q, P) for q in (b[2], b[3], b[4]) if _len(_sub(q, P)) >= 4), _sub(b[4], P))
        if _len(ta) < 1e-6 or _len(tb) < 1e-6: continue
        if _turn(ta, tb) > 30: continue
        d = _norm(_add(_norm(ta), _norm(tb)))
        la = min(max(_len(_sub(P, a[3])), 6.0), 0.45 * _seglen(a))
        lb = min(max(_len(_sub(b[2], P)), 6.0), 0.45 * _seglen(b))
        a[3] = _sub(P, _mul(d, la)); b[2] = _add(P, _mul(d, lb))
    return segs


def _tiny_curves_to_lines(segs):
    out = []
    for s in segs:
        if s[0] == 'C' and _seglen(s) < 4:
            out.append(['L', s[1], s[4]])
        else:
            out.append(s)
    return out


def _refit_chains(segs):
    n = len(segs)
    if n < 4: return segs
    short = [s[0] == 'L' and _seglen(s) <= CHAIN_SEG for s in segs]
    if all(short) or not any(short): return segs
    # rotate so we start on a non-chain segment
    k = short.index(False)
    segs = segs[k:] + segs[:k]; short = short[k:] + short[:k]
    out, i = [], 0
    while i < n:
        if not short[i]:
            out.append(segs[i]); i += 1; continue
        j = i
        while j < n and short[j] and (j == i or _turn(_sub(segs[j - 1][2], segs[j - 1][1]),
                                                       _sub(segs[j][2], segs[j][1])) < CHAIN_TURN):
            j += 1
        run = segs[i:j]
        if len(run) >= 3:
            pts = [run[0][1]] + [s[2] for s in run]
            prev, nxt = out[-1] if out else segs[-1], segs[j % n]
            t0 = _norm(_end_tan(prev)) if prev[0] == 'C' else _norm(_sub(pts[1], pts[0]))
            t1 = _norm(_start_tan(nxt)) if nxt[0] == 'C' else _norm(_sub(pts[-1], pts[-2]))
            # only smooth through if the neighbours are curves flowing in (else keep a corner)
            if prev[0] == 'L' and _turn(_end_tan(prev), _sub(pts[1], pts[0])) > CHAIN_TURN:
                t0 = _norm(_sub(pts[1], pts[0]))
            if nxt[0] == 'L' and _turn(_sub(pts[-1], pts[-2]), _start_tan(nxt)) > CHAIN_TURN:
                t1 = _norm(_sub(pts[-1], pts[-2]))
            out += _fit_rec(pts, t0, t1)
        else:
            out += run
        i = j if j > i else i + 1
    return out


# ---------------------------------------------------------------- micro steps
def _isect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9: return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


def _set_end(s, P):
    d = _sub(P, s[-1])
    s[-1] = P
    if s[0] == 'C': s[3] = _add(s[3], d)


def _set_start(s, P):
    d = _sub(P, s[1])
    s[1] = P
    if s[0] == 'C': s[2] = _add(s[2], d)


def _collapse_micro(segs):
    changed = True
    guard = 0
    while changed and len(segs) > 3 and guard < 50:
        changed = False; guard += 1
        n = len(segs)
        for i in range(n):
            s = segs[i]
            if s[0] != 'L' or _seglen(s) >= MICRO: continue
            p, q = segs[i - 1], segs[(i + 1) % n]
            if _seglen(s) < 2.5:                        # sub-pixel jog: always merge away
                P = _mul(_add(s[1], s[2]), 0.5)
                P = (float(round(P[0])), float(round(P[1])))
                _set_end(p, P); _set_start(q, P)
                del segs[i]; changed = True
                break
            d = _sub(s[2], s[1])
            if _turn(_end_tan(p), d) <= 20 or _turn(d, _start_tan(q)) <= 20:
                continue
            if q[0] == 'L' and _seglen(q) < MICRO and _seglen(s) + _seglen(q) < 2 * MICRO:
                q[1] = s[1]; del segs[i]; changed = True     # two tiny jogs in a row -> one
                break
            if _seglen(p) < MICRO or _seglen(q) < MICRO:
                continue
            P = _isect(s[1], _norm(_end_tan(p)), s[2], _norm(_start_tan(q)))
            mid = _mul(_add(s[1], s[2]), 0.5)
            if P is None or _len(_sub(P, mid)) > 3 * MICRO:
                P = mid
            P = (float(round(P[0])), float(round(P[1])))
            _set_end(p, P); _set_start(q, P)
            del segs[i]
            changed = True
            break
    return segs


def _merge_collinear(segs):
    i = 0
    while len(segs) > 3 and i < len(segs):
        n = len(segs)
        a, b = segs[i], segs[(i + 1) % n]
        if a[0] == 'L' and b[0] == 'L' and _turn(_sub(a[2], a[1]), _sub(b[2], b[1])) < 0.5:
            a[2] = b[2]; del segs[(i + 1) % n]
            if (i + 1) % n < i: i -= 1
            continue
        i += 1
    return segs


def clean(contours):
    out = []
    for c in contours:
        segs = _to_cyc(c)
        segs = _round(segs)
        if len(segs) < 3:
            continue
        segs = _refit_chains(segs)
        segs = _tiny_curves_to_lines(segs)
        segs = _collapse_micro(segs)
        segs = _merge_collinear(segs)
        segs = _smooth_joints(segs)
        out.append(_from_cyc(segs))
    return out
