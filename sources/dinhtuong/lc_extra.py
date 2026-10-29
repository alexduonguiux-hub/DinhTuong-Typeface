"""R17-R19 (29/10, v1.001): the last three lowercase letters that were still typed as capitals or expanded by ccmp
(þ -> Þ, ð -> Ð, ß -> S S since the caps-only v0.95). Built ONLY from the lowercase's own modules (lc96f):

  R17 þ  = b + p: the p's bowl and stem, the stem running on to the ascender (R4: both free ends flare).
  R18 ð  = the o (F4 ring, round class width) + the straight diagonal of the 6 / 9 (R15c) mirrored: its outer edge is
           the tangent to the ring's outer curve at ETH_ANG (12°) off vertical, leaning left as it rises, thickness
           0.9 v square to the stroke, top cut level on the ascender (R7), crisp crotch with the ring (R9);
           + the house bar of đ / ħ (0.9 h, at the đ bar's height, 120 in / 25 out). (Approved 29/10 13:5x.)
           g_eth_arc (one compass arc instead of the diagonal) is kept as the rejected study (ETH_MODE=arc).
  R19 ß  = a stem (flared foot) + two stacked elliptic rings like s / 3 (R3b): the upper ring (stem side = the stem,
           top on the ascender + overshoot) ends at its lower left with a vertical cut that keeps the e's aperture
           (0.5 h Regular) from the stem; the lower ring (x-height + overshoots, the round class height) hangs from
           the shared waist stroke and ends at its lower left with the house tail (R5d), its cut kept TAIL_CLEAR off the
           stem's flared foot.

Usage (proof): python3 lc_extra.py -> out/lc_extra/proof.svg
"""
import os, math
os.environ.setdefault('LC_OPT', 'f')
import lc96f as L
import concept_v1 as CV
from concept_v1 import rect, ell, fstem

XH, ASC, DESC, OV = L.XH, L.ASC, L.DESC, L.OV
ETH_LEAN = float(os.environ.get('ETH_LEAN', '0.35'))   # R18: arc centre left of the o's centre, x the o's rx
ETH_EXT = float(os.environ.get('ETH_EXT', '0.25'))         # R18: the arc runs on past its top by 0.5 x its counter's half width before the cut
BETA_W = 1.04          # R19: ß body / n body
BETA_WAIST = float(os.environ.get('BETA_WAIST', '0.62'))
ETH_ANG = 12.0      # R18: the ascender's lean off vertical (the 6 / 9 module at its own angle)
ETH_BAR_IN = float(os.environ.get('ETH_BAR_IN', '120'))
BETA_UP = 0.86         # R19: upper ring width / lower ring width


def g_thorn(B):
    ops, W, cx, cy = B.bowl('l', DESC, ASC)                      # R17: free ends both flare (R4)
    sp = B.spur_dx() + B.v - L.CX * B.Rr
    return B.G('þ', W, 52 + sp, 36, ops)


def dbar_y(B):
    """the đ bar's level (lcfont): centred between x-height and ascender, >= 0.5 h Regular over the bowl."""
    yb = max((XH + ASC) / 2 - B.h * 0.45, XH + OV + 0.5 * 93)
    return min(yb, ASC - 0.9 * B.h - 40)


