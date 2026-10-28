"""A2 — Latin-1 / Windows-1252 completion (Bold master).

New marks (same construction rules as the Vietnamese kit):
  diaeresis = two round dots (the tittle family)    ring  = a small compass ring
  caron     = the circumflex chevron turned over     macron = a flat-cut bar
  cedilla   = an even stroke hooking left under the letter, ends cut flat
New letters: Æ æ Œ œ Ø ø ß Þ þ ð µ ƒ   (Ð = Đ)
Symbols: ^ ` ~ ¡ ¿ ¢ £ ¤ ¥ ¦ § © ® ª º ¬ ± ² ³ ¹ ¼ ½ ¾ ´ ¨ ¯ ¸ ˆ ˜ ˇ ˚ ¶ ‚ „ † ‡ • ‰ ‹ › € ™ space
"""
import math as _m
import unicodedata
import glyphs_c as GL
from glyphs_c import *
from marks_flat import band, tittle
import figs_c as F
from lcsym import lcg, XH as LXH, ASC as LASC, DESC as LDESC
LV = lambda: round(0.93 * GL.V)            # R0b: the current lowercase stem (F2: v = 0.93 V)

G = GL.G
DIA, RING, CARON, MACRON, CEDIL = '̈', '̊', '̌', '̄', '̧'


# ---------------------------------------------------------------- helpers
def bounds(ops):
    xs, ys = [], []
    for op, c in ops:
        if op == 'group':
            b = bounds([(o, cc) for o, cc in c if o in ('add', 'group')])
            if b: xs += [b[0], b[2]]; ys += [b[1], b[3]]
        elif op == 'add':
            for x, y in flatten(c, 8):
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def tf_ops(ops, f):
    out = []
    for op, c in ops:
        out.append((op, tf_ops(c, f)) if op == 'group' else (op, transform(c, f)))
    return out


def make(ch, ops, lsb, rsb, name=None):
    """register a glyph from ops in any coordinates: normalised so the ink starts at x=0."""
    b = bounds(ops)
    x0 = b[0]
    ops = shift_ops(ops, -x0, 0)
    g = Glyph(name or ch, b[2] - x0, lsb, rsb, ord(ch) if len(ch) == 1 else 0)
    g.ops = ops
    G[g.name] = g
    return g


def scaled(ch, s, dx=0, dy=0):
    """ops of glyph ch, scaled about its origin and moved."""
    g = G[ch]
    return tf_ops(g.ops, lambda x, y: (dx + x * s, dy + y * s))


# ---------------------------------------------------------------- marks
def mk_diaeresis(upper=False):
    k = 0.15 + 0.85 * GL.WK               # dots shrink a little less than strokes
    d = (140 if upper else 132) * k
    gap = 64 + (1 - k) * 60                # keep the pair's overall span
    return [('add', circle(-(gap / 2 + d / 2), d / 2, d / 2)), ('add', circle(gap / 2 + d / 2, d / 2, d / 2))]


def mk_ring(upper=False):
    import marks_flat as MF                       # R8b: one mark stroke (sides MV, top/bottom MH)
    T = MF._st()                                   # v0.95 R8: the ring is cut from the same strip (one thickness T)
    w, h_ = (max(228, 2 * T + 100), max(186, 2 * T + 70)) if upper else (220, 190)
    return [('group', ring(-w / 2, 0, w / 2, h_, T, T, FULL, FULL))]


def mk_caron(upper=False):
    ops = GL.mark_ops('circumflex', upper)
    hgt = GL.MARK_HGT['circumflex'] * (CAP_SCALE if upper else 1.0)
    return F.rot180_ops(ops, 0, hgt / 2)


def mk_macron(upper=False):
    # R8q (28/10 'dấu ngang ngắn' — the house huyền is the 300-long strip LYING (R8d), so a 300 macron read as À):
    # the macron is the SAME strip (thickness T, flared free ends) cut to 0.6 of its length (180), in every weight
    import os, marks_flat as MF
    if os.environ.get('MACRON_SHORT', '1') == '1':
        L = 0.6 * MF.STRIP_L
        return [('add', fbar(-L / 2, 0, L / 2, MF._st(), f=fl - 2, left=True, right=True))]
    return [('add', fbar(-150, 0, 150, MF.MH, f=fl - 2, left=True, right=True))]   # R8b: a horizontal = MH


