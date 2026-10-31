"""DINHTUONG60s — lowercase PROPOSAL F (v0.96 draft, 27/10 02:42): built from the user's own n g m.

Measured on the user's drawing (x-height 330 px -> 530 u, stem 82 px ~ Medium v 132):
  F1 Grid      x-height 530 · ascender 740 · descender −200 · overshoot 12 (round tops/bottoms).
               Stems end FLAT on the x-height; rounds overshoot.
  F2 Strokes   (27/10 02:46 "đúng principle") P1: every vertical — stem, arch leg, ring side, hook
               side — weighs v = 0.93 V; every round top/bottom, bar and hook bar weighs h = 0.93 H
               (the caps' contrast 0.86). P4: m is dense — legs 0.88 v, roofs 0.94 h, counters 0.84 of
               the n's. P2: the s spine is the heaviest horizontal (1.12 h), above the middle.
               P3: the e bar 0.9 h on the optical centre (0.53 x-height).
  F3 Arch      two compass circles sharing one centre: the counter circle (radius r = half the
               counter) touches the stem's edge; the outer one is r + t. It overshoots the x-height and
               leaves the stem BELOW it — the flat stem top stands proud as a small spur, by itself.
               The leg drops straight from the centre line to the baseline.
  F4 Ring      o = a circle, diameter x-height + 2 overshoots; counter = the ellipse inset by the ring
               strokes (sides 0.84 v, top 0.70 v).
  F5 Bowl      a b d g p q = the F4 ring + a stem whose outer edge stands 0.12 v outside the ring; the
               counter is cut AFTER the stem, so it bites into the stem (the drawing's thin joint), and
               the ring meets the stem below the x-height (the same spur as F3).
  F6 Hook      g j f t: the F3 arch module turned (same t; r = the n's for g, 0.55 of it for j f t) as a quarter, running on as a FLAT bar
               (flat on the baseline / descender / ascender), cut vertically, free end flared (R4).
  F7 Cuts      c e s r: vertical cuts standing on the shoulder, 0.45 of the counter's half-width out
               from the centre (caps R5: vertical cut, never level).
  F8 Others    i j l: stems + round dot (the period). k v w x y z: straight diagonals, level cuts
               (caps R7), from option A.
Usage: A2_WEIGHT=bold python3 lc96f.py -> out/lc96/lc96f_<w>.json
"""
import os, json, math
import lc96 as A
import concept_v1 as CV
from concept_v1 import rect, fstem, fbar
# C4b (31/10 'cần giảm cảm giác chữ bị bóp méo'): a Condensed round must not be the Normal ellipse squeezed. Measured
# fullness (outer area / box) of o, Normal -> Condensed: Roboto 0.807 -> 0.828, Archivo 0.834 -> 0.840, Encode
# 0.829 -> 0.834, Barlow 0.832 -> 0.887 (rounds get FULLER); ours stayed a pure ellipse, 0.789 -> 0.786, counter
# 0.789 -> 0.777. The lowercase ring's handle k goes 0.56 (ellipse, Normal) -> 0.66 at 80 % (fullness 0.831),
# linear in DT_WIDTH: the round's shoulders fill out as it narrows. Normal (DT_WIDTH = 1) is unchanged.
# The boolean re-fit loses ~0.02 of fullness (k 0.66 built 0.809), so k is set by the BUILT result: 0.72 -> o 0.83.
KC_COND = float(os.environ.get('KC_COND', '0.72'))
_KC_C = CV.KC + (KC_COND - CV.KC) * (1.0 - __import__('width').WID) / 0.20


def ell(cx, cy, rx, ry, k=None):
    return CV.ell(cx, cy, rx, ry, _KC_C if k is None else k)

XH, ASC, DESC = A.XH, A.ASC, A.DESC
OV = 12
TA = 1.00                  # P1: an arch's leg weighs what a stem weighs
TS = 1.00                  # P1: a ring's vertical sides weigh what a stem weighs; tops/bottoms = h (caps contrast)
SPUR_D = 46                # F5b: where a bowl meets its stem: 46 u (0.5 h of the Regular) under the x-height
SPUR = 0.12                # bowl stem stands this much (x v) outside the ring
CUT = 0.45                 # F7
CUT_S = 0.72               # P2: s terminals a touch nearer the centre than c (0.45), so its apertures stay open
JT = 0.25                  # F10 (02:51 'điểm giao'): at every joint the counter runs JT x v further into the
                           # stem, so the round stroke THINS into the joint instead of piling ink there
CUT_A = 0.80               # a: the hood's free end reaches well round (a terminal on the left shoulder)
AP_S = float(os.environ.get('S_APER', '0.3')) * 93   # 27/10 16:58 designer chose B: s keeps Regular's arm curve at Regular's reach; aperture = R5 tip clearance 0.3 h Regular
AP_E = 0.5 * 93             # F7c: the e's aperture (tail tip to bar) never under 0.5 h of the Regular (46 u)
R_W = float(os.environ.get('R_W', '0.70'))   # F7c: r's vertical cut at this fraction of the n's width
Z_PERP_K = 0.835   # R2d2: z diagonal thickness square to the stroke, in v (Regular's measured value)
TERM_C, TERM_E, TERM_S, TERM_A, TERM_R = 35, 20, 28, 150, float(os.environ.get('TERM_R', '40'))   # F7b (03:02 'đuôi a, e, c ngắn'): terminals end on a RAY from
                           # the round's centre (cut square to the stroke), at these angles (deg, 0 = right, ccw)
CX0 = 0.88
CX = CX0 * __import__('width').WID   # C2 Condensed: rings x DT_WIDTH (wd() scales the other bodies); F9 (02:49 'co ngang'): every round is an upright ellipse, horizontal radii x 0.88
# R2d: Regular body widths (before CX) of the lowercase diagonals; R2D=0 restores the v0.967 widths
DIAG_W = ({'v': 551, 'y': 551, 'x': 541, 'w': 452, 'k': 505, 'z': 462} if os.environ.get('R2D', '1') == '1'
          else {'v': 470, 'y': 470, 'x': 450, 'w': 380, 'k': 470, 'z': 420})   # k z: reference medians 1.02 / 0.89 (designer 02:44)
CUT_C = 0.80               # c: wider than the 0.45 rule (02:50 'c quá hẹp') but the cut still stands on the shoulder
CUT_E = 0.95               # e: the lower tail runs nearly to the right edge (02:50 'đuôi e ngắn')
HK = 0.55                  # F6: j f t hooks use 0.55 of the n's counter (g uses the full module, as drawn)


