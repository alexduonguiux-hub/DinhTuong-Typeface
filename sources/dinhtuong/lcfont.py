"""DINHTUONG60s v0.96 draft — the lowercase proposal (lc96) joined to the built capitals.

* Marks are the CAPS marks, composed by the caps rules (R8 / R8d), only moved down to the
  lowercase zone: zone_lc = XH + (ZONE_UC - CAP). Same strips (300 × T), same circumflex /
  breve / tilde / hook, same offsets, same 'every sắc ends on one top line' rule
  (lowercase top = zone_lc + 300). On ă every tone rides ON TOP of the breve, exactly as Ắ.
* Kerning: kern_style.run() on caps + lowercase (refs HH / Hn / nn / nH), incl. the mark guard.

Usage: A2_WEIGHT=bold python3 lcfont.py  -> out/lc96/kern_lc96_<w>.json + glyph cache (pickle)
"""
import os, sys, json, pickle, unicodedata
import family as FM

W8 = os.environ.get('A2_WEIGHT', 'regular')
CAPS = FM.style_glyphs()                      # build the caps first (lc96 re-points concept globals)
import glyphs_c as GL
import marks_flat as MF
OPT = os.environ.get('LC_OPT', 'a')
import lc96
import importlib
lcm = lc96 if OPT == 'a' else importlib.import_module('lc96' + OPT)
from geo import Glyph

B = lcm.LC(W8)
GL.v = B.v                                    # the horn plate is sized by the lowercase stem
GL.OV_L = lcm.OV
ZONE = _ZONE_X = lcm.XH + (GL.ZONE_UC - GL.CAP)        # 578: the caps mark zone moved to the x-height
ACUTE_L = MF.ACUTE_L                         # v0.96c: one sắc length everywhere (= caps)
SY = GL.CAP_SCALE                             # caps offsets, unchanged
GAPS = GL.MARK_GAPS
TONES = {'́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde'}
CIRC, BREVE, HORN, DOTB = '̂', '̆', '̛', '̣'

BASE = {}
for gd in B.proposal():
    g = Glyph('lc_' + gd['name'], gd['body'], gd['lsb'], gd['rsb'], ord(gd['name']))
    g.ops = list(gd['ops'])
    BASE[gd['name']] = g
# dotless i: the i without its dot (marks replace the dot, as on İ/Í)
_i = BASE['i']
BASE['ı'] = Glyph('lc_dotlessi', _i.body, _i.lsb, _i.rsb, 0x131)
def _maxy(op):
    ys = [v for q in (op[1] if op[0] != 'group' else []) for v in q[2::2] if q[0] != 'Z']
    return max(ys) if ys else -1e9
BASE['ı'].ops = [op for op in _i.ops if op[0] == 'group' or _maxy(op) < lcm.XH + 20] if OPT not in ('a',) else [_i.ops[0]]
# dotless j (v0.966, 28/10: ĵ kept the j's dot under its circumflex): marks REPLACE the dot, as on ı
_j = BASE['j']
BASE['ȷ'] = Glyph('lc_dotlessj', _j.body, _j.lsb, _j.rsb, 0x237)
BASE['ȷ'].ops = [op for op in _j.ops if op[0] == 'group' or _maxy(op) < lcm.XH + 20]
_jdot = [op for op in _j.ops if op[0] != 'group' and _maxy(op) >= lcm.XH + 20]
_xs = [v for op in _jdot for q in op[1] if q[0] != 'Z' for v in q[1::2]]
J_AXIS = (min(_xs) + max(_xs)) / 2 if _xs else _j.body / 2      # the marks sit where the dot sat (on the stem)
# đ: the d with the caps Đ bar rule — a bar of h across the ascender, centred between x-height and ascender
_d = BASE['d']
dd = Glyph('lc_dcroat', _d.body, _d.lsb, _d.rsb + 10, 0x111)   # F13 (v0.962): bar 25 past the stem, rsb + 10 (was 50 / + 20): đĩ = đi
yb = max((lcm.XH + lcm.ASC) / 2 - B.h * 0.45, lcm.XH + getattr(lcm, 'OV', 0) + 0.5 * 93)   # QA: the bar clears the bowl by >= 0.5 h (Regular units)
yb = min(yb, lcm.ASC - 0.9 * B.h - 40)
dd.ops = list(_d.ops) + [('add', GL.rect(_d.body - B.v - 120, yb, _d.body + 25, yb + 0.9 * B.h))]
BASE['đ'] = dd
import flare                                  # R4b: every free end flares like the stems (diagonals, bar ends)
if os.environ.get('FLARE_ALL', '1') == '1':
    for _g in BASE.values():
        flare.apply(_g, (0, lcm.XH, lcm.ASC, lcm.DESC), B.fl)