def mk_cedilla():
    """stroke dropping from the letter's foot and hooking left like the j tail: compass corner
    (outer/counter rounded rects, true curves), the free end cut flat (vertical)."""
    w, wh = 88 * GL.WK, 70 * GL.WK
    r = max(50, w / 2 + 18)                       # centre-line radius; inside never < 18u
    xs, ytop = 14, 40
    ybot = -40 - r - wh / 2                       # outer bottom of the turn
    xl = xs - 1.7 * r                             # free end (cut flat)
    return [('group', [('add', rrect(xl, ybot, xs + w / 2, ytop, (0, 0, r + w / 2, 0))),
                       ('sub', rrect(xl - 1, ybot + wh, xs - w / 2, ytop + 1, (0, 0, max(r - w / 2, 18), 0)))])]


NEW_TOP = {DIA: mk_diaeresis, RING: mk_ring, CARON: mk_caron, MACRON: mk_macron}

_compose_vn = GL.compose


def compose(ch, gaps=None):
    """Vietnamese composer + the Latin-1 marks (single mark above, or cedilla below)."""
    if ch in G:
        return G[ch]
    d = unicodedata.normalize('NFD', ch)
    base, marks = d[0], d[1:]
    import latin_core_c as LC
    new = [m for m in marks if m in NEW_TOP or m == CEDIL or m in (LC.DOTA, LC.DBLAC, LC.OGON, LC.COMMAB)]
    if not new:
        return _compose_vn(ch, gaps)
    upper = base.isupper()
    bname = 'dotlessi' if base == 'i' else base
    bg = G[bname]
    import latin_core_c as LC                       # GF Latin Core (R8i-R8m): dot above, double acute, ogonek, comma below
    if any(m in (LC.DOTA, LC.DBLAC, LC.OGON, LC.COMMAB) for m in marks) or (CEDIL in marks and base in LC.LATVIAN):
        r = LC.compose_caps(ch, bg, upper)
        g = Glyph('uni%04X' % ord(ch), bg.body, bg.lsb, bg.rsb, ord(ch))
        g.ops, g.parts = r
        return g
    if base == 'L' and CARON in marks:              # R8m: the vertical caron (apostrophe) right of the stem
        g = Glyph('uni%04X' % ord(ch), bg.body, bg.lsb, bg.rsb, ord(ch))
        o = LC.vcaron_on(V, CAP)
        g.ops = list(bg.ops) + o; g.parts = [('base', list(bg.ops)), ('vcaron', o)]
        return g
    g = Glyph('uni%04X' % ord(ch), bg.body, bg.lsb, bg.rsb, ord(ch))
    g.ops = list(bg.ops)
    g.parts = [('base', list(bg.ops))]
    cx = bg.body / 2
    zone = GL.ZONE_UC if upper else GL.ZONE_LC
    for m in marks:
        if m in NEW_TOP:
            ops = shift_ops(NEW_TOP[m](upper), cx, zone)
            g.ops += ops; g.parts.append((unicodedata.name(m).split()[-1].lower(), ops))
        elif m == CEDIL:
            ox = {'C': cx + 20, 'c': cx + 16}.get(base, cx)
            ops = shift_ops(mk_cedilla(), ox, 0)
            g.ops += ops; g.parts.append(('cedilla', ops))
        elif m in GL.TONES or m == GL.CIRC:
            name = GL.TONES.get(m, 'circumflex')
            ops = shift_ops(GL.mark_ops(name, upper), cx, zone)
            g.ops += ops; g.parts.append((name, ops))
    return g


GL.compose_latin = compose


# ---------------------------------------------------------------- letters
def L_Oslash():
    o = G['O']
    W = o.body
    dw = diag_dx(DIAG * 0.62, W, CAP + 120)
    ops = list(o.ops) + [('add', poly([(-30, -60), (-30 + dw, -60), (W + 30, CAP + 60), (W + 30 - dw, CAP + 60)]))]
    return make('Ø', ops, o.lsb, o.rsb)


def L_oslash():
    o = G['o']
    W = o.body
    dw = diag_dx(diag * 0.62, W, XH + 110)
    ops = list(o.ops) + [('add', poly([(-24, -56), (-24 + dw, -56), (W + 24, XH + 56), (W + 24 - dw, XH + 56)]))]
    return make('ø', ops, o.lsb, o.rsb)


