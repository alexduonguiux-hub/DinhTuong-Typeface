"""A2 mark kit v2 — 'nét chữ' : every mark is cut from the same parts as the letters.
 - acute/grave : a diagonal slab like the legs of A/V/K, both ends cut flat (horizontal),
                 pressed slightly wider at the top = the same brush swell as a stem's free end
 - circumflex  : a mini A without crossbar — flat-topped apex + V-notch (same as A/V/M)
 - breve       : a mini u-bowl — round bottom, both arms cut flat at the top
 - hook        : a '?' built from the o-ring + a stem stub, terminals cut flat
 - tilde       : an n-shoulder joined to a u-cup, ends cut flat
 - dots        : round tittle (compass circle) for i, j and dot below
 - horn        : a stem stub that rises from the bowl and ends flat with the brush flare
"""
import math as _m
import glyphs_c as GL
from glyphs_c import *

_k = GL.WK     # stroke scale vs Bold (1.0 bold, 0.69 regular)
MW = round(128 * _k)      # mark stroke (vertical-ish parts)
MWH = round(108 * _k)     # mark stroke (horizontal parts) — thinner, same contrast as v/h
DOT_D = round(164 * (0.15 + 0.85 * _k))  # round tittle (i, j, dot below)
# R8b (26/10 'độ dày các dấu không đều'): ONE mark stroke, measured square to the stroke:
# vertical-ish parts MV = 0.64 v (= the horn plate), horizontal parts MH = 0.83 MV (letters' contrast)
MV = 0.64 * GL.v
MH = 0.83 * MV
DOT = DOT_D


def tittle(cx, cy, d=DOT_D):
    """dots stay round (review 26/10): a compass circle, same as the bowls' curvature."""
    return circle(cx, cy, d / 2)


STRIP_L = 300        # R8d v0.95b (ref. 27/10 00:17, measured): sắc, huyền, nặng = ONE steel strip 300 long
STRIP_T = 0.42       # thickness (V units), the same standing or lying — v0.95 review "giảm độ dày của các dấu": 0.54 -> 0.42
STRIP_STACK = 165    # strip length when it shares the letter with a mũ / trăng (huyền on a stack keeps 300; see compose)
ACUTE_K = 0.72       # R8e (28/10 11:00 'có thể giảm độ dài dấu sắc 1 chút'): 0.8 -> 0.72 (240 -> 216). R8d v0.96c (27/10 14:36 'giảm độ dài dấu sắc 20% từ trên xuống, đồng bộ chiều cao các chỗ'):
ACUTE_L = round(ACUTE_K * STRIP_L)   # 240: ONE sắc length everywhere (Á Ấ Ắ Ớ Ứ, á ấ ắ …); its foot stays where it was
ACUTE_UP = 0         # sắc stands on the mark zone (cap + 50; sample 48)
GRAVE_UP = 12        # huyền floats 62 above the cap (sample 62)
DOTB_GAP = 62        # nặng hangs 62 under the baseline (sample 62)


def _st():
    return STRIP_T * GL.V


ACUTE_TILT = float(__import__('os').environ.get('ACUTE_TILT', '18'))   # R8e (28/10 10:5x, designer chose 18°: 'Sí' read as 'Sl' with a standing strip): degrees off vertical, top to the right


# R8i (31/10, designer's samples 'thử lại bộ dấu sắc mới' then 'update lại độ dài và vị trí', measured on Bold: Á Ấ Ắ
# Ú ấ): the sắc is the LYING strip of huyền sheared up to the right — both ends cut VERTICAL, vertical thickness T
# (sample 72 u; T Bold 70.6), long edges rising ACUTE_R8I_ANG (sample v2 27.1°, v1 22.2°), horizontal span
# ACUTE_R8I_SPAN (sample v2 194 = 0.65 x STRIP_L; v1 246), the same everywhere (caps / lowercase, lone / stacked).
# Trial switch: ACUTE_TOPLINE=4 (glyphs_c).
ACUTE_R8I_ANG = 27.0
ACUTE_R8I_SPAN = round(0.65 * STRIP_L)      # 195


def R8I():
    return __import__('os').environ.get('ACUTE_TOPLINE', '4') in ('4', '5')


