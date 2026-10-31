"""A2 'Biển sơn Chợ Lớn' — figures 0-9 and punctuation / symbols.

Same vocabulary as the letters:
  * stems V=168 with the brush flare at free ends (fstem), bars H=140 / HM=124 (fbar)
  * round 'compass' bowls (ring with FULL radii), open terminals cut vertically/horizontally
  * diagonals on the thinner diagonal rule (DIAG*), flat cuts
  * dots are round (circle d = V) — same family as the i-dot / dấu nặng
Figures are lining (cap height) and proportional.
Every glyph is keyed by its character in G so compose()/proofs pick it up.
"""
import os as _os
import math as _m
import glyphs_c as GL
from glyphs_c import *
from marks_flat import band

import marks_flat as _MF
D = round(_MF.DOT_D * 1.03)  # punctuation dot = i-dot x1.03 in EVERY weight (same dot family)
R = D / 2
K_ = GL.WKC                  # stroke scale vs Bold caps
SBF = 36 + (168 - V) * 0.15  # figure sidebearing


def _g(ch, W, lsb, rsb):
    return Glyph(ch, W, lsb, rsb, ord(ch))


def _reg(g):
    G[g.name] = g
    return g


def dot(cx, cy, r=R):
    return circle(cx, cy, r)


def slab(x0b, x1b, yb, x0t, x1t, yt):
    """quadrilateral with flat (horizontal) cuts top and bottom."""
    return poly([(x0b, yb), (x1b, yb), (x1t, yt), (x0t, yt)])


def rot_ops(ops, ang, cx, cy):
    ca, sa = _m.cos(ang), _m.sin(ang)
    f = lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca)
    out = []
    for op, c in ops:
        out.append((op, rot_ops(c, ang, cx, cy)) if op == 'group' else (op, transform(c, f)))
    return out


def rot180_ops(ops, cx, cy):
    return rot_ops(ops, _m.pi, cx, cy)


# ============================ FIGURES ============================
# 26/10 audit "bộ số các weight": figures were drawn on the full cap stem (V/H) and read
# heavier than the text, most of all in Regular. Lining figures now run at FIG_K of the cap
# strokes (same ratio in every weight), diagonals keep the diagonal rule on top of that.
FIG_K = 0.95
_FIG_KEYS = ('V', 'H', 'HM', 'DIAG', 'DIAG_Z')


def figweight(fn):
    def wrapped():
        g0 = globals(); saved = {k: g0[k] for k in _FIG_KEYS}
        try:
            for k in _FIG_KEYS: g0[k] = saved[k] * FIG_K
            return fn()
        finally:
            g0.update(saved)
    wrapped.__name__ = fn.__name__
    return wrapped