# v0.962 Vietnamese kerning fixes (vn_fix.py): S1c caps spacing, S1i narrow caps keep I's sides, R8c2 horn reach
import vn_fix as VF
if os.environ.get('VN_FIX', '1') == '1':
    VF_NARROW = VF.narrow_caps(CAPS)
    VF_REACH = VF.caps_horn(CAPS)


def compose(ch):
    if ch in BASE:
        return BASE[ch]
    nfd = unicodedata.normalize('NFD', ch)
    base, marks = nfd[0], nfd[1:]
    top_marks = any(m in TONES or m in (CIRC, BREVE) for m in marks)
    bg = BASE['ı' if (base == 'i' and top_marks) else ('ȷ' if (base == 'j' and top_marks) else base)]
    g = Glyph('lc_uni%04X' % ord(ch), bg.body, bg.lsb, bg.rsb, ord(ch))
    g.ops = list(bg.ops); g.parts = [('base', list(bg.ops))]
    cx = J_AXIS if base == 'j' else bg.body / 2
    # v0.970 (mark QA: ĺ's sắc sat ON the l's ascender): a letter with an ascender carries its marks over the ascender
    ZONE = (lcm.ASC + (_ZONE_X - lcm.XH)) if base in 'bdhkl' else _ZONE_X
    h_ops = []
    if HORN in marks:
        if base == 'u' and os.environ.get('VN_FIX', '1') == '1':   # R8c2: reach = rsb(u) + lsb(n) - 26, advance unchanged
            h_ops = VF.horn_fit(bg.body, lcm.XH, False, BASE['u'].rsb + BASE['n'].lsb - VF.PAIR_MIN)
            g.ops += h_ops; g.parts[0] = ('base', g.parts[0][1] + h_ops)
        else:
            h_ops = MF.horn_ops(bg.body, lcm.XH, False, o_shape=(base == 'o'))
            g.ops += h_ops; g.parts[0] = ('base', g.parts[0][1] + h_ops)
            g.rsb += max(0, MF.horn_reach(False, base) - 44 * GL.WK)
    first = 'circumflex' if CIRC in marks else ('breve' if BREVE in marks else None)
    tone = next((TONES[m] for m in marks if m in TONES), None)
    top_h = 0
    if first == 'circumflex':                        # R8k: the mũ (and every tone on it) sits 40 over the letter's ink
        ZONE = ZONE + GL.CIRC_FOOT(bg.ops + h_ops, cx, ZONE, ('L', base, round(cx, 1)))
    if first:
        ops = GL.shift_ops(GL.mark_ops(first, True), cx, ZONE)
        g.ops += ops; g.parts.append((first, ops))
        top_h = GL.MARK_HGT[first] * SY
    if tone:
        ops = GL.mark_ops(tone, True)
        if base == 'i' and tone == 'tilde':
            ops = GL.scale_ops(ops, 0.8, 1.0)
        if first == 'circumflex' and tone in ('acute', 'hook'):        # caps: sắc / hỏi hang off the mũ's right shoulder
            dx, dy = GAPS['side'][tone]
            ops = GL.mark_ops(tone, True, ACUTE_L) if tone == 'acute' else GL.MARK_STACK_FN[tone]()
            if tone == 'acute':                                         # R8e: the tilted sắc keeps its foot (no touching the mũ)
                ops = GL.shift_ops(ops, GL.ACUTE_FOOT_DX(), 0)
            ydy = dy * SY
            if tone == 'acute' and GL.ACUTE_BESIDE():                  # R8g: sắc beside the mũ on the mark zone (ấ = á)
                ops = GL.mark_ops('acute', True, ACUTE_L)
                ydy, dx = 0, GL.ACUTE_BESIDE_DX(True)
            elif tone == 'acute' and GL.ACUTE_MODE() in ('4', '5'):    # R8i: centred over the mũ
                ops = GL.mark_ops('acute', True)
                dx = GL.ACUTE_IN_DX(GL.ACUTE_R8I_LC_DX, bg.ops, cx)        # R8k-b behind the mũ, R8k-c inside the letter
                ydy = GL.ACUTE_CIRC_Y(False, dx)                            # 40 from the mũ
            elif tone == 'acute' and GL.ACUTE_TOPLINE():               # R8f trial: ấ's sắc ends on ắ's line
                ydy = GL.ACUTE_STACK_Y()
                dx = GL.ACUTE_CIRC_DX(dx, ydy, True)                   # R8f: pulled left to 40 from the mũ
            ops = GL.shift_ops(ops, cx + dx, ZONE + ydy)
            if tone == 'hook' and MF.R8I():                            # R8k: hỏi beside the new mũ keeps 40 from it
                ops = GL.CLEAR_UP(ops, [o for nm, o2 in g.parts if nm == 'circumflex' for o in o2], MF.CIRC_R8K_GAP)
        elif first:                                                    # caps: on trăng (and huyền / ngã on mũ) the tone rides on top
            y0 = (ZONE + GL.ACUTE_STACK_Y()) if (tone == 'acute' and first == 'breve' and GL.ACUTE_TOPLINE()) else ZONE + top_h + GAPS['stack_gap'] * SY
            if tone == 'acute':
                ops = GL.mark_ops('acute', True, ACUTE_L)
            elif tone in GL.MARK_STACK_FN:
                ops = GL.MARK_STACK_FN[tone]()
            if tone == 'acute':
                ops = GL.shift_ops(ops, GL.ACUTE_FOOT_DX(), 0)
            ops = GL.shift_ops(ops, cx, y0)
        else:
            hx = GL._horn_clear(ops, h_ops, cx, ZONE) if (HORN in marks and base == 'o') else 0
            adv = bg.lsb + bg.body + bg.rsb
            if tone == 'grave' and adv - 40 < MF.STRIP_L and os.environ.get('GRAVE_FULL', '1') != '1':   # caps Ì rule (off since R8h: huyền full length on ì)
                ops = GL.mark_ops('grave', True, adv - 40)
            ops = GL.shift_ops(ops, cx + hx, ZONE)
        g.ops += ops; g.parts.append((tone, ops))
    if DOTB in marks:
        adv = bg.lsb + bg.body + bg.rsb
        db = MF.mk_dotbelow(length=min(MF.STRIP_L, adv - 40))
        ops = GL.shift_ops(db, cx, -52 if base != 'y' else lcm.DESC - 40)
        g.ops += ops; g.parts.append(('dotbelow', ops))
    return g


