"""Dinh Tuong variable font (wght 400-700) sources from the three static masters, so the VF renders EXACTLY like the
static fonts at wght 400 / 500 / 700 (designer 31/10: 'đồng bộ để hiển thị tĩnh và variables phải giống nhau').

* Masters = the static UFOs (sources/ufo, already point-compatible by VF3 / VF4-S) at wght 400 / 500 / 700.
* Glyphs that are not yet compatible R = M = B (the open VF4 list) are kept EXACT per weight instead of being bent:
  X carries Regular's outline in every master, X.wM Medium's, X.wB Bold's (each compatible by construction), and a
  designspace rule (processed last -> 'rclt', after ccmp composes) swaps X -> X.wM for 450 <= wght < 600 and
  X -> X.wB for wght >= 600. At 400 / 500 / 700 every glyph is the static glyph; between them these glyphs step
  instead of interpolating, until their VF4 construction rule makes them compatible.
* Kerning: each master's own features.fea; the alternates join every class and every pair of their base glyph.

Usage: python3 scripts/make_vf_sources.py   ->  sources/vf/DinhTuong[wght].designspace + 3 UFOs
"""
import os, re, shutil
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'sources', 'ufo')
OUT = os.path.join(ROOT, 'sources', 'vf')
W = [('Regular', 400), ('Medium', 500), ('Bold', 700)]
ALT = [('wM', 500), ('wB', 700)]
STEP = {'wM': (450, 599.99), 'wB': (600, 700)}


def sig(g):
    return [tuple(p.type for p in c.points) for c in g.contours]


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    F = {s: ufoLib2.Font.open(os.path.join(SRC, f'DinhTuong-{s}.ufo')) for s, _ in W}
    names = list(F['Regular'].keys())
    bad = [n for n in names if not (sig(F['Regular'][n]) == sig(F['Medium'][n]) == sig(F['Bold'][n]))]
    src = {s: ufoLib2.Font.open(os.path.join(SRC, f'DinhTuong-{s}.ufo')) for s, _ in W}   # pristine copies to read from
    for s, _ in W:
        f = F[s]
        for n in bad:
            for tag, wsrc in [('', 'Regular'), ('wM', 'Medium'), ('wB', 'Bold')]:
                gsrc = src[wsrc][n]
                name = n if not tag else f'{n}.{tag}'
                g = f[name] if name in f else f.newGlyph(name)
                g.clearContours(); g.width = gsrc.width
                for c in gsrc.contours:
                    g.contours.append(c.copy() if hasattr(c, 'copy') else c)
                if tag:
                    g.unicodes = []
        # kerning / classes in the fea: alternates follow their base glyph
        fea = open(os.path.join(SRC, f'DinhTuong-{s}.ufo', 'features.fea')).read()
        out = []
        for line in fea.split('\n'):
            m = re.match(r'(\s*@\S+\s*=\s*\[)(.*)(\];.*)', line)
            if m:
                toks = m.group(2).split()
                toks += [f'{t}.{a}' for t in toks if t in bad for a, _ in ALT]
                out.append(m.group(1) + ' '.join(toks) + m.group(3)); continue
            m = re.match(r'(\s*pos\s+)(\[[^\]]*\]|\S+)\s+(\[[^\]]*\]|\S+)(\s+-?\d+;.*)', line)
            if m:
                def inline(tok):   # an inline class [a b c]: the alternates join it (class kerning keeps its value)
                    if not tok.startswith('['):
                        return tok
                    gl = tok[1:-1].split()
                    return '[' + ' '.join(gl + [f'{t}.{a}' for t in gl if t in bad for a, _ in ALT]) + ']'
                l0, r0 = inline(m.group(2)), inline(m.group(3))
                L = [l0] + ([f'{l0}.{a}' for a, _ in ALT] if l0 in bad else [])
                R = [r0] + ([f'{r0}.{a}' for a, _ in ALT] if r0 in bad else [])
                for l in L:
                    for r in R:
                        out.append(f'{m.group(1)}{l} {r}{m.group(4)}')
                continue
            out.append(line)
        f.features.text = '\n'.join(out)
        f.lib['public.glyphOrder'] = list(f.lib.get('public.glyphOrder', names)) + [f'{n}.{a}' for n in bad for a, _ in ALT if f'{n}.{a}' not in f.lib.get('public.glyphOrder', [])]
        f.save(os.path.join(OUT, f'DinhTuong-{s}.ufo'), overwrite=True)

    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = 'Weight', 'wght', 400, 400, 700
    ds.addAxis(ax)
    for s, v in W:
        sd = SourceDescriptor(); sd.filename = f'DinhTuong-{s}.ufo'; sd.path = os.path.join(OUT, sd.filename); sd.styleName = s; sd.familyName = 'Dinh Tuong'
        sd.location = {'Weight': v}
        ds.addSource(sd)
    for s, v in [('Regular', 400), ('Medium', 500), ('SemiBold', 600), ('Bold', 700)]:
        i = InstanceDescriptor(); i.familyName = 'Dinh Tuong'; i.styleName = s; i.location = {'Weight': v}
        ds.addInstance(i)
    for a, (lo, hi) in STEP.items():
        r = RuleDescriptor(); r.name = f'VF4 exact {a}'
        r.conditionSets.append([dict(name='Weight', minimum=lo, maximum=hi)])
        r.subs = [(n, f'{n}.{a}') for n in bad]
        ds.addRule(r)
    ds.rulesProcessingLast = True
    ds.write(os.path.join(OUT, 'DinhTuong[wght].designspace'))
    print('VF sources:', OUT, '| exact-per-weight glyphs (VF4 open):', len(bad))


if __name__ == '__main__':
    main()
