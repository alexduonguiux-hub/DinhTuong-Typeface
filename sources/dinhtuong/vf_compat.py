"""VF3 (vf-concept-v1, approved 30/10): make the three UFO masters point-compatible for the variable font
without changing any outline.

VF3a  drop redundant nodes: curves whose handles lie on the chord (<= 0.6 u) become lines, zero-length segments go,
      consecutive collinear lines merge.
VF3b  same start point, direction and contour order in every master (start on a matched corner).
VF3c  corner-anchored split: corners (tangent break > 12 deg) are matched in order; every smooth run between two corners
      gets the same number of segments in every master by splitting segments exactly (de Casteljau) at the arc-length
      fractions of the master with the most nodes. Splitting is exact: the outline does not move.

Only glyphs that are not compatible as written are touched. Glyphs whose corner counts differ between weights (VF4)
are left as they are and reported; they need a construction rule, not a mechanical fix.

Usage: python3 vf_compat.py Regular.ufo Medium.ufo Bold.ufo [--dry]
"""
import sys, math
import ufoLib2
from ufoLib2.objects import Contour, Point

TOL = 0.6
CORNER = 12.0


# ---------------------------------------------------------------- segments
def segments(c):
    """[(p0, [c1, c2] or [], p1)] cubic/line segments, closed contour."""
    pts = c.points
    n = len(pts)
    on = [i for i, p in enumerate(pts) if p.type]
    out = []
    for k, i in enumerate(on):
        j = on[(k + 1) % len(on)]
        ctl = []
        m = (i + 1) % n
        while m != j:
            ctl.append((pts[m].x, pts[m].y))
            m = (m + 1) % n
        out.append([(pts[i].x, pts[i].y), ctl, (pts[j].x, pts[j].y)])
    return out


def to_contour(S):
    c = Contour()
    for s in S:
        for q in s[1]:
            c.points.append(Point(q[0], q[1], None))
        c.points.append(Point(s[2][0], s[2][1], 'curve' if s[1] else 'line'))
    return c


def dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    return abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / L


def simplify(S):
    """VF3a."""
    S = [[s[0], list(s[1]), s[2]] for s in S]
    for s in S:
        if s[1] and all(dist(q, s[0], s[2]) < TOL for q in s[1]):
            # handles on the chord AND inside it (no overshoot) -> a line
            ax, ay = s[0]; bx, by = s[2]; L2 = (bx - ax) ** 2 + (by - ay) ** 2
            inside = L2 > 0 and all(-0.01 <= ((q[0] - ax) * (bx - ax) + (q[1] - ay) * (by - ay)) / L2 <= 1.01 for q in s[1])
            if inside or L2 == 0:
                s[1] = []
    S = [s for s in S if s[1] or math.hypot(s[2][0] - s[0][0], s[2][1] - s[0][1]) > 0.5]
    changed = True
    while changed and len(S) > 2:
        changed = False
        for k in range(len(S)):
            a = S[k]; b = S[(k + 1) % len(S)]
            if not a[1] and not b[1] and dist(a[2], a[0], b[2]) < TOL:
                a[2] = b[2]
                S.pop((k + 1) % len(S))
                changed = True
                break
    # keep closure consistent
    for k in range(len(S)):
        S[k][0] = S[k - 1][2]
    return S


def turn(S, k):
    prev = S[k - 1]; s = S[k]
    a = prev[1][-1] if prev[1] else prev[0]
    b = s[1][0] if s[1] else s[2]
    p = s[0]
    t1 = math.atan2(p[1] - a[1], p[0] - a[0]); t2 = math.atan2(b[1] - p[1], b[0] - p[0])
    return abs((math.degrees(t2 - t1) + 180) % 360 - 180)


def corners(S):
    return [k for k in range(len(S)) if turn(S, k) > CORNER]


def sig(S):
    return tuple(len(s[1]) for s in S)


# ---------------------------------------------------------------- cubic helpers
def as_cubic(s):
    if s[1]:
        return s
    (ax, ay), (bx, by) = s[0], s[2]
    return [s[0], [(ax + (bx - ax) / 3, ay + (by - ay) / 3), (ax + 2 * (bx - ax) / 3, ay + 2 * (by - ay) / 3)], s[2]]


