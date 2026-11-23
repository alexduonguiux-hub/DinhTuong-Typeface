"""A1 (1.010, QA alignment): a level edge that stands within 1.5 u of a guideline sits ON it.

With the narrower heavier capitals (W2) the M's flared stem tops and its diagonals met at y 699.x in Bold / Extra Bold,
so its whole top edge was written at 699 (qa_alignment: 'level points within 2 u of a guideline but not on it').
Rule: an on-curve point whose segment to a neighbour is level (both on-curve, same y) and whose y lies within
SNAP of the baseline, the x-height or the cap height is moved onto that line, with its level neighbour. Only level
runs move, so no curve changes shape; a point already on a guideline is left alone. Idempotent.

Usage: python3 snap_levels.py Regular.ufo Medium.ufo Bold.ufo ExtraBold.ufo
"""
import sys

import ufoLib2

LINES = (0, 530, 700)
SNAP = 1.5


def snap_glyph(g):
    """moves each level run (consecutive on-curve points at one y) within SNAP of a guideline onto it - BOTH ends,
    so the run stays level"""
    moved = 0
    for c in g.contours:
        pts = c.points
        n = len(pts)
        for i, p in enumerate(pts):
            q = pts[(i + 1) % n]
            if p.type is None or q.type is None or abs(p.y - q.y) > 0.01:
                continue
            for line in LINES:
                if 0 < abs(p.y - line) <= SNAP:
                    p.y = q.y = line
                    moved += 2
                    break
    return moved


if __name__ == '__main__':
    for path in sys.argv[1:]:
        f = ufoLib2.Font.open(path)
        hits = {}
        for g in f:
            m = snap_glyph(g)
            if m:
                hits[g.name] = m
        f.save()
        print(path.rsplit('/', 1)[-1], 'A1 level points onto guidelines:', sum(hits.values()), ' '.join(sorted(hits)))
