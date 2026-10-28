"""Compile one style of DINHTUONG60s (ex Đìzai-Saigon) to OpenType/CFF (env A2_WEIGHT, A2_ITALIC).

  outlines : boolean ops -> clean contours (booleng: Clipper + curve re-fit), integer grid
  features : kern (class kerning by base letter + accented exceptions),
             ccmp (decomposed Unicode input  a + ◌̂ + ◌́  ->  ấ, so VNI / NFD text renders)
  metrics  : win/hhea/typo all = real font bbox (no clipping of Ẳ or ỵ), USE_TYPO_METRICS
"""
import json, os, sys, math, unicodedata
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.agl import UV2AGL
import family as FM
import booleng

FAMILY = 'DINHTUONG60s'           # display family name (renamed from Đìzai-Saigon at v0.95)
FAMILY_ASCII = 'DINHTUONG60s'     # CFF strings must stay ASCII
PSFAM = 'DINHTUONG60s'            # PostScript / file name
VERSION = '0.950'
FAM_ASC, FAM_DESC = 1050, -250      # v0.95b: line spacing (typo + hhea) — the single sắc strip reaches 1050
FAM_WIN = 1140                       # v0.95c: usWinAscent covers the tallest stack (Bold Ẳ 1135) so Windows never clips
DESCRIPTION = ('DINHTUONG60s — chữ khuôn thép đúc của biển hiệu, biển cổng thập niên 1960. Chỉ chữ hoa '
               '(gõ chữ thường ra chữ hoa). Hỗ trợ tiếng Việt đầy đủ, dấu vẽ cùng nét với chữ.')
FAM_WIN_DESC = 250                   # usWinDescent (v0.96: raised for ỵ, whose nặng hangs under the y tail)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


SEQ_NAMES = {'J\u0301': 'Jacute', 'j\u0301': 'jacute'}   # unencoded glyphs reached through ccmp (Dutch ÍJ́ íj́)


def gname(ch):
    if ch in SEQ_NAMES:
        return SEQ_NAMES[ch]
    if ch.endswith('.tf'):
        return gname(ch[0]) + '.tf'
    u = ord(ch)
    if u == 0x20:
        return 'space'
    n = UV2AGL.get(u)
    if n and n != '.notdef':
        return n
    return 'uni%04X' % u


def draw(contours, pen, dx):
    for c in contours:
        started = False
        for s in c:
            if s[0] == 'M':
                pen.moveTo((round(s[1] + dx), round(s[2]))); started = True
            elif s[0] == 'L':
                pen.lineTo((round(s[1] + dx), round(s[2])))
            elif s[0] == 'C':
                pen.curveTo((round(s[1] + dx), round(s[2])), (round(s[3] + dx), round(s[4])),
                            (round(s[5] + dx), round(s[6])))
            elif s[0] == 'Z' and started:
                pen.closePath(); started = False


