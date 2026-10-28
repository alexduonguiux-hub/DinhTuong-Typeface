"""Concept v1 -> full charset (26/10, phương án B duyệt).

The approved control glyphs and every glyph that shares their rules are taken straight from
concept_v1.Build (one construction, one source); the rule functions the rest of the charset calls
(GL.tail = R5 with R2b weight units) are replaced by the concept versions, so C G 3 5 6 9 ß £ ...
follow the same rule without being redrawn by hand.

  pre()  : before GL.build_all()  -> patch rule functions
  post() : after  GL.build_all()  -> replace letters (before build_vn: đ, Vietnamese use them)
  figs() : after  GL.build_vn()   -> replace 2 and ?
"""
import glyphs_c as GL
import concept_v1 as CV
from geo import Glyph

B = CV.Build(GL.WEIGHT)
LETTERS = ['n', 'h', 'm', 'u', 'r', 'o', 'a', 'c', 'e', 'g', 'q', 'd', 'b', 'p', 's', 'H', 'O', 'S', 'C']
FIGS = {'two': '2', 'three': '3', 'question': '?'}


def _tail(cx, cedge, wall, stroke, side, vdir, tip_limit=None, **kw):
    return B.tail([], cx, cedge, wall, stroke, side, vdir, tip_limit, **kw)


def pre():
    GL.tail = _tail


def _sb(val):
    """concept sidebearings are written for the 46/34 grid; shift them onto this weight's table."""
    if val == 46:
        return GL.SB_STRAIGHT
    return val + (GL.SB_ROUND - 34)


def _glyph(gd, ch):
    old = GL.G.get(ch)
    g = Glyph(old.name if old else ch, gd['body'], _sb(gd['lsb']), _sb(gd['rsb']), ord(ch))
    g.ops = list(gd['ops'])
    GL.G[ch] = g
    return g


def _all():
    out = {}
    for gd in B.all() + B.extra():
        out[gd['name']] = gd
    return out


def _caps_notch():
    """R9c on the capitals' bowls (26/10 'thử'): B D P R. The stem's end that coincides with the
    bowl's flat edge is FLUSH (R4), and the bowl leaves the stem through the same 45° outer notch
    as the lowercase (depth per weight, <= 3/4 of H). The bowl's return into the stem stays whole."""
    from geo import Glyph
    V, H, HM, W8 = GL.V, GL.H, GL.HM, GL.WKC
    rr, fs, rect, FULL = GL.rrect, GL.fstem, GL.rect, GL.FULL
    def mk(ch, W, lsb, rsb, ops):
        g = Glyph(ch, W, lsb, rsb, ord(ch)); g.ops = ops; GL.G[ch] = g
    notch = lambda: B.notch_out([], V, GL.CAP, 'l', 'up', H)
    # B: upper and lower bowls; stem flush top and bottom (both ends are bowl edges)
    W, yb = 548, 296
    mk('B', W, GL.SB_STRAIGHT, GL.SB_ROUND, [('group', [
        ('add', rr(V / 2, yb, W - 30, GL.CAP, (0, FULL, FULL, 0))),
        ('add', rr(V / 2, 0, W, yb + HM, (0, FULL, FULL, 0))),
        ('add', fs(0, 0, V, GL.CAP, top=False, bot=False)),
        ('sub', rr(V - 1, yb + HM, W - 30 - V + 6, GL.CAP - H, (0, FULL, FULL, 0))),
        ('sub', rr(V - 1, H, W - V, yb, (0, FULL, FULL, 0))), notch()])])
    W = 572
    mk('D', W, GL.SB_STRAIGHT, GL.SB_ROUND, [('group', [
        ('add', fs(0, 0, V, GL.CAP, top=False, bot=False)),
        ('add', rr(V / 2, 0, W, GL.CAP, (0, FULL, FULL, 0))),
        ('sub', rr(V - 1, H, W - V, GL.CAP - H, (0, FULL, FULL, 0))), notch()])])
    W, yb = 532, 268
    mk('P', W, GL.SB_STRAIGHT, GL.SB_ROUND - 8, [('group', [
        ('add', fs(0, 0, V, GL.CAP, top=False)),
        ('add', rr(V / 2, yb, W, GL.CAP, (0, FULL, FULL, 0))),
        ('sub', rr(V - 1, yb + round(130 * W8), W - V, GL.CAP - H, (0, FULL, FULL, 0))), notch()])])
    W, yb = 548, 286
    lw = GL.diag_dx(GL.DIAG, 220, yb + 40) * 0.95
    mk('R', W, GL.SB_STRAIGHT, GL.SB_DIAG + 4, [('group', [
        ('add', fs(0, 0, V, GL.CAP, top=False, bot=True)),
        ('add', rr(V / 2, yb, W - 20, GL.CAP, (0, FULL, FULL, 0))),
        ('sub', rr(V - 1, yb + round(130 * W8), W - 20 - V, GL.CAP - H, (0, FULL, FULL, 0))), notch(),
        ('add', GL.stroke((W - 20 - V - lw / 2 + 70, yb + 30), (W - lw / 2, 0), lw)),
        ('sub', rect(V + 2, -300, W + 50, 0))])])


def post():
    A = _all()
    for ch in LETTERS:
        _glyph(A[ch], ch)
    # _caps_notch()   # tried 26/10 for B D P R, declined by the designer: capitals keep plain joints


OPEN_SIDE = 10     # R14 (v0.95): an open side (only tips reach it) gets the round side's ink sidebearing + 10


def _ink_x(g):
    import booleng
    xs = [s[i] for c in booleng.evaluate(g.ops) for s in c for i in range(1, len(s), 2)]
    return min(xs), max(xs)


def figs():
    A = _all()
    for n, ch in FIGS.items():
        _glyph(A[n], ch)
    # R14: the 3's left side is open (two tips cut inside the body, R5) -> spaced from its ink,
    # not from the body box; was ~60 units looser than every other figure (13 23 ... 93).
    z0 = GL.G['0']; x0, _ = _ink_x(z0)
    g = GL.G['3']; x3, _ = _ink_x(g)
    g.lsb = (z0.lsb + x0 + OPEN_SIDE) - x3
