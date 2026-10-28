"""Vietnamese kerning audit v2 (27/10, sources: Trương 'Vietnamese Typography', Glyphs 'Kerning', Kern On manual,
TypeDrawers 'FAQ: Vietnamese'). Every adjacent pair inside every Vietnamese syllable, in THREE casings
(lowercase, Capitalised, ALL CAPS — signage is set in caps), kerning applied:
  CLOSE    nearest ink (marks, horns, descenders) < 26 u                         [collision; Trương: marks never touch]
  UNEVEN   optical white differs from the same pair WITHOUT marks/horn > 12 u   [ưn = un, ƯT = UT, ất = at]
           (+ = looser than its base pair: Trương's 'ƯT gap as wide as a word space')
  OVERKERN |k| > 40 % of the narrower glyph's advance                            [Glyphs: never > 40 %]
and on the whole kerning table:
  NEUTRAL  straight sides (H I | left of n h m r b k l | right of d q) must kern 0 [Kern On: neutral sides]
  NEGONLY  glyph sides whose every pair is negative (spacing too loose)          [Kern On]
Usage: LC_OPT=f A2_WEIGHT=<w> python3 kqa_vn.py  -> out/lc96/kqa_vn_<w>.json"""
import json, unicodedata, collections, os
import numpy as np
import lcfont as LF
import kern_style as KS
import kern
import vnkern_syl as VS

w = LF.W8
LO = LF.lowercase_set()
G = dict(LF.CAPS); G.update(LO)
K = json.load(open(f"out/lc96/kern_lc96f_{w}.json"))
XH, CAP = LF.lcm.XH, 700
TOL, MIN_GAP, DC = 12, 26, 150


def kv(a, b):
    if a + b in K['exceptions']:
        return K['exceptions'][a + b]
    return K['pairs'].get(KS.kclassL(a) + KS.kclass(b), 0)


def white(a, b, k, y1):
    lA, rA, aA = kern.mask(a); lB, rB, aB = kern.mask(b)
    sl = kern.band_rows(0, y1)
    g = (aA - rA[sl]) + lB[sl] + k
    g = np.where(np.isnan(g), DC, np.minimum(g, DC))
    return float(g.mean())


def base(c):
    d = unicodedata.normalize('NFD', c)
    return d[0]


syl = VS.syllables()
casings = {'lower': syl, 'Cap': {s[0].upper() + s[1:] for s in syl}, 'CAPS': {s.upper() for s in syl}}
res = {'weight': w}
kern.MASK.clear()
seen = {}
for cs, words in casings.items():
    pairs = collections.Counter()
    for s in words:
        for i in range(len(s) - 1):
            pairs[s[i:i + 2]] += 1
    close, uneven, over = [], [], []
    for p, n in pairs.items():
        a, b = p
        if a not in G or b not in G:
            continue
        k = kv(a, b)
        if p not in seen:
            seen[p] = kern.raw_gap(G[a], G[b], -400, 1240, k)
        gap = seen[p]
        if gap < MIN_GAP:
            close.append((p, k, round(gap), n))
        adv = min(G[a].advance, G[b].advance)
        if abs(k) > 0.4 * adv:
            over.append((p, k, round(adv)))
        ba, bb = base(a), base(b)
        if (ba, bb) != (a, b) and ba in G and bb in G:
            top = (CAP + 120) if (a.isupper() and b.isupper()) else (XH + 120)
            d = white(G[a], G[b], k, top) - white(G[ba], G[bb], kv(ba, bb), top)
            if abs(d) > TOL:
                uneven.append((p, ba + bb, k, kv(ba, bb), round(d), n))
    uneven.sort(key=lambda r: -abs(r[4]) * r[5] ** 0.5)
    res[cs] = {'pairs': len(pairs), 'close': close, 'overkern': over, 'uneven_n': len(uneven),
               'uneven_loose': sum(1 for u in uneven if u[4] > 0), 'uneven_tight': sum(1 for u in uneven if u[4] < 0),
               'uneven': uneven[:80]}

# table-wide checks
NEUT_L = set('HIhnmrbkl')     # left sides that are straight stems
NEUT_R = set('HIdq')          # right sides that are straight stems
neutral = []
for a in G:
    for b in G:
        if len(a) != 1 or len(b) != 1 or not (a.isalpha() and b.isalpha()):
            continue
        if b in NEUT_L and a in NEUT_R and kv(a, b):
            neutral.append((a + b, kv(a, b)))
sides = collections.defaultdict(list)
for p, v in K['pairs'].items():
    sides['L:' + p[0]].append(v); sides['R:' + p[1]].append(v)
negonly = sorted(s for s, vs in sides.items() if len(vs) >= 6 and all(v < 0 for v in vs))
res['neutral_nonzero'] = neutral
res['negative_only_sides'] = negonly
res['table'] = {'class_pairs': len(K['pairs']), 'exceptions': len(K['exceptions'])}
os.makedirs('out/lc96', exist_ok=True)
json.dump(res, open(f'out/lc96/kqa_vn_{w}.json', 'w'), ensure_ascii=False, indent=1)
for cs in casings:
    r = res[cs]
    print(w, cs, 'pairs', r['pairs'], 'close', len(r['close']), 'overkern', len(r['overkern']),
          'uneven', r['uneven_n'], '(loose', r['uneven_loose'], 'tight', r['uneven_tight'], ')')
print(w, 'neutral nonzero', len(neutral), 'negative-only sides', negonly)
