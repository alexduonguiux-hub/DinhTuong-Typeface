"""VF4-S (vf-concept-v1, approved 30/10, option B): the S / s spine joins each bowl ring TANGENTIALLY (G1, turn
<= 3 deg) in every weight.

Cause of the old kinks: R11b draws each spine edge as one cubic that meets its ring G2 at a join point (the counter's
or the outer ring's extreme). The boolean engine (flatten -> Clipper -> curve re-fit, integer grid) cannot place an
intersection between two curves that touch tangentially: it left short lines and re-fitted handles there, turning
4-15 deg (S Medium: 15 + 18 deg within 3 u). The amount changed with the weight, so S s could not interpolate.

Fix (construction, not retouching): after the union, every spine edge is put back as the EXACT R11b cubic from join
to join, and on the ring side of each join the outline is the EXACT ring ellipse (cubic arc, k = 4/3 tan(dt/4)) up to
the first node >= RUN units away (never past a real corner); that node is moved onto the ellipse and the next
segment's handle is turned onto the ellipse tangent (length kept). Nothing else in the glyph moves.

Spine data come from the generator (spine_data.py -> spine_data.json: R11b inputs per weight, for S and s).
Every glyph that carries the S or s spine (S s and their accented forms) is found by its four join points.

Usage: python3 s_spine_fix.py spine_data.json Regular.ufo Medium.ufo Bold.ufo [--dry]
"""
import sys, json, math
import ufoLib2
from ufoLib2.objects import Contour, Point

RUN = 20.0          # ring-side run replaced by the exact ellipse (units)
CORNER = 25.0       # never extend the ring run past a turn larger than this
SNAP = 3.0          # a join must lie within this distance of an existing node


# ------------------------------------------------------------------ geometry from R11b (concept_v1.s_spine_geom)
def rings(W, T, ov, sx, sy, sm, ti):
    ym = (T - sm) / 2 + 8
    U = (W / 2, (ym + T + ov) / 2, (W - ti) / 2, (T + ov - ym) / 2)
    Uc = (W / 2, ((T + ov - sy) + (ym + sm)) / 2, (W - ti) / 2 - sx, ((T + ov - sy) - (ym + sm)) / 2)
    Lo = (W / 2, (-ov + ym + sm) / 2, W / 2, (ym + sm + ov) / 2)
    Lc = (W / 2, (ym + (-ov + sy)) / 2, W / 2 - sx, (ym - (-ov + sy)) / 2)
    return U, Uc, Lo, Lc


def ell_t(E, p):
    cx, cy, rx, ry = E
    return math.atan2((p[1] - cy) / ry, (p[0] - cx) / rx)


def ell_p(E, t):
    cx, cy, rx, ry = E
    return (cx + rx * math.cos(t), cy + ry * math.sin(t))


def ell_d(E, t):
    cx, cy, rx, ry = E
    return (-rx * math.sin(t), ry * math.cos(t))


def ell_arc(E, t0, t1):
    """cubic segments [p0, [c1, c2], p1] for the ellipse arc t0 -> t1 (signed, |t1 - t0| < pi)."""
    n = max(1, math.ceil(abs(t1 - t0) / (math.pi / 2) - 1e-9))
    out = []
    for i in range(n):
        a = t0 + (t1 - t0) * i / n
        b = t0 + (t1 - t0) * (i + 1) / n
        k = 4 / 3 * math.tan((b - a) / 4)
        p0, p3 = ell_p(E, a), ell_p(E, b)
        da, db = ell_d(E, a), ell_d(E, b)
        out.append([p0, [(p0[0] + k * da[0], p0[1] + k * da[1]), (p3[0] - k * db[0], p3[1] - k * db[1])], p3])
    return out


# ------------------------------------------------------------------ contour <-> segments
def segments(c):
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
    r = lambda v: round(v)
    for s in S:
        for q in s[1]:
            c.points.append(Point(r(q[0]), r(q[1]), None))
        c.points.append(Point(r(s[2][0]), r(s[2][1]), 'curve' if s[1] else 'line'))
    return c


def seglen(s, n=24):
    q = [s[0]] + s[1] + [s[2]]
    def bp(t):
        r = q
        while len(r) > 1:
            r = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(r, r[1:])]
        return r[0]
    L, p = 0, s[0]
    for i in range(1, n + 1):
        b = bp(i / n); L += math.dist(p, b); p = b
    return L


def turn_at(S, k):
    """turn (deg) at the node where S[k-1] ends and S[k] starts."""
    prev, s = S[k - 1], S[k]
    a = prev[1][-1] if prev[1] else prev[0]
    b = s[1][0] if s[1] else s[2]
    p = s[0]
    if math.dist(a, p) < 1e-6 or math.dist(b, p) < 1e-6:
        return 0.0
    t1 = math.atan2(p[1] - a[1], p[0] - a[0]); t2 = math.atan2(b[1] - p[1], b[0] - p[0])
    return abs((math.degrees(t2 - t1) + 180) % 360 - 180)


def rev(s):
    return [s[2], s[1][::-1], s[0]]


# ------------------------------------------------------------------ the fix
def nearest_node(S, p):
    k = min(range(len(S)), key=lambda i: math.dist(S[i][0], p))
    return k, math.dist(S[k][0], p)