def g_eth_arc(B):
    """R18 (v1): the ascender is one compass arc continuing the ring's right side (centre ETH_LEAN left of the o's)."""
    v, h = B.v, B.h
    Rx = B.rx_round()
    ring, cy = B.ring(Rx, rx=Rx)
    xa = Rx - ETH_LEAN * Rx
    ro, ryo = Rx + ETH_LEAN * Rx, ASC - cy
    ri, ryi = ro - v, ASC - cy - h
    x_cut = xa - ETH_EXT * ri
    arc = ('group', [('add', ell(xa, cy, ro, ryo)), ('sub', ell(xa, cy, ri, ryi)),
                     ('sub', rect(-3000, -3000, 6000, cy)), ('sub', rect(-3000, -3000, x_cut, 6000))])
    yb = dbar_y(B)
    ym = yb + 0.45 * h
    xo = xa + ro * math.sqrt(max(0, 1 - ((ym - cy) / ryo) ** 2))
    xi = xa + ri * math.sqrt(max(0, 1 - ((ym - cy) / ryi) ** 2))
    if os.environ.get('ETH_BAR', 'turn') == 'turn':
        # R18b: the đ bar (same length and weight) turned NINE_ANG (the 6 / 9 diagonal's angle), rising to the right,
        # centred on the arc's centre line halfway between the bowl's top and the ascender
        import figs_c as FC
        from concept_v1 import poly
        yc = (XH + OV + ASC) / 2
        rm, rym = (ro + ri) / 2, (ryo + ryi) / 2
        xc = xa + rm * math.sqrt(max(0, 1 - ((yc - cy) / rym) ** 2))
        Lb = (xo - xi) + ETH_BAR_IN + 25 if os.environ.get('ETH_BAR_L') is None else float(os.environ['ETH_BAR_L'])
        Lb = B.v + 145                                       # the đ bar's length (120 in + stem + 25 out)
        a = math.radians(FC.NINE_ANG)
        ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        hb = 0.9 * h / 2
        P = [(xc - ux * Lb * 0.55 - nx * hb, yc - uy * Lb * 0.55 - ny * hb), (xc + ux * Lb * 0.45 - nx * hb, yc + uy * Lb * 0.45 - ny * hb),
             (xc + ux * Lb * 0.45 + nx * hb, yc + uy * Lb * 0.45 + ny * hb), (xc - ux * Lb * 0.55 + nx * hb, yc - uy * Lb * 0.55 + ny * hb)]
        bar = ('add', poly(P))
    else:
        bar = ('add', rect(xi - ETH_BAR_IN, yb, xo + 25, yb + 0.9 * h))
    G = [('circle', xa, cy, ro, ryo, 'arc'), ('circle', xa, cy, ri, ryi, 'arc in'), ('vline', x_cut, 'cut'), ('hline', yb, 'đ bar')]
    return B.G('ð', 2 * Rx, 36, 36, [('group', ring), arc, bar], G)


def g_eth(B):
    if os.environ.get('ETH_MODE', 'diag') == 'arc':
        return g_eth_arc(B)
    return g_eth_diag(B)


def g_eth_diag(B):
    """R18 (v2): the o + the 6 / 9's straight diagonal (R15c), mirrored: its outer edge is the tangent to the ring's
    outer curve at NINE_ANG (23°) off vertical, leaning left as it rises; thickness 0.9 v square to the stroke (R2);
    the top cut level on the ascender (R7); the inner edge meets the ring in a crisp crotch (R9); + the đ / ħ bar."""
    import figs_c as FC
    from concept_v1 import poly
    v, h = B.v, B.h
    Rx = B.rx_round()
    ring, cy = B.ring(Rx, rx=Rx)
    a, b = Rx, B.Rr
    th = math.radians(float(os.environ.get('ETH_ANG', ETH_ANG)))
    t = math.atan(b / a * math.tan(th))                     # tangent point: upper right of the ring
    px, py = Rx + a * math.cos(t), cy + b * math.sin(t)
    xo = lambda y: px - (y - py) * math.tan(th)              # outer edge
    wd = 0.9 * v / math.cos(th)
    xi = lambda y: xo(y) - wd
    diag = ('add', poly([(px, py), (xo(ASC), ASC), (xi(ASC), ASC), (xi(cy), cy)]))
    yb = dbar_y(B)
    ym = yb + 0.45 * h
    bar = ('add', rect(xi(ym) - 120, yb, xo(ym) + 25, yb + 0.9 * h))
    G = [('circle', Rx, cy, a, b, 'ring'), ('pt', px, py, 'tangent'), ('hline', yb, 'đ bar')]
    return B.G('ð', 2 * Rx, 36, 36, [('group', [ring[0], diag, ring[1]]), bar], G)