_TUNED = []
S1E_RO = 1.48   # S1e: ro white / nn white at 0.30 x-height depth (median of Inter, Liberation, Calibri, Poppins, DejaVu R/B)


def tune_spacing(rounds=3, k=0.85):
    """S1b (28/10 02:44 'kerning oxo, vex, owo hơi xa' / 02:45 'wave, hay, xe cũng bị xa'): spacing first,
    kerning second. Each lowercase side is set so that the optical white between it and an n equals
    T x the white of n|n, where the white is measured row by row over the x-height band with each glyph's
    profile clamped at depth D = 0.41 x (n|n white) FROM ITS OWN OUTERMOST INK (not from the advance edge), and
    T is the median of the same measure on Inter, Liberation Sans, DejaVu Sans, Carlito and Poppins
    (spacing_targets.json; rounds ~1.0, diagonals ~0.93). The old S1 clamped at 40u from the advance edge,
    so a straight side (sb > 40) always read 'full' and every round or diagonal side was opened until it
    did too: oo 1.29, ox 1.25, on 1.12 x nn (references 0.9-1.0). The n keeps its sides; i l keep theirs.
    Composed letters inherit the sides of their base. Runs once per process."""
    if _TUNED or os.environ.get('LC_TUNE', '1') != '1':
        return
    import kern, json as _json
    import numpy as _np
    T = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spacing_targets.json')))
    D = None                                                     # set from n|n below: 0.41 x the n|n white
    sl = kern.band_rows(0, lcm.XH)

    def white(a, b):
        nonlocal D
        lA, rA, aA = kern.mask(a); lB, rB, aB = kern.mask(b)
        ra, lb = rA[sl], lB[sl]
        ra = _np.where(_np.isnan(ra), -1e9, ra); lb = _np.where(_np.isnan(lb), 1e9, lb)
        ra = _np.maximum(ra, _np.nanmax(rA[sl]) - D); lb = _np.minimum(lb, _np.nanmin(lB[sl]) + D)
        return float(_np.mean(aA - ra + lb))
    n = BASE['n']
    import width as _WD
    if _WD.WID < 1.0:
        # C8 (vf-condensed-concept-v1): the Condensed sidebearings are x SSB (0.85 at 80 %) of Normal. n, i, l keep
        # their own sides (everything else is solved against n|n below), so they are the ones scaled here.
        for c in 'nil':
            if c in BASE:
                BASE[c].lsb *= _WD.SSB; BASE[c].rsb *= _WD.SSB
    names = [c for c in 'abcdefghjkmopqrstuvwxyzđı' if c in BASE]
    log = {}
    if os.environ.get('S1B', '1') != '1':                         # the v0.967 measure (40u from the advance edge)
        depth0, kern.DEPTH = kern.DEPTH, 40
        for _ in range(rounds):
            kern.MASK.clear()
            ref = kern.gaps(n, n, 0, lcm.XH).mean()
            for c in names:
                g = BASE[c]
                g.lsb = max(4, g.lsb + k * (ref - kern.gaps(n, g, 0, lcm.XH).mean()))
                g.rsb = max(4, g.rsb + k * (ref - kern.gaps(g, n, 0, lcm.XH).mean()))
                kern.MASK.pop(g.name, None)
        kern.DEPTH = depth0
    else:
        kern.MASK.clear()
        OFF = os.environ.get('S1C', '1') == '1'
        if OFF:
            # S1c (28/10 02:54 'kerning chữ xa nữa'): the depth is an OPTICAL size, 0.12 x-height (60 px at x-height
            # 500, as measured on the references), and each side's target is the references' white OFFSET from n|n in
            # x-height units (spacing_offsets.json: o ~0, v -0.017, a-left +0.011), not a ratio of n|n. A ratio
            # carries the references' looser n|n (0.29 x-height; ours 0.19) into every round and diagonal.
            T = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spacing_offsets.json')))
            D = 0.12 * lcm.XH
        else:
            D = 1e9
            D = 0.41 * white(n, n)      # S1b: the references' depth / n|n ratio
        ref = white(n, n)
        SB_MIN = float(os.environ.get('SB_MIN', '0'))   # no ink past the advance edge
        for c in names:
            g = BASE[c]
            key = {'đ': 'd', 'ı': 'i'}.get(c, c)
            tl, tr = T.get(key, (0.0, 0.0) if OFF else (1.0, 1.0))
            gl, gr = (ref + tl * lcm.XH, ref + tr * lcm.XH) if OFF else (tl * ref, tr * ref)
            for _ in range(2):                                    # the measure is linear in the side bearing
                g.lsb = max(SB_MIN, g.lsb + (gl - white(n, g)))
                kern.MASK.pop(g.name, None)
                g.rsb = max(SB_MIN, g.rsb + (gr - white(g, n)))
                kern.MASK.pop(g.name, None)
        if OFF and os.environ.get('S1E', '1') == '1' and 'r' in BASE and 'o' in BASE:
            # S1e (28/10 14:23 'kerning "zon" "ron" hơi lỏng'): the 0.12 x-height depth of S1c sees only the arm of r,
            # not the white UNDER it. Measured deep (0.30 x-height, white / nn white): ro 1.70 Regular / 1.52 Bold, the
            # loosest of every reference (Inter 1.43, Liberation 1.58, DejaVu 1.13, Calibri 1.42, Poppins 1.54).
            # r's right side is set so that ro (deep) = the references' median 1.48 x nn.
            D0 = D
            D = 0.30 * lcm.XH
            rr, oo = BASE['r'], BASE['o']
            for _ in range(2):
                kern.MASK.pop(rr.name, None)
                rr.rsb = max(SB_MIN - 40, rr.rsb + (S1E_RO * white(n, n) - white(rr, oo)))
            kern.MASK.pop(rr.name, None)
            D = D0
    kern.MASK.clear()
    for c in names:
        log[c] = (round(BASE[c].lsb), round(BASE[c].rsb))
    _TUNED.append(log)