def tv(ang):
    """R8l (31/10 'cân bằng độ dày các dấu với nhau'): a sheared strip is T thick SQUARE to its run, like the level
    huyền, trăng, ngã, hỏi, nặng (measured 1.002: sắc 0.89 T, mũ 0.92 T — vertical T made them read lighter), so its
    vertical-cut thickness is T / cos(angle)."""
    return _st() / _m.cos(_m.radians(ang))


def mk_acute(length=ACUTE_L, **_):
    if R8I():
        t, s = tv(ACUTE_R8I_ANG), ACUTE_R8I_SPAN
        rise = s * _m.tan(_m.radians(ACUTE_R8I_ANG))
        return [('add', poly([(-s / 2, ACUTE_UP), (s / 2, ACUTE_UP + rise), (s / 2, ACUTE_UP + rise + t), (-s / 2, ACUTE_UP + t)]))]
    return _mk_acute_r8e(length)


def _mk_acute_r8e(length=ACUTE_L, **_):
    """sắc: the strip STANDING, centred on the letter (built at final size: no cap scaling). With ACUTE_TILT the
    strip leans like the legs of A / V (thickness T square to the stroke, both ends cut level, same height), its
    middle still on the letter's axis."""
    t = _st()
    if not ACUTE_TILT:
        return [('add', rect(-t / 2, ACUTE_UP, t / 2, ACUTE_UP + length))]
    a = _m.radians(ACUTE_TILT)
    w, dx = t / _m.cos(a), length * _m.tan(a)
    y0, y1 = ACUTE_UP, ACUTE_UP + length
    return [('add', poly([(-dx / 2 - w / 2, y0), (-dx / 2 + w / 2, y0), (dx / 2 + w / 2, y1), (dx / 2 - w / 2, y1)]))]


def mk_grave(length=STRIP_L, **_):
    """huyền: the strip LYING, centred on the letter (built at final size: no cap scaling)."""
    t = _st()
    return [('add', rect(-length / 2, GRAVE_UP, length / 2, GRAVE_UP + t))]


def mk_circumflex_v94(hgt=140, half=150, top=None, notch=None, inner_top=None):
    """mũ (v0.94 QA "â ô ê bold fail"): a small Λ built like the letters' A/V — two diagonal bars
    of 0.84 MV (R7: two diagonals meeting) square to the bar, a FLAT apex of MH, and an open
    counter whose top is flat too (inner top width = 0.42 MH), so the counter stays open in every
    weight instead of closing into a solid triangle. Like the letters' A: outer apex flat, inner
    apex pointed (at MH under the top)."""
    t = 0.84 * MV
    wi = 0.0 if inner_top is None else inner_top     # inner apex POINTED, outer apex flat (like the letters' A)
    yi = hgt - MH                                  # inner flat top
    Tt = 0.0
    for _ in range(60):                            # outer top width so the inner top is wi wide
        dx = half - Tt / 2
        bw = t / _m.cos(_m.atan2(dx, hgt))         # horizontal width of a leg
        x_in = -half + bw + dx * yi / hgt          # inner left edge at the inner top
        Tt += (wi / 2 + x_in) * 0.8 * 2            # widen/narrow the outer top
        Tt = max(Tt, 0.0)
    dx = half - Tt / 2
    bw = t / _m.cos(_m.atan2(dx, hgt))
    return [('group', [('add', poly([(-half, 0), (half, 0), (Tt / 2, hgt), (-Tt / 2, hgt)])),
                       ('sub', poly([(-half + bw, -1), (half - bw, -1), (wi / 2, yi), (-wi / 2, yi)]))])]


def band(path, wv, wh=None, tangents=None):
    """stroke along a centre line with BUTT ends (cut square, never rounded) and the
    letters' contrast: full weight wv where the stroke runs vertical, wh where it runs
    horizontal (same v/h logic as the stems vs bars). tangents: exact directions per point
    (analytic curves) so the offset edges and the end cuts carry no facet errors."""
    wh = wv if wh is None else wh
    N = len(path); L, R = [], []
    for i in range(N):
        x, y = path[i]
        if tangents is not None:
            dx, dy = tangents[i]
        else:
            xa, ya = path[max(i - 1, 0)]; xb, yb = path[min(i + 1, N - 1)]
            dx, dy = xb - xa, yb - ya
        d = _m.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        r = (wh + (wv - wh) * abs(dy) / d) / 2
        L.append((x + nx * r, y + ny * r)); R.append((x - nx * r, y - ny * r))
    return poly([(round(px, 1), round(py, 1)) for px, py in L + R[::-1]])


