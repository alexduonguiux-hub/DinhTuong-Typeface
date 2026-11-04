"""VF5 (1.004, designer: 'làm luôn đi'): make the glyphs that VF3 (sources/dinhtuong/vf_compat.py) leaves incompatible
point-compatible for the variable font WITHOUT changing any master's outline.

VF3 matches corners; it gives up when a weight has one corner more (a short joint segment that only one weight has).
For those glyphs, contour by contour (the masters have the same contours in the same order):
  1. same direction and start: each contour starts on its on-curve point nearest the contour's lower-left box corner,
     and runs in the Regular contour's direction;
  2. every line becomes the equivalent cubic (handles at 1/3 and 2/3: the same straight line);
  3. nodes are matched by POSITION (normalised to the contour's box, sequence alignment); a node one master lacks is
     split into it exactly (de Casteljau) at the same local arc fraction between the neighbouring matched nodes,
     so corners stay matched to corners (a global arc-length match drifted and bent Q, {, § in between).
Every master then has the same number of cubic segments per contour. The outlines are unchanged (splits and
line -> cubic conversions are exact), so the variable font still draws exactly like the static fonts at the masters,
and in between it interpolates instead of stepping.

Usage: python3 scripts/vf_compat_generic.py Regular.ufo Medium.ufo Bold.ufo [glyph ...]
  (in place; the extra glyph names are VF3's VF4 report, re-matched even if their point types already agree)
"""
import math
import sys

import ufoLib2
from ufoLib2.objects import Contour, Point

GAP = 0.12            # alignment: cost of a node with no partner (distance in contour-box units)


def sig(g):
    return [tuple(p.type for p in c.points) for c in g.contours]


def segs_of(c):
    """closed contour -> list of cubic segments [p0, c1, c2, p3] (lines as exact cubics)"""
    pts = list(c.points)
    on = [i for i, p in enumerate(pts) if p.type]
    n = len(pts); out = []
    for k, i in enumerate(on):
        j = on[(k + 1) % len(on)]
        p0 = (pts[i].x, pts[i].y); p3 = (pts[j].x, pts[j].y)
        offs = [(pts[(i + m) % n].x, pts[(i + m) % n].y) for m in range(1, (j - i) % n)]
        if pts[j].type == 'line' or not offs:
            c1 = (p0[0] + (p3[0] - p0[0]) / 3, p0[1] + (p3[1] - p0[1]) / 3)
            c2 = (p0[0] + 2 * (p3[0] - p0[0]) / 3, p0[1] + 2 * (p3[1] - p0[1]) / 3)
            out.append([p0, c1, c2, p3])
        elif len(offs) == 2:
            out.append([p0, offs[0], offs[1], p3])
        else:
            raise ValueError('not a cubic contour')
    return out


def area(S):
    a = 0.0
    for s in S:
        for k in range(16):
            p, q = bz(s, k / 16), bz(s, (k + 1) / 16)
            a += p[0] * q[1] - q[0] * p[1]
    return a / 2


def bz(s, t):
    u = 1 - t
    return (u**3*s[0][0] + 3*u*u*t*s[1][0] + 3*u*t*t*s[2][0] + t**3*s[3][0],
            u**3*s[0][1] + 3*u*u*t*s[1][1] + 3*u*t*t*s[2][1] + t**3*s[3][1])


def seglen(s):
    pts = [bz(s, k / 24) for k in range(25)]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def reverse(S):
    return [[s[3], s[2], s[1], s[0]] for s in reversed(S)]


def restart(S):
    """start on the node nearest the lower-left corner of the contour's box"""
    xs = [s[0][0] for s in S]; ys = [s[0][1] for s in S]
    x0, y0 = min(xs), min(ys)
    k = min(range(len(S)), key=lambda i: math.hypot(S[i][0][0] - x0, S[i][0][1] - y0))
    return S[k:] + S[:k]


def split(s, t):
    a, b, c, d = s
    lerp = lambda p, q: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    ab, bc, cd = lerp(a, b), lerp(b, c), lerp(c, d)
    abc, bcd = lerp(ab, bc), lerp(bc, cd)
    m = lerp(abc, bcd)
    return [a, ab, abc, m], [m, bcd, cd, d]


def t_at_length(s, L):
    """parameter t where the arc length from the segment's start reaches L"""
    acc, prev = 0.0, bz(s, 0)
    for k in range(1, 201):
        p = bz(s, k / 200); d = math.dist(prev, p)
        if acc + d >= L:
            return (k - 1 + (L - acc) / d) / 200 if d else k / 200
        acc += d; prev = p
    return 1.0


def cum(S):
    L = [0.0]
    for s in S:
        L.append(L[-1] + seglen(s))
    return L


