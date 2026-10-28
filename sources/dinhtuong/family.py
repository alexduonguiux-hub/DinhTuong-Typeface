"""DIZAI Chợ Lớn — family builder (one style per process: A2_WEIGHT + A2_ITALIC env vars).

style_glyphs() -> ordered {char: Glyph} for the full charset, already slanted for italics.
Italic = slanted roman (concept: a sign-painter's lean, not a cursive hand):
  * 10° shear about the x-height middle (y = XH/2) so spacing stays balanced left/right,
  * marks are composed upright and slanted with their base (they follow the letter's axis),
  * kerning is re-measured on the slanted shapes.
"""
import os, math, unicodedata
import glyphs_c as GL
import latin1_c as L1
from geo import Glyph

WEIGHT = GL.WEIGHT
ITALIC = os.environ.get('A2_ITALIC', '0') == '1'
ANGLE = 10.0
T = math.tan(math.radians(ANGLE))
YC = GL.XH / 2
WCLASS = {'regular': 400, 'medium': 500, 'bold': 700}[WEIGHT]
STYLE = {'regular': 'Regular', 'medium': 'Medium', 'bold': 'Bold'}[WEIGHT]
if ITALIC:
    STYLE = 'Italic' if WEIGHT == 'regular' else STYLE + ' Italic'

EXTRA = ['ı']                                 # dotless i (Turkish + built-in for i-marks)
COMBINING = ['̀', '́', '̂', '̃', '̄', '̆', '̈', '̉', '̊', '̌', '̛', '̣', '̧', '\u0307', '\u030b', '\u0326', '\u0328']   # + GF Latin Core


def slant(ops):
    if not ITALIC:
        return ops
    return L1.tf_ops(ops, lambda x, y: (x + (y - YC) * T, y))


_built = False


def build():
    global _built
    if not _built:
        import concept_port as CP
        CP.pre(); GL.build_all(); CP.post(); GL.build_vn(); CP.figs(); L1.build_latin1(); _built = True


def comb_mark(m):
    """zero-width combining mark, drawn over a virtual lowercase o centred at x = -250."""
    up = False
    if m == '̛':
        ops = GL.horn_ops(-250 + GL.G['o'].body / 2 - 8, GL.XH, False)
    elif m == '̣':
        ops = GL.shift_ops(GL.mk_dotbelow(), -250, -52)
    elif m == '̧':
        ops = GL.shift_ops(L1.mk_cedilla(), -250, 0)
    elif m in ('\u0307', '\u030b'):
        import latin_core_c as LC
        ops = GL.shift_ops(LC.mk_dotabove(up) if m == '\u0307' else LC.mk_dblacute(up), -250, GL.ZONE_LC)
    elif m == '\u0326':
        import latin_core_c as LC
        ops = GL.shift_ops(LC.mk_commabelow(), -250, 0)
    elif m == '\u0328':
        import latin_core_c as LC
        og = LC.mk_ogonek(); b = L1.bounds(og)
        ops = GL.shift_ops(og, -250 + 60 - b[0], 0)
    elif m in L1.NEW_TOP:
        ops = GL.shift_ops(L1.NEW_TOP[m](up), -250, GL.ZONE_LC)
    else:
        name = {'̀': 'grave', '́': 'acute', '̂': 'circumflex', '̃': 'tilde', '̆': 'breve', '̉': 'hook'}[m]
        ops = GL.shift_ops(GL.mark_ops(name, up), -250, GL.ZONE_LC)
    g = Glyph('comb%04X' % ord(m), 0, 0, 0, ord(m))
    g.ops = ops
    return g


NARROW = set('iıIjJl')
MAX_OVERHANG = 10           # a mark may overhang the advance by at most this (units)