def mk_breve_v94(hgt=120, half=146, w=None, wh=None):
    """mini u-bowl, built exactly like the letter u: rounded-rect bowl, arms cut flat on top."""
    w = MV if w is None else w
    wh = MH if wh is None else wh
    return [('group', [('add', rrect(-half, 0, half, hgt, (0, 0, FULL, FULL))),
                       ('sub', rrect(-half + w, wh, half - w, hgt + 1, (0, 0, FULL, FULL)))])]


def _oval(x0, y0, x1, y1, k=0.56):
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    return [('M', cx, y1),
            ('C', cx + k * rx, y1, x1, cy + k * ry, x1, cy),
            ('C', x1, cy - k * ry, cx + k * rx, y0, cx, y0),
            ('C', cx - k * rx, y0, x0, cy - k * ry, x0, cy),
            ('C', x0, cy + k * ry, cx - k * rx, y1, cx, y1), ('Z',)]


def mk_hook_v94(rx=76, ry=55, wv=None, wh=None, stem=None):   # ry 60->55: heavier R8b stroke, Ẳ stays under the family ascender
    """dấu hỏi = a 3/4 compass ring built exactly like the letters' bowls (outer oval minus
    counter oval: sides wv, top/bottom wh), free end cut level at the equator, foot cut
    flat at the stem line. 26/10 sync: true curves (the old polygon band left steps/kinks),
    foot flush with the curl's bottom in every weight."""
    wv = MV if wv is None else wv
    wh = MH if wh is None else wh
    stem = wh / 2 if stem is None else stem
    cy = stem + ry
    return [('group', [('add', _oval(-rx - wv / 2, cy - ry - wh / 2, rx + wv / 2, cy + ry + wh / 2)),
                       ('sub', _oval(-rx + wv / 2, cy - ry + wh / 2, rx - wv / 2, cy + ry - wh / 2)),
                       ('sub', rect(-rx - wv, cy - ry - wh, 0, cy)),          # open lower-left quarter
                       ('sub', rect(-rx - wv, cy - 1, GL.hook_cut(0, rx - wv / 2, 'l', GL.HOOK_PHI), cy + ry + wh)),   # house hook cut
                       *[b for b in [GL.blunt_tip(0, cy, ry - wh / 2, GL.hook_cut(0, rx - wv / 2, 'l', GL.HOOK_PHI), 'l', 'up', wv, rx - wv / 2)] if b]]),
            ('add', rect(-wv / 2, cy - ry - wh / 2, 0, cy - ry + wh / 2))]       # foot: flat cut at -wv/2


def mk_tilde_v94(hgt=122, half=156, w=None, wh=None):
    """one even stroke, round waves, both ends cut vertically like the c/e terminals."""
    w = MV if w is None else w
    wh = MH if wh is None else wh
    amp = (hgt - wh) / 2 - 4
    pts = [(-half - 40 + (2 * half + 80) * i / 40, 0) for i in range(41)]
    pts = [(x, hgt / 2 + amp * _m.sin((x + half) / (2 * half) * 2 * _m.pi)) for x, _ in pts]
    return [('group', [('add', band(pts, w, wh)),
                       ('sub', rect(-half - 200, -200, -half, hgt + 200)),
                       ('sub', rect(half, -200, half + 200, hgt + 200))])]


# ---- v0.95c (27/10 "dấu ô / ngã mỏng so với sắc huyền — nên cùng độ dày"): EVERY mark is cut from the
# same strip: ONE thickness T = STRIP_T * V, the same in every direction, built at its final size on the
# capitals (no cap scaling). Each mark grows just enough to keep its counter / wave open at that thickness.
# R8k (31/10, designer's sample 'Đổi dấu ô mới luôn', measured on Bold â Ấ): the mũ is two strips of the R8i sắc
# meeting in a POINTED apex (outer and inner) — each arm rises CIRC_R8K_ANG (sample 29.0-29.5°, height 144 = 120 tan 30°
# + 75), both outer ends cut VERTICAL, vertical thickness T (sample 75; T Bold 70.6), half-width CIRC_R8K_HALF (sample
# width 238-241). It sits CIRC_R8K_GAP above its letter's ink (sample Â 41, â 40): see glyphs_c.CIRC_FOOT.
CIRC_R8K_ANG = 30.0
CIRC_R8K_HALF = 120.0
CIRC_R8K_GAP = 40