def wedge(cx, cy, a0, a1, L=3000):
    """the sector between angles a0 -> a1 (deg, ccw) around (cx, cy): removing it ends a round stroke on two
    rays from its centre, i.e. cut square to the stroke (F7b)."""
    from concept_v1 import poly
    n = max(2, int(abs(a1 - a0) / 30) + 1)
    pts = [(cx, cy)] + [(cx + L * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                         cy + L * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return ('sub', poly(pts))


def ray_x(cx, rx, ry, deg):
    """x where the ray at deg from the centre leaves an ellipse (rx, ry)."""
    t = math.atan2(math.tan(math.radians(deg)) * rx, ry) if abs(math.cos(math.radians(deg))) > 1e-6 else math.pi / 2
    return cx + rx * abs(math.cos(t)) * (1 if math.cos(math.radians(deg)) >= 0 else -1)


def fstem2(x0, y0, x1, y1, f, tl=True, tr=True, bl=True, br=True):
    """R4 stem whose four corners flare independently: a side that meets a notch or a line does not flare
    (F11, 12:26 'khu vực cắt giao chưa rõ ràng')."""
    import flare_spec as _FS                     # R4c: one flare everywhere
    f = _FS.amt(f); L = _FS.length(y1 - y0)
    a, b, c, d = (f if tl else 0), (f if tr else 0), (f if bl else 0), (f if br else 0)
    return [('M', x0 - c, y0), ('L', x1 + d, y0),
            ('C', x1 + d * 0.15, y0 + L * 0.35, x1, y0 + L * 0.7, x1, y0 + L),
            ('L', x1, y1 - L),
            ('C', x1, y1 - L * 0.7, x1 + b * 0.15, y1 - L * 0.35, x1 + b, y1),
            ('L', x0 - a, y1),
            ('C', x0 - a * 0.15, y1 - L * 0.35, x0, y1 - L * 0.7, x0, y1 - L),
            ('L', x0, y0 + L),
            ('C', x0, y0 + L * 0.7, x0 - c * 0.15, y0 + L * 0.35, x0 - c, y0), ('Z',)]


def fbar2(x0, y0, x1, y1, f, left=False, right=True, lo=True, hi=True):
    """R4 bar whose free end flares only AWAY from the line it lies on (lo: flare below y0, hi: above y1) (F11)."""
    import flare_spec as _FS                     # R4c: one flare everywhere
    f = _FS.amt(f); L = _FS.length(x1 - x0)
    fr, fl_ = (f if right else 0), (f if left else 0)
    rlo, rhi = (fr if lo else 0), (fr if hi else 0)
    llo, lhi = (fl_ if lo else 0), (fl_ if hi else 0)
    return [('M', x0, y0 - llo), ('C', x0 + L * 0.35, y0 - llo * 0.15, x0 + L * 0.7, y0, x0 + L, y0),
            ('L', x1 - L, y0), ('C', x1 - L * 0.7, y0, x1 - L * 0.35, y0 - rlo * 0.15, x1, y0 - rlo),
            ('L', x1, y1 + rhi), ('C', x1 - L * 0.35, y1 + rhi * 0.15, x1 - L * 0.7, y1, x1 - L, y1),
            ('L', x0 + L, y1), ('C', x0 + L * 0.7, y1, x0 + L * 0.35, y1 + lhi * 0.15, x0, y1 + lhi), ('Z',)]


class LF(A.LC):
    def __init__(self, w):
        super().__init__(w)
        self.v_reg = round(0.93 * CV.W8['regular']['V'])
        self.t = TA * self.v                      # arch legs / hook sides
        self.ts, self.tt = TS * self.v, self.h   # ring sides / ring + arch tops
        Wn = self.wd(440)
        self.r = (Wn - self.v - self.t) / 2        # the n's counter radius
        self.Wn = Wn
        # F10b (03:13 'mối nối tạo cảm giác dày'; principle: joints thin out, heavier weights thin MORE):
        # joint thinning 0.30 v (Regular) -> 0.45 v (Bold), linear in the stem
        f = (self.v - self.v_reg) / (round(0.93 * CV.W8['bold']['V']) - self.v_reg)
        self.jt = (0.30 + 0.15 * f) * self.v
        # P4c (27/10 13:36 'cân bằng, không sai principle'): principle 'dense letters (a e) need a touch less weight'
        # + 'verticals carry the weight'. Verticals NEVER lighten (m = n, P4b). Only the HORIZONTALS that close a
        # small stacked counter — a's bowl top/bottom, e's bar — thin with weight, like the joints (F10):
        # x1.00 Regular -> x0.925 Medium -> x0.85 Bold. Keeps a's bowl/hood counter ratio ~0.6 in every weight
        # (it fell 0.64 -> 0.39 with full h) on ONE skeleton.
        self.kd = 1.0 - 0.15 * f
        self.Rr = (XH + 2 * OV) / 2                 # ring radius

    def rx_round(self):
        """R2c: the lowercase round class (o c e) widens 0.7 x the stem growth over Regular, half on each side."""
        return CX * self.Rr + __import__('r2c').grow('round', self.v - self.v_reg) / 2

    def wd(self, W_reg):
        return round(__import__('width').cw(W_reg) + 1.2 * (self.v - self.v_reg))

    def G(self, name, body, lsb, rsb, ops, guides=()):
        return dict(name=name, body=body, lsb=lsb, rsb=rsb, ops=ops, guides=list(guides))

    def stem(self, x0, y0, y1, top=True, bot=True, w=None, tr=None):
        x1 = x0 + (self.v if w is None else w)
        if tr is False:                               # F11: the right head corner meets an arch's notch: no flare there
            return ('add', fstem2(x0, y0, x1, y1, self.fl, tl=top, tr=False, bl=bot, br=bot))
        return ('add', fstem(x0, y0, x1, y1, self.fl, top=top, bot=bot))

    def arch_jt(self, r, tl, tt):
        """F10c (28/10 20:19 'làm phần cắt chỗ giao nhau rõ ràng hơn (sâu hơn) vì nó làm điểm nối cảm giác dày hơn'):
        the arch's outer curve meets the stem's edge D = 0.14 x-height under the stem top in every weight (Inter /
        Liberation / DejaVu / Carlito / Poppins 0.09-0.18, median 0.14; F10 alone gave 0.06): the outer curve's
        offset jt is solved for that depth (never less than F10's). Counter and legs are untouched."""
        jt = self.jt
        D = float(os.environ.get('F10C', 0.14)) * XH
        if D > 0:
            ry = r / CX
            cy = XH + OV - (ry + tt)
            ryo = ry + tt
            u = (XH - D - cy) / ryo
            sq = math.sqrt(max(0.0, 1 - u * u))
            jt = max(jt, 2 * (sq * (r + tl) - r) / (1 + sq))
        return jt

    # F3 ----------------------------------------------------------------------------------------
    def arch(self, xs, r, tl, tt=None):
        """counter circle radius r touching the stem edge xs; outer = r + tl (sides) / r + tt (top).
        Returns (ops, cx, cy, guides)."""
        tt = self.h if tt is None else tt
        cx = xs + r
        ry = r / CX                                   # F9: the counter is an upright ellipse
        cy = XH + OV - (ry + tt)
        jt = self.jt                              # F10: the OUTER curve leaves the stem jt later, so the
        # shoulder thins as it joins the stem (no notch: the counter is untouched, the leg keeps its weight)
        jt = self.arch_jt(r, tl, tt)
        ring = ('group', [('add', ell(cx + jt / 2, cy, r + tl - jt / 2, ry + tt)), ('sub', ell(cx, cy, r, ry)),
                          ('sub', rect(-3000, -3000, 6000, cy))])
        leg = ('add', fstem(cx + r, 0, cx + r + tl, cy + 1, self.fl, top=False))
        G = [('circle', cx, cy, r, ry, 'counter'), ('circle', cx, cy, r + tl, ry + tt, 'arch')]
        return [ring, leg], cx, cy, G

    def g_n(self):
        v = self.v
        ops, cx, cy, G = self.arch(v, self.r, self.t)
        return self.G('n', self.Wn, 52, 46, [self.stem(0, 0, XH, tr=False)] + ops, G)

    def g_h(self):
        v = self.v
        ops, cx, cy, G = self.arch(v, self.r, self.t)
        return self.G('h', self.Wn, 52, 46, [self.stem(0, 0, ASC)] + ops, G)

    def g_m(self):
        v = self.v
        # P4b (27/10 13:22 'glyph m phải dày tương đương n'): m's legs and roofs weigh EXACTLY what n's do
        # (v / h, F2 P1); m stays narrower only through its counters (0.84 of the n's)
        rm, tm = 0.84 * self.r, self.t
        o1, cx1, _, G1 = self.arch(v, rm, tm, self.h)
        x2 = cx1 + rm + tm
        o2, cx2, _, G2 = self.arch(x2, rm, tm, self.h)
        W = cx2 + rm + tm
        return self.G('m', W, 52, 46, [self.stem(0, 0, XH, tr=False)] + o1 + o2, G1 + G2)

    def g_u(self):
        from lc96c import xform
        n = self.g_n()
        W = n['body']
        return self.G('u', W, 46, 52, xform(n['ops'], lambda x, y: (W - x, XH - y)))

    def g_r(self):
        v = self.v
        ops, cx, cy, G = self.arch(v, self.r, self.t)
        # F7b: the arm ends on the ray at TERM_R from the arch's centre (cut square to the stroke)
        ring = ops[0]
        if os.environ.get('R_CUT', 'd') in ('a', 'd'):
            # F7d (28/10 'giảm nét nhọn ... chỉnh lại góc cong'): the r's inner corner at the cut was 35-36 deg, the
            # house tails meet their cut at ARM_ANG (c 52-54, e 60, a 47-54, s 54-59). Two ways to reach ARM_ANG:
            #  'a' = cut earlier on the counter's own arc (where it runs ARM_ANG off vertical; shorter arm)
            #  'd' = keep the reach, the counter's top-right quarter is STRETCHED (R5d, like c) until it meets the
            #        cut at ARM_ANG; the outer quarter stretched x R_LO so the arm keeps its face.
            r_, ry_ = self.r, self.r / CX
            jt, tl, tt = self.arch_jt(self.r, self.t, self.h), self.t, self.h
            ang = float(os.environ.get('R_ANG', CV.ARM_ANG))
            def qd(x0, y0, a, b, k=CV.KC):       # upper-right quarter of ell(): (x0+a, y0) -> (x0, y0+b)
                return [('M', x0, y0), ('L', x0 + a, y0), ('C', x0 + a, y0 + k * b, x0 + k * a, y0 + b, x0, y0 + b), ('Z',)]
            def off_v(x0, a, b, xc, k=CV.KC):    # angle off vertical of that quarter where x = xc
                P = [(x0 + a, 0), (x0 + a, k * b), (x0 + k * a, b), (x0, b)]
                lo, hi = 0.0, 1.0
                for _ in range(60):
                    t = (lo + hi) / 2; m = 1 - t
                    x = m**3 * P[0][0] + 3*m*m*t * P[1][0] + 3*m*t*t * P[2][0] + t**3 * P[3][0]
                    (lo, hi) = (t, hi) if x > xc else (lo, t)
                t = (lo + hi) / 2; m = 1 - t
                d = [3*m*m*(P[1][j]-P[0][j]) + 6*m*t*(P[2][j]-P[1][j]) + 3*t*t*(P[3][j]-P[2][j]) for j in (0, 1)]
                y = sum(c * p[1] for c, p in zip((m**3, 3*m*m*t, 3*m*t*t, t**3), P))
                return math.degrees(math.atan2(abs(d[0]), abs(d[1]))), y
            if os.environ.get('R_CUT', 'd') == 'a':
                lo, hi = cx, cx + r_
                for _ in range(60):
                    mid = (lo + hi) / 2
                    (lo, hi) = (mid, hi) if off_v(cx, r_, ry_, mid)[0] > ang else (lo, mid)
                x_cut = (lo + hi) / 2
                arm = ('group', [ring, ('sub', rect(x_cut, -3000, 6000, 6000))])
            else:
                x_cut = min(R_W * self.Wn, cx + r_ * math.cos(math.atan(ry_ / r_ * math.tan(math.radians(35)))))
                if os.environ.get('REACH_OUT'):
                    CV._REACH_OUT['lc96f.g_r:arm'] = x_cut - cx
                if __import__('width').WID < 1.0:
                    # C5b: the arm's reach scales with the body (x DT_WIDTH of the Normal reach in this weight), not
                    # with the Condensed counter (which shrinks to ~0.7): r was 0.65 / 0.62 / 0.60 of n vs 0.69 / 0.67 / 0.64
                    x_cut = max(x_cut, cx + __import__('width').WID * CV._reach_normal(self.w).get('lc96f.g_r:arm', 0.0))
                dx = x_cut - cx
                lo, hi = max(dx, r_), 20 * r_
                for _ in range(80):
                    mid = (lo + hi) / 2
                    (lo, hi) = (lo, mid) if off_v(cx, mid, ry_, x_cut)[0] > ang else (mid, hi)
                a_i = (lo + hi) / 2
                xo, ao, bo = cx + jt / 2, r_ + tl - jt / 2, ry_ + tt
                a_o = (float(os.environ.get('R_LO', '1.0')) if os.environ.get('R_LO', '1.0') != 'face' else 1.0) * ao
                if os.environ.get('R_LO') == 'face':      # outer stretch solved: vertical face at the cut = the arm's top stroke
                    yi = cy + off_v(cx, a_i, ry_, x_cut)[1]
                    lo, hi = ao, 20 * ao
                    for _ in range(80):
                        mid = (lo + hi) / 2
                        (lo, hi) = (lo, mid) if cy + off_v(xo, mid, bo, x_cut)[1] - yi > float(os.environ.get('R_FACE', 1.0)) * tt else (mid, hi)
                    a_o = (lo + hi) / 2
                arm = ('group', [('add', ell(xo, cy, ao, bo)), ('add', qd(xo, cy, a_o, bo)),
                                 ('sub', ell(cx, cy, r_, ry_)), ('sub', qd(cx, cy, a_i, ry_)),
                                 ('sub', rect(-3000, -3000, 6000, cy)), ('sub', rect(x_cut, -3000, 6000, 6000))])
                G = G + [('circle', cx, cy, a_i, ry_, 'arm-in'), ('circle', xo, cy, a_o, bo, 'arm-out')]
            G = G + [('vline', x_cut, 'cut')]
            return self.G('r', x_cut, 52, 8, [self.stem(0, 0, XH, tr=False), arm], G)
        if os.environ.get('R_CUT', 'v') == 'v':
            # F7c (28/10 visual-weight audit + 'chữ r có thể làm nét cắt dọc như concept hiện có không?'): the arm ends
            # with the house VERTICAL cut (like a c e C S), at R_W of the n's width (refs 0.54-0.70; ours was 0.88 on
            # the 40° ray, which left r light and loose).
            # 28/10 'cắt dọc bold đang lỗi dư nét nhọn dưới': a cut at a fixed fraction of n fell OUTSIDE the counter's
            # right extreme in Bold (401 > 394) and left a sliver under the arm. R5 instead: the cut stands where the
            # counter's own arc runs TAIL_PHI (35°) off vertical, so it always crosses the counter and meets it the
            # same way as every house tail (a c e C S); R_W only caps the reach.
            r_, ry_ = self.r, self.r / CX
            t_ = math.atan(ry_ / r_ * math.tan(math.radians(35)))
            x_cut = min(R_W * self.Wn, cx + r_ * math.cos(t_))
            arm = ('group', [ring, ('sub', rect(x_cut, -3000, 6000, 6000))])
            G = G + [('vline', x_cut, 'cut')]
            return self.G('r', x_cut, 52, 8, [self.stem(0, 0, XH, tr=False), arm], G)
        arm = ('group', [ring, wedge(cx, cy, -90, TERM_R)])
        body = ray_x(cx, self.r + self.t, self.r / CX + self.h, TERM_R)
        return self.G('r', body, 52, 8, [self.stem(0, 0, XH, tr=False), arm], G)

    # F4 / F5 -------------------------------------------------------------------------------------
    def ring(self, cx, R=None, rx=None):
        R = self.Rr if R is None else R
        rx = CX * R if rx is None else rx
        cy = XH / 2
        return [('add', ell(cx, cy, rx, R)), ('sub', ell(cx, cy, rx - self.ts, R - self.tt))], cy

    def g_o(self):
        R, Rx = self.Rr, self.rx_round()
        ops, cy = self.ring(Rx, rx=Rx)
        return self.G('o', 2 * Rx, 36, 36, [('group', ops)], [('circle', Rx, cy, Rx, R, 'ring')])

    def bowl(self, side, y0, y1, top=True, bot=True):
        """F5: ring + stem; side 'r' = stem on the right (a d g q)."""
        R, v = self.Rr, self.v
        Rx = self.bowl_rx()
        ring, cy = self.ring(Rx, rx=Rx)
        dx = self.spur_dx()
        if side == 'r':
            cx = Rx
            xr = cx + dx + v                         # F5b: the stem stands where the bowl meets it SPUR_D under the x-height
            stem = self.stem(xr - v, y0, y1, top=top, bot=bot)
            W = xr
        else:
            cx = Rx
            xl = cx - dx - v
            stem = self.stem(xl, y0, y1, top=top, bot=bot)
            W = 2 * Rx
        counter = self.bowl_counter(side, cx, cy, Rx, R, xr - v if side == 'r' else xl + v)
        ops = [('group', [ring[0], stem, counter])]
        return ops, W, cx, cy

    def _spur_f(self, k):
        """the ring's half-width fraction at the F5b notch height, for a ring of handle k (k = KC: the ellipse)."""
        R = self.Rr
        yn = max(0.0, min(1.0, (XH - SPUR_D - XH / 2) / R))
        if abs(k - CV.KC) < 1e-9:
            return math.sqrt(max(0.0, 1 - yn * yn))
        lo, hi = 0.0, 1.0
        for _ in range(60):
            t = (lo + hi) / 2; m = 1 - t
            (lo, hi) = (t, hi) if 3 * m * m * t * k + 3 * m * t * t + t ** 3 < yn else (lo, t)
        t = (lo + hi) / 2; m = 1 - t
        return m ** 3 + 3 * m * m * t + 3 * m * t * t * k

    def bowl_rx(self):
        """C4b (QA 31/10): the Condensed bowl of b d p q g is the fuller ring; its stem sits on the F5b notch of THAT
        curve (SPUR_D = 45 u deep, as Normal; an ellipse formula left it 19-20 u, the thick joint F10c removed), and
        the ring is narrowed so the letter keeps its Normal ink / n: Rx' = Rx (1 + f_ellipse) / (1 + f_full)."""
        Rx = CX * self.Rr
        W_ = __import__('width')
        if W_.WID >= 1.0:
            return Rx
        # ... and the stem's share: the Condensed stem is x0.93 while the letter is x~0.81, which made every bowl
        # letter +0.031 / +0.025 / +0.022 of n wider than Normal (QA C2b); the ring gives back that excess.
        excess = self.v * (1 - (W_.WID + 0.01) / W_.SV)
        return (Rx * (1 + self._spur_f(CV.KC)) - excess) / (1 + self._spur_f(_KC_C))

    def spur_dx(self):
        """F5b (12:26 'khu vực cắt giao chưa rõ ràng' at Medium/Bold): the bowl's outer curve meets the stem's inner
        edge exactly SPUR_D below the x-height (and above the baseline) in every weight — a clear, deliberate notch,
        never a step of a few units. Returns the stem's inner edge as an offset from the ring's centre."""
        return self.bowl_rx() * self._spur_f(_KC_C)

    def bowl_counter(self, side, cx, cy, Rx, R, x_stem):
        """F10d (12:22 'bóp vòng khuyết'): the counter stays a WHOLE ellipse — never cut by the stem. Its far side
        keeps the bowl's full stroke; its stem side is squeezed to just touch the stem's inner edge. The bowl's
        stroke then thins by itself toward the two joints (principle: joints thin out), the stem stays straight."""
        if side == 'r':
            x0, x1 = cx - (Rx - self.ts), x_stem
        else:
            x0, x1 = x_stem, cx + (Rx - self.ts)
        return ('sub', ell((x0 + x1) / 2, cy, (x1 - x0) / 2, R - self.tt))

    def g_d(self):
        ops, W, cx, cy = self.bowl('r', 0, ASC, bot=False)        # R4: the end joined to the bowl does not flare
        return self.G('d', W, 36, 52, ops)

    def g_a(self):
        """a (02:51 'a có móc'): double-storey. Hood = the n's arch turned the other way (its counter
        touches the stem from the left, outer = counter + strokes), the free end cut vertically on the
        shoulder (F7). Bowl = a smaller upright ellipse ring (0.58 x-height) springing out of the stem,
        its counter running JT into the stem (F10). Stem from the baseline (flared) into the hood."""
        v, h = self.v, self.h
        # C4b exception (QA 31/10): the a keeps true ellipses. Its fuller Condensed bowl closed the bowl/stem notch (Normal
        # 28 / 22 u deep in M / B) into a 25-29 deg crotch on the baseline, and its hood tail met the cut at 42 deg (Bold).
        W = self.wd(round(470 * CX0))
        r = (W - v - 0.85 * v) / 2                   # hood counter: between the hood's left side and the stem
        ry = r / CX
        xs = W - v                                   # stem's left edge
        cx = xs - r
        cy = XH + OV - (ry + h)
        jt = self.jt
        hood = ('group', [('add', CV.ell(cx + 0.075 * v, cy, r + 0.925 * v, ry + h)), ('sub', CV.ell(cx, cy, r, ry)),
                          ('sub', rect(-3000, -3000, 6000, cy)),
                          wedge(cx, cy, getattr(self, 'term_a', TERM_A), 180)])   # F7b: the hood's end on the ray at TERM_A
        if os.environ.get('AE_CUT', 'R5') == 'R5':     # F7e (27/10 18:24 'đổi đuôi chữ a, c, e như yêu cầu'): the hood's free
            # end is the caps tail R5d (C mirrored): vertical cut, Regular's stretched arm, same cut in every weight.
            yb0 = 0.62 * XH
            GA = []
            ta = self.tail(GA, cx, cy + ry, cx - r, 0.85 * v, 'l', 'up', tip_limit=max(cy, yb0 + AP_S), cry=ry,
                           ring=(cy, r + 0.85 * v, ry + h))
            hood = ('group', [('add', CV.ell(cx + 0.075 * v, cy, r + 0.925 * v, ry + h)), ('sub', CV.ell(cx, cy, r, ry))] +
                    CV.arm_ink(ta) + [('sub', rect(cx, -3000, 6000, cy)), ('sub', ta['disk']),
                              ('sub', rect(-3000, -3000, ta['xt'], 6000)), ('sub', rect(-3000, -3000, cx, ta['tip']))])
                                                                     # (small forms may turn it further: lcsym R0b)
        yb = 0.62 * XH
        bx1 = W - 0.5 * v
        brx, bry = bx1 / 2, (yb + OV) / 2
        bcy = (yb - OV) / 2
        st = ('add', fstem2(xs, 0, W, cy + 1, self.fl, tl=False, tr=False, bl=False, br=True))   # F11 (13:20 QA): the foot's LEFT
        # corner sits in the bowl/stem notch — no flare into a notch (it nearly closed the notch into a pin-hole)
        cx0 = 0.95 * v                               # F10d: whole ellipse, far side full stroke, stem side touching the stem
        bowl = ('group', [('add', CV.ell(brx, bcy, brx, bry)), st,
                          ('sub', CV.ell((cx0 + xs) / 2, bcy, (xs - cx0) / 2, bry - self.kd * h))])   # P4b (13:22): a's bowl weighs h like every round (no 'dense letter' lightening)
        return self.G('a', W, 34, 50, [hood, bowl], locals().get('GA', []))

    def g_q(self):
        ops, W, cx, cy = self.bowl('r', DESC, XH, top=False)
        return self.G('q', W, 36, 52, ops)

    def g_b(self):
        ops, W, cx, cy = self.bowl('l', 0, ASC, bot=False)
        sp = self.spur_dx() + self.v - self.bowl_rx()          # how far the stem stands left of the ring
        return self.G('b', W, 52 + sp, 36, ops)          # the stem's edge stands sp left of the body

    def g_p(self):
        ops, W, cx, cy = self.bowl('l', DESC, XH, top=False)
        sp = self.spur_dx() + self.v - self.bowl_rx()
        return self.G('p', W, 52 + sp, 36, ops)

    # F6 -------------------------------------------------------------------------------------------
    def hook(self, x_edge, where, reach, k=1.0):
        """the arch module as a quarter + a flat bar.
        where: 'dl' (descender, swinging left: g j — x_edge = stem's RIGHT edge),
               'br' (baseline, swinging right: t — x_edge = stem's LEFT edge),
               'ur' (ascender, swinging right: f — x_edge = stem's LEFT edge).
        reach: the bar's free end x. Returns (ops, y where the stem joins the hook)."""
        r, t = k * self.r, self.h
        R = r + self.v                    # the side of the quarter is the stem itself (v); its bar is t
        if where == 'dl':
            cx, cy = x_edge - R, DESC + r / CX + t
            q = [('sub', rect(-3000, cy, 6000, 3000)), ('sub', rect(-3000, -3000, cx, 3000))]
            bar = ('add', fbar2(reach, DESC, cx + 1, DESC + t, self.fl, left=False, right=False))   # F11: a hook's bar ends in a clean vertical cut
            yj = cy
        elif where == 'br':
            cx, cy = x_edge + R, r / CX + t
            q = [('sub', rect(-3000, cy, 6000, 3000)), ('sub', rect(cx, -3000, 6000, 3000))]
            bar = ('add', fbar2(cx - 1, 0, reach, t, self.fl, left=False, right=False))              # F11
            yj = cy
        else:  # 'ur'
            cx, cy = x_edge + R, ASC - r / CX - t
            q = [('sub', rect(-3000, -3000, 6000, cy)), ('sub', rect(cx, -3000, 6000, 3000))]
            bar = ('add', fbar2(cx - 1, ASC - t, reach, ASC, self.fl, left=False, right=False))      # F11
            yj = cy
        ring = ('group', [('add', ell(cx, cy, R, r / CX + t)), ('sub', ell(cx, cy, r, r / CX))] + q)   # a hook continues the stem: no joint
        return [ring, bar], yj, (cx, cy)

    def g_g(self):
        R, v = self.Rr, self.v
        Rx = self.bowl_rx()
        ring, cy = self.ring(Rx, rx=Rx)
        xr = Rx + self.spur_dx() + v                    # F5b
        hk, yj, _ = self.hook(xr, 'dl', 0.30 * Rx)
        if os.environ.get('G_HOOK', 'curve') == 'curve':    # F6g (designer chose E, 27/10 18:30); asked 18:27 'đuôi chữ g thường cho cong thay vì thẳng':
            # the descender = the lower half of an elliptic ring (stem side = the stem, bottom = h, overshoot OV),
            # its free left end the caps tail R5d (vertical cut, Regular's stretched arm, reach floor).
            h = self.h
            rxh = xr - v - Rx                          # counter: from the bowl's axis to the stem's left edge
            ryh = float(os.environ.get('G_RY', '0.65')) * rxh
            cyh = DESC - OV + h + ryh
            G = []
            tg = self.tail(G, Rx, cyh - ryh, Rx - rxh, v, 'l', 'down', tip_limit=-OV - AP_S, cry=ryh,
                           ring=(cyh, rxh + v, ryh + h))
            hk = [('group', [('add', CV.ell(Rx, cyh, rxh + v, ryh + h)), ('sub', CV.ell(Rx, cyh, rxh, ryh)),
                             ('sub', rect(-3000, cyh, 6000, 3000))] + CV.arm_ink(tg) +
                   [('sub', tg['disk']), ('sub', rect(-3000, -3000, tg['xt'], 3000)), ('sub', rect(-3000, tg['tip'], Rx, cyh + 1))] +
                   ([('sub', rect(-3000, -3000, 0.30 * Rx, 3000))] if os.environ.get('G_CUT', 'old') == 'old' else []))]   # cut at the old bar's end
            yj = cyh
            if self.w != 'regular' and os.environ.get('G_KEEP', '1') == '1':
                # F6h (28/10 14:50-14:51 'bụng chữ g sau khi bold lên đã phá mất form của regular', 'phần đuôi sau khi
                # bold lên đã phá nét cong mềm mại', 'độ dày ... phần đuôi cũng không đồng bộ'): the hook's counter here
                # does not shrink with weight (stem edge and bowl axis are fixed), so R5d's 'Regular radii = counter + dv'
                # gave Medium / Bold a DIFFERENT, larger arm curve: a hump in the inner edge and a thinner face at the cut
                # (B 92 < R 103). Rule: every weight draws REGULAR's descender. Outer edge left of the bowl axis = Regular's
                # (ring + stretched arm, same cut, same reach); right of it the weight's own ring (the stem grew there).
                # Inner edge (counter + arm) = Regular's, moved up by the bottom stroke's growth (h - h_regular), so the
                # bottom, the arm and the face at the cut all thicken by the same amount and keep Regular's curve.
                Rg = LF('regular')
                cyR = DESC - OV + Rg.h + ryh
                dy = cyh - cyR
                GR = []
                tR = Rg.tail(GR, Rx, cyR - ryh, Rx - rxh, Rg.v, 'l', 'down', tip_limit=-OV - AP_S, cry=ryh,
                             ring=(cyR, rxh + Rg.v, ryh + Rg.h))
                mv = lambda p: [(o[0],) + tuple(c + (dy if k % 2 else 0) for k, c in enumerate(o[1:])) for o in p]
                hk = [('group', [('group', [('add', CV.ell(Rx, cyh, rxh + v, ryh + h)), ('sub', rect(-3000, -3000, Rx, 3000))]),
                                 ('group', [('add', CV.ell(Rx, cyR, rxh + Rg.v, ryh + Rg.h)), ('sub', rect(Rx, -3000, 3000, 3000))])] +
                       CV.arm_ink(tR) +
                       [('sub', CV.ell(Rx, cyh, rxh, ryh)), ('sub', rect(-3000, cyh, 6000, 3000)), ('sub', mv(tR['disk'])),
                        ('sub', rect(-3000, -3000, tR['xt'], 3000)), ('sub', rect(-3000, tR['tip'] + dy, Rx, cyh + 1))] +
                       ([('sub', rect(-3000, -3000, 0.30 * Rx, 3000))] if os.environ.get('G_CUT', 'old') == 'old' else []))]
                G = [(g[0], g[1], g[2] + dy) + tuple(g[3:]) if g[0] == 'pt' else g for g in GR]   # inner points moved with the inner edge
        counter = self.bowl_counter('r', Rx, cy, Rx, R, xr - v)       # F10d
        st = self.stem(xr - v, yj - 1, XH, top=False, bot=False)
        ops = [('group', [ring[0], st, counter])] + hk
        return self.G('g', xr, 36, 52, ops, locals().get('G', []))

    def g_j(self):
        v = self.v
        xr = v + 40
        R = HK * self.r + self.v
        hk, yj, _ = self.hook(xr, 'dl', xr - R - 50, k=HK)
        ops = hk + [self.stem(xr - v, yj - 1, XH, bot=False), self.dot(xr - v / 2)]
        return self.G('j', xr, 52 - (xr - v) + 0, 52, ops)

    def g_t(self):
        v, h = self.v, self.h
        xs = 70
        top = XH + 0.45 * (ASC - XH)
        R = HK * self.r + self.v
        reach = xs + R + 60
        hk, yj, _ = self.hook(xs, 'br', reach, k=HK)
        ops = hk + [self.stem(xs, yj - 1, top, bot=False), ('add', rect(0, XH - 0.9 * self.h, xs + v + 120, XH))]
        return self.G('t', reach, 12, 12, ops)

    def g_f(self):
        v = self.v
        xs = 70
        R = HK * self.r + self.v
        reach = xs + R + 50
        hk, yj, _ = self.hook(xs, 'ur', reach, k=HK)
        ops = hk + [self.stem(xs, 0, yj + 1, top=False), ('add', rect(0, XH - 0.9 * self.h, xs + v + 120, XH))]
        return self.G('f', reach, 12, 0, ops)

    # F7 -------------------------------------------------------------------------------------------
    def g_c(self):
        Rx = self.rx_round()
        ring, cy = self.ring(Rx, rx=Rx)
        if os.environ.get('AE_CUT', 'R5') == 'R5':     # F7e: both ends = the caps C (R5d) on the lowercase ring
            G, R = [], self.Rr
            ryi = R - self.tt
            tu = self.tail(G, Rx, cy + ryi, 2 * Rx - self.ts, self.ts, 'r', 'up', cry=ryi, ring=(cy, Rx, R))
            tl = self.tail(G, Rx, cy - ryi, 2 * Rx - self.ts, self.ts, 'r', 'down', cry=ryi, ring=(cy, Rx, R))
            ops = ring + CV.arm_ink(tu) + CV.arm_ink(tl) + CV.band(tu['disk'], y0=cy) + CV.band(tl['disk'], y1=cy) + [
                ('sub', rect(tu['xt'], -3000, 6000, 6000)), ('sub', rect(Rx, tl['tip'], tu['xt'] + 1, tu['tip']))]
            return self.G('c', tu['xt'], 36, 30, [('group', ops)], G)     # ink ends at the cut; same right side as F7b
        body = ray_x(Rx, Rx, self.Rr, TERM_C)        # F7b: both ends on rays at +-TERM_C
        return self.G('c', body, 36, 30, [('group', ring + [wedge(Rx, cy, -TERM_C, TERM_C)])])

    def g_e(self):
        R = self.Rr
        Rx = self.rx_round()
        ring, cy = self.ring(Rx, rx=Rx)
        hb = 0.9 * self.h * self.kd                  # P3: a bar is a touch lighter than the round's top; P4c: thins with weight
        yb = 0.56 * XH                               # P3: the bar sits above the middle (optical centre); 0.56 keeps the eye and the aperture balanced
        from concept_v1 import poly
        xo = lambda y: Rx + Rx * math.sqrt(max(0, 1 - ((y - cy) / R) ** 2)) - 1   # the ring's outer edge at height y
        lo, hi = yb - hb / 2, yb + hb / 2
        edge = [(xo(lo), lo)] + ([(2 * Rx - 1, cy)] if lo < cy < hi else []) + [(xo(hi), hi)]   # QA: the bar's end follows the ring
        bar = ('add', poly([(self.ts - 2, lo)] + edge + [(self.ts - 2, hi)]))
        a_lo = math.degrees(math.atan2(min(lo, cy) - cy, Rx))
        # F7c (03:13 'e dính đuôi và thân ở Bold'; principle: openings in REGULAR units): the tail ends on the
        # ray at TERM_E unless that brings its inner corner closer than AP_E to the bar — then the ray turns down
        # just enough. Regular keeps its long tail; Bold gets the same white in units.
        rxi, ryi = Rx - self.ts, R - self.tt
        th = TERM_E
        while th < 70:
            t = math.atan2(math.tan(math.radians(th)) * rxi, ryi)
            if lo - (cy - ryi * math.sin(t)) >= AP_E:
                break
            th += 0.5
        cut = [wedge(Rx, cy, -th, a_lo), ('sub', rect(Rx, cy - 1, 6000, lo))]
        if os.environ.get('AE_CUT', 'R5') == 'R5':     # F7e: the caps tail R5d on e's lower end (vertical cut, Regular's arm)
            G = []
            tl = self.tail(G, Rx, cy - ryi, 2 * Rx - self.ts, self.ts, 'r', 'down', tip_limit=lo - AP_S, cry=ryi,
                           ring=(cy, Rx, R), face=float(os.environ.get('E_FACE', '1.12')),
                           reach=float(os.environ.get('E_REACH', '192')) * __import__('width').WID + (Rx - CX * R))   # C5b: x DT_WIDTH   # R5e: lone tail: approved F7 reach, optical face
            cut = CV.arm_ink(tl) + CV.band(tl['disk'], y1=lo) + [('sub', rect(tl['xt'], -3000, 6000, lo)),
                                                                  ('sub', rect(Rx, tl['tip'], 6000, lo))]
            return self.G('e', 2 * Rx, 36, 24, [('group', ring + cut), bar], G)
        return self.G('e', 2 * Rx, 36, 24, [('group', ring + cut), bar])

    def g_s(self):
        """F7s (27/10 15:40 'cắt chữ s để không ngã ra sau … vẽ chữ s thường theo cách vẽ S hoa'): the s is the
        caps S construction (R5 + R11, concept_v1.s_shape) at the x-height: two stacked elliptic rings sharing
        the spine; each free end is cut VERTICALLY at the outer edge - 0.55 stroke (Regular units) and its
        inner edge is one compass arc meeting that cut 35 deg off vertical. The 28 deg ray cut (F7b) tilted
        both terminal faces the same way, so the letter read as rotated back; vertical cuts stand it up
        like S. Strokes unchanged: sides 0.95 v, tops h, spine 1.12 h; same width."""
        if os.environ.get('S_RAY') == '1':
            return self.g_s_ray()
        W = 0.86 * 2 * CX * self.Rr + __import__('r2c').grow('s', self.v - self.v_reg)   # R2c
        # Aperture: F7c / QA 1.6 (openings in REGULAR units): each tip stays >= AP_E (0.5 h Regular = 46) off the
        # spine; when the R5 arc would come closer (Medium, Bold) the reach is kept and the arc steepens (R2b).
        T, ov, sx, sy, sm, ti = XH, OV, 0.95 * self.v, self.h, 1.12 * self.h, 18
        G = []
        ym = (T - sm) / 2 + 8
        xr_u = W - ti / 2 - sx
        tu = self.tail(G, W / 2, T + ov - sy, xr_u, sx, 'r', 'up', tip_limit=ym + sm + AP_S, cry=((T + ov - sy) - (ym + sm)) / 2,
                       ring=((ym + T + ov) / 2, (W - ti) / 2, (T + ov - ym) / 2))
        tl = self.tail(G, W / 2, -ov + sy, sx, sx, 'l', 'down', tip_limit=ym - AP_S, cry=(ym - (-ov + sy)) / 2,
                       ring=((-ov + ym + sm) / 2, W / 2, (ym + sm + ov) / 2))
        up = [('add', CV.ebox(ti / 2, ym, W - ti / 2, T + ov)),
              ('sub', CV.ebox(ti / 2 + sx, ym + sm, W - ti / 2 - sx, T + ov - sy))] + CV.arm_ink(tu) + [
              ('sub', tu['disk']),
              ('sub', rect(tu['xt'], tu['cy'], W + 1, T + ov + 1)),
              ('sub', rect(W / 2, ym - 1, W + 1, tu['tip']))]
        lo = [('add', CV.ebox(0, -ov, W, ym + sm)),
              ('sub', CV.ebox(sx, -ov + sy, W - sx, ym))] + CV.arm_ink(tl) + [
              ('sub', tl['disk']),
              ('sub', rect(-1, -ov - 1, tl['xt'], tl['cy'])),
              ('sub', rect(-1, tl['tip'], W / 2 - 3, ym + sm + 1))]
        G.append(('hline', ym, 'spine'))
        if os.environ.get('S_SPINE', 'g2') == 'g2':
            # R11b (28/10 22:50 'phần uốn lượn ở giữa chữ s và S chưa mượt'): the same smooth spine as the caps S
            fw = (self.v - self.v_reg) / (round(0.93 * CV.W8['bold']['V']) - self.v_reg)
            spine, y_up, y_lo = CV.s_spine(W, T, ov, sx, sy, sm, ti, G, k=CV.spine_k(fw))
            up.append(('sub', rect(-1, ym - 1, W / 2, y_up)))
            lo.append(('sub', rect(W / 2 - 4, y_lo, W + 1, ym + sm + 1)))   # covers the W/2-3 sliver of the ring top
            return self.G('s', W, 34, 34, [('group', up), ('group', lo), ('add', spine)], G)
        return self.G('s', W, 34, 34, [('group', up), ('group', lo)], G)

    def g_s_ray(self):
        """s (02:50 'không cân'): built point-symmetric — the upper bowl is the lower one turned 180 deg,
        then the optical corrections: the spine (the heaviest horizontal, 1.12 h) sits at 0.52 of the
        x-height so the lower bowl is the larger, and the upper bowl is 0.96 as wide. Both terminals
        are cut vertically by the same rule (F7) and reach the same way round."""
        R, v, h = self.Rr, self.v, self.h
        W = 0.86 * 2 * CX * R
        sv = 0.95 * v
        tsp = 1.12 * h
        yspine = 0.52 * XH
        ys0, ys1 = yspine - tsp / 2, yspine + tsp / 2
        top, bot = XH + OV, -OV
        xc = W / 2
        rxl = W / 2
        rxu = 0.96 * W / 2
        ryu, cyu = (top - ys0) / 2, (top + ys0) / 2
        ryl, cyl = (ys1 - bot) / 2, (ys1 + bot) / 2
        iu_t, iu_b = top - h, ys1
        il_t, il_b = ys0, bot + h
        up = [('add', ell(xc, cyu, rxu, ryu)), ('sub', ell(xc, (iu_t + iu_b) / 2, rxu - sv, (iu_t - iu_b) / 2)),
              wedge(xc + 3, cyu, -90, TERM_S), ('sub', rect(xc + 3, -3000, 6000, cyu))]      # F7b; QA: the halves overlap 3u at the spine
        lo = [('add', ell(xc, cyl, rxl, ryl)), ('sub', ell(xc, (il_t + il_b) / 2, rxl - sv, (il_t - il_b) / 2)),
              wedge(xc - 3, cyl, 90, 180 + TERM_S), ('sub', rect(-3000, cyl, xc - 3, 3000))]
        return self.G('s', W, 34, 34, [('group', up), ('group', lo)])

    # F9: the straight letters condense with the rounds
    # R2d (28/10 02:39 'bề ngang chữ v, x, w, y hình như hơi hẹp — chữ thường'): the lowercase diagonals take the
    # caps' own proportion: ink / n = V / H (v y 1.10, x 1.08, w 1.58). Before: v y 0.94, x 0.91, w 1.30 (refs 1.09-1.17).
    def g_v(self):
        import glyphs_c as GL
        W = self.wd(round(DIAG_W['v'] * CX0))
        dw = 0.9 * self.v / math.cos(math.atan2(W / 2 - 50, XH))
        return self.G('v', W, 14, 14, GL.vshape(0, W, XH, 0, dw, 110))

    def g_w(self):
        import glyphs_c as GL
        W1 = self.wd(round(DIAG_W['w'] * CX0))
        dw = 0.85 * self.v / math.cos(math.atan2(W1 / 2 - 40, XH))
        W = 2 * W1 - dw
        return self.G('w', W, 12, 12, [('group', GL.vshape(0, W1, XH, 0, dw, 96)), ('group', GL.vshape(W - W1, W, XH, 0, dw, 96))])

    def g_x(self):
        import glyphs_c as GL
        W = self.wd(round(DIAG_W['x'] * CX0))
        dw = 0.9 * self.v / math.cos(math.atan2(W - 160, XH)) * 1.04
        return self.G('x', W, 12, 12, [('add', GL.pinch((dw / 2, XH), (W - dw / 2, 0), dw)), ('add', GL.pinch((W - dw / 2, XH), (dw / 2, 0), dw))])

    def g_z(self):
        from concept_v1 import poly
        W, h = self.wd(round(DIAG_W['z'] * CX0)), self.h
        dw = 0.9 * self.v / math.cos(math.atan2(W - 200, XH - 2 * h)) * 1.04
        if os.environ.get('Z_PERP', '1') == '1':
            # R2d2 (28/10 visual-weight audit: z Bold grew +9% over the lowercase median; refs -8..+1%): the old width
            # assumed a run of W - 200, so the diagonal's TRUE thickness (square to the stroke) went 0.83 v Regular ->
            # 0.92 v Bold. Solve the horizontal width so the perpendicular thickness is Z_PERP_K x v in every weight
            # (Regular's own 0.835: Regular unchanged).
            dy, T = XH - 2 * h, Z_PERP_K * self.v
            lo, hi = 1.0, W * 0.9
            for _ in range(60):
                mid = (lo + hi) / 2
                if mid * dy / math.hypot(W - mid, dy) < T: lo = mid
                else: hi = mid
            dw = (lo + hi) / 2
        return self.G('z', W, 28, 28, [('add', fbar2(0, XH - h, W, XH, self.fl, left=True, right=False, hi=False)), ('add', fbar2(0, 0, W, h, self.fl, left=False, right=True, lo=False)),
                                        ('add', poly([(W - dw, XH - h + 1), (W, XH - h + 1), (dw, h - 1), (0, h - 1)]))])

    def g_k(self):
        """k (F11, 12:26): the caps K rule (arm from 0.30, leg from the arm's centre at 0.52). The little white
        triangle between the stem, the arm and the leg's upper end is FILLED, so below the arm there is one clean
        V between the stem and the leg, and above it one clean V between the arm and the leg."""
        from concept_v1 import poly
        v = self.v
        W = self.wd(round(DIAG_W['k'] * CX0))
        dg = 0.9 * v
        yc, yj = 0.30 * XH, 0.52 * XH
        aw = dg / math.cos(math.atan2(W - v - 40, XH - yc))
        ax0, ax1 = v - aw / 2, W - aw / 2
        lw = dg * 0.95 / math.cos(math.atan2(W - v - 110, yj))
        xj = ax0 + (yj - yc) / (XH - yc) * (ax1 - ax0)
        arm_lo = lambda x: yc + (x - (ax0 + aw / 2)) * (XH - yc) / (ax1 - ax0)      # arm's lower-right edge
        # leg's left edge: from (xj - lw/2, yj) to (W - lw, 0)
        lx = lambda y: (W - lw) + (xj - lw / 2 - (W - lw)) * y / yj
        # where the leg's left edge meets the arm's lower edge (P3) and the stem (P2)
        y3 = yj
        for _ in range(60):
            y3 = arm_lo(lx(y3))
        y2 = yj * (v - (W - lw)) / (xj - lw / 2 - (W - lw)) if (xj - lw / 2) != (W - lw) else -1
        ops = [self.stem(0, 0, ASC),
               ('group', [('add', poly([(ax0 - aw / 2, yc), (ax0 + aw / 2, yc), (ax1 + aw / 2, XH), (ax1 - aw / 2, XH)])),
                          ('sub', rect(-400, -400, v / 4, XH + 400))]),
               ('add', poly([(xj - lw / 2, yj), (xj + lw / 2, yj), (W, 0), (W - lw, 0)]))]
        if y2 > 0:
            ops.append(('add', poly([(v - 2, arm_lo(v - 2)), (lx(y3), y3), (v - 2, y2)])))
        ops += [('sub', rect(v, XH, W + 200, XH + 400)), ('sub', rect(v, -400, W + 200, 0))]
        return self.G('k', W, 52, 14, ops)

    def g_y(self):
        """y (12:30 'nét y lỗi'): the v's two arms (same edges, same angle) — the right arm runs on, straight, to
        the descender (level cut); the left arm runs on until BOTH its edges meet the right arm's inner edge, so it
        ends flush inside the right arm: one V crotch above, one clean knee below, no ledge."""
        from concept_v1 import poly
        W = self.wd(round(DIAG_W['y'] * CX0))
        dw = 0.9 * self.v / math.cos(math.atan2(W / 2 - 50, XH))
        fb = 110
        c = W / 2

        def line(p, q):
            return p, (q[0] - p[0], q[1] - p[1])

        def meet(l1, l2):
            (p, d), (q, e) = l1, l2
            den = d[0] * e[1] - d[1] * e[0]
            t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
            return (p[0] + t * d[0], p[1] + t * d[1])

        Lout = line((0, XH), (c - fb / 2, 0)); Lin = line((dw, XH), (c - fb / 2 + dw, 0))
        Rout = line((W, XH), (c + fb / 2, 0)); Rin = line((W - dw, XH), (c + fb / 2 - dw, 0))
        k = (W - (c + fb / 2)) / XH
        xd = c + fb / 2 - k * (-DESC)
        right = ('add', poly([(W - dw, XH), (W, XH), (xd, DESC), (xd - dw, DESC)]))
        Rin2 = line((W - dw + 6, XH), (c + fb / 2 - dw + 6, 0))     # 6u inside the right arm: a true overlap, one outline
        left = ('add', poly([(0, XH), (dw, XH), meet(Lin, Rin2), meet(Lout, Rin2)]))
        return self.G('y', W, 14, 14, [right, left])

    def proposal(self):
        return [self.g_n(), self.g_h(), self.g_m(), self.g_u(), self.g_r(), self.g_o(), self.g_c(), self.g_e(),
                self.g_a(), self.g_s(), self.g_g(), self.g_d(), self.g_b(), self.g_p(), self.g_q(), self.g_t(),
                self.g_f(), self.g_i(), self.g_j(), self.g_l(), self.g_k(), self.g_v(), self.g_w(), self.g_x(),
                self.g_y(), self.g_z()]


LC = LF

if __name__ == '__main__':
    import booleng
    w = os.environ.get('A2_WEIGHT', 'regular')
    B = LF(w)
    data = {}
    for gd in B.proposal():
        cs = booleng.evaluate(gd['ops'])
        data[gd['name']] = dict(body=gd['body'], lsb=gd['lsb'], rsb=gd['rsb'], contours=cs,
                                guides=[list(q) for q in gd['guides']])
    os.makedirs('out/lc96', exist_ok=True)
    json.dump(data, open(f'out/lc96/lc96f_{w}.json', 'w'))
    print(w, 'v', B.v, 't', round(B.t), 'r', round(B.r), 'Wn', B.Wn, len(data), 'glyphs')
