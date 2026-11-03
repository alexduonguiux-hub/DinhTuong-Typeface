#!/usr/bin/env python3
"""A1 (1.004): guideline audit on the UFO masters, the design points (not the TTF conversion).

Font Bakery's outline_alignment_miss runs on the TTF, where cu2qu adds on-curve points on every curve that runs
close to a guideline (flares leaving a cut line, bowl curves near the baseline), and where marks and joins placed by
other rules land near a guideline by coincidence. This audit checks what can actually be wrong: a point where the
outline runs LEVEL (either end of a horizontal straight edge, or a round's extreme) that lies 0 < |dy| <= 2 units from the
baseline, x-height, cap height, ascender or descender. Marks are not aligned to guidelines and are left out: spacing /
combining mark glyphs, quotes (placed from the cap height), in composites every component but the base letter, and in
decomposed letters every contour that lies wholly in a mark zone (above the x-height / cap height, or below the
baseline).

Usage: python3 scripts/qa_alignment.py sources/ufo/DinhTuong-Regular.ufo ...   (exit 1 when anything is found)
"""
import sys
import unicodedata

import ufoLib2
from fontTools.pens.recordingPen import RecordingPen

TOL = 2.0


def is_mark(glyph):
    for u in glyph.unicodes:
        if unicodedata.category(chr(u)) in ('Mn', 'Sk', 'Lm', 'Pi', 'Pf'):   # marks; quotes sit on the cap line
            return True
    return glyph.name.endswith('comb') or glyph.name.endswith('.case')


def contours(font, glyph):
    rec = RecordingPen()
    dx = dy = 0.0
    g = glyph
    while g.components and not g.contours:               # follow the base chain (ẩ -> â -> a): marks are left out
        base = g.components[0]
        dx += base.transformation[4]; dy += base.transformation[5]
        g = font[base.baseGlyph]
    if g.components:                                     # a base that mixes contours and components: its own contours
        for c in g.contours:
            c.draw(rec)
    else:
        g.draw(rec)
    rec = [(op, [(p[0] + dx, p[1] + dy) for p in a]) for op, a in rec.value]
    out, cur = [], []
    for op, a in rec:
        if op == 'moveTo':
            cur = [('L', a[0], None)]
        elif op == 'lineTo':
            cur.append(('L', a[0], None))
        elif op == 'curveTo':
            cur.append(('C', a[2], (a[0], a[1])))
        elif op in ('closePath', 'endPath'):
            out.append(cur); cur = []
    return out


def level_points(cont):
    """on-curve points where the outline runs level: both ends of a horizontal straight edge (a cut, a bar, a foot),
    and every round's extreme (arrives and leaves with level handles)."""
    n = len(cont)
    seen = set()
    for i, (kind, p, hs) in enumerate(cont):
        nk, np_, nhs = cont[(i + 1) % n]
        prev_p = cont[i - 1][1]
        if kind == 'L' and abs(prev_p[1] - p[1]) < 1e-6 and prev_p[0] != p[0]:       # horizontal edge prev -> p
            for q in (prev_p, p):
                if q not in seen:
                    seen.add(q); yield q
            continue
        a_in = hs[1] if kind == 'C' else prev_p
        a_out = nhs[0] if nk == 'C' else np_
        if abs(a_in[1] - p[1]) < 1e-6 and abs(a_out[1] - p[1]) < 1e-6 and (a_in[0] != p[0] or a_out[0] != p[0]):
            if p not in seen:
                seen.add(p); yield p


def audit(path):
    f = ufoLib2.Font.open(path)
    i = f.info
    lines = {'baseline': 0, 'x-height': i.xHeight, 'cap-height': i.capHeight, 'ascender': i.ascender,
             'descender': i.descender}
    found = []
    for g in f:
        if is_mark(g):
            continue
        ch = chr(g.unicodes[0]) if g.unicodes else ''
        top = i.capHeight if ch.isupper() else i.xHeight
        for c in contours(f, g):
            ys = [p[1] for _, p, _ in c]
            if g.unicodes and (min(ys) >= top - 10 or max(ys) <= 10 and min(ys) < -20):
                continue                                 # a mark contour inside a decomposed letter (ẩ, ặ, ...)
            for p in level_points(c):
                for name, y in lines.items():
                    if y is not None and 0 < abs(p[1] - y) <= TOL:
                        found.append((g.name, p, name, y))
    return found


if __name__ == '__main__':
    bad = 0
    for path in sys.argv[1:]:
        r = audit(path)
        bad += len(r)
        print(f'{path}: {len(r)} level points within {TOL:g} u of a guideline but not on it')
        for g, p, name, y in r[:40]:
            print(f'   {g}: ({p[0]:g}, {p[1]:g}) {name} {y}')
    sys.exit(1 if bad else 0)
