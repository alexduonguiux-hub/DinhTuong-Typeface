"""Export the generated masters as UFO 3 (inspection / editing copy of the rule-built sources).

The generators in this folder are the real sources: they draw every glyph from its construction rules. This script
writes what they produce as UFO 3 so the outlines, metrics, kerning and features can be opened in any font editor.

  outlines + advances + unicodes   from the built OTF (CFF, cubic)
  kerning + groups                 from kern_v096_<w>.json (class kerning: public.kern1 / public.kern2, exceptions)
  features.fea                     the build's feature file minus the kern feature (kerning lives in kerning.plist)
  fontinfo                         names, metrics and OS/2 values of the release font

Usage: python3 export_ufo.py <release otf> <kern json> <fea> <out.ufo>"""
import sys, os, json, re, shutil
from fontTools.ttLib import TTFont
from fontTools.ufoLib import UFOWriter
from fontTools.pens.pointPen import SegmentToPointPen

otf, kjson, fea, out = sys.argv[1:5]
f = TTFont(otf)
gs = f.getGlyphSet()
cmap = f.getBestCmap()
rev = {}
for u, n in cmap.items():
    rev.setdefault(n, []).append(u)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
if os.path.exists(out):
    shutil.rmtree(out)
w = UFOWriter(out, formatVersion=3)
glyphset = w.getGlyphSet()


class _G:
    pass


for name in f.getGlyphOrder():
    g = _G()
    g.width = f['hmtx'][name][0]
    g.unicodes = sorted(rev.get(name, []))
    glyphset.writeGlyph(name, g, drawPointsFunc=lambda pp, n=name: gs[n].draw(SegmentToPointPen(pp)))
glyphset.writeContents()
w.writeLayerContents()

n = f['name']; os2 = f['OS/2']; hh = f['hhea']
nm = lambda i: (n.getDebugName(i) or '')
ver = f['head'].fontRevision
info = _G()
info.familyName = nm(16) or nm(1)
info.styleName = nm(17) or nm(2)
info.styleMapFamilyName = nm(1)
info.styleMapStyleName = nm(2).lower() if nm(2).lower() in ('regular', 'bold') else 'regular'
info.versionMajor, info.versionMinor = int(ver), int(round((ver - int(ver)) * 1000))
info.copyright = nm(0)
info.unitsPerEm = f['head'].unitsPerEm
info.ascender, info.descender = 740, -200
info.xHeight, info.capHeight = os2.sxHeight or 530, os2.sCapHeight or 700
info.openTypeNameDesigner, info.openTypeNameDesignerURL = nm(9), nm(12)
info.openTypeNameManufacturer, info.openTypeNameManufacturerURL = nm(8), nm(11)
info.openTypeNameLicense, info.openTypeNameLicenseURL = nm(13), nm(14)
info.openTypeNameDescription = nm(10)
info.openTypeOS2WeightClass = os2.usWeightClass
info.openTypeOS2Type = []
info.openTypeOS2VendorID = os2.achVendID
info.openTypeOS2TypoAscender, info.openTypeOS2TypoDescender, info.openTypeOS2TypoLineGap = os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap
info.openTypeOS2WinAscent, info.openTypeOS2WinDescent = os2.usWinAscent, os2.usWinDescent
info.openTypeHheaAscender, info.openTypeHheaDescender, info.openTypeHheaLineGap = hh.ascent, hh.descent, hh.lineGap
info.openTypeOS2Selection = [7] if os2.fsSelection & (1 << 7) else []
info.postscriptFontName = nm(6)
w.writeInfo(info)

# kerning: the build's class kerning (classes keyed by characters) -> glyph-name groups
K = json.load(open(kjson))
gname = lambda ch: cmap.get(ord(ch)) if len(ch) == 1 else None
groups, kerning = {}, {}
side_key = {'classesL': 'public.kern1.', 'classesR': 'public.kern2.'}
cls_name = {}
for side, pre in side_key.items():
    for c, mem in K[side].items():
        names = [gname(m) for m in mem if gname(m)]
        if len(names) > 1:
            key = pre + (gname(c) or 'u%04X' % ord(c))
            groups[key] = names
            cls_name[(side, c)] = key
for pair, v in K['pairs'].items():
    a, b = pair[0], pair[1:]
    la = cls_name.get(('classesL', a)) or gname(a)
    rb = cls_name.get(('classesR', b)) or gname(b)
    if la and rb and v:
        kerning[(la, rb)] = int(round(v))
for pair, v in K['exceptions'].items():
    a, b = pair[0], pair[1:]
    if gname(a) and gname(b):
        kerning[(gname(a), gname(b))] = int(round(v))
w.writeGroups(groups)
w.writeKerning(kerning)

src = open(fea).read()
src = re.sub(r'feature kern \{.*?\} kern;\s*', '', src, flags=re.S)
w.writeFeatures(src)
w.writeLib({'public.glyphOrder': f.getGlyphOrder()})
w.close()
print(out, len(f.getGlyphOrder()), 'glyphs', len(groups), 'groups', len(kerning), 'kern pairs')
