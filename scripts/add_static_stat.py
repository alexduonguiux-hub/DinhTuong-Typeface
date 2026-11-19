#!/usr/bin/env python3
"""The static fonts' STAT (Google Fonts: a family with an italic needs wght + ital in every font's STAT, like the
variable fonts gftools builds): fonts/{ttf,otf}/DinhTuong-*.{ttf,otf}, upright and italic. Adds / replaces STAT only.
Each static font names only its own weight and its own ital value (Roman 0 elidable, linked to Italic 1).
Usage: python3 scripts/add_static_stat.py"""
import glob
import os

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WNAME = {400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold'}
n = 0
for p in sorted(glob.glob(f'{ROOT}/fonts/ttf/DinhTuong-*.ttf') + glob.glob(f'{ROOT}/fonts/otf/DinhTuong-*.otf')):
    f = TTFont(p)
    w = f['OS/2'].usWeightClass; it = bool(f['OS/2'].fsSelection & 1)
    # a static font's STAT names only its own place on each axis (Google Fonts STAT_in_statics)
    axes = [dict(tag='wght', name='Weight', values=[dict(value=w, name=WNAME[w], flags=0x2 if w == 400 else 0,
                                                         **({'linkedValue': 700} if w == 400 else {}))]),
            dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic') if it else
                                                    dict(value=0, name='Roman', flags=0x2, linkedValue=1)])]
    buildStatTable(f, axes, elidedFallbackName=2, windowsNames=True, macNames=False)
    f['name'].removeUnusedNames(f)
    f.save(p); n += 1
print('STAT (wght + ital) in', n, 'static fonts')
