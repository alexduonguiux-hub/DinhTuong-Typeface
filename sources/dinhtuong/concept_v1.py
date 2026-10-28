"""Đìzai-Saigon — CONCEPT v1 (redrawn from scratch, 26/10).

One rule book, every glyph built only from it. Each builder returns the boolean ops AND the
construction guides it used (circles, cut lines, metric lines), so the guide sheet is the
construction itself.

RULE BOOK
  R1 Grid      UPM 1000 · baseline 0 · x 530 · cap 700 · asc 760 · desc -200 · overshoot o 6 / O 8
  R2 Strokes   per weight: V H HM (caps) · v h (lowercase) · horizontals ~0.83 of verticals
  R3 Rings     every bowl is a stadium ring: o-ring 498 wide (R_o 249), O-ring 560 (R_O 280);
               counter = ring inset by the stroke (sides v/V, top-bottom h/H)
  R4 Stems     ruled; a FREE straight end flares like a brush (fl / FL per side)
  R5 Tail      every open end of a round stroke: one VERTICAL cut at counter wall ± TAIL_KEEP·stroke;
               the tail's inner edge is ONE compass arc leaving the counter's top/bottom point
               (horizontal tangent) and meeting the cut TAIL_PHI off vertical. No level cut, no needle.
               The tip keeps TAIL_CLEAR from the next stroke (shortens the reach if needed).
  R6 Hook      descender/ascender hooks (j f J): half ring around the small compass r1 = r_o/2;
               g: the counter is an oval r_o across x r1 down (tail reaches under the bowl)
               (caps: r_O), side = the stem, cut vertically TAIL_PHI short of the counter's extreme
               point -> the same 35° meeting as R5.
  R7 Diagonals flat level cuts, ~0.9 of the stem.
  R8 Marks     cut from the letters' own parts (unchanged from v0.9).
  R13 Bowls    a b d g p q: the n arch mirrored and doubled (flat edges out of the stem, far side
               one compass, counter square at the stem + R9b notches top and bottom).
Usage: python3 concept_v1.py  -> out/concept_v1/{proof_<w>.png, guides_<w>.png, data_<w>.json}
"""
import math, os, json, sys

W8 = {'bold':    dict(V=168, H=140, HM=124, v=150, h=124, FL=9, fl=8),
      'medium':  dict(V=142, H=120, HM=106, v=128, h=106, FL=8, fl=7),
      'regular': dict(V=116, H=100, HM=90,  v=104, h=88,  FL=7, fl=6)}

CAP, XH, ASC, DESC = 700, 530, 760, -200
OV_C, OV_L = 8, 6
RING_O, RING_o = 560, 498
TAIL_KEEP, TAIL_PHI = 0.45, 35.0   # R5 (R5b 62 deg tried 27/10 16:02, on hold 16:08)
HOOK_PHI = 35.0                     # R6 hook cut (unchanged; was shared with TAIL_PHI)
TAIL_MODE = os.environ.get('TAIL_MODE', 'R5d')  # R5d v0.963 (27/10 16:28 'cong vừa', weights keep Regular's curve)
ARM_LO, ARM_LI, ARM_ANG = 1.12, 1.63, 50.0
TAIL_ANG = float(os.environ.get('TAIL_ANG', 50))
KC = 0.56
G2_EPS = float(os.environ.get('G2_EPS', '0.8'))   # R5g: the blend starts this far outside the round (no coincident edges)
ARM_PAR = os.environ.get('ARM_PAR', '1') == '1'   # R5h: the arm keeps one thickness to the cut (no taper)
G2_PRE = float(os.environ.get('G2_PRE', '25'))   # R5g: the arm leaves the round this many degrees before its extreme point
SPINE = float(os.environ.get('SPINE', 1.10))   # R11: the S spine is the heaviest part (TypeDrawers: "esses need to be thickest in the spine")
SWIDE = float(os.environ.get('SWIDE', 0.5))    # S/s widen with the stroke so their counters stay the same in every weight
JOINT = {'regular': 0.88, 'medium': 0.84, 'bold': 0.80}   # R9b joint thickness / stroke (heavier -> thinner)
DENSE = 0.96          # R10 dense letters (a e g s) carry a touch less weight
JSTYLE = os.environ.get('JSTYLE', 'outer')   # 'inner' = R9b notch in the counter corner; 'outer' = R9c notch on the outer edge
JOUT = {'regular': 1 - 67 / 88, 'medium': 1 - 71 / 106, 'bold': 1 - 77 / 124}   # 26/10: +20% over 56/59/64   # R9c joint left after the outer notch / stroke
# (notch depth 67/71/77 units = 0.76/0.67/0.62 of h (26/10 'tăng khoét 20%'): the notch is an OPENING, so it
#  must read the same at every weight -> lighter weights cut relatively deeper; absolute depth
#  and absolute joint still grow monotonically R->M->B)
FIG = 0.95            # figure strokes = 0.95 x caps (v0.9 audit rule)
BAR_AT = 0.52         # R12 crossbar centre at 52% of the space it divides (optically above centre)
FULL = 9999


# ------------------------------------------------------------------ primitives
def rect(x0, y0, x1, y1):
    return [('M', x0, y0), ('L', x1, y0), ('L', x1, y1), ('L', x0, y1), ('Z',)]


def rrect(x0, y0, x1, y1, r=(0, 0, 0, 0), k=KC):
    """rounded rect, radii (tl, tr, br, bl); FULL clamps to a semicircle."""
    if isinstance(r, (int, float)):
        r = (r, r, r, r)
    lim = min(x1 - x0, y1 - y0) / 2
    tl, tr, br, bl = [min(q, lim) for q in r]
    p = [('M', x0 + tl, y1), ('L', x1 - tr, y1)]
    if tr: p.append(('C', x1 - tr + k * tr, y1, x1, y1 - tr + k * tr, x1, y1 - tr))
    p.append(('L', x1, y0 + br))
    if br: p.append(('C', x1, y0 + br - k * br, x1 - br + k * br, y0, x1 - br, y0))
    p.append(('L', x0 + bl, y0))
    if bl: p.append(('C', x0 + bl - k * bl, y0, x0, y0 + bl - k * bl, x0, y0 + bl))
    p.append(('L', x0, y1 - tl))
    if tl: p.append(('C', x0, y1 - tl + k * tl, x0 + tl - k * tl, y1, x0 + tl, y1))
    p.append(('Z',))
    return p


def ell(cx, cy, rx, ry, k=KC):
    return [('M', cx, cy + ry),
            ('C', cx + k * rx, cy + ry, cx + rx, cy + k * ry, cx + rx, cy),
            ('C', cx + rx, cy - k * ry, cx + k * rx, cy - ry, cx, cy - ry),
            ('C', cx - k * rx, cy - ry, cx - rx, cy - k * ry, cx - rx, cy),
            ('C', cx - rx, cy + k * ry, cx - k * rx, cy + ry, cx, cy + ry), ('Z',)]


