"""GF Latin Core completion (28/10 16:52 'chuẩn hoá ... upload lên google font'; designer chose 'mở rộng đủ GF Latin Core').

Rule book additions (R8i … R8p, L-letters), every part cut from the house kit, sized from the stroke table:
  R8i  dot above  ( ̇ )  = ONE dot of the diaeresis (the tittle family), centred on the letter's axis
  R8j  double acute ( ̋ ) = TWO house acutes (18°, length 216, R8e), mark-to-mark gap 40 (R8 mark gap), centred
  R8k  ogonek ( ̨ )     = the house cedilla MIRRORED (drops from the foot, turns right, free end cut flat); it hangs
                          from the letter's rightmost foot on the baseline (A E U I / a e u i), stroke overlapping the
                          foot by 40 like the cedilla
  R8l  comma below ( ̦ ) = the house comma (dot + flat-cut tail) at 0.78 size, its top 40 under the baseline,
                          centred under the letter. Latvian Ģ Ķ Ļ Ņ ķ ļ ņ (Unicode: cedilla) take the comma below,
                          as in every reference font; ģ takes the comma TURNED above (no room below the g)
  R8m  vertical caron   = the house apostrophe ’ at 0.85 size, 40 right of the stem, top on the stem's top:
                          ď ľ ť Ľ (Ď Ť keep the chevron caron, R8 caron)
  R8n  stroke Ł ł       = a slash of the Ø rule turned into a short bar: parallel edges, flat level cuts, vertical
                          thickness = the horizontal of the case (HM caps, 0.9 h lowercase), rising 35°, centred on the stem
  R8o  stroke Ħ ħ       = the Đ / đ bar rule: Ħ a second bar HM across both stems at 0.78 cap, overhanging 60 with flared
                          ends; ħ the đ bar mirrored (25 past the stem outside, 120 over the shoulder)
  L-ẞ  capital sharp s  = stem V + top bar H + one diagonal (DIAG, flat cuts) into a lower bowl drawn like the 3's
                          (ring of V / H, open left, vertical house cut on the counter wall)
"""
import math
import unicodedata
import glyphs_c as GL
from glyphs_c import *
import figs_c as F

DOTA, DBLAC, OGON, COMMAB, CEDIL, CARON = '̇', '̋', '̨', '̦', '̧', '̌'
MARK_GAP = 40
LATVIAN = set('GKLNRgklnr')          # Unicode cedilla on these = comma below (typographic convention)


# ------------------------------------------------------------------ helpers
def ink_x_at(ops, y, side='r'):
    """rightmost / leftmost ink x of a glyph's outline at height y (union evaluated)."""
    import booleng
    xs = []
    for c in booleng.evaluate(ops):
        pts = []
        for s in c:
            if s[0] in ('M', 'L'):
                pts.append((s[1], s[2]))
            elif s[0] == 'C':
                p0 = pts[-1] if pts else (s[5], s[6])
                for i in range(1, 9):
                    t = i / 8; m = 1 - t
                    pts.append((m**3 * p0[0] + 3 * m * m * t * s[1] + 3 * m * t * t * s[3] + t**3 * s[5],
                                m**3 * p0[1] + 3 * m * m * t * s[2] + 3 * m * t * t * s[4] + t**3 * s[6]))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 - y) * (y1 - y) < 0:
                xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    if not xs:
        return None
    return max(xs) if side == 'r' else min(xs)


def bounds(ops):
    import latin1_c as L1
    return L1.bounds(ops)


# ------------------------------------------------------------------ marks
def mk_dotabove(upper=False):
    k = 0.15 + 0.85 * GL.WK
    d = (140 if upper else 132) * k                # R8i: one dot of the diaeresis
    return [('add', circle(0, d / 2, d / 2))]


def mk_dblacute(upper=False):
    # 1.002: the double acute (Hungarian ő ű) keeps the R8e standing strips; the R8i lying sắc is Vietnamese and two of
    # them side by side would run 550 wide. Open for the designer.
    a = __import__('marks_flat')._mk_acute_r8e()
    b = bounds(a)
    w = b[2] - b[0]
    off = (w + MARK_GAP) / 2                       # R8j: two acutes, gap 40
    c = (b[0] + b[2]) / 2
    return shift_ops(a, -off - c, 0) + shift_ops(a, off - c, 0)


def mk_ogonek(upper=True):
    """R8k: the house cedilla's construction (vertical stroke, one compass turn, horizontal end cut flat), MIRRORED,
    one size up (it carries the letter's foot): stroke 1.15 x the cedilla's, turn radius 85, drop to -175."""
    import latin1_c as L1
    w, wh = 1.15 * 88 * GL.WK, 1.15 * 70 * GL.WK
    r = max(85, w / 2 + 24)
    xs, ytop = 0, 40
    ybot = -175
    xl = xs - 1.55 * r
    ced = [('group', [('add', rrect(xl, ybot, xs + w / 2, ytop, (0, 0, r + w / 2, 0))),
                      ('sub', rrect(xl - 1, ybot + wh, xs - w / 2, ytop + 1, (0, 0, max(r - w / 2, 18), 0)))])]
    return L1.tf_ops(ced, lambda x, y: (-x, y))          # stroke at x in [-w/2, w/2], tail to the right


def mk_commabelow(scale=0.78):
    ops = F._comma_ops(0, 0)                       # dot centre at (R, R), tail down to -170
    b = bounds(ops)
    ops = scale_ops(shift_ops(ops, -(b[0] + b[2]) / 2, -b[3]), scale, scale)
    return shift_ops(ops, 0, -MARK_GAP)            # R8l: top 40 under the baseline


