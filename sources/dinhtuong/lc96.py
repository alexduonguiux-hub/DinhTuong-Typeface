"""DINHTUONG60s — lowercase PROPOSAL (v0.96 draft, 27/10): a new lowercase derived from the capitals.

The old lowercase is ignored. Every letter is built from the CAPS grammar:
  L1 Grid      x-height 530 (0.76 cap — sign lettering, large x) · ascender 740 (a touch above the
               caps 700, so b d h k l stand clear of capitals) · descender −200 · overshoot 7.
  L2 Strokes   v = 0.93 V, h = 0.93 H (lowercase a touch lighter than caps, same contrast 0.86).
  L3 Ring      o = the O's stadium ring scaled to the x-height: 480 wide, two compass ends + straight
               sides; counter = ring inset by one stroke. c e follow it.
  L4 Stems     ruled, free ends flare like the caps (R4); stems that meet an arch end flat.
  L5 Arch      n h m r u: the caps D/P/R bowl turned into an arch — the top runs FLAT out of the stem
               and turns down through ONE compass (FULL radius). Junction SQUARE, no notch (caps R9).
  L6 Bowl      a b d g p q: the same half-stadium as the caps D/P bowl, flat at the stem, square joint.
  L7 Tail      c e s a (hood) and the hooks of f g j t: the caps R5/R6 rules unchanged.
  L8 Diagonal  k v w x y z: flat level cuts, 0.9 v, as the caps (R7).
  L9 Dots      i j: round dot = the period; marks = the caps steel-strip system at x-height + 50.
Usage: A2_WEIGHT=bold python3 lc96.py  -> out/lc96/lc96_<w>.json (outlines + guides per glyph)
"""
import os, sys, json, math
import concept_v1 as CV

XH, ASC, DESC, OV = 530, 740, -200, 7
RING = 480
KV = 0.93

# re-point the concept rule book at the new lowercase grid (this process only)
CV.XH, CV.ASC, CV.DESC, CV.OV_L, CV.RING_o = XH, ASC, DESC, OV, RING
CV.JSTYLE = 'none'
from concept_v1 import rrect, rect, fstem, poly, FULL, band, ell