def L_AE():
    """Æ = the LEFT LEG OF A + E (27/10 13:03 'xéo không cân đối'). Before: the diagonal was a wedge (dw at the
    foot, 0.35 dw at the top) at its own angle — its two edges were not parallel, so the stroke thinned upward and
    leaned more than A. Now (R7): the leg is A's left leg exactly — same angle (outer edge rises W_A/2 - 75 over the
    cap height), same horizontal width dw, both edges PARALLEL, foot cut level on the baseline. The E stem's left
    edge stands on A's axis (W_A / 2), so the white between leg and stem is exactly the left half of A's counter
    (same apex height, same width at the bar) and the leg's top is the left half of A's flat apex. Bar at A's height
    (168), its end just inside the leg's outer edge (as A)."""
    WA = 572 + gw('diag')                       # cap_A width (R2c)
    run = WA / 2 - 75                           # A's outer leg edge: (0, 0) -> (run, CAP)
    dw = diag_dx(DIAG, WA / 2 - 80, CAP)        # A's leg width
    xs = WA / 2                                 # E stem's left edge on A's AXIS: the leg's inner edge meets it exactly
                                                # where A's two inner edges meet, so Æ's counter = the left half of A's
    W = xs + 470 + gw('one')                    # the E part keeps E's width rule (R2c)
    ops = [('add', poly([(0, 0), (dw, 0), (run + dw, CAP), (run, CAP)])),
           ('add', fstem(xs, 0, xs + V, CAP, top=False)),
           ('add', fbar(xs + V / 2, CAP - H, W, CAP)), ('add', fbar(xs + V / 2, 0, W, H)),
           ('add', fbar(xs + V / 2, 290, W - 46, 290 + HM)),
           ('add', rect(run * (168 + HM) / CAP + 2, 168, xs + 2, 168 + HM))]
    ops.append(('sub', rect(-300, -300, W + 300, 0)))
    return make('Æ', ops, SB_DIAG, SB_STRAIGHT - 18)


def L_ae():
    a, e = G['a'], G['e']
    sh = a.body - v + 10
    ops = list(a.ops) + [('group', shift_ops(e.ops, sh, 0))]
    return make('æ', ops, a.lsb, e.rsb)


def L_OE():
    o, e = G['O'], G['E']
    sh = o.body - V
    ops = [('group', list(o.ops))] + [('group', shift_ops(e.ops, sh, 0))]
    # v0.969 (R2c: advance monotonic R -> M -> B): the shared stem swallows one stroke of growth while both outer
    # sides tighten (R13), so the ligature lost 1u in Bold; it gives back a quarter of the caps' stroke growth on the right
    return make('Œ', ops, o.lsb, e.rsb + 0.25 * GL.DV_C)


def L_oe():
    o, e = G['o'], G['e']
    sh = o.body - v + 10
    ops = [('group', list(o.ops))] + [('group', shift_ops(e.ops, sh, 0))]
    return make('œ', ops, o.lsb, e.rsb)


def L_germandbls():
    """ß: ascender stem + n-shoulder; the lower bowl ends like the 3 (compass corner, C-cut)."""
    W = 490
    top = ASC
    ym = 400
    Rs = min(W - 26, top - ym) / 2
    yb_top = ym + HM - 40
    lo, hi = h - OV_L, ym - 40
    # 26/10 house hook cut: vertical, ending on the counter's lower-left arc; as long as it can be
    # while the tail keeps TAIL_CLEAR off the stem foot (stem v + flare)
    rl = min(W - v - (v - 1), hi - lo) / 2
    cyl = lo + rl
    xcl = max(v - 1, v + fl + GL.TAIL_CLEAR)
    ops = [('add', fstem(0, 0, v, top - Rs, f=fl, top=False)),
           ('group', [('add', rrect(0, ym, W - 26, top, (FULL, FULL, 0, 0))),
                      ('sub', rrect(v, ym - 1, W - 26 - v + 8, top - h, (FULL, FULL, 0, 0))),
                      ('sub', rect(v, ym - 1, W, ym + 70))]),
           ('group', [('add', rrect(v / 2, -OV_L, W, yb_top, (0, FULL, FULL, FULL))),
                      ('sub', rrect(v - 1, lo, W - v, hi, (0, FULL, FULL, FULL))),
                      ('sub', rect(-1, cyl, W / 2, ym + HM)),
                      ('sub', rect(-1, -OV_L - 1, xcl, cyl)),
                      *[b for b in [GL.blunt_tip(v - 1 + rl, cyl, rl, xcl, 'l', 'down', v)] if b]])]
    return make('ß', ops, SB_STRAIGHT, SB_ROUND)


