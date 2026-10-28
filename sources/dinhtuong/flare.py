"""R4b (28/10 01:24, designer: 'các đặc điểm này không thấy xuất hiện xuyên suốt các chữ khác nhau — ví dụ chữ A
và V hoa'; chose 'loe tất cả'): EVERY free stroke end that is cut level on a guideline flares like the stems (R4),
diagonals included (A V W X Y, K R legs, k v w x y, 7 ...), and the vertical cut of every free bar end
(designer 01:27: 'cân nhắc thêm loe ở phần này của G' - G's bar; f t crossbars, the 1's flag ...).

A free end = a level cut on a guideline (baseline, x-height, cap height, ascender, descender) whose two sides are
straight and parallel (a stroke end, not a vertex like A's apex or V's foot). The flare is the stems' own: the cut
widens by f on each side, MEASURED PERPENDICULAR TO THE STROKE (f / sin of the side's angle along the line), and
blends into the side over the ONE flare length (flare_spec, R4c) with the same curve as fstem. Stems drawn by fstem are already flared (their corners are curves) and are left alone."""
import math
import booleng

TOL_PAR = 4.0      # degrees: the two sides of a stroke end are parallel within this
MAX_CUT = 270      # a longer level edge is a bar / foot, not a stroke end
MIN_DY = 0.5       # a side flatter than 30 deg is a bar, not a stroke


def _u(x, y):
    l = math.hypot(x, y)
    return (x / l, y / l) if l else (0.0, 0.0)


def _flat(contours, n=8):
    polys = []
    for c in contours:
        pts, cur = [], None
        for s in c:
            if s[0] in ('M', 'L'):
                cur = (s[1], s[2]); pts.append(cur)
            elif s[0] == 'C':
                p0 = cur
                for k in range(1, n + 1):
                    t = k / n; u = 1 - t
                    pts.append((u**3 * p0[0] + 3 * u * u * t * s[1] + 3 * u * t * t * s[3] + t**3 * s[5],
                                u**3 * p0[1] + 3 * u * u * t * s[2] + 3 * u * t * t * s[4] + t**3 * s[6]))
                cur = (s[5], s[6])
        polys.append(pts)
    return polys


def _inside(polys, x, y):
    w = False
    for P in polys:
        n = len(P)
        for i in range(n):
            (x1, y1), (x2, y2) = P[i], P[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                w = not w
    return w


def patches(ops, lines, f):
    """union patches that add the R4 flare to every free end of the glyph (ops): level cuts on one of `lines`
    and vertical cuts of horizontal-ish strokes (bar ends: G's bar, f t crossbars, the 1's flag ...)."""
    out = []
    cont = booleng.evaluate(ops)
    polys = _flat(cont)
    for c in cont:
        pts, kinds = [], []
        for s in c:
            if s[0] in ('M', 'L'):
                pts.append((s[1], s[2])); kinds.append('L')
            elif s[0] == 'C':
                pts.append((s[5], s[6])); kinds.append('C')
        n = len(pts)
        if n < 4:
            continue
        if pts[0] == pts[-1]:
            pts, kinds = pts[:-1], kinds[:-1]; n -= 1
        seg_kind = [kinds[(i + 1) % n] for i in range(n)]          # kind of the segment i -> i+1
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            if seg_kind[i] != 'L':
                continue
            level = abs(a[1] - b[1]) < 0.5
            vert = abs(a[0] - b[0]) < 0.5
            if level and not any(abs(a[1] - y) < 1.0 for y in lines):
                continue
            if not (level or vert):
                continue
            cut = math.hypot(b[0] - a[0], b[1] - a[1])
            if cut < 20 or cut > MAX_CUT:
                continue
            p_, q_ = pts[(i - 1) % n], pts[(i + 2) % n]
            if seg_kind[(i - 1) % n] != 'L' or seg_kind[(i + 1) % n] != 'L':
                continue
            da, db = _u(p_[0] - a[0], p_[1] - a[1]), _u(q_[0] - b[0], q_[1] - b[1])
            nrm = (0, 1) if level else (1, 0)                    # the cut's normal
            pa, pb = da[0] * nrm[0] + da[1] * nrm[1], db[0] * nrm[0] + db[1] * nrm[1]
            if abs(pa) < MIN_DY or abs(pb) < MIN_DY or pa * pb <= 0:
                continue
            ang = math.degrees(math.acos(max(-1, min(1, da[0] * db[0] + da[1] * db[1]))))
            if ang > TOL_PAR:
                continue                                        # sides diverge: a vertex (A apex, V foot), not an end
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            sg = 1 if pa > 0 else -1
            if not (_inside(polys, m[0] + nrm[0] * sg * 3, m[1] + nrm[1] * sg * 3) and
                    not _inside(polys, m[0] - nrm[0] * sg * 3, m[1] - nrm[1] * sg * 3)):
                continue                                        # not an outer end (a counter wall)
            la = math.hypot(p_[0] - a[0], p_[1] - a[1]); lb = math.hypot(q_[0] - b[0], q_[1] - b[1])
            import flare_spec as _FS                    # R4c: one flare everywhere (amount F, length L)
            f = _FS.F
            Lv = _FS.length(max(la * abs(pa), lb * abs(pb)))
            for C, d, other, side_len, pc in ((a, da, b, la, pa), (b, db, a, lb, pb)):
                o = _u(C[0] - other[0], C[1] - other[1])         # along the cut, away from the stroke
                fl = f / max(abs(pc), 0.3)                       # f measured perpendicular to the stroke
                Ls = min(Lv / abs(pc), 0.9 * side_len)
                Cp = (C[0] + o[0] * fl, C[1] + o[1] * fl)
                c1 = (C[0] + o[0] * 0.15 * fl + d[0] * 0.35 * Ls, C[1] + o[1] * 0.15 * fl + d[1] * 0.35 * Ls)
                c2 = (C[0] + d[0] * 0.7 * Ls, C[1] + d[1] * 0.7 * Ls)
                P = (C[0] + d[0] * Ls, C[1] + d[1] * Ls)
                inn = 4.0                                        # overlap the stroke (no coincident edges)
                out.append(('add', [('M', Cp[0], Cp[1]), ('C', c1[0], c1[1], c2[0], c2[1], P[0], P[1]),
                                    ('L', P[0] - o[0] * inn, P[1] - o[1] * inn), ('L', C[0] - o[0] * inn, C[1] - o[1] * inn),
                                    ('Z',)]))
    return out


def apply(g, lines, f):
    """add the R4b flare patches to glyph g in place; returns how many ends were flared."""
    ps = patches(g.ops, lines, f)
    if ps:
        g.ops = list(g.ops) + ps
        if hasattr(g, 'parts') and g.parts:
            g.parts[0] = (g.parts[0][0], list(g.parts[0][1]) + ps)
    return len(ps) // 2