def mk_circumflex(**_):
    T = _st()
    if R8I():
        T = tv(CIRC_R8K_ANG)                           # R8l
        h = CIRC_R8K_HALF; r = h * _m.tan(_m.radians(CIRC_R8K_ANG))
        return [('add', poly([(-h, 0), (-h, T), (0, r + T), (h, T), (h, 0), (0, r)]))]
    return mk_circumflex_v94_T(hgt=CIRC_HGT(), half=144, t=T, flat=T)


def CIRC_HGT():
    if R8I():
        return CIRC_R8K_HALF * _m.tan(_m.radians(CIRC_R8K_ANG)) + tv(CIRC_R8K_ANG)
    """mũ height — v0.95 review "giảm độ cao của dấu ô": max(118, 1.7T) -> max(96, 1.45T); the inner
    apex stays pointed and the counter open (Bold: 32u under the flat top)."""
    return max(96, 1.45 * _st())


def mk_circumflex_v94_T(hgt, half, t, flat, wi=0.0):
    yi = hgt - flat
    Tt = 0.0
    for _ in range(60):
        dx = half - Tt / 2
        bw = t / _m.cos(_m.atan2(dx, hgt))
        x_in = -half + bw + dx * yi / hgt
        Tt += (wi / 2 + x_in) * 0.8 * 2
        Tt = max(Tt, 0.0)
    dx = half - Tt / 2
    bw = t / _m.cos(_m.atan2(dx, hgt))
    return [('group', [('add', poly([(-half, 0), (half, 0), (Tt / 2, hgt), (-Tt / 2, hgt)])),
                       ('sub', poly([(-half + bw, -1), (half - bw, -1), (wi / 2, yi), (-wi / 2, yi)]))])]


def _offq(A, B, cy, r, sx):
    """one quarter of an edge of a strip bent on the half-ellipse centre line A x B (centre (0, cy)), from the bottom
    point (tangent level) to the side point (tangent vertical) on side sx (+1/-1). r(s) = signed half-thickness for a
    stroke whose direction has |sin| = s (s 0 = running level, 1 = running vertical; + = outer edge). One cubic, end
    tangents exact, passing through the true edge point at the 45-degree parameter."""
    P0 = (0.0, cy - B - r(0.0)); P3 = (sx * (A + r(1.0)), cy)
    t = _m.radians(45)
    ex, ey = A * _m.sin(t), -B * _m.cos(t)                    # centre-line point (lower quadrant)
    tx, ty = A * _m.cos(t), B * _m.sin(t)                     # its tangent
    tl = _m.hypot(tx, ty)
    nx, ny = ty / tl, -tx / tl                                # outward normal
    d = r(abs(ty) / tl)
    Mx, My = ex + d * nx, cy + ey + d * ny
    h1 = (Mx - 0.5 * abs(P3[0])) / 0.375                       # B(.5).x = .5 P0x + .375 h1 + .5 P3x  (P0x = 0)
    h2 = (0.5 * P0[1] + 0.5 * P3[1] - My) / 0.375              # B(.5).y = .5 P0y + .5 P3y - .375 h2
    return P0, (sx * h1, P0[1]), (P3[0], P3[1] - h2), P3


def mk_breve(**_):
    """trăng v0.96b (27/10 12:41 'độ dày của dấu ă lại cho đều và chuẩn'): ONE steel strip bent on a half-ellipse
    centre line, drawn with the LETTERS' contrast (R2 / type principle 'horizontals lighter than verticals'):
    T where it runs vertical (the arms, = the sắc strip), T*H/V where it runs level (the bottom, like the bottom of
    u / o), blended by the stroke direction exactly like band(). Both edges are offsets of the one centre line, so
    the strip is even all along — no swelling at the bottom where the eye reads a level stroke as heavier. Arms end
    at the ring's widest line, where the strip runs vertical: the level cut is square to the stroke. Same box as
    v0.96 (half 140, height max(101, 1.6 T)): every stack keeps its place."""
    T = _st()
    Th = T * GL.H / GL.V
    hgt = max(101, 1.6 * T)
    A, B, cy = 140 - T / 2, hgt - Th / 2, hgt
    ro = lambda s: (Th + (T - Th) * s) / 2
    ri = lambda s: -ro(s)
    oL = _offq(A, B, cy, ro, -1); oR = _offq(A, B, cy, ro, +1)
    iL = _offq(A, B, cy, ri, -1); iR = _offq(A, B, cy, ri, +1)
    path = [('M', *oL[3]), ('C', *oL[2], *oL[1], *oL[0]), ('C', *oR[1], *oR[2], *oR[3]),
            ('L', *iR[3]), ('C', *iR[2], *iR[1], *iR[0]), ('C', *iL[1], *iL[2], *iL[3]), ('Z',)]
    return [('add', path)]