def ebox(x0, y0, x1, y1):
    """true ellipse in a box (R3b: a ring wider than tall is an OVAL, never a flat-topped stadium)."""
    return ell((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2)


def quarter_disk(cx, cy, rho, side, vdir, k=KC):
    sx = 1 if side == 'r' else -1
    sy = 1 if vdir == 'up' else -1
    ax, bx, by = cx + sx * rho, cx, cy + sy * rho
    return [('M', cx, cy), ('L', ax, cy),
            ('C', ax, cy + sy * k * rho, bx + sx * k * rho, by, bx, by), ('Z',)]


def arm_ink(t):
    """R5d: the stretched outer quarter of a tail's arm (nothing in the older modes)."""
    return [('add', t['add'])] if t.get('add') else []


def _unit(x, y):
    n = math.hypot(x, y)
    return (x / n, y / n)


def _kcap(b, a, k=None):
    """curvature of the drawn round (ell(), handle k) at the end of its vertical radius b (horizontal radius a)."""
    k = KC if k is None else k
    return 2 * (1 - k) / (3 * k * k) * b / (a * a)


def _kell(a, b, th):
    """curvature of the ellipse x = a sin t, y = b cos t at t = th."""
    return a * b / (a * a * math.cos(th) ** 2 + b * b * math.sin(th) ** 2) ** 1.5


def _bez_k(P, n=48):
    """(arc length, curvature) samples of a cubic P = [P0, P1, P2, P3]."""
    out, s, prev = [], 0.0, None
    for i in range(n + 1):
        t = i / n; m = 1 - t
        d1 = [3 * m * m * (P[1][j] - P[0][j]) + 6 * m * t * (P[2][j] - P[1][j]) + 3 * t * t * (P[3][j] - P[2][j]) for j in (0, 1)]
        d2 = [6 * m * (P[2][j] - 2 * P[1][j] + P[0][j]) + 6 * t * (P[3][j] - 2 * P[2][j] + P[1][j]) for j in (0, 1)]
        pt = [m ** 3 * P[0][j] + 3 * m * m * t * P[1][j] + 3 * m * t * t * P[2][j] + t ** 3 * P[3][j] for j in (0, 1)]
        if prev is not None:
            s += math.hypot(pt[0] - prev[0], pt[1] - prev[1])
        prev = pt
        sp = math.hypot(*d1)
        out.append((s, (d1[0] * d2[1] - d1[1] * d2[0]) / max(sp ** 3, 1e-12)))
    return out


def _cap_pt(cx, yc, rx, ry, sx, sy, ph, k=None):
    """R5g: the point of the DRAWN round (ell(), handle k) ph radians before its extreme point (on the side away
    from the tail), with the unit tangent pointing toward the tail and the drawn curve's curvature there."""
    k = KC if k is None else k
    P = [(cx, yc + sy * ry), (cx - sx * k * rx, yc + sy * ry), (cx - sx * rx, yc + sy * k * ry), (cx - sx * rx, yc)]
    B = lambda t, j: (1 - t) ** 3 * P[0][j] + 3 * (1 - t) ** 2 * t * P[1][j] + 3 * (1 - t) * t * t * P[2][j] + t ** 3 * P[3][j]
    xg = rx * math.sin(ph)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        (lo, hi) = (m, hi) if abs(B(m, 0) - cx) < xg else (lo, m)
    t = (lo + hi) / 2
    d1 = [3 * (1 - t) ** 2 * (P[1][j] - P[0][j]) + 6 * (1 - t) * t * (P[2][j] - P[1][j]) + 3 * t * t * (P[3][j] - P[2][j]) for j in (0, 1)]
    d2 = [6 * (1 - t) * (P[2][j] - 2 * P[1][j] + P[0][j]) + 6 * t * (P[3][j] - 2 * P[2][j] + P[1][j]) for j in (0, 1)]
    sp = math.hypot(*d1)
    kap = abs(d1[0] * d2[1] - d1[1] * d2[0]) / sp ** 3
    return (B(t, 0), B(t, 1)), (-d1[0] / sp, -d1[1] / sp), kap


def _push(P, t, C, eps):
    """move P by eps along the normal of tangent t that points away from centre C."""
    n = (-t[1], t[0])
    if (P[0] - C[0]) * n[0] + (P[1] - C[1]) * n[1] < 0:
        n = (-n[0], -n[1])
    return (P[0] + eps * n[0], P[1] + eps * n[1])

def _g2_handles(J, tJ, T, tT, kJ, kT, ylim=None):
    """R5g: G2 at the junction (curvature kJ = the round's), then the FAIREST cubic to the cut (same end point
    and end tangent): the handle at the cut is chosen so the curvature runs down from kJ as evenly as possible
    (least squared curvature change along the arc, no inflection) - a spiral easing out of the round."""
    if os.environ.get('G2_ENDK') == '1':
        return _g2_handles_both(J, tJ, T, tT, kJ, kT)
    cr = lambda u, v: u[0] * v[1] - u[1] * v[0]
    L = math.hypot(T[0] - J[0], T[1] - J[1])
    best = None
    for i in range(1, 120):
        h2 = L * i / 120
        P2 = (T[0] - h2 * tT[0], T[1] - h2 * tT[1])
        h1 = math.sqrt(max(1e-9, 2.0 / 3.0 * abs(cr(tJ, (P2[0] - J[0], P2[1] - J[1]))) / kJ))
        if h1 > 0.95 * L:
            continue
        P1 = (J[0] + h1 * tJ[0], J[1] + h1 * tJ[1])
        sk = _bez_k([J, P1, P2, T])
        ks = [abs(k) for _, k in sk]
        if min(k for _, k in sk) * max(k for _, k in sk) < 0:      # inflection
            continue
        over = 0.0
        if ylim is not None:                                       # prefer: never past the round's extreme line
            yl, sg = ylim
            ys = [(1 - t) ** 3 * J[1] + 3 * (1 - t) ** 2 * t * P1[1] + 3 * (1 - t) * t * t * P2[1] + t ** 3 * T[1] for t in [i / 40 for i in range(41)]]
            over = max(0.0, max(sg * (y - yl) for y in ys) - 0.5)
        e = sum(((ks[j + 1] - ks[j]) / max(sk[j + 1][0] - sk[j][0], 1e-6)) ** 2 * (sk[j + 1][0] - sk[j][0]) for j in range(len(sk) - 1))
        e += 1e6 * sum(max(0.0, ks[j + 1] - ks[j]) ** 2 for j in range(len(ks) - 1))   # curvature never rises again
        e += 1e-3 * over ** 2                                      # a past-the-line dip costs, but fairness first
        if best is None or e < best[0]:
            best = (e, h1, h2)
    return (best[1], best[2]) if best else _g2_handles_both(J, tJ, T, tT, kJ, kT)


def _g2_handles_both(J, tJ, T, tT, kJ, kT):
    """R5g: handle lengths of the cubic J -> T (unit tangents tJ at J, tT at T, both pointing J->T) whose end
    curvatures are kJ and kT (curvature-continuous blend)."""
    cr = lambda u, v: u[0] * v[1] - u[1] * v[0]
    L = math.hypot(T[0] - J[0], T[1] - J[1])
    h1 = h2 = L / 3
    for _ in range(200):
        P2 = (T[0] - h2 * tT[0], T[1] - h2 * tT[1])
        n1 = math.sqrt(max(1e-9, 2.0 / 3.0 * abs(cr(tJ, (P2[0] - J[0], P2[1] - J[1]))) / kJ))
        P1 = (J[0] + n1 * tJ[0], J[1] + n1 * tJ[1])
        n2 = math.sqrt(max(1e-9, 2.0 / 3.0 * abs(cr(tT, (P1[0] - T[0], P1[1] - T[1]))) / kT))
        h1, h2 = 0.5 * h1 + 0.5 * min(n1, 0.95 * L), 0.5 * h2 + 0.5 * min(n2, 0.95 * L)
    return h1, h2


def band(path, y0=-9999, y1=9999):
    """the part of a path between y0 and y1, as 'sub' ops (keeps one tail's construction out
    of the other tail's zone when two tails share a ring)."""
    import booleng
    cs = booleng.evaluate([('add', path), ('sub', rect(-9999, y1, 9999, 99999)),
                           ('sub', rect(-9999, -99999, 9999, y0))], clean=False)
    return [('sub', c + [('Z',)] if c[-1][0] != 'Z' else c) for c in cs]


def poly(pts):
    return [('M',) + tuple(pts[0])] + [('L',) + tuple(p) for p in pts[1:]] + [('Z',)]


def fstem(x0, y0, x1, y1, f, top=True, bot=True):
    """R4: ruled stem whose free ends flare like a brush."""
    import flare_spec as _FS                     # R4c: one flare everywhere
    f = _FS.amt(f); L = _FS.length(y1 - y0)
    ft, fb = (f if top else 0), (f if bot else 0)
    return [('M', x0 - fb, y0), ('L', x1 + fb, y0),
            ('C', x1 + fb * 0.15, y0 + L * 0.35, x1, y0 + L * 0.7, x1, y0 + L),
            ('L', x1, y1 - L),
            ('C', x1, y1 - L * 0.7, x1 + ft * 0.15, y1 - L * 0.35, x1 + ft, y1),
            ('L', x0 - ft, y1),
            ('C', x0 - ft * 0.15, y1 - L * 0.35, x0, y1 - L * 0.7, x0, y1 - L),
            ('L', x0, y0 + L),
            ('C', x0, y0 + L * 0.7, x0 - fb * 0.15, y0 + L * 0.35, x0 - fb, y0), ('Z',)]


def fbar(x0, y0, x1, y1, f, left=False, right=True):
    import flare_spec as _FS                     # R4c: one flare everywhere
    f = _FS.amt(f); L = _FS.length(x1 - x0)
    fr, fl_ = (f if right else 0), (f if left else 0)
    return [('M', x0, y0 - fl_), ('C', x0 + L * 0.35, y0 - fl_ * 0.15, x0 + L * 0.7, y0, x0 + L, y0),
            ('L', x1 - L, y0), ('C', x1 - L * 0.7, y0, x1 - L * 0.35, y0 - fr * 0.15, x1, y0 - fr),
            ('L', x1, y1 + fr), ('C', x1 - L * 0.35, y1 + fr * 0.15, x1 - L * 0.7, y1, x1 - L, y1),
            ('L', x0 + L, y1), ('C', x0 + L * 0.7, y1, x0 + L * 0.35, y1 + fl_ * 0.15, x0, y1 + fl_), ('Z',)]



# R2b reach table: Regular's tail reach per (glyph, end), the floor for Medium / Bold
_REACH = {}
_REACH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'tail_reach_regular.json')
_SRC = ('concept_v1.py', 'concept_port.py', 'glyphs_c.py', 'figs_c.py', 'latin1_c.py', 'lc96f.py', 'lcfont.py')