def _a_levels(a):
    """bowl centre and hood centre of the a (from its stem op: the stem runs from 0 to the hood centre + 1)."""
    st = a.ops[1][1][1][1]
    ys = [q[i] for q in st if q[0] != 'Z' for i in range(2, len(q), 2)]
    ytop = max(ys) - 1
    yb = 0.62 * lcm.XH
    return (yb - lcm.OV) / 2, ytop


def lig_lc():
    """F14 (28/10 03:20, French: 'cœur', 'sœur', 'ex-æquo'): æ œ ø as true lowercase, built from the lowercase's own
    parts (R7b): æ = the whole a + the whole e, the e's left wall laid over the a's stem (3u overlap, no coincident
    edges), so the stem is shared; œ = o + e the same way (one shared wall); ø = o + a slash at the caps Ø's rule
    (0.62 of the diagonal stroke, parallel edges, level cuts 56u past baseline and x-height). Sides: left of the first
    letter, right of the last (both already spaced by S1c)."""
    from geo import diag_dx
    a, e, o = BASE['a'], BASE['e'], BASE['o']
    v = B.v
    out = {}
    AE = os.environ.get('AE_LIG', 'B')
    for ch, first, cp in (('æ', a, 0xE6), ('œ', o, 0x153)):
        fops = list(first.ops)
        sh = first.body - v + 3
        if ch == 'æ' and AE != 'A':
            # F14b (28/10 03:3x, references Inter / Helvetica / DejaVu / Calibri: a double-storey a drops its stem in
            # æ): the a keeps its hood and its bowl; the e's left wall is the shared stroke they both run into.
            hood, bowl = fops[0], fops[1]
            fops = [hood, ('group', [op for i, op in enumerate(bowl[1]) if i != 1])] + fops[2:]
            # the hood's lower end (cut level on its centre line) and the bowl's top meet the e's wall through the
            # part of the old stem that lies BETWEEN them (bowl centre -> hood centre): no step at the hood's foot
            yb_c, yh_c = _a_levels(first)
            fops.append(('add', GL.rect(first.body - v, yb_c, first.body - 0.5 * v, yh_c + 1)))
            sh = first.body - v * float(os.environ.get('AE_SH', '1.0')) + 3
        g = Glyph('lc_uni%04X' % cp, sh + e.body, first.lsb, e.rsb, cp)
        g.ops = [('group', fops), ('group', GL.shift_ops(e.ops, sh, 0))]
        out[ch] = g
    W = o.body
    dw = diag_dx(round(v * 0.90) * 0.62, W, lcm.XH + 112)
    g = Glyph('lc_oslash', W, o.lsb, o.rsb, 0xF8)
    ex = float(os.environ.get('OS_EX', '30'))             # F14c: the slash passes the o's overshoot by ex (refs 0-0.07 x-height)
    y0, y1 = -lcm.OV - ex, lcm.XH + lcm.OV + ex
    dw = diag_dx(round(v * 0.90) * 0.62, W, y1 - y0)
    g.ops = list(o.ops) + [('add', GL.poly([(-18, y0), (-18 + dw, y0), (W + 18, y1), (W + 18 - dw, y1)]))]
    out['ø'] = g
    return out