class LC(CV.Build):
    def __init__(self, w):
        super().__init__(w)
        self.v = round(KV * self.V)
        self.h = round(KV * self.H)
        self.R_o = RING / 2
        self.r_o = self.R_o - self.v
        self.r1 = self.r_o / 2
        self.k = 0.93 * CV.W8['regular']['V'] / self.v
        self.TAIL_CLEAR = 0.3 * self.h * self.k

    # L5 / L6: no notch anywhere (caps R9: square joints)
    def notch_out(self, G, *a, **k):
        return ('sub', poly([(-9000, -9000), (-8999, -9000), (-8999, -8999)]))

    def joint(self, G, *a, **k):
        return self.notch_out(G)

    def bowl(self, G, x0, y0, x1, y1, sv, sh, side, sh_top=None):
        sh_top = sh if sh_top is None else sh_top
        if side == 'r':
            R = (FULL, 0, 0, FULL)
            ob, cb = (x0, y0, x1 - sv / 2, y1), (x0 + sv, y0 + sh, x1 - sv + 1, y1 - sh_top)
        else:
            R = (0, FULL, FULL, 0)
            ob, cb = (x0 + sv / 2, y0, x1, y1), (x0 + sv - 1, y0 + sh, x1 - sv, y1 - sh_top)
        for (a0, b0, a1, b1), lab in ((ob, 'bowl'), (cb, 'counter')):
            r = min(a1 - a0, b1 - b0) / 2
            cx = a0 + r if side == 'r' else a1 - r
            G += [('circle', cx, b1 - r, r, r, lab), ('circle', cx, b0 + r, r, r, lab)]
        return ('group', [('add', rrect(*ob, R)), ('sub', rrect(*cb, R))])

    def g_o(self):
        G, W = [], RING
        G += [('circle', W / 2, XH + OV - self.R_o, self.R_o, self.R_o, 'o-ring'),
              ('circle', W / 2, -OV + self.R_o, self.R_o, self.R_o, 'o-ring')]
        return dict(name='o', body=W, lsb=34, rsb=34, ops=self.ring(0, -OV, W, XH + OV, self.v, self.h), guides=G)

    def g_t(self):
        """t: a ruled cross — stem from the baseline to 0.5 of the way to the ascender, bar flush with
        the x-height (h thick); the foot turns right through the R6 hook (like J/j, mirrored)."""
        v, h = self.v, self.h
        W = 340
        xs = 70
        top = XH + 0.5 * (ASC - XH)
        rin = self.r1 * 0.8
        yc = -OV + h + rin
        hk, xcut = self.hook([], xs, yc, h, v, rin, down=False)
        hk = [(o, c) for o, c in hk]
        # hook(down=False) builds the UPPER half; mirror it vertically about yc to get the foot
        def flip(c):
            return [(q[0],) + tuple(val if i % 2 == 0 else 2 * yc - val for i, val in enumerate(q[1:])) if q[0] != 'Z' else q for q in c]
        foot = [(o, flip(c)) for o, c in hk]
        G = [('hline', XH, 'x-height'), ('circle', xs + rin + v, yc, rin, rin, 'hook')]
        ops = [('group', foot + [('add', rect(xs, yc - 1, xs + v, top))]),
               ('add', rect(xs - 70, XH - h, W, XH)), ('add', fstem(xs, yc, xs + v, top, self.fl, bot=False))]
        return dict(name='t', body=W, lsb=10, rsb=20, ops=ops, guides=G)

    def g_f(self):
        """f: stem + R6 hook at the top (the j/g hook turned up), bar flush with the x-height."""
        v, h = self.v, self.h
        xs = 60
        rin = self.r1
        yc = ASC - h - rin
        hk, xcut = self.hook([], xs, yc, h, v, rin, down=False)
        W = xcut + 10
        G = [('hline', XH, 'x-height'), ('circle', xs + rin + v, yc, rin, rin, 'hook'), ('vline', xcut, 'cut')]
        ops = [('group', hk + [('add', rect(xs, 0, xs + v, yc + 1))]),
               ('add', fstem(xs, 0, xs + v, yc, self.fl, top=False)),
               ('add', rect(0, XH - h, xs + v + 150, XH))]
        return dict(name='f', body=W, lsb=10, rsb=0, ops=ops, guides=G)

    def dot(self, cx):
        d = 1.18 * self.v
        return ('add', ell(cx, XH + 70 + d / 2, d / 2, d / 2))

    def g_i(self):
        v = self.v
        return dict(name='i', body=v, lsb=46, rsb=46, guides=[],
                    ops=[('add', fstem(0, 0, v, XH, self.fl, top=False)), self.dot(v / 2)])

    def g_l(self):
        v = self.v
        return dict(name='l', body=v, lsb=46, rsb=46, guides=[], ops=[('add', fstem(0, 0, v, ASC, self.fl))])

    def g_j(self):
        """j: the g's hook (R6) on a stem, dot above."""
        v, h = self.v, self.h
        rin = self.r1
        bottom = DESC - OV
        yc = bottom + h + rin
        W = 2 * (rin + v) - 20
        hk, xcut = self.hook([], W, yc, h, v, rin, down=True)
        ops = [('group', hk + [('add', rect(W - v, yc - 1, W, XH))]), self.dot(W - v / 2)]
        return dict(name='j', body=W, lsb=46 - (W - v), rsb=46, guides=[('circle', W - rin - v, yc, rin, rin, 'hook'), ('vline', xcut, 'cut')], ops=ops)

    def g_k(self):
        """k: the caps K rule at the x-height (arm from 0.35 of the height, leg from the arm's centre)."""
        v = self.v
        W = 470
        dg = 0.9 * v
        yc, yj = 0.30 * XH, 0.52 * XH
        aw = dg / math.cos(math.atan2(W - v - 40, XH - yc))
        ax0, ax1 = v - aw / 2, W - aw / 2
        lw = dg * 0.95 / math.cos(math.atan2(W - v - 110, yj))
        xj = ax0 + (yj - yc) / (XH - yc) * (ax1 - ax0)
        ops = [('add', fstem(0, 0, v, ASC, self.fl)),
               ('group', [('add', CV.poly([(ax0 - aw / 2, yc), (ax0 + aw / 2, yc), (ax1 + aw / 2, XH), (ax1 - aw / 2, XH)])),
                          ('sub', rect(-400, -400, v / 4, XH + 400))]),
               ('add', CV.poly([(xj - lw / 2, yj), (xj + lw / 2, yj), (W, 0), (W - lw, 0)])),
               ('sub', rect(v, XH, W + 200, XH + 400)), ('sub', rect(v, -400, W + 200, 0))]
        return dict(name='k', body=W, lsb=46, rsb=14, ops=ops, guides=[])

    def g_v(self):
        v = self.v
        W = 470
        dw = 0.9 * v / math.cos(math.atan2(W / 2 - 50, XH))
        import glyphs_c as GL
        return dict(name='v', body=W, lsb=14, rsb=14, guides=[], ops=GL.vshape(0, W, XH, 0, dw, 120))

    def g_y(self):
        """y: the v whose right arm runs on down to the descender (flat cut), left arm stops on it."""
        v = self.v
        W = 480
        dw = 0.9 * v / math.cos(math.atan2(W / 2 - 40, XH))
        c = W / 2
        slope = (W - dw - c + 60) / XH
        ops = [('add', CV.poly([(0, XH), (dw, XH), (c + 30, 40), (c - 30 - dw * 0.2, 40)])),
               ('add', CV.poly([(W - dw, XH), (W, XH), (c - 60 - slope * (0 - DESC) + dw, DESC), (c - 60 - slope * (0 - DESC), DESC)]))]
        return dict(name='y', body=W, lsb=14, rsb=14, guides=[], ops=ops)

    def g_w(self):
        """w: two v's sharing the middle stroke, as the caps W (multi-diagonal 0.9 v)."""
        import glyphs_c as GL
        W1 = 380
        dw = 0.85 * self.v / math.cos(math.atan2(W1 / 2 - 40, XH))
        W = 2 * W1 - dw
        return dict(name='w', body=W, lsb=12, rsb=12, guides=[],
                    ops=[('group', GL.vshape(0, W1, XH, 0, dw, 100)), ('group', GL.vshape(W - W1, W, XH, 0, dw, 100))])

    def g_x(self):
        import glyphs_c as GL
        W = 450
        dw = 0.9 * self.v / math.cos(math.atan2(W - 160, XH)) * 1.04
        return dict(name='x', body=W, lsb=12, rsb=12, guides=[],
                    ops=[('add', GL.pinch((dw / 2, XH), (W - dw / 2, 0), dw)), ('add', GL.pinch((W - dw / 2, XH), (dw / 2, 0), dw))])

    def g_z(self):
        import glyphs_c as GL
        W, h = 420, self.h
        dw = 0.9 * self.v / math.cos(math.atan2(W - 200, XH - 2 * h)) * 1.04
        return dict(name='z', body=W, lsb=30, rsb=30, guides=[],
                    ops=[('add', GL.fbar(0, XH - h, W, XH, left=True, right=False)), ('add', GL.fbar(0, 0, W, h, left=False, right=True)),
                         ('add', CV.poly([(W - dw, XH - h + 1), (W, XH - h + 1), (dw, h - 1), (0, h - 1)]))])

    def proposal(self):
        n = self.g_n(); h = self.g_h(); m = self.g_m(); u = self.g_u(); r = self.g_r()
        out = [n, h, m, u, r, self.g_o(), self.g_c(), self.g_e(), self.g_a(), self.g_s(), self.g_g(),
               self.g_d(), self.g_b(), self.g_p(), self.g_q(), self.g_t(), self.g_f(), self.g_i(), self.g_j(),
               self.g_l(), self.g_k(), self.g_v(), self.g_w(), self.g_x(), self.g_y(), self.g_z()]
        return out


if __name__ == '__main__':
    import booleng
    w = os.environ.get('A2_WEIGHT', 'regular')
    B = LC(w)
    data = {}
    for gd in B.proposal():
        cs = booleng.evaluate(gd['ops'])
        data[gd['name']] = dict(body=gd['body'], lsb=gd['lsb'], rsb=gd['rsb'], contours=cs,
                                guides=[list(q) for q in gd['guides']])
    os.makedirs('out/lc96', exist_ok=True)
    json.dump(data, open(f'out/lc96/lc96_{w}.json', 'w'))
    print(w, 'v', B.v, 'h', B.h, len(data), 'glyphs')