def build(kern_file=None):
    G = FM.style_glyphs()
    chars = list(G.keys())
    names = {ch: gname(ch) for ch in chars}
    assert len(set(names.values())) == len(names), 'duplicate glyph names'
    order = ['.notdef'] + [names[c] for c in chars]

    # outlines
    outlines, advances = {}, {}
    for ch in chars:
        g = G[ch]
        outlines[names[ch]] = (booleng.evaluate(g.ops), g.lsb)
        advances[names[ch]] = g.advance if ch not in FM.COMBINING else 0

    charstrings, metrics = {}, {}
    ymin, ymax = 0, 0
    for n in order:
        if n == '.notdef':
            w = 500
            pen = T2CharStringPen(w, None)
            for (x0, y0, x1, y1), rev in (((50, 0, 450, 700), False), ((110, 60, 390, 640), True)):
                pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                if rev: pts = pts[::-1]
                pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
            charstrings[n] = pen.getCharString(); metrics[n] = (w, 50)
            continue
        cont, lsb = outlines[n]
        w = advances[n]
        pen = T2CharStringPen(w, None)
        draw(cont, pen, lsb)
        charstrings[n] = pen.getCharString()
        bp = BoundsPen(None); draw(cont, bp, lsb)
        if bp.bounds:
            metrics[n] = (w, bp.bounds[0]); ymin = min(ymin, bp.bounds[1]); ymax = max(ymax, bp.bounds[3])
        else:
            metrics[n] = (w, 0)

    weight, italic = FM.WEIGHT, FM.ITALIC
    style = FM.STYLE
    ribbi = weight in ('regular', 'bold')
    fam1 = FAMILY if ribbi else f'{FAMILY} Medium'
    sub2 = style if ribbi else ('Italic' if italic else 'Regular')
    ps = PSFAM + '-' + style.replace(' ', '')
    if style == 'Italic':
        ps = PSFAM + '-Italic'

    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    cmap = {ord(c): names[c] for c in chars if len(c) == 1}
    cmap.update({ord(lo): names[up] for lo, up in FM.CASE_ALIAS.items()})   # caps-only: a -> A ...
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps, {'FullName': f'{FAMILY_ASCII} {style}', 'FamilyName': FAMILY_ASCII, 'Weight': style,
                     'ItalicAngle': -FM.ANGLE if italic else 0, 'UnderlinePosition': -130,
                     'UnderlineThickness': 70},
                charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    # one set of vertical metrics for the whole family (same line height in every style);
    # must clear the tallest stack (Ẳ ~1001) and the lowest mark (ỵ ~-236)
    asc, desc = FAM_ASC, FAM_DESC
    assert ymax <= FAM_WIN and ymin >= -FAM_WIN_DESC, (ymin, ymax)
    fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0,
                             caretSlopeRise=1000 if italic else 1,
                             caretSlopeRun=round(1000 * FM.T) if italic else 0)
    fsSel = 0
    if italic: fsSel |= 1
    if weight == 'bold': fsSel |= 1 << 5
    if not italic and weight != 'bold': fsSel |= 1 << 6
    fsSel |= 1 << 7                                     # USE_TYPO_METRICS
    fb.setupOS2(usWeightClass=FM.WCLASS, usWidthClass=5, fsType=0, achVendID='DIZA',
                sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                usWinAscent=FAM_WIN, usWinDescent=max(-desc, FAM_WIN_DESC), sxHeight=530, sCapHeight=700,
                fsSelection=fsSel, ulCodePageRange1=(1 << 0) | (1 << 8),
                ySubscriptXSize=650, ySubscriptYSize=600, ySubscriptYOffset=75,
                ySuperscriptXSize=650, ySuperscriptYSize=600, ySuperscriptYOffset=350,
                yStrikeoutSize=70, yStrikeoutPosition=300, version=4)
    fb.setupPost(italicAngle=-FM.ANGLE if italic else 0, underlinePosition=-130, underlineThickness=70,
                 isFixedPitch=0)
    nm = {'copyright': '© 2026 ĐIZAI studio (dizai.studio)',
          'familyName': fam1, 'styleName': sub2,
          'uniqueFontIdentifier': f'{VERSION};DIZA;{ps}',
          'fullName': f'{FAMILY} {style}', 'version': f'Version {VERSION}', 'psName': ps,
          'designer': 'ĐIZAI studio', 'description': DESCRIPTION, 'vendorURL': 'https://dizai.studio'}
    if not ribbi:
        nm['typographicFamily'] = FAMILY
        nm['typographicSubfamily'] = style
    fb.setupNameTable(nm, mac=False)
    fb.font['head'].macStyle = (1 if weight == 'bold' else 0) | (2 if italic else 0)
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)

    fea = features(G, names, kern_file)
    addOpenTypeFeaturesFromString(fb.font, fea)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, ps + '.otf')
    fb.save(path)
    open(os.path.join(OUT, ps + '.fea'), 'w').write(fea)
    return path, (ymin, ymax)


