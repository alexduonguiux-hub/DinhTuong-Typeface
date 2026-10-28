"""K3 reference envelope (28/10 15:41 'kiểm tra lại kerning của tất cả các cặp chữ' -> 'sửa theo luật').

For every base pair (A-Z a-z 0-9 . , : ; ! ? - ' " ( ) & /, not punctuation + punctuation) of the BUILT font:
  d   = (optical white of the pair - optical white of its reference pair) / x-height
        optical white = mean over the shared band (x-height band when a lowercase is involved, else cap band) of the
        distance between the two profiles, each clamped at depth 0.30 x-height from its own extreme;
        reference pair = nn (lc lc), HH (caps / punctuation), Hn / nH (mixed), 00 (figures)
  [lo, hi] = the same measure in Inter, Liberation, DejaVu, Carlito, Poppins, Regular and Bold
  tight (d < lo - TOL): open by (lo - d) x-height
  loose (d > hi + TOL): close by (d - hi) x-height, but never below the ink floor (26)
The result is the ABSOLUTE kerning of that pair's class pair (or of its exception), written to k3_<w>.json and
applied by build96.py. Values are absolute, so re-running on a K3 build is stable.
Usage: A2_WEIGHT=<w> python3 k3_gen.py [font dir=out/v096]"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

W8 = os.environ.get('A2_WEIGHT', 'regular')
STY = {'regular': 'Regular', 'medium': 'Medium', 'bold': 'Bold'}[W8]
FD = sys.argv[1] if len(sys.argv) > 1 else 'out/v096'
TOL, FLOOR = 0.02, 26
REFS = [('/usr/share/fonts/opentype/inter/Inter-Regular.otf', '/usr/share/fonts/opentype/inter/Inter-Bold.otf'),
        ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        ('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf', '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'),
        ('/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf', '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf')]
BASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?-\'"()&/'
S, Y0, H = 1000, 1300, 1800


class F:
    def __init__(s, path):
        s.f = ImageFont.truetype(path, S, layout_engine=ImageFont.Layout.RAQM)
        t = TTFont(path); sc = S / t['head'].unitsPerEm; o = t['OS/2']
        s.xh = -s.f.getbbox('x', anchor='ls')[1]; s.cap = -s.f.getbbox('H', anchor='ls')[1]   # measured (DejaVu has no OS/2 x-height)
        s.prof, s.adv = {}, {}
    def p(s, ch):
        if ch not in s.prof:
            im = Image.new('L', (1600, H), 0)
            ImageDraw.Draw(im).text((300, Y0), ch, font=s.f, fill=255, anchor='ls')
            a = np.array(im) > 127; has = a.any(1)
            L = np.where(has, a.argmax(1) - 300, np.nan); R = np.where(has, a.shape[1] - a[:, ::-1].argmax(1) - 300, np.nan)
            s.prof[ch] = (L.astype(float), R.astype(float)); s.adv[ch] = s.f.getlength(ch)
        return s.prof[ch]
    def k(s, a, b): return s.f.getlength(a + b) - s.f.getlength(a) - s.f.getlength(b)
    def gap(s, a, b, k):
        La, Ra = s.p(a); Lb, Rb = s.p(b)
        g = s.adv[a] + k - Ra + Lb; g = g[~np.isnan(g)]
        return float(g.min()) if len(g) else 9999.0
    def white(s, a, b, band, k):
        La, Ra = s.p(a); Lb, Rb = s.p(b)
        sl = slice(int(Y0 - band[1]), int(Y0 - band[0])); dep = 0.30 * s.xh
        ra, lb = Ra[sl], Lb[sl]
        if np.all(np.isnan(ra)) or np.all(np.isnan(lb)): return None
        ma, mb = np.nanmax(ra), np.nanmin(lb)
        rc = np.where(np.isnan(ra), ma - dep, np.maximum(ra, ma - dep))
        lc = np.where(np.isnan(lb), mb + dep, np.minimum(lb, mb + dep))
        return float(np.mean(s.adv[a] + k - rc + lc))


kind = lambda c: 'f' if c.isdigit() else (('u' if c.isupper() else 'l') if c.isalpha() else 'p')


def band(fo, a, b):
    return (0, fo.xh) if 'l' in (kind(a), kind(b)) else (0, fo.cap)


def norm(a, b):
    ka, kb = kind(a), kind(b)
    if ka == 'l' and kb == 'l': return 'nn'
    if kb == 'l': return 'Hn'
    if ka == 'l': return 'nH'
    if ka == 'f' and kb == 'f': return '00'
    return 'HH'


def delta(fo, a, b, k=None):
    k = fo.k(a, b) if k is None else k
    w = fo.white(a, b, band(fo, a, b), k); n = norm(a, b)
    wn = fo.white(n[0], n[1], band(fo, n[0], n[1]), fo.k(n[0], n[1]))
    return None if w is None or wn is None else (w - wn) / fo.xh


def main():
    fo = F(f'{FD}/DINHTUONG60s-{STY}.otf')
    K = json.load(open(f'{FD}/kern_v096_{W8}.json'))
    cls = lambda side, ch: next((c for c, m in K[side].items() if ch in m), ch)
    refs = [F(p) for pair in REFS for p in pair]
    PREV = json.load(open(f'k3_{W8}.json')) if os.path.exists(f'k3_{W8}.json') and os.environ.get('K3_FRESH') != '1' else {}
    out = {'pairs': dict(PREV.get('pairs', {})), 'exceptions': dict(PREV.get('exceptions', {})), 'sides': {}}   # cumulative
    need = {}                                               # pair -> (s units, k0, d, lo, hi)
    for a in BASE:
        for b in BASE:
            if kind(a) == 'p' and kind(b) == 'p':
                continue
            d = delta(fo, a, b)
            rv = [v for v in (delta(r, a, b) for r in refs) if v is not None]
            if d is None or not rv:
                continue
            lo, hi = min(rv), max(rv)
            k0 = fo.k(a, b); g0 = fo.gap(a, b, k0)
            s = 0.0
            if d < lo - TOL:
                s = (lo - d) * fo.xh                      # open to the tightest reference
            elif d > hi + TOL:
                s = -min((d - hi) * fo.xh, max(0.0, g0 - FLOOR))   # close to the loosest reference, ink floor wins
            need[a + b] = (s, k0, d, lo, hi)
    # S1f: when MOST pairs on one side of a glyph need the same correction, it is that side's spacing, not kerning:
    # the side moves by the median correction over all its letter / figure partners (zeros included).
    AN = [c for c in BASE if kind(c) != 'p']
    sideR, sideL = {}, {}
    for x in BASE:
        r = [need.get(x + y, (0,))[0] for y in AN if x + y in need]
        l = [need.get(y + x, (0,))[0] for y in AN if y + x in need]
        mr = float(np.median(r)) if r else 0.0
        ml = float(np.median(l)) if l else 0.0
        # only an UNKERNED side is a spacing fault (E + X is kerned in by autokern: that stays a kerning fix)
        if r and np.median([abs(need[x + y][1]) for y in AN if x + y in need]) >= 5: mr = 0.0
        if l and np.median([abs(need[y + x][1]) for y in AN if y + x in need]) >= 5: ml = 0.0
        if abs(mr) >= 10: sideR[x] = int(round(mr / 5.0)) * 5
        if abs(ml) >= 10: sideL[x] = int(round(ml / 5.0)) * 5
    prev = json.load(open(f'k3_{W8}.json')).get('sides', {}) if os.path.exists(f'k3_{W8}.json') and os.environ.get('K3_FRESH') != '1' else {}
    for x in set(sideR) | set(sideL) | set(prev):      # sides are cumulative: the build already carries the previous shift
        pl, pr_ = prev.get(x, [0, 0])
        out['sides'][x] = [pl + sideL.get(x, 0), pr_ + sideR.get(x, 0)]
    log = []
    for pr, (s, k0, d, lo, hi) in need.items():
        a, b = pr[0], pr[1]
        res = s - sideR.get(a, 0) - sideL.get(b, 0)
        dd = d + (sideR.get(a, 0) + sideL.get(b, 0)) / fo.xh
        if lo - TOL <= dd <= hi + TOL and abs(res) < 10:
            continue
        if abs(res) < 5:
            continue
        k1 = int(round((k0 + res) / 5.0)) * 5
        if k1 == round(k0):
            continue
        if a + b in K['exceptions']:
            out['exceptions'][a + b] = k1
        else:
            out['pairs'][cls('classesL', a) + cls('classesR', b)] = k1
        log.append((pr, round(d, 3), round(lo, 3), round(hi, 3), round(k0), k1))
    json.dump(out, open(f'k3_{W8}.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(log, open(f'out/k3_{W8}_log.json', 'w'), ensure_ascii=False)
    print(W8, 'S1f sides', out['sides'])
    print(W8, 'K3 pair changes', len(log), 'open', sum(1 for x in log if x[5] > x[4]), 'close', sum(1 for x in log if x[5] < x[4]))


if __name__ == '__main__':
    main()
