"""OTF (CFF) -> TTF (glyf, quadratic) with fontTools cu2qu; keeps GSUB/GPOS/name/OS2."""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

MAX_ERR = 0.5      # font units: quadratic approximation tolerance

def convert(src, dst):
    f = TTFont(src)
    gs = f.getGlyphSet()
    glyf = newTable('glyf'); glyf.glyphOrder = f.getGlyphOrder(); glyf.glyphs = {}
    for name in f.getGlyphOrder():
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, MAX_ERR, reverse_direction=True))
        glyf[name] = pen.glyph()
    # v0.96 QA: hmtx lsb must equal the glyf xMin, or the outline is drawn shifted (parenleft was +17.75)
    for name in f.getGlyphOrder():
        g = glyf[name]; g.recalcBounds(glyf)
        adv, _ = f['hmtx'][name]
        f['hmtx'][name] = (adv, g.xMin if getattr(g, 'numberOfContours', 0) else 0)
    f['loca'] = newTable('loca')
    f['glyf'] = glyf
    del f['CFF ']
    if 'VORG' in f: del f['VORG']
    f['maxp'] = newTable('maxp'); m = f['maxp']
    m.tableVersion = 0x00010000
    for k in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs',
              'maxStackElements', 'maxSizeOfInstructions', 'maxComponentElements', 'maxComponentDepth'):
        setattr(m, k, 0)
    m.maxZones = 1
    m.numGlyphs = len(f.getGlyphOrder())
    post = f['post']; post.formatType = 2.0; post.extraNames = []; post.mapping = {}
    post.glyphOrder = f.getGlyphOrder()
    f['head'].glyphDataFormat = 0
    f.sfntVersion = '\x00\x01\x00\x00'
    f['gasp'] = newTable('gasp'); f['gasp'].gaspRange = {0xFFFF: 0x000F}
    f.save(dst)

if __name__ == '__main__':
    for w in ('Regular', 'Medium', 'Bold'):
        convert(f'out/DINHTUONG60s-{w}.otf', f'out/ttf/DINHTUONG60s-{w}.ttf')
        print(w, 'ok')