def features(G, names, kern_file):
    import kern_style as KS
    K = json.load(open(kern_file))
    pairs, exc = K['pairs'], K['exceptions']
    cL, cR = K['classesL'], K['classesR']
    L = ['languagesystem DFLT dflt;', 'languagesystem latn dflt;', 'languagesystem latn VIT;', '']
    # ccmp: decomposed input -> precomposed glyph
    subs = []
    comb = set(FM.COMBINING)
    for ch in G:
        if ch in comb or len(ch) != 1:
            continue
        d = unicodedata.normalize('NFD', ch)
        if len(d) < 2 or not all(m in comb for m in d[1:]):
            continue
        base, marks = d[0], d[1:]
        seen = set()
        for i in range(len(marks)):
            pre = unicodedata.normalize('NFC', base + marks[:i])
            if len(pre) != 1 or pre not in G:
                continue
            seq = (pre,) + tuple(marks[i:])
            if seq in seen: continue
            seen.add(seq)
            subs.append((len(seq), ' '.join(names[x] for x in seq), names[ch]))
            if pre == 'i' and 'ı' in names:                         # dotless forms too
                subs.append((len(seq), ' '.join([names['ı']] + [names[x] for x in seq[1:]]), names[ch]))
    for ch in G:                                                     # base + marks with no code point (J́ j́)
        if ch in SEQ_NAMES:
            subs.append((len(ch), ' '.join(names[x] for x in ch), names[ch]))
            if ch[0] == 'j' and 'ȷ' in names:
                subs.append((len(ch), ' '.join([names['ȷ']] + [names[x] for x in ch[1:]]), names[ch]))
    subs.sort(key=lambda s: -s[0])
    L.append('feature tnum {')
    for d in '0123456789':
        L.append(f'  sub {names[d]} by {names[d + ".tf"]};')
    L.append('} tnum;')
    L.append('')
    L.append('feature ccmp {')
    for ch, seq in FM.CASE_MULTI.items():
        if ch in names:
            L.append(f'  sub {names[ch]} by {" ".join(names[c] for c in seq)};')
    L.append('  lookup VN_COMPOSE {')
    for _, src, dst in subs:
        L.append(f'    sub {src} by {dst};')
    L.append('  } VN_COMPOSE;')
    L.append('} ccmp;')
    L.append('')
    # kerning
    for c, mem in cL.items():
        L.append(f'@kL_{names[c]} = [{" ".join(names[m] for m in mem)}];')
    for c, mem in cR.items():
        L.append(f'@kR_{names[c]} = [{" ".join(names[m] for m in mem)}];')
    L.append('feature kern {')
    L.append('  lookup KERN {')
    for p, v in sorted(exc.items()):
        L.append(f'    pos {names[p[0]]} {names[p[1]]} {v};')
    for p, v in sorted(pairs.items()):
        a, b = p[0], p[1]
        la = f'@kL_{names[a]}' if a in cL else names[a]
        rb = f'@kR_{names[b]}' if b in cR else names[b]
        if la.startswith('@') or rb.startswith('@'):
            la = la if la.startswith('@') else f'[{la}]'
            rb = rb if rb.startswith('@') else f'[{rb}]'
            L.append(f'    pos {la} {rb} {v};')
        else:
            L.append(f'    pos {la} {rb} {v};')
    L.append('  } KERN;')
    L.append('} kern;')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    kf = f"kern_{FM.WEIGHT}{'_it' if FM.ITALIC else ''}.json"
    p, yy = build(kf)
    from fontTools.ttLib import TTFont as _TT
    _f = _TT(p); _f['head'].fontRevision = float(VERSION); _f.save(p)   # head revision = VERSION (was 1.0)
    print(p, 'ymin/ymax', [round(x) for x in yy])
