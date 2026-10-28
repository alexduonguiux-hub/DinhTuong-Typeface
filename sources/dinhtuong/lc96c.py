"""DINHTUONG60s — lowercase PROPOSAL C (v0.96 draft, 27/10): "mượt" — the smooth lowercase.

Why A and B read stiff: every round part was a straight line joined to a circle arc (stadium,
bent box). Where a line meets an arc the curvature jumps from 0 to 1/r — the eye sees a corner
even though the tangent is continuous. And every arch left its stem at a square corner.

C keeps the caps' skeleton, strokes and cuts, and changes only the CURVE and the JOINT:
  C1 Grid      x-height 530 · ascender 740 · descender −200 · overshoot 8 (round tops/bottoms).
  C2 Strokes   v = 0.93 V, h = 0.93 H (as A, B).
  C3 Curve     ruler + compass only. Every round part is a FOUR-CENTRE OVAL (the classical
               draughtsman's oval): per quarter, a small compass (r = 0.75 x the shorter half-axis)
               and a large one, tangent where they meet. The caps' stadium O is the same construction
               with r = the full half-width (large radius = infinity, i.e. a straight side); the
               lowercase relaxes it to 0.75, so the curvature steps in two small jumps instead of one
               big one — smooth to the eye, still drawn with the compass. Counter = the four-centre
               oval of the box inset by the strokes (same rule).
  C4 Joint     an arch / bowl springs OUT of its stem: the outer curve starts 0.45 v inside the stem,
               the counter starts on the stem's edge. The stroke thins into the joint (no notch,
               no square corner) — the junction reads as a crisp crotch (house rule R9: no fillet).
  C5 Cuts      open ends (a c e s f g j t r) are cut VERTICALLY (caps R5 cut, no level cut).
  C6 Hooks     f g j t: the lower (upper) half of a squircle hanging off the stem, cut vertically.
  C7 Stems     free stem ends flare like the caps (R4).
  C8 Diagonals k v w x y z: flat level cuts, 0.9 v (caps R7) — as option A.
  C9 Dots/marks round period dot; marks = the caps steel-strip system (lcfont).
Usage: A2_WEIGHT=bold python3 lc96c.py -> out/lc96/lc96c_<w>.json
"""
import os, json, math
import lc96 as A
import concept_v1 as CV
from concept_v1 import rect, fstem, ell

XH, ASC, DESC, OV = 530, 740, -200, 8
K = 0.62                       # superellipse handle
TERM = 0.55                    # C5: an open end is cut on the shoulder, 0.55 of the COUNTER's half-width out from the centre
HOOK_IN = 140                  # C6: a hook's counter is this wide (regular units)
JX = 0.45                      # C4: the outer curve starts this many stems inside the stem


RHO = 0.75                     # C3: small compass = 0.75 of the shorter half-axis


def _arc(cx, cy, r, t0, t1):
    """compass arc from angle t0 to t1 (radians) as cubic segments [(c1, c2, p)]."""
    n = max(1, math.ceil(abs(t1 - t0) / (math.pi / 2) - 1e-9))
    d = (t1 - t0) / n
    k = 4 / 3 * math.tan(d / 4)
    out = []
    for i in range(n):
        a, b = t0 + i * d, t0 + (i + 1) * d
        p0 = (cx + r * math.cos(a), cy + r * math.sin(a)); p1 = (cx + r * math.cos(b), cy + r * math.sin(b))
        c1 = (p0[0] - k * r * math.sin(a), p0[1] + k * r * math.cos(a))
        c2 = (p1[0] + k * r * math.sin(b), p1[1] - k * r * math.cos(b))
        out.append((c1, c2, p1))
    return out


