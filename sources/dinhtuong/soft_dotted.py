"""SD1 (1.004, Font Bakery soft_dotted): the dot of a soft-dotted letter (i j į ị) goes when a mark is set above it.

The precomposed letters already do this (ì í ĩ ỉ … are drawn on ı). For sequences the font has no precomposed glyph
for (i + ring, j + grave, į + acute, ị + circumflex, i + horn + dot above …), ccmp now swaps the base for its dotless
form before any mark above, also across marks below / the horn:
    i -> dotlessi    j -> uni0237    iogonek -> iogonek.dotless    uni1ECB -> uni1ECB.dotless
The two new glyphs are į and ị with the dot contour (the one wholly above the x-height) left out, so they are exactly
the drawn letters without the dot (same advance, same stem, same mark below).

Usage: python3 soft_dotted.py Regular.ufo Medium.ufo Bold.ufo     (idempotent: rerunning replaces what it wrote)
"""
import re
import sys

import ufoLib2

DOTLESS = {'i': 'dotlessi', 'j': 'uni0237', 'iogonek': 'iogonek.dotless', 'uni1ECB': 'uni1ECB.dotless'}
TOP = [0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0306, 0x0307, 0x0308, 0x0309, 0x030A, 0x030B, 0x030C]
LOW = [0x031B, 0x0323, 0x0326, 0x0327, 0x0328]          # marks below / the horn, which may stand between
BEGIN, END = '# SD1 soft-dotted (soft_dotted.py) begin', '# SD1 soft-dotted end'


def dotless_copy(font, src, name):
    g = font[src]
    keep = [c for c in g.contours if min(p.y for p in c.points) < font.info.xHeight - 10]
    if len(keep) == len(g.contours):
        raise SystemExit(f'{src}: no dot contour above the x-height')
    if name in font:
        del font[name]
    n = font.newGlyph(name)
    n.width = g.width
    for c in keep:
        n.contours.append(c.copy() if hasattr(c, 'copy') else c)
    order = font.lib.setdefault('public.glyphOrder', list(font.keys()))
    if name not in order:
        order.append(name)


def fea_block(font):
    cmap = {u: g.name for g in font for u in g.unicodes}
    top = [cmap[u] for u in TOP if u in cmap]
    low = [cmap[u] for u in LOW if u in cmap]
    bases = [b for b in DOTLESS if b in font and DOTLESS[b] in font]
    L = [BEGIN,
         f'@SD_BASE = [{" ".join(bases)}];',
         f'@SD_TOP = [{" ".join(top)}];',
         f'@SD_LOW = [{" ".join(low)}];',
         'lookup SD_DOTLESS {',
         *[f'  sub {b} by {DOTLESS[b]};' for b in bases],
         '} SD_DOTLESS;',
         END]
    rules = ['  lookup SOFT_DOTTED {',
             "    sub @SD_BASE' lookup SD_DOTLESS @SD_TOP;",
             "    sub @SD_BASE' lookup SD_DOTLESS @SD_LOW @SD_TOP;",
             "    sub @SD_BASE' lookup SD_DOTLESS @SD_LOW @SD_LOW @SD_TOP;",
             '  } SOFT_DOTTED;']
    return '\n'.join(L) + '\n', '\n'.join(rules) + '\n'


def patch_fea(font):
    fea = font.features.text
    fea = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n', '', fea, flags=re.S)
    fea = re.sub(r'  lookup SOFT_DOTTED \{.*?\} SOFT_DOTTED;\n', '', fea, flags=re.S)
    head, rules = fea_block(font)
    i = fea.index('feature ccmp {')
    fea = fea[:i] + head + fea[i:]
    j = fea.index('  } VN_COMPOSE;\n') + len('  } VN_COMPOSE;\n')       # after the composition, before ccmp ends
    fea = fea[:j] + rules + fea[j:]
    font.features.text = fea


if __name__ == '__main__':
    for path in sys.argv[1:]:
        f = ufoLib2.Font.open(path)
        dotless_copy(f, 'iogonek', 'iogonek.dotless')
        dotless_copy(f, 'uni1ECB', 'uni1ECB.dotless')
        patch_fea(f)
        f.save(overwrite=True)
        print(path, 'SD1: iogonek.dotless uni1ECB.dotless + ccmp SOFT_DOTTED')