def bpt(s, t):
    q = [s[0]] + s[1] + [s[2]]
    while len(q) > 1:
        q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
    return q[0]


def seglen(s, n=32):
    L = 0; p = s[0]
    for i in range(1, n + 1):
        q = bpt(s, i / n); L += math.hypot(q[0] - p[0], q[1] - p[1]); p = q
    return L


def split(s, t):
    if not s[1]:
        m = ((1 - t) * s[0][0] + t * s[2][0], (1 - t) * s[0][1] + t * s[2][1])
        return [s[0], [], m], [m, [], s[2]]
    p0, (p1, p2), p3 = s[0], s[1], s[2]
    L = lambda a, b: ((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])
    a, b, c = L(p0, p1), L(p1, p2), L(p2, p3)
    d, e = L(a, b), L(b, c)
    m = L(d, e)
    return [p0, [a, d], m], [m, [e, c], p3]


def t_at_len(s, frac, n=64):
    tot = seglen(s, n); goal = frac * tot; L = 0; p = s[0]
    for i in range(1, n + 1):
        q = bpt(s, i / n); dl = math.hypot(q[0] - p[0], q[1] - p[1])
        if L + dl >= goal:
            return (i - 1 + (goal - L) / dl) / n if dl else i / n
        L += dl; p = q
    return 1.0


def run_fracs(run):
    lens = [seglen(s) for s in run]; tot = sum(lens) or 1; acc = 0; out = []
    for l in lens[:-1]:
        acc += l; out.append(acc / tot)
    return out, lens, tot


def match(fa, fb):
    """Monotone assignment of the (fewer) fractions fb to fractions fa; returns indices into fa."""
    n, m = len(fa), len(fb)
    INF = 1e18
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(1, n + 1):
        D[i][0] = 0
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j], D[i - 1][j - 1] + abs(fa[i - 1] - fb[j - 1]))
    out = []; i, j = n, m
    while j > 0:
        if D[i][j] == D[i - 1][j - 1] + abs(fa[i - 1] - fb[j - 1]) and (D[i - 1][j] != D[i][j] or i - 1 < j - 1 + 1):
            out.append(i - 1); i -= 1; j -= 1
        else:
            i -= 1
    return out[::-1]


def refine(run, target):
    """Split segments of run so that it gets a node at each fraction in target that is not already matched."""
    fr, lens, tot = run_fracs(run)
    have = match(target, fr) if fr else []
    need = [f for k, f in enumerate(target) if k not in have]
    bounds = [0] + fr + [1]
    out = []
    for k, s in enumerate(run):
        lo, hi = bounds[k], bounds[k + 1]
        cuts = [(f - lo) / (hi - lo) for f in need if lo < f < hi]
        cur = s; done = 0.0
        for c in cuts:
            local = (c - done) / (1 - done)
            t = t_at_len(cur, local)
            a, cur = split(cur, t)
            out.append(a); done = c
        out.append(cur)
    return out


# ---------------------------------------------------------------- per glyph
def rotate(S, k):
    return S[k:] + S[:k]


