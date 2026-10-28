"""Check the Google Fonts build (fontmake from sources/ufo) against the generators' reference binaries.

Usage: python3 scripts/compare_build.py <reference fonts dir> <built fonts dir>

For each style (TTF): same cmap; same advance width for every character; same outline (ink area within 0.5 %,
bounding box within 2 units -- TrueType curves are re-approximated); same kerning for every pair of encoded
characters (flattened from the GPOS kern feature); same vertical metrics. Exit code 1 on any difference."""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen

REF, NEW = sys.argv[1], sys.argv[2]


def find(d, style):
    for root, _, files in os.walk(d):
        for f in files:
            if f == f'DinhTuong-{style}.ttf':
                return os.path.join(root, f)
    return None


def kern_table(font):
    """{(left glyph, right glyph): x advance adjustment} from every PairPos lookup of the kern feature."""
    out = {}
    if 'GPOS' not in font:
        return out
    gpos = font['GPOS'].table
    idx = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern':
            idx.update(fr.Feature.LookupListIndex)
    order = font.getGlyphOrder()
    for li in sorted(idx):
        lk = gpos.LookupList.Lookup[li]
        subs = lk.SubTable
        if lk.LookupType == 9:
            subs = [s.ExtSubTable for s in subs]
        for st in subs:
            if type(st).__name__ != 'PairPos':
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for g1, ps in zip(cov, st.PairSet):
                    for pvr in ps.PairValueRecord:
                        v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                        out.setdefault((g1, pvr.SecondGlyph), v)
            elif st.Format == 2:
                c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
                second = {}
                for g in order:
                    second.setdefault(c2.get(g, 0), []).append(g)
                for g1 in cov:
                    rec = st.Class1Record[c1.get(g1, 0)]
                    for k2, r2 in enumerate(rec.Class2Record):
                        v = getattr(r2.Value1, 'XAdvance', 0) if r2.Value1 else 0
                        if v:
                            for g2 in second.get(k2, []):
                                out.setdefault((g1, g2), v)
    return out


def glyph_stats(font, name):
    gs = font.getGlyphSet()
    a = AreaPen(gs); gs[name].draw(a)
    b = BoundsPen(gs); gs[name].draw(b)
    return abs(a.value), b.bounds


bad = 0
for style in ('Regular', 'Medium', 'Bold'):
    pr, pn = find(REF, style), find(NEW, style)
    if not pr or not pn:
        print(style, 'missing', pr, pn); bad += 1; continue
    r, n = TTFont(pr), TTFont(pn)
    cr, cn = r.getBestCmap(), n.getBestCmap()
    errs = []
    if set(cr) != set(cn):
        errs.append(f'cmap differs: only ref {sorted(set(cr) - set(cn))[:10]} only new {sorted(set(cn) - set(cr))[:10]}')
    for u in sorted(set(cr) & set(cn)):
        gr, gn = cr[u], cn[u]
        if r['hmtx'][gr][0] != n['hmtx'][gn][0]:
            errs.append(f'advance {chr(u)} {r["hmtx"][gr][0]} -> {n["hmtx"][gn][0]}')
        ar, br = glyph_stats(r, gr); an, bn = glyph_stats(n, gn)
        if ar and abs(an - ar) / ar > 0.005:
            errs.append(f'outline area {chr(u)} {ar:.0f} -> {an:.0f}')
        if (br is None) != (bn is None) or (br and max(abs(x - y) for x, y in zip(br, bn)) > 2):
            errs.append(f'bounds {chr(u)} {br} -> {bn}')
    kr, kn = kern_table(r), kern_table(n)
    rev_r = {g: u for u, g in cr.items()}; rev_n = {g: u for u, g in cn.items()}
    pr_ = {(rev_r[a], rev_r[b]): v for (a, b), v in kr.items() if a in rev_r and b in rev_r and v}
    pn_ = {(rev_n[a], rev_n[b]): v for (a, b), v in kn.items() if a in rev_n and b in rev_n and v}
    kd = [(chr(a) + chr(b), pr_.get((a, b), 0), pn_.get((a, b), 0)) for (a, b) in set(pr_) | set(pn_) if pr_.get((a, b), 0) != pn_.get((a, b), 0)]
    if kd:
        errs.append(f'kerning: {len(kd)} pairs differ, e.g. {kd[:12]}')
    for tag, attrs in (('hhea', ('ascent', 'descent', 'lineGap')),
                       ('OS/2', ('sTypoAscender', 'sTypoDescender', 'sTypoLineGap', 'usWinAscent', 'usWinDescent',
                                 'sxHeight', 'sCapHeight', 'usWeightClass'))):
        for a in attrs:
            if getattr(r[tag], a) != getattr(n[tag], a):
                errs.append(f'{tag}.{a} {getattr(r[tag], a)} -> {getattr(n[tag], a)}')
    print(f'{style}: {len(cr)} characters, {len(pr_)} kerned pairs (reference) / {len(pn_)} (build) -> '
          + ('IDENTICAL' if not errs else f'{len(errs)} differences'))
    for e in errs[:40]:
        print('   ', e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
