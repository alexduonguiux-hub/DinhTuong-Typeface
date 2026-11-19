"""L1 (19/11, designer: 'khi gõ 2 chữ tt gõ liền kề thì cho nét ngang dính nhau', then ft tf ff too; fi fl not wanted):
standard ligatures t_t f_t t_f f_f whose crossbars run on unbroken.

Rule: t and f carry their crossbar at the same height in every weight and it spans the whole glyph, so a ligature is
simply the two letters at their natural spacing (the t|t kerning that kept the bars apart is not applied) with the
two flared bar ends that meet cut back to the plain bar (R4b flares only FREE ends), the bar running on between them. Nothing else of either letter changes.

The glyphs are written into each master (outline union, no components), appended to public.glyphOrder, and
features.fea gets
  * feature liga with the four substitutions;
  * kerning for the ligatures: a ligature's LEFT side kerns as its first letter, its RIGHT side as its last letter
    (every 'pos t X' pair is copied for t_t and f_t, every 'pos X t' pair for t_t and t_f; the same for f);
  * GDEF ligature carets between the two letters (at the first letter's advance).

Usage: python3 ligatures.py Regular.ufo Medium.ufo Bold.ufo
"""
import re
import sys

import ufoLib2
from booleanOperations import BooleanOperationManager as BOM
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from ufoLib2.objects import Glyph

LIGS = [('t', 't', 't_t'), ('f', 't', 'f_t'), ('t', 'f', 't_f'), ('f', 'f', 'f_f')]
FLARE = 42.0         # the flared length of a free bar end (R4b), cut back where two bars meet