def L_Thorn():
    p = G['P']
    ops = shift_ops([op for op in p.ops if op[0] != 'add' or True], 0, 0)
    W = p.body
    ops = [('add', fstem(0, 0, V, CAP)),
           ('group', [('add', rrect(V / 2, 130, W, 560, (0, FULL, FULL, 0))),
                      ('sub', rrect(V - 1, 130 + 128 * GL.WKC, W - V, 560 - H, (0, FULL, FULL, 0)))])]
    return make('Þ', ops, p.lsb, p.rsb)


def L_thorn():
    p = G['p']
    ops = [(op, c) for op, c in p.ops]
    ops.append(('add', fstem(0, XH - 20, v, ASC, f=fl, bot=False)))
    return make('þ', ops, p.lsb, p.rsb)


def L_eth():
    o = G['o']
    W = o.body
    ops = list(o.ops) + [('add', poly([(W - v - 10, XH - 120), (W, XH - 120), (W * 0.55 + 70, ASC), (W * 0.55 - 50, ASC)])),
                         ('add', fbar(W * 0.25, 600, W - 10, 600 + 100 * GL.WK, f=fl - 2, left=True, right=True))]
    return make('ð', ops, o.lsb, o.rsb)


def L_mu():
    """µ (R0b): the CURRENT u (F3, n turned 180°) whose left leg runs on down to the descender as a stem (R4)."""
    u = lcg('u')
    ops = list(u.ops) + [('add', fstem(0, LDESC, LV(), 0.55 * LXH, f=fl, top=False))]
    return make('µ', ops, u.lsb, u.rsb)


def L_florin():
    """ƒ (R0b): the CURRENT f's hook + crossbar on top, the CURRENT j's hook below (F6), one straight stem
    between them (no flare where the stem runs into a hook)."""
    f, j = lcg('f'), lcg('j')
    lv = LV()
    xs = 70                                      # lc96f: f's stem left edge
    xr_j = lv + 40                               # lc96f: j's stem right edge
    top = f.ops[:2] + [f.ops[3]]                 # f = hook ring, hook bar, stem, crossbar
    tail = shift_ops(j.ops[:2], xs + lv - xr_j, 0)   # j = hook ring, hook bar, stem, dot
    # the stem runs exactly between the two hooks' centre lines (F6: each hook's side IS the stem there)
    lh = 0.93 * GL.H
    r = (round(440 + 1.2 * (lv - round(0.93 * 116))) - 2 * lv) / 2 * 0.55      # lc96f: HK x the n's counter radius
    cy_j, cy_f = LDESC + r / 0.88 + lh, LASC - r / 0.88 - lh
    ops = top + tail + [('add', rect(xs, cy_j - 1, xs + lv, cy_f + 1))]
    return make('ƒ', ops, 30, f.rsb)


# ---------------------------------------------------------------- symbols
def spacing_mark(ch, ops, lc=True, w=None):
    zone = GL.ZONE_LC
    ops = shift_ops(ops, 0, zone)
    return make(ch, ops, 60, 60)


def S_misc():
    out = []
    out.append(spacing_mark('´', GL.mark_ops('acute')))
    out.append(spacing_mark('`', GL.mark_ops('grave')))
    out.append(spacing_mark('¨', mk_diaeresis()))
    out.append(spacing_mark('¯', mk_macron()))
    out.append(spacing_mark('ˆ', GL.mark_ops('circumflex')))
    out.append(spacing_mark('˜', GL.mark_ops('tilde')))
    out.append(spacing_mark('ˇ', mk_caron()))
    out.append(spacing_mark('˚', mk_ring()))
    out.append(make('¸', shift_ops(mk_cedilla(), 0, 0), 60, 60))
    # ascii ^ ~
    circ = scale_ops(GL.mark_ops('circumflex'), 1.35, 1.6)
    out.append(make('^', shift_ops(circ, 0, 420), 40, 40))
    til = scale_ops(GL.mark_ops('tilde'), 1.45, 1.3)
    b = bounds(til)
    out.append(make('~', shift_ops(til, 0, F.MATH_Y - (b[1] + b[3]) / 2), 40, 40))
    # space
    sp = Glyph('space', 240, 0, 0, 0x20); sp.ops = []; G[' '] = sp; G['space'] = sp
    nb = Glyph('nbspace', 240, 0, 0, 0xA0); nb.ops = []; G[' '] = nb
    for cp, nm in ((0x202F, 'uni202F'), (0x2009, 'uni2009')):   # F16: French narrow no-break / thin space, reference median 0.65 of the word space
        t = Glyph(nm, round(0.65 * 240), 0, 0, cp); t.ops = []; G[chr(cp)] = t
    return out


