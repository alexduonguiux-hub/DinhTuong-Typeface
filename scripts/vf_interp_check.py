"""Variable font between the masters: every character at wght 400..700 (step 25) must grow steadily.
Fails on an ink area that shrinks anywhere, an area step far off the mean step (a collapse or a jump: a master pair
whose points do not correspond), or a bbox edge that does not move linearly between two masters (a step more than
JUMP units off that interval's mean step).
Usage: python3 scripts/vf_interp_check.py [fonts/variable/DinhTuong[wght].ttf]   (needs uharfbuzz)"""
import os
import sys

import uharfbuzz as hb
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'fonts', 'variable', 'DinhTuong[wght].ttf')
W = list(range(400, 701, 25))
JUMP = 3
MASTERS = (400, 500, 700)


class P:
    def __init__(s, *p): s.p = p
    def moveTo(s, a): [x.moveTo(a) for x in s.p]
    def lineTo(s, a): [x.lineTo(a) for x in s.p]
    def qCurveTo(s, *a): [x.qCurveTo(*a) for x in s.p]
    def curveTo(s, *a): [x.curveTo(*a) for x in s.p]
    def closePath(s): [x.closePath() for x in s.p]


def main():
    font = hb.Font(hb.Face(open(VF, 'rb').read()))
    cmap = TTFont(VF).getBestCmap()
    shrink, uneven, jumps, n = [], [], [], 0
    for u in sorted(cmap):
        gid = font.get_nominal_glyph(u)
        if gid is None:
            continue
        A, B = [], []
        for w in W:
            font.set_variations({'wght': w})
            ap, bp = AreaPen(), BoundsPen(None)
            font.draw_glyph_with_pen(gid, P(ap, bp))
            A.append(abs(ap.value)); B.append(bp.bounds)
        if not A[-1]:
            continue
        n += 1
        d = [b - a for a, b in zip(A, A[1:])]
        if any(x < -0.002 * A[-1] for x in d):
            shrink.append(chr(u))
        mean = (A[-1] - A[0]) / len(d)
        if mean > 0 and max(abs(d[i + 1] - d[i]) for i in range(len(d) - 1)) > 1.5 * mean:
            uneven.append(chr(u))
        bad = False
        for lo, hi in zip(MASTERS, MASTERS[1:]):
            idx = [i for i, w in enumerate(W) if lo <= w <= hi]
            seg = [B[i] for i in idx]
            if not all(seg):
                continue
            for e in range(4):
                st = [b[e] - a[e] for a, b in zip(seg, seg[1:])]
                m = (seg[-1][e] - seg[0][e]) / len(st)
                if any(abs(s - m) > JUMP for s in st):
                    bad = True
        if bad:
            jumps.append(chr(u))
    print(f'{n} characters at wght {W[0]}..{W[-1]} step {W[1] - W[0]}: area shrinks {len(shrink)} {"".join(shrink)} | '
          f'uneven steps {len(uneven)} {"".join(uneven)} | bbox not linear between masters (> {JUMP} u) {len(jumps)} {"".join(jumps)}')
    sys.exit(1 if shrink or uneven or jumps else 0)


if __name__ == '__main__':
    main()