def _tail_key(vdir, side):
    import sys as _s
    f = _s._getframe(1)
    while f is not None and f.f_code.co_name in ('tail', 'tail_d', '_tail', '_tail_key', 'td'):
        f = f.f_back
    b = f.f_back if f is not None else None
    mod = os.path.splitext(os.path.basename(f.f_code.co_filename))[0] if f else '?'
    name = f.f_code.co_name if f else '?'
    # the glyph's own constructor names the tail; shared helpers (s_shape, _six_ops) add the glyph that called them
    who = name + ('<' + b.f_code.co_name if (b is not None and name in ('s_shape', '_six_ops')) else '')
    return '%s.%s:%s:%s' % (mod, who, vdir, side)


def _save_reach_atexit():
    if os.environ.get('REACH_GEN') == '1' and _REACH:
        _save_reach()


import atexit as _atexit
_atexit.register(_save_reach_atexit)


def _save_reach():
    import json
    os.makedirs(os.path.dirname(_REACH_FILE), exist_ok=True)
    tmp = _REACH_FILE + '.%d' % os.getpid()
    json.dump(_REACH, open(tmp, 'w'), indent=0, sort_keys=True)
    os.replace(tmp, _REACH_FILE)


_REACH_REG = None


def _reach_regular():
    global _REACH_REG
    if _REACH_REG is None:
        import json, subprocess
        here = os.path.dirname(os.path.abspath(__file__))
        newest = max(os.path.getmtime(os.path.join(here, f)) for f in _SRC if os.path.exists(os.path.join(here, f)))
        if not os.path.exists(_REACH_FILE) or os.path.getmtime(_REACH_FILE) < newest:
            env = dict(os.environ, A2_WEIGHT='regular', LC_OPT=os.environ.get('LC_OPT', 'f'), REACH_GEN='1')
            subprocess.run(['python3', '-c', 'import lcfont as L; L.lowercase_set()'], cwd=here, env=env,
                           check=True, stdout=subprocess.DEVNULL)
        _REACH_REG = json.load(open(_REACH_FILE))
    return _REACH_REG

