"""R0b (27/10 13:08 'còn dùng glyph chữ u cũ' / 'check lại hết các ký tự xem còn dùng glyph cũ'):
every symbol of the caps font that BORROWS a lowercase form — ª º µ ƒ ¢ § @ ₫ — takes it from the CURRENT
lowercase (option F, lc96f, same weight), never from the retired v0.94 lowercase.

The lowercase is built in its own process (it re-points concept_v1's globals), so its outlines are exported to
out/lcsym_<weight>.json and the caps build reads them back with lcg(ch).
Export: for w in regular medium bold; do LC_OPT=f A2_WEIGHT=$w python3 lcsym.py; done
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
CHARS = 'acosufjdđn'
XH, ASC, DESC = 530, 740, -200          # lc96f grid (F1)
_cache = {}


def _ops(o):
    out = []
    for op, c in o:
        if op == 'group':
            out.append((op, _ops(c)))
        else:
            out.append((op, [tuple(q) for q in c]))
    return out


def lcg(ch, weight=None):
    """the current lowercase glyph ch (a Glyph), for the weight being built."""
    from geo import Glyph
    w = weight or os.environ.get('A2_WEIGHT', 'regular')
    if w not in _cache:
        p = os.path.join(HERE, 'out', f'lcsym_{w}.json')
        if not os.path.exists(p) and os.environ.get('LCSYM_BOOT') == '1':
            # first export in a clean checkout: the caps build reads these only for ª º µ ƒ ¢ § @ ₫, which the
            # export never uses -> the committed seed copy (the real build re-reads the freshly exported file)
            p = os.path.join(HERE, 'seed', f'lcsym_{w}.json')
        if not os.path.exists(p):
            raise FileNotFoundError(f'{p}: run  LC_OPT=f A2_WEIGHT={w} python3 lcsym.py  first (R0b)')
        _cache[w] = json.load(open(p))
    d = _cache[w]
    body, lsb, rsb, ops = d[ch] if ch in d else d[ch.split('@')[0]]   # first export: the small form is not there yet
    g = Glyph('lcsym_' + ch, body, lsb, rsb, None)
    g.ops = _ops(ops)
    return g


if __name__ == '__main__':
    os.environ['LCSYM_BOOT'] = '1'
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    import lcfont as LF
    LO = LF.lowercase_set()
    out = {}
    for ch in CHARS:
        g = LO[ch]
        out[ch] = [g.body, g.lsb, g.rsb, g.ops]
    # R0b-2 (13:08 'ª Bold/Medium hơi dính'): a SMALL a (ª at 0.6, @ at 0.72) must keep the house clearance
    # (36 u at its final size) between the hood's tip and the bowl. Scaling shrinks that aperture, so — as F7c does
    # for the e — the hood's cut RAY turns back toward the top (shorter hood) just enough; strokes are not touched.
    import math, lc96f as F
    B = F.LF(LF.W8)
    v, h = B.v, B.h
    W = B.wd(round(470 * F.CX)); r = (W - v - 0.85 * v) / 2; ry = r / F.CX; xs = W - v; cx = xs - r
    cy = F.XH + F.OV - (ry + h)
    yb = 0.62 * F.XH; brx, bry = (W - 0.5 * v) / 2, (yb + F.OV) / 2; bcy = (yb - F.OV) / 2
    ox, orx, ory = cx + 0.075 * v, r + 0.925 * v, ry + h
    bowl = [(brx + brx * math.cos(t / 200 * math.pi), bcy + bry * math.sin(t / 200 * math.pi)) for t in range(0, 201)]
    def gap(T):
        a = math.radians(T); pts = []
        for i in range(400):
            q = (cx + i * math.cos(a), cy + i * math.sin(a))
            if ((q[0] - ox) / orx) ** 2 + ((q[1] - cy) / ory) ** 2 <= 1 and ((q[0] - cx) / r) ** 2 + ((q[1] - cy) / ry) ** 2 >= 1:
                pts.append(q)
        return min(math.hypot(p[0] - b[0], p[1] - b[1]) for p in pts for b in bowl)
    for sc in (0.6, 0.72):
        T = F.TERM_A
        while gap(T) * sc < 36 and T > 110:     # a SHORTER hood: the cut ray turns back toward the top
            T -= 0.5
        B.term_a = T
        g = B.g_a()
        out[f'a@{sc}'] = [g['body'], g['lsb'], g['rsb'], g['ops']]
        print(f'small a x{sc}: hood ray {T} deg, aperture {gap(T) * sc:.0f} u at size')
    p = os.path.join(HERE, 'out', f'lcsym_{LF.W8}.json')
    json.dump(out, open(p, 'w'))
    print(p, len(out), 'v', LF.B.v, 'h', LF.B.h)