def S_inverted():
    ex, q = G['!'], G['?']
    yc = (CAP + DESC + 40) / 2
    make('¡', F.rot180_ops(ex.ops, ex.body / 2, yc), ex.rsb, ex.lsb)
    make('¿', F.rot180_ops(q.ops, q.body / 2, yc), q.rsb, q.lsb)


def S_cent():
    c = lcg('c')                                 # R0b: the current c
    W = c.body
    XH = LXH
    ops = list(c.ops) + [('add', rect(W * 0.52 - 46 * GL.WK, XH, W * 0.52 + 46 * GL.WK, XH + 110)),
                         ('add', rect(W * 0.52 - 46 * GL.WK, -110, W * 0.52 + 46 * GL.WK, 0))]
    make('¢', ops, c.lsb, c.rsb)


def S_sterling():
    W = 500 + gw('bowl')                       # R2c
    x0 = 70
    xw = W - 20 - V + 10                       # counter's right wall
    top = CAP + OV_C
    # R5 (v0.94 QA: the wall cut left a 0° needle): the hook ends with the house tail
    tu = GL.tail((x0 + V + xw) / 2, top - H, xw, V, 'r', 'up', tip_limit=470 + 0.3 * H,
                 ring=(top - (W - 20 - x0) / 2, (W - 20 - x0) / 2, (W - 20 - x0) / 2))
    ops = [('add', rect(x0, H - 2, x0 + V, 470)),
           ('group', [('add', rrect(x0, 360, W - 20, top, (FULL, FULL, 0, 0))),
                      ('sub', rrect(x0 + V, 359, xw, top - H, (FULL, FULL, 0, 0))),
                      ('sub', rect(x0 + V, 359, W, 470))] + __import__('concept_v1').arm_ink(tu) + [
                      ('sub', tu['disk']),
                      ('sub', rect(tu['xt'], tu['cy'], W + 1, top + 1)),
                      ('sub', rect((x0 + V + xw) / 2, 359, W + 1, tu['tip']))]),
           ('add', fbar(0, 300, x0 + V + 150, 300 + HM, left=True, right=True)),
           ('add', fbar(0, 0, W, H, left=False, right=True))]
    make('£', ops, SB_ROUND, SB_ROUND - 10)


def S_currency():
    s = 380
    cx, cy = s / 2, F.MATH_Y
    ops = [('group', ring(cx - 130, cy - 130, cx + 130, cy + 130, 84 * GL.WKC, 84 * GL.WKC, FULL, FULL))]
    arm = [('add', rect(cx - 36 * GL.WKC, cy + 120, cx + 36 * GL.WKC, cy + 200))]
    for k in range(4):
        ops += F.rot_ops(arm, _m.pi / 4 + k * _m.pi / 2, cx, cy)
    make('¤', ops, 30, 30)


YEN_FOOT = 38
YEN_GAP = 60   # v0.969 (closing QA: ¥ Medium): the two bars keep ONE gap in Regular units (rule: ¥ € gap 60), not 0.5 bar


def S_yen():
    y = G['Y']
    W = y.body
    # 26/10 sync: the upper bar's top sits exactly at the Y's crotch (no 10-17u sliver of stem
    # showing between bar and arms), the lower bar one bar-gap below, in every weight
    t = 100 * GL.WKC
    crotch = 236                                                     # cap_Y: the V's flat foot meets the stem here
    # v0.969: gap (60) and the lower bar's foot (38) are fixed in Regular units; the bars stack up from that foot, so
    # in Medium / Bold the upper bar rises over the crotch and crosses the arms (never a sliver of stem between)
    top = max(crotch, YEN_FOOT + 2 * t + YEN_GAP)
    ops = list(y.ops) + [('add', fbar(W / 2 - 200, top - t, W / 2 + 200, top, left=True, right=True)),
                         ('add', fbar(W / 2 - 200, top - 2 * t - YEN_GAP, W / 2 + 200, top - t - YEN_GAP, left=True, right=True))]
    make('¥', ops, y.lsb, y.rsb)