def mk_commaturned(scale=0.78):
    ops = F._comma_ops(0, 0)
    b = bounds(ops)
    ops = shift_ops(ops, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)
    ops = F.rot180_ops(ops, 0, 0)
    ops = scale_ops(ops, scale, scale)
    b = bounds(ops)
    return shift_ops(ops, 0, -b[1])                # bottom on 0: placed in the mark zone by the caller


def mk_vcaron(scale=0.85):
    ops = F._comma_ops(0, 0)
    b = bounds(ops)
    ops = scale_ops(shift_ops(ops, -b[0], -b[3]), scale, scale)   # left edge 0, top 0
    return ops


# ------------------------------------------------------------------ placement on a base
def ogonek_on(bops, body, foot_y=12):
    """R8k: the ogonek's stroke stands under the base's rightmost foot on the baseline (its right edge 12 inside it)."""
    xr = ink_x_at(bops, foot_y, 'r')
    xr = body if xr is None else xr
    w = 1.15 * 88 * GL.WK
    return shift_ops(mk_ogonek(), xr - 12 - w / 2, 0)


def vcaron_on(stem_right, top):
    return shift_ops(mk_vcaron(), stem_right + MARK_GAP, top)


# ------------------------------------------------------------------ capitals
def compose_caps(ch, bg, upper=True):
    """caps (and lowercase, upper=False) composites with the new marks; returns (ops, parts, extra_rsb) or None."""
    d = unicodedata.normalize('NFD', ch)
    base, marks = d[0], d[1:]
    zone = GL.ZONE_UC if upper else GL.ZONE_LC
    cx = bg.body / 2
    ops, parts, xr = list(bg.ops), [('base', list(bg.ops))], 0
    for m in marks:
        if m == DOTA:
            o = shift_ops(mk_dotabove(upper), cx, zone); nm = 'dotabove'
        elif m == DBLAC:
            o = shift_ops(mk_dblacute(upper), cx, zone); nm = 'dblacute'
        elif m == OGON:
            o = ogonek_on(bg.ops, bg.body); nm = 'ogonek'
        elif m == COMMAB or (m == CEDIL and base in LATVIAN):
            yb = min(0, bounds(bg.ops)[1])           # R8l: 40 under the base's own ink (round bases overshoot)
            o = shift_ops(mk_commabelow(), cx, yb); nm = 'commabelow'
        else:
            return None
        ops += o; parts.append((nm, o))
    return ops, parts


# ------------------------------------------------------------------ letters + spacing marks (called by latin1_c.build_latin1)
def slash_bar(x0, x1, yc, t_perp, ang=35.0):
    """R8n: a short bar rising ang°, perpendicular thickness t_perp, ends cut vertically like every house bar."""
    dy = (x1 - x0) * math.tan(math.radians(ang))
    t = t_perp / math.cos(math.radians(ang))
    y0 = yc - dy / 2 - t / 2
    return ('add', poly([(x0, y0), (x1, y0 + dy), (x1, y0 + dy + t), (x0, y0 + t)]))


def L_Lslash():
    import latin1_c as L1
    l = G['L']
    ops = list(l.ops) + [slash_bar(-70, V + 130, 0.40 * CAP, HM)]
    return L1.make('Ł', ops, max(20, l.lsb - 70), l.rsb)


def L_Hbar():
    import latin1_c as L1
    h = G['H']
    yb = 0.78 * CAP - HM / 2
    ops = list(h.ops) + [('add', fbar(-60, yb, h.body + 60, yb + HM, left=True, right=True))]   # R8o: flared free ends
    return L1.make('Ħ', ops, max(20, h.lsb - 60), max(20, h.rsb - 60))


def L_Germandbls():
    """ẞ: stem V + top bar H + one diagonal (DIAG, level cuts) landing on the lower bowl; the lower bowl is the B's
    (D-shape, V / H, compass corners) whose bottom stroke ends free, cut vertically 0.6 V off the stem."""
    import latin1_c as L1
    W = G['B'].body + 70                            # wider than B: the upper counter is a triangle
    top = CAP
    yj = round(0.58 * CAP)                          # top of the lower bowl
    ym = yj - HM
    xt = W - 40                                     # the top bar's right end = the diagonal's top right
    xj = V + 0.45 * (W - V)                         # the diagonal lands on the bowl's top bar here
    dw = diag_dx(DIAG, xt - xj, top - yj)
    kd = (xt - dw - xj) / (top - ym)                # the diagonal's inner edge: x = xj + kd (y - ym)
    ops = [('add', fstem(0, 0, V, top, top=False)),
           ('add', rect(V / 2, top - H, xt, top)),
           ('add', poly([(xj, ym), (xj + dw, ym), (xt, top), (xt - dw, top)])),
           ('group', [('add', rrect(V / 2, 0, W, yj, (0, FULL, FULL, 0))),
                      ('sub', rrect(V - 1, H, W - V, ym, (0, FULL, FULL, 0))),
                      ('sub', poly([(V - 1, ym - 1), (xj + 1 - kd, ym - 1), (xj + 1 + kd * (yj + 2 - ym), yj + 1), (V - 1, yj + 1)])),   # open left of the diagonal's inner edge
                      ('sub', rect(V - 1, -1, V + 0.6 * V, H + 1))])]        # the bottom stroke ends free
    return L1.make('ẞ', ops, SB_STRAIGHT, SB_ROUND)


def S_core_marks():
    import latin1_c as L1
    L1.spacing_mark('˘', GL.mark_ops('breve'))
    L1.spacing_mark('˙', mk_dotabove())
    L1.spacing_mark('˝', mk_dblacute())
    og = mk_ogonek(); b = bounds(og)
    L1.make('˛', shift_ops(og, -b[0], 0), 60, 60)


def build_core():
    L_Lslash(); L_Hbar(); L_Germandbls(); S_core_marks()
