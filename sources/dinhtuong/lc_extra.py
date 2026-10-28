"""The lowercase letters composed from the capitals' marks (Latin-1 + GF Latin Core), shared by build96.py and the
Figma generators. Same code as build96.py's composer: extend(LO) adds them to a lowercase set."""
import unicodedata
import lcfont as LF
import glyphs_c as GL
import family as FM
from geo import Glyph

CAPS = LF.CAPS
LO = {}
EXTRA = 'äëïöüÿåçšž'


def from_caps(lo):
    cap = CAPS[lo.upper()]
    base = unicodedata.normalize('NFD', lo)[0]
    bg = LF.BASE['ı' if base == 'i' else base]
    g = Glyph('lc_uni%04X' % ord(lo), bg.body, bg.lsb, bg.rsb, ord(lo))
    g.ops = list(bg.ops); g.parts = [('base', list(bg.ops))]
    dx = bg.body / 2 - cap.body / 2
    for nm, ops in cap.parts[1:]:
        dy = -(LF.lcm.OV - GL.OV_C) if nm in ('cedilla', 'commabelow') else (LF.lcm.XH - GL.CAP)
        o = GL.shift_ops(ops, dx, dy)
        g.ops += o; g.parts.append((nm, o))
    FM._open_narrow(lo, g)                  # ï: the diaeresis overhangs the advance by <= 10 (caps Ï rule)
    return g



# GF Latin Core lowercase (28/10): marks from the capitals (F12: lowercase marks follow the caps), lowered to the x-height
CORE_FC = 'āċčēėěġīňőřūůűżẁẃẅķļņşșț'


def core_lc(c):
    import latin_core_c as LC
    lv, lh = LF.B.v, LF.B.h
    if c in 'ąęįų':                                # R8k: ogonek from the rightmost foot of the lowercase base
        bg = LF.BASE['ı' if c == 'į' else unicodedata.normalize('NFD', c)[0]]
        o = LC.ogonek_on(bg.ops, bg.body)
        nm = 'ogonek'
    elif c in 'ďľť':                               # R8m: vertical caron right of the stem, top on the stem's top
        b0 = unicodedata.normalize('NFD', c)[0]
        bg = LF.BASE[b0]
        xs_r = LC.ink_x_at(bg.ops, LF.lcm.ASC - 60, 'r') if b0 in 'dl' else LC.ink_x_at(bg.ops, LF.lcm.XH + 60, 'r')
        top = LF.lcm.ASC if b0 in 'dl' else LC.bounds(bg.ops)[3]
        o = LC.vcaron_on(xs_r, top)
        nm = 'vcaron'
    elif c == 'ģ':                                 # R8l: the comma turned above (no room under the g)
        bg = LF.BASE['g']
        o = GL.shift_ops(LC.mk_commaturned(), bg.body / 2, LF.ZONE)
        nm = 'commaturned'
    elif c == 'ł':                                 # R8n: the Ł slash at the lowercase horizontal (0.9 h)
        bg = LF.BASE['l']
        o = [LC.slash_bar(-60, lv + 110, 0.62 * LF.lcm.XH, 0.9 * lh)]
        nm = 'slash'
    elif c == 'ħ':                                 # R8o: the đ bar mirrored on the h's stem
        bg = LF.BASE['h']
        yb = max((LF.lcm.XH + LF.lcm.ASC) / 2 - lh * 0.45, LF.lcm.XH + getattr(LF.lcm, 'OV', 0) + 0.5 * 93)
        yb = min(yb, LF.lcm.ASC - 0.9 * lh - 40)
        o = [('add', GL.rect(-25, yb, lv + 120, yb + 0.9 * lh))]
        nm = 'bar'
    else:
        return None
    g = Glyph('lc_uni%04X' % ord(c), bg.body, bg.lsb, bg.rsb, ord(c))
    g.ops = list(bg.ops) + o; g.parts = [('base', list(bg.ops)), (nm, o)]
    b = LC.bounds(o)
    if b[2] > bg.body + bg.rsb - 20:              # a mark reaching past the advance widens it (ď ľ ť)
        g.rsb = b[2] - bg.body + 30
    if b[0] < -bg.lsb + 20:
        g.lsb = -b[0] + 30
    FM._open_narrow(c, g)
    return g


def extend(lo_set):
    for c in EXTRA + CORE_FC:
        lo_set[c] = from_caps(c)
    for c in 'ąęįųďľťģłħ':
        lo_set[c] = core_lc(c)
    lo_set['ȷ'] = LF.BASE['ȷ']
    return EXTRA + CORE_FC + 'ąęįųďľťģłħȷ'
