#!/usr/bin/env python3
"""Dinh Tuong Italic (concept italic-A, designer 19/11: 'A, 10°, đủ 4 weight'): the upright steel-cut letters set at a
10° slant, every form kept (no cursive substitutions). Exact geometry on the finished masters, one rule set:

  R-I1  one slant for every glyph and every weight: ITALIC_ANGLE = 10°, sheared about the x-height's middle
        (YP = 265), so a letter leans around its optical centre and its sidebearings stay balanced.
  R-I2  the stroke keeps its weight: a shear thins every vertical stem to V cos(10°) measured square to the stem, so
        each glyph is first widened by 1 / cos(10°) (+1.5 %) about the middle of its advance. Horizontals keep H.
        The advance (and so the spacing and the kerning) is unchanged.
  R-I4  every vertical cut (C G S c e s 2 3 5 ... terminals, stem ends) becomes a cut parallel to the slant axis;
        every level cut (feet, bars, the level undersides of the R8w marks) stays level -- this is what a shear does.
  R-I5  the marks lean with their letter and their centre moves along the slant axis (height x tan 10°), so a stacked
        mark stays over its base; heights and the R8w stack top line are unchanged.
  R-I6  spacing and kerning are the upright ones (the advances are unchanged); the collision guard is re-checked on
        the italic (scripts/italic_check.py).

Writes sources/ufo-italic/ (static masters) from sources/ufo/ and sources/vf-italic/ (variable masters, still
point-compatible: one affine map per glyph) from sources/vf/.
Usage: python3 scripts/make_italic.py
"""
import math
import os
import shutil
import xml.etree.ElementTree as ET

import ufoLib2

ITALIC_ANGLE = 10.0
YP = 265.0                                   # x-height 530 / 2
K = math.tan(math.radians(ITALIC_ANGLE))
SX = 1.0 / math.cos(math.radians(ITALIC_ANGLE))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = {'Regular': 'Italic', 'Medium': 'Medium Italic', 'Bold': 'Bold Italic'}
PSSTYLE = {'Regular': 'Italic', 'Medium': 'MediumItalic', 'Bold': 'BoldItalic'}


def shear_glyph(g):
    cx = g.width / 2.0
    for c in g.contours:
        for p in c.points:
            p.x = round(cx + (p.x - cx) * SX + (p.y - YP) * K, 2)
    for a in g.anchors:
        a.x = cx + (a.x - cx) * SX + (a.y - YP) * K
    g.clearGuidelines()
    if g.components:
        raise SystemExit(f'{g.name}: components are not expected in the Dinh Tuong masters')


def kern_fix(fea, w):
    """R-I6: the glyph pairs of sources/italic-kern.json (scripts/italic_check.py --fix) at the head of the kern lookup;
    an existing glyph pair takes the new value."""
    import json, re
    p = f'{ROOT}/sources/italic-kern.json'
    if not os.path.exists(p):
        return fea
    pairs = json.load(open(p)).get(w, {})
    lines = fea.split('\n')
    have = {}
    for i, l in enumerate(lines):
        m = re.match(r'^    pos ([^@\[\s]+) ([^@\[\s]+) (-?\d+);$', l)
        if m: have.setdefault(f'{m.group(1)} {m.group(2)}', []).append(i)   # a pair can be declared twice: the first wins
    add = []
    for k, v in sorted(pairs.items()):
        if k in have:
            for i in have[k]:
                lines[i] = f'    pos {k} {v};'
        else:
            add.append(f'    pos {k} {v};')
    i = lines.index('  lookup KERN {')
    lines[i + 1:i + 1] = ['    # R-I6 italic collision guard (scripts/italic_check.py)'] + add
    return '\n'.join(lines)


def italic_ufo(src, dst, w, static=False):
    f = ufoLib2.Font.open(src)
    if static:   # the family's underline (post table) as in the upright static release binaries: 70 thick at -130
        f.info.postscriptUnderlineThickness = 70
        f.info.postscriptUnderlinePosition = -130
    f.features.text = kern_fix(f.features.text, w)
    for g in f:
        shear_glyph(g)
    i = f.info
    i.italicAngle = -ITALIC_ANGLE
    i.postscriptSlantAngle = -ITALIC_ANGLE
    i.styleName = STYLE[w]
    i.styleMapFamilyName = 'Dinh Tuong' if w in ('Regular', 'Bold') else f'Dinh Tuong {w}'
    i.styleMapStyleName = 'bold italic' if w == 'Bold' else 'italic'
    i.postscriptFontName = f'DinhTuong-{PSSTYLE[w]}'
    i.postscriptFullName = f'Dinh Tuong {STYLE[w]}'
    i.openTypeNameUniqueID = None
    sel = [b for b in (i.openTypeOS2Selection or []) if b not in (0, 5, 6)]
    i.openTypeOS2Selection = sel
    if os.path.exists(dst):
        shutil.rmtree(dst)
    f.save(dst)


def main():
    os.makedirs(f'{ROOT}/sources/ufo-italic', exist_ok=True)
    for w in ('Regular', 'Medium', 'Bold'):
        italic_ufo(f'{ROOT}/sources/ufo/DinhTuong-{w}.ufo', f'{ROOT}/sources/ufo-italic/DinhTuong-{PSSTYLE[w]}.ufo', w, static=True)
    os.makedirs(f'{ROOT}/sources/vf-italic', exist_ok=True)
    for w in ('Regular', 'Medium', 'Bold'):
        italic_ufo(f'{ROOT}/sources/vf/DinhTuong-{w}.ufo', f'{ROOT}/sources/vf-italic/DinhTuong-{PSSTYLE[w]}.ufo', w)
    ds = ET.parse(f'{ROOT}/sources/vf/DinhTuong.designspace')
    for s in ds.getroot().iter('source'):
        w = s.get('stylename')
        s.set('filename', f'DinhTuong-{PSSTYLE[w]}.ufo'); s.set('stylename', STYLE[w])
    for s in ds.getroot().iter('instance'):
        st = s.get('stylename')
        s.set('stylename', 'Italic' if st == 'Regular' else f'{st} Italic')
    ds.write(f'{ROOT}/sources/vf-italic/DinhTuong-Italic.designspace', xml_declaration=True, encoding='UTF-8')
    print(f'italic {ITALIC_ANGLE}°: sources/ufo-italic (3 masters), sources/vf-italic (3 masters + designspace)')


if __name__ == '__main__':
    main()