def S_brokenbar():
    ops = [('add', rect(0, -200, V - 30, 330)), ('add', rect(0, 470, V - 30, CAP + 120))]
    make('¦', ops, 60, 60)


def S_section():
    s = lcg('s')                                 # R0b: the current s
    ops = [('group', shift_ops(s.ops, 0, 250))] + [('group', shift_ops(s.ops, 0, -120))]
    make('§', ops, s.lsb, s.rsb)


def _circled(ch, inner_ops):
    W = 780
    cy = CAP / 2
    ops = [('group', ring(0, cy - W / 2, W, cy + W / 2, 92 * GL.WKC, 92 * GL.WKC, FULL, FULL))]
    b = bounds(inner_ops)
    iw, ih = b[2] - b[0], b[3] - b[1]
    ops += shift_ops(inner_ops, W / 2 - (b[0] + iw / 2), cy - (b[1] + ih / 2))
    make(ch, ops, 30, 30)


def S_copy_reg():
    _circled('©', [('group', scaled('C', 0.56))])
    _circled('®', [('group', scaled('R', 0.56))])


def S_ordinals():
    for ch, src in (('ª', 'a'), ('º', 'o')):
        g = lcg('a@0.6' if src == 'a' else src)  # R0b: the current a / o (small a: aperture kept, lcsym)
        s = 0.6
        # 27/10 13:08 'Bold/Medium hơi dính': the bar was fixed at 250..250+70*WK, so in Bold its top reached
        # the letter's overshoot (3 u apart). Now the bar hangs ONE clearance (46 = 0.5 h Regular, as đ / e)
        # under the letter's lowest ink, and is as thick as the small letter's own level strokes (0.6 h).
        y_ink = 330 - 12 * s                     # the scaled letter's overshoot below its baseline
        bt = s * 0.93 * GL.H
        ops = [('group', tf_ops(g.ops, lambda x, y: (x * s, 330 + y * s)))] + \
              [('add', rect(0, y_ink - 46 - bt, g.body * s, y_ink - 46))]
        make(ch, ops, 40, 40)


def S_logicalnot():
    W = 480
    ops = [('add', rect(0, F.MATH_Y, W, F.MATH_Y + F.MT_)), ('add', rect(W - F.MT_, F.MATH_Y - 150, W, F.MATH_Y + 1))]
    make('¬', ops, 40, 40)


def S_plusminus():
    W = 480
    c = F.MATH_Y + 60
    ops = [('add', rect(0, c - F.MT_ / 2, W, c + F.MT_ / 2)),
           ('add', rect(W / 2 - F.MT_ / 2, c - 200, W / 2 + F.MT_ / 2, c + 200)),
           ('add', rect(0, c - 300 - F.MT_ / 2, W, c - 300 + F.MT_ / 2))]
    make('±', ops, 40, 40)


SUP_S, SUP_Y = 0.56, 330


def S_superiors():
    for ch, src in (('¹', '1'), ('²', '2'), ('³', '3')):
        make(ch, [('group', scaled(src, SUP_S, 0, SUP_Y))], 30, 30)


def S_fractions():
    sl = lambda x0: [('add', poly([(x0, 0), (x0 + 92 * GL.WKC, 0), (x0 + 360, CAP), (x0 + 360 - 92 * GL.WKC, CAP)]))]
    for ch, a, b in (('¼', '1', '4'), ('½', '1', '2'), ('¾', '3', '4')):
        ga, gb = G[a], G[b]
        sa = 0.52
        num = [('group', scaled(a, sa, 0, CAP - CAP * sa))]
        x_sl = ga.body * sa + 10
        den_x = x_sl + 240
        den = [('group', scaled(b, sa, den_x, 0))]
        make(ch, num + sl(x_sl) + den, 30, 30)


def S_pilcrow():
    t = 90 * GL.WKC                                  # QA 26/10: strokes follow the weight
    e = gw('bowl')                                   # R2c
    ops = [('add', rect(250 + e, DESC + 40, 250 + e + t, CAP)), ('add', rect(490 + e - t, DESC + 40, 490 + e, CAP)),
           ('add', rect(250 + e, CAP - t, 490 + e, CAP)),
           ('add', rrect(0, CAP - 420, 340 + e, CAP, (FULL, 0, 0, FULL)))]
    make('¶', ops, 40, 40)