def put_edge(S, cub, Ea, Eb):
    """Replace the run of S between the nodes nearest cub's ends by the exact cubic; returns new S or None."""
    A, B = cub[0], cub[3]
    ia, da = nearest_node(S, A)
    ib, db = nearest_node(S, B)
    if da > SNAP or db > SNAP or ia == ib:
        return None
    S = S[ia:] + S[:ia]                       # node A first
    ib = (ib - ia) % len(S)
    fwd = sum(seglen(s) for s in S[:ib]); bwd = sum(seglen(s) for s in S[ib:])
    L = seglen([A, [cub[1], cub[2]], B])
    seg = [A, [cub[1], cub[2]], B]
    if abs(fwd - L) <= abs(bwd - L):
        S = [seg] + S[ib:]                    # A -> B forward, spine first
        S[-1][2] = A; S[1][0] = B
        ends = [('start', Ea), ('end', Eb)]
    else:
        S = [rev(seg)] + S[:ib]               # B -> A, spine first
        S[-1][2] = B; S[1][0] = A
        ends = [('start', Eb), ('end', Ea)]
    for side, E in ends:
        S = ring_run(S, 0, side, E)
    return S


def ring_run(S, k, side, E):
    """On the ring side of the spine segment S[k] ('start': before it, 'end': after it), lay the exact ellipse."""
    n = len(S)
    # rotate so the spine segment is S[0]
    S = S[k:] + S[:k]
    if side == 'end':
        J = S[0][2]
        acc, j = 0.0, 1
        while j < n - 1:
            acc += seglen(S[j])
            if acc >= RUN or turn_at(S, (j + 1) % n) > CORNER:
                break
            j += 1
        N = S[j][2]
        tJ, tN = ell_t(E, J), ell_t(E, N)
        d = (tN - tJ + math.pi) % (2 * math.pi) - math.pi
        arc = ell_arc(E, tJ, tJ + d)
        arc[0][0] = J
        Np = arc[-1][2]
        rest = S[j + 1:]
        if rest:
            rest[0][0] = Np
            if rest[0][1]:
                t = ell_d(E, tJ + d); ln = math.hypot(*t); sg = 1 if d > 0 else -1
                h = rest[0][1][0]; L = math.dist(h, N)
                rest[0][1][0] = (Np[0] + sg * t[0] / ln * L, Np[1] + sg * t[1] / ln * L)
        S = [S[0]] + arc + rest
    else:
        J = S[0][0]
        acc, j = 0.0, n - 1
        while j > 1:
            acc += seglen(S[j])
            if acc >= RUN or turn_at(S, j) > CORNER:
                break
            j -= 1
        N = S[j][0]
        tN, tJ = ell_t(E, N), ell_t(E, J)
        d = (tJ - tN + math.pi) % (2 * math.pi) - math.pi
        arc = ell_arc(E, tN, tN + d)
        arc[-1][2] = J
        Np = arc[0][0]
        before = S[1:j]
        if before:
            before[-1][2] = Np
            if before[-1][1]:
                t = ell_d(E, tN); ln = math.hypot(*t); sg = 1 if d > 0 else -1
                h = before[-1][1][-1]; L = math.dist(h, N)
                before[-1][1][-1] = (Np[0] - sg * t[0] / ln * L, Np[1] - sg * t[1] / ln * L)
        S = [S[0]] + before + arc
        # rotate back so the spine segment stays a segment (order is free for a closed contour)
    return S


def spine_parts(rec, dx):
    W, T, ov, sx, sy, sm, ti = rec['args']
    U, Uc, Lo, Lc = [(e[0] + dx, e[1], e[2], e[3]) for e in rings(W, T, ov, sx, sy, sm, ti)]
    sh = lambda c: [(x + dx, y) for x, y in c]
    top, bot = sh(rec['top']), sh(rec['bot'])
    return [(top, Uc, Lo), (bot, U, Lc)]           # top: P0 on Uc -> P3 on Lo; bottom: Q0 on U -> Q3 on Lc


def fix_glyph(g, rec):
    nodes = [(p.x, p.y) for c in g.contours for p in c.points if p.type]
    if not nodes:
        return False
    J0 = rec['top'][0]
    cands = sorted({round(n[0] - J0[0]) for n in nodes if abs(n[1] - J0[1]) < SNAP})
    for dx in cands:
        parts = spine_parts(rec, dx)
        joins = [p for cub, _, _ in parts for p in (cub[0], cub[3])]
        if not all(min(math.dist(j, n) for n in nodes) <= SNAP for j in joins):
            continue
        new = []
        done = 0
        for c in g.contours:
            S = segments(c)
            for cub, Ea, Eb in parts:
                if min(math.dist(cub[0], s[0]) for s in S) <= SNAP and min(math.dist(cub[3], s[0]) for s in S) <= SNAP:
                    S2 = put_edge(S, cub, Ea, Eb)
                    if S2:
                        S = S2; done += 1
            new.append(S)
        if done == 2:
            g.clearContours()
            for S in new:
                g.contours.append(to_contour(S))
            return True
    return False


def main(data, paths, dry=False):
    D = json.load(open(data))
    for p in paths:
        f = ufoLib2.Font.open(p)
        style = f.info.styleName
        recs = D[style]
        fixed = []
        for name in f.keys():
            for key in ('S', 's'):
                if fix_glyph(f[name], recs[key]):
                    fixed.append(name); break
        print(style, 'VF4-S fixed:', len(fixed), ' '.join(fixed))
        if not dry:
            f.save()


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1:], '--dry' in sys.argv)
