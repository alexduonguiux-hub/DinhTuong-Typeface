#!/usr/bin/env python3
"""Release patch (1.004 on 1.003, same method as scripts/patch_release_binaries.py for 1.002): the new binaries are the
previous binaries with ONLY the changed glyphs replaced. OTF charstrings are drawn from the UFO, TTF glyphs and hmtx
come from the fontmake build of the same UFOs, GPOS from that build (the UFO features.fea), and the version is set in
name ID 3 / 5 and head.fontRevision. Every other glyph and table stays byte-identical.

Usage: python3 scripts/patch_release_glyphs.py <previous fonts dir> <fontmake build dir> <changed.json> <version>
  changed.json: {"Regular": [glyph, ...], "Medium": [...], "Bold": [...]}
Writes fonts/{ttf,otf}/ and sources/reference/fonts/{ttf,otf}/.
"""
import json
import sys

import ufoLib2
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

OLD, FM, CHJ, VERSION = sys.argv[1:5]
CH = json.load(open(CHJ))
for w in ['Regular', 'Medium', 'Bold']:
    u = ufoLib2.Font.open(f'sources/ufo/DinhTuong-{w}.ufo')
    names = sorted(set(CH[w]))
    for kind in ['ttf', 'otf']:
        base = TTFont(f'{OLD}/{kind}/DinhTuong-{w}.{kind}')
        fm = TTFont(f'{FM}/{kind}/DinhTuong-{w}.{kind}')
        old_ver = f"{base['head'].fontRevision:.3f}"
        for g in names:
            if kind == 'ttf':
                base['glyf'][g] = fm['glyf'][g]
            else:
                cs = base['CFF '].cff.topDictIndex[0].CharStrings
                pen = T2CharStringPen(u[g].width, None)
                u[g].draw(pen)
                cs[g] = pen.getCharString(private=cs[g].private, globalSubrs=cs[g].globalSubrs)
            base['hmtx'][g] = fm['hmtx'][g]
        base['GPOS'] = fm['GPOS']
        for rec in base['name'].names:
            if rec.nameID in (3, 5):
                s = rec.toUnicode()
                if old_ver in s:
                    rec.string = s.replace(old_ver, VERSION)
        base['head'].fontRevision = float(VERSION)
        for p in [f'fonts/{kind}/DinhTuong-{w}.{kind}', f'sources/reference/fonts/{kind}/DinhTuong-{w}.{kind}']:
            base.save(p)
    print(w, 'glyphs replaced', len(names))