def S_lowquotes():
    c = F._comma_ops()
    make('‚', c, 56, 40)
    make('„', c + shift_ops(F._comma_ops(), F.D + 50, 0), 56, 40)


def S_daggers():
    W = 420 + gw('one')                              # R2c
    k = GL.WKC                                       # QA 26/10: strokes follow the weight
    st = [('add', rect(W / 2 - 62 * k, DESC + 60, W / 2 + 62 * k, CAP))]
    make('†', st + [('add', fbar(0, CAP - 250, W, CAP - 250 + 110 * k, left=True, right=True))], 40, 40)
    make('‡', st + [('add', fbar(0, CAP - 250, W, CAP - 250 + 110 * k, left=True, right=True)),
                    ('add', fbar(0, 120, W, 120 + 110 * k, left=True, right=True))], 40, 40)


def S_bullet():
    r = 150 * (0.35 + 0.65 * GL.WKC)                 # QA 26/10: bullet follows the weight like the dots
    make('•', [('add', circle(r, F.MATH_Y, r))], 50 + 150 - r, 50 + 150 - r)


def S_perthousand():
    p = G['%']
    W = p.body
    ops = list(p.ops) + [('group', ring(W + 50, 0, W + 50 + 250 + 0.8 * gw('round'), 330, 92 * F.K_, 84 * F.K_, FULL, FULL))]
    make('‰', ops, p.lsb, p.rsb)


def S_single_guil():
    l = [(op, transform(c, lambda x, y: (x * 0.5, F.MATH_Y + (y - F.MATH_Y) * 0.62))) for op, c in F._chev(420 + 2 * gw('diag'), 480, 118 * F.K_)]
    make('‹', l, 40, 40)
    make('›', F.rot180_ops(l, 105 + gw('diag') / 2, F.MATH_Y), 40, 40)


def S_euro():
    c = G['C']
    ops = [('group', shift_ops(c.ops, 70, 0))]
    t = 96 * GL.WKC
    ops += [('add', fbar(0, 448 - t / 2, 380, 448 + t / 2, left=True, right=True)),
            ('add', fbar(0, 268 - t / 2, 380, 268 + t / 2, left=True, right=True))]
    make('€', ops, 20, c.rsb)


def S_trademark():
    s = 0.44
    t = scaled('T', s, 0, CAP - CAP * s)
    m = scaled('M', s, G['T'].body * s + 40, CAP - CAP * s)
    make('™', [('group', t), ('group', m)], 40, 40)


def build_latin1():
    for f in (L_Oslash, L_oslash, L_AE, L_ae, L_OE, L_oe, L_germandbls, L_Thorn, L_thorn, L_eth, L_mu,
              L_florin, S_misc, S_inverted, S_cent, S_sterling, S_currency, S_yen, S_brokenbar, S_section,
              S_copy_reg, S_ordinals, S_logicalnot, S_plusminus, S_superiors, S_fractions, S_pilcrow,
              S_lowquotes, S_daggers, S_bullet, S_perthousand, S_single_guil, S_euro, S_trademark):
        f()
    import latin_core_c as LC
    LC.build_core()
    G['Ð'] = G['Dcroat']
    G['­'] = G['-']
    return G


# ---------------------------------------------------------------- character set
def charset():
    cs = [chr(c) for c in range(0x20, 0x7F)]
    cs += [chr(c) for c in range(0xA0, 0x100)]
    cs += list('ŒœŠšŽžŸƒˆ˜ˇ˚–—‘’‚“”„†‡•…‰‹›€™−₫ĐđĂăƠơƯưĨĩŨũ')
    cs += list('ĆĈĔĜĞĤĬĴĹŃŎŔŚŜŬŴŶŹ')          # F15: the caps of the Latin-extended lowercase already in the font
    cs += ['\u202f', '\u2009']               # F16: French narrow no-break space, thin space (0.65 word space)
    cs += list('ĀĄĊČĎĒĖĘĚĠĢĦĪĮİĶĻĽŁŅŇŐŘŞŤŪŮŰŲŻȘȚẀẂẄẞ˘˙˛˝')   # GF Latin Core (28/10)
    vn = []
    for b in 'aăâeêioôơuưy':
        for t in ['', '́', '̀', '̉', '̃', '̣']:
            vn.append(unicodedata.normalize('NFC', b + t))
    vn += [c.upper() for c in vn]
    out = []
    for c in cs + vn:
        if c not in out:
            out.append(c)
    return out
