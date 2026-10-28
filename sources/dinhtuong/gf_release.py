"""Google Fonts release (28/10 'chuẩn hoá ... upload lên google font'): the working build (DINHTUONG60s-*.otf/.ttf)
becomes the family 'Dinh Tuong' with the metadata Google Fonts requires.

  name   0 copyright 'Copyright 2026 The Dinh Tuong Project Authors (<repo>)'   1/2 RIBBI family/style
         3 unique id '<ver>;DIZA;DinhTuong-<Style>'   4 full name   5 'Version <ver>'   6 PostScript
         8 manufacturer, 9 designer, 11/12 URLs, 13/14 SIL OFL 1.1 + https://openfontlicense.org
         16/17 typographic family/style for Medium only (non-RIBBI)
  OS/2   fsType 0 (installable), usWeightClass 400/500/700, fsSelection REGULAR/BOLD + USE_TYPO_METRICS
  TTF    unhinted: gasp 0xFFFF -> 0x000F and the 'fix-nonhinting' prep program (gftools)
  files  fonts/otf/DinhTuong-<Style>.otf, fonts/ttf/DinhTuong-<Style>.ttf (+ fonts/webfonts/*.woff2 when brotli exists)

Usage: python3 gf_release.py <src dir with DINHTUONG60s-*> <dst repo root> [version]"""
import os, sys
from fontTools.ttLib import TTFont, newTable

SRC, DST = sys.argv[1], sys.argv[2]
VER = sys.argv[3] if len(sys.argv) > 3 else None
FAMILY, PSFAM, VENDOR = 'Dinh Tuong', 'DinhTuong', 'DIZA'
REPO = 'https://github.com/alexduonguiux-hub/DinhTuong-Typeface'
COPY = f'Copyright 2026 The Dinh Tuong Project Authors ({REPO})'
LIC = ('This Font Software is licensed under the SIL Open Font License, Version 1.1. '
       'This license is available with a FAQ at: https://openfontlicense.org')
LIC_URL = 'https://openfontlicense.org'
DESC = 'Dinh Tuong: cast-steel stencil lettering from the shop and gate signs of 1960s Saigon, with full Vietnamese.'
STYLES = {'Regular': 400, 'Medium': 500, 'Bold': 700}


def setname(f, nid, s):
    n = f['name']
    for rec in [r for r in n.names if r.nameID == nid]:
        n.removeNames(nameID=nid)
    if s is None:
        return
    n.setName(s, nid, 3, 1, 0x409)                   # Windows only (no Mac name records, as Google Fonts asks)


def fix(path, style, out):
    f = TTFont(path)
    ver = VER or '%.3f' % f['head'].fontRevision
    ribbi = style in ('Regular', 'Bold')
    ps = f'{PSFAM}-{style}'
    for nid in list({r.nameID for r in f['name'].names}):
        if nid >= 0:
            f['name'].removeNames(nameID=nid)
    setname(f, 0, COPY)
    setname(f, 1, FAMILY if ribbi else f'{FAMILY} {style}')
    setname(f, 2, style if ribbi else 'Regular')
    setname(f, 3, f'{ver};{VENDOR};{ps}')
    setname(f, 4, f'{FAMILY} {style}')
    setname(f, 5, f'Version {ver}')
    setname(f, 6, ps)
    setname(f, 8, 'DIZAI studio')
    setname(f, 9, 'DIZAI studio')
    setname(f, 10, DESC)
    setname(f, 11, 'https://dizai.studio')
    setname(f, 12, 'https://dizai.studio')
    setname(f, 13, LIC)
    setname(f, 14, LIC_URL)
    if not ribbi:
        setname(f, 16, FAMILY)
        setname(f, 17, style)
    f['head'].fontRevision = float(ver)
    os2 = f['OS/2']
    os2.fsType = 0
    os2.usWeightClass = STYLES[style]
    os2.achVendID = VENDOR
    sel = os2.fsSelection & ~((1 << 0) | (1 << 5) | (1 << 6))
    sel |= (1 << 5) if style == 'Bold' else (1 << 6)
    sel |= (1 << 7)                                  # USE_TYPO_METRICS
    os2.fsSelection = sel | (1 << 8)          # WWS: the family is weight / width / slope only (fontspector fsselection_wws)
    f['head'].macStyle = 1 if style == 'Bold' else 0
    if 'CFF ' in f:
        cff = f['CFF '].cff
        cff.fontNames = [ps]
        td = cff.topDictIndex[0]
        td.FullName, td.FamilyName = f'{FAMILY} {style}', FAMILY
        td.Notice = COPY
        if hasattr(td, 'Copyright'):
            td.Copyright = COPY
        td.version = ver
    if 'glyf' in f:                                  # unhinted TTF the way gftools fix-nonhinting leaves it
        from fontTools.ttLib.tables import ttProgram
        gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 0x000F}; f['gasp'] = gasp
        prep = newTable('prep'); prep.program = ttProgram.Program()
        prep.program.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]'])
        f['prep'] = prep
        f['head'].flags |= (1 << 3)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    f.save(out)
    return out


for style in STYLES:
    for ext in ('otf', 'ttf'):
        src = os.path.join(SRC, f'DINHTUONG60s-{style}.{ext}')
        out = fix(src, style, os.path.join(DST, 'fonts', ext, f'{PSFAM}-{style}.{ext}'))
        print(out)
        if ext == 'ttf':
            try:
                import brotli  # noqa: F401
                w = TTFont(out); w.flavor = 'woff2'
                wd = os.path.join(DST, 'fonts', 'webfonts'); os.makedirs(wd, exist_ok=True)
                w.save(os.path.join(wd, f'{PSFAM}-{style}.woff2'))
            except ImportError:
                pass