def centre(S):
    xs = [s[0][0] for s in S]; ys = [s[0][1] for s in S]
    return ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2), (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def rel(p, S):
    (cx, cy), (w, h) = centre(S)
    return ((p[0] - cx) / w, (p[1] - cy) / h)


def align(ref, S, cref, cS):
    """Rotate S so its corners line up with ref's corners (same count). Returns rotated S, its corners."""
    best = None
    for r in range(len(cS)):
        d = sum(math.dist(rel(ref[cref[i]][0], ref), rel(S[cS[(i + r) % len(cS)]][0], S)) for i in range(len(cref)))
        if best is None or d < best[0]:
            best = (d, r)
    r = best[1]
    k0 = cS[r % len(cS)]
    S2 = rotate(S, k0)
    return S2, corners(S2)


def runs(S, cs):
    out = []
    for i, k in enumerate(cs):
        e = cs[(i + 1) % len(cs)] if i + 1 < len(cs) else len(S)
        out.append(S[k:e])
    return out


def signed_area(S):
    a = 0
    for s in S:
        a += s[0][0] * s[2][1] - s[2][0] * s[0][1]
    return a / 2


def cdist(S0, S):
    """Contour correspondence cost: centre + size, and never across winding (outer vs counter)."""
    (c0, d0), (c1, d1) = centre(S0), centre(S)
    pen = 0 if (signed_area(S0) > 0) == (signed_area(S) > 0) else 1e6
    return math.dist(c0, c1) + math.dist(d0, d1) + pen


def misaligned(A, lim=0.25):
    for ci in range(len(A[0])):
        S0 = A[0][ci]
        for m in (1, 2):
            S = A[m][ci]
            if math.dist(centre(S0)[0], centre(S)[0]) > 0.25 * max(centre(S0)[1]):
                return True
            if math.dist(rel(S0[0][0], S0), rel(S[0][0], S)) > lim:
                return True
    return False


def fix_glyph(gl):
    """gl: [Glyph R, M, B]. Returns list of new contour-segment lists per master, or None (VF4)."""
    A = [[simplify(segments(c)) for c in g.contours] for g in gl]
    if len({len(x) for x in A}) != 1:
        return None, 'contour count'
    # VF3a enough? (same node types AND the same start point / contour order)
    if all([sig(s) for s in A[0]] == [sig(s) for s in a] for a in A[1:]) and not misaligned(A):
        return A, 'a'
    # contour order: match to master 0 by centre
    ref = A[0]
    for m in (1, 2):
        used = set(); order = []
        for s in ref:
            j = min((j for j in range(len(A[m])) if j not in used), key=lambda j: cdist(s, A[m][j]))
            used.add(j); order.append(A[m][j])
        A[m] = order
    out = [[], [], []]
    for ci in range(len(ref)):
        Ss = [A[m][ci] for m in range(3)]
        cs = [corners(S) for S in Ss]
        if len({len(c) for c in cs}) != 1:
            return None, 'corners %s' % [len(c) for c in cs]
        if not cs[0]:
            # smooth closed contour (ring): start at the top-most node; treat as one run
            Ss = [rotate(S, max(range(len(S)), key=lambda k: (S[k][0][1], -S[k][0][0]))) for S in Ss]
            rs = [[S] for S in Ss]
        else:
            Ss[0] = rotate(Ss[0], cs[0][0]); c0 = corners(Ss[0])
            for m in (1, 2):
                Ss[m], _ = align(Ss[0], Ss[m], c0, cs[m])
            cs = [corners(S) for S in Ss]
            rs = [runs(S, c) for S, c in zip(Ss, cs)]
        new = [[], [], []]
        for ri in range(len(rs[0])):
            R = [rs[m][ri] for m in range(3)]
            fr = [run_fracs(r)[0] for r in R]
            top = max(range(3), key=lambda m: len(fr[m]))
            for m in range(3):
                R[m] = refine(R[m], fr[top]) if len(fr[m]) < len(fr[top]) else R[m]
            if len({len(r) for r in R}) != 1:
                return None, 'run split'
            for k in range(len(R[0])):
                if any(R[m][k][1] for m in range(3)):
                    for m in range(3):
                        R[m][k] = as_cubic(R[m][k])
            for m in range(3):
                new[m] += R[m]
        for m in range(3):
            out[m].append(new[m])
    if all([sig(s) for s in out[0]] == [sig(s) for s in o] for o in out[1:]):
        return out, 'c'
    return None, 'not compatible after c'


def compatible(gl):
    def s(g):
        return [tuple(p.type for p in c.points) for c in g.contours]
    return s(gl[0]) == s(gl[1]) == s(gl[2])


def main(paths, dry=False):
    F = [ufoLib2.Font.open(p) for p in paths]
    stats = {}; vf4 = []
    for name in F[0].keys():
        gl = [f[name] for f in F]
        if compatible(gl) and not misaligned([[segments(c) for c in g.contours] for g in gl]):
            stats['as is'] = stats.get('as is', 0) + 1
            continue
        res, how = fix_glyph(gl)
        if res is None:
            vf4.append((name, how))
            continue
        stats[how] = stats.get(how, 0) + 1
        for g, cl in zip(gl, res):
            g.clearContours()
            for S in cl:
                g.contours.append(to_contour(S))
    print('VF3:', stats, '| VF4 (left as is):', len(vf4))
    print(' '.join(n for n, _ in vf4))
    if not dry:
        for f in F:
            f.save()
    return vf4


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args, '--dry' in sys.argv)