def norm_nodes(S):
    xs = [s[0][0] for s in S]; ys = [s[0][1] for s in S]
    x0, y0, w, h = min(xs), min(ys), (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    return [((s[0][0] - x0) / w, (s[0][1] - y0) / h) for s in S]


def align(A, B, gap=GAP):
    """Needleman-Wunsch over two node sequences (normalised positions), node 0 matched to node 0.
    Returns [(i or None, j or None)] in contour order."""
    n, m = len(A), len(B)
    INF = 1e18
    D = [[INF] * (m + 1) for _ in range(n + 1)]; T = [[None] * (m + 1) for _ in range(n + 1)]
    D[1][1] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if i == 1 and j == 1:
                continue
            best, bt = INF, None
            if i > 1 and j > 1 and D[i - 1][j - 1] < INF:
                c = D[i - 1][j - 1] + math.dist(A[i - 1], B[j - 1])
                if c < best: best, bt = c, 'd'
            if i > 1 and D[i - 1][j] < INF and D[i - 1][j] + gap < best:
                best, bt = D[i - 1][j] + gap, 'u'
            if j > 1 and D[i][j - 1] < INF and D[i][j - 1] + gap < best:
                best, bt = D[i][j - 1] + gap, 'l'
            D[i][j], T[i][j] = best, bt
    i, j, out = n, m, []
    while (i, j) != (1, 1):
        bt = T[i][j]
        if bt == 'd': out.append((i - 1, j - 1)); i -= 1; j -= 1
        elif bt == 'u': out.append((i - 1, None)); i -= 1
        else: out.append((None, j - 1)); j -= 1
    out.append((0, 0))
    return out[::-1]


def split_at(S, positions):
    """S with extra nodes at the given arc lengths (exact splits)"""
    L = cum(S); out = []
    for k, s in enumerate(S):
        cuts = sorted(p for p in positions if L[k] + 1e-6 < p < L[k + 1] - 1e-6)
        cur, done = s, L[k]
        for p in cuts:
            t = t_at_length(cur, p - done)
            left, cur = split(cur, t)
            out.append(left); done += seglen(left)
        out.append(cur)
    return out


def local_pos(LA, LB, al, idx_b, side_a):
    """arc length in A for an unmatched node of B: same local fraction between the neighbouring matched pairs"""
    k = idx_b
    prev = next(((a, b) for a, b in reversed(al[:k]) if a is not None and b is not None), (0, 0))
    nxt = next(((a, b) for a, b in al[k + 1:] if a is not None and b is not None), None)
    pa, pb = LA[prev[0]], LB[prev[1]]
    na, nb = (LA[nxt[0]], LB[nxt[1]]) if nxt else (LA[-1], LB[-1])
    _, j = al[k]
    f = (LB[j] - pb) / ((nb - pb) or 1.0)
    return pa + f * (na - pa)


def pair_up(SA, SB):
    """make SA and SB node-for-node compatible (splitting each where the other has a node it lacks)"""
    al = align(norm_nodes(SA), norm_nodes(SB))
    LA, LB = cum(SA), cum(SB)
    addA = [local_pos(LA, LB, al, k, 'a') for k, (a, b) in enumerate(al) if a is None]
    alr = [(b, a) for a, b in al]
    addB = [local_pos(LB, LA, alr, k, 'b') for k, (b, a) in enumerate(alr) if b is None]
    return split_at(SA, addA), split_at(SB, addB), addA


def compat_contours(SS):
    """SS: one contour per master (cubic lists, same start / direction) -> node-compatible lists"""
    R, M, B = SS
    R1, M1, _ = pair_up(R, M)
    R2, B2, addR = pair_up(R1, B)
    if addR:
        # the nodes added to R in the second pass go into M at the same segment-local arc fraction (R1 and M1 are
        # node-for-node)
        LR1, LM1 = cum(R1), cum(M1); pos = []
        for p in addR:
            k = max(i for i in range(len(R1)) if LR1[i] <= p)
            f = (p - LR1[k]) / ((LR1[k + 1] - LR1[k]) or 1.0)
            pos.append(LM1[k] + f * (LM1[k + 1] - LM1[k]))
        M1 = split_at(M1, pos)
    return [R2, M1, B2]


def to_contour(S):
    pts = []
    for s in S:
        pts += [Point(s[1][0], s[1][1]), Point(s[2][0], s[2][1]), Point(s[3][0], s[3][1], 'curve')]
    return Contour(points=[pts[-1]] + pts[:-1])


def fix_glyph(gs):
    if len({len(g.contours) for g in gs}) != 1:
        return False
    new = [[] for _ in gs]
    for ci in range(len(gs[0].contours)):
        SS = [segs_of(g.contours[ci]) for g in gs]
        ref = area(SS[0]) > 0
        SS = [S if (area(S) > 0) == ref else reverse(S) for S in SS]
        SS = [restart(S) for S in SS]
        SS = compat_contours(SS)
        if len({len(S) for S in SS}) != 1:
            return False
        for m, S in enumerate(SS):
            new[m].append(to_contour(S))
    for g, cs in zip(gs, new):
        g.clearContours()
        for c in cs:
            g.contours.append(c)
    return True


def main(paths, force=()):
    F = [ufoLib2.Font.open(p) for p in paths]
    # also the glyphs VF3 reported as left as is (VF4): their point types may line up while the points do not
    # (another start / rotation), which interpolates into a collapsed shape
    bad = [n for n in F[0].keys() if not (sig(F[0][n]) == sig(F[1][n]) == sig(F[2][n])) or n in force]
    fixed, left = [], []
    for n in bad:
        gs = [f[n] for f in F]
        if fix_glyph(gs) and sig(gs[0]) == sig(gs[1]) == sig(gs[2]):
            fixed.append(n)
        else:
            left.append(n)
    for f in F:
        f.save(overwrite=True)
    print('VF5 compatible:', len(fixed), ' '.join(fixed), '| still incompatible:', len(left), ' '.join(left))


if __name__ == '__main__':
    main(sys.argv[1:4], set(sys.argv[4:]))