def quarter(qa, qb):
    """C3 four-centre quarter (ruler + compass): from the top point (0, qb) to the side point (qa, 0)
    in the frame of the quarter's centre. Two compass arcs, tangent where they meet:
    the small one (radius r = RHO x the shorter half-axis) at the end of the LONGER axis, the large
    one (R from the tangency condition) at the other end. Returns (segments, centres)."""
    if abs(qa - qb) < 0.5:
        return _arc(0, 0, qa, math.pi / 2, 0), [(0, 0, qa)]
    if qb > qa:                                   # tall: small arc on top, centre on the vertical axis
        r = RHO * qa
        R = (qa ** 2 + (qb - r) ** 2 - r ** 2) / (2 * (qa - r))
        cs, cb = (0, qb - r), (qa - R, 0)
        phi = math.atan2(cs[1] - cb[1], cs[0] - cb[0])
        seg = _arc(cs[0], cs[1], r, math.pi / 2, phi) + _arc(cb[0], cb[1], R, phi, 0)
        return seg, [(cs[0], cs[1], r), (cb[0], cb[1], R)]
    r = RHO * qb                                  # wide: small arc at the side, centre on the horizontal axis
    R = (qb ** 2 + (qa - r) ** 2 - r ** 2) / (2 * (qb - r))
    cs, cb = (qa - r, 0), (0, qb - R)
    phi = math.atan2(cs[1] - cb[1], cs[0] - cb[0])
    seg = _arc(cb[0], cb[1], R, math.pi / 2, phi) + _arc(cs[0], cs[1], r, phi, 0)
    return seg, [(cb[0], cb[1], R), (cs[0], cs[1], r)]


def _place(seg, start, ox, oy, sx, sy, reverse):
    """map a quarter (start point + segments) into a corner; reverse the drawing order if asked."""
    m = lambda p: (ox + sx * p[0], oy + sy * p[1])
    pts = [m(start)] + [m(q) for sg in seg for q in sg]
    segs = [(pts[1 + 3 * i], pts[2 + 3 * i], pts[3 + 3 * i]) for i in range(len(seg))]
    if not reverse:
        return [('C',) + c1 + c2 + p for c1, c2, p in segs]
    ends = [pts[0]] + [sg[2] for sg in segs]
    out = []
    for i in range(len(segs) - 1, -1, -1):
        c1, c2, p = segs[i]
        out.append(('C',) + c2 + c1 + ends[i])
    return out


GUIDES = []                                       # compass centres of the last glyph built (for the guide page)


def sq(x0, y0, x1, y1, rx, ry, corners=('tl', 'tr', 'br', 'bl'), k=None):
    """box whose listed corners are C3 four-centre quarters with extents (rx, ry) (clamped to half the box)."""
    rx = min(rx, (x1 - x0) / 2); ry = min(ry, (y1 - y0) / 2)
    seg, cen = quarter(rx, ry) if (rx > 0 and ry > 0) else ([], [])
    has = {c: c in corners and seg for c in ('tl', 'tr', 'br', 'bl')}
    R = {c: ((rx, ry) if has[c] else (0, 0)) for c in has}
    p = [('M', x0 + R['tl'][0], y1), ('L', x1 - R['tr'][0], y1)]
    if has['tr']:
        ox, oy = x1 - rx, y1 - ry
        p += _place(seg, (0, ry), ox, oy, 1, 1, False)
        GUIDES.extend((ox + c[0], oy + c[1], c[2]) for c in cen)
    p.append(('L', x1, y0 + R['br'][1]))
    if has['br']:
        ox, oy = x1 - rx, y0 + ry
        p += _place(seg, (0, ry), ox, oy, 1, -1, True)
        GUIDES.extend((ox + c[0], oy - c[1], c[2]) for c in cen)
    p.append(('L', x0 + R['bl'][0], y0))
    if has['bl']:
        ox, oy = x0 + rx, y0 + ry
        p += _place(seg, (0, ry), ox, oy, -1, -1, False)
        GUIDES.extend((ox - c[0], oy - c[1], c[2]) for c in cen)
    p.append(('L', x0, y1 - R['tl'][1]))
    if has['tl']:
        ox, oy = x0 + rx, y1 - ry
        p += _place(seg, (0, ry), ox, oy, -1, 1, True)
        GUIDES.extend((ox - c[0], oy + c[1], c[2]) for c in cen)
    p.append(('Z',))
    return p