def _flat(glyph):
    """the glyph's contours as polylines (curves sampled)"""
    rec = RecordingPen(); glyph.draw(rec)
    polys, cur, start = [], None, None
    for op, a in rec.value:
        if op == 'moveTo':
            cur = start = a[0]; polys.append([cur])
        elif op == 'lineTo':
            cur = a[0]; polys[-1].append(cur)
        elif op == 'curveTo':
            (x1, y1), (x2, y2), (x3, y3) = a
            for i in range(1, 17):
                t = i / 16; m = 1 - t
                polys[-1].append((m**3 * cur[0] + 3 * m * m * t * x1 + 3 * m * t * t * x2 + t**3 * x3,
                                  m**3 * cur[1] + 3 * m * m * t * y1 + 3 * m * t * t * y2 + t**3 * y3))
            cur = a[-1]
        elif op == 'qCurveTo':
            pts = [cur] + list(a)
            for k in range(1, len(pts) - 1):
                p0 = pts[k - 1] if k == 1 else ((pts[k - 1][0] + pts[k][0]) / 2, (pts[k - 1][1] + pts[k][1]) / 2)
                p2 = pts[k + 1] if k == len(pts) - 2 else ((pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2)
                for i in range(1, 9):
                    t = i / 8; m = 1 - t
                    polys[-1].append((m * m * p0[0] + 2 * m * t * pts[k][0] + t * t * p2[0], m * m * p0[1] + 2 * m * t * pts[k][1] + t * t * p2[1]))
            cur = a[-1]
        elif op in ('closePath', 'endPath'):
            cur = start
    return polys


def ink_runs_x(glyph, x, y0=300, y1=650):
    """vertical runs of ink on the line x = const (bottom, top), between y0 and y1"""
    ys = []
    for pts in _flat(glyph):
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            if (ax - x) * (bx - x) < 0:
                ys.append(ay + (x - ax) * (by - ay) / (bx - ax))
    ys = sorted(ys)
    runs = list(zip(ys[::2], ys[1::2]))
    return [r for r in runs if r[0] < y1 and r[1] > y0]


def bar_span(glyph, x):
    runs = [r for r in ink_runs_x(glyph, x) if 350 <= (r[0] + r[1]) / 2 <= 620]   # the crossbar, not f's hook
    if not runs:
        raise SystemExit(f'{glyph.name}: no crossbar at x={x:.0f}')
    return max(runs, key=lambda r: r[1] - r[0])


def build(font):
    for a, b, name in LIGS:
        ga, gb = font[a], font[b]
        ax0, ay0, ax1, ay1 = ga.getBounds(font)
        bx0, by0, bx1, by1 = gb.getBounds(font)
        sh = ga.width
        # the bar's own thickness, measured past the flared end (R4b flares every free bar end over ~40 u)
        lo_a, hi_a = bar_span(ga, ax1 - FLARE - 8)
        lo_b, hi_b = bar_span(gb, bx0 + FLARE + 8)
        lo, hi = max(lo_a, lo_b), min(hi_a, hi_b)
        rec = RecordingPen()
        ga.draw(rec)
        gb.draw(TransformPen(rec, (1, 0, 0, 1, sh, 0)))
        # the two flared ends that meet are cut back to the plain bar, and the bar runs on between them
        x0, x1 = ax1 - FLARE, sh + bx0 + FLARE
        rec.moveTo((x0, lo)); rec.lineTo((x1, lo)); rec.lineTo((x1, hi)); rec.lineTo((x0, hi)); rec.closePath()
        tmp = Glyph('tmp')
        rec.replay(tmp.getPen())
        un = Glyph('un')
        BOM.union(list(tmp.contours), un.getPointPen())
        cut = Glyph('cut')
        cp = cut.getPen()
        for ya, yb in ((lo - 90, lo), (hi, hi + 90)):
            cp.moveTo((x0, ya)); cp.lineTo((x1, ya)); cp.lineTo((x1, yb)); cp.lineTo((x0, yb)); cp.closePath()
        g = Glyph(name)
        g.width = ga.width + gb.width
        BOM.difference(list(un.contours), list(cut.contours), g.getPointPen())
        if name in font:
            del font[name]
        font.layers.defaultLayer.insertGlyph(g, name=name, overwrite=True)
        order = font.lib.get('public.glyphOrder', [])
        order = [o for o in order if o not in [n for _, _, n in LIGS]]
        order += sorted(n for _, _, n in LIGS if n in font or n == name)   # appended in name order (release patch)
        font.lib['public.glyphOrder'] = order
        print(f'  {name}: width {g.width}, bar {lo:.0f}-{hi:.0f}, joined over {x0:.0f}..{x1:.0f}')


POS = re.compile(r'^(\s*pos\s+)(\S+)\s+(\S+)\s+(-?\d+)\s*;\s*$')


def features(font):
    fea = font.features.text
    if 'feature liga' in fea:
        fea = re.sub(r'\nfeature liga \{.*?\} liga;\n', '\n', fea, flags=re.S)
    first = {l: [n for a, b, n in LIGS if a == l] for l in 'tf'}     # ligatures starting with l (left side = l)
    last = {l: [n for a, b, n in LIGS if b == l] for l in 'tf'}      # ligatures ending with l (right side = l)
    out, added = [], 0
    for line in fea.split('\n'):
        out.append(line)
        m = POS.match(line)
        if not m or any(n in line for _, _, n in LIGS):
            continue
        ind, left, right, val = m.groups()
        bare = lambda t: t[1:-1] if re.fullmatch(r'\[[^\] ]+\]', t) else t      # '[t]' is the glyph t
        lg, rg = bare(left), bare(right)
        if lg not in ('t', 'f') and rg not in ('t', 'f'):
            continue
        lefts = last[lg] if lg in ('t', 'f') else [left]
        rights = first[rg] if rg in ('t', 'f') else [right]
        for L in lefts:
            for R in rights:
                if L == left and R == right:
                    continue
                out.append(f'{ind}{L} {R} {val};'); added += 1
    fea = '\n'.join(out).rstrip('\n') + '\n'
    subs = '\n'.join(f'  sub {a} {b} by {n};' for a, b, n in LIGS)
    fea += f'\nfeature liga {{\n{subs}\n}} liga;\n'
    font.features.text = fea
    print(f'  liga: {len(LIGS)} ligatures, {added} kerning pairs copied')


def carets(font):
    """GDEF ligature carets: the caret between the two letters stands where the first one ends (its advance)"""
    fea = re.sub(r'\ntable GDEF \{.*?\} GDEF;\n', '\n', font.features.text, flags=re.S)
    lines = '\n'.join(f'  LigatureCaretByPos {n} {font[a].width:g};' for a, b, n in LIGS)
    font.features.text = fea.rstrip('\n') + f'\n\ntable GDEF {{\n{lines}\n}} GDEF;\n'


if __name__ == '__main__':
    for path in sys.argv[1:]:
        f = ufoLib2.Font.open(path)
        print(path)
        build(f)
        features(f)
        carets(f)
        f.save()
