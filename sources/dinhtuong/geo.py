"""Construction kit for the font. Font units, UPM 1000, y-up, baseline 0.
Every glyph is a sequence of boolean ops on closed contours: ('add'|'sub', contour).
A contour is a list of segments: ('M',x,y) ('L',x,y) ('C',x1,y1,x2,y2,x,y) ('Z',).
"""
import math

# ---------------- METRICS (the concept grid) ----------------
UPM = 1000
CAP = 700          # cap height
XH = 530           # x-height (large, 70s display: 76% of cap)
ASC = 760          # ascender (b d h k l) sits above cap
DESC = -200        # descender
OV_C = 8           # overshoot caps (squarish bowls need little)
OV_L = 6           # overshoot lowercase

# stems: optical contrast ~ 86% (horizontals thinner than verticals)
V = 176            # cap vertical stem
H = 146            # cap horizontal
HM = 132           # cap middle bars (E F H B P R A) a touch thinner
v = 158            # lowercase vertical
h = 132            # lowercase horizontal

# superellipse corners: handle factor larger than circle (0.552) -> squarer 'TV screen' curve
K = 0.64
RO = 236           # cap bowl outer radius
RI = 64            # cap counter radius (tight, ink-trap-like softness)
ro = 196           # lc bowl outer radius
ri = 54            # lc counter radius
RS = 10            # micro radius on 'sharp' outer corners (ink spread)

SB_STRAIGHT = 46
SB_ROUND = 34
SB_DIAG = 16


def rrect(x0, y0, x1, y1, r=(0, 0, 0, 0), k=K):
    """rounded rect, r = (tl, tr, br, bl)."""
    if isinstance(r, (int, float)):
        r = (r, r, r, r)
    w, hh = x1 - x0, y1 - y0
    lim = min(w, hh) / 2
    tl, tr, br, bl = [min(max(c, 0), lim) for c in r]
    p = []
    p.append(('M', x0 + tl, y1))
    p.append(('L', x1 - tr, y1))
    if tr:
        p.append(('C', x1 - tr + k * tr, y1, x1, y1 - tr + k * tr, x1, y1 - tr))
    p.append(('L', x1, y0 + br))
    if br:
        p.append(('C', x1, y0 + br - k * br, x1 - br + k * br, y0, x1 - br, y0))
    p.append(('L', x0 + bl, y0))
    if bl:
        p.append(('C', x0 + bl - k * bl, y0, x0, y0 + bl - k * bl, x0, y0 + bl))
    p.append(('L', x0, y1 - tl))
    if tl:
        p.append(('C', x0, y1 - tl + k * tl, x0 + tl - k * tl, y1, x0 + tl, y1))
    p.append(('Z',))
    return p


def rect(x0, y0, x1, y1, soft=0):
    return rrect(x0, y0, x1, y1, (soft, soft, soft, soft))


def poly(pts):
    p = [('M',) + tuple(pts[0])]
    for q in pts[1:]:
        p.append(('L',) + tuple(q))
    p.append(('Z',))
    return p


def diag_dx(target, dx_run, dy):
    """horizontal width of a diagonal stroke whose perpendicular thickness = target.
    dx_run: horizontal run of the stroke's centre line, dy: vertical rise."""
    # iterate: angle depends slightly on width; use centre-line angle
    ang = math.atan2(abs(dy), abs(dx_run))
    return target / math.sin(ang)


def transform(contour, fn):
    out = []
    for s in contour:
        if s[0] == 'Z':
            out.append(s)
            continue
        vals = list(s[1:])
        pts = []
        for i in range(0, len(vals), 2):
            pts.extend(fn(vals[i], vals[i + 1]))
        out.append((s[0],) + tuple(pts))
    return out


def rot180(contour, cx, cy):
    return transform(contour, lambda x, y: (2 * cx - x, 2 * cy - y))


def mirror_x(contour, cx):
    return reverse(transform(contour, lambda x, y: (2 * cx - x, y)))


def mirror_y(contour, cy):
    return reverse(transform(contour, lambda x, y: (x, 2 * cy - y)))


def shift(contour, dx, dy):
    return transform(contour, lambda x, y: (x + dx, y + dy))


def reverse(contour):
    # winding direction doesn't matter for Figma booleans; keep as is
    return contour


class Glyph:
    def __init__(self, name, body, lsb=SB_STRAIGHT, rsb=SB_STRAIGHT, unicode=None):
        self.name = name
        self.body = body
        self.lsb, self.rsb = lsb, rsb
        self.ops = []
        self.unicode = unicode

    def add(self, *cs):
        for c in cs:
            self.ops.append(('add', c))
        return self

    def group(self, ops):
        """add a compound built from its own boolean ops (union into glyph)."""
        self.ops.append(('group', ops))
        return self

    def sub(self, *cs):
        for c in cs:
            self.ops.append(('sub', c))
        return self

    @property
    def advance(self):
        return round(self.lsb + self.body + self.rsb)


def to_svg_d(contour, dx=0, top=ASC + 240):
    """font units -> svg coords (y down). top = font y mapped to svg y 0."""
    out = []
    last = None
    for s in contour:
        if s[0] == 'Z':
            out.append('Z')
            continue
        if s[0] == 'L' and last is not None and abs(s[1] - last[0]) < 0.05 and abs(s[2] - last[1]) < 0.05:
            continue
        last = (s[-2], s[-1])
        vals = list(s[1:])
        nums = []
        for i in range(0, len(vals), 2):
            nums.append(f"{vals[i] + dx:.1f} {top - vals[i + 1]:.1f}")
        out.append(s[0] + ' ' + ' '.join(nums))
    return ' '.join(out)


def flatten(contour, steps=14):
    pts = []
    cur = None
    for s in contour:
        if s[0] == 'M' or s[0] == 'L':
            cur = (s[1], s[2]); pts.append(cur)
        elif s[0] == 'C':
            x0, y0 = cur
            x1, y1, x2, y2, x3, y3 = s[1:]
            for i in range(1, steps + 1):
                t = i / steps; u = 1 - t
                x = u**3*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t**3*x3
                y = u**3*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t**3*y3
                pts.append((x, y))
            cur = (x3, y3)
    return pts