# ------------------------------------------------------------------ the rule book in code
class Build:
    """one weight's construction context."""

    def __init__(self, weight):
        self.w = weight
        for k, val in W8[weight].items():
            setattr(self, k, val)
        import r2c as _r2c
        self.dV = self.V - W8['regular']['V']        # R2c: caps stroke growth over Regular
        self.R_O, self.R_o = (RING_O + _r2c.grow('round', self.dV)) / 2, (RING_o + _r2c.grow('round', self.v - W8['regular']['v'])) / 2   # R2c: rings widen (round class)
        self.r_O, self.r_o = self.R_O - self.V, self.R_o - self.v
        self.r1 = self.r_o / 2
        # R2b weight progression: anything measured in "strokes" that sets an OPENING (tail inset,
        # tip clearance) is measured in the REGULAR's strokes, so heavier weights keep the same
        # openings in units -> relatively tighter apertures and longer tails, never shorter ones.
        self.k = W8['regular']['V'] / self.V
        self.TAIL_CLEAR = 0.3 * self.h * self.k
        self.J = JOINT[weight]

    # R3
    def ring(self, x0, y0, x1, y1, sx, sy, R=FULL, r=FULL):
        return [('add', rrect(x0, y0, x1, y1, R)), ('sub', rrect(x0 + sx, y0 + sy, x1 - sx, y1 - sy, r))]

    # R5
    def tail(self, G, cx, cedge, wall, stroke, side, vdir, tip_limit=None, cry=None, ring=None, face=None, reach=None):
        """returns dict(xt, cy, rho, tip, disk) and records its guides in G."""
        if TAIL_MODE == 'R5d':
            return self.tail_d(G, cx, cedge, wall, side, vdir, tip_limit, cry, ring, stroke, face=face, reach=reach)
        c, sn = math.cos(math.radians(TAIL_PHI)), math.sin(math.radians(TAIL_PHI))
        inset = (1 - TAIL_KEEP) * stroke * self.k          # R2b: inset from the OUTER edge, regular units
        xt = wall + stroke - inset if side == 'r' else wall - stroke + inset
        dx = abs(xt - cx)
        rho = dx / c
        if vdir == 'up':
            tip = cedge - rho * (1 - sn)
            if tip_limit is not None and tip < tip_limit:   # keep the reach, steepen the arc instead
                dy = cedge - tip_limit
                rho = (dx * dx + dy * dy) / (2 * dy)
                tip = tip_limit
            cy = cedge - rho
        else:
            tip = cedge + rho * (1 - sn)
            if tip_limit is not None and tip > tip_limit:
                dy = tip_limit - cedge
                rho = (dx * dx + dy * dy) / (2 * dy)
                tip = tip_limit
            cy = cedge + rho
        G.append(('vline', xt, 'cut'))
        G.append(('pt', xt, tip, 'tip'))
        if TAIL_MODE == 'R5c':                     # R5c: same reach, flatter inner arc (tail_s.py)
            import tail_s
            rc = abs(wall - cx)
            path, info = tail_s.region(cx, cedge, xt, tip, rc, side, vdir, TAIL_ANG, cry, ybot=cy)
            G.append(('circle', info['C'][0], info['C'][1], info['rho'], info['rho'], 'tail'))
            return dict(xt=xt, cy=cy, rho=rho, tip=tip, disk=path, info=info)
        G.append(('circle', cx, cy, rho, rho, 'tail'))
        return dict(xt=xt, cy=cy, rho=rho, tip=tip, disk=quarter_disk(cx, cy, rho, side, vdir))

    # R5d
    def tail_d(self, G, cx, cedge, wall, side, vdir, tip_limit=None, cry=None, ring=None, stroke=None, face=None, reach=None):
        """R5d (27/10 16:18-16:28: designer's sample, 'cong vừa', 'Bold không làm hư đường cong Regular').
        The open quarter of the ring is drawn STRETCHED horizontally: the counter edge = the counter's own cap
        (radii rx, ry) stretched x ARM_LI, the outer edge = the ring's own cap (ring = (centre y, Rx, Ry)) stretched
        x ARM_LO; both leave the round at its top point with a horizontal tangent. The VERTICAL cut stands where
        the stretched counter edge runs ARM_ANG off vertical. Ratios and angle are the same in every weight, so
        Medium / Bold keep Regular's curve; a clearance limit moves the cut along the SAME curve (never bends it)."""
        import tail_s
        sx = 1 if side == 'r' else -1
        sy = 1 if vdir == 'up' else -1
        # 27/10 16:47 ('càng bold thì đuôi càng bị ngắn'): every weight uses REGULAR's arm curve, moved only so its
        # top sits on this weight's counter (the extra weight is added parallel to it): same cut, same reach,
        # same angle at the cut in every weight; the heavier weight's face is simply thicker.
        dv = (stroke or 0) * (1 - self.k)                  # how much the side stroke grew over Regular
        rx = abs(wall - cx) + dv                           # REGULAR's counter radii
        ry = (rx if cry is None else cry + dv * W8['regular']['H'] / W8['regular']['V'])
        ci = cedge - sy * ry
        a_i = ARM_LI * rx
        q = math.tan(math.radians(90 - ARM_ANG)) * a_i / ry
        u = q / math.sqrt(1 + q * q)
        dx = u * a_i
        # 27/10 16:49 ('chữ s thường vẫn bị ngắn đuôi khi bold lên'), R2b strictly: the REACH (cut to axis) is
        # measured in Regular and is a floor in every heavier weight. The cut never slides back; when a clearance
        # limit applies, the same stretched-cap curve is stretched further (flatter, blunter tip) to keep the reach.
        if self.w != 'regular':
            dx = max(dx, _reach_regular().get(_tail_key(vdir, side), 0.0))
            if dx > u * a_i:
                a_i = dx / u
        elif os.environ.get('REACH_GEN') == '1':     # only the generator writes the table (once, at exit)
            _REACH[_tail_key(vdir, side)] = dx
        tip = ci + sy * ry * math.sqrt(max(0.0, 1 - (dx / a_i) ** 2))
        arm_A = None
        if (face or reach) and ring is not None:
            # R5e (27/10 18:36-18:41, e: 'đuôi hơi mỏng' then 'đuôi bị ngắn, làm chữ không cân bằng'): a LONE tail under
            # a bar keeps its own approved reach (Regular units, every weight) and an optically heavier face
            # (face x the standard R5d face). Same outer arm (ring cap x ARM_LO); only the counter arm's stretch is
            # solved so it meets the cut at that face.
            co_, Rx_, Ry_ = ring
            yo_at = lambda d: co_ + sy * Ry_ * math.cos(math.asin(min(1.0, d / (ARM_LO * Rx_))))
            f_std = abs(yo_at(dx) - tip)
            if reach:
                # 27/10 18:45 ('đuôi e nhọn quá' in Medium / Bold): at the approved reach the counter arm still meets
                # the cut ARM_ANG off vertical (no needle, like every R5d tail): solve its stretch from the angle ...
                dx = reach
                kq = math.tan(math.radians(90 - ARM_ANG))
                lo_, hi_ = dx, 20 * dx
                for _ in range(80):
                    mid = (lo_ + hi_) / 2
                    q_ = kq * mid / ry
                    (lo_, hi_) = (mid, hi_) if mid * q_ / math.sqrt(1 + q_ * q_) < dx else (lo_, mid)
                a_i = (lo_ + hi_) / 2
                tip = ci + sy * ry * math.sqrt(max(0.0, 1 - (dx / a_i) ** 2))
                # ... and the face (face x the standard face) from the OUTER arm's stretch
                yo_t = tip + sy * (face or 1.0) * f_std
                c_ = min(0.999, max(0.05, (yo_t - co_) * sy / Ry_))
                arm_A = dx / math.sqrt(1 - c_ * c_)
            else:
                yo = yo_at(dx)
                tip = yo - sy * (face or 1.0) * f_std
                h_ = min(0.995, max(0.0, (tip - ci) * sy / ry))
                a_i = dx / math.sqrt(1 - h_ * h_)
        if tip_limit is not None and (tip - tip_limit) * sy < 0:
            h = min(0.995, (tip_limit - ci) * sy / ry)
            a_i = dx / math.sqrt(1 - h * h)
            tip = ci + sy * ry * h
        xt = cx + sx * dx
        g2 = os.environ.get('ARM_G2', '1') == '1'
        quarter = lambda c0, a, b: [('M', cx, c0), ('L', cx + sx * a, c0),
                                    ('C', cx + sx * a, c0 + sy * 0.5523 * b, cx + sx * 0.5523 * a, c0 + sy * b, cx, c0 + sy * b), ('Z',)]
        disk = quarter(ci, a_i, ry)
        if g2:
            # R5g (28/10 00:16 'đường cong từ bụng xuống đuôi không tự nhiên'): the arm leaves the counter G2
            # (with the counter's own curvature) G2_PRE degrees BEFORE its extreme point and eases (fairest cubic,
            # curvature only falling) to the same cut, tip and end tangent - a spiral out of the round.
            th_i = math.asin(min(1.0, dx / a_i))
            Ti = (xt, tip)
            ti = _unit(sx * a_i * math.cos(th_i), -sy * ry * math.sin(th_i))
            rxw, ryw = abs(wall - cx), (abs(wall - cx) if cry is None else cry)
            yc = cedge - sy * ryw
            ph = math.radians(G2_PRE)
            Ji, tj, kj = _cap_pt(cx, yc, rxw, ryw, sx, sy, ph)
            kT = _kell(a_i, ry, th_i)
            if ARM_PAR and ring is not None:
                # R5h (28/10 01:21 'đuôi sao lại nhỏ dần … style chúng ta đâu có hướng nhỏ dần'): the arm is a band of
                # ONE thickness. Its inner edge ends PARALLEL to the outer edge at the cut, one ring-thickness t
                # inside it (t = the round's own thickness where the arm leaves it, G2_PRE before the extreme), so the
                # arm never thins toward the tip. Outer edge, reach and cut unchanged.
                co_, Rx_, Ry_ = ring
                A_ = ARM_LO * Rx_ if arm_A is None else arm_A
                th_o = math.asin(min(1.0, dx / A_))
                p0_ = (cx + sx * A_ * math.sin(th_o), co_ + sy * Ry_ * math.cos(th_o))
                to_ = _unit(sx * A_ * math.cos(th_o), -sy * Ry_ * math.sin(th_o))
                Jo_, _, _ = _cap_pt(cx, co_, Rx_, Ry_, sx, sy, math.radians(G2_PRE))
                t_ = math.hypot(Jo_[0] - Ji[0], Jo_[1] - Ji[1])
                tip = p0_[1] - sy * t_ / max(abs(to_[0]), 0.25)
                if tip_limit is not None and (tip - tip_limit) * sy < 0:
                    tip = tip_limit                          # clearance wins (reported by QA)
                top0 = ci if (ci - yc) * sy < 0 else yc
                if (tip - top0) * sy < 0:
                    tip = top0                               # never past the counter's centre line (the disk ends there)
                Ti, ti = (xt, tip), to_
                ko = _kell(A_, Ry_, th_o)
                kT = ko / (1 - t_ * ko) if t_ * ko < 0.9 else ko
            Ji = _push(Ji, tj, (cx, yc), G2_EPS)          # no coincident edges in the union (skill: overlap, never touch)
            G.append(('pt', Ji[0], Ji[1], 'g2'))          # R5g guide: where the arm leaves the counter
            h1, h2 = _g2_handles(Ji, tj, Ti, ti, kj, kT, ylim=(cedge, sy))
            E = 60.0
            top = ci if (ci - yc) * sy < 0 else yc
            disk = [('M', cx, top), ('L', xt + sx * E, top), ('L', xt + ti[0] * E, tip + ti[1] * E), ('L', xt, tip),
                    ('C', xt - ti[0] * h2, tip - ti[1] * h2, Ji[0] + tj[0] * h1, Ji[1] + tj[1] * h1, Ji[0], Ji[1]), ('Z',)]
            inner_c = ('C', xt - ti[0] * h2, tip - ti[1] * h2, Ji[0] + tj[0] * h1, Ji[1] + tj[1] * h1, Ji[0], Ji[1])
        add = None
        cy = ci
        if ring is not None:
            co, Rx, Ry = ring
            A = ARM_LO * Rx if arm_A is None else arm_A   # the arm's outer edge, only up to the cut (R5e: solved)
            th = math.asin(min(1.0, dx / A))
            P = lambda t: (cx + sx * A * math.sin(t), co + sy * Ry * math.cos(t))
            D = lambda t: (sx * A * math.cos(t), -sy * Ry * math.sin(t))
            kk = 4.0 / 3.0 * math.tan(th / 4.0)
            p0, p3, d0, d3 = P(th), P(0.0), D(th), D(0.0)
            add = [('M', cx, co), ('L', xt, co), ('L', p0[0], p0[1]),
                   ('C', p0[0] - kk * d0[0], p0[1] - kk * d0[1], p3[0] + kk * d3[0], p3[1] + kk * d3[1], p3[0], p3[1]), ('Z',)]
            if g2:                                        # R5g on the outer edge: leave the ring G2, G2_PRE before its extreme
                to = _unit(*d0)
                ph = math.radians(G2_PRE)
                Jo, tjo, kjo = _cap_pt(cx, co, Rx, Ry, sx, sy, ph)
                Jo = _push(Jo, tjo, (cx, co), G2_EPS)
                G.append(('pt', Jo[0], Jo[1], 'g2'))
                h1, h2 = _g2_handles(Jo, tjo, p0, to, kjo, _kell(A, Ry, th), ylim=(co + sy * Ry, sy))
                ox, oy = Rx - 0.45 * (stroke or 0.2 * Rx), Ry - 0.45 * (stroke or 0.2 * Ry) * Ry / Rx   # a path inside the stroke
                tr = math.asin(max(-0.999, min(0.999, sx * (xt - cx) / ox)))
                back = [(cx + sx * ox * math.sin(t), co + sy * oy * math.cos(t))
                        for t in [tr * (1 - i / 24) - ph * (i / 24) for i in range(25)]]
                add = [('M', Jo[0], Jo[1]), ('C', Jo[0] + tjo[0] * h1, Jo[1] + tjo[1] * h1, p0[0] - to[0] * h2, p0[1] - to[1] * h2, p0[0], p0[1]),
                       ('L', xt, back[0][1])] + [('L', x_, y_) for x_, y_ in back] + [('Z',)]
                if ARM_PAR:                               # R5h: the arm band itself (outer arm, the cut, inner arm): no leak past the inner edge
                    # its inner boundary runs 3 u PAST the inner edge (into the counter side, tapering to 0 at the junction) so
                    # the disk subtracted afterwards draws the edge alone: never two coincident curves in one boolean
                    o3 = -sy * 3.0
                    ic = inner_c
                    inner_o = ('C', ic[1], ic[2] + o3, ic[3], ic[4] + o3 * 0.5, ic[5], ic[6])
                    add = [('M', Jo[0], Jo[1]), ('C', Jo[0] + tjo[0] * h1, Jo[1] + tjo[1] * h1, p0[0] - to[0] * h2, p0[1] - to[1] * h2, p0[0], p0[1]),
                           ('L', xt, tip + o3), inner_o, ('Z',)]
            if (ci - co) * sy > 0:                        # the band between the two cap centres (inside the counter)
                cy = co
                y0, y1 = sorted((co - sy, ci + sy))
                x0, x1 = sorted((cx, xt + sx))
                band = [('M', x0, y0), ('L', x1, y0), ('L', x1, y1), ('L', x0, y1), ('Z',)]
                if sx * sy < 0:
                    band = [band[0], band[3], band[2], band[1], ('Z',)]
                band = [(op[0],) + tuple(op[1:]) for op in band]
                disk = disk + band
        G.append(('circle', cx, ci, a_i, ry, 'tail'))
        G.append(('vline', xt, 'cut'))
        G.append(('pt', xt, tip, 'tip'))
        return dict(xt=xt, cy=cy, rho=a_i, tip=tip, disk=disk, add=add)

    # R9b
    def joint(self, G, xw, ye, stem_side, vdir, stroke, span=None):
        """thin a joint with a crisp notch: the counter's inner corner at the stem wall (xw, ye) is
        cut by a straight chamfer of depth (1-J)*stroke along the wall and 1.6x that along the
        counter edge. Straight lines only -> no wave, the joint reads as a deliberate notch."""
        d = (1 - self.J) * stroke
        sx = 1 if stem_side == 'l' else -1
        sy = 1 if vdir == 'up' else -1
        G.append(('pt', xw, ye + sy * d, 'joint'))
        return ('sub', [('M', xw - sx, ye - sy), ('L', xw - sx, ye + sy * d), ('L', xw, ye + sy * d),
                        ('L', xw + sx * 1.6 * d, ye), ('L', xw + sx * 1.6 * d, ye - sy), ('Z',)])

    # R9c
    def notch_out(self, G, xw, ye, stem_side, vdir, stroke):
        """option B: the stroke leaving the stem is split from it by a 45° triangular notch on its
        OUTER edge (the side away from the counter it closes): one leg on the stem-wall line, depth
        d = (1-JOUT)*stroke, one leg along the edge, same length. The counter corner stays square."""
        d = min((1 - JOUT[self.w]) * self.h, 0.75 * stroke)   # one absolute depth per weight, never > 3/4 of the stroke it cuts
        sx = 1 if stem_side == 'l' else -1
        sy = -1 if vdir == 'up' else 1          # 'up' = outer edge on top, notch goes down into the stroke
        G.append(('pt', xw, ye + sy * d, 'notch'))
        return ('sub', poly([(xw, ye + sy * d), (xw + sx * d, ye), (xw + sx * d, ye - sy * 2), (xw, ye - sy * 2)]))

    # R6
    def hook(self, G, xr, yc, tb, stroke, rin, down=True, rxin=None):
        """half ring round the counter (rxin x rin; circle when rxin is None), side = stroke,
        outer = counter + (stroke, tb); vertical cut TAIL_PHI short of the counter's extreme
        point. Returns (ops, xcut)."""
        rxi = rin if rxin is None else rxin
        rxo, ryo = rxi + stroke, rin + tb
        d = rxi * math.cos(math.radians(HOOK_PHI))
        if down:
            xc = xr - rxo
            xcut = xc - d
            ops = [('add', ell(xc, yc, rxo, ryo)), ('sub', ell(xc, yc, rxi, rin)),
                   ('sub', rect(xc - rxo - 1, yc - ryo - 1, xcut, yc + ryo + 1)),
                   ('sub', rect(xcut - 1, yc, xr + 1, yc + ryo + 1))]
        else:
            xc = xr + rxo
            xcut = xc + d
            ops = [('add', ell(xc, yc, rxo, ryo)), ('sub', ell(xc, yc, rxi, rin)),
                   ('sub', rect(xcut, yc - ryo - 1, xc + rxo + 1, yc + ryo + 1)),
                   ('sub', rect(xr - 1, yc - ryo - 1, xcut + 1, yc))]
        G += [('circle', xc, yc, rxi, rin, 'hook'), ('circle', xc, yc, rxo, ryo, 'hook'), ('vline', xcut, 'cut')]
        return ops, xcut

    # R13
    def bowl(self, G, x0, y0, x1, y1, sv, sh, side, sh_top=None):
        """R13 stem bowl (a b d g p q): the n arch mirrored and doubled. Outer = box from the
        stem's centre line to the far side, the far side turned by ONE compass (FULL radius,
        same as the n shoulder); counter = the box inset by the strokes, far side FULL, square
        at the stem; both stem corners get the R9b joint notch. Flat edges run straight out of
        the stem -> the bowl reads like the n, never a separate ring glued on."""
        sh_top = sh if sh_top is None else sh_top
        if side == 'r':
            xs, R = x1 - sv, (FULL, 0, 0, FULL)
            ob, cb = (x0, y0, x1 - sv / 2, y1), (x0 + sv, y0 + sh, x1 - sv + 1, y1 - sh_top)
        else:
            xs, R = x0 + sv, (0, FULL, FULL, 0)
            ob, cb = (x0 + sv / 2, y0, x1, y1), (x0 + sv - 1, y0 + sh, x1 - sv, y1 - sh_top)
        for (a0, b0, a1, b1), lab in ((ob, 'bowl'), (cb, 'counter')):
            r = min(a1 - a0, b1 - b0) / 2
            cx = a0 + r if side == 'r' else a1 - r
            G += [('circle', cx, b1 - r, r, r, lab), ('circle', cx, b0 + r, r, r, lab)]
        if JSTYLE == 'outer':                      # R9c: notch where the bowl leaves the stem (top edge); its end merges square
            js = [self.notch_out(G, xs, y1, side, 'up', sh_top)]
        else:
            js = [self.joint(G, xs, y1 - sh_top, side, 'up', sh_top), self.joint(G, xs, y0 + sh, side, 'down', sh)]
        return ('group', [('add', rrect(*ob, R)), ('sub', rrect(*cb, R))] + js)

    # ------------------------------------------------------------- the 12 control glyphs
    def g_o(self):
        G, W = [], 2 * self.R_o
        G += [('circle', W / 2, XH + OV_L - self.R_o, self.R_o, self.R_o, 'o-ring'),
              ('circle', W / 2, -OV_L + self.R_o, self.R_o, self.R_o, 'o-ring')]
        return dict(name='o', body=W, lsb=34, rsb=34, ops=self.ring(0, -OV_L, W, XH + OV_L, self.v, self.h), guides=G)

    def g_O(self):
        G, W = [], 2 * self.R_O
        G += [('circle', W / 2, CAP + OV_C - self.R_O, self.R_O, self.R_O, 'O-ring'),
              ('circle', W / 2, -OV_C + self.R_O, self.R_O, self.R_O, 'O-ring')]
        return dict(name='O', body=W, lsb=34, rsb=34, ops=self.ring(0, -OV_C, W, CAP + OV_C, self.V, self.H), guides=G)

    def g_n(self):
        """n (approved v0.9 form): the arch's top runs flat out of the stem top and turns down
        through ONE compass semicircle; R9: the inside junction with the stem is a CRISP square
        corner, so the joint reads (no fillet blending the arch into the stem)."""
        G, W, v, h = [], 470, self.v, self.h
        top = XH + OV_L
        Ra = (W - v / 2) / 2
        G += [('circle', W - Ra, top - Ra, Ra, Ra, 'shoulder'), ('pt', v, top - h, 'junction')]
        ops = [('group', [('add', rrect(v / 2, 0, W, top, (0, FULL, 0, 0))),
                          ('sub', rrect(v - 1, -1, W - v, top - h, (0, FULL, 0, 0))),
                          self.notch_out(G, v, top, 'l', 'up', h) if JSTYLE == 'outer' else
                          self.joint(G, v, top - h, 'l', 'up', h, (W - 2 * v) / 2)]),
               ('add', fstem(0, 0, v, top, self.fl, top=False)),
               ('add', fstem(W - v, 0, W, 300, self.fl, top=False))]
        return dict(name='n', body=W, lsb=46, rsb=46, ops=ops, guides=G)

    def g_H(self):
        W, V, HM = 520 + __import__('r2c').grow('straight', self.dV), self.V, self.HM
        yb = BAR_AT * CAP - HM / 2                 # R12
        ops = [('add', fstem(0, 0, V, CAP, self.FL)), ('add', fstem(W - V, 0, W, CAP, self.FL)),
               ('add', rect(V - 1, yb, W - V + 1, yb + HM))]
        return dict(name='H', body=W, lsb=46, rsb=46, ops=ops, guides=[('hline', yb, 'bar'), ('hline', yb + HM, 'bar')])

    def g_c(self):
        G, W, v, h = [], 2 * self.R_o, self.v, self.h
        tu = self.tail(G, W / 2, XH + OV_L - h, W - v, v, 'r', 'up')
        tl = self.tail(G, W / 2, -OV_L + h, W - v, v, 'r', 'down')
        ops = self.ring(0, -OV_L, W, XH + OV_L, v, h) + band(tu['disk'], y0=tl['tip']) + \
            band(tl['disk'], y1=tu['tip']) + [
            ('sub', rect(tu['xt'], -OV_L - 1, W + 1, XH + OV_L + 1))]
        return dict(name='c', body=W, lsb=34, rsb=-(W - tu['xt']) + 48, ops=ops, guides=G)

    def g_e(self):
        G, W, v, h = [], RING_o, self.v * DENSE, self.h * DENSE
        bh = h - 14 * self.h / 124                 # bar a touch lighter than h
        c0, c1 = -OV_L + h, XH + OV_L - h          # the counter it divides
        yb = c0 + BAR_AT * (c1 - c0) - bh / 2      # R12
        tl = self.tail(G, W / 2, -OV_L + h, W - v, v, 'r', 'down', tip_limit=yb - self.TAIL_CLEAR)
        ops = [('group', self.ring(0, -OV_L, W, XH + OV_L, v, h) + band(tl['disk'], y1=yb) + [
                    ('sub', rect(tl['xt'], -OV_L - 1, W + 1, yb)),
                    ('sub', rect(W / 2, tl['tip'], W + 1, yb))]),
               ('add', rect(v - 1, yb, W - v + 1, yb + bh))]
        G.append(('hline', yb, 'bar'))
        return dict(name='e', body=W, lsb=34, rsb=28, ops=ops, guides=G)

    def g_a(self):
        G, W, v, h = [], RING_o, self.v * DENSE, self.h * DENSE
        hb = 300
        top = XH + OV_L
        y0 = top - W
        ta = self.tail(G, W / 2, top - h, v, v, 'l', 'up', tip_limit=hb + self.TAIL_CLEAR)
        ops = [self.bowl(G, 0, -OV_L, W, hb, v, h, 'r', sh_top=h - 10),
               ('group', [('add', rrect(0, y0, W, top, (FULL, FULL, 0, 0))),
                          ('sub', rrect(v, y0 - 1, W - v, top - h, (FULL, FULL, 0, 0))),
                          ('sub', ta['disk']),
                          ('sub', rect(W - v, y0 - 2, W + 1, hb)),
                          ('sub', rect(-1, y0 - 2, ta['xt'], top + 1)),
                          ('sub', rect(-1, y0 - 2, W / 2, ta['tip']))]),
               ('add', rect(W - v, -OV_L, W, top - 200))]
        G += [('circle', W / 2, top - self.R_o, self.R_o, self.R_o, 'o-ring'), ('hline', hb, 'bowl')]
        return dict(name='a', body=W, lsb=34, rsb=46, ops=ops, guides=G)

    def g_g(self):
        G, W, v, h = [], RING_o, self.v * DENSE, self.h * DENSE
        clear = OV_L + 0.3 * h
        bottom = min(DESC - OV_L, -clear - h - self.r1)
        yc = bottom + h + self.r1
        # R6g (26/10 "đuôi g còn ngắn"): g's hook is the lower half of the o's counter as an OVAL
        # (R3: wider than tall) - across = the o counter (r_o), down = the small compass r1 -
        # so the tail reaches under the bowl like the o it hangs from, same 35° vertical cut.
        hk, xcut = self.hook(G, W, yc, h, v, self.r1, down=True, rxin=self.R_o - self.v)
        ops = [('group', hk + [('add', rect(W - v, yc - 1, W, XH + OV_L))]),
               self.bowl(G, 0, -OV_L, W, XH + OV_L, v, h, 'r')]
        return dict(name='g', body=W, lsb=34, rsb=46, ops=ops, guides=G)

    def g_q(self):
        G, W, v, h = [], RING_o, self.v, self.h
        ops = [self.bowl(G, 0, -OV_L, W, XH + OV_L, v, h, 'r'),
               ('add', fstem(W - v, DESC, W, XH + OV_L, self.fl, top=False))]
        return dict(name='q', body=W, lsb=34, rsb=46, ops=ops, guides=G)

    def g_d(self):
        G, W, v, h = [], RING_o, self.v, self.h
        ops = [self.bowl(G, 0, -OV_L, W, XH + OV_L, v, h, 'r'),
               ('add', fstem(W - v, -OV_L, W, ASC, self.fl, bot=False))]
        return dict(name='d', body=W, lsb=34, rsb=46, ops=ops, guides=G)

    def g_p(self):
        G, W, v, h = [], RING_o, self.v, self.h
        ops = [self.bowl(G, 0, -OV_L, W, XH + OV_L, v, h, 'l'),
               ('add', fstem(0, DESC, v, XH + OV_L, self.fl, top=False))]
        return dict(name='p', body=W, lsb=46, rsb=34, ops=ops, guides=G)

    def g_b(self):
        G, W, v, h = [], RING_o, self.v, self.h
        ops = [self.bowl(G, 0, -OV_L, W, XH + OV_L, v, h, 'l'),
               ('add', fstem(0, -OV_L, v, ASC, self.fl, bot=False))]
        return dict(name='b', body=W, lsb=46, rsb=34, ops=ops, guides=G)

    # ---- arches (R4 + R9c), same construction as n
    def _arch(self, x0, x1, top, sv, sh, notch=True, G=None):
        """n-arch from the stem whose LEFT wall is x0 (stem x0..x0+sv) to the right leg ending at x1."""
        G = [] if G is None else G
        Ra = (x1 - x0 - sv / 2) / 2
        G.append(('circle', x1 - Ra, top - Ra, Ra, Ra, 'shoulder'))
        ops = [('add', rrect(x0 + sv / 2, 0, x1, top, (0, FULL, 0, 0))),
               ('sub', rrect(x0 + sv - 1, -1, x1 - sv, top - sh, (0, FULL, 0, 0)))]
        if notch:
            ops.append(self.notch_out(G, x0 + sv, top, 'l', 'up', sh))
        return ('group', ops)

    def g_h(self):
        W, v, h = 470, self.v, self.h
        top = XH + OV_L
        G = []
        ops = [self._arch(0, W, top, v, h, G=G), ('add', fstem(0, 0, v, ASC, self.fl)),
               ('add', fstem(W - v, 0, W, 300, self.fl, top=False))]
        return dict(name='h', body=W, lsb=46, rsb=46, ops=ops, guides=G)

    def g_m(self):
        """m (ref. 26/10): the first arch is the n-arch (R9c notch where it leaves the left stem,
        one compass shoulder down onto the middle stem). The second arch springs from the middle
        stem's CENTRE line exactly like n's arch springs from its stem (rrect from x0 + v/2), so its
        square top-left corner meets the first shoulder in a clean V: that V is the separation, no
        second notch, no spur."""
        vm = round(self.v * 0.94)                    # three stems in one cell: a touch lighter
        cw = round((470 - 2 * self.v) * 0.86)        # counters a touch narrower than n's
        W = 3 * vm + 2 * cw
        top, h = XH + OV_L, self.h
        mid0 = vm + cw
        G = []
        R2 = (W - mid0 - vm / 2) / 2
        G.append(('circle', W - R2, top - R2, R2, R2, 'shoulder'))
        ops = [self._arch(0, mid0 + vm, top, vm, h, G=G),
               ('group', [('add', rrect(mid0 + vm / 2, 0, W, top, (0, FULL, 0, 0))),
                          ('sub', rrect(mid0 + vm - 1, -1, W - vm, top - h, (0, FULL, 0, 0)))]),
               ('add', fstem(0, 0, vm, top, self.fl - 1, top=False)),
               ('add', fstem(mid0, 0, mid0 + vm, 300, self.fl - 1, top=False)),
               ('add', fstem(W - vm, 0, W, 300, self.fl - 1, top=False))]
        return dict(name='m', body=W, lsb=46, rsb=46, ops=ops, guides=G)

    def g_u(self):
        """u = n turned 180° about the x-height centre (notch on the baseline edge)."""
        n = self.g_n()
        W = n['body']
        def rot(c):
            out = []
            for q in c:
                if q[0] == 'Z': out.append(q); continue
                vals = list(q[1:])
                for i in range(0, len(vals), 2):
                    vals[i], vals[i + 1] = W - vals[i], XH - vals[i + 1]
                out.append((q[0],) + tuple(vals))
            return out
        def rops(ops):
            return [(o, rops(c)) if o == 'group' else (o, rot(c)) for o, c in ops]
        gu = []
        for q in n['guides']:
            if q[0] == 'circle': gu.append(('circle', W - q[1], XH - q[2]) + tuple(q[3:]))
            elif q[0] == 'pt': gu.append(('pt', W - q[1], XH - q[2], q[3]))
        return dict(name='u', body=W, lsb=46, rsb=46, ops=rops(n['ops']), guides=gu)

    def g_r(self):
        W, v, h = 392, self.v, self.h
        top = XH + OV_L
        hb = round(136 * self.v / 150)
        R = (W - v / 2) / 2
        yv = top - R
        G = [('circle', W - R, top - R, R, R, 'shoulder')]
        ops = [('group', [('add', rrect(v / 2, 0, W, top, (0, FULL, 0, 0))),
                          ('sub', rrect(v - 1, -1, W - hb, top - h, (0, FULL, 0, 0))),
                          ('sub', rect(v - 1, -1, W + 1, yv - 20)),
                          self.notch_out(G, v, top, 'l', 'up', h)]),
               ('group', [('add', fstem(W - hb, 300, W, 480, self.fl, top=False)),
                          ('sub', rect(W - hb - 20, yv, W + 20, 500))]),
               ('add', fstem(0, 0, v, top, self.fl, top=False))]
        return dict(name='r', body=W, lsb=46, rsb=2, ops=ops, guides=G)

    def g_C(self):
        G, W, V, H = [], 2 * self.R_O, self.V, self.H
        R = W / 2
        tu = self.tail(G, W / 2, CAP + OV_C - H, W - V, V, 'r', 'up', ring=(CAP + OV_C - R, R, R))
        tl = self.tail(G, W / 2, -OV_C + H, W - V, V, 'r', 'down', ring=(-OV_C + R, R, R))
        ops = self.ring(0, -OV_C, W, CAP + OV_C, V, H) + arm_ink(tu) + arm_ink(tl) + band(tu['disk'], y0=tl['tip']) + \
            band(tl['disk'], y1=tu['tip']) + [('sub', rect(tu['xt'], -OV_C - 1, W + 1, CAP + OV_C + 1)),
                                               ('sub', rect(W / 2, tl['cy'] - 1, tu['xt'] + 1, tu['cy'] + 1))]   # R5d: the aperture between the arms
        return dict(name='C', body=W, lsb=34, rsb=-(W - tu['xt']) + 52, ops=ops, guides=G)

    def extra(self):
        return [self.g_h(), self.g_m(), self.g_u(), self.g_r(), self.g_C(), self.g_three()]

    def s_shape(self, G, W, T, ov, sx, sy, sm, ti):
        """R5 on both ends of an S: two stacked rings sharing the spine."""
        ym = (T - sm) / 2 + 8
        xr_u = W - ti / 2 - sx
        tu = self.tail(G, W / 2, T + ov - sy, xr_u, sx, 'r', 'up', tip_limit=ym + sm + 0.3 * sy * self.k,
                       cry=((T + ov - sy) - (ym + sm)) / 2, ring=((ym + T + ov) / 2, (W - ti) / 2, (T + ov - ym) / 2))
        tl = self.tail(G, W / 2, -ov + sy, sx, sx, 'l', 'down', tip_limit=ym - 0.3 * sy * self.k,
                       cry=(ym - (-ov + sy)) / 2, ring=((-ov + ym + sm) / 2, W / 2, (ym + sm + ov) / 2))
        up = [('add', ebox(ti / 2, ym, W - ti / 2, T + ov)),
              ('sub', ebox(ti / 2 + sx, ym + sm, W - ti / 2 - sx, T + ov - sy))] + arm_ink(tu) + [
              ('sub', tu['disk']),
              ('sub', rect(tu['xt'], tu['cy'], W + 1, T + ov + 1)),
              ('sub', rect(W / 2, ym - 1, W + 1, tu['tip']))]
        lo = [('add', ebox(0, -ov, W, ym + sm)),
              ('sub', ebox(sx, -ov + sy, W - sx, ym))] + arm_ink(tl) + [
              ('sub', tl['disk']),
              ('sub', rect(-1, -ov - 1, tl['xt'], tl['cy'])),
              ('sub', rect(-1, tl['tip'], W / 2 - 3, ym + sm + 1))]
        G.append(('hline', ym, 'spine'))
        return [('group', up), ('group', lo)], tu, tl

    def g_s(self):
        G, W = [], 432 + 2 * (self.v - W8['regular']['v']) * SWIDE
        v, h = self.v * DENSE, self.h * DENSE
        ops, tu, tl = self.s_shape(G, W, XH, OV_L, v - 8, h, SPINE * h, 18)
        return dict(name='s', body=W, lsb=30, rsb=30, ops=ops, guides=G)

    def g_S(self):
        G, W = [], 516 + (__import__('r2c').grow('s', self.dV) if __import__('r2c').ON else 2 * self.dV * SWIDE)
        ops, tu, tl = self.s_shape(G, W, CAP, OV_C, self.V - 10, self.H, SPINE * self.H, 22)
        return dict(name='S', body=W, lsb=34, rsb=34, ops=ops, guides=G)

    def _etan(self, P, cx, cy, rx, ry):
        """lower-right tangent point from P to the ellipse (affine: scale y by rx/ry -> circle)."""
        sc = rx / ry
        px, py = P[0] - cx, (P[1] - cy) * sc
        d = math.hypot(px, py)
        base, a = math.atan2(py, px), math.acos(rx / d)
        best = None
        for t in (base + a, base - a):
            x, y = cx + rx * math.cos(t), cy + rx * math.sin(t) / sc
            if best is None or x - 0.2 * y > best[0][0] - 0.2 * best[0][1]:
                best = ((x, y), t)
        (x, y), t = best
        if t > 0: t -= 2 * math.pi
        return (x, y), t

    def g_two(self):
        """2 (redrawn 26/10): the upper half of an OVAL ring (R3) with the R5 tail on the left;
        its right side runs on TANGENTIALLY into one straight diagonal (R7, 0.9 of the figure stem,
        measured square to the stroke) that lands on a flat base bar flaring at its free end (R4).
        Figure strokes = 0.95 x caps."""
        G, W = [], 510 + __import__('r2c').grow('round', self.dV)
        V, H = FIG * self.V, FIG * self.H
        if os.environ.get('FIG2', 'r15e') == 'r15e':
            # R15e (28/10 18:07 designer's sample '2' + 'đồng bộ độ dày với các số khác'): same construction, the
            # sample's proportion: the 2 is 0.915 x the width of the 9 (sample 273 / 298 px; R15c ring: counter circle
            # + V sides, 0.67 cap tall). Strokes are already the figures' one weight (ring V / H, diagonal 0.9 V, bar H).
            wb9 = (0.67 * CAP - 2 * H) + 2 * V
            W = 0.915 * wb9
            if os.environ.get('CAPW', '1') == '1':
                # R16 (28/10): Regular is the master -- the 2 keeps Regular's 0.915 x 9 and widens like the 8 (R2c round);
                # it narrowed to 0.89 of the 8 in Bold (refs >= 0.93)
                Vr, Hr = FIG * W8['regular']['V'], FIG * W8['regular']['H']
                W = 0.915 * ((0.67 * CAP - 2 * Hr) + 2 * Vr) + __import__('r2c').grow('round', self.dV)
        top, yb = CAP + OV_C, 236
        cx, cy = W / 2, (yb + top) / 2
        rxo, ryo = W / 2, (top - yb) / 2
        rxi, ryi = rxo - V, ryo - H
        kw2 = dict(reach=0.84 * rxo) if os.environ.get('FIG2', 'r15e') == 'r15e' else {}   # R15e: the sample's tail reaches 0.84 of the ring's half-width
        t = self.tail(G, cx, top - H, V, V, 'l', 'up', tip_limit=cy + 0.3 * H * self.k, cry=ryi, ring=(cy, rxo, ryo), **kw2)
        dz = 0.90 * V
        A = (0.0, 90.0 if os.environ.get('FIG2', 'r15e') == 'r15e' else 36.0)   # R15e: the diagonal's inner edge meets the bar's left end 90 up (sample)
        Ti, ti = self._etan(A, cx, cy, rxi, ryi)
        ux, uy = Ti[0] - A[0], Ti[1] - A[1]
        ul = math.hypot(ux, uy)
        bx = 200.0
        for _ in range(60):
            B = (bx, H - 1)
            To, to = self._etan(B, cx, cy, rxo, ryo)
            dist = abs((B[0] - A[0]) * uy - (B[1] - A[1]) * ux) / ul
            bx += (dz - dist) * 0.8
        arc_o = [(cx + rxo * math.cos(a), cy + ryo * math.sin(a)) for a in [to * k / 30 for k in range(31)]]
        arc_i = [(cx + rxi * math.cos(a), cy + ryi * math.sin(a)) for a in [ti + (0 - ti) * k / 30 for k in range(31)]]
        join = [(W, cy + 1)] + arc_o + [B, A] + arc_i + [(W - V, cy + 1)]
        xh = A[0] + (H - A[1]) * (Ti[0] - A[0]) / (Ti[1] - A[1])
        ops = [('group', [('add', ebox(0, yb, W, top)), ('sub', ebox(V, yb + H, W - V, top - H))] + arm_ink(t) + [
                          ('sub', rect(-1, yb - 1, W + 1, cy)),
                          ('sub', t['disk']),
                          ('sub', rect(-1, cy - 1, t['xt'], top + 1)),
                          ('sub', rect(-1, cy - 1, W / 2, t['tip']))]),
               ('add', poly(join)),
               ('group', [('add', fbar(0, 0, W, H, self.FL, left=False, right=True)),
                          ('sub', poly([(-1, A[1]), (xh, H + 1), (-1, H + 1)]))])]
        G += [('circle', cx, cy, rxo, ryo, 'ring'), ('circle', cx, cy, rxi, ryi, 'counter'),
              ('pt', To[0], To[1], 'tangent'), ('pt', Ti[0], Ti[1], 'tangent')]
        return dict(name='two', body=W, lsb=40, rsb=40, ops=ops, guides=G)

    def g_three(self):
        """3 (redrawn 26/10): two OVAL rings (R3) open on the left, the lower one larger (stable,
        like S), sharing ONE middle stroke whose centre sits at 52% of the cap (R12); the middle
        stroke runs left as a flat bar cut vertically at 0.3 W. Both free ends = R5 tails."""
        # R16 (28/10): the 3 was the narrowest figure (ink 0.87 of the 8; refs 0.94-1.01) -> ink 0.95 of the 8
        G, W = [], (float(os.environ.get('THREE_W', 524)) if os.environ.get('CAPW', '1') == '1' else 492) + __import__('r2c').grow('round', self.dV)
        V, H, HM = FIG * self.V, FIG * self.H, FIG * self.HM
        top, bot = CAP + OV_C, -OV_C
        ym = BAR_AT * CAP - HM / 2
        xu0, xu1 = 22, W - 14
        cxu, cxl = (xu0 + xu1) / 2, W / 2
        xm = 0.30 * W
        tu = self.tail(G, cxu, top - H, xu0 + V, V, 'l', 'up', tip_limit=ym + HM + 0.3 * H * self.k,
                       cry=(top - H - ym - HM) / 2, ring=((ym + top) / 2, (xu1 - xu0) / 2, (top - ym) / 2))
        # R15i (28/10 18:33 'số 3 ở medium và bold đuôi hơi lòi ra'): the lower tail's vertical cut stands FLUSH under the
        # upper tail's cut (one vertical line, like the 5's tail on its stem) in every weight; it reached 30 further left
        kw3 = dict(reach=cxl - tu['xt']) if os.environ.get('THREE_FLUSH', '1') == '1' else {}
        tl = self.tail(G, cxl, bot + H, V, V, 'l', 'down', tip_limit=ym - 0.3 * H * self.k,
                       cry=(ym - bot - H) / 2, ring=((bot + ym + HM) / 2, W / 2, (ym + HM - bot) / 2), **kw3)
        up = [('add', ebox(xu0, ym, xu1, top)), ('sub', ebox(xu0 + V, ym + HM, xu1 - V, top - H))] + arm_ink(tu) + [
              ('sub', tu['disk']),
              ('sub', rect(-1, tu['cy'], tu['xt'], top + 1)),
              ('sub', rect(-1, ym + HM, cxu, tu['tip']))]
        lo = [('add', ebox(0, bot, W, ym + HM)), ('sub', ebox(V, bot + H, W - V, ym))] + arm_ink(tl) + [
              ('sub', tl['disk']),
              ('sub', rect(-1, bot - 1, tl['xt'], tl['cy'])),
              ('sub', rect(-1, tl['tip'], cxl, ym))]
        ops = [('group', up), ('group', lo), ('add', rect(xm, ym, cxl, ym + HM)),
               ('sub', rect(-1, ym - 1, xm, ym + HM + 1))]
        G += [('circle', cxu, (ym + top) / 2, (xu1 - xu0) / 2, (top - ym) / 2, 'ring'),
              ('circle', cxl, (bot + ym + HM) / 2, W / 2, (ym + HM - bot) / 2, 'ring'),
              ('hline', ym, 'bar'), ('hline', ym + HM, 'bar'), ('vline', xm, 'cut')]
        return dict(name='three', body=W, lsb=40, rsb=40, ops=ops, guides=G)

    def g_question(self):
        """?: three quarters of a ring (R5 tail on the left), the right side swings into a
        short stem over the dot."""
        G, W, V, H = [], 470 + __import__('r2c').grow('round', self.dV), self.V, self.H
        y0, top = 310, CAP + OV_C               # ring: counter ~ the 2's (stadium on the O rule)
        ri = (W - 2 * V) / 2
        cy_low = y0 + H + ri
        ym = (y0 + top) / 2
        t = self.tail(G, W / 2, top - H, V, V, 'l', 'up', tip_limit=ym, cry=(top - H - y0 - H) / 2,
                      ring=((y0 + top) / 2, W / 2, (top - y0) / 2))
        sw = 0.88 * V
        _kk = W8[self.w]['v'] / 150
        D = round(round(164 * (0.15 + 0.85 * _kk)) * 1.03)   # punctuation dot = i-dot x 1.03 (one dot family)
        ops = [('group', [('add', ebox(0, y0, W, top)), ('sub', ebox(V, y0 + H, W - V, top - H))] + arm_ink(t) + [
                    ('sub', t['disk']),
                    ('sub', rect(-1, y0 - 1, t['xt'], top + 1)),
                    ('sub', rect(-1, y0 - 1, W / 2 - sw / 2, t['tip']))]),
               ('add', fstem(W / 2 - sw / 2, 230, W / 2 + sw / 2, y0 + H, self.FL, top=False)),
               ('add', ell(W / 2, D / 2, D / 2, D / 2))]
        G.append(('circle', W / 2, cy_low, ri, ri, 'counter'))
        return dict(name='question', body=W, lsb=30, rsb=30, ops=ops, guides=G)

    def all(self):
        return [self.g_n(), self.g_o(), self.g_H(), self.g_O(), self.g_a(), self.g_c(), self.g_e(),
                self.g_g(), self.g_q(), self.g_d(), self.g_b(), self.g_p(), self.g_s(), self.g_S(), self.g_two(), self.g_question()]