def _open_narrow(ch, g):
    """i-family with wide marks (î ï ĩ Ï Î ...): open the sidebearings so the mark overhangs the
    advance by <= MAX_OVERHANG instead of crashing into the neighbour (spacing, not kerning)."""
    d = unicodedata.normalize('NFD', ch)
    if len(d) < 2 or d[0] not in NARROW or not hasattr(g, 'parts'):
        return
    xs = []
    for name, ops in g.parts[1:]:
        b = L1.bounds(ops)
        if b: xs += [b[0], b[2]]
    if not xs:
        return
    over_l = -min(xs) - g.lsb            # how far the mark reaches past the left edge
    over_r = max(xs) - (g.body + g.rsb)
    if over_l > MAX_OVERHANG: g.lsb += over_l - MAX_OVERHANG
    if over_r > MAX_OVERHANG: g.rsb += over_r - MAX_OVERHANG


CAPS_ONLY = os.environ.get('A2_CAPS', '1') == '1'      # v0.95 DINHTUONG60s: capitals only
CASE_ALIAS = {}          # lowercase code point -> capital glyph (cmap), filled by _caps_only
CASE_MULTI = {'ß': 'SS'}  # one code point -> several capitals (GSUB ccmp)


def _caps_only(out):
    """Caps-only edition: every lowercase letter with a one-letter capital is typed AS that capital
    (cmap alias, no lowercase outline left in the font); ß is kept as a slot drawn as S and
    expanded to S S by ccmp. µ and ƒ are symbols here (no Latin capital) and stay."""
    CASE_ALIAS.clear()
    for ch in list(out):
        if len(ch) != 1 or not ch.islower() or ch in CASE_MULTI:
            continue
        up = ch.upper()
        if len(up) == 1 and up != ch and up in out:
            CASE_ALIAS[ch] = up
            del out[ch]
    for ch, seq in CASE_MULTI.items():
        if ch in out:
            s = out[seq[0]]
            g = Glyph(out[ch].name, s.body, s.lsb, s.rsb, ord(ch)); g.ops = s.ops
            out[ch] = g


def style_glyphs():
    build()
    import flare                                  # R4b: every free end flares like the stems (diagonals, bar ends)
    if os.environ.get('FLARE_ALL', '1') == '1':
        for g in list(GL.G.values()):
            u = getattr(g, 'unicode', None)
            if u and unicodedata.category(chr(u)) in ('Sk', 'Mn', 'Lm'):
                continue                          # spacing / combining marks keep the mark system's cuts
            flare.apply(g, (0, GL.CAP), GL.FL)
    out = {}
    for ch in L1.charset() + EXTRA:
        g = GL.G['dotlessi'] if ch == 'ı' else L1.compose(ch)
        out[ch] = g
    for m in COMBINING:
        out[m] = comb_mark(m)
    for ch, g in out.items():
        _open_narrow(ch, g)
    if os.environ.get('FIG_SPACE', '1') == '1':
        import fig_space                          # R16: every figure side leaves the 0's optical white
        fig_space.apply(out)
    # tabular figures (tnum): every figure on the advance of the zero, ink centred
    tab = out['0'].advance
    import booleng
    for d in '0123456789':
        g = out[d]
        xs = [s[i] for c in booleng.evaluate(g.ops) for s in c for i in range(1, len(s), 2)]
        x0, x1 = min(xs), max(xs)                     # centre the INK (3's body box is wider than its ink)
        lsb = (tab - (x1 - x0)) / 2 - x0
        t = Glyph(g.name + '.tf', g.body, lsb, tab - g.body - lsb, None)
        t.ops = g.ops
        out[d + '.tf'] = t
    if CAPS_ONLY:
        _caps_only(out)
    if ITALIC:
        sl = {}
        for ch, g in out.items():
            n = Glyph(g.name, g.body, g.lsb, g.rsb, g.unicode)
            n.ops = slant(g.ops)
            if hasattr(g, 'parts'):
                n.parts = [(a, slant(b)) for a, b in g.parts]
            sl[ch] = n
        out = sl
    return out
