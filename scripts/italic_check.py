#!/usr/bin/env python3
"""Italic checks (scripts/make_italic.py).
R-I6  collisions: every pair of letters, figures and punctuation, shaped with kerning (HarfBuzz), keeps an ink gap
      >= 26 u on every scanline (the generator's collision floor, the S3 guard) wherever the upright pair does;
      pairs that fall under the floor only in the italic are listed.
Usage: python3 scripts/italic_check.py [--fix]   (needs uharfbuzz)
  --fix  writes sources/italic-kern.json: for every such pair, the glyph-pair kerning that restores the floor (the
         pair's current value + the shortfall, rounded up to 5 like the generator's guard); scripts/make_italic.py puts
         these pairs at the head of the italic masters' kern lookup. Re-run make_italic + the build after a fix."""
import math
import os
import sys
import unicodedata

import uharfbuzz as hb
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAIRS = [('Regular', 'Italic'), ('Medium', 'MediumItalic'), ('Bold', 'BoldItalic')]
FLOOR = 26
STEP = 6
ANG = math.radians(10)


def profiles(path):
    """glyph name -> {ybin: (xmin, xmax)} of the ink (outline edges crossed at each scanline)."""
    f = TTFont(path); gs = f.getGlyphSet(); out = {}
    for g in f.getGlyphOrder():
        rec = RecordingPen(); gs[g].draw(rec)
        segs = []; cur = None; start = None
        for op, a in rec.value:
            if op == 'moveTo': cur = start = a[0]
            elif op == 'lineTo': segs.append((cur, a[0])); cur = a[0]
            elif op == 'qCurveTo':
                pts = [cur] + list(a)
                # implied on-curve points
                on = [pts[0]]; ctrl = []
                for i in range(1, len(pts) - 1):
                    c = pts[i]; n = pts[i + 1]
                    if i < len(pts) - 2: n = ((c[0] + n[0]) / 2, (c[1] + n[1]) / 2)
                    p0 = on[-1]
                    for k in range(1, 9):
                        t = k / 8
                        q = ((1-t)**2*p0[0] + 2*(1-t)*t*c[0] + t*t*n[0], (1-t)**2*p0[1] + 2*(1-t)*t*c[1] + t*t*n[1])
                        segs.append((cur, q)); cur = q
                    on.append(n)
            elif op == 'curveTo':
                p0 = cur; b, c, d = a
                for k in range(1, 13):
                    t = k / 12
                    q = ((1-t)**3*p0[0] + 3*(1-t)**2*t*b[0] + 3*(1-t)*t*t*c[0] + t**3*d[0],
                         (1-t)**3*p0[1] + 3*(1-t)**2*t*b[1] + 3*(1-t)*t*t*c[1] + t**3*d[1])
                    segs.append((cur, q)); cur = q
            elif op in ('closePath', 'endPath'):
                if cur is not None and start is not None and cur != start: segs.append((cur, start))
                cur = start
        prof = {}
        for (x0, y0), (x1, y1) in segs:
            lo, hi = sorted((y0, y1))
            for yb in range(int(math.ceil(lo / STEP)), int(math.floor(hi / STEP)) + 1):
                y = yb * STEP
                if y1 == y0: xs = [x0, x1]
                else: xs = [x0 + (x1 - x0) * (y - y0) / (y1 - y0)]
                a_, b_ = prof.get(yb, (1e9, -1e9))
                prof[yb] = (min(a_, *xs), max(b_, *xs))
        out[g] = prof
    return f, out


def gaps(path, chars):
    f, prof = profiles(path)
    hf = hb.Font(hb.Face(open(path, 'rb').read()))
    order = f.getGlyphOrder()
    res = {}
    for a in chars:
        for b in chars:
            buf = hb.Buffer(); buf.add_str(a + b); buf.guess_segment_properties(); hb.shape(hf, buf, {'kern': True})
            inf, pos = buf.glyph_infos, buf.glyph_positions
            if len(inf) != 2: continue
            ga, gb = order[inf[0].codepoint], order[inf[1].codepoint]
            off = pos[0].x_advance + pos[1].x_offset - pos[0].x_offset
            pa, pb = prof[ga], prof[gb]
            g = min((pb[y][0] + off - pa[y][1] for y in pa if y in pb), default=None)
            if g is not None:
                kern = pos[0].x_advance - hf.get_glyph_h_advance(inf[0].codepoint)
                res[a + b] = (g, ga, gb, kern)
    return res


def main():
    cm = TTFont(f'{ROOT}/fonts/ttf/DinhTuong-Regular.ttf').getBestCmap()
    vn = set('aăâbcdđeêghiklmnoôơpqrstuưvxyfjwzAĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXYFJWZ')
    vn |= {unicodedata.normalize('NFC', b + m) for b in 'aăâeêioôơuưyAĂÂEÊIOÔƠUƯY' for m in '\u0300\u0301\u0309\u0303\u0323'}
    chars = sorted(c for c in vn | set('0123456789.,:;!?()[]{}/&@#%"\'-–—«»') if ord(c) in cm)
    import json
    fix = '--fix' in sys.argv
    kj = f'{ROOT}/sources/italic-kern.json'
    out = json.load(open(kj)) if (fix and os.path.exists(kj)) else {}
    bad_all = 0
    for up, it in PAIRS:
        gu = gaps(f'{ROOT}/fonts/ttf/DinhTuong-{up}.ttf', chars)
        gi = gaps(f'{ROOT}/fonts/ttf/DinhTuong-{it}.ttf', chars)
        new = sorted(((gi[p][0], p, gu[p][0] if p in gu else None) for p in gi if gi[p][0] < FLOOR and (gu[p][0] if p in gu else -1e9) >= FLOOR))
        bad_all += len(new)
        if fix:
            d = out.setdefault(up, {})
            for g, p, u in new:
                _, ga, gb, kern = gi[p]
                need = kern + (FLOOR - g)
                v = int(math.ceil(need / 5.0) * 5)
                key = f'{ga} {gb}'
                d[key] = max(v, d.get(key, v))
        print(f'{it}: {len(gi)} pairs · italic gap < {FLOOR} where the upright keeps it: {len(new)}',
              ' '.join(f'{p}:{round(g)}(up {round(u)})' for g, p, u in new[:60]))
    if fix:
        json.dump(out, open(kj, 'w'), indent=0, sort_keys=True)
        print('wrote', kj, {k: len(v) for k, v in out.items()})
    sys.exit(1 if bad_all else 0)


if __name__ == '__main__':
    main()