TILDE_R8M_CREST = 0.29       # R8m: centre-line crest at 0.29 of the width (top edge peaks at the sample's 0.27), trough at 0.71
TILDE_R8M_MID_HANDLE = 0.30  # crest -> trough cubic: level handles 0.30 of the span (sample centre slope 26.6°)
TILDE_R8M_END_ANG = 45.0     # the centre line leaves each end at 45° (sample: ends steeper than the middle)
TILDE_R8M_END_HANDLE = 0.6   # end handles 0.6 of the crest handle
TILDE_R8M_FLANK = 0.94       # stroke T where it runs level (crest, trough), thinning toward 0.94 T as it turns steep:
                             # the sample's square-to-run thickness is 0.607 H at the crest, 0.58 H at 26.6° (ratio 0.955).
                             # The four numbers above were set by the best area match to the sample (XOR 4.5 % of its ink).


def mk_tilde_r8m(half, amp, T):
    """R8m (31/10, designer's sample: 'vấn đề không nằm ở điểm cắt, nó là cân bằng điểm cong'). Measured on the sample:
    crest at 0.27 / trough at 0.71-0.74 of the width; the left end's lower corner ON the trough line and the right end's
    upper corner ON the crest line (four extremes on two level lines); flatter through the middle (26.6°), steeper at
    the ends (39°); T square to the run. The old wave was one sine period cut at its zero crossings (ends at mid
    height: one crest and one trough), so its mass read as leaning down to the right.
    Construction (three cubic segments, no tracing): anchors at the crest (x = -half + 0.54 half, y = +amp) and the
    trough (point-symmetric), both with level tangents; crest -> trough handles TILDE_R8M_MID_HANDLE of the span; each
    end leaves at TILDE_R8M_END_ANG with handles as long as the crest's, its height solved so the end's lower (left) /
    upper (right) corner, offset T / 2cos square to the run, lies on the trough / crest line. Ends cut vertical; T
    square to the run (R8l)."""
    xc = -half + 2 * half * TILDE_R8M_CREST            # crest x; trough at -xc
    span = -2 * xc
    h = TILDE_R8M_MID_HANDLE * span
    te = _m.radians(TILDE_R8M_END_ANG)
    def cub(P, t):
        m = 1 - t
        x = m**3 * P[0][0] + 3 * m * m * t * P[1][0] + 3 * m * t * t * P[2][0] + t**3 * P[3][0]
        y = m**3 * P[0][1] + 3 * m * m * t * P[1][1] + 3 * m * t * t * P[2][1] + t**3 * P[3][1]
        dx = 3 * (m * m * (P[1][0] - P[0][0]) + 2 * m * t * (P[2][0] - P[1][0]) + t * t * (P[3][0] - P[2][0]))
        dy = 3 * (m * m * (P[1][1] - P[0][1]) + 2 * m * t * (P[2][1] - P[1][1]) + t * t * (P[3][1] - P[2][1]))
        return (x, y), (dx, dy)
    ye = -amp - T / 2 + T / (2 * _m.cos(te))              # the left end's lower corner on the trough line
    lh = min(TILDE_R8M_END_HANDLE * h, (xc + half) * 0.9)
    E = (-half - 80 * _m.cos(te), ye - 80 * _m.sin(te))   # centre line runs on past the cut, along the end tangent
    S1 = [E, (-half + lh * _m.cos(te), ye + lh * _m.sin(te)), (xc - lh, amp), (xc, amp)]
    S2 = [(xc, amp), (xc + h, amp), (-xc - h, -amp), (-xc, -amp)]
    S3 = [(-q[0], -q[1]) for q in S1[::-1]]
    # the two edges, sampled finely (T where level, FLANK x T where steep, square to the run)
    top, bot = [], []
    for k, S in enumerate((S1, S2, S3)):
        for i in range(0 if k == 0 else 1, 201):
            (x, y), (dx, dy) = cub(S, i / 200)
            d = _m.hypot(dx, dy) or 1
            r = (T + (TILDE_R8M_FLANK * T - T) * abs(dy) / d) / 2
            top.append((x - dy / d * r, y + dx / d * r)); bot.append((x + dy / d * r, y - dx / d * r))
    def clip(E_):            # keep -half <= x <= half, ends interpolated exactly on the vertical cuts
        out = []
        for a, b in zip(E_, E_[1:]):
            for q in (a, b):
                pass
        pts = [q for q in E_ if -half <= q[0] <= half]
        def at(xv):
            for a, b in zip(E_, E_[1:]):
                if (a[0] - xv) * (b[0] - xv) <= 0 and a[0] != b[0]:
                    t = (xv - a[0]) / (b[0] - a[0]); return (xv, a[1] + t * (b[1] - a[1]))
        return [at(-half)] + pts + [at(half)]
    top, bot = clip(top), clip(bot)
    # R8m-b (31/10 'chỉnh nét smooth hơn mẫu mình vẽ'): each edge is redrawn as THREE cubics with nodes only at its ends
    # and its two extremes (level tangents there), handles fitted to the offset edge by least squares: no facets, no
    # boolean re-fit, and the same 8 segments (4 corners) in every weight, so the masters stay point-compatible.
    def fit(P, t0, t1):
        n = len(P); L = [0.0]
        for a, b in zip(P, P[1:]): L.append(L[-1] + _m.dist(a, b))
        us = [l / L[-1] for l in L]
        p0, p3 = P[0], P[-1]
        A11 = A12 = A22 = B1 = B2 = 0.0
        for u, q in zip(us, P):
            b0, b1, b2, b3 = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
            c1 = (b1 * t0[0], b1 * t0[1]); c2 = (-b2 * t1[0], -b2 * t1[1])
            rx = q[0] - (b0 + b1) * p0[0] - (b2 + b3) * p3[0]; ry = q[1] - (b0 + b1) * p0[1] - (b2 + b3) * p3[1]
            A11 += c1[0] ** 2 + c1[1] ** 2; A12 += c1[0] * c2[0] + c1[1] * c2[1]; A22 += c2[0] ** 2 + c2[1] ** 2
            B1 += c1[0] * rx + c1[1] * ry; B2 += c2[0] * rx + c2[1] * ry
        det = A11 * A22 - A12 * A12
        a = (B1 * A22 - A12 * B2) / det; b = (A11 * B2 - A12 * B1) / det
        return (p0[0] + a * t0[0], p0[1] + a * t0[1]), (p3[0] - b * t1[0], p3[1] - b * t1[1]), p3
    def unit(a, b):
        d = _m.dist(a, b) or 1; return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    def edge_cubics(P):
        n = len(P)
        imax = max(range(n // 2), key=lambda i: P[i][1])          # the extreme near the crest
        imin = min(range(n // 2, n), key=lambda i: P[i][1])        # the extreme near the trough
        parts = [(0, imax), (imax, imin), (imin, n - 1)]
        out = []
        for a, b in parts:
            seg = P[a:b + 1]
            t0 = unit(seg[0], seg[min(3, len(seg) - 1)]) if a == 0 else (1.0, 0.0)
            t1 = unit(seg[max(-4, -len(seg))], seg[-1]) if b == n - 1 else (1.0, 0.0)
            out.append(fit(seg, t0, t1))
        return P[0], out
    yc = amp + T / 2
    sh = lambda q: (round(q[0], 2), round(q[1] + yc, 2))
    t0, tc = edge_cubics(top)
    b0, bc = edge_cubics(bot)
    path = [('M',) + sh(t0)]
    for c1, c2, p3 in tc:
        path.append(('C',) + sh(c1) + sh(c2) + sh(p3))
    path.append(('L',) + sh(bot[-1]))                         # right end: vertical cut
    rev = []                                                  # bottom edge right -> left
    pts_b = [b0] + [c[2] for c in bc]
    for k in range(len(bc) - 1, -1, -1):
        c1, c2, p3 = bc[k]
        rev.append(('C',) + sh(c2) + sh(c1) + sh(pts_b[k]))
    path += rev
    path.append(('Z',))                                       # left end: vertical cut
    return [('add', path)]


def mk_tilde(**_):
    T = _st()
    amp = max(24, 0.35 * T)
    if R8I():
        return mk_tilde_r8m(150, amp, T)
    return mk_tilde_v94(hgt=T + 2 * (amp + 4), half=150, w=T, wh=T)


def mk_hook(**_):
    T = _st()
    return mk_hook_v94(rx=max(73, 1.0 * T), ry=max(46, 0.9 * T), wv=T, wh=T)


def mk_hook_stack(**_):
    """hỏi riding on a trăng / mũ: same thickness T, a tighter curl so stacks stay low."""
    T = _st()
    return mk_hook_v94(rx=max(66, 0.85 * T), ry=max(40, 0.65 * T), wv=T, wh=T)


def mk_tilde_stack(**_):
    T = _st()
    amp = max(20, 0.28 * T)
    if R8I():
        return mk_tilde_r8m(140, amp, T)
    return mk_tilde_v94(hgt=T + 2 * (amp + 4), half=140, w=T, wh=T)


def mk_dotbelow(length=None):
    """nặng v0.95b: the same strip LYING under the letter; compose places this at y -52, so the top
    edge lands DOTB_GAP under the baseline."""
    t = _st()
    top = -(DOTB_GAP - 52)
    L = STRIP_L if length is None else length
    return [('add', rect(-L / 2, top - t, L / 2, top))]


def horn_ops_L94(x_wall, y_top, upper=False, o_shape=False, **_):
    """sừng (ơ ư) v0.94 — ONE steel plate for both (ref. ơư 26/10 22:24, measured):
      run top    y_run = letter top - 0.25 st
      post       width w = 0.64 st, left wall xp; top cut on the sắc slant: y_run + 0.69 st -> + 1.09 st
      underside  ONE oval compass from the post's right edge down to the letter's wall:
                 centre (xs, y_run), rx = slot + w, ry = 0.66 st
      inner      small compass f = 0.17 st between the letter's top and the post
    ư: xs = the stem's right wall, slot g = 0.19 st -> xp = xs + g.
    ơ: the post stands on the o's shoulder: xp = o's right edge - 0.47 st (it passes the o by 0.17 st)."""
    st = GL.V if upper else GL.v
    w, g, f = 0.64 * st, 0.19 * st, 0.17 * st
    yr = y_top - 0.25 * st
    if o_shape:
        xp = x_wall - 0.47 * st
        xs = xp - g
    else:
        xs = x_wall
        xp = xs + g
    rx, ry, k = g + w, 0.66 * st, 0.56
    CV = __import__('concept_v1')
    under = [('M', xs - 1, yr), ('L', xs + rx, yr),
             ('C', xs + rx, yr - k * ry, xs - 1 + k * (rx + 1), yr - ry, xs - 1, yr - ry), ('Z',)]
    fill = [('add', rect(xs - w, yr - ry, xs + 1, yr))] if o_shape else []   # ơ: the run's top runs flat back into the o's shoulder (no step)
    return [('group', fill + [('add', under),
                       ('add', poly([(xp, yr - 1), (xp + w, yr - 1), (xp + w, yr + 1.09 * st), (xp, yr + 0.69 * st)])),
                       ('add', rect(xp - f, yr - 1, xp + 1, yr + f)),
                       ('sub', CV.ell(xp - f, yr + f, f, f))])]


HORN_D = 1.07       # R8c v0.95: diameter of the round horn, in stems (ref. ƯƠ 27/10 00:05, measured)
HORN_UP = 0.17      # centre above the letter's top
HORN_IN = 0.24      # Ư: the disc overlaps the stem's right wall by this much
HORN_ANG_O = 31     # Ơ: direction of the disc centre from the O's top arc centre, degrees off vertical
HORN_BITE_O = 0.17  # Ơ: the disc overlaps the O's outer shoulder by this much (along the radius)


HP_W = 0.60      # post width (V)          — sample: 100 / 168
HP_H = 0.60      # post height above the letter's top
HP_G = 0.11      # Ư: slot between the stem and the post (above the top only)
HP_A = 0.17      # shelf depth under the top before the underside curve starts
HP_B = 0.43      # underside: vertical radius of the quarter oval


def horn_ops(x_wall, y_top, upper=False, o_shape=False, **_):
    """sừng v0.95b — ONE flat-topped L-plate for Ơ and Ư (ref. "THỰƠ" 27/10 00:17, measured on Bold):
      post  : width 0.60 V, flat top 0.60 V above the letter's top;
      shelf : the plate's top is flush with the letter's top, its depth runs 0.17 V down;
      under : ONE quarter oval (rx = slot + post, ry = 0.43 V) from the post's right edge back into the letter.
      Ư: the post stands 0.11 V clear of the stem (white slot above the top); the shelf bridges to the stem.
      Ơ: the post's right edge is flush with the O's right edge; the shelf squares the O's top-right corner."""
    st = GL.V if upper else GL.v
    w, h, g, a, b = HP_W * st, HP_H * st, HP_G * st, HP_A * st, HP_B * st
    CV = __import__('concept_v1')
    if o_shape:
        y_top = y_top + (GL.OV_C if upper else GL.OV_L)   # flush with the O's real top (no step at the overshoot)
        xr = x_wall
        xl = xr - w
        xs = xr - (w + g)                 # the oval's centre column (same radii as on Ư)
        # v0.95b fix "dấu ơ vẽ lỗi": the shelf must reach down to the O's shoulder everywhere left of the
        # oval, or a white wedge opens between the shelf and the curving shoulder.
        fill = [('add', rect(x_wall / 2, y_top - a - b, xs + 1, y_top)),
                ('add', rect(xs, y_top - a, xr, y_top))]
    else:
        xs = x_wall
        xl, xr = xs + g, xs + g + w
        fill = [('add', rect(xs - 1, y_top - a, xr, y_top))]
    rx, k = xr - xs, 0.5523
    yc = y_top - a
    under = [('M', xs - 1, yc + 0.5), ('L', xr, yc + 0.5),
             ('C', xr, yc - k * b, xs + k * rx, yc - b, xs - 1, yc - b), ('Z',)]
    return [('group', fill + [('add', under), ('add', rect(xl, y_top - 1, xr, y_top + h))])]


def horn_disc(*a, **k):
    raise RuntimeError('v0.95b: the round horn was replaced by the L-plate')


def horn_reach(upper=False, base=None):
    """how far the horn passes the letter's right edge."""
    st = GL.V if upper else GL.v
    if base in ('o', 'O'):
        return 0.0
    return (HP_G + HP_W) * st


def lc_i():
    g = Glyph('i', v, SB_STRAIGHT, SB_STRAIGHT, 0x69)
    g.add(fstem(0, 0, v, XH, f=fl, top=False), tittle(v / 2, XH + 62 + DOT / 2))
    return reg(g)


def lc_j():
    """j = stem + curved_hook (quarter ring, counter r1), same hook as g; dot above."""
    ops, xc, yc = GL.curved_hook(0)
    W = -xc
    g = Glyph('j', W, SB_STRAIGHT - (W - v) + 20, SB_STRAIGHT, 0x6A)
    g.ops = GL.shift_ops([('group', ops + [('add', rect(-v, yc - 1, 0, XH))])], W, 0)
    g.add(tittle(W - v / 2, XH + 62 + DOT / 2))
    return reg(g)


def apply(gaps=None):
    GL.MARKS.update({'acute': mk_acute, 'grave': mk_grave, 'circumflex': mk_circumflex,
                     'breve': mk_breve, 'hook': mk_hook, 'tilde': mk_tilde})
    GL.MARK_HGT.update({'circumflex': CIRC_HGT() / GL.CAP_SCALE, 'breve': max(101, 1.6 * _st()) / GL.CAP_SCALE})   # compose multiplies by CAP_SCALE
    GL.MARK_TOP.pop('acute', None)   # v0.96c: no common top line any more — one LENGTH (ACUTE_L) instead
    GL.MARK_STACK_FN.update({'hook': mk_hook_stack, 'tilde': mk_tilde_stack})
    GL.MARK_NOSCALE.update({'acute', 'grave', 'circumflex', 'breve', 'tilde', 'hook'})
    GL.MARK_STACK_LEN.update({'acute': ACUTE_L, 'grave': STRIP_STACK})
    GL.mk_dotbelow = mk_dotbelow
    GL.horn_ops = horn_ops
    GL.lc_i = lc_i; GL.lc_j = lc_j
    if gaps: GL.MARK_GAPS.update(gaps)
