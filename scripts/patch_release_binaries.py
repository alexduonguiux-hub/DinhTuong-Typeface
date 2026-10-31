"""1.002 binaries = the 1.001 binaries with ONLY the glyphs that changed replaced (OTF charstrings drawn from the UFO,
TTF glyphs from the fontmake build of the same UFOs), GPOS from that build, name / head revision from the generator
reference. Every other glyph and table stays byte-identical to 1.001.
Usage: python3 scripts/patch_release_binaries.py <fonts-1.001 dir> <fontmake build dir> <generator reference fonts dir> <changed.json>"""
import sys, json
import ufoLib2
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
OLD, FM, REF, CHJ = sys.argv[1:5]
SF = 'S Sacute Scaron Scedilla Scircumflex dollar s sacute scaron scedilla scircumflex uni0218 uni0219'.split()   # VF4-S
CH = json.load(open(CHJ))
for w in ['Regular', 'Medium', 'Bold']:
    u = ufoLib2.Font.open(f'sources/ufo/DinhTuong-{w}.ufo')
    names = sorted(set(CH[w]) | set(SF))
    for kind in ['ttf', 'otf']:
        base = TTFont(f'{OLD}/{kind}/DinhTuong-{w}.{kind}'); fm = TTFont(f'{FM}/{kind}/DinhTuong-{w}.{kind}')
        ref = TTFont(f'{REF}/{kind}/DinhTuong-{w}.{kind}')
        for g in names:
            if kind == 'ttf':
                base['glyf'][g] = fm['glyf'][g]
            else:
                cs = base['CFF '].cff.topDictIndex[0].CharStrings
                pen = T2CharStringPen(u[g].width, None); u[g].draw(pen)
                cs[g] = pen.getCharString(private=cs[g].private, globalSubrs=cs[g].globalSubrs)
            base['hmtx'][g] = fm['hmtx'][g]
        base['GPOS'] = fm['GPOS']; base['name'] = ref['name']; base['head'].fontRevision = ref['head'].fontRevision
        for p in [f'fonts/{kind}/DinhTuong-{w}.{kind}', f'sources/reference/fonts/{kind}/DinhTuong-{w}.{kind}']:
            base.save(p)
    print(w, 'glyphs replaced', len(names))