def g_germandbls(B):
    v, h = B.v, B.h
    W = BETA_W * B.Wn
    T = ASC + OV                                  # round top: overshoot
    sm = h                                        # waist = a round's top / bottom stroke
    ym = BETA_WAIST * T - sm                     # waist: the lower ring's top at BETA_WAIST of the height (refs 0.58-0.64)
    Wu = BETA_UP * W
    G = []
    # upper ring: its left side IS the stem (x 0..v)
    up_o = CV.ebox(0, ym, Wu, T)
    up_i = CV.ebox(v, ym + sm, Wu - v, T - h)
    cyu = (ym + T) / 2
    x_w = v + L.AP_E                              # R19: waist end keeps the e's aperture off the stem
    up = [('add', up_o), ('sub', up_i), ('sub', rect(v, ym - 1, x_w, cyu))]
    # lower ring: solve its left edge so the R5d cut lands TAIL_CLEAR right of the stem's flared foot
    clear = v + B.fl + float(os.environ.get('SZ_CLEAR', '1.0')) * L.AP_E   # R19: the e's aperture (0.5 h Regular)
    def lower(x0):
        g = []
        cx = (x0 + W) / 2
        t = B.tail(g, cx, -OV + h, x0 + v, v, 'l', 'down', tip_limit=ym - L.AP_S,
                   cry=(ym - (-OV + h)) / 2, ring=((-OV + ym + sm) / 2, (W - x0) / 2, (ym + sm + OV) / 2))
        return t, g, cx
    lo_, hi_ = -200.0, 200.0
    for _ in range(50):
        mid = (lo_ + hi_) / 2
        t, _, _ = lower(mid)
        (lo_, hi_) = (mid, hi_) if t['xt'] < clear else (lo_, mid)
    x0 = hi_
    t, gl, cxl = lower(x0)
    G += gl
    lo = [('add', CV.ebox(x0, -OV, W, ym + sm)), ('sub', CV.ebox(x0 + v, -OV + h, W - v, ym))] + CV.arm_ink(t) + [
          ('sub', t['disk']), ('sub', rect(-1000, -OV - 1, t['xt'], t['cy'])),
          ('sub', rect(-1000, t['tip'], cxl, ym + sm + 1))]
    st = B.stem(0, 0, cyu + 1, top=False)
    G += [('hline', ym, 'waist'), ('vline', x_w, 'waist cut'), ('vline', clear, 'tail clear')]
    return B.G('ß', W, 52, 36, [st, ('group', up), ('group', lo)], G)


if __name__ == '__main__':
    import booleng
    from geo import to_svg_d
    os.makedirs('out/lc_extra', exist_ok=True)
    rows = []
    for w in ('regular', 'medium', 'bold'):
        B = L.LF(w)
        base = {g['name']: g for g in B.proposal()}
        new = {'þ': g_thorn(B), 'ð': g_eth(B), 'ß': g_germandbls(B)}
        rows.append((w, base, new))
    sc, X = float(os.environ.get('SC', '0.16')), 30
    RH = 1150 * sc
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="%d" viewBox="0 0 1900 %d"><rect width="100%%" height="100%%" fill="#fff"/>' % (len(rows) * RH + 40, len(rows) * RH + 40)]
    for i, (w, base, new) in enumerate(rows):
        x = X
        ybase = 20 + i * RH + 0.80 * RH
        for word in os.environ.get('WORDS', 'nþn bþp nðn dðo nßn hßs').split():
            for ch in word:
                gd = new.get(ch) or base.get(ch)
                if gd is None:
                    x += 60; continue
                cs = booleng.evaluate(gd['ops'])
                x += gd['lsb'] * sc
                d = ''.join(to_svg_d(c, 0, 0) for c in cs)
                out.append(f'<path transform="translate({x:.1f} {ybase:.1f}) scale({sc} {sc})" d="{d}" fill="#111"/>')
                if ch in new and os.environ.get('NOGUIDE') != '1':
                    for gg in gd['guides']:
                        if gg[0] == 'circle':
                            out.append(f'<ellipse transform="translate({x:.1f} {ybase:.1f}) scale({sc} {-sc})" cx="{gg[1]}" cy="{gg[2]}" rx="{gg[3]}" ry="{gg[4]}" fill="none" stroke="#f30" stroke-width="5"/>')
                        elif gg[0] == 'vline':
                            out.append(f'<line transform="translate({x:.1f} {ybase:.1f}) scale({sc} {-sc})" x1="{gg[1]}" y1="-250" x2="{gg[1]}" y2="800" stroke="#09f" stroke-width="5"/>')
                        elif gg[0] == 'hline':
                            out.append(f'<line transform="translate({x:.1f} {ybase:.1f}) scale({sc} {-sc})" x1="-50" y1="{gg[1]}" x2="{gd["body"] + 50}" y2="{gg[1]}" stroke="#09f" stroke-width="5"/>')
                x += (gd['body'] + gd['rsb']) * sc
            x += 40
    out.append('</svg>')
    open('out/lc_extra/proof.svg', 'w').write('\n'.join(out))
    print('ok')
