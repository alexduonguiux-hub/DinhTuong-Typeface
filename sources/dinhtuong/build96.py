"""DINHTUONG60s v0.96 release build: capitals v0.95 (marks v0.96c) + lowercase F, one font per weight.

  A2_WEIGHT=<w> python3 build96.py  ->  out/v096/DINHTUONG60s-<W>.otf / .ttf / .woff2

* Lowercase = lcfont.lowercase_set() (option F, spacing S1, Vietnamese marks R8/R8d lowered to the x-height, F12).
* Latin-1 / Ext-A lowercase that the Vietnamese composer does not cover (ä ë ï ö ü ÿ å ç š ž, ı) are composed by the
  SAME rule: the capital's own mark (diaeresis, ring, caron, cedilla), moved to the lowercase base:
  centred on the base, top marks lowered by XH − CAP (the caps mark zone moved to the x-height, F12).
* æ œ ø (lcfont F14) and þ ð ß (lc_extra R17-R19, v1.001) are true lowercase; nothing is typed as its capital any more,
  and the caps-only ccmp ß -> S S is gone.
* Kerning = out/lc96/kern_lc96f_<w>.json; the new letters join their base letter's class, then the S3 collision
  guard (ink gap >= 26 after kerning) is re-run for every pair that contains one of them.
"""
import os, sys, json, math, unicodedata
os.environ.setdefault('LC_OPT', 'f')
import lcfont as LF
import family as FM
import glyphs_c as GL
import kern, kern_style
import build_otf as BO
from geo import Glyph

W8 = LF.W8
STYLE = {'regular': 'Regular', 'medium': 'Medium', 'bold': 'Bold'}[W8]
OUTD = os.environ.get('OUTD') or os.path.join(BO.OUT, 'v096')
os.makedirs(OUTD, exist_ok=True)
PAIR_MIN = 26

CAPS = LF.CAPS
LO = LF.lowercase_set()
LO['ı'] = LF.BASE['ı']
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


for c in EXTRA:
    LO[c] = from_caps(c)

# GF Latin Core lowercase (28/10): marks from the capitals (F12: lowercase marks follow the caps), lowered to the x-height
CORE_FC = 'āċčēėěġīňőřūůűżẁẃẅķļņşșț'
for c in CORE_FC:
    LO[c] = from_caps(c)


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


for c in 'ąęįųďľťģłħ':
    LO[c] = core_lc(c)
LO['ȷ'] = LF.BASE['ȷ']
EXTRA = EXTRA + CORE_FC + 'ąęįųďľťģłħȷ'

# R17-R19 (v1.001, 29/10 'ß -> SS'): þ ð ß drawn from the lowercase modules (lc_extra), sides from the tuned base
# letters (þ = p's, ð = o's, ß = h's left / b's right), free ends flared like every lowercase letter (R4b)
import lc_extra as LX
import flare
LX_SIDES = {'þ': ('p', 'p'), 'ð': ('o', 'o'), 'ß': ('h', 'b')}
for ch, fn in (('þ', LX.g_thorn), ('ð', LX.g_eth), ('ß', LX.g_germandbls)):
    gd = fn(LF.B)
    sl, sr = LX_SIDES[ch]
    g = Glyph('lc_uni%04X' % ord(ch), gd['body'], LF.BASE[sl].lsb, LF.BASE[sr].rsb, ord(ch))
    g.ops = list(gd['ops'])
    if os.environ.get('FLARE_ALL', '1') == '1':
        flare.apply(g, (0, LF.lcm.XH, LF.lcm.ASC, LF.lcm.DESC), LF.B.fl)
    LO[ch] = g
FM.CASE_MULTI.clear()                    # R19: ß is its own letter: no ccmp ß -> S S
G = dict(CAPS); G.update(LO)