def xform(ops, f):
    """apply a point map f(x, y) -> (x, y) to nested boolean ops (mirror maps flip the winding;
    booleng uses non-zero/even-odd per contour so that is harmless)."""
    out = []
    for op, c in ops:
        if op == 'group':
            out.append((op, xform(c, f))); continue
        q = []
        for s in c:
            if s[0] == 'Z':
                q.append(s); continue
            pts = [f(s[i], s[i + 1]) for i in range(1, len(s), 2)]
            q.append((s[0],) + tuple(v for p in pts for v in p))
        out.append((op, q))
    return out


class LC3:
    def __init__(self, w):
        b = CV.Build(w)
        self.fl = b.fl
        self.v, self.h = round(0.93 * b.V), round(0.93 * b.H)
        self.v_reg = round(0.93 * CV.W8['regular']['V'])
        self.k = self.v_reg / self.v
        self.A = A.LC(w)

    def wd(self, W_reg):
        """widths grow by 0.6 of the strokes' growth over the Regular (counters shrink by the rest)."""
        return round(W_reg + 1.2 * (self.v - self.v_reg))

    def G(self, name, body, lsb, rsb, ops, guides=()):
        return dict(name=name, body=body, lsb=lsb, rsb=rsb, ops=ops, guides=list(guides))

    def stem(self, x0, y0, y1, top=True, bot=True):
        return ('add', fstem(x0, y0, x0 + self.v, y1, self.fl, top=top, bot=bot))

    def dot(self, cx):
        d = 1.18 * self.v
        return ('add', ell(cx, XH + 70 + d / 2, d / 2, d / 2))

    # C3: a closed squircle ring
    def ring(self, x0, y0, x1, y1, sv=None, sh=None):
        sv = self.v if sv is None else sv
        sh = self.h if sh is None else sh
        W, H = x1 - x0, y1 - y0
        return [('add', sq(x0, y0, x1, y1, W / 2, H / 2)),
                ('sub', sq(x0 + sv, y0 + sh, x1 - sv, y1 - sh, W / 2 - sv, H / 2 - sh))]

    # C4: an arch springing out of a stem whose RIGHT edge is xs (n h m r; u by rotation)
    def arch(self, xs, x1, top=XH + OV, ry=None):
        """C4: the arch is a compass semicircle springing out of the stem: outer circle on the box from
        JX v inside the stem to the leg's outer edge, counter circle on the box between the stem's edge
        and the leg's inner edge, h below the top. Two compass circles, nothing else."""
        v, h = self.v, self.h
        xo = xs - (1 - JX) * v
        ro, ri = (x1 - xo) / 2, (x1 - v - xs) / 2
        outer = sq(xo, -600, x1, top, ro, ro, ('tl', 'tr'))
        inner = sq(xs, -700, x1 - v, top - h, ri, ri, ('tl', 'tr'))
        return [('group', [('add', outer), ('sub', inner), ('sub', rect(-2000, -2000, 4000, 0))])]

    def leg(self, x1, ytop):
        return self.stem(x1 - self.v, 0, ytop, top=False)

    def g_n(self):
        W, v = self.wd(450), self.v
        return self.G('n', W, 50, 44, [self.stem(0, 0, XH)] + self.arch(v, W) + [self.leg(W, XH * 0.45)])

    def g_h(self):
        W, v = self.wd(450), self.v
        return self.G('h', W, 50, 44, [self.stem(0, 0, ASC)] + self.arch(v, W) + [self.leg(W, XH * 0.45)])

    def g_m(self):
        v = self.v
        W1 = self.wd(370)
        W = 2 * W1 - v
        ops = [self.stem(0, 0, XH)] + self.arch(v, W1) + [self.leg(W1, XH * 0.45)] + \
              self.arch(W1, W) + [self.leg(W, XH * 0.45)]
        return self.G('m', W, 50, 44, ops)

    def g_u(self):
        n = self.g_n()
        W = n['body']
        ops = xform(n['ops'], lambda x, y: (W - x, XH - y))
        return self.G('u', W, 44, 50, ops)

    def g_r(self):
        """r: the n's arch cut vertically (C5) where its shoulder starts to fall."""
        v = self.v
        Wn = self.wd(450)
        Wr = round(Wn * 0.70)
        ops = [self.stem(0, 0, XH), ('group', self.arch(v, Wn) + [('sub', rect(Wr, -2000, 4000, 4000))])]
        return self.G('r', Wr, 50, 6, ops)

    def g_o(self):
        W = self.wd(500)
        return self.G('o', W, 40, 40, [('group', self.ring(0, -OV, W, XH + OV))])

    def cut_ring(self, W, xcut, y_lo=-OV - 1, y_hi=XH + OV + 1):
        return [('group', self.ring(0, -OV, W, XH + OV) + [('sub', rect(xcut, y_lo, W + 1, y_hi))])]

    def g_c(self):
        W = self.wd(470)
        xcut = W / 2 + TERM * (W / 2 - self.v)       # C5: the cut stands on the shoulder, above the counter
        return self.G('c', W, 40, 22, self.cut_ring(W, xcut))

    def g_e(self):
        W, v, h = self.wd(490), self.v, self.h
        yb = 0.53 * XH - h / 2
        xcut = W / 2 + (TERM + 0.1) * (W / 2 - self.v)
        ops = [('group', self.ring(0, -OV, W, XH + OV) + [('sub', rect(xcut, -OV - 1, W + 1, yb))]),
               ('add', rect(v - 2, yb, W - 2, yb + h))]
        return self.G('e', W, 40, 26, ops)

    def g_s(self):
        """s: an upper and a lower squircle ring sharing the spine at the centre line (both quarters
        are horizontal there, so the spine runs through without a joint). Lower bowl larger."""
        W, v, h = self.wd(420), self.v, self.h
        hs = 1.05 * h
        ys0 = 0.52 * XH - hs / 2 + 4                 # spine bottom (upper ring's bottom)
        ys1 = ys0 + hs                               # spine top    (lower ring's top)
        inset = 0.035 * W                            # upper bowl a touch narrower
        xc = W / 2
        cut = W / 2 - TERM * (W / 2 - v)        # distance of each cut from its side
        ycu = (ys0 + XH + OV) / 2
        ycl = (-OV + ys1) / 2
        up = self.ring(inset, ys0, W - inset, XH + OV, sv=v * 0.96, sh=h) + \
            [('sub', rect(W - inset - cut, ycu, W + 10, XH + OV + 10)), ('sub', rect(xc, ys0 - 10, W + 10, ycu))]
        # the upper ring's spine band must be exactly hs: its bottom stroke is set to hs
        up = [('add', sq(inset, ys0, W - inset, XH + OV, (W - 2 * inset) / 2, (XH + OV - ys0) / 2)),
              ('sub', sq(inset + 0.96 * v, ys1, W - inset - 0.96 * v, XH + OV - h,
                         (W - 2 * inset) / 2 - 0.96 * v, (XH + OV - ys0) / 2 - (h + hs) / 2)),
              ('sub', rect(W - cut, ycu, W + 10, XH + OV + 10)), ('sub', rect(xc, ys0 - 10, W + 10, ycu))]
        lo = [('add', sq(0, -OV, W, ys1, W / 2, (ys1 + OV) / 2)),
              ('sub', sq(v, -OV + h, W - v, ys0, W / 2 - v, (ys1 + OV) / 2 - (h + hs) / 2)),
              ('sub', rect(-10, -OV - 10, cut, ycl)), ('sub', rect(-10, ycl, xc, ys1 + 10))]
        return self.G('s', W, 34, 34, [('group', up), ('group', lo)])

    # bowls with a stem: the bowl springs out of the stem (C4)
    def bowl(self, W, side, y0=-OV, y1=XH + OV):
        v, h = self.v, self.h
        H = y1 - y0
        if side == 'l':                              # stem on the right (a d g q)
            xo1 = W - JX * v
            outer = sq(0, y0, xo1, y1, xo1 / 2, H / 2)
            inner = sq(v, y0 + h, W - v, y1 - h, (W - 2 * v) / 2, H / 2 - h)
        else:                                        # stem on the left (b p)
            xo0 = JX * v
            outer = sq(xo0, y0, W, y1, (W - xo0) / 2, H / 2)
            inner = sq(v, y0 + h, W - v, y1 - h, (W - 2 * v) / 2, H / 2 - h)
        return [('group', [('add', outer), ('sub', inner)])]

    def g_d(self):
        W, v = self.wd(490), self.v
        return self.G('d', W, 40, 50, self.bowl(W, 'l') + [self.stem(W - v, 0, ASC)])

    def g_q(self):
        W, v = self.wd(490), self.v
        return self.G('q', W, 40, 50, self.bowl(W, 'l') + [self.stem(W - v, DESC, XH)])

    def g_b(self):
        W, v = self.wd(490), self.v
        return self.G('b', W, 50, 40, self.bowl(W, 'r') + [self.stem(0, 0, ASC)])

    def g_p(self):
        W, v = self.wd(490), self.v
        return self.G('p', W, 50, 40, self.bowl(W, 'r') + [self.stem(0, DESC, XH)])

    def g_a(self):
        """a (double-storey): the lower bowl springs out of the stem; the hood is the top half of a
        squircle whose right side runs into the stem, its left end cut vertically (C5)."""
        W, v, h = self.wd(460), self.v, self.h
        yb1 = 0.60 * XH                              # bowl top
        hood_y0 = 0.30 * XH
        cut = W / 2 - TERM * (W / 2 - v)
        bowl = [('group', [('add', sq(0, -OV, W - JX * v, yb1, (W - JX * v) / 2, (yb1 + OV) / 2)),
                           ('sub', sq(v, -OV + h, W - v, yb1 - h, (W - 2 * v) / 2, (yb1 + OV) / 2 - h))])]
        hood = [('group', self.ring(0, hood_y0, W, XH + OV) +
                 [('sub', rect(-10, hood_y0 - 10, W - v, (hood_y0 + XH + OV) / 2)),
                  ('sub', rect(-10, (hood_y0 + XH + OV) / 2, cut, XH + OV + 10))])]
        return self.G('a', W, 34, 50, bowl + hood + [self.stem(W - v, 0, (hood_y0 + XH) / 2, top=False)])

    # C6: hooks
    def hook(self, xs, side, end, HW, HH, cut):
        """half squircle ring hanging off a stem whose LEFT edge is xs.
        end = 'down' (descender; the hook's top half is removed) or 'up' (head of f; bottom half removed);
        side = which way the hook swings ('l' j g, 'r' t f)."""
        v, h = self.v, self.h
        if end == 'down':
            y0, y1 = DESC - OV, DESC - OV + HH
        else:
            y0, y1 = ASC + OV - HH, ASC + OV
        x0, x1 = (xs + v - HW, xs + v) if side == 'l' else (xs, xs + HW)
        ym = (y0 + y1) / 2
        keep_lo, keep_hi = (y0 - 10, ym) if end == 'down' else (ym, y1 + 10)
        ops = self.ring(x0, y0, x1, y1) + [('sub', rect(x0 - 10, keep_hi if end == 'down' else y0 - 10,
                                                         x1 + 10, y1 + 10 if end == 'down' else keep_lo))]
        if side == 'l':
            ops.append(('sub', rect(x0 - 10, y0 - 10, x0 + cut, y1 + 10)))
        else:
            ops.append(('sub', rect(x1 - cut, y0 - 10, x1 + 10, y1 + 10)))
        return [('group', ops)], ym

    def g_j(self):
        v = self.v
        HW = 2 * v + HOOK_IN
        hk, ym = self.hook(HW - v, 'l', 'down', HW, 300, (HW / 2 - TERM * (HW / 2 - self.v)))
        return self.G('j', HW, 50 - (HW - v), 50, hk + [self.stem(HW - v, ym - 1, XH, bot=False), self.dot(HW - v / 2)])

    def g_g(self):
        W, v = self.wd(490), self.v
        hk, ym = self.hook(W - v, 'l', 'down', W, 330, W / 2 - TERM * (W / 2 - v))
        return self.G('g', W, 40, 50, self.bowl(W, 'l') + hk + [self.stem(W - v, ym - 1, XH, bot=False)])

    def g_t(self):
        v, h = self.v, self.h
        xs = 64
        HW = 2 * v + HOOK_IN
        top = XH + 0.45 * (ASC - XH)
        hk, ym = self.hook_foot(xs, HW)
        ops = hk + [self.stem(xs, ym - 1, top, bot=False), ('add', rect(0, XH - h, xs + 210, XH))]
        return self.G('t', xs + HW, 10, 10, ops)

    def hook_foot(self, xs, HW):
        """t's foot: the bottom half of a squircle ring off the stem, swinging right, cut vertically."""
        HH = 320
        y0, y1 = -OV, -OV + HH
        ym = (y0 + y1) / 2
        x0, x1 = xs, xs + HW
        ops = self.ring(x0, y0, x1, y1) + [('sub', rect(x0 - 10, ym, x1 + 10, y1 + 10)),
                                            ('sub', rect(x1 - (HW / 2 - TERM * (HW / 2 - self.v)), y0 - 10, x1 + 10, y1 + 10))]
        return [('group', ops)], ym

    def g_f(self):
        v, h = self.v, self.h
        xs = 64
        HW = 2 * v + HOOK_IN + 30
        hk, ym = self.hook(xs, 'r', 'up', HW, 320, (HW / 2 - TERM * (HW / 2 - self.v)))
        ops = hk + [self.stem(xs, 0, ym + 1, top=False), ('add', rect(0, XH - h, xs + 210, XH))]
        return self.G('f', xs + HW, 10, 0, ops)

    def g_i(self):
        v = self.v
        return self.G('i', v, 50, 50, [self.stem(0, 0, XH), self.dot(v / 2)])

    def g_l(self):
        v = self.v
        return self.G('l', v, 50, 50, [self.stem(0, 0, ASC)])

    def proposal(self):
        A_ = self.A
        return [self.g_n(), self.g_h(), self.g_m(), self.g_u(), self.g_r(), self.g_o(), self.g_c(), self.g_e(),
                self.g_a(), self.g_s(), self.g_g(), self.g_d(), self.g_b(), self.g_p(), self.g_q(), self.g_t(),
                self.g_f(), self.g_i(), self.g_j(), self.g_l(), A_.g_k(), A_.g_v(), A_.g_w(), A_.g_x(), A_.g_y(),
                A_.g_z()]


LC = LC3

if __name__ == '__main__':
    import booleng
    w = os.environ.get('A2_WEIGHT', 'regular')
    B = LC3(w)
    data = {}
    names = ['n', 'h', 'm', 'u', 'r', 'o', 'c', 'e', 'a', 's', 'g', 'd', 'b', 'p', 'q', 't', 'f', 'i', 'j', 'l']
    built = []
    for n in names:
        GUIDES.clear()
        gd = getattr(B, 'g_' + n)()
        gd['guides'] = [('circle', x, y, r, r, 'compass') for x, y, r in dict.fromkeys((round(x), round(y), round(r)) for x, y, r in GUIDES)]
        built.append(gd)
    built += [getattr(B.A, 'g_' + n)() for n in 'kvwxyz']
    for gd in built:
        cs = booleng.evaluate(gd['ops'])
        data[gd['name']] = dict(body=gd['body'], lsb=gd['lsb'], rsb=gd['rsb'], contours=cs,
                                guides=[list(q) for q in gd['guides']])
    os.makedirs('out/lc96', exist_ok=True)
    json.dump(data, open(f'out/lc96/lc96c_{w}.json', 'w'))
    print(w, 'v', B.v, 'h', B.h, len(data), 'glyphs')
