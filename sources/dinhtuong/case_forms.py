"""C1 (1.009, designer: 'thêm tính năng case để các dấu : ; không chạm đáy khi cap'): case-sensitive forms.

Rule: in all-caps text the colon and semicolon stand centred on the capitals, not on the lowercase. colon.case and
semicolon.case are the same outlines moved up by (CAP - XH) / 2, so the colon's two dots sit symmetric about the middle
of the cap height (CAP / 2) instead of the x-height's; the semicolon moves by the same amount, so its dots line up with
the colon's. Advance widths are unchanged.

Each master gets
  * the two glyphs (outlines copied and moved, no components), appended to public.glyphOrder;
  * feature case: sub colon by colon.case; sub semicolon by semicolon.case;
  * feature calt (on by default): the same, by context, right after a capital or a figure (C1-c);
  * kerning: an alternate kerns exactly as its base glyph (it joins every class its base is in, and every single-glyph
    'pos' pair of its base is copied for it).

Usage: python3 case_forms.py Regular.ufo Medium.ufo Bold.ufo ExtraBold.ufo
"""
import re
import sys

import ufoLib2
from ufoLib2.objects import Glyph

CAP, XH = 700, 530
DY = (CAP - XH) / 2
CASE = [('colon', 'colon.case'), ('semicolon', 'semicolon.case')]


def build(font):
    for base, name in CASE:
        src = font[base]
        g = Glyph(name)
        g.width = src.width
        pen = g.getPointPen()
        src.drawPoints(_Shift(pen, DY))
        font.layers.defaultLayer.insertGlyph(g, name=name, overwrite=True)
    order = [o for o in font.lib.get('public.glyphOrder', []) if o not in [n for _, n in CASE]]
    font.lib['public.glyphOrder'] = order + [n for _, n in CASE]


class _Shift:
    def __init__(self, pen, dy):
        self.pen, self.dy = pen, dy

    def beginPath(self, **kw):
        self.pen.beginPath(**kw)

    def endPath(self):
        self.pen.endPath()

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kw):
        self.pen.addPoint((pt[0], pt[1] + self.dy), segmentType, smooth, name, **kw)

    def addComponent(self, *a, **kw):
        self.pen.addComponent(*a, **kw)


POS = re.compile(r'^(\s*pos\s+)(\S+)\s+(\S+)(\s+-?\d+\s*;.*)$')
CLS = re.compile(r'^(\s*@\S+\s*=\s*\[)(.*)(\];.*)$')


def features(font):
    fea = font.features.text
    fea = re.sub(r'\nfeature case \{.*?\} case;\n', '\n', fea, flags=re.S)
    fea = re.sub(r'\nfeature calt \{.*?\} calt;\n', '\n', fea, flags=re.S)
    fea = re.sub(r'\n@CASE_BEFORE = \[.*?\];\n', '\n', fea, flags=re.S)
    alt = dict(CASE)
    out, copied = [], 0
    for line in fea.split('\n'):
        if any(n in line for _, n in CASE):          # rerun: drop what an earlier run wrote
            if POS.match(line):
                continue
            line = line.replace(' colon.case', '').replace(' semicolon.case', '')
        m = CLS.match(line)
        if m:
            toks = m.group(2).split()
            toks += [alt[t] for t in toks if t in alt]
            out.append(m.group(1) + ' '.join(toks) + m.group(3)); continue
        out.append(line)
        m = POS.match(line)
        if m:
            ind, left, right, rest = m.groups()
            bare = lambda t: t[1:-1] if re.fullmatch(r'\[[^\] ]+\]', t) else t
            L = [left] + ([alt[bare(left)]] if bare(left) in alt else [])
            R = [right] + ([alt[bare(right)]] if bare(right) in alt else [])
            for l in L:
                for r in R:
                    if (l, r) != (left, right):
                        out.append(f'{ind}{l} {r}{rest}'); copied += 1
    fea = '\n'.join(out).rstrip('\n') + '\n'
    subs = '\n'.join(f'  sub {b} by {n};' for b, n in CASE)
    fea += f'\nfeature case {{\n{subs}\n}} case;\n'
    # C1-c (1.009, 'bản cài vẫn chưa fix được'): most apps never switch 'case' on for text typed in capitals, so the same
    # forms also come in by context in 'calt' (on by default): a colon / semicolon right after a capital or a figure
    # (the figures stand at cap height) takes its case form - 'GIỜ: 10:30' is raised, 'giờ: 10' is not
    import unicodedata
    before = sorted(g.name for g in font if g.unicodes and any(unicodedata.category(chr(u)) == 'Lu' or chr(u).isdigit() and u < 128 for u in g.unicodes))
    before += sorted(n for n in font.keys() if n.endswith('.tf') and n[:-3] in before)
    fea += f'\n@CASE_BEFORE = [{" ".join(before)}];\n'
    ctx = '\n'.join(f"  sub @CASE_BEFORE {b}' by {n};" for b, n in CASE)
    fea += f'\nfeature calt {{\n{ctx}\n}} calt;\n'
    font.features.text = fea
    print(f'  case: {len(CASE)} forms (+{DY:g} u), {copied} kerning pairs copied')


if __name__ == '__main__':
    for path in sys.argv[1:]:
        f = ufoLib2.Font.open(path)
        print(path)
        build(f)
        features(f)
        f.save()