def seq_acute(seq, base, ref, ref_base, y_probe):
    """R8p (fontspector shape_languages, Dutch 'ÍJ́ íj́'): J́ / j́ = the J / dotless j with the house acute of Í / í, its
    axis moved from the I / ı stem centre onto the J / j stem centre (measured on the ink at y_probe)."""
    import latin_core_c as LC
    bg, rg = G[base], G[ref]
    acute = [o for nm, o in rg.parts if nm == 'acute'][0]
    rb = G[ref_base]
    c_ref = (LC.ink_x_at(rb.ops, y_probe, 'l') + LC.ink_x_at(rb.ops, y_probe, 'r')) / 2
    c_j = (LC.ink_x_at(bg.ops, y_probe, 'l') + LC.ink_x_at(bg.ops, y_probe, 'r')) / 2
    o = GL.shift_ops(acute, c_j - c_ref, 0)
    g = Glyph(seq, bg.body, bg.lsb, bg.rsb, None)
    g.ops = list(bg.ops) + o; g.parts = [('base', list(bg.ops)), ('acute', o)]
    b = __import__('latin_core_c').bounds(o)
    if b[0] < -bg.lsb + 20:
        g.lsb = -b[0] + 20
    G[seq] = g


seq_acute('J\u0301', 'J', 'Í', 'I', GL.CAP - 20)
seq_acute('j\u0301', 'ȷ', 'í', 'ı', LF.lcm.XH - 20)
for lo in list(FM.CASE_ALIAS):
    if lo in G:
        del FM.CASE_ALIAS[lo]
ALIASED = ''.join(sorted(FM.CASE_ALIAS))

# ---- kerning: lc96f + new letters in their base classes + collision guard
K = json.load(open(os.path.join(BO.OUT, 'lc96', f'kern_lc96f_{W8}.json')))
NEWK = {c: {'ı': 'i', 'ł': 'l', 'ħ': 'h', 'ȷ': 'j'}.get(c, unicodedata.normalize('NFD', c)[0]) for c in EXTRA + 'ı'}
for c, b in NEWK.items():
    for side, fn in (('classesL', kern_style.kclassL), ('classesR', kern_style.kclass)):
        cls = fn(b)
        if cls in K[side]:
            if c not in K[side][cls]:
                K[side][cls].append(c)
        elif b in K[side]:
            K[side][b].append(c)


for c, (sl, sr) in LX_SIDES.items():    # R17-R19: each side kerns with the base letter whose side it copies
    NEWK[c] = sl
    for side, fn, b in (('classesL', kern_style.kclassL, sr), ('classesR', kern_style.kclass, sl)):
        cls = fn(b)
        tgt = cls if cls in K[side] else b
        K[side].setdefault(tgt, [b])                 # a base letter without a class gets one (b p): its pairs keep their key
        if c not in K[side][tgt]:
            K[side][tgt].append(c)


def cls_of(side, ch):
    for k, mem in K[side].items():
        if ch in mem:
            return k
    return ch


def kv(a, b):
    if a + b in K['exceptions']:
        return K['exceptions'][a + b]
    return K['pairs'].get(cls_of('classesL', a) + cls_of('classesR', b), 0)


TONEM = set('̣́̀̉̃')
toned = lambda c: bool(set(unicodedata.normalize('NFD', c)[1:]) & TONEM)
kern.MASK.clear()
letters = [c for c in G if len(c) == 1 and c.isalpha()]
added = 0

# K3 (28/10 15:41 'kiểm tra lại kerning của tất cả các cặp chữ'; designer chose 'sửa theo luật'): reference envelope.
# Every base pair (A-Z a-z 0-9 . , : ; ! ? - ' " ( ) & /) is measured as optical white minus its reference pair
# (nn / HH / Hn / 00), in x-heights, against Inter, Liberation, DejaVu, Carlito and Poppins (Regular + Bold):
# never tighter than the tightest reference; never looser than the loosest unless the ink floor (26) holds it open.
# The values (absolute kerning per class pair / exception) are solved from the built font by k3_gen.py.
K3F = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'k3_{W8}.json')
if os.environ.get('K3', '1') == '1' and os.path.exists(K3F):
    K3 = json.load(open(K3F))
    for key, v in K3.get('pairs', {}).items():
        K['pairs'][key] = v
        aL, bR = key[0], key[1:]
        for la in K['classesL'].get(aL, [aL]):                 # an exception may not stay tighter than its new class value
            for rb in K['classesR'].get(bR, [bR]):
                if la + rb in K['exceptions'] and K['exceptions'][la + rb] < v:
                    K['exceptions'][la + rb] = v
    for pr, v in K3.get('exceptions', {}).items():
        K['exceptions'][pr] = v
    # S1f: a side that (unkerned) is outside the references for MOST partners moves as spacing, on the base glyph and
    # every member of its class (accented forms keep the base's spacing)
    done_ids = set()
    for x, (dl, dr) in K3.get('sides', {}).items():
        for c, g in G.items():
            if len(c) != 1 or id(g) in done_ids:
                continue
            hit = False
            if dl and kern_style.kclass(c) == x:
                g.lsb += dl; hit = True
            if dr and kern_style.kclassL(c) == x:
                g.rsb += dr; hit = True
            if hit:
                done_ids.add(id(g))
    kern.MASK.clear()
    print('S1f sides', K3.get('sides', {}))
    print('K3 pairs', len(K3.get('pairs', {})), 'exceptions', len(K3.get('exceptions', {})))