def lowercase_set():
    tune_spacing()
    if not getattr(lowercase_set, '_sb', False):             # S1d: the lone straight letters (see glyphs_c.NARROW_SB)
        for c in 'ilı':
            if c in BASE:
                BASE[c].lsb += GL.NARROW_SB; BASE[c].rsb += GL.NARROW_SB
        lowercase_set._sb = True
    out = {}
    for c in 'abcdefghijklmnopqrstuvwxyzđ':
        out[c] = compose(c)
    VN = set(TONES) | {CIRC, BREVE, HORN, DOTB}
    for cp in list(range(0xC0, 0x180)) + [0x1A1, 0x1B0] + list(range(0x1EA0, 0x1EFA)):   # QA: ơ ư sit outside Latin-1/Ext-A
        lo = chr(cp)
        nfd = unicodedata.normalize('NFD', lo)
        if lo.islower() and nfd[0] in BASE and len(nfd) > 1 and set(nfd[1:]) <= VN:
            out[lo] = compose(lo)
    if os.environ.get('LIG_LC', '1') == '1':
        out.update(lig_lc())
    return out


if __name__ == '__main__':
    import kern_style
    LO = lowercase_set()
    G = dict(CAPS); G.update(LO)
    FM.style_glyphs = lambda: G               # kern_style measures this combined set
    import kern
    import numpy as np
    import math as _m
    _ak = kern.autokern

    def W(a, b, y0, y1, Dc):
        """S2 white between a and b, row by row, the COMBINED gap clamped at Dc: unlike a per-side clamp it
        does not split into 'a's side + b's side', so what is left after removing each letter's own
        spacing is the pair's interaction (an arm over a bowl, two diagonals, a round under a hook)."""
        lA, rA, aA = kern.mask(a); lB, rB, aB = kern.mask(b)
        sl = kern.band_rows(y0, y1)
        g = (aA - rA[sl]) + lB[sl]
        g = np.where(np.isnan(g), Dc, np.minimum(g, Dc))
        return g.mean()

    def _ak_lc(G_, A_, B_, ref):
        out = {}
        for a in A_:
            for b in B_:
                fig = (a.isdigit() or b.isdigit()) and a.isalnum() and b.isalnum()   # figure + punctuation keeps the old path
                if not fig and (not (b.islower() and (a.isupper() or a.islower())) or a not in G_ or b not in G_):
                    out.update(_ak(G_, [a], [b], ref)); continue
                ga, gb = G_[a], G_[b]
                y0, y1 = 0, lcm.XH
                if fig:                              # R16: figures are set like capitals; kern only the interaction
                    na = G_['n'] if a.islower() else G_['H']     # each side against its own neutral straight letter
                    nb = G_['n'] if b.islower() else G_['H']
                    y0, y1 = 0, (lcm.XH if (a.islower() or b.islower()) else GL.CAP)
                    Dc = 150
                    k = 0.7 * (W(ga, nb, y0, y1, Dc) + W(na, gb, y0, y1, Dc) - W(na, nb, y0, y1, Dc) - W(ga, gb, y0, y1, Dc))
                    k = min(k, 0)
                    thr = 15
                elif a.isupper():                      # caps | lowercase: against H | b (b's own spacing removed)
                    Dc = 300
                    k = 0.55 * (W(G_['H'], gb, y0, y1, Dc) - W(ga, gb, y0, y1, Dc))   # the arm is above the x-height: tuck in only half way
                    thr = 20
                elif HORN in unicodedata.normalize('NFD', a):   # S4 (12:19 'ư ơ hơi xa'): a horned letter is set
                    # as close as its plain base (u, o) would be: the horn may hang over the next letter
                    Dc = 150
                    base = unicodedata.normalize('NFC', unicodedata.normalize('NFD', a).replace(HORN, ''))
                    gbase = G_[base] if base in G_ else compose(base)
                    k = 1.0 * (W(gbase, gb, y0, y1, Dc) - W(ga, gb, y0, y1, Dc))   # the full difference: same white as the base
                    k = min(k, 0) if k > -1e9 and W(ga, gb, y0, y1, Dc) >= W(gbase, gb, y0, y1, Dc) - 10 else k   # v0.967: a horn that
                    # crowds the next letter (ớt: the horn over t's flared bar) opens the pair back to the base's white
                    thr = 10
                else:                                # lowercase | lowercase: the interaction only
                    Dc = 150
                    n = G_['n']
                    k = 0.7 * (W(ga, n, y0, y1, Dc) + W(n, gb, y0, y1, Dc) - W(n, n, y0, y1, Dc) - W(ga, gb, y0, y1, Dc))
                    k = min(k, 0)                    # a clamp artefact never opens a pair; only a collision does (below)
                    thr = 15
                clear = kern.raw_gap(ga, gb, -300, 1100)
                k = max(k, kern.MIN_CLEAR - clear) if clear < 9000 else k
                k = int(round(k / 5.0)) * 5
                k = max(-150, min(40, k))
                if abs(k) >= thr:
                    out[a + b] = k
        return out
    kern.autokern = _ak_lc
    kern_style.kern.autokern = _ak_lc
    FM.WEIGHT = 'lc96' + ('' if OPT == 'a' else OPT) + '_' + W8                   # -> kern_lc96_<w>.json (never the shipping kern file)
    out = kern_style.run()
    # S3 (QA 'không dính nét'): every pair that can meet in Vietnamese text (not two toned vowels side by side)
    # keeps >= PAIR_MIN of white between the inks, kerning included
    import kern, json as _json, math as _m
    PAIR_MIN = 26
    TONEM = set('\u0301\u0300\u0309\u0303\u0323')
    toned = lambda c: bool(set(unicodedata.normalize('NFD', c)[1:]) & TONEM)
    kfile = f"kern_{'lc96' + ('' if OPT == 'a' else OPT)}_{W8}.json"
    KJ = _json.load(open(kfile))
    def kv(a, b):
        if a + b in KJ['exceptions']:
            return KJ['exceptions'][a + b]
        return KJ['pairs'].get(kern_style.kclassL(a) + kern_style.kclass(b), 0)
    kern.MASK.clear()
    letters = [c for c in G if len(c) == 1 and c.isalpha()]
    # S5 (12:37 'kerning tiếng Việt'): a horned letter (ư Ư ơ Ơ and their toned forms) before a lowercase letter is
    # set so that the optical white over baseline..x-height+horn equals the same pair WITHOUT the horn (ưn = un,
    # ươ = uo). The horn is part of the letter, not a floating mark: it may hang over the next letter down to the
    # letter-to-letter clearance (PAIR_MIN), not the mark clearance kern_style applies.
    def Wb(a_, b_, k_, y1, Dc=150):
        lA, rA, aA = kern.mask(a_); lB, rB, aB = kern.mask(b_)
        sl = kern.band_rows(0, y1)
        g_ = (aA - rA[sl]) + lB[sl] + k_
        g_ = np.where(np.isnan(g_), Dc, np.minimum(g_, Dc))
        return float(g_.mean())
    # S5b: the same rule for EVERY Vietnamese letter (horn, tilde/hook/acute that widens the advance, dot below):
    # the pair must keep the white of its unmarked base pair (Ĩn = In, đĩ = đi, ưn = un), never closer than PAIR_MIN.
    base0 = lambda c: unicodedata.normalize('NFD', c)[0]
    marked = [c for c in letters if base0(c) != c]
    lows = [c for c in letters if c.islower()]
    cand = set()
    for a in marked:
        for b in lows:
            cand.add((a, b))
    for b in [c for c in marked if c.islower()]:
        for a in letters:
            cand.add((a, b))
    nh = 0
    top = lcm.XH + 120
    for a, b in sorted(cand):
        if toned(a) and toned(b):
            continue
        ba, bb = base0(a), base0(b)
        if ba not in G or bb not in G:
            continue
        target = Wb(G[ba], G[bb], kv(ba, bb), top)
        k = kv(a, b)
        for _ in range(6):                      # solve white(a, b, k) = target (the clamp makes it non-linear)
            k += target - Wb(G[a], G[b], k, top)
        k = min(k, max(kv(a, b), kv(ba, bb)))   # never open a pair wider than both its own class and its base
        gap = kern.raw_gap(G[a], G[b], -400, 1240, k)
        if gap < PAIR_MIN:
            k += PAIR_MIN - gap
            k = int(_m.ceil(k / 5.0)) * 5          # QA: rounding must never take a pair back under PAIR_MIN
        else:
            k = int(round(k / 5.0)) * 5
            if kern.raw_gap(G[a], G[b], -400, 1240, k) < PAIR_MIN:
                k += 5
        if k != kv(a, b):
            KJ['exceptions'][a + b] = k
            nh += 1
    print('mark pairs set', nh)
    added = 0
    for a in letters:
        for b in letters:
            if (b.isupper() and a.islower()) or (toned(a) and toned(b)):
                continue
            k = kv(a, b)
            gap = kern.raw_gap(G[a], G[b], -400, 1240, k)
            if gap < PAIR_MIN:
                KJ['exceptions'][a + b] = int(_m.ceil((k + PAIR_MIN - gap) / 5.0)) * 5
                added += 1
    _json.dump(KJ, open(kfile, 'w'), ensure_ascii=False, indent=0)
    print('collision guard: exceptions added', added)
    os.makedirs('out/lc96', exist_ok=True)
    tag = 'lc96' + ('' if OPT == 'a' else OPT)
    os.replace(f'kern_{tag}_{W8}.json', f'out/lc96/kern_{tag}_{W8}.json')
    pickle.dump({'lo': {k: (g.name, g.body, g.lsb, g.rsb, g.ops) for k, g in LO.items()}},
                open(f'out/lc96/lo_{tag}_{W8}.pkl', 'wb'))
    print(W8, 'lowercase', len(LO))
