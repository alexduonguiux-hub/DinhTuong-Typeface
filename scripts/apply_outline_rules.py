#!/usr/bin/env python3
"""1.004: apply the outline rules R-axis, R-colinear, R-absorb, R-micro2 and R-g1 (sources/dinhtuong/outline_clean.py) to the UFO masters as
they stand, so only the points those rules target move and every other glyph stays exactly as released.
The generator applies the same rules in outline_clean.clean() to every new build.

Usage: python3 scripts/apply_outline_rules.py <changed.json> Regular.ufo Medium.ufo Bold.ufo
Writes the UFOs in place and the per-weight list of changed glyphs to changed.json.
"""
import json
import os
import sys

import ufoLib2
from ufoLib2.objects import Contour, Point

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sources', 'dinhtuong'))
import outline_clean as oc  # noqa: E402


def to_segs(contour):
    pts = list(contour.points)
    on = [i for i, p in enumerate(pts) if p.type]
    if not on or pts[on[0]].type == 'move':
        return None                                   # open contour: leave it
    n = len(pts)
    start = on[0]
    order = pts[start:] + pts[:start]
    segs, cur, pend = [], (float(order[0].x), float(order[0].y)), []
    for p in order[1:] + [order[0]]:
        if p.type is None:
            pend.append((float(p.x), float(p.y)))
            continue
        q = (float(p.x), float(p.y))
        if p.type == 'line':
            segs.append(['L', cur, q])
        elif p.type == 'curve' and len(pend) == 2:
            segs.append(['C', cur, pend[0], pend[1], q])
        else:
            return None                               # quadratic / unusual: leave it
        cur, pend = q, []
    smooth = {(float(p.x), float(p.y)) for p in pts if p.type and p.smooth}
    return segs, smooth


def from_segs(segs, smooth):
    pts = []
    for s in segs:
        if s[0] == 'L':
            x, y = s[2]; pts.append(Point(x, y, 'line', smooth=(x, y) in smooth))
        else:
            (a, b), (c, d), (x, y) = s[2], s[3], s[4]
            pts += [Point(a, b), Point(c, d), Point(x, y, 'curve', smooth=(x, y) in smooth)]
    # the last segment ends on the contour's original first point: put it back in front (same start, same order)
    return Contour(points=[pts[-1]] + pts[:-1])


def norm(v):
    return int(v) if float(v).is_integer() else v


def rules(segs):
    segs = oc._snap_axis(segs)
    segs = oc._merge_collinear(segs)
    segs = oc._merge_near_colinear(segs)
    segs = oc._absorb_micro(segs)
    segs = oc._absorb_any(segs)
    segs = [[s[0]] + [(float(round(q[0])), float(round(q[1]))) for q in s[1:]] for s in segs]   # the grid the font stores: kinks show there
    segs = oc._g1_kinks(segs)
    segs = [[s[0]] + [(float(round(q[0])), float(round(q[1]))) for q in s[1:]] for s in segs]
    return segs


def apply(font):
    changed = []
    for g in font:
        new, touched = [], False
        for c in g.contours:
            r = to_segs(c)
            if r is None:
                new.append(c); continue
            segs, smooth = r
            before = [list(s) for s in segs]
            for _ in range(6):                        # to a fixed point: removing one micro step can expose the next
                prev_round = [list(s) for s in segs]
                segs = rules(segs)
                if segs == prev_round:
                    break
            if segs != before:
                touched = True
                nc = from_segs(segs, smooth)
                for p in nc.points:
                    p.x, p.y = norm(p.x), norm(p.y)
                new.append(nc)
            else:
                new.append(c)
        if touched:
            g.contours.clear()
            for c in new:
                g.contours.append(c)
            changed.append(g.name)
    return sorted(changed)


if __name__ == '__main__':
    out, ufos = sys.argv[1], sys.argv[2:]
    res = {}
    for path in ufos:
        f = ufoLib2.Font.open(path)
        res[os.path.basename(path).split('-')[-1].split('.')[0]] = ch = apply(f)
        f.save(overwrite=True)
        print(path, len(ch), 'glyphs:', ' '.join(ch))
    json.dump(res, open(out, 'w'), indent=1)