@figweight
def fig0():
    W = __import__('width').cw(500) + gw('round')
    g = _g('0', W, SBF, SBF)
    g.group(ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    return _reg(g)


@figweight
def fig1():
    # v0.963 (27/10 16:27 'giảm độ dài phần đầu số 1 còn 1/2 và cho nét đều lại'): the flag's run is halved
    # (170 -> 85, the same in every weight, same slope) and it is a RULED stroke of even thickness: two parallel
    # edges, perpendicular thickness = the diagonal rule (R2: single diagonal 0.9 x stem), left end cut vertical.
    style = _os.environ.get('ONE_FLAG', 'wedge2')
    if style == 'wedge2':
        return _fig1_wedge2()
    if style == 'beak':
        return _fig1_beak()
    if style == 'wedge':
        return _fig1_wedge()
    run = 170 * float(_os.environ.get('ONE_RUN', 0.5))
    W = run + V
    g = _g('1', W, SBF - 6, SBF + 20)
    g.add(fstem(W - V, 0, W, CAP, top=False))
    xs = W - V
    a = _m.atan2(140, 170)                              # slope of the flag (unchanged)
    drop = run * _m.tan(a)
    tv = 0.9 * V / _m.cos(a)                            # vertical thickness of a stroke 0.9 V thick, measured square
    g.add(poly([(xs + 1, CAP), (xs + 1, CAP - tv - (xs + 1 - xs) * _m.tan(a)), (0, CAP - drop - tv), (0, CAP - drop)]))
    return _reg(g)


def _arc(C, R, t0, t1):
    """circular arc (centre C, radius R) from angle t0 to t1 (radians) as cubic segments (<= 45 deg each)."""
    n = max(1, int(abs(t1 - t0) / (_m.pi / 4)) + 1)
    out, d = [], (t1 - t0) / n
    k = 4 / 3 * _m.tan(d / 4)
    for i in range(n):
        a0, a1 = t0 + i * d, t0 + (i + 1) * d
        p0 = (C[0] + R * _m.cos(a0), C[1] + R * _m.sin(a0)); p3 = (C[0] + R * _m.cos(a1), C[1] + R * _m.sin(a1))
        out.append(('C', p0[0] - k * R * _m.sin(a0), p0[1] + k * R * _m.cos(a0),
                    p3[0] + k * R * _m.sin(a1), p3[1] - k * R * _m.cos(a1), p3[0], p3[1]))
    return out


def _fig1_wedge():
    """R15b (28/10 02:16, designer's sample 'thử lại kiểu này'): the 1's flag is a solid WEDGE - one ruled edge from the
    stem's top-left corner down to a point, and a level underside back to the stem wall (a crisp inner corner).
    Measured on the sample: reach 0.71 stem, the edge 36.5 deg off vertical. Reach and angle are Regular's in every
    weight (the v0.963 rule: the flag's run is the same in every weight), so the heavier stem simply stands beside it."""
    reach = 0.71 * 116.0
    ang = _m.radians(36.5)
    drop = reach / _m.tan(ang)
    W = reach + V
    g = _g('1', W, SBF - 6, SBF + 20)
    xs = W - V
    g.add(fstem(xs, 0, W, CAP, top=False))
    g.add(poly([(xs + 2, CAP), (xs + 2, CAP - drop), (0, CAP - drop), (xs, CAP)]))
    return _reg(g)


def _fig1_wedge2():
    """R15d (28/10 17:29 sample '196' + 18:00 'đã chỉnh lại số 1 chưa'): measured on the sample (cap 397 px = 700 u):
      * the stem is a straight stroke of the DIAGONAL thickness 0.9 V (= the 6 / 9 diagonals, sample: 1-stem 77 px,
        9-diagonal 82 px perpendicular, bowl side 88 px): the figures' straight strokes are one weight
      * the flag is a solid wedge whose TOP runs on from the stem's top 63 u to the left, a ruled edge (the R15b angle
        36.5° off vertical) down to the tip 141 u left of the stem, and a level underside 109 u under the cap line back
        to the stem wall (crisp inner corner). Flag sizes are the same in every weight (v0.963 rule)."""
    sv = 0.9 * V
    top_l, reach, drop = 63.0, 141.0, 109.0
    W = reach + sv
    g = _g('1', W, SBF - 6, SBF + 20)
    xs = W - sv
    g.add(fstem(xs, 0, W, CAP, top=False))
    g.add(poly([(xs + 2, CAP), (xs + 2, CAP - drop), (0, CAP - drop), (xs - top_l, CAP)]))
    return _reg(g)


def _fig1_beak():
    """R15 (28/10 02:07, designer's sample 'glyph đuôi chỗ đầu số 1 nên thử như thế này'): the 1's flag is a short
    BAR (thickness H) cut vertically at its free end; its top edge rises 4.7 deg toward the stem and turns up into
    the stem's top through one compass arc (r 0.75 H_reg), its bottom edge runs level and turns down into the stem
    wall through one long compass arc (r 1.59 H_reg, leaving the bottom 0.85 H_reg before the wall) - a bracketed beak, not a diagonal flag. Reach (stem wall -> tip)
    and the flag's centre line are in Regular units; the bar thickens about its centre line (Regular is the master)."""
    Hr = 100.0                                          # Regular's H: the unit of every length here
    reach = 1.31 * Hr
    W = reach + V
    g = _g('1', W, SBF - 6, SBF + 20)
    xs = W - V                                          # the stem's left wall
    g.add(fstem(xs, 0, W, CAP, top=False))
    yc = CAP - 1.13 * Hr                                # the flag's centre line at its tip
    top, bot = yc + H / 2, yc - H / 2
    sl = _m.radians(4.7)
    T1 = (xs - 0.77 * Hr, top + (reach - 0.77 * Hr) * _m.tan(sl))
    R1 = 0.75 * Hr
    C1 = (T1[0] - R1 * _m.sin(sl), T1[1] + R1 * _m.cos(sl))
    dy = CAP - C1[1]
    t_end = _m.asin(max(-1.0, min(1.0, dy / R1)))       # where the arc meets the cap line (angle from the centre)
    t_start = sl - _m.pi / 2
    top_arc = _arc(C1, R1, t_start, t_end)
    P2 = (C1[0] + R1 * _m.cos(t_end), CAP)
    R2 = 1.59 * Hr                                     # 02:13 'bụng nét nên cong hơn': a longer, flatter belly
    B1 = (xs - 0.85 * Hr, bot)
    C2 = (B1[0], bot + R2)
    xe = xs + 2                                          # into the stem (union overlaps)
    t2 = _m.asin(min(1.0, (xe - C2[0]) / R2))
    bot_arc = _arc(C2, R2, -_m.pi / 2, -_m.pi / 2 + t2)
    # outline: tip bottom -> level bottom -> fillet into the stem -> up the stem -> cap -> arc down -> rising top -> tip top
    path = [('M', 0, bot), ('L', B1[0], B1[1])] + bot_arc + [('L', xe, CAP), ('L', P2[0], P2[1])]
    rev = []
    pts = [(C1[0] + R1 * _m.cos(t), C1[1] + R1 * _m.sin(t)) for t in (t_end, t_start)]
    rev = _arc(C1, R1, t_end, t_start)
    path += rev + [('L', 0, top), ('Z',)]
    g.add(path)
    return _reg(g)


def _ell(cx, cy, rx, ry, a0, a1, n=40):
    return [(cx + rx * _m.cos(a), cy + ry * _m.sin(a)) for a in [a0 + (a1 - a0) * k / n for k in range(n + 1)]]


def _tangent_join(cx, cy, rx, ry, target, a_from=0.0, a_to=-1.4):
    """angle on the ellipse (going clockwise) where the tangent points straight at target."""
    best, ba = 1e9, a_from
    for k in range(400):
        a = a_from + (a_to - a_from) * k / 399
        px, py = cx + rx * _m.cos(a), cy + ry * _m.sin(a)
        tx, ty = rx * _m.sin(a), -ry * _m.cos(a)            # clockwise direction
        vx, vy = target[0] - px, target[1] - py
        err = abs(_m.atan2(ty, tx) - _m.atan2(vy, vx))
        if err < best:
            best, ba = err, a
    return ba


def _tan_pt(px, py, cx, cy, r, side):
    """tangent point on circle (cx,cy,r) seen from external point P; side=+1/-1 picks the branch."""
    dx, dy = px - cx, py - cy
    d = _m.hypot(dx, dy)
    a = _m.atan2(dy, dx)
    b = _m.acos(r / d)
    t = a + side * b
    return (cx + r * _m.cos(t), cy + r * _m.sin(t)), t


@figweight
def fig2():
    """2 = the C/S bowl (same ring, same vertical terminal cut) whose right side runs on into
    the Z diagonal TANGENTIALLY: the diagonal's outer edge is tangent to the bowl's outer
    curve and its inner edge tangent to the counter — no kink at the join."""
    W = 510
    g = _g('2', W, SBF, SBF)
    y0, top = 196, CAP + OV_C
    yc = (y0 + top) / 2
    # outer bowl ~ circle (stadium with a tiny straight part), counter = stadium
    Ro = W / 2
    cxo, cyo = W / 2, y0 + Ro                 # centre of the outer lower semicircle
    ri = (W - 2 * V) / 2
    cyi = y0 + H + ri                          # centre of the counter's lower semicircle
    # diagonal lands on the base bar: left edge at (0, H), right edge at (bx, H)
    A = (0.0, 36.0)                           # 26/10: short vertical face at the foot (was H, then 64)
    bx = 180.0
    def lower_right(P, cx, cy, r):
        cands = [_tan_pt(P[0], P[1], cx, cy, r, sd) for sd in (1, -1)]
        (pt, t) = max(cands, key=lambda c: c[0][0] - c[0][1] * 0.2)
        if t > 0: t -= 2 * _m.pi
        return pt, t
    Ti, ti = lower_right(A, W / 2, cyi, ri)    # inner edge tangent (counter side)
    ux, uy = Ti[0] - A[0], Ti[1] - A[1]
    ul = _m.hypot(ux, uy)
    for _ in range(30):                         # diagonal as thick as the Z's (perpendicular)
        B = (bx, H - 1)
        To, to = lower_right(B, cxo, cyo, Ro)  # outer edge tangent (right/lower side)
        dist = abs((B[0] - A[0]) * uy - (B[1] - A[1]) * ux) / ul
        bx += (DIAG_Z - dist) * 0.8
    arc_o = [(cxo + Ro * _m.cos(a), cyo + Ro * _m.sin(a)) for a in [0 + (to - 0) * k / 24 for k in range(25)]]
    arc_i = [(W / 2 + ri * _m.cos(a), cyi + ri * _m.sin(a)) for a in [ti + (0 - ti) * k / 24 for k in range(25)]]
    join = [(W, yc + 1)] + arc_o + [B, A] + arc_i + [(W - V, yc + 1)]
    g.group(ring(0, y0, W, top, V, H, FULL, FULL) +
            [('sub', rect(-1, y0 - 1, W + 1, yc)),                         # upper half only
             ('sub', rect(-1, y0 - 1, V, top + 1)),        # house cut: vertical, on the counter wall
             *[b for b in [GL.blunt_tip(W / 2, top - H - ri, ri, V, 'l', 'up', V)] if b]])
    g.add(poly(join))
    # base bar: its top-left corner is tucked under the diagonal, so the foot's vertical
    # face is only A.y tall (26/10 "phần này ngắn lại")
    xh = (H - A[1]) * (Ti[0] - A[0]) / (Ti[1] - A[1])
    g.group([('add', fbar(0, 0, W, H, left=False, right=True)),
             ('sub', poly([(-1, A[1]), (xh, H + 1), (-1, H + 1)]))])
    return _reg(g)


@figweight
def fig3():
    """3 = two bowls opened on the left, joined by ONE middle bar of HM: the bar is a clean
    rectangle (square inner/outer corners on the left), cut flat at 0.3W; bowls round on the
    right; free ends cut vertically (C rule)."""
    W = 486
    g = _g('3', W, SBF - 4 - 36, SBF)          # open left side: ink starts ~SBF-10 from the origin
    top, bot = CAP + OV_C, -OV_C
    ym = 300                                  # bottom of the middle bar
    xm = W * 0.30
    xu0, xu1 = 26, W - 18                     # upper bowl a little narrower
    xcu = xu0 + (xu1 - xu0) * 0.12           # 26/10 audit: terminals reach further left
    xcl = W * 0.08                           # (ink 389 -> ~450, colour 0.75 -> ~0.85)
    # 26/10 terminal rule: cuts meet the counters where their walls are vertical, and the
    # end cuts keep TERM_KEEP of the stroke (term_x / term_y, same as C 6 9 S ...)
    xcu = xu0 + V - 8                         # 26/10 house hook cut: vertical, on the counter wall
    xcl = V
    ru = min(xu1 - xu0 - 2 * (V - 8), top - H - ym - HM) / 2
    rl = min(W - 2 * V, ym - bot - H) / 2
    ycu = term_y(top - H - 24, ym + HM, top - H, xu1 - xu0 - 2 * (V - 8), 'down')
    ycl = term_y(bot + H + 24, bot + H, ym, W - 2 * V, 'up')
    up = [('add', rrect(xu0, ym, xu1, top, (FULL, FULL, FULL, 0))),
          ('sub', rrect(xu0 + V - 8, ym + HM, xu1 - V + 8, top - H, (FULL, FULL, FULL, 0))),
          ('sub', rect(-1, ym + HM, xcu, top + 1)),                           # house cut on the counter wall
          *[b for b in [GL.blunt_tip(xcu + ru, top - H - ru, ru, xcu, 'l', 'up', V - 8)] if b]]
    lo = [('add', rrect(0, bot, W, ym + HM, (0, FULL, FULL, FULL))),
          ('sub', rrect(V, bot + H, W - V, ym, (0, FULL, FULL, FULL))),
          ('sub', rect(-1, bot - 1, xcl, ym)),                                 # house cut on the counter wall
          *[b for b in [GL.blunt_tip(V + rl, bot + H + rl, rl, xcl, 'l', 'down', V)] if b]]
    g.group(up); g.group(lo)
    g.sub(rect(-1, ym - 1, xm, ym + HM + 1))   # middle bar ends flat
    g.lsb = SBF - 1 - min(xcu, xcl)            # open left: ink starts ~SBF-1 like before
    return _reg(g)


@figweight
def fig4():
    # R15g (28/10 18:25 'giảm bề ngang số 4 một chút cho cân bằng thị giác'): the open triangle reads lighter than a
    # closed round, so the 4 stays a little wider than the 0 -- 1.04 x the 0's width in EVERY weight (median of Inter,
    # Liberation, DejaVu, Carlito, Poppins); it was 1.08 / 1.09 / 1.10 (R / M / B), growing faster than the 0
    W = float(_os.environ.get('FOUR_K', 1.04)) * (500 + gw('round'))
    g = _g('4', W, SBF - 10, SBF - 6)
    yb = 170
    sx = W - V - 64
    g.add(fstem(sx, 0, sx + V, CAP, top=False))
    dw = diag_dx(DIAG, sx, CAP - yb - HM)
    g.group([('add', poly([(sx - 6, CAP), (sx + V, CAP), (dw, yb + HM - 1), (0, yb + HM - 1)])),
             ('add', fbar(0, yb, W, yb + HM, left=False, right=True))])
    return _reg(g)


@figweight
def fig5():
    W = 500 + gw('round')
    g = _g('5', W, SBF - 24, SBF)              # straight stem at x0: ink-left = SBF
    # R15h (28/10 18:30 'nâng vòng bụng số 5 một chút'): bowl top 0.645 cap (was 0.614; Inter / Liberation / DejaVu
    # 0.634-0.665) -- a shorter neck, the bowl carries more of the figure
    yt = round(float(_os.environ.get('FIVE_YT', 0.645)) * CAP)   # bowl top
    x0 = 24
    gap = 70
    r5 = min(W - V - x0 - V, yt - H - (-OV_C + H)) / 2
    # R5 (26/10 "đuôi số 5 ngắn"): the free end is the house tail, not a cut on the counter wall
    # v0.963 (27/10 16:07 'đuôi số 5 dời qua trái', 16:20 'medium, bold không bị kéo dài đuôi'): the bowl reaches
    # left of the stem by 0.5 of the REGULAR figure stem, the same distance in every weight
    v_reg = __import__('concept_v1').W8['regular']['V'] * FIG_K
    xb = x0 - float(_os.environ.get('FIVE_DX', 0.5)) * v_reg
    cxb = (xb + W) / 2
    h_reg = __import__('concept_v1').W8['regular']['H'] * FIG_K
    # 28/10 18:14 ('đuôi số 5 medium và bold hơi dư ra ngoài — chỉnh lại cho bằng với thân'): the tail's vertical cut
    # stands FLUSH with the stem's left edge (x0) in every weight (it reached 8 / 14 / 20 past it in R / M / B)
    kw5 = dict(reach=cxb - x0) if _os.environ.get('FIVE_FLUSH', '1') == '1' else {}
    tl = GL.tail(cxb, -OV_C + H, xb + V, V, 'l', 'down', tip_limit=yt - H - 0.3 * h_reg,
                 cry=(yt - H - (-OV_C + H)) / 2, ring=((-OV_C + yt) / 2, (W - xb) / 2, (yt + OV_C) / 2), **kw5)
    # v0.963 (27/10 16:19 'làm nét bụng mềm mại lại'; R3b: a ring wider than tall is an OVAL): the bowl is a true
    # ellipse ring (no flat bottom run); only its top-left quarter runs flat into the stem (square joint, R9)
    cyb = (-OV_C + yt) / 2
    bowl = [('add', _oval(xb, -OV_C, W, yt)), ('add', rect(x0, cyb, cxb + 1, yt)),
            ('sub', _oval(xb + V, -OV_C + H, W - V, yt - H)), ('sub', rect(x0 + V, cyb, cxb + 1, yt - H))]
    bowl += __import__('concept_v1').arm_ink(tl)
    g.group(bowl +
            __import__('concept_v1').band(tl['disk'], y1=yt - H) +       # the tail's compass stays inside the counter
            [('sub', rect(xb - 1, -OV_C - 1, tl['xt'], min(tl['cy'], yt - H))),
             ('sub', rect(xb - 1, tl['tip'], cxb, yt - H))] +
            ([('sub', rect(xb - 2, yt - H - 1, x0, yt + 2))] if xb < x0 else []))   # nothing of the bowl's top runs left of the stem
    g.add(rect(x0, yt - H, x0 + V, CAP - H + 2))
    # R15f (28/10 18:23 'đầu số 5 thụt vào 1 chút'; 18:33 'thụt sâu hơn'): the head's flared cut stands 0.5 of the REGULAR figure stem
    # inside the bowl's outer edge, the same distance in every weight (it was 14)
    g.add(fbar(x0, CAP - H, W - float(_os.environ.get('FIVE_HEAD', 0.5)) * v_reg, CAP, left=False, right=True))
    if xb < x0 and not kw5:
        g.lsb = SBF - xb                         # the bowl's left (the tail) now starts the ink: ink-left = SBF
    return _reg(g)


def _oval(x0, y0, x1, y1, k=0.56):
    """true ellipse in the box (elliptical quarter arcs, no flat runs)."""
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    return [('M', cx, y1),
            ('C', cx + k * rx, y1, x1, cy + k * ry, x1, cy),
            ('C', x1, cy - k * ry, cx + k * rx, y0, cx, y0),
            ('C', cx - k * rx, y0, x0, cy - k * ry, x0, cy),
            ('C', x0, cy + k * ry, cx - k * rx, y1, cx, y1), ('Z',)]


SIX_CUT = CAP - 236  # upper terminal ends at the same height as C's terminals


def _six_ops(W):
    # 26/10 review: the lower counter was a stadium with a kink where the big ring's inner
    # curve crossed it -> now the lower bowl is a pair of true ellipses, and the stem of the
    # big ring only exists above the bowl's equator (where both have vertical tangents), so
    # the counter is one smooth oval. The upper terminal is cut at C's height (SIX_CUT) so its flat
    # cut meets the counter curve at a steep angle, like C, instead of a shallow lip.
    yt = float(_os.environ.get('SIX_YT', 430))   # v0.963 (27/10 16:22-16:26 'nâng chiều cao bụng số 6 và 9'): bowl top 440, on the 5's bowl line (was 414)
    y0, y1 = -OV_C, yt + 10
    ymid = (y0 + y1) / 2
    cnt = _oval(V, y0 + H, W - V, y1 - H)
    h_reg = __import__('concept_v1').W8['regular']['H'] * FIG_K   # R2b: the tail's clearance in REGULAR units
    tu = GL.tail(W / 2, CAP + OV_C - H, W - V, V, 'r', 'up', tip_limit=y1 + 0.3 * h_reg, ring=(CAP + OV_C - W / 2, W / 2, W / 2))
    big = ring(0, -OV_C, W, CAP + OV_C, V, H, (FULL, FULL, 0, 0), (FULL, FULL, 0, 0)) + __import__('concept_v1').arm_ink(tu) + \
        [('sub', rect(-1, -OV_C - 1, W + 1, ymid)),          # stem straight down to the equator
         ('sub', cnt),
         ('sub', tu['disk']),                                  # R5 tail (26/10 "đuôi 6 9 ngắn")
         ('sub', rect(tu['xt'], tu['cy'], W + 1, CAP + OV_C + 1)),
         ('sub', rect(W / 2, ymid, W + 1, tu['tip']))]
    low = [('add', _oval(0, y0, W, y1)), ('sub', cnt)]
    return [('group', big), ('group', low)]


FIG69 = _os.environ.get('FIG69', 'diag')
NINE_H = 0.67        # R15c: the bowl's outer height / cap height (designer's 1960s sample '196', 28/10 17:29)
NINE_ANG = 23.0      # R15c: the diagonal's angle off vertical (sample ~23-24°)


def _nine_geom():
    """R15c (28/10 17:29 'update lại các số này' + 'vẽ lại cho smooth và đồng bộ độ dày glyph, đúng chuẩn guide'):
    9 = an elliptic ring + ONE straight diagonal.
      * counter = a CIRCLE; outer = counter + the figure strokes (V sides, H top / bottom) -> outer height NINE_H x cap,
        top on the cap line + overshoot (same guides as 0 3 8)
      * the diagonal's outer edge is the TANGENT to the ring's outer curve at NINE_ANG off vertical (G1, no kink); its
        inner edge is parallel, perpendicular thickness = the diagonal rule 0.9 V (R2); the foot is cut level on the
        baseline; the inner edge meets the ring in a crisp crotch (R9)
      * 6 = 9 turned 180° about the figure's centre (top cut on the cap line)"""
    hb = NINE_H * CAP
    c = hb - 2 * H                                  # the counter circle's diameter
    wb = c + 2 * V
    top = CAP + OV_C
    a, b = wb / 2, hb / 2
    cx, cy = wb / 2, top - b
    th = _m.radians(NINE_ANG)
    t = -_m.atan(b / a * _m.tan(th))                 # tangent point on the outer ellipse (right, below the centre)
    px, py = cx + a * _m.cos(t), cy + b * _m.sin(t)
    xr = px - py * _m.tan(th)                       # outer edge on the baseline
    wd = 0.9 * V / _m.cos(th)                      # horizontal width of the diagonal
    return dict(wb=wb, hb=hb, top=top, cx=cx, cy=cy, a=a, b=b, px=px, py=py, xr=xr, wd=wd, th=th)


NINE_CURVE = _os.environ.get('NINE_CURVE', '0') == '1'   # 28/10 18:13 'thôi bỏ cong số 6, 9, và 7': straight R15c kept
NINE_A0, NINE_A1 = 8.0, 33.0     # R15c2: the diagonal leaves the ring 8° off vertical and lands 33° off vertical


def _nine_ops():
    if NINE_CURVE:
        return _nine_ops_curved()
    q = _nine_geom()
    wb, top, hb = q['wb'], q['top'], q['hb']
    px, py, xr, wd = q['px'], q['py'], q['xr'], q['wd']
    diag = poly([(xr - wd, 0), (xr, 0), (px, py), (px - wd, py)])
    return [('group', [('add', _oval(0, top - hb, wb, top)), ('add', diag),
                       ('sub', _oval(V, top - hb + H, wb - V, top - H))])]


def _nine_ops_curved():
    """R15c2 (28/10 18:10 designer's '96' sample: 'số 6 và 9 hơi cong 1 tí'): the 9's stroke is no longer straight but
    a gentle continuation of the ring: its outer edge leaves the ring's outer curve TANGENTIALLY where the ring runs
    NINE_A0 off vertical (G1, no kink) and bends steadily (one cubic, curvature only falling) until it lands
    NINE_A1 off vertical on the same baseline foot as R15c (sample: 7° at the ring -> 34° at the foot). The inner edge
    is the outer edge offset by the diagonal thickness 0.9 V (ends offset along their normals, same end tangents);
    the foot is cut level on the baseline; the inner edge meets the ring in a crisp crotch."""
    q = _nine_geom()
    wb, top, hb, a, b, cx, cy = q['wb'], q['top'], q['hb'], q['a'], q['b'], q['cx'], q['cy']
    th0, th1 = _m.radians(NINE_A0), _m.radians(NINE_A1)
    t0 = -_m.atan(b / a * _m.tan(th0))
    P0 = (cx + a * _m.cos(t0), cy + b * _m.sin(t0))
    F = (q['xr'], 0.0)                                            # the R15c foot (outer edge on the baseline)
    d0 = (-_m.sin(th0), -_m.cos(th0)); d1 = (-_m.sin(th1), -_m.cos(th1))
    ch = _m.hypot(F[0] - P0[0], F[1] - P0[1]) / 3
    P1 = (P0[0] + ch * d0[0], P0[1] + ch * d0[1]); P2 = (F[0] - ch * d1[0], F[1] - ch * d1[1])
    T = 0.9 * V
    n0 = (-_m.cos(th0), _m.sin(th0)); n1 = (-_m.cos(th1), _m.sin(th1))
    Q0 = (P0[0] + T * n0[0], P0[1] + T * n0[1])
    Q3 = (F[0] + T * n1[0], F[1] + T * n1[1])
    sft = Q3[1] / _m.cos(th1)                                     # slide along the end tangent onto the baseline
    Q3 = (Q3[0] + sft * d1[0], Q3[1] + sft * d1[1])
    chq = _m.hypot(Q3[0] - Q0[0], Q3[1] - Q0[1]) / 3
    Q1 = (Q0[0] + chq * d0[0], Q0[1] + chq * d0[1]); Q2 = (Q3[0] - chq * d1[0], Q3[1] - chq * d1[1])
    stroke = [('M',) + P0, ('C',) + P1 + P2 + F, ('L',) + Q3, ('C',) + Q2 + Q1 + Q0, ('Z',)]
    return [('group', [('add', _oval(0, top - hb, wb, top)), ('add', stroke),
                       ('sub', _oval(V, top - hb + H, wb - V, top - H))])]


@figweight
def fig6():
    if FIG69 == 'diag':
        q = _nine_geom()
        W = q['wb']
        g = _g('6', W, SBF, SBF)
        g.ops += rot180_ops(_nine_ops(), W / 2, CAP / 2)
        return _reg(g)
    W = 510 + gw('round')
    g = _g('6', W, SBF, SBF - 12)
    g.ops += _six_ops(W)
    return _reg(g)


@figweight
def fig9():
    if FIG69 == 'diag':
        q = _nine_geom()
        W = q['wb']
        g = _g('9', W, SBF, SBF)
        g.ops += _nine_ops()
        return _reg(g)
    W = 510 + gw('round')
    g = _g('9', W, SBF - 12, SBF)
    g.ops += rot180_ops(_six_ops(W), W / 2, CAP / 2)
    return _reg(g)


@figweight
def fig7():
    W = 480 + gw('one')
    g = _g('7', W, SBF - 6, SBF - 10)
    g.add(fbar(0, CAP - H, W, CAP, left=True, right=False))
    dw = DIAG
    for _ in range(20):                     # centre-line run depends on dw itself
        dw = diag_dx(DIAG, W - 110 - dw, CAP - H)
    if _os.environ.get('SEVEN_CURVE', '0') == '1':      # 28/10 18:13: dropped, the 7 stays straight
        # R15f (28/10 18:11 'thử luôn cho số 7 cũng cong nhẹ như vậy'): the 7's stroke bends like the 6's (R15c2 turned
        # 180°): it leaves the bar NINE_A1 off vertical and lands NINE_A0 off vertical, one cubic per edge, thickness
        # DIAG measured square; the bar end (outer edge at W) and the foot (inner edge at 110) stay where they were.
        th0, th1 = _m.radians(NINE_A1), _m.radians(NINE_A0)
        yt = CAP - H + 1
        d0 = (-_m.sin(th0), -_m.cos(th0)); d1 = (-_m.sin(th1), -_m.cos(th1))
        n0 = (-_m.cos(th0), _m.sin(th0)); n1 = (-_m.cos(th1), _m.sin(th1))
        T = DIAG
        Fl = (110.0, 0.0)                                              # inner foot (left edge on the baseline)
        Fr = (110.0 + T / _m.cos(th1), 0.0)                            # outer foot
        P0 = (W, yt)
        ch = _m.hypot(Fr[0] - P0[0], Fr[1] - P0[1]) / 3
        P1 = (P0[0] + ch * d0[0], P0[1] + ch * d0[1]); P2 = (Fr[0] - ch * d1[0], Fr[1] - ch * d1[1])
        Q0 = (W - T / _m.cos(th0), yt)                                 # inner edge on the bar's underside
        chq = _m.hypot(Fl[0] - Q0[0], Fl[1] - Q0[1]) / 3
        Q1 = (Q0[0] + chq * d0[0], Q0[1] + chq * d0[1]); Q2 = (Fl[0] - chq * d1[0], Fl[1] - chq * d1[1])
        g.add([('M',) + P0, ('C',) + P1 + P2 + Fr, ('L',) + Fl, ('C',) + Q2 + Q1 + Q0, ('Z',)])
        return _reg(g)
    g.add(poly([(W - dw, CAP - H + 1), (W, CAP - H + 1), (110 + dw, 0), (110, 0)]))
    return _reg(g)


@figweight
def fig8():
    W = 500 + gw('round')
    g = _g('8', W, SBF, SBF)
    ym = 316
    # 26/10 sync: both bowls are true ellipses (outer + counter), same family as the 6/9 bowl
    g.group([('add', _oval(34, ym, W - 34, CAP + OV_C)),
             ('sub', _oval(34 + V * 0.92, ym + H * 0.92, W - 34 - V * 0.92, CAP + OV_C - H * 0.92))])   # audit: 8 was the darkest figure
    # lower bowl's top stops at the upper counter's bottom (it used to poke 0.08H into it ->
    # 26/10 "khoét trong số 8 ở trên bị móp ở dưới")
    yl = ym + H * 0.92
    g.group([('add', _oval(0, -OV_C, W, yl)), ('sub', _oval(V, -OV_C + H, W - V, yl - H))])
    return _reg(g)


# ============================ PUNCTUATION ============================
def _comma_ops(x=0, y=0):
    """round dot + a flat-cut tail leaning down-left (the sắc slab, reversed)."""
    return [('add', dot(x + R, y + R)),
            ('add', poly([(x + R - 8, y + R), (x + D, y + R), (x + 18 + 38 * K_, y - 170), (x + 18 - 38 * K_, y - 170)]))]


def p_period():
    g = _g('.', D, 48, 48); g.add(dot(R, R)); return _reg(g)


def p_comma():
    g = _g(',', D, 56, 40); g.ops += _comma_ops(); return _reg(g)


def p_colon():
    g = _g(':', D, 48, 48); g.add(dot(R, R), dot(R, XH - R)); return _reg(g)


def p_semicolon():
    g = _g(';', D, 56, 40); g.ops += _comma_ops(); g.add(dot(R, XH - R)); return _reg(g)


def p_ellipsis():
    gap = 70
    g = _g('…', 3 * D + 2 * gap, 48, 48)
    for i in range(3):
        g.add(dot(R + i * (D + gap), R))
    return _reg(g)


def p_middot():
    g = _g('·', D, 48, 48); g.add(dot(R, 330)); return _reg(g)


def p_exclam():
    g = _g('!', D, 54, 54)
    g.add(slab(14, D - 14, 250, 0, D, CAP))       # wedge: full stem at the top, lighter at foot
    g.add(dot(R, R))
    return _reg(g)


def p_question():
    W = 420
    g = _g('?', W, 30, 34)
    rx, ry, cy = W / 2 - V / 2, 150, CAP - 150 - H / 2 + 6
    # same construction as the hook mark / the bowls: outer oval minus counter oval, 3/4 kept
    g.group([('add', _oval(W / 2 - rx - V / 2, cy - ry - H / 2, W / 2 + rx + V / 2, cy + ry + H / 2)),
             ('sub', _oval(W / 2 - rx + V / 2, cy - ry + H / 2, W / 2 + rx - V / 2, cy + ry - H / 2)),
             ('sub', rect(-50, cy - ry - H, W / 2, cy)),
             ('sub', rect(-50, cy - 1, GL.hook_cut(W / 2, rx - V / 2, 'l', GL.HOOK_PHI), CAP + 100)),   # house hook cut
             *[b for b in [GL.blunt_tip(W / 2, cy, ry - H / 2, GL.hook_cut(W / 2, rx - V / 2, 'l', GL.HOOK_PHI), 'l', 'up', V, rx - V / 2)] if b]])
    g.add(rect(W / 2 - 74 * K_, 250, W / 2 + 74 * K_, cy - ry + H / 2))
    g.add(dot(W / 2, R))
    return _reg(g)


def p_quotesingle():
    g = _g("'", 130, 50, 50); g.add(slab(65 - 43 * K_, 65 + 43 * K_, CAP - 250, 65 - 65 * K_, 65 + 65 * K_, CAP)); return _reg(g)


def p_quotedbl():
    g = _g('"', 130 * 2 + 70, 50, 50)
    g.add(slab(65 - 43 * K_, 65 + 43 * K_, CAP - 250, 65 - 65 * K_, 65 + 65 * K_, CAP), slab(265 - 43 * K_, 265 + 43 * K_, CAP - 250, 265 - 65 * K_, 265 + 65 * K_, CAP))
    return _reg(g)


def _q9(x):       # ’ shape at cap height (comma raised)
    return shift_ops(_comma_ops(x, 0), 0, CAP - D)


def p_quoteright():
    g = _g('’', D, 56, 40); g.ops += _q9(0); return _reg(g)


def p_quoteleft():
    g = _g('‘', D, 40, 56); g.ops += rot180_ops(_q9(0), R, CAP - R); return _reg(g)


def p_quotedblright():
    g = _g('”', 2 * D + 50, 56, 40); g.ops += _q9(0) + _q9(D + 50); return _reg(g)


def p_quotedblleft():
    g = _g('“', 2 * D + 50, 40, 56)
    g.ops += rot180_ops(_q9(0) + _q9(D + 50), (2 * D + 50) / 2, CAP - R)
    return _reg(g)


def _paren_ops(W):
    top, bot = CAP + 90, -140
    rx, ry = W - V / 2, (top - bot) / 2 + 40
    cx, cy = W, (top + bot) / 2
    arc = [(cx + rx * _m.cos(a), cy + ry * _m.sin(a)) for a in [_m.pi * (0.62 + 0.76 * i / 120) for i in range(121)]]
    return [('group', [('add', band(arc, V * 0.92, H * 0.92)),
                       ('sub', rect(-200, top, W + 200, top + 300)),
                       ('sub', rect(-200, bot - 300, W + 200, bot))])]


def p_parenleft():
    W = 230
    g = _g('(', W, 44, 14); g.ops += _paren_ops(W); return _reg(g)


def p_parenright():
    W = 230
    g = _g(')', W, 14, 44); g.ops += rot180_ops(_paren_ops(W), W / 2, (CAP - 50) / 2); return _reg(g)


def p_bracketleft():
    W = 240 + gw('one')                             # R2c
    g = _g('[', W, 50, 20)
    g.add(rect(0, -140, V, CAP + 90), rect(0, CAP + 90 - HM, W, CAP + 90), rect(0, -140, W, -140 + HM))
    return _reg(g)


def p_bracketright():
    W = 240 + gw('one')                             # R2c
    g = _g(']', W, 20, 50)
    g.add(rect(W - V, -140, W, CAP + 90), rect(0, CAP + 90 - HM, W, CAP + 90), rect(0, -140, W, -140 + HM))
    return _reg(g)


def _brace_ops(W):
    """{ built like the parentheses / brackets: one even stroke with round corners (compass
    corners = the same outer/counter rounded-rect construction as the bowls), flat cuts at
    the ends, a short flat nib at the middle. 26/10 sync: true curves (old polygon band left
    steps)."""
    top, bot = CAP + 90, -140
    mid = (top + bot) / 2
    wv, wh = V * 0.88, H * 0.86
    sx = W * 0.56
    r1 = max(96, wv / 2 + 30)            # centre-line radius of the end corner
    r2 = max(84, wv / 2 + 24)            # ... of the nib corner

    def rr(x0, y0, x1, y1, rad, sign):
        tl, tr, br, bl = rad
        if sign > 0:
            return rrect(x0, y0, x1, y1, (tl, tr, br, bl))
        return rrect(x0, 2 * mid - y1, x1, 2 * mid - y0, (bl, br, tr, tl))

    ops = []
    for sign in (1, -1):
        yo = top if sign > 0 else top          # mirrored by rr()
        # end corner: bar along the top turning down into the spine (top-left corner)
        ops.append(('group', [('add', rr(sx - wv / 2, mid, W, yo, (r1 + wv / 2, 0, 0, 0), sign)),
                              ('sub', rr(sx + wv / 2, mid - 1, W + 1, yo - wh, (max(r1 - wv / 2, 12), 0, 0, 0), sign))]))
        # nib corner: spine turning left into the nib (bottom-right corner of this half)
        ops.append(('group', [('add', rr(-1, mid - wh / 2, sx + wv / 2, mid + r2 + 120, (0, 0, r2 + wv / 2, 0), sign)),
                              ('sub', rr(-2, mid + wh / 2, sx - wv / 2, mid + r2 + 121, (0, 0, max(r2 - wv / 2, 12), 0), sign))]))
    return [('group', ops + [('sub', rect(-300, -600, 0, 1400)), ('sub', rect(W, -600, W + 300, 1400))])]


def p_braceleft():
    W = 300
    g = _g('{', W, 34, 24); g.ops += _brace_ops(W); return _reg(g)


def p_braceright():
    W = 300
    g = _g('}', W, 24, 34); g.ops += rot180_ops(_brace_ops(W), W / 2, (CAP + 90 - 140) / 2); return _reg(g)


def p_slash():
    W = 380 + gw('diag')                            # R2c
    g = _g('/', W, 10, 10)
    dw = diag_dx(DIAG, W, CAP + 230) * 0.98
    g.add(poly([(0, -140), (dw, -140), (W, CAP + 90), (W - dw, CAP + 90)]))
    return _reg(g)


def p_backslash():
    W = 380 + gw('diag')                            # R2c
    g = _g('\\', W, 10, 10)
    dw = diag_dx(DIAG, W, CAP + 230) * 0.98
    g.add(poly([(W - dw, -140), (W, -140), (dw, CAP + 90), (0, CAP + 90)]))
    return _reg(g)


def p_bar():
    g = _g('|', V - 30, 60, 60); g.add(rect(0, -200, V - 30, CAP + 120)); return _reg(g)


def _hbar(ch, W, y=262, t=None, sb=40):
    t = t or 132 * K_
    y = y + (132 - t) / 2
    g = _g(ch, W, sb, sb); g.add(fbar(0, y, W, y + t, left=True, right=True)); return _reg(g)


def p_endash():
    return _hbar('–', 500)


def p_emdash():
    return _hbar('—', 920, sb=20)


def p_underscore():
    g = _g('_', 520, 10, 10); g.add(rect(0, -150, 520, -150 + HM)); return _reg(g)


MATH_Y = 330          # optical centre for math signs (between x-height middle and cap middle)
MT_ = 124 * K_        # math stroke


def p_plus():
    W = 480
    g = _g('+', W, 40, 40)
    g.add(rect(0, MATH_Y - MT_ / 2, W, MATH_Y + MT_ / 2), rect(W / 2 - MT_ / 2, MATH_Y - W / 2, W / 2 + MT_ / 2, MATH_Y + W / 2))
    return _reg(g)


def p_minus():
    W = 480
    g = _g('−', W, 40, 40); g.add(rect(0, MATH_Y - MT_ / 2, W, MATH_Y + MT_ / 2)); return _reg(g)


def p_equal():
    W = 480
    g = _g('=', W, 40, 40)
    g.add(rect(0, MATH_Y + 40, W, MATH_Y + 40 + MT_ - 10), rect(0, MATH_Y - 40 - MT_ + 10, W, MATH_Y - 40))
    return _reg(g)


def p_multiply():
    W = 400
    g = _g('×', W, 50, 50)
    L = W * 0.70
    arm = [('add', rect(W / 2 - L, MATH_Y - MT_ / 2 + 6, W / 2 + L, MATH_Y + MT_ / 2 - 6))]
    g.ops += rot_ops(arm, _m.pi / 4, W / 2, MATH_Y) + rot_ops(arm, -_m.pi / 4, W / 2, MATH_Y)
    return _reg(g)


def p_divide():
    W = 480
    g = _g('÷', W, 40, 40)
    g.add(rect(0, MATH_Y - MT_ / 2, W, MATH_Y + MT_ / 2))
    g.add(dot(W / 2, MATH_Y + 160, 62 * (0.3 + 0.7 * K_)), dot(W / 2, MATH_Y - 160, 62 * (0.3 + 0.7 * K_)))
    return _reg(g)


def _chev(W, H_, t):
    """chevron pointing left, flat cuts (like the < of the circumflex)."""
    return [('add', poly([(W, MATH_Y + H_ / 2), (W, MATH_Y + H_ / 2 - t * 1.25), (t * 1.35, MATH_Y), (W, MATH_Y - H_ / 2 + t * 1.25),
                          (W, MATH_Y - H_ / 2), (0, MATH_Y + 0), ]))] if False else \
        [('add', poly([(0, MATH_Y + t * 0.62), (W, MATH_Y + H_ / 2), (W, MATH_Y + H_ / 2 - t * 1.3), (t * 1.6, MATH_Y),
                       (W, MATH_Y - H_ / 2 + t * 1.3), (W, MATH_Y - H_ / 2), (0, MATH_Y - t * 0.62)]))]


def p_less():
    W = 420
    g = _g('<', W, 46, 46); g.ops += _chev(W, 480, 118 * K_); return _reg(g)


def p_greater():
    W = 420
    g = _g('>', W, 46, 46); g.ops += rot180_ops(_chev(W, 480, 118 * K_), W / 2, MATH_Y); return _reg(g)


def p_guillemotleft():
    e = gw('diag')                                  # R2c
    W = 440 + 1.5 * e                               # the white between the two chevrons grows with them
    g = _g('«', W, 30, 30)
    one = [(op, transform(c, lambda x, y: (x * 0.5, MATH_Y + (y - MATH_Y) * 0.62))) for op, c in _chev(420 + e, 480, 118 * K_)]
    g.ops += one + shift_ops(one, 220 + e, 0)
    return _reg(g)


def p_guillemotright():
    e = gw('diag')                                  # R2c
    W = 440 + 1.5 * e
    g = _g('»', W, 30, 30)
    one = [(op, transform(c, lambda x, y: (x * 0.5, MATH_Y + (y - MATH_Y) * 0.62))) for op, c in _chev(420 + e, 480, 118 * K_)]
    g.ops += rot180_ops(one + shift_ops(one, 220 + e, 0), W / 2, MATH_Y)
    return _reg(g)


def p_percent():
    W = 700 + gw('multi')                           # R2c
    g = _g('%', W, 26, 26)
    rw, rh = 250 + 0.8 * gw('round'), 330
    g.group(ring(0, CAP - rh, rw, CAP, 92 * K_, 84 * K_, FULL, FULL))
    g.group(ring(W - rw, 0, W, rh, 92 * K_, 84 * K_, FULL, FULL))
    dw = diag_dx(DIAG * 0.8, W - 200, CAP)
    g.add(poly([(100, 0), (100 + dw, 0), (W - 100, CAP), (W - 100 - dw, CAP)]))
    return _reg(g)


def p_numbersign():
    W = 560 + gw('straight')                        # R2c
    g = _g('#', W, 24, 24)
    s, b = 112 * K_, 104 * K_
    for x in (120, W - 120 - s):
        g.add(rect(x, 0, x + s, CAP))
    for y in (180, CAP - 180 - b):
        g.add(rect(0, y, W, y + b))
    return _reg(g)


def p_asterisk():
    W = 400
    g = _g('*', W, 30, 30)
    cx, cy, L, t = W / 2, CAP - 170, 170, 92 * K_
    arm = [('add', poly([(cx - t / 2, cy), (cx + t / 2, cy), (cx + t * 0.62, cy + L), (cx - t * 0.62, cy + L)]))]
    for k in range(6):
        g.ops += rot_ops(arm, k * _m.pi / 3, cx, cy)
    return _reg(g)


def p_degree():
    W = 250
    g = _g('°', W, 40, 40); g.group(ring(0, CAP - 260, W, CAP, 80 * K_, 70 * K_, FULL, FULL)); return _reg(g)


def p_dollar():
    base = G['S']
    g = _g('$', base.body, base.lsb, base.rsb)
    g.ops = list(base.ops)
    cx = base.body / 2
    g.add(rect(cx - 48, CAP + OV_C - 10, cx + 48, CAP + 120), rect(cx - 48, -120, cx + 48, -OV_C + 10))
    return _reg(g)


def p_dong():
    from lcsym import lcg
    base = lcg('đ')                             # R0b: the current đ
    g = _g('₫', base.body, base.lsb, base.rsb)
    g.ops = list(base.ops)
    g.add(fbar(60, -200, base.body - 10, -200 + 110, left=True, right=True))
    return _reg(g)


def p_ampersand():
    """& : small upper loop + lower bowl open to the right + diagonal leg + flared arm —
    built from the same ring / slab / bar parts as the letters."""
    W = 620 + gw('bowl')                            # R2c
    g = _g('&', W, 26, 6)
    g.group(ring(50, 392, 400, CAP + OV_C, 128 * K_, 112 * K_, FULL, FULL))
    dw = diag_dx(DIAG, W - 160, 452)
    # the lower bowl is cut exactly along the leg's LEFT edge (so it runs into the leg with no
    # ledge in any weight; the old level cut at H+30 left a step in Regular)
    # v0.94 QA: the cut runs 3u INSIDE the leg (coincident edges broke the boolean union and
    # filled half of the lower counter)
    xe = lambda y: 96 + (452 - y) / 452 * (W - dw - 96) + 3
    g.group(ring(0, -OV_C, 480, 452, V, H, FULL, FULL) +
            [('sub', poly([(xe(470), 470), (W + 50, 470), (W + 50, -60), (xe(-60), -60)]))])
    g.add(poly([(96, 452), (96 + dw, 452), (W, 0), (W - dw, 0)]))
    g.add(fbar(360, 236, W, 236 + HM, left=False, right=True))
    return _reg(g)


def p_at():
    """@ in one continuous stroke: the inner a's stem runs out along a foot into the right side
    of the outer ring, which then goes round (top, left, bottom) and ends with a flat cut."""
    W = 800 + gw('multi')                           # R2c
    g = _g('@', W, 30, 30)
    top, bot = CAP + 40, -170
    from lcsym import lcg
    a = lcg('a@0.72')                           # R0b: the current a (small a: aperture kept, lcsym)
    s = 0.72
    ox, oy = W / 2 - a.body * 0.72 / 2 - 8, 96
    tf = lambda x, y: (ox + x * s, oy + y * s)
    ainner = [(op, transform(c, tf)) if op != 'group' else (op, [(o2, transform(c2, tf)) for o2, c2 in c])
              for op, c in a.ops]
    yj = oy                                     # the foot sits on the a's baseline
    foot_t = 104 * K_
    g.group(ring(0, bot, W, top, 132 * K_, 118 * K_, FULL, FULL) +
            [('sub', rect(W * 0.52, bot - 1, W + 1, yj))])             # open the lower right
    g.group(ainner)
    sx0 = ox + (a.body - round(0.93 * V)) * s   # a's stem, left edge (F2: v = 0.93 V)
    # foot: stem -> ring. It leaves the stem's RIGHT edge (QA 13:20: started at the left edge it closed the a's
    # bowl/stem notch into a pin-hole); it starts at the stem's middle so it swallows the stem's foot flare
    g.add(rect(sx0 + round(0.93 * V) * s / 2, yj, W, yj + foot_t))
    return _reg(g)


FIG_FUNCS = [fig0, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9,
             p_period, p_comma, p_colon, p_semicolon, p_ellipsis, p_middot, p_exclam, p_question,
             p_quotesingle, p_quotedbl, p_quoteleft, p_quoteright, p_quotedblleft, p_quotedblright,
             p_parenleft, p_parenright, p_bracketleft, p_bracketright, p_braceleft, p_braceright, p_slash, p_backslash, p_bar,
             p_endash, p_emdash, p_underscore, p_plus, p_minus, p_equal, p_multiply, p_divide,
             p_less, p_greater, p_guillemotleft, p_guillemotright, p_percent, p_numbersign,
             p_asterisk, p_degree, p_dollar, p_dong, p_ampersand, p_at]


def build_figs():
    for f in FIG_FUNCS:
        f()
    return G