# S3b (28/10 full pair audit): the collision guard covers EVERY pair that can occur in text: letters, figures and
# punctuation, lowercase before a capital too (kA, kV, mA, McD), & ( ) / quotes, not only pairs with a new letter.
# Skipped: two toned letters side by side (never in Vietnamese), punctuation with punctuation.
PUNCT_G = [c for c in '&()[]{}/\\\'"‘’“”.,:;!?¿¡«»‹›-–—*@#%' if c in G]
FIGS = [c for c in G if len(c) == 1 and c.isdigit()]
pool = letters + FIGS + PUNCT_G
added3 = 0
for a in pool:
    for b in pool:
        if toned(a) and toned(b):
            continue
        if a in PUNCT_G and b in PUNCT_G:
            continue
        k = kv(a, b)
        gap = kern.raw_gap(G[a], G[b], -400, 1240, k)
        if gap < PAIR_MIN:
            K['exceptions'][a + b] = int(math.ceil((k + PAIR_MIN - gap) / 5.0)) * 5
            added3 += 1
print('S3b guard: pairs', len(pool) ** 2, 'exceptions added', added3)
for n in NEWK:
    for a, b in [(n, x) for x in letters] + [(x, n) for x in letters]:
        if (b.isupper() and a.islower()) or (toned(a) and toned(b)):
            continue
        k = kv(a, b)
        gap = kern.raw_gap(G[a], G[b], -400, 1240, k)
        if gap < PAIR_MIN:
            K['exceptions'][a + b] = int(math.ceil((k + PAIR_MIN - gap) / 5.0)) * 5
            added += 1
kf = os.path.join(OUTD, f'kern_v096_{W8}.json')
json.dump(K, open(kf, 'w'), ensure_ascii=False, indent=0)
print('new letters', len(NEWK), 'collision exceptions added', added)

# ---- compile
FM.style_glyphs = lambda: G
BO.VERSION = os.environ.get('REL', '0.961')   # 0.961: s = caps S construction (F7s)
BO.FAM_WIN_DESC = 330                     # ỵ: nặng under the y tail reaches -299 / -310 / -321 (R / M / B); line spacing (typo/hhea -250) unchanged
BO.OUT = OUTD
BO.DESCRIPTION = ('DINHTUONG60s — chữ khuôn thép đúc của biển hiệu, biển cổng Sài Gòn thập niên 1960. '
                  'Chữ hoa và chữ thường, hỗ trợ tiếng Việt đầy đủ, dấu vẽ cùng nét với chữ.')
p, yy = BO.build(kf)
from fontTools.ttLib import TTFont
f = TTFont(p); f['head'].fontRevision = float(BO.VERSION); f.save(p)
import otf2ttf
ttf = p[:-4] + '.ttf'
otf2ttf.convert(p, ttf)
try:
    w2 = TTFont(ttf); w2.flavor = 'woff2'; w2.save(p[:-4] + '.woff2')
except ImportError as e:                    # brotli not installed: WOFF2 skipped (OTF / TTF unaffected)
    print('woff2 skipped:', e)
print(STYLE, 'glyphs', len(G), 'lowercase', len(LO), 'still typed as caps:', ALIASED, 'ymin/ymax', [round(v) for v in yy])