# ------------------------------------------------------------------ rendering
def flatten(contour, n=20):
    pts, cur = [], None
    for c in contour:
        if c[0] in ('M', 'L'):
            cur = (c[1], c[2]); pts.append(cur)
        elif c[0] == 'C':
            p0, p1, p2, p3 = cur, c[1:3], c[3:5], c[5:7]
            for i in range(1, n + 1):
                t = i / n
                a, b, cc, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                pts.append((a * p0[0] + b * p1[0] + cc * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + cc * p2[1] + d * p3[1]))
            cur = p3
    return pts


def render(builds, path, S=0.42, guides=True, text=None):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import booleng
    TOP, BOT = ASC + 120, DESC - 100
    cells = []
    for gd in builds:
        cont = booleng.evaluate(gd['ops'])
        gd['contours'] = cont
        w = gd['lsb'] + gd['body'] + gd['rsb']
        x0 = -gd['lsb'] - (60 if guides else 0)
        cw = int((w + (120 if guides else 0)) * S)
        ch = int((TOP - BOT) * S)
        im = Image.new('RGB', (cw, ch), (245, 241, 230))
        tf = lambda x, y: ((x - x0) * S, (TOP - y) * S)
        A = np.zeros((ch, cw), bool)
        for c in cont:
            m = Image.new('L', (cw, ch), 0)
            ImageDraw.Draw(m).polygon([tf(*p) for p in flatten(c)], fill=255)
            A ^= np.array(m) > 0
        arr = np.array(im)
        arr[A] = (28, 27, 25) if not guides else (190, 186, 178)
        im = Image.fromarray(arr)
        d = ImageDraw.Draw(im)
        if guides:
            for y in (DESC, 0, XH, CAP, ASC):
                d.line([tf(x0, y), tf(x0 + cw / S, y)], fill=(160, 160, 160), width=1)
            for gg in gd['guides']:
                if gg[0] == 'circle':
                    _, cx, cy, rx, ry, lab = gg
                    a, b = tf(cx - rx, cy + ry), tf(cx + rx, cy - ry)
                    d.ellipse([a, b], outline=(13, 148, 136), width=2)
                    p = tf(cx, cy); d.line([(p[0] - 5, p[1]), (p[0] + 5, p[1])], fill=(13, 148, 136), width=2)
                    d.line([(p[0], p[1] - 5), (p[0], p[1] + 5)], fill=(13, 148, 136), width=2)
                elif gg[0] == 'vline':
                    a, b = tf(gg[1], TOP), tf(gg[1], BOT)
                    d.line([a, b], fill=(220, 38, 38), width=2)
                elif gg[0] == 'hline':
                    a, b = tf(x0, gg[1]), tf(x0 + cw / S, gg[1])
                    d.line([a, b], fill=(37, 99, 235), width=1)
                elif gg[0] == 'pt':
                    p = tf(gg[1], gg[2]); d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], outline=(220, 38, 38), width=2)
        cells.append(im)
    W = sum(c.width for c in cells) + 10 * len(cells)
    H = max(c.height for c in cells) + (50 if text else 0)
    out = Image.new('RGB', (W, H), 'white')
    x = 0
    for c in cells:
        out.paste(c, (x, H - c.height)); x += c.width + 10
    if text:
        ImageDraw.Draw(out).text((10, 10), text, fill='black', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28))
    out.save(path)
    return builds


if __name__ == '__main__':
    od = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'concept_v1')
    os.makedirs(od, exist_ok=True)
    for w in sys.argv[1:] or ['bold', 'medium', 'regular']:
        B = Build(w)
        gl = B.all()
        sfx = '' if JSTYLE == 'outer' else '_optA'
        render(gl, os.path.join(od, f'proof{sfx}_{w}.png'), S=0.3, guides=False, text=f'Concept v1 · {w}')
        render(gl, os.path.join(od, f'guides{sfx}_{w}.png'), S=0.3, guides=True, text=f'Concept v1 · {w} · guides')
        json.dump([{k: g[k] for k in ('name', 'body', 'lsb', 'rsb', 'contours', 'guides')} for g in gl],
                  open(os.path.join(od, f'data{sfx}_{w}.json'), 'w'))
        print(w, 'ok')
