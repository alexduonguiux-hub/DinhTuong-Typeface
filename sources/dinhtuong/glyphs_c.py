from geo import *

G = {}


def reg(g):
    G[g.name] = g
    return g


# ===================== MODULES =====================
def ring(x0, y0, x1, y1, sx, sy, R, r):
    """closed bowl: outer squircle-rect minus counter. sx = side stroke, sy = top/bottom stroke.
    R, r may be tuples (tl,tr,br,bl)."""
    return [('add', rrect(x0, y0, x1, y1, R)),
            ('sub', rrect(x0 + sx, y0 + sy, x1 - sx, y1 - sy, r))]


def arch(x0, x1, y_top, stem, bar, R, r, left_round=True, right_round=True, y0=0):
    """n-arch / A-arch: rounded top, open bottom."""
    Rt = (R if left_round else 0, R if right_round else 0, 0, 0)
    rt = (r if left_round else 0, r if right_round else 0, 0, 0)
    return [('add', rrect(x0, y0, x1, y_top, Rt)),
            ('sub', rrect(x0 + stem, y0 - 1, x1 - stem, y_top - bar, rt))]


def apply(g, ops):
    for op, c in ops:
        g.ops.append((op, c))
    return g


def vshape(x0, x1, top, bottom, dw, fb, trap=None):
    """V with flat vertex. dw = horizontal stroke width, fb = flat bottom width.
    trap = how much deeper than geometric the inner notch is cut (thins the vertex)."""
    c = (x0 + x1) / 2
    outer = poly([(x0, top), (x1, top), (c + fb / 2, bottom), (c - fb / 2, bottom)])
    # inner apex where inner edges (parallel, offset dw) meet at x=c
    run = (c - fb / 2) - x0
    t = (c - (x0 + dw)) / run
    yi = top - t * (top - bottom)
    if trap is None:
        trap = TRAP if (top - bottom) > 600 else TRAP * 0.8
    yi = max(bottom + 0.35 * fb, yi - trap)
    inner = poly([(x0 + dw, top + 1), (x1 - dw, top + 1), (c, yi)])
    return [('add', outer), ('sub', inner)]


def pinch(p0, p1, w, k=0.9):
    """diagonal with flat cuts, thinned to k*w at its midpoint (optical crossing compensation)."""
    (x0, y0), (x1, y1) = p0, p1
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    return poly([(x0 - w / 2, y0), (x0 + w / 2, y0), (xm + k * w / 2, ym), (x1 + w / 2, y1),
                 (x1 - w / 2, y1), (xm - k * w / 2, ym)])


def stroke(p0, p1, w):
    """diagonal stroke with flat horizontal cuts. p0,p1 = centre points at the cut lines,
    w = horizontal width."""
    (x0, y0), (x1, y1) = p0, p1
    return poly([(x0 - w / 2, y0), (x0 + w / 2, y0), (x1 + w / 2, y1), (x1 - w / 2, y1)])


# DIAGONAL RULE (optical): a diagonal looks heavier than a vertical of the same
# perpendicular width, and diagonals pile ink where they meet. So diagonals are
# drawn THINNER than the stems, thinner still when several meet, and the inner
# crotch of a vertex is cut deeper (ink trap) instead of meeting at full weight.
DIAG = round(V * 0.90)        # 158  single diagonal (V, N, K leg, R leg, A in B)
DIAG_K_ARM = round(V * 0.86)  # 151  K arm (meets stem + leg)
DIAG_Y = round(V * 0.88)      # 155  Y arms (meet into the stem)
DIAG_X = round(V * 0.88)      # 155  X (crossing, plus 10% pinch)
DIAG_MULTI = round(V * 0.84)  # 148  W, M-notch (four diagonals per glyph)
DIAG_Z = round(V * 0.92)      # 162  Z spine (between its 146 bars and 176 stems)
diag = round(v * 0.90)        # 142
diag_k_arm = round(v * 0.86)  # 136
diag_y = round(v * 0.88)      # 139
diag_x = round(v * 0.88)      # 139
diag_multi = round(v * 0.84)  # 133
diag_z = round(v * 0.92)      # 145
TRAP = 34                     # extra depth of the inner vertex notch (units, caps; lc uses 0.8x)


# ===================== UPPERCASE =====================
def cap_A():
    W = 604
    g = Glyph('A', W, SB_ROUND + 6, SB_ROUND + 6, 0x41)
    apply(g, arch(0, W, CAP + OV_C, V, H, RO, RI))
    g.add(rect(V - 1, 206, W - V + 1, 206 + HM))
    return reg(g)


def cap_B():
    W = 584
    g = Glyph('B', W, SB_STRAIGHT, SB_ROUND, 0x42)
    yb = 300
    g.group([('add', rrect(0, yb, W - 34, CAP, (0, 200, 186, 0))),
             ('add', rrect(0, 0, W, yb + HM, (0, 214, RO, 0))),
             ('add', rect(0, 0, V, CAP)),
             ('sub', rrect(V, yb + HM, W - 34 - 166, CAP - H, (0, RI, RI, 0))),
             ('sub', rrect(V, H, W - V, yb, (0, RI, RI, 0)))])
    return reg(g)


def cap_C():
    W = 598
    g = Glyph('C', W, SB_ROUND, SB_ROUND - 34, 0x43)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, RO, RI))
    g.sub(rect(W * 0.5, H - OV_C + 70, W + 1, CAP + OV_C - H - 70))
    g.sub(rect(W - 58, -OV_C - 1, W + 1, CAP + OV_C + 1))
    return reg(g)


def cap_D():
    W = 612
    g = Glyph('D', W, SB_STRAIGHT, SB_ROUND, 0x44)
    apply(g, ring(0, 0, W, CAP, V, H, (0, RO, RO, 0), (0, RI, RI, 0)))
    return reg(g)


def cap_E():
    W = 478
    g = Glyph('E', W, SB_STRAIGHT, SB_STRAIGHT - 16, 0x45)
    g.add(rect(0, 0, V, CAP), rect(0, CAP - H, W, CAP), rect(0, 0, W, H),
          rect(0, 286, W - 34, 286 + HM))
    return reg(g)


def cap_F():
    W = 462
    g = Glyph('F', W, SB_STRAIGHT, SB_STRAIGHT - 24, 0x46)
    g.add(rect(0, 0, V, CAP), rect(0, CAP - H, W, CAP), rect(0, 270, W - 40, 270 + HM))
    return reg(g)


def cap_G():
    W = 616
    g = Glyph('G', W, SB_ROUND, SB_ROUND, 0x47)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, RO, RI))
    yb = 270
    g.sub(rect(W * 0.5, yb + HM, W + 1, CAP + OV_C - H - 70))
    g.sub(rect(W - 58, yb + HM, W + 1, CAP + OV_C + 1))
    g.add(rect(W * 0.5 - 14, yb, W, yb + HM))
    return reg(g)


def cap_H():
    W = 596
    g = Glyph('H', W, SB_STRAIGHT, SB_STRAIGHT, 0x48)
    g.add(rect(0, 0, V, CAP), rect(W - V, 0, W, CAP), rect(V - 1, 292, W - V + 1, 292 + HM))
    return reg(g)


def cap_I():
    g = Glyph('I', V, SB_STRAIGHT, SB_STRAIGHT, 0x49)
    g.add(rect(0, 0, V, CAP))
    return reg(g)


def cap_J():
    W = 512
    g = Glyph('J', W, SB_ROUND - 14, SB_STRAIGHT, 0x4A)
    apply(g, ring(0, -OV_C, W, CAP + 400, V, H, (0, 0, RO, RO), (0, 0, RI, RI)))
    g.sub(rect(-1, CAP, W + 1, CAP + 401))
    g.sub(rect(-1, 236, V + 1, CAP + 1))
    return reg(g)


def cap_K():
    W = 612
    g = Glyph('K', W, SB_STRAIGHT, SB_DIAG, 0x4B)
    g.add(rect(0, 0, V, CAP))
    aw = diag_dx(DIAG_K_ARM, W - V - 60, CAP - 300)
    g.add(stroke((V + 20, 250), (W - aw / 2, CAP), aw))
    lw = diag_dx(DIAG, W - V - 120, 380) * (158 / 185.1) * (158 / 152.6)  # calibrated
    g.add(stroke((V + 70 + lw / 2 - 40, 400), (W - lw / 2, 0), lw))
    g.sub(rect(-200, -400, -1, CAP + 400))  # clean anything left of stem
    g.sub(rect(-200, CAP, W + 200, CAP + 400))
    g.sub(rect(-200, -400, W + 200, 0))
    return reg(g)


def cap_L():
    W = 468
    g = Glyph('L', W, SB_STRAIGHT, SB_STRAIGHT - 24, 0x4C)
    g.add(rect(0, 0, V, CAP), rect(0, 0, W, H))
    return reg(g)


def cap_M():
    VM = 166
    cw = 128
    W = 3 * VM + 2 * cw
    Ra = 178
    g = Glyph('M', W, SB_STRAIGHT - 8, SB_STRAIGHT - 8, 0x4D)
    mid0 = VM + cw
    g.group(arch(0, mid0 + VM, CAP + OV_C, VM, H, Ra, RI))
    g.group(arch(mid0, W, CAP + OV_C, VM, H, Ra, RI))
    return reg(g)


def cap_N():
    W = 604
    VN = 164
    g = Glyph('N', W, SB_STRAIGHT, SB_STRAIGHT, 0x4E)
    dw = diag_dx(DIAG, W - 210, CAP)
    g.add(rect(0, 0, VN, CAP), rect(W - VN, 0, W, CAP))
    g.add(poly([(0, CAP), (dw, CAP), (W, 0), (W - dw, 0)]))
    return reg(g)


def cap_O():
    W = 648
    g = Glyph('O', W, SB_ROUND, SB_ROUND, 0x4F)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, RO, RI))
    return reg(g)


def cap_P():
    W = 572
    g = Glyph('P', W, SB_STRAIGHT, SB_ROUND - 10, 0x50)
    yb = 246
    g.add(rect(0, 0, V, CAP))
    sy = (HM + H) / 2
    g.add(rrect(V / 2, yb, W, CAP, (0, RO, RO, 0)))
    g.sub(rrect(V - 1, yb + sy, W - V, CAP - sy, (0, RI, RI, 0)))
    return reg(g)


def cap_Q():
    W = 648
    g = Glyph('Q', W, SB_ROUND, SB_ROUND - 4, 0x51)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, RO, RI))
    tw = diag_dx(156, 220, 290)
    g.add(stroke((W * 0.6, 196), (W - 52, -92), tw))
    return reg(g)


def cap_R():
    W = 590
    g = Glyph('R', W, SB_STRAIGHT, SB_DIAG + 4, 0x52)
    yb = 270
    g.add(rect(0, 0, V, CAP))
    apply(g, ring(0, yb, W - 18, CAP, V, (HM + H) / 2, (0, RO, RO, 0), (0, RI, RI, 0)))
    lw = diag_dx(DIAG, 230, yb + 40)
    g.add(stroke((W - 18 - V - lw / 2 + 80, yb + 40), (W - lw / 2, 0), lw))
    g.sub(rect(-1, -300, W + 50, 0))
    return reg(g)


def s_shape(W, T, ov, sx, sy, sm, R1, R2, r, gap_u, gap_l, top_inset=26):
    """Geometric S: two stacked rings sharing the spine, each with one side opened.
    sm = spine thickness. 26/10 house hook cut: each free end is cut VERTICALLY on its counter's
    wall (where the counter's arc meets its straight wall), with no level cut."""
    ym = (T - sm) / 2 + 8
    xr_u = W - top_inset / 2 - sx                       # upper counter's right wall
    ru = min(xr_u - (top_inset / 2 + sx), T + ov - sy - ym - sm) / 2
    cyu = T + ov - sy - ru                              # where that wall starts (arc/wall junction)
    rl = min(W - 2 * sx, ym - (-ov + sy)) / 2
    cyl = -ov + sy + rl
    up = [('add', rrect(top_inset / 2, ym, W - top_inset / 2, T + ov, R1)),
          ('sub', rrect(top_inset / 2 + sx, ym + sm, W - top_inset / 2 - sx, T + ov - sy, r)),
          ('sub', rect(W / 2, ym - 1, W + 1, cyu)),
          ('sub', rect(xr_u, cyu - 1, W + 1, T + ov + 1))] + \
         [b for b in [blunt_tip(xr_u - ru, cyu, ru, xr_u, 'r', 'up', sx)] if b]
    lo = [('add', rrect(0, -ov, W, ym + sm, R2)),
          ('sub', rrect(sx, -ov + sy, W - sx, ym, r)),
          ('sub', rect(-1, cyl, W / 2 - 3, ym + sm + 1)),
          ('sub', rect(-1, -ov - 1, sx, cyl + 1))] + \
         [b for b in [blunt_tip(sx + rl, cyl, rl, sx, 'l', 'down', sx)] if b]
    return up, lo


def cap_S():
    W = 576
    g = Glyph('S', W, SB_ROUND, SB_ROUND, 0x53)
    up, lo = s_shape(W, CAP, OV_C, V - 8, H, HM, 212, 226, RI, 64, 64)
    g.group(up)
    g.group(lo)
    return reg(g)


def cap_T():
    W = 572
    g = Glyph('T', W, SB_DIAG + 4, SB_DIAG + 4, 0x54)
    g.add(rect(0, CAP - H, W, CAP), rect((W - V) / 2, 0, (W + V) / 2, CAP))
    return reg(g)


def cap_U():
    W = 604
    g = Glyph('U', W, SB_STRAIGHT, SB_STRAIGHT, 0x55)
    apply(g, ring(0, -OV_C, W, CAP + 400, V, H, (0, 0, RO, RO), (0, 0, RI, RI)))
    g.sub(rect(-1, CAP, W + 1, CAP + 401))
    return reg(g)


def cap_V():
    W = 640
    g = Glyph('V', W, SB_DIAG, SB_DIAG, 0x56)
    dw = diag_dx(DIAG, W / 2 - 60, CAP)
    apply(g, vshape(0, W, CAP, 0, dw, 168))
    return reg(g)


def cap_W():
    W1 = 520
    dw = diag_dx(DIAG_MULTI, W1 / 2 - 40, CAP)
    W = 2 * W1 - dw
    g = Glyph('W', W, SB_DIAG, SB_DIAG, 0x57)
    g.group(vshape(0, W1, CAP, 0, dw, 140))
    g.group(vshape(W - W1, W, CAP, 0, dw, 140))
    return reg(g)


def cap_X():
    W = 624
    g = Glyph('X', W, SB_DIAG, SB_DIAG, 0x58)
    dw = diag_dx(DIAG_X, W - 200, CAP) * (155 / 149.3)  # calibrated
    g.add(pinch((dw / 2, CAP), (W - dw / 2, 0), dw))
    g.add(pinch((W - dw / 2, CAP), (dw / 2, 0), dw))
    return reg(g)


def cap_Y():
    W = 628
    g = Glyph('Y', W, SB_DIAG, SB_DIAG, 0x59)
    dw = diag_dx(DIAG_Y, W / 2 - 60, CAP - 300) * (155 / 163.3)  # calibrated to measured perpendicular
    c = W / 2
    g.group(vshape(0, W, CAP, 230, dw, V))
    g.add(rect(c - V / 2, 0, c + V / 2, 300))
    return reg(g)


def cap_Z():
    W = 548
    g = Glyph('Z', W, SB_ROUND, SB_ROUND, 0x5A)
    dw = diag_dx(DIAG_Z, W - 240, CAP - 2 * H) * (162 / 155.4)  # calibrated
    g.add(rect(0, CAP - H, W, CAP), rect(0, 0, W, H))
    g.add(poly([(W - dw, CAP - H + 1), (W, CAP - H + 1), (dw, H - 1), (0, H - 1)]))
    return reg(g)


# ===================== LOWERCASE =====================
def lc_bowl(g, W, stem_side=None, top=XH, ov=OV_L):
    """o-bowl; stem_side 'r'/'l' flattens the corners that meet a stem."""
    if stem_side == 'r':
        R, r = (ro, 0, 0, ro), (ri, 0, 0, ri)
    elif stem_side == 'l':
        R, r = (0, ro, ro, 0), (0, ri, ri, 0)
    else:
        R, r = ro, ri
    return apply(g, ring(0, -ov, W, top + ov, v, h, R, r))


def lc_a():
    W = 500
    g = Glyph('a', W, SB_ROUND, SB_STRAIGHT, 0x61)
    lc_bowl(g, W, 'r')
    return reg(g)


def lc_b():
    W = 500
    g = Glyph('b', W, SB_STRAIGHT, SB_ROUND, 0x62)
    lc_bowl(g, W, 'l')
    g.add(rect(0, -OV_L, v, ASC))
    return reg(g)


def lc_c():
    W = 470
    g = Glyph('c', W, SB_ROUND, SB_ROUND - 30, 0x63)
    lc_bowl(g, W)
    g.sub(rect(W * 0.5, h - OV_L + 54, W + 1, XH + OV_L - h - 54))
    g.sub(rect(W - 48, -OV_L - 1, W + 1, XH + OV_L + 1))
    return reg(g)


def lc_d():
    W = 500
    g = Glyph('d', W, SB_ROUND, SB_STRAIGHT, 0x64)
    lc_bowl(g, W, 'r')
    g.add(rect(W - v, -OV_L, W, ASC))
    return reg(g)


def lc_e():
    W = 492
    g = Glyph('e', W, SB_ROUND, SB_ROUND - 4, 0x65)
    lc_bowl(g, W)
    yb = 222
    g.add(rect(v - 1, yb, W - v + 1, yb + h - 12))
    g.sub(rect(W * 0.5, h - OV_L + 46, W + 1, yb))
    g.sub(rect(W - 48, -OV_L - 1, W + 1, yb))
    return reg(g)


def lc_f():
    W = 352
    s0 = 46
    g = Glyph('f', W, SB_DIAG + 4, -18, 0x66)
    g.group([('add', rrect(s0, 0, W, ASC, (170, 170, 0, 0))),
             ('sub', rrect(s0 + v, -1, W + 1, ASC - h + 4, (ri, 0, 0, 0))),
             ('sub', rect(W - 40, -1, W + 1, ASC + 1))])
    g.add(rect(0, XH - h + 6, W - 52, XH))
    return reg(g)


def lc_g():
    W = 500
    g = Glyph('g', W, SB_ROUND, SB_STRAIGHT, 0x67)
    g.group([('add', rrect(0, DESC, W, 60, (0, 0, ro, ro))),
             ('sub', rrect(v, DESC + h, W - v, 61, (0, 0, ri, ri))),
             ('sub', rect(-1, DESC + h + 66, W - v, 61))])
    g.add(rect(W - v, -10, W, XH))
    lc_bowl(g, W, 'r')
    return reg(g)


def lc_h():
    W = 494
    g = Glyph('h', W, SB_STRAIGHT, SB_STRAIGHT, 0x68)
    apply(g, arch(0, W, XH + OV_L, v, h, ro, ri, left_round=False))
    g.add(rect(0, 0, v, ASC))
    return reg(g)


def tittle(cx, y0, w=v + 4, hgt=150):
    return rrect(cx - w / 2, y0, cx + w / 2, y0 + hgt, 40)


def lc_i():
    g = Glyph('i', v, SB_STRAIGHT, SB_STRAIGHT, 0x69)
    g.add(rect(0, 0, v, XH), tittle(v / 2, ASC - 150))
    return reg(g)


def lc_j():
    W = 300
    g = Glyph('j', W, SB_STRAIGHT - (W - v), SB_STRAIGHT, 0x6A)
    g.group([('add', rrect(0, DESC, W, XH, (0, 0, ro, 0))),
             ('sub', rrect(-1, DESC + h, W - v, XH + 1, (0, 0, ri, 0))),
             ])
    g.add(tittle(W - v / 2, ASC - 150))
    return reg(g)


def lc_k():
    W = 476
    g = Glyph('k', W, SB_STRAIGHT, SB_DIAG - 4, 0x6B)
    g.add(rect(0, 0, v, ASC))
    aw = diag_dx(diag_k_arm, W - v - 40, XH - 190)
    g.add(stroke((v + 14, 180), (W - aw / 2, XH), aw))
    lw = diag_dx(diag, W - v - 100, 290) * (142 / 166.2) * (142 / 136.9)  # calibrated
    g.add(stroke((v + 50 + lw / 2 - 30, 300), (W - lw / 2, 0), lw))
    g.sub(rect(-200, -400, -1, XH + 400), rect(v, XH, W + 200, XH + 400),
          rect(-200, -400, W + 200, 0))
    return reg(g)


def lc_l():
    g = Glyph('l', v, SB_STRAIGHT, SB_STRAIGHT, 0x6C)
    g.add(rect(0, 0, v, ASC))
    return reg(g)


def lc_m():
    vm = 150
    cw = 118
    W = 3 * vm + 2 * cw
    g = Glyph('m', W, SB_STRAIGHT, SB_STRAIGHT, 0x6D)
    mid0 = vm + cw
    g.group(arch(0, mid0 + vm, XH + OV_L, vm, h, 150, ri, left_round=False))
    g.group(arch(mid0, W, XH + OV_L, vm, h, 150, ri))
    return reg(g)


def lc_n():
    W = 494
    g = Glyph('n', W, SB_STRAIGHT, SB_STRAIGHT, 0x6E)
    apply(g, arch(0, W, XH + OV_L, v, h, ro, ri, left_round=False))
    return reg(g)


def lc_o():
    W = 516
    g = Glyph('o', W, SB_ROUND, SB_ROUND, 0x6F)
    lc_bowl(g, W)
    return reg(g)


def lc_p():
    W = 500
    g = Glyph('p', W, SB_STRAIGHT, SB_ROUND, 0x70)
    lc_bowl(g, W, 'l')
    g.add(rect(0, DESC, v, XH + OV_L))
    return reg(g)


def lc_q():
    W = 500
    g = Glyph('q', W, SB_ROUND, SB_STRAIGHT, 0x71)
    lc_bowl(g, W, 'r')
    g.add(rect(W - v, DESC, W, XH + OV_L))
    return reg(g)


def lc_r():
    W = 352
    g = Glyph('r', W, SB_STRAIGHT, SB_DIAG + 4, 0x72)
    g.add(rect(0, 0, v, XH))
    g.group([('add', rrect(0, 0, W, XH + OV_L, (0, 176, 0, 0))),
             ('sub', rrect(v, -1, W + 1, XH + OV_L - h, (ri, 0, 0, 0))),
             ])
    g.add(rect(0, 0, v, XH))
    return reg(g)


def lc_s():
    W = 468
    g = Glyph('s', W, SB_ROUND, SB_ROUND, 0x73)
    up, lo = s_shape(W, XH, OV_L, v - 8, h, h - 6, 168, 178, ri, 46, 46, top_inset=20)
    g.group(up)
    g.group(lo)
    return reg(g)


def lc_t():
    W = 346
    s0 = 44
    g = Glyph('t', W, SB_DIAG + 4, -14, 0x74)
    g.group([('add', rrect(s0, -OV_L, W, 680, (0, 0, 170, 0))),
             ('sub', rrect(s0 + v, h - OV_L, W + 1, 681, (0, 0, ri, 0))),
             ('sub', rect(W - 40, -OV_L - 1, W + 1, 681))])
    g.add(rect(0, XH - h + 6, W - 46, XH))
    return reg(g)


def lc_u():
    W = 494
    g = Glyph('u', W, SB_STRAIGHT, SB_STRAIGHT, 0x75)
    for op, c in arch(0, W, XH + OV_L, v, h, ro, ri, left_round=False):
        g.ops.append((op, rot180(c, W / 2, (XH) / 2)))
    return reg(g)


def lc_v():
    W = 520
    g = Glyph('v', W, SB_DIAG, SB_DIAG, 0x76)
    dw = diag_dx(diag, W / 2 - 50, XH)
    apply(g, vshape(0, W, XH, 0, dw, 140))
    return reg(g)


def lc_w():
    W1 = 440
    dw = diag_dx(diag_multi, W1 / 2 - 34, XH)
    W = 2 * W1 - dw
    g = Glyph('w', W, SB_DIAG, SB_DIAG, 0x77)
    g.group(vshape(0, W1, XH, 0, dw, 118))
    g.group(vshape(W - W1, W, XH, 0, dw, 118))
    return reg(g)


def lc_x():
    W = 510
    g = Glyph('x', W, SB_DIAG, SB_DIAG, 0x78)
    dw = diag_dx(diag_x, W - 170, XH) * (139 / 135.0)  # calibrated
    g.add(pinch((dw / 2, XH), (W - dw / 2, 0), dw))
    g.add(pinch((W - dw / 2, XH), (dw / 2, 0), dw))
    return reg(g)


def lc_y():
    W = 520
    g = Glyph('y', W, SB_DIAG, SB_DIAG, 0x79)
    dw = diag_dx(diag, W / 2 - 50, XH) * (142 / 147.9)  # calibrated
    c = W / 2
    vx = c - 34                      # where the left arm lands on the baseline
    g.add(stroke((dw / 2, XH), (vx, 0), dw))
    xr = W - dw / 2
    s_ = (vx + 40 - xr) / (0 - XH)   # right arm passes just right of the vertex
    g.add(stroke((xr, XH), (xr + s_ * (DESC - XH), DESC), dw))
    return reg(g)


def lc_z():
    W = 446
    g = Glyph('z', W, SB_ROUND, SB_ROUND, 0x7A)
    dw = diag_dx(diag_z, W - 200, XH - 2 * h)
    g.add(rect(0, XH - h, W, XH), rect(0, 0, W, h))
    g.add(poly([(W - dw, XH - h + 1), (W, XH - h + 1), (dw, h - 1), (0, h - 1)]))
    return reg(g)


def build_all():
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, '__name__', '').startswith(('cap_', 'lc_')) and fn.__name__ not in ('lc_bowl',):
            fn()
    return G


# ===================== VIETNAMESE MARK SYSTEM =====================
# Marks are built from the same vocabulary: diagonal slabs with flat cuts,
# the arch module (breve), the tittle (dot below), the stem stub (horn).
# Each mark is defined around x=0 with its BOTTOM at y=0; placement adds the zone height.
MT = 86          # mark stroke (heavy, ~47% of v) so marks hold up at black weight
MH = 168         # mark height (lowercase)


def mk_acute(hgt=MH, w=142):
    return [('add', stroke((-40, 0), (46, hgt), w))]


def mk_grave(hgt=MH, w=142):
    return [('add', stroke((40, 0), (-46, hgt), w))]


def mk_circumflex(hgt=142, half=152, dw=104, fb=86):
    ops = vshape(-half, half, hgt, 0, dw, fb)
    return [(op, mirror_y(c, hgt / 2)) for op, c in ops]


def mk_breve(hgt=126, half=134, side=80, bot=72):
    return [('add', rrect(-half, 0, half, hgt + 60, (0, 0, 66, 66))),
            ('sub', rrect(-half + side, bot, half - side, hgt + 61, (0, 0, 18, 18))),
            ('sub', rect(-half - 1, hgt, half + 1, hgt + 61))]


def mk_hook(hgt=184):
    # an upright '7' hook: top bar from the arch module bending into a stem stub
    return [('add', rrect(-92, 0, 66, hgt, (46, 66, 0, 0))),
            ('sub', rrect(-93, -1, 66 - 80, hgt - 68, (0, 22, 0, 0)))]


def mk_tilde(hgt=122, half=150, side=62, bar=56):
    # squared wave: an arch and a cup sharing one middle leg
    mid = side / 2
    a = [('add', rrect(-half, 30, mid, hgt, (52, 52, 0, 0))),
         ('sub', rrect(-half + side, 29, mid - side, hgt - bar, (14, 14, 0, 0)))]
    b = [('add', rrect(-mid, 0, half, hgt - 30, (0, 0, 52, 52))),
         ('sub', rrect(-mid + side, bar, half - side, hgt - 29, (0, 0, 14, 14)))]
    return [('group', a), ('group', b)]


def mk_dotbelow():
    return [('add', rrect(-(v + 4) / 2, -150, (v + 4) / 2, 0, 40))]


MARKS = {
    'acute': mk_acute, 'grave': mk_grave, 'circumflex': mk_circumflex, 'breve': mk_breve,
    'hook': mk_hook, 'tilde': mk_tilde,
}

ZONE_LC = XH + 58      # bottom of lowercase marks
ZONE_UC = CAP + 48     # bottom of uppercase marks
CAP_SCALE = 0.84       # cap marks are flatter so stacks fit the line


def scale_ops(ops, sx, sy):
    out = []
    for op, c in ops:
        if op == 'group':
            out.append((op, scale_ops(c, sx, sy)))
        else:
            out.append((op, transform(c, lambda x, y: (x * sx, y * sy))))
    return out


def shift_ops(ops, dx, dy):
    out = []
    for op, c in ops:
        if op == 'group':
            out.append((op, shift_ops(c, dx, dy)))
        else:
            out.append((op, shift(c, dx, dy)))
    return out


MARK_NOSCALE = set()      # v0.95b: marks built at their final size (the strips)
MARK_TOP = {}             # v0.95c: absolute top line of a mark wherever it sits (sắc)
MARK_STACK_FN = {}        # v0.95c: tighter same-thickness builders for tones riding on mũ / trăng
MARK_STACK_LEN = {}       # v0.95b: strip length when stacked with mũ / trăng


ACUTE_STACK_GAP = 40      # R8f (28/10, approved C + pull-left): sắc–trăng and sắc–mũ ink gap, Regular units, every weight; ấ ắ ế ố share one top line


def ACUTE_TOPLINE():
    return __import__('os').environ.get('ACUTE_TOPLINE', '4') in ('1', '2', '3', '4', '5')


ACUTE_R8I_GAP = 35        # R8i v2 (31/10 sample): sắc–trăng ink gap on Ắ (sample 35); Ấ shares Ắ's height (one top line, sample 865 / 865)
ACUTE_R8I_LC_GAP = 40     # R8i v2: lowercase ấ ế ố — sắc–mũ gap (sample 41; = the R8f stack gap 40)
ACUTE_R8I_LC_DX = 212     # R8k-b (31/10 'dời dấu sắc ra sau như này', sample Ấ ấ): the sắc rides BEHIND the mũ, over its right arm —
                          # its centre 212 right of the mũ's centre on ấ ế ố (left end 115 past the mũ's centre), height by the 40 gap
ACUTE_R8K_UC_DX = 189     # R8k-b: on Ấ Ế Ố the centre is 189 right of the mũ's centre (left end 92 past it); height = Ắ's line


_CFOOT = {}


def CLEAR_UP(ops, other_ops, gap):
    """R8k: lift ops (never lower) until their ink keeps gap from other_ops."""
    import mark_qa as MQ
    o = MQ.raster(other_ops)
    if MQ.min_dist(o, MQ.raster(ops)) >= gap: return ops
    lo, hi = 0.0, 300.0
    for _ in range(16):
        mid = (lo + hi) / 2
        if MQ.min_dist(o, MQ.raster(shift_ops(ops, 0, mid))) >= gap: hi = mid
        else: lo = mid
    return shift_ops(ops, 0, hi)


def CIRC_FOOT(base_ops, cx, zone, key=None):
    """R8k: the mũ's foot relative to the mark zone — the lowest height at which its ink keeps CIRC_R8K_GAP (40) from
    the letter's ink (sample Â 41, â 40). 0 when the R8k mũ is off."""
    mf = __import__('marks_flat')
    if not mf.R8I(): return 0.0
    if key is not None and key in _CFOOT: return _CFOOT[key]
    import mark_qa as MQ
    b = MQ.raster(base_ops)
    lo, hi = -250.0, 250.0
    for _ in range(18):
        mid = (lo + hi) / 2
        if MQ.min_dist(b, MQ.raster(shift_ops(mark_ops('circumflex', True), cx, zone + mid))) >= mf.CIRC_R8K_GAP: hi = mid
        else: lo = mid
    if key is not None: _CFOOT[key] = hi
    return hi
ACUTE_R8I_BREVE_DX = 62   # R8i v2: on the trăng the sắc's centre is 62 right of the axis (sample Ắ +62)


def ACUTE_MODE():
    return __import__('os').environ.get('ACUTE_TOPLINE', '4')


_CIRC_Y = {}


def ACUTE_IN_DX(dx0, base_ops, cx):
    """R8k-c (31/10 'điều chỉnh cho nằm trong glyph dựng'): the sắc behind the mũ never runs past the letter's own ink
    on the right — its right end stops at the base's right edge (Ế ấ ế ố were 49-95 past it)."""
    s = __import__('marks_flat').ACUTE_R8I_SPAN
    return min(dx0, ops_xrange(base_ops)[1] - cx - s / 2)


def ACUTE_CIRC_Y(upper=True, dxa=None):
    """R8i/R8k: the lowest height (over the mũ's own foot) at which the sắc keeps its gap from the mũ: lowercase
    ACUTE_R8I_LC_GAP at ACUTE_R8I_LC_DX; capitals ACUTE_R8I_GAP, centred."""
    gap, d0 = (ACUTE_R8I_GAP, ACUTE_R8K_UC_DX) if upper else (ACUTE_R8I_LC_GAP, ACUTE_R8I_LC_DX)
    dxa = d0 if dxa is None else dxa
    key = (upper, round(dxa, 1))
    if key in _CIRC_Y: return _CIRC_Y[key]
    import mark_qa as MQ
    ci = MQ.raster(mark_ops('circumflex', True))
    lo, hi = 0.0, 400.0
    for _ in range(16):
        mid = (lo + hi) / 2
        if MQ.min_dist(ci, MQ.raster(shift_ops(mark_ops('acute', True), dxa, mid))) >= gap: hi = mid
        else: lo = mid
    _CIRC_Y[key] = hi
    return hi


ACUTE_SIDE_GAP = 30       # R8g (28/10 13:12, designer's ế sample): sắc BESIDE the mũ, ink gap 30 (= R8 mark–mark floor)


def ACUTE_BESIDE():
    return __import__('os').environ.get('ACUTE_TOPLINE', '4') == '3'


_BESIDE = {}


def ACUTE_BESIDE_DX(upper=True):
    """R8g (28/10 13:12 'thử đổi dấu sắc theo kiểu như này để chiều cao dấu các chữ á ấ đều bằng nhau', sample ế):
    on ấ ế ố the sắc is NOT raised: it stands on the mark zone exactly like the lone sắc of á (same foot, same 216
    length, same top), beside the mũ's right foot, as close as the ink gap ACUTE_SIDE_GAP allows. Returns the x of
    the sắc's axis relative to the mũ's centre."""
    if upper in _BESIDE: return _BESIDE[upper]
    import mark_qa as MQ
    ci = MQ.raster(mark_ops('circumflex', upper))
    L = __import__('marks_flat').ACUTE_L
    def gap(dx):
        return MQ.min_dist(ci, MQ.raster(shift_ops(mark_ops('acute', upper, L), dx, 0)))
    lo, hi = 0.0, 700.0
    for _ in range(18):
        mid = (lo + hi) / 2
        if gap(mid) >= ACUTE_SIDE_GAP: hi = mid
        else: lo = mid
    _BESIDE[upper] = hi
    return hi


_STACK_Y = {}


def ACUTE_STACK_Y():
    """R8f: the height (over the mark zone) of the sắc's foot on ắ. Mode 1: 40 over the trăng's arm tops. Mode 2
    (compact): the lowest foot that keeps the sắc 40 (Regular units) from the trăng's ink — the tilted strip dips
    into the trăng's open cup, as Inter / FreeSans stack it. ấ ế ố then use the SAME foot height, so every stacked
    sắc ends on one line."""
    mode = __import__('os').environ.get('ACUTE_TOPLINE', '4')
    if mode in _STACK_Y: return _STACK_Y[mode]
    hb = MARK_HGT['breve'] * CAP_SCALE
    if mode not in ('2', '3', '4', '5'):        # R8g keeps R8f's compact sắc on the trăng (ắ)
        _STACK_Y[mode] = hb + ACUTE_STACK_GAP; return _STACK_Y[mode]
    import mark_qa as MQ
    br = MQ.raster(mark_ops('breve', True))
    def gap(y):
        ac = shift_ops(shift_ops(mark_ops('acute', True, __import__('marks_flat').ACUTE_L), ACUTE_FOOT_DX(), 0), 0, y)
        return MQ.min_dist(br, MQ.raster(ac))
    lo, hi = 0.0, hb + 120.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if gap(mid) >= (ACUTE_R8I_GAP if mode in ('4', '5') else ACUTE_STACK_GAP): hi = mid
        else: lo = mid
    if mode in ('4', '5') and not __import__('marks_flat').R8I():
        # R8i v2 QA: Ấ and Ắ share ONE line (sample 865 / 865), but the line must also keep Ấ's centred sắc
        # ACUTE_R8I_GAP from the mũ (Regular: the trăng-only solve left Ấ at 26 < the 30 floor). Line = the higher solve.
        ci = MQ.raster(mark_ops('circumflex', True))
        lo2, hi2 = 0.0, hb + 160.0
        for _ in range(14):
            mid = (lo2 + hi2) / 2
            if MQ.min_dist(ci, MQ.raster(shift_ops(mark_ops('acute', True), 0, mid))) >= ACUTE_R8I_GAP: hi2 = mid
            else: lo2 = mid
        hi = max(hi, hi2)
    _STACK_Y[mode] = hi
    return hi


_CIRC_DX = {}


def ACUTE_CIRC_DX(dx0, ydy, upper=True):
    """R8f (28/10 11:13 'dời dấu sắc gần dấu ô lại … qua trái — lệch phải tạo cảm giác nó xa'): once the sắc on ấ ế ố
    is raised to the common top line, it is pulled LEFT toward the mũ until its ink is ACUTE_STACK_GAP (40, Regular
    units) from the mũ — the same gap it keeps from the trăng on ắ. Never moved right of where it hung before."""
    if __import__('os').environ.get('ACUTE_TOPLINE', '4') != '2': return dx0
    key = (round(dx0, 2), round(ydy, 2), upper)
    if key in _CIRC_DX: return _CIRC_DX[key]
    import mark_qa as MQ
    ci = MQ.raster(mark_ops('circumflex', upper))
    L = __import__('marks_flat').ACUTE_L
    def gap(dx):
        return MQ.min_dist(ci, MQ.raster(shift_ops(shift_ops(mark_ops('acute', upper, L), ACUTE_FOOT_DX(), 0), dx, ydy)))
    if gap(dx0) <= ACUTE_STACK_GAP:
        _CIRC_DX[key] = dx0; return dx0
    lo, hi = dx0 - 400.0, dx0
    for _ in range(16):
        mid = (lo + hi) / 2
        if gap(mid) >= ACUTE_STACK_GAP: hi = mid
        else: lo = mid
    _CIRC_DX[key] = hi
    return hi


def ACUTE_FOOT_DX():
    """R8e: half the horizontal run of the tilted sắc strip (0 when it stands)."""
    mf = __import__('marks_flat')
    if mf.R8I():                               # R8i v2: on the trăng the sắc's centre sits 62 right of the axis (sample Ắ)
        return ACUTE_R8I_BREVE_DX
    return mf.ACUTE_L * _m.tan(_m.radians(mf.ACUTE_TILT)) / 2


def mark_ops(name, upper=False, length=None):
    ops = MARKS[name]() if length is None else MARKS[name](length=length)
    if upper and name not in MARK_NOSCALE:
        ops = scale_ops(ops, 0.96, CAP_SCALE)
    return ops


# horn and stroke (Đ) are attached parts, not floating marks
def horn_ops(x_right, y_top, upper=False):
    w, up = (146, 122) if upper else (128, 108)
    return [('add', rrect(x_right - 46, y_top - 150, x_right + w - 46, y_top + up, (0, 56, 0, 0))),
            ('sub', rect(x_right + w - 46 - 1, -1000, x_right + w, y_top + up - 70))]


def dotless_i():
    g = Glyph('dotlessi', v, SB_STRAIGHT, SB_STRAIGHT, 0x131)
    g.add(rect(0, 0, v, XH))
    return reg(g)


def stroke_D():
    base = G['D']
    g = Glyph('Dcroat', base.body + 40, SB_STRAIGHT, base.rsb, 0x110)
    g.ops = shift_ops(base.ops, 40, 0)
    g.add(rect(-6, 296, V + 40 + 110, 296 + HM - 16))
    return reg(g)


def stroke_d():
    base = G['d']
    g = Glyph('dcroat', base.body + 40, base.lsb, base.rsb - 10, 0x111)
    g.ops = list(base.ops)
    W = base.body
    g.add(rect(W - v - 96, ASC - 150, W + 40, ASC - 150 + h - 26))
    return reg(g)


# ===================== COMPOSER =====================
import unicodedata

TONES = {'́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde'}
CIRC, BREVE, HORN, DOTB = '̂', '̆', '̛', '̣'
MARK_HGT = {'circumflex': 142, 'breve': 126}


# extra right sidebearing a horn adds. 26/10 review "kerning giữa ư và ơ hơi xa": the old flat
# +58/+76 made ươ ~40u looser than uo. Tuned per base so that, by area in the x-height band,
# ươ == uo and ơn == on (horn_tune.py); horn-vs-mark / horn-vs-t clearances are then guarded
# by kerning exceptions.
HORN_INC = {'u': 16, 'o': -8, 'U': 14, 'O': -12}   # v0.94: o/O horns moved 42 in (HORN_O_IN 8 -> 50), spacing kept
HORN_O_IN = 0


def horn_inc(upper, base=None):
    base = base or ('U' if upper else 'u')
    return HORN_INC[base]


HORN_TONE_GAP = 38      # v0.95: a tone on Ơ moves left only as far as needed to clear the round horn by this


def _dense(ops, step=4.0):
    out = []
    for op, c in ops:
        if op == 'group':
            out += _dense(c, step); continue
        if op != 'add':
            continue
        pts = flatten(c, 16)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / step))
            out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    return out


def _horn_clear(ops, h_ops, cx, zone):
    """0 when the centred tone clears the horn plate by HORN_TONE_GAP, else the smallest left shift (step 2)."""
    T, Hp = _dense(ops), _dense(h_ops)
    for k in range(0, 200):
        dx = -2 * k
        d = min(((x + cx + dx - hx) ** 2 + (y + zone - hy) ** 2) ** 0.5 for x, y in T[::2] for hx, hy in Hp[::2])
        if d >= HORN_TONE_GAP:
            return dx
    return dx


def compose(ch, gaps=None):
    """Compose a Vietnamese letter. g.parts keeps (label, ops) for collision QA."""
    gaps = gaps or MARK_GAPS
    if ch in G:
        return G[ch]
    if ch == 'Đ':
        return G['Dcroat']
    if ch == 'đ':
        return G['dcroat']
    d = unicodedata.normalize('NFD', ch)
    base, marks = d[0], d[1:]
    upper = base.isupper()
    bname = 'dotlessi' if base == 'i' else base
    bg = G[bname]
    g = Glyph('uni%04X' % ord(ch), bg.body, bg.lsb, bg.rsb, ord(ch))
    g.ops = list(bg.ops)
    g.parts = [('base', list(bg.ops))]
    cx = bg.body / 2
    # F15 (28/10, caps of the Latin-extended lowercase): a mark sits on the letter's visual axis — J on its stem,
    # L just right of its stem (references Inter / DejaVu / Liberation / Calibri: 0.21-0.32 of L's width)
    if base == 'J':                          # the mark's right edge flush with the stem's (v0.969 QA: centred on the
        cx = bg.body - 144                   # stem the 288-wide mũ overhung and Ĵ's ink shrank R -> B)
    elif base == 'L':
        cx = V
    zone = ZONE_UC if upper else ZONE_LC
    sy = CAP_SCALE if upper else 1.0
    top_h = 0
    if HORN in marks:
        xr = bg.body - (HORN_O_IN if base in 'oO' else 0)   # v0.94 L-plate horn (marks_flat.horn_ops)
        yt = CAP if upper else XH
        h_ops = horn_ops(bg.body, yt, upper, o_shape=(base in 'oO'))   # v0.94: one plate for ơ and ư
        g.ops += h_ops
        g.parts[0] = ('base', g.parts[0][1] + h_ops)
        reach = __import__('marks_flat').horn_reach(upper, base)
        g.rsb += max(0, reach - 44 * WK)        # horn tip 44k inside the advance, as before
    first = 'circumflex' if CIRC in marks else ('breve' if BREVE in marks else None)
    tone = next((TONES[m] for m in marks if m in TONES), None)
    sshift = side_shift(tone, upper, gaps) if (first == 'circumflex' and tone in ('acute', 'hook') and not (tone == 'acute' and ACUTE_MODE() in ('4', '5'))) else 0
    yc = CIRC_FOOT(bg.ops + (h_ops if HORN in marks else []), cx + sshift, zone, ('U', bname, round(cx + sshift, 1))) if first == 'circumflex' else 0.0
    zone0 = zone
    zone = zone + yc                                 # R8k: the mũ and every tone stacked on it move with the mũ's foot
    if first:
        ops = shift_ops(mark_ops(first, upper), cx + sshift, zone)
        g.ops += ops; g.parts.append((first, ops))
        top_h = MARK_HGT[first] * sy
    if tone:
        ops = mark_ops(tone, upper)
        if base in 'iI' and tone == 'tilde':
            ops = scale_ops(ops, 0.8, 1.0)
        if first == 'circumflex' and tone not in ('tilde', 'grave'):   # v0.95 review: huyền rides ON TOP of mũ / trăng, full length
            ops = mark_ops(tone, upper, MARK_STACK_LEN[tone]) if tone in MARK_STACK_LEN else (MARK_STACK_FN[tone]() if tone in MARK_STACK_FN else (ops if tone in MARK_NOSCALE else scale_ops(ops, 0.86, 0.86)))
            dx, dy = gaps['side'][tone]
            if tone in MARK_TOP and upper:          # v0.95c: every sắc ends on the same top line (Ấ = Á = Ắ)
                ops = mark_ops(tone, upper, MARK_TOP[tone] - (zone + dy * sy))
            if tone == 'acute':                     # R8e: a tilted sắc on the mũ's shoulder keeps the standing strip's FOOT
                ops = shift_ops(ops, ACUTE_FOOT_DX(), 0)   # (it leans away from the mũ, never into it — 'ố ấ ế')
            ydy = dy * sy
            if tone == 'acute' and ACUTE_BESIDE():  # R8g: sắc beside the mũ on the mark zone (ấ top = á top)
                ops = mark_ops('acute', upper, __import__('marks_flat').ACUTE_L)
                ydy, dx = 0, ACUTE_BESIDE_DX(upper)
            elif tone == 'acute' and ACUTE_MODE() in ('4', '5'):   # R8i: the sắc CENTRED over the mũ (sample Ấ +1 u, ấ +3 u)
                ops = mark_ops('acute', upper)
                dx = ACUTE_IN_DX(ACUTE_R8K_UC_DX, bg.ops, cx)            # R8k-b behind the mũ, R8k-c inside the letter
                ydy = max(ACUTE_STACK_Y() + zone0 - zone, ACUTE_CIRC_Y(upper, dx))   # Ắ's line, unless the mũ needs more
            elif tone == 'acute' and ACUTE_TOPLINE():  # R8f trial: the sắc on ấ ends on the same line as on ắ
                ydy = ACUTE_STACK_Y()
                dx = ACUTE_CIRC_DX(dx, ydy, True)   # R8f: pulled left to 40 from the mũ
            ops = shift_ops(ops, cx + dx + sshift, zone + ydy)
            if tone == 'hook' and __import__('marks_flat').R8I():   # R8k: hỏi beside the new mũ keeps 40 from it (was 20-31)
                ops = CLEAR_UP(ops, [o for nm, o2 in g.parts if nm == 'circumflex' for o in o2], __import__('marks_flat').CIRC_R8K_GAP)
        elif first:
            ops = mark_ops(tone, upper) if tone == 'grave' else (mark_ops(tone, upper, MARK_STACK_LEN[tone]) if tone in MARK_STACK_LEN else (MARK_STACK_FN[tone]() if tone in MARK_STACK_FN else (ops if tone in MARK_NOSCALE else scale_ops(ops, 0.88, 0.80))))   # v0.95c: one thickness, never scaled; huyền full length
            if tone in MARK_TOP and upper:          # v0.95c: every sắc ends on the same top line
                ops = mark_ops(tone, upper, MARK_TOP[tone] - (zone + top_h + gaps['stack_gap'] * sy))
            if tone == 'acute':                     # R8e: on the trăng too, the foot stays on the axis
                ops = shift_ops(ops, ACUTE_FOOT_DX(), 0)
            if tone == 'acute' and first == 'breve' and ACUTE_TOPLINE():
                ops = shift_ops(ops, cx, zone + ACUTE_STACK_Y())
            else:
                ops = shift_ops(ops, cx, zone + top_h + gaps['stack_gap'] * sy)
        else:
            hx = gaps.get('horn_tone_dx', 0) if HORN in marks else 0
            if HORN in marks and base in 'oO':
                hx = _horn_clear(ops, h_ops, cx, zone)   # v0.95 round horn: centred unless the disc is in the way
            if tone == 'grave' and upper and 'grave' in MARK_STACK_LEN and __import__('os').environ.get('GRAVE_FULL', '1') != '1':   # v0.95 QA: Ì — the lying strip never overhangs a narrow letter (R8h 28/10 13:16 'dấu huyền của i và I hơi ngắn': full length, may overhang)
                adv = bg.lsb + bg.body + bg.rsb
                if adv - 40 < __import__('marks_flat').STRIP_L:
                    ops = mark_ops('grave', upper, adv - 40)
            ops = shift_ops(ops, cx + hx, zone)
        g.ops += ops; g.parts.append((tone, ops))
    if DOTB in marks:
        adv = bg.lsb + bg.body + bg.rsb
        try:
            db = mk_dotbelow(length=min(__import__('marks_flat').STRIP_L, adv - 40))   # v0.95 QA: Ị
        except TypeError:
            db = mk_dotbelow()
        ops = shift_ops(db, cx + (gaps['y_dot_dx'] if base == 'y' else 0), -72 if base == 'y' else -52)
        g.ops += ops; g.parts.append(('dotbelow', ops))
    return g


# measured so every mark-to-mark gap >= 46 (lc) / 44 (uc) units and the dot clears y's tail by >= 50
MARK_GAPS = {'side': {'acute': (254, 70), 'grave': (186, 70), 'hook': (170, 70)}, 'stack_gap': 52, 'y_dot_dx': 176}


def ops_xrange(ops):
    xs = []
    for op, c in ops:
        if op == 'group':
            a, b = ops_xrange(c); xs += [a, b]
        elif op == 'add':
            xs += [p[0] for p in flatten(c, 6)]
    return min(xs), max(xs)


def side_shift(tone, upper, gaps=None):
    """x shift that re-centres a circumflex + side-tone group over the letter."""
    gaps = gaps or MARK_GAPS
    c_ops = mark_ops('circumflex', upper)
    t_ops = scale_ops(mark_ops(tone, upper), 0.86, 0.86)
    dx, dy = gaps['side'][tone]
    t_ops = shift_ops(t_ops, dx, 0)
    a1, b1 = ops_xrange(c_ops); a2, b2 = ops_xrange(t_ops)
    return -((min(a1, a2) + max(b1, b2)) / 2) * STACK_CENTER_K


# Vietnamese convention (26/10 review "dấu hơi lệch"): the circumflex stays centred on
# the letter and the tone hangs off its right shoulder. 0 = circumflex centred, 1 = whole
# group centred (old behaviour, read as skewed).
STACK_CENTER_K = 0.0


def build_vn():
    dotless_i()
    stroke_D()
    stroke_d()
    import figs_c            # figures + punctuation (need S, a, đ already built)
    figs_c.build_figs()


# =====================================================================
# A2 — "BIỂN SƠN CHỢ LỚN" (hand-painted shop sign, Saigon–Chợ Lớn 60s/70s)
# Built with the same grid as A/B, but: narrower (~85%), round 'compass'
# bowls, stems that flare slightly at their free ends (brush), and a
# diacritic kit drawn as one brush stroke or a compass/ruler primitive.
# Everything below overrides the A definitions of the same name.
# =====================================================================
import math as _m
_base_rrect = rrect
KC = 0.56                     # circle-like curves (0.552 = true circle)


def rrect(x0, y0, x1, y1, r=(0, 0, 0, 0), k=KC):
    return _base_rrect(x0, y0, x1, y1, r, k)


FULL = 9999                   # radius 'full' -> clamps to a semicircle
import os as _os
WEIGHT = _os.environ.get('A2_WEIGHT', 'bold')
# stem table per weight (Bold = the approved master). Regular/Medium keep the same
# contrast ratio (h/v ~0.83) and diagonal-lightening rules; sidebearings open up as
# stems get thinner so the colour stays even.
_WT = {'bold':    dict(V=168, H=140, HM=124, v=150, h=124, SB=(42, 30, 14), F=(9, 8)),
       'medium':  dict(V=142, H=120, HM=106, v=128, h=106, SB=(46, 33, 16), F=(8, 7)),
       'regular': dict(V=116, H=100, HM=90,  v=104, h=88,  SB=(50, 36, 18), F=(7, 6))}[WEIGHT]
V, H, HM = _WT['V'], _WT['H'], _WT['HM']      # caps: stem, horizontal, middle bar
v, h = _WT['v'], _WT['h']                     # lowercase
WK = v / 150                                  # stroke scale vs Bold, for literal stroke sizes
WKC = V / 168                                 # same for caps
SB_STRAIGHT, SB_ROUND, SB_DIAG = _WT['SB']
FL, fl = _WT['F']                             # brush flare per side at a free stem end
DIAG = round(V * 0.90); DIAG_K_ARM = round(V * 0.86); DIAG_Y = round(V * 0.88)
DIAG_X = round(V * 0.88); DIAG_MULTI = round(V * 0.84); DIAG_Z = round(V * 0.92)
diag = round(v * 0.90); diag_k_arm = round(v * 0.86); diag_y = round(v * 0.88)
diag_x = round(v * 0.88); diag_multi = round(v * 0.84); diag_z = round(v * 0.92)
import r2c as _r2c
DV_C = V - 116                                # R2c: the caps' stroke growth over Regular
# R16 (28/10 18:26 'đánh giá lại kích thước các chữ in hoa — đã đồng bộ và cân bằng thị giác chưa'; designer kept the
# narrow upright-ellipse O): widths re-proportioned on the five reference fonts, measured as ratios so the narrow O is
# respected (CAPW=0 restores v0.980):
#   U = H + 1.5 % (was the O-ring, 1.075 H; refs 0.98-1.04)      D <= O: 0.977 O (was 1.03 O; a half-round never wider)
#   B = 0.95 R, P = 0.96 B (P was 0.96 R; refs P/R ~0.91)          K = 1.02 H in Regular (was 1.07; refs <= 1.04)
#   T grows like H (straight), Z like a bowl (0.9): both kept their Regular ratio to H in Bold (they narrowed 4-5 %)
CAPW = __import__('os').environ.get('CAPW', '1') == '1'


def gw(kind):
    """R2c: extra body width of a capital / figure of this class in this weight (0 in Regular)."""
    return _r2c.grow(kind, DV_C)


# ---- CONSTRUCTION SYSTEM (26/10, duyệt) ------------------------------------------------------
# Every round part comes from three compass modules; widths and radii are never free numbers.
#   O-ring (caps):      box RING_O wide; outer corners = semicircle R_O = RING_O/2; counter = box
#                       inset by one stroke (V sides, H top/bottom), its radius r_O = R_O - V.
#   o-ring (lowercase): box RING_o wide; R_o = RING_o/2; r_o = R_o - v.
#   r1 = r_o / 2:       the small compass — every inside corner, every join, every hook counter.
# Strokes: V, H = .83V, HM = .74V; v, h = .83v; diagonals .9 of the stem (weight table above).
RING_O, RING_o = 560, 498
R_O, R_o = RING_O / 2, RING_o / 2
r_O, r_o = R_O - V, R_o - v
r1 = r_o / 2
HOOK_CLEAR = OV_L + 0.3 * h        # a descender hook's terminal stays this far under the baseline


# ---- TERMINAL RULE (26/10 audit "các glyph phải đồng bộ") -------------------------------
# Every open terminal of a round stroke (C G c e S s 2 3 5 6 9 € ¢ £ $ ...) is cut the same way:
#  1. the vertical end cut keeps TERM_KEEP of the stroke past the counter wall, in every
#     weight (it used to be a fixed fraction of the width, so thin weights got a sliver/point);
#  2. the horizontal cut meets the counter where its wall is (near) vertical: at most
#     TERM_PHI off vertical (ink corner 90-105 deg). Above that the cut leaves a lip on the
#     curve (old 3/6/9); below the counter's equator it leaves an acute hook (old light S).
TERM_KEEP = 0.45
TERM_PHI = 15.0
_SPHI = __import__('math').sin(__import__('math').radians(TERM_PHI))


def term_x(wall, stem, side='r'):
    """x of the vertical end cut. wall = counter's straight wall, stem = stroke there."""
    return wall + stem * TERM_KEEP if side == 'r' else wall - stem * TERM_KEEP


def term_y(design, inner_lo, inner_hi, inner_w, face):
    """clamp a horizontal terminal cut to the house rule.
    face='down': the terminal hangs from the top stroke (its cut face looks down);
    face='up'  : it rises from the bottom stroke (cut face looks up)."""
    ri = min(inner_w, inner_hi - inner_lo) / 2
    if face == 'down':
        lo_ok, hi_ok = inner_lo + ri, inner_hi - ri + ri * _SPHI
        return min(max(design, lo_ok), hi_ok)
    lo_ok, hi_ok = inner_lo + ri - ri * _SPHI, inner_hi - ri
    return max(min(design, hi_ok), lo_ok)


def _ell(cx, cy, rx, ry, k=KC):
    """full ellipse (same curve tension as the compass bowls)"""
    return [('M', cx, cy + ry),
            ('C', cx + k * rx, cy + ry, cx + rx, cy + k * ry, cx + rx, cy),
            ('C', cx + rx, cy - k * ry, cx + k * rx, cy - ry, cx, cy - ry),
            ('C', cx - k * rx, cy - ry, cx - rx, cy - k * ry, cx - rx, cy),
            ('C', cx - rx, cy + k * ry, cx - k * rx, cy + ry, cx, cy + ry), ('Z',)]


HOOK_PHI = 35.0   # review 26/10 "giảm đuôi nhọn": the cut meets the counter 35° past its extreme
                  # point instead of tangent to it, so the pointed tip of the cut stays short


BOWL_PHI = float(_os.environ.get('A2_BOWL_PHI', 0.0))   # bowls (stadium counters): cut at the
                  # counter's wall line, where the arc meets the straight wall (26/10 "đuôi bị cụt")


TAIL_CLEAR = 0.3 * h   # a tail's tip keeps this much air to the next stroke (a's bowl, e's bar)


def hook_cut(xc, r, side, phi=None):
    """THE house hook cut (review 26/10 "cứ móc như này là đổi hết"): every open end of a round
    stroke is cut VERTICALLY, HOOK_PHI short of the counter's extreme point (centre xc, radius r),
    with no level cut: the ink ends in a short point on the counter. side = which extreme."""
    d = r * _m.cos(_m.radians(BOWL_PHI if phi is None else phi))
    return xc + d if side == 'r' else xc - d


TIP_W = float(_os.environ.get('A2_TIP_W', 0.0))   # blunt tip: flat end this fraction of the stroke


def blunt_tip(cx, cy, r, xcut, side, vdir, stroke, rx=None):
    """review 26/10 "đuôi nhọn khó nhìn": where a vertical house cut meets its counter (centre
    cx,cy; radii rx,r) the ink thins to a needle. Cut the needle off LEVEL where it is still
    TIP_W * stroke wide. side = which side the cut is on ('r'/'l'); vdir = 'up' if the tip points
    up (terminal above the counter centre), 'down' otherwise. Returns a rect op or None."""
    if TIP_W <= 0:
        return None
    rx = r if rx is None else rx
    w = TIP_W * stroke
    d = abs(xcut - cx)
    if d - w <= 0 or d - w >= rx:
        return None
    dy = r * _m.sqrt(1 - ((d - w) / rx) ** 2)
    xa = cx + (d - w) if side == 'r' else cx - (d - w)
    x0, x1 = (xa, xcut + 2) if side == 'r' else (xcut - 2, xa)
    y0, y1 = (cy - 1, cy + dy) if vdir == 'up' else (cy - dy, cy + 1)
    return ('sub', rect(x0, y0, x1, y1))


TAIL_PHI = 35.0       # R5 (R5b 62 deg tried 27/10, on hold): the tail's inner arc meets the vertical cut this far off vertical


def quarter_disk(cx, cy, rho, side, vdir, k=KC):
    """quarter of a compass disk: side 'r'/'l' of the centre, vdir 'up' (above) / 'down'."""
    sx = 1 if side == 'r' else -1
    sy = 1 if vdir == 'up' else -1
    ax, ay = cx + sx * rho, cy             # on the horizontal radius
    bx, by = cx, cy + sy * rho             # on the vertical radius
    return [('M', cx, cy), ('L', ax, ay),
            ('C', ax, ay + sy * k * rho, bx + sx * k * rho, by, bx, by), ('Z',)]


def tail(cx, cedge, wall, stroke, side, vdir, tip_limit=None):
    """THE house tail (review 26/10 "vẽ sao cho cân đối"): a round stroke ends with a VERTICAL cut
    placed like the old C-cut (TERM_KEEP of the stroke past the counter wall), and the tail's inner
    edge is ONE compass arc that leaves the counter at its top (or bottom) point cx,cedge with the
    same horizontal tangent and meets the cut TAIL_PHI off vertical: no needle, no level cut.
    rho = |xt - cx| / cos(TAIL_PHI). tip_limit caps how far the tip may come (y), shrinking the reach
    (a's arm over the bowl, e's tail under the bar).
    Returns dict(xt, cy, rho, tip, disk)."""
    c, sn = _m.cos(_m.radians(TAIL_PHI)), _m.sin(_m.radians(TAIL_PHI))
    xt = wall + TERM_KEEP * stroke if side == 'r' else wall - TERM_KEEP * stroke
    rho = abs(xt - cx) / c
    if vdir == 'up':                           # tail hangs from the top stroke
        tip = cedge - rho * (1 - sn)
        if tip_limit is not None and tip < tip_limit:
            rho = (cedge - tip_limit) / (1 - sn)
        cy = cedge - rho
        tip = cy + rho * sn
    else:                                      # tail rises from the bottom stroke
        tip = cedge + rho * (1 - sn)
        if tip_limit is not None and tip > tip_limit:
            rho = (tip_limit - cedge) / (1 - sn)
        cy = cedge + rho
        tip = cy - rho * sn
    xt = cx + rho * c if side == 'r' else cx - rho * c
    return dict(xt=xt, cy=cy, rho=rho, tip=tip, disk=quarter_disk(cx, cy, rho, side, vdir))


def hook_quarter(xr, yc, tb, down=True):
    """the hook module (review 26/10, ref. drawing): HALF of a compass ring whose counter is the
    small compass r1 (= r_o/2) and whose side is the stem v (outer rx = r1 + v); top/bottom = tb
    (outer ry = r1 + tb), so it is built exactly like the o (side v, horizontal tb). The stroke runs
    round the ring and is cut VERTICALLY through the counter's extreme point (cut line tangent to
    the counter), which puts the cut on the o's axis: xr - (2*r1 + v) = xr - R_o.
    down=True: lower half (g, j; xr = stem's right wall); down=False: upper half (f; xr = stem's
    left wall). Returns (ops, cut x)."""
    rxi = ryi = r1
    rxo, ryo = r1 + v, r1 + tb
    if down:
        xc = xr - rxo
        xcut = xc - rxi * _m.cos(_m.radians(HOOK_PHI))
        ops = [('add', _ell(xc, yc, rxo, ryo)), ('sub', _ell(xc, yc, rxi, ryi)),
               ('sub', rect(xc - rxo - 1, yc - ryo - 1, xcut, yc + ryo + 1)),      # vertical cut
               ('sub', rect(xcut - 1, yc, xr + 1, yc + ryo + 1))]                  # keep lower half
        bt = blunt_tip(xc, yc, ryi, xcut, 'l', 'down', v, rxi)
        return ops + ([bt] if bt else []), xcut
    xl = xr
    xc = xl + rxo
    xcut = xc + rxi * _m.cos(_m.radians(HOOK_PHI))
    ops = [('add', _ell(xc, yc, rxo, ryo)), ('sub', _ell(xc, yc, rxi, ryi)),
           ('sub', rect(xcut, yc - ryo - 1, xc + rxo + 1, yc + ryo + 1)),
           ('sub', rect(xl - 1, yc - ryo - 1, xcut + 1, yc))]
    bt = blunt_tip(xc, yc, ryi, xcut, 'r', 'up', v, rxi)
    return ops + ([bt] if bt else []), xcut


def curved_hook(xr, tb=None):
    """descender hook (j, g): stem (xr-v .. xr) + hook_quarter. Bottom = descender - overshoot,
    lowered only as far as needed to keep the counter's top (= the hook centre line) HOOK_CLEAR
    under the baseline. Returns (ops, cut x = o-axis, centre y = where the straight stem starts)."""
    tb = h if tb is None else tb
    bottom = min(DESC - OV_L, -HOOK_CLEAR - tb - r1)
    yc = bottom + tb + r1
    ops, xc = hook_quarter(xr, yc, tb, down=True)
    return ops, xc, yc


def flare_tail(xl, xr, tb, R):
    """26/10 (duyệt): descender hook ending like the capitals' bar ends: the stem turns left
    through a compass corner (outer R, inner RIN) into a flat bar whose free end swells with the
    brush flare (fbar), exactly like the ends of E F L T Z."""
    return [('add', rrect(xl + 120, DESC, xr, 60, (0, 0, R, 0))),
            ('sub', rrect(xl - 1, DESC + tb, xr - v, 61, (0, 0, RIN, 0))),
            ('add', fbar(xl, DESC, xl + 200, DESC + tb, f=fl, left=True, right=False))]


def tail_ring(xr, tb, xl=None):
    """descender hook (j, g): the bottom of a compass ring whose right side is the stem (ending at
    xr), swinging up on the left and ending with the C-cut, exactly like a's arm upside down.
    The counter's corner radius ri is what the descender allows while the terminal stays >= 50u
    under the baseline overshoot (room under g's bowl). xl: where the hook starts on the left
    (default: as narrow as the counter allows; g passes its own reach). Returns (ops, xl)."""
    ri = (-OV_L - 50) - (DESC + tb)
    if xl is None:
        xl = xr - 2 * v - 2 * ri
    ycut = term_y(DESC + tb + ri, DESC + tb, 160, 2 * ri, 'up')
    return [('add', rrect(xl, DESC, xr, 60, (0, 0, FULL, FULL))),
            ('sub', rrect(xl + v, DESC + tb, xr - v, 61, (0, 0, ri, ri))),
            ('sub', rect(xl - 1, ycut, xr - v, 62)),
            ('sub', rect(xl - 1, DESC - 1, term_x(xl + v, v, 'l'), 62))], xl


def fstem(x0, y0, x1, y1, f=FL, top=True, bot=True):
    """vertical stem whose free ends flare like a sign-writer's brush."""
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


def fbar(x0, y0, x1, y1, f=FL, left=False, right=True):
    """R4 bar flaring at its free end(s). F11c (28/10 19:51 'kiểm tra lại chiều cao chữ hoa': T's flared bar rose 9 above I):
    a bar edge lying ON a guideline (baseline 0 / cap height) never flares past it -- only the edge away from the line
    flares, by the one R4c amount (the caps follow the lowercase F11)."""
    import flare_spec as _FS                     # R4c: one flare everywhere
    f = _FS.amt(f); L = _FS.length(x1 - x0)
    fr, fl_ = (f if right else 0), (f if left else 0)
    on = __import__('os').environ.get('F11C', '1') == '1'
    hi = not (on and abs(y1 - CAP) < 1.5)
    lo = not (on and abs(y0) < 1.5)
    rlo, rhi = (fr if lo else 0), (fr if hi else 0)
    llo, lhi = (fl_ if lo else 0), (fl_ if hi else 0)
    return [('M', x0, y0 - llo), ('C', x0 + L * 0.35, y0 - llo * 0.15, x0 + L * 0.7, y0, x0 + L, y0),
            ('L', x1 - L, y0), ('C', x1 - L * 0.7, y0, x1 - L * 0.35, y0 - rlo * 0.15, x1, y0 - rlo),
            ('L', x1, y1 + rhi), ('C', x1 - L * 0.35, y1 + rhi * 0.15, x1 - L * 0.7, y1, x1 - L, y1),
            ('L', x0 + L, y1), ('C', x0 + L * 0.7, y1, x0 + L * 0.35, y1 + lhi * 0.15, x0, y1 + lhi), ('Z',)]


def circle(cx, cy, r):
    return rrect(cx - r, cy - r, cx + r, cy + r, r, 0.5523)


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return poly(lo[:-1] + up[:-1])


def brush(path, w0, w1, n=28):
    """one brush stroke along a polyline/curve sample: width w0 -> w1, round ends.
    Returned as a list of ops (hulls of consecutive dabs) so curved strokes stay curved."""
    pts = path
    ops = []
    N = len(pts)
    def dab(i):
        t = i / (N - 1); r = (w0 + (w1 - w0) * t) / 2; x, y = pts[i]
        return [(x + r * _m.cos(a), y + r * _m.sin(a)) for a in [k * 2 * _m.pi / 24 for k in range(24)]]
    for i in range(N - 1):
        ops.append(('add', hull(dab(i) + dab(i + 1))))
    return ops


def lerp_path(p0, p1, n=6):
    return [(p0[0] + (p1[0] - p0[0]) * i / (n - 1), p0[1] + (p1[1] - p0[1]) * i / (n - 1)) for i in range(n)]


# ------------------------------ UPPERCASE ------------------------------
def cap_A():
    W = 572 + gw('diag')
    g = Glyph('A', W, SB_DIAG, SB_DIAG, 0x41)
    dw = diag_dx(DIAG, W / 2 - 80, CAP)
    for op, c in vshape(0, W, CAP, 0, dw, 150):
        g.ops.append((op, mirror_y(c, CAP / 2)))
    # 26/10 "A regular dư nét 2 bên": the bar ends were a fixed 0.6*dw in, which pokes out of
    # the thinner legs in Medium/Regular. Now they sit just inside the outer leg edge at the
    # bar's top in every weight.
    xa = (W / 2 - 75) * (168 + HM) / CAP + 2
    g.add(rect(xa, 168, W - xa, 168 + HM))
    g.sub(rect(-300, -300, W + 300, 0))
    return reg(g)


def cap_B():
    W = (528 if CAPW else 548) + gw('bowl')
    g = Glyph('B', W, SB_STRAIGHT, SB_ROUND, 0x42)
    yb = 296
    g.group([('add', rrect(V / 2, yb, W - 30, CAP, (0, FULL, FULL, 0))),
             ('add', rrect(V / 2, 0, W, yb + HM, (0, FULL, FULL, 0))),
             ('add', fstem(0, 0, V, CAP)),
             ('sub', rrect(V - 1, yb + HM, W - 30 - V + 6, CAP - H, (0, FULL, FULL, 0))),
             ('sub', rrect(V - 1, H, W - V, yb, (0, FULL, FULL, 0)))])
    return reg(g)


def cap_O():
    W = 560
    g = Glyph('O', W, SB_ROUND, SB_ROUND, 0x4F)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    return reg(g)


def cap_C():
    W = 540
    g = Glyph('C', W, SB_ROUND, SB_ROUND - 30, 0x43)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    g.sub(rect(W * 0.5, 236, W + 1, CAP - 236))
    g.sub(rect(W * 0.80, -OV_C - 1, W + 1, CAP + OV_C + 1))
    return reg(g)


def cap_G():
    W = 568
    g = Glyph('G', W, SB_ROUND, SB_ROUND, 0x47)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    yb = 250
    g.sub(rect(W * 0.5, yb + HM, W + 1, CAP - 236))
    g.sub(rect(W * 0.80, yb + HM, W + 1, CAP + OV_C + 1))
    g.add(rect(W * 0.46, yb, W, yb + HM))
    return reg(g)


def cap_D():
    W = (540 + gw('round')) if CAPW else (572 + gw('bowl'))   # R16: D keeps 0.977 O in every weight (grows like O)
    g = Glyph('D', W, SB_STRAIGHT, SB_ROUND, 0x44)
    g.add(fstem(0, 0, V, CAP))
    g.add(rrect(V / 2, 0, W, CAP, (0, FULL, FULL, 0)))
    g.sub(rrect(V - 1, H, W - V, CAP - H, (0, FULL, FULL, 0)))
    return reg(g)


def E_BAR(H, HM):
    """R12: the middle arm's centre sits at 52% of the space between the foot and the top arm (as H's bar)."""
    return H + 0.52 * (CAP - 2 * H) - HM / 2


def cap_E():
    W = 404 + gw('one')
    g = Glyph('E', W, SB_STRAIGHT, SB_STRAIGHT - 18, 0x45)
    yb = E_BAR(H, HM)                                  # v0.95 R12 (was a fixed 290: centre 0.48 cap -> top-heavy E)
    g.add(fstem(0, 0, V, CAP), fbar(V / 2, CAP - H, W, CAP), fbar(V / 2, 0, W, H),
          fbar(V / 2, yb, W - 46, yb + HM))
    return reg(g)


def cap_F():
    W = 392 + gw('one')
    g = Glyph('F', W, SB_STRAIGHT, SB_STRAIGHT - 24, 0x46)
    yb = E_BAR(H, HM) - 0.25 * HM                      # v0.95 R12: F's arm a quarter bar lower than E's (no foot under it)
    g.add(fstem(0, 0, V, CAP), fbar(V / 2, CAP - H, W, CAP), fbar(V / 2, yb, W - 46, yb + HM))
    return reg(g)


def cap_H():
    W = 520
    g = Glyph('H', W, SB_STRAIGHT, SB_STRAIGHT, 0x48)
    g.add(fstem(0, 0, V, CAP), fstem(W - V, 0, W, CAP), rect(V - 1, 300, W - V + 1, 300 + HM))
    return reg(g)


NARROW_SB = float(__import__('os').environ.get('NARROW_SB', '12'))   # S1d (28/10 visual-weight audit: I i l darker than every
# reference — colour I 1.25-1.33 vs 1.02-1.15, i 1.26-1.32 vs 1.00-1.17, l 1.39-1.44 vs 1.15-1.29): the lone straight letters
# get 12 more units each side (all weights), which brings their colour inside the references' range.


def cap_I():
    g = Glyph('I', V, SB_STRAIGHT + NARROW_SB, SB_STRAIGHT + NARROW_SB, 0x49)
    g.add(fstem(0, 0, V, CAP))
    return reg(g)


def cap_J():
    """J = the lower half of the O-ring (outer R_O, counter r_O, bottom H like O) carrying the stem
    on its right, cut VERTICALLY through the counter's leftmost point (the same hook as g j f,
    review 26/10). Body = R_O + r_O, so the cut sits on x = 0."""
    # R2c + 'Regular is the master' (28/10 01:22 'móc đuôi J cong nhiều, nét cắt nhọn quá mức'): the heavier hook is
    # REGULAR's hook with the extra stroke added on both sides (outer circle +0.55 dV, counter -0.45 dV), and the cut
    # stays at REGULAR's reach from the axis — so the hook's tip stays at Regular's height and angle.
    R_O = RING_O / 2 + (0.55 * DV_C if _r2c.ON else 0)
    r_O = R_O - V
    xc = r_O * _m.cos(_m.radians(HOOK_PHI))  # the cut meets this weight's counter HOOK_PHI past its extreme: the tip
                                             # stays at Regular's height and angle (the hook does not curl up)
    W = xc + R_O
    # R14 (open side) + R2c: the hook's tip side is an OPEN side (only the tip reaches it), so it keeps Regular's
    # sidebearing; the hook itself widens little (it is Regular's hook + stroke), and the advance must still grow
    g = Glyph('J', W, 36 if _r2c.ON else SB_ROUND, SB_STRAIGHT, 0x4A)
    yo = -OV_C + R_O                         # outer circle centre
    yi = -OV_C + H + r_O                     # counter centre (bottom = H, like the O)
    g.group([('add', _ell(xc, yo, R_O, R_O)), ('sub', _ell(xc, yi, r_O, r_O)),
             ('sub', rect(-R_O - 1, -OV_C - 1, 0, CAP + 1)),                 # vertical cut, tangent to the counter
             ('sub', rect(-1, yi, W - V, CAP + 1)),                         # open above the counter's equator
             ('sub', rect(-1, yo, W + 1, CAP + 1))])
    bt = blunt_tip(xc, yi, r_O, 0, 'l', 'down', V)
    if bt: g.ops.append(bt)
    g.add(fstem(W - V, yo - 1, W, CAP, bot=False))
    return reg(g)


K_CROTCH, K_JOIN = 0.35, 0.57


def cap_K():
    """K/k rule: the arm's lower edge meets the stem wall at K_CROTCH of the height (above the
    stem's flare zone) and its bottom cut lies inside the stem; the leg springs from the arm's
    centre line at K_JOIN of the height."""
    W = (529 if CAPW else 556) + gw('multi')
    g = Glyph('K', W, SB_STRAIGHT, SB_DIAG, 0x4B)
    g.add(fstem(0, 0, V, CAP))
    aw = diag_dx(DIAG_K_ARM, W - V - 60, CAP - 300)
    ax0, ax1 = V - aw / 2, W - aw / 2
    yc, yj = K_CROTCH * CAP, K_JOIN * CAP
    g.group([('add', stroke((ax0, yc), (ax1, CAP), aw)), ('sub', rect(-400, -400, V / 4, CAP + 400))])
    lw = diag_dx(DIAG, W - V - 120, 380) * 0.86
    xj = ax0 + (yj - yc) / (CAP - yc) * (ax1 - ax0)
    g.add(stroke((xj, yj), (W - lw / 2, 0), lw))
    g.sub(rect(-200, -400, -12, CAP + 400), rect(V, CAP, W + 200, CAP + 400), rect(V, -400, W + 200, 0))
    return reg(g)


def cap_L():
    W = 404 + gw('one')
    g = Glyph('L', W, SB_STRAIGHT, SB_STRAIGHT - 24, 0x4C)
    g.add(fstem(0, 0, V, CAP), fbar(V / 2, 0, W, H))
    return reg(g)


M_W = 640   # v0.95 review 27/10 "chữ M hơi rộng — giảm xíu nữa": 700 -> 640


def cap_M():
    W = M_W + gw('multi')
    VM = round(160 * WKC)
    g = Glyph('M', W, SB_STRAIGHT - 4, SB_STRAIGHT - 4, 0x4D)
    g.add(fstem(0, 0, VM, CAP), fstem(W - VM, 0, W, CAP))
    dw = diag_dx(DIAG_MULTI, W / 2 - VM, CAP - 190)
    g.group(vshape(0, W, CAP, 190, dw, 140 * WKC))
    return reg(g)


def cap_N():
    W = 540 + gw('straight')
    VN = round(156 * WKC)
    g = Glyph('N', W, SB_STRAIGHT, SB_STRAIGHT, 0x4E)
    dw = diag_dx(DIAG, W - 190, CAP)
    g.add(fstem(0, 0, VN, CAP, top=False), fstem(W - VN, 0, W, CAP, bot=False))
    g.add(poly([(0, CAP), (dw, CAP), (W, 0), (W - dw, 0)]))
    return reg(g)


def cap_P():
    W = (507 if CAPW else 532) + gw('bowl')
    g = Glyph('P', W, SB_STRAIGHT, SB_ROUND - 8, 0x50)
    yb = 268
    g.add(fstem(0, 0, V, CAP))
    g.add(rrect(V / 2, yb, W, CAP, (0, FULL, FULL, 0)))
    g.sub(rrect(V - 1, yb + round(130 * WKC), W - V, CAP - H, (0, FULL, FULL, 0)))
    return reg(g)


def cap_Q():
    W = 560 + gw('round')
    g = Glyph('Q', W, SB_ROUND, SB_ROUND - 4, 0x51)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    tw = diag_dx(146 * WKC, 200, 290)
    g.add(stroke((W * 0.62, 190), (W - 40, -96), tw))
    return reg(g)


R_LEG_X = 430      # v0.95: x of the R leg's outer edge where it leaves the bowl (Bold reference, all weights)


def cap_R():
    W = 548 + gw('bowl')
    g = Glyph('R', W, SB_STRAIGHT, SB_DIAG + 4, 0x52)
    yb = 286
    g.add(fstem(0, 0, V, CAP, bot=True))
    g.add(rrect(V / 2, yb, W - 20, CAP, (0, FULL, FULL, 0)))
    g.sub(rrect(V - 1, yb + round(130 * WKC), W - 20 - V, CAP - H, (0, FULL, FULL, 0)))
    lw = diag_dx(DIAG, 220, yb + 40) * 0.95
    # v0.95 review "chân R của medium và regular bị trôi ra xa so với bold": the leg used to start at
    # W-20-V-lw/2+70, so a thinner stem pushed it ~80u to the right (Regular: almost vertical, with a
    # ledge poking out of the bowl). Rule (R7, R2b): the leg's OUTER edge is ONE line in every weight —
    # from the bowl's bottom (x = R_LEG_X, the Bold junction) to the foot flush with the advance —
    # and the stroke grows inward from it; its top is cut level inside the bowl's bottom bar.
    xr0, xr1 = R_LEG_X + gw('bowl'), W                      # outer (right) edge: top and foot
    ytop = yb + 0.5 * HM
    xs = xr0 - lw / 2 + (xr1 - xr0) * (yb + 30 - ytop) / (yb + 30)   # centre on the outer line at y=yb+30
    g.group([('add', stroke((xr0 - lw / 2, yb + 30), (xr1 - lw / 2, 0), lw)),
             ('sub', rect(V / 2, ytop, W + 50, CAP + 50))])
    g.sub(rect(V + 2, -300, W + 50, 0))
    return reg(g)


def cap_S():
    W = 516
    g = Glyph('S', W, SB_ROUND, SB_ROUND, 0x53)
    up, lo = s_shape(W, CAP, OV_C, V - 10, H, HM, FULL, FULL, FULL, 60, 60, top_inset=22)
    g.group(up); g.group(lo)
    return reg(g)


def cap_T():
    W = 520 + gw('straight' if CAPW else 'one')
    g = Glyph('T', W, SB_DIAG + 4, SB_DIAG + 4, 0x54)
    g.add(fbar(0, CAP - H, W, CAP, left=True, right=True), fstem((W - V) / 2, 0, (W + V) / 2, CAP, top=False))
    return reg(g)


def cap_U():
    W = (528 if CAPW else RING_O) + gw('straight')
    g = Glyph('U', W, SB_STRAIGHT, SB_STRAIGHT, 0x55)
    apply(g, ring(0, -OV_C, W, CAP + 400, V, H, (0, 0, FULL, FULL), (0, 0, FULL, FULL)))
    g.sub(rect(-1, 300, W + 1, CAP + 401))
    g.add(fstem(0, 290, V, CAP, bot=False), fstem(W - V, 290, W, CAP, bot=False))
    return reg(g)


def cap_V():
    W = 580 + gw('diag')
    g = Glyph('V', W, SB_DIAG, SB_DIAG, 0x56)
    dw = diag_dx(DIAG, W / 2 - 60, CAP)
    apply(g, vshape(0, W, CAP, 0, dw, 150))
    return reg(g)


def cap_W():
    W_reg = 2 * 470 - diag_dx(round(116 * 0.84), 470 / 2 - 40, CAP)
    W1 = 470
    for _ in range(6):                         # R2c: solve the half-width so the whole W widens by gw('multi')
        dw = diag_dx(DIAG_MULTI, W1 / 2 - 40, CAP)
        W1 = (W_reg + gw('multi') + dw) / 2
    dw = diag_dx(DIAG_MULTI, W1 / 2 - 40, CAP)
    W = 2 * W1 - dw
    g = Glyph('W', W, SB_DIAG, SB_DIAG, 0x57)
    g.group(vshape(0, W1, CAP, 0, dw, 128))
    g.group(vshape(W - W1, W, CAP, 0, dw, 128))
    return reg(g)


def cap_X():
    W = 564 + gw('diag')
    g = Glyph('X', W, SB_DIAG, SB_DIAG, 0x58)
    dw = diag_dx(DIAG_X, W - 200, CAP) * 1.04
    g.add(pinch((dw / 2, CAP), (W - dw / 2, 0), dw))
    g.add(pinch((W - dw / 2, CAP), (dw / 2, 0), dw))
    return reg(g)


def cap_Y():
    W = 572 + gw('diag')
    g = Glyph('Y', W, SB_DIAG, SB_DIAG, 0x59)
    dw = diag_dx(DIAG_Y, W / 2 - 60, CAP - 300) * 0.95
    c = W / 2
    g.group(vshape(0, W, CAP, 236, dw, V))
    g.add(fstem(c - V / 2, 0, c + V / 2, 300, top=False))
    return reg(g)


def cap_Z():
    W = 500 + gw('bowl' if CAPW else 'one')
    g = Glyph('Z', W, SB_ROUND, SB_ROUND, 0x5A)
    dw = diag_dx(DIAG_Z, W - 230, CAP - 2 * H) * 1.04
    g.add(fbar(0, CAP - H, W, CAP, left=True, right=False), fbar(0, 0, W, H, left=False, right=True))
    g.add(poly([(W - dw, CAP - H + 1), (W, CAP - H + 1), (dw, H - 1), (0, H - 1)]))
    return reg(g)


# ------------------------------ LOWERCASE ------------------------------
def lc_bowl(g, W, stem_side=None, top=XH, ov=OV_L):
    if stem_side == 'r':
        R, r = (FULL, 0, 0, FULL), (FULL, 0, 0, FULL)
    elif stem_side == 'l':
        R, r = (0, FULL, FULL, 0), (0, FULL, FULL, 0)
    else:
        R, r = FULL, FULL
    return apply(g, ring(0, -ov, W, top + ov, v, h, R, r))


def lc_a():
    W = 468
    g = Glyph('a', W, SB_ROUND, SB_STRAIGHT, 0x61)
    hb = 300
    g.group([('add', rrect(0, -OV_L, W - v / 2, hb, (FULL, 0, 0, FULL))),
             ('sub', rrect(v, h - OV_L - 4, W - v + 1, hb - h + 10, (FULL, 0, 0, FULL)))])
    g.group([('add', rrect(36, 0, W, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(-1, -1, W - v, XH + OV_L - h, (0, FULL, 0, 0)))])
    g.sub(rect(-1, hb, W - v, XH + OV_L - h))
    g.add(fstem(W - v, 0, W, 300, f=fl, top=False))
    return reg(g)


def lc_b():
    W = RING_o
    g = Glyph('b', W, SB_STRAIGHT, SB_ROUND, 0x62)
    lc_bowl(g, W, 'l')
    g.add(fstem(0, -OV_L, v, ASC, f=fl, bot=False))
    return reg(g)


def lc_c():
    W = 440
    g = Glyph('c', W, SB_ROUND, SB_ROUND - 26, 0x63)
    lc_bowl(g, W)
    g.sub(rect(W * 0.5, 178, W + 1, XH - 178))
    g.sub(rect(W * 0.80, -OV_L - 1, W + 1, XH + OV_L + 1))
    return reg(g)


def lc_d():
    W = RING_o
    g = Glyph('d', W, SB_ROUND, SB_STRAIGHT, 0x64)
    lc_bowl(g, W, 'r')
    g.add(fstem(W - v, -OV_L, W, ASC, f=fl, bot=False))
    return reg(g)


def lc_e():
    W = 460
    g = Glyph('e', W, SB_ROUND, SB_ROUND - 6, 0x65)
    lc_bowl(g, W)
    yb = 226
    g.add(rect(v - 1, yb, W - v + 1, yb + h - 14))
    g.sub(rect(W * 0.5, 170, W + 1, yb))
    g.sub(rect(W * 0.80, -OV_L - 1, W + 1, yb))
    return reg(g)


def lc_f():
    """f hook = the same hook_quarter turned over (upper-left quarter of the 2:1 o-ring): the stem
    turns right, cut vertically on the o-axis (s0 + R_o); top at the ascender; crossbar h with
    brush flares."""
    s0 = 40
    yc = ASC - h - r1
    ops, xc = hook_quarter(s0, yc, h, down=False)
    W = round(xc + 36)
    g = Glyph('f', W, SB_DIAG + 4, -16 - 36, 0x66)
    g.group(ops)
    g.add(fstem(s0, 0, s0 + v, yc + 1, f=fl, top=False))
    g.add(fbar(0, XH - h + 6, W - 46, XH, f=fl - 2, left=True, right=True))
    return reg(g)


def lc_g():
    W = 470
    g = Glyph('g', W, SB_ROUND, SB_STRAIGHT, 0x67)
    tb = 112                                   # tail bar
    g.group([('add', rrect(28, DESC, W, -30, (0, 0, 170, 0))),
             ('sub', rrect(-1, DESC + tb, W - v, -29, (0, 0, 54, 0)))])
    g.add(rect(W - v, -40, W, XH))
    lc_bowl(g, W, 'r')
    return reg(g)


def lc_h():
    W = 470
    g = Glyph('h', W, SB_STRAIGHT, SB_STRAIGHT, 0x68)
    apply(g, arch(v / 2, W, XH + OV_L, v / 2, h, FULL, FULL, left_round=False))
    g.sub(rect(W - v, -1, W + 50, 120))
    g.add(fstem(0, 0, v, ASC, f=fl), fstem(W - v, 0, W, 300, f=fl, top=False))
    return reg(g)


def tittle(cx, y0, w=None, hgt=None):
    return circle(cx, y0 + 82, 82)


def lc_i():
    g = Glyph('i', v, SB_STRAIGHT, SB_STRAIGHT, 0x69)
    g.add(fstem(0, 0, v, XH, f=fl, top=False), circle(v / 2, XH + 62 + 82, 82))
    return reg(g)


def lc_j():
    W = 260
    g = Glyph('j', W, SB_STRAIGHT - (W - v), SB_STRAIGHT, 0x6A)
    g.group([('add', rrect(0, DESC, W, XH, (0, 0, 150, 0))),
             ('sub', rrect(-1, DESC + 112, W - v, XH + 1, (0, 0, 46, 0)))])
    g.add(circle(W - v / 2, XH + 62 + 82, 82))
    return reg(g)


def lc_k():
    """same K/k rule as the capital (crotch K_CROTCH, leg join K_JOIN of the x-height)."""
    W = 448
    g = Glyph('k', W, SB_STRAIGHT, SB_DIAG - 2, 0x6B)
    g.add(fstem(0, 0, v, ASC, f=fl))
    aw = diag_dx(diag_k_arm, W - v - 40, XH - 190)
    ax0, ax1 = v - aw / 2, W - aw / 2
    yc, yj = K_CROTCH * XH, K_JOIN * XH
    g.group([('add', stroke((ax0, yc), (ax1, XH), aw)), ('sub', rect(-400, -400, v / 4, XH + 400))])
    lw = diag_dx(diag, W - v - 100, 290) * 0.86
    xj = ax0 + (yj - yc) / (XH - yc) * (ax1 - ax0)
    g.add(stroke((xj, yj), (W - lw / 2, 0), lw))
    g.sub(rect(-200, -400, -12, XH + 400), rect(v, XH, W + 200, XH + 400), rect(v, -400, W + 200, 0))
    return reg(g)


def lc_l():
    g = Glyph('l', v, SB_STRAIGHT, SB_STRAIGHT, 0x6C)
    g.add(fstem(0, 0, v, ASC, f=fl))
    return reg(g)


def lc_m():
    vm = 140
    cw = 104
    W = 3 * vm + 2 * cw
    g = Glyph('m', W, SB_STRAIGHT, SB_STRAIGHT, 0x6D)
    mid0 = vm + cw
    g.group(arch(vm / 2, mid0 + vm, XH + OV_L, vm / 2, h, FULL, FULL, left_round=False))
    g.group(arch(mid0, W, XH + OV_L, vm, h, FULL, FULL, left_round=False))
    g.add(fstem(0, 0, vm, XH, f=fl - 1, top=False), fstem(mid0, 0, mid0 + vm, 300, f=fl - 1, top=False),
          fstem(W - vm, 0, W, 300, f=fl - 1, top=False))
    return reg(g)


def lc_n():
    W = 470
    g = Glyph('n', W, SB_STRAIGHT, SB_STRAIGHT, 0x6E)
    apply(g, arch(v / 2, W, XH + OV_L, v / 2, h, FULL, FULL, left_round=False))
    g.add(fstem(0, 0, v, XH, f=fl, top=False), fstem(W - v, 0, W, 300, f=fl, top=False))
    return reg(g)


def lc_o():
    # 26/10 review "u và o không cân": a compass-round o must be wider than the straight n/u to
    # look the same size (its corners are cut away). Was 480 (ink 481 < n/u 487) -> 498 (+3%).
    W = 498
    g = Glyph('o', W, SB_ROUND, SB_ROUND, 0x6F)
    lc_bowl(g, W)
    return reg(g)


def lc_p():
    W = RING_o
    g = Glyph('p', W, SB_STRAIGHT, SB_ROUND, 0x70)
    lc_bowl(g, W, 'l')
    g.add(fstem(0, DESC, v, XH + OV_L, f=fl, top=False))
    return reg(g)


def lc_q():
    W = RING_o
    g = Glyph('q', W, SB_ROUND, SB_STRAIGHT, 0x71)
    lc_bowl(g, W, 'r')
    g.add(fstem(W - v, DESC, W, XH + OV_L, f=fl, top=False))
    return reg(g)


def lc_r():
    """r 'chân cọ' (approved 26/10): the n-shoulder drops into a short leg that ends
    with the same brush flare as every free stem end."""
    W, hb, yend = 392, round(136 * WK), 300
    g = Glyph('r', W, SB_STRAIGHT, 2, 0x72)   # open lower-right: tight rsb instead of kerning every pair
    R = (W - v / 2) / 2                 # outer shoulder radius (clamped semicircle)
    yv = XH + OV_L - R                  # where the outer curve turns vertical
    g.group([('add', rrect(v / 2, 0, W, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(v - 1, -1, W - hb, XH + OV_L - h, (0, FULL, 0, 0))),
             ('sub', rect(v - 1, -1, W + 1, yv - 20))])
    # flare drawn over a 180-unit virtual length (soft swell), trimmed flat into the shoulder
    g.group([('add', fstem(W - hb, yend, W, yend + 180, f=fl, top=False)),
             ('sub', rect(W - hb - 20, yv, W + 20, yend + 200))])
    g.add(fstem(0, 0, v, XH + OV_L, f=fl, top=False))
    return reg(g)


def lc_s():
    W = 432
    g = Glyph('s', W, SB_ROUND, SB_ROUND, 0x73)
    up, lo = s_shape(W, XH, OV_L, v - 8, h, h - 6, FULL, FULL, FULL, 46, 46, top_inset=18)
    g.group(up); g.group(lo)
    return reg(g)


def lc_t():
    W = 330
    s0 = 40
    g = Glyph('t', W, SB_DIAG + 4, -14, 0x74)
    g.group([('add', rrect(s0, -OV_L, W, 600, (0, 0, FULL, 0))),
             ('sub', rrect(s0 + v, h - OV_L, W + 1, 601, (0, 0, FULL, 0))),
             ('sub', rect(W - 36, -OV_L - 1, W + 1, 601))])
    g.sub(rect(s0 - 1, 400, s0 + v + 1, 601))
    g.add(fstem(s0, 300, s0 + v, 660, f=fl, bot=False))
    g.add(fbar(0, XH - h + 6, W - 40, XH, f=fl - 2, left=True, right=True))
    return reg(g)


def lc_u():
    W = 470
    g = Glyph('u', W, SB_STRAIGHT, SB_STRAIGHT, 0x75)
    for op, c in arch(v / 2, W, XH + OV_L, v / 2, h, FULL, FULL, left_round=False):
        g.ops.append((op, rot180(c, W / 2 + v / 4, XH / 2)))
    g.add(fstem(0, 230, v, XH, f=fl, bot=False), fstem(W - v, 0, W, XH, f=fl))
    return reg(g)


def lc_v():
    W = 480
    g = Glyph('v', W, SB_DIAG, SB_DIAG, 0x76)
    dw = diag_dx(diag, W / 2 - 50, XH)
    apply(g, vshape(0, W, XH, 0, dw, 130))
    return reg(g)


def lc_w():
    W1 = 400
    dw = diag_dx(diag_multi, W1 / 2 - 34, XH)
    W = 2 * W1 - dw
    g = Glyph('w', W, SB_DIAG, SB_DIAG, 0x77)
    g.group(vshape(0, W1, XH, 0, dw, 110))
    g.group(vshape(W - W1, W, XH, 0, dw, 110))
    return reg(g)


def lc_x():
    W = 470
    g = Glyph('x', W, SB_DIAG, SB_DIAG, 0x78)
    dw = diag_dx(diag_x, W - 170, XH) * 1.03
    g.add(pinch((dw / 2, XH), (W - dw / 2, 0), dw))
    g.add(pinch((W - dw / 2, XH), (dw / 2, 0), dw))
    return reg(g)


def lc_y():
    W = 480
    g = Glyph('y', W, SB_DIAG, SB_DIAG, 0x79)
    dw = diag_dx(diag, W / 2 - 50, XH) * 0.96
    c = W / 2
    vx = c - 30
    g.add(stroke((dw / 2, XH), (vx, 0), dw))
    xr = W - dw / 2
    s_ = (vx + 38 - xr) / (0 - XH)
    g.add(stroke((xr, XH), (xr + s_ * (DESC - XH), DESC), dw))
    return reg(g)


def lc_z():
    W = 420
    g = Glyph('z', W, SB_ROUND, SB_ROUND, 0x7A)
    dw = diag_dx(diag_z, W - 190, XH - 2 * h) * 0.98
    g.add(fbar(0, XH - h, W, XH, f=fl - 2, left=True, right=False), fbar(0, 0, W, h, f=fl - 2, left=False, right=True))
    g.add(poly([(W - dw, XH - h + 1), (W, XH - h + 1), (dw, h - 1), (0, h - 1)]))
    return reg(g)


# ------------------------- DIACRITICS: compass & brush -------------------------
# Ruler/compass primitives: circumflex = solid triangle; dot (i/j tittle, dot below,
# horn) = circle. Brush marks: acute/grave = one tapered stroke (thick end up),
# hook = a '?' stroke, tilde = a sine stroke, breve = a cup stroke.
MW = 92                       # brush width (thick end)


def mk_acute(hgt=176):
    return brush(lerp_path((-30, 26), (38, hgt - 46), 8), 56, MW + 22)


def mk_grave(hgt=176):
    return brush(lerp_path((30, 26), (-38, hgt - 46), 8), 56, MW + 22)


def mk_circumflex(hgt=140, half=124):
    return [('add', poly([(-half, 0), (half, 0), (0, hgt)]))]


def mk_breve(hgt=118, half=122):
    r = half - MW / 2
    pts = [(r * _m.cos(a), hgt - MW / 2 - r * 0.9 * _m.sin(a) + 0 * a) for a in [_m.pi * (1 - i / 14) for i in range(15)]]
    pts = [(x, y - (hgt - MW / 2) + (MW / 2) + (r * 0.9)) for x, y in pts]
    return brush([(x, hgt - (y)) for x, y in pts][::-1], MW, MW)


def mk_hook(hgt=186):
    cx, cy, r = 4, hgt - 64, 46
    arc = [(cx + r * _m.cos(a), cy + r * _m.sin(a)) for a in [_m.pi * (0.95 - 1.45 * i / 12) for i in range(13)]]
    tail = lerp_path(arc[-1], (cx - 6, 30), 5)[1:]
    return brush(arc + tail, 70, 54)


def mk_tilde(hgt=110, half=134):
    pts = [(-half + 2 * half * i / 18, 0) for i in range(19)]
    pts = [(x, hgt / 2 + (hgt / 2 - MW / 2.4) * _m.sin((x + half) / (2 * half) * 2 * _m.pi + _m.pi * 0.0)) for x, _ in pts]
    pts = [(x, 2 * (hgt / 2) - y) for x, y in pts]
    return brush(pts, 74, 74)


def mk_dotbelow():
    return [('add', circle(0, -82, 82))]


MARKS = {'acute': mk_acute, 'grave': mk_grave, 'circumflex': mk_circumflex, 'breve': mk_breve,
         'hook': mk_hook, 'tilde': mk_tilde}
MARK_HGT = {'circumflex': 140, 'breve': 118}
ZONE_LC = XH + 62
ZONE_UC = CAP + 50


def horn_ops(x_right, y_top, upper=False):
    r = 66 if upper else 58
    cx, cy = x_right - r * 0.35, y_top + r * 0.55
    return [('add', circle(cx, cy, r)), ('add', rect(cx - r * 0.9, y_top - 120, cx + r * 0.35, cy))]


def stroke_D():
    base = G['D']
    g = Glyph('Dcroat', base.body + 40, SB_STRAIGHT, base.rsb, 0x110)
    g.ops = shift_ops(base.ops, 40, 0)
    g.add(fbar(-6, 300, V + 40 + 104, 300 + HM - 16, left=True, right=True))
    return reg(g)


def stroke_d():
    base = G['d']
    g = Glyph('dcroat', base.body + 40, base.lsb, base.rsb - 10, 0x111)
    g.ops = list(base.ops)
    W = base.body
    g.add(fbar(W - v - 90, ASC - 156, W + 40, ASC - 156 + h - 24, f=fl - 2, left=True, right=True))
    return reg(g)


# --- arches built explicitly (stem side flat, shoulder a full semicircle) ---
def _arch(g, x0, x1, top, stem, bar, flare_right=True):
    g.add(rrect(x0 + stem / 2, 0, x1, top, (0, FULL, 0, 0)))
    g.sub(rrect(x0 + stem - 1, -1, x1 - stem, top - bar, (0, FULL, 0, 0)))


def lc_n():
    W = 470
    g = Glyph('n', W, SB_STRAIGHT, SB_STRAIGHT, 0x6E)
    _arch(g, 0, W, XH + OV_L, v, h)
    g.add(fstem(0, 0, v, XH + OV_L, f=fl, top=False), fstem(W - v, 0, W, 300, f=fl, top=False))
    return reg(g)


def lc_h():
    W = 470
    g = Glyph('h', W, SB_STRAIGHT, SB_STRAIGHT, 0x68)
    _arch(g, 0, W, XH + OV_L, v, h)
    g.add(fstem(0, 0, v, ASC, f=fl), fstem(W - v, 0, W, 300, f=fl, top=False))
    return reg(g)


def lc_m():
    vm = round(140 * WK); cw = round(104 + (140 - vm) * 0.9)
    W = 3 * vm + 2 * cw
    mid0 = vm + cw
    g = Glyph('m', W, SB_STRAIGHT, SB_STRAIGHT, 0x6D)
    g.group([('add', rrect(vm / 2, 0, mid0 + vm, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(vm - 1, -1, mid0, XH + OV_L - h, (0, FULL, 0, 0)))])
    g.group([('add', rrect(mid0 + vm / 2, 0, W, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(mid0 + vm - 1, -1, W - vm, XH + OV_L - h, (0, FULL, 0, 0)))])
    g.add(fstem(0, 0, vm, XH + OV_L, f=fl - 1, top=False), fstem(mid0, 0, mid0 + vm, 300, f=fl - 1, top=False),
          fstem(W - vm, 0, W, 300, f=fl - 1, top=False))
    return reg(g)


def lc_u():
    W = 470
    g = Glyph('u', W, SB_STRAIGHT, SB_STRAIGHT, 0x75)
    g.add(rrect(0, -OV_L, W - v / 2, XH - 100, (0, 0, 0, FULL)))
    g.sub(rrect(v, h - OV_L, W - v + 1, XH, (0, 0, 0, FULL)))
    g.add(fstem(0, 230, v, XH, f=fl, bot=False), fstem(W - v, -OV_L, W, XH, f=fl))
    return reg(g)


def lc_t():
    """26/10 "bỏ đuôi chữ t": no hook — a straight stem with the brush flare at both free
    ends (like l / i) crossed by the flared bar."""
    s0 = 40
    W = s0 + v + 100                     # bar overhangs the stem 100 to the right, 40 left
    g = Glyph('t', W, SB_DIAG + 4, -8, 0x74)    # open lower-right under the bar
    g.add(fstem(s0, 0, s0 + v, 660, f=fl))
    g.add(fbar(0, XH - h + 6, W, XH, f=fl - 2, left=True, right=True))
    return reg(g)


def cap_hyphen():
    W = 300
    g = Glyph('-', W, 40, 40, 0x2D)
    t = 132 * WKC                                   # unicode QA 26/10: was fixed at the Bold 132
    g.add(fbar(0, 262 + (132 - t) / 2, W, 262 + (132 + t) / 2, left=True, right=True))
    return reg(g)


# --- mark sizes tuned up: the sign's marks are big, bold shapes ---
def mk_acute(hgt=184):
    return brush(lerp_path((-34, 30), (42, hgt - 58), 8), 64, 128)


def mk_grave(hgt=184):
    return brush(lerp_path((34, 30), (-42, hgt - 58), 8), 64, 128)


def mk_circumflex(hgt=150, half=146):
    return [('add', poly([(-half, 0), (half, 0), (0, hgt)]))]


def mk_breve(hgt=128, half=136, w=96):
    r = half - w / 2
    pts = [(r * _m.cos(a), w / 2 + r * 0.82 * (1 - _m.sin(a)) - 0) for a in [_m.pi * (1 + i / 14) for i in range(15)]]
    pts = [(x, hgt - w / 2 - (y - w / 2) * 0 - r * 0.82 * (1 + _m.sin(a))) for (x, y), a in zip(pts, [_m.pi * (1 + i / 14) for i in range(15)])]
    return brush(pts, w, w)


def mk_hook(hgt=196):
    cx, cy, r = 6, hgt - 68, 56
    arc = [(cx + r * _m.cos(a), cy + r * _m.sin(a)) for a in [_m.pi * (0.95 - 1.45 * i / 12) for i in range(13)]]
    tail = lerp_path(arc[-1], (cx - 8, 34), 5)[1:]
    return brush(arc + tail, 86, 64)


def mk_tilde(hgt=124, half=144, w=88):
    amp = hgt / 2 - w / 2
    pts = [(-half + 2 * half * i / 20, 0) for i in range(21)]
    pts = [(x, hgt / 2 - amp * _m.sin((x + half) / (2 * half) * 2 * _m.pi)) for x, _ in pts]
    return brush(pts, w, w)


MARKS = {'acute': mk_acute, 'grave': mk_grave, 'circumflex': mk_circumflex, 'breve': mk_breve,
         'hook': mk_hook, 'tilde': mk_tilde}
MARK_HGT = {'circumflex': 150, 'breve': 128}


def mk_breve(hgt=128, half=136, w=94):
    r = half - w / 2
    yc, ry = hgt - w / 2, hgt - w
    pts = [(r * _m.cos(a), yc + ry * _m.sin(a)) for a in [_m.pi + _m.pi * i / 14 for i in range(15)]]
    return brush(pts, w, w)


def mk_tilde(hgt=124, half=116, w=88):
    amp = hgt / 2 - w / 2
    pts = [(-half + 2 * half * i / 20, 0) for i in range(21)]
    pts = [(x, hgt / 2 - amp * _m.sin((x + half) / (2 * half) * 2 * _m.pi)) for x, _ in pts]
    return brush(pts, w, w)


def mk_hook(hgt=180):
    cx, cy, r = 6, hgt - 62, 50
    arc = [(cx + r * _m.cos(a), cy + r * _m.sin(a)) for a in [_m.pi * (0.95 - 1.45 * i / 12) for i in range(13)]]
    tail = lerp_path(arc[-1], (cx - 8, 32), 5)[1:]
    return brush(arc + tail, 84, 62)


MARKS = {'acute': mk_acute, 'grave': mk_grave, 'circumflex': mk_circumflex, 'breve': mk_breve,
         'hook': mk_hook, 'tilde': mk_tilde}


# measured: every mark-to-mark gap >= 46 (lc) / 44 (uc); y's dot clears the tail by >= 46
MARK_GAPS = {'side': {'acute': (188, 70), 'grave': (152, 70), 'hook': (156, 70)}, 'stack_gap': 52, 'y_dot_dx': 168}


def fillet(x, y, R, corner='bl'):
    """concave fillet filling a 90° inside corner at (x, y). corner = which side of
    the white space is rounded: 'bl' = the bottom-left inside corner of a counter whose
    walls run up (x) and right (y) from the corner, i.e. the fill sits at x-R..x, y..y+R."""
    if corner == 'br':     # wall on the right at x, floor at y -> fill x-R..x, y..y+R
        return [('add', rect(x - R, y, x, y + R)), ('sub', circle(x - R, y + R, R))]
    return [('add', rect(x, y, x + R, y + R)), ('sub', circle(x + R, y + R, R))]


def lc_a():
    W = 468
    g = Glyph('a', W, SB_ROUND, SB_STRAIGHT, 0x61)
    hb = 300
    g.group([('add', rrect(0, -OV_L, W - v / 2, hb, (FULL, 0, 0, FULL))),
             ('sub', rrect(v, h - OV_L - 4, W - v + 1, hb - h + 10, (FULL, 0, 0, FULL)))])
    g.group([('add', rrect(36, 0, W, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(-1, -1, W - v, XH + OV_L - h, (0, FULL, 0, 0)))])
    g.sub(rect(-1, hb, W - v, XH + OV_L - h))
    g.add(fstem(W - v, 0, W, 300, f=fl, top=False))
    # the upper counter's floor meets the stem with a curve, not a square corner
    g.group(fillet(W - v, hb, 70, 'br'))
    return reg(g)


# INSIDE-CORNER RULE: where a horizontal stroke meets a stem inside a counter,
# the white corner is rounded with ONE shared radius, so a, g, j, t... speak alike.
RIN = r1          # lowercase inside-corner radius = the small compass r1 (= r_o / 2)


def lc_a():
    W = 468
    g = Glyph('a', W, SB_ROUND, SB_STRAIGHT, 0x61)
    hb = 300
    g.group([('add', rrect(0, -OV_L, W - v / 2, hb, (FULL, 0, 0, FULL))),
             ('sub', rrect(v, h - OV_L - 4, W - v + 1, hb - h + 10, (FULL, 0, 0, FULL)))])
    g.group([('add', rrect(36, 0, W, XH + OV_L, (0, FULL, 0, 0))),
             ('sub', rrect(-1, -1, W - v, XH + OV_L - h, (0, FULL, 0, 0)))])
    g.sub(rect(-1, hb, W - v, XH + OV_L - h))
    g.add(fstem(W - v, 0, W, 300, f=fl, top=False))
    g.group(fillet(W - v, hb, RIN, 'br'))
    return reg(g)


def lc_g():
    """bowl = o-ring with the stem on the right; tail = curved_hook (quarter ring, counter r1)."""
    W = RING_o
    g = Glyph('g', W, SB_ROUND, SB_STRAIGHT, 0x67)
    ops, xc, yc = curved_hook(W)
    g.group(ops + [('add', rect(W - v, yc - 1, W, XH))])        # stem starts on the hook's centre line
    lc_bowl(g, W, 'r')
    return reg(g)


def lc_j():
    W = 260
    g = Glyph('j', W, SB_STRAIGHT - (W - v), SB_STRAIGHT, 0x6A)
    g.group([('add', rrect(0, DESC, W, XH, (0, 0, 150, 0))),
             ('sub', rrect(-1, DESC + 112, W - v, XH + 1, (0, 0, RIN, 0)))])
    g.add(circle(W - v / 2, XH + 62 + 82, 82))
    return reg(g)


# TERMINAL RULE: round-letter terminals (C G c e) are cut vertically at the same
# fraction of the bowl width, long enough to read as a full stroke (not tucked in).
TERM_UC, TERM_LC = 0.90, 0.92


def cap_C():
    W = 540
    g = Glyph('C', W, SB_ROUND, SB_ROUND - 14, 0x43)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    g.sub(rect(W * 0.5, 236, W + 1, CAP - 236))
    g.sub(rect(W * TERM_UC, -OV_C - 1, W + 1, CAP + OV_C + 1))
    return reg(g)


G_FLUSH = __import__('os').environ.get('G_FLUSH', 'D')   # 28/10 15:33 designer: back to D (sample 'bold · dãn + một nhát cắt'); R12b trial (28/10 13:30 'dời nét dưới của G bằng với nét cắt ở trên'):
G_FLUSH_IN = float(__import__('os').environ.get('G_FLUSH_IN', '0'))                                        # 'A': the arm's cut moves OUT to W - 17 (Regular units; refs 0.97-1.0 W)
                                                        # 'B': the lower right moves IN to the arm's cut (quarter oval + post)


def cap_G():
    W = RING_O + gw('round')
    g = Glyph('G', W, SB_ROUND, SB_ROUND, 0x47)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    yb = min(250, -OV_C + H + (W - 2 * V) / 2)        # v0.95 QA: never above the counter's lower arc (Bold had a 6u ledge)
    kw = {}
    if G_FLUSH == 'A':
        kw = dict(reach=(W - G_FLUSH_IN) - W / 2)
    tu = tail(W / 2, CAP + OV_C - H, W - V, V, 'r', 'up', tip_limit=yb + HM + 0.5 * H, ring=(CAP + OV_C - W / 2, W / 2, W / 2), **kw)
    if tu.get('add'):
        g.add(tu['add'])                                  # R5d: the stretched arm
    # v0.962 (R5b): the tail's compass disk only cuts ABOVE the bar — with a flatter arc its centre falls below
    # the bar and the disk would bite the bowl's lower right away from the bar
    g.ops += __import__('concept_v1').band(tu['disk'], y0=yb + HM)
    g.sub(rect(tu['xt'], max(tu['cy'], yb + HM), W + 1, CAP + OV_C + 1),
          rect(W / 2, yb + HM, W + 1, tu['tip']))
    g.add(rect(W * 0.46, yb, W, yb + HM))
    if G_FLUSH == 'B':
        CVm = __import__('concept_v1')
        xt = tu['xt']; c0 = -OV_C + W / 2; ryo = W / 2; rxo = xt - W / 2
        g.sub(rect(W / 2, -OV_C - 2, W + 2, yb + HM))                 # the old lower-right quarter and bar end
        g.group([('add', CVm.ell(W / 2, c0, rxo, ryo)), ('sub', CVm.ell(W / 2, c0, rxo - V, ryo - H)),
                 ('sub', rect(-2, c0, W + 2, CAP + 50)), ('sub', rect(-2, -OV_C - 50, W / 2, c0 + 1))])
        g.add(rect(xt - V, c0 - 3, xt, yb + HM))                      # the post: one stem V, flush with the arm's cut
        g.add(rect(W * 0.46, yb, xt - V + 3, yb + HM))                # the bar runs into the post
        g.body = xt                                                    # the right side bearing is measured from the post
    if G_FLUSH == 'D' and not getattr(cap_G, '_inner', False):
        # R12b-D (28/10 13:54, designer's 'COLLÈGE' reference: 'chữ C và G có độ dãn ra để chữ G có độ rộng tương thích
        # kèm nét cắt' / 'có thể học thử cách làm này'): the single cut of R12b-C, but G's round is STRETCHED by the cut's
        # inset so the cut lands where G's round used to end — G keeps its width (ref.: cut G = 1.18 x C, ours 1.13).
        # 28/10 15:33 (back to D): the stretch is SOLVED (a few passes) so the cut lands exactly on the unstretched
        # round's right edge W in every weight — one pass left it 10 past W in Regular and short of W in Medium / Bold
        # (Medium narrower than Regular). Bar = HM like E F H ('vẫn cân bằng độ dày nét ngang').
        d = W - tu['xt']
        cap_G._inner = True
        try:
            save = globals()['RING_O']
            for _ in range(6):
                globals()['RING_O'] = save + d
                g2 = cap_G()
                if abs(g2.body - W) < 0.5:
                    break
                d += W - g2.body
        finally:
            globals()['RING_O'] = save; cap_G._inner = False
        return g2
    if G_FLUSH == 'C' or (G_FLUSH == 'D' and getattr(cap_G, '_inner', False)):
        # R12b-C (28/10 13:46, designer's Bold sample): ONE vertical cut for the whole right side. The lower bowl is the
        # ring's own round cut at the arm's cut x (like C's lower terminal); a post one stem V wide joins the bar to
        # the lower round. Corner where the round meets the cut, as on C.
        xt = tu['xt']
        g.sub(rect(xt, -OV_C - 2, W + 2, yb + HM))
        ri = (W - 2 * V) / 2; ci = -OV_C + H + ri                       # the counter's lower corner (circle, radius ri)
        dx = min(ri, abs((xt - V) - W / 2))
        y_in = ci - (ri * ri - dx * dx) ** 0.5
        g.add(rect(xt - V, y_in - 6, xt, yb + HM))
        g.body = xt
    return reg(g)


def lc_c():
    W = 440
    g = Glyph('c', W, SB_ROUND, SB_ROUND - 10, 0x63)
    lc_bowl(g, W)
    g.sub(rect(W * 0.5, 178, W + 1, XH - 178))
    g.sub(rect(W * TERM_LC, -OV_L - 1, W + 1, XH + OV_L + 1))
    return reg(g)


def lc_e():
    W = 460
    g = Glyph('e', W, SB_ROUND, SB_ROUND - 2, 0x65)
    lc_bowl(g, W)
    yb = 226
    g.add(rect(v - 1, yb, W - v + 1, yb + h - 14))
    g.sub(rect(W * 0.5, 170, W + 1, yb))
    g.sub(rect(W * TERM_LC, -OV_L - 1, W + 1, yb))
    return reg(g)


# --- decisions after review (26/10): e/c/C/G keep the short 80% terminal (concept),
#     a keeps only its round shoulder (top), g keeps its rounded tail corner ---
TERM_UC, TERM_LC = 0.80, 0.80


def cap_C():
    W = 540
    g = Glyph('C', W, SB_ROUND, SB_ROUND - 30, 0x43)
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    g.sub(rect(W * 0.5, 236, W + 1, CAP - 236))
    g.sub(rect(W * TERM_UC, -OV_C - 1, W + 1, CAP + OV_C + 1))
    return reg(g)


def lc_c():
    W = 440
    g = Glyph('c', W, SB_ROUND, SB_ROUND - 26, 0x63)
    lc_bowl(g, W)
    g.sub(rect(W * 0.5, 178, W + 1, XH - 178))
    g.sub(rect(W * TERM_LC, -OV_L - 1, W + 1, XH + OV_L + 1))
    return reg(g)


def lc_e():
    W = RING_o
    g = Glyph('e', W, SB_ROUND, SB_ROUND - 6, 0x65)
    lc_bowl(g, W)
    yb = 226
    tl = tail(W / 2, -OV_L + h, W - v, v, 'r', 'down', tip_limit=yb - TAIL_CLEAR)
    g.sub(tl['disk'], rect(tl['xt'], -OV_L - 1, W + 1, min(tl['cy'], yb)),
          rect(W / 2, tl['tip'], W + 1, yb))
    # the tail's construction only works below the bar: give the bowl back above it
    g.group(ring(0, -OV_L, W, XH + OV_L, v, h, FULL, FULL) + [('sub', rect(-1, -OV_L - 2, W + 1, yb))])
    g.add(rect(v - 1, yb, W - v + 1, yb + h - 14))
    return reg(g)


def lc_a():
    """a: the arm is the top of the o-ring swinging down on the left and ending with the house
    tail (vertical cut, inner compass arc meeting it TAIL_PHI off vertical), tip clear of the bowl."""
    W = RING_o
    g = Glyph('a', W, SB_ROUND, SB_STRAIGHT, 0x61)
    hb = 300
    g.group([('add', rrect(0, -OV_L, W - v / 2, hb, (FULL, 0, 0, FULL))),
             ('sub', rrect(v, h - OV_L - 4, W - v + 1, hb - h + 10, (FULL, 0, 0, FULL)))])
    top = XH + OV_L
    y0 = top - W                                  # same curvature as the c / o bowls
    ta = tail(W / 2, top - h, v, v, 'l', 'up', tip_limit=hb + TAIL_CLEAR)
    g.group([('add', rrect(0, y0, W, top, (FULL, FULL, 0, 0))),
             ('sub', rrect(v, y0 - 1, W - v, top - h, (FULL, FULL, 0, 0))),
             ('sub', ta['disk']),
             ('sub', rect(W - v, y0 - 2, W + 1, hb)),                      # right side = the stem
             ('sub', rect(-1, y0 - 2, ta['xt'], top + 1)),
             ('sub', rect(-1, y0 - 2, W / 2, ta['tip']))])
    g.add(fstem(W - v, -OV_L, W, hb + 40, f=fl, top=False))
    g.add(rect(W - v, hb, W, top - 200))
    return reg(g)


def cap_C():
    W = RING_O
    top_c, bot_c = CAP + OV_C - H, -OV_C + H
    tu = tail(W / 2, top_c, W - V, V, 'r', 'up')
    tl = tail(W / 2, bot_c, W - V, V, 'r', 'down')
    g = Glyph('C', W, SB_ROUND, -(W - tu['xt']) + 52, 0x43)     # optical rsb ~52 from the cut
    apply(g, ring(0, -OV_C, W, CAP + OV_C, V, H, FULL, FULL))
    g.sub(tu['disk'], tl['disk'],
          rect(tu['xt'], tu['cy'], W + 1, CAP + OV_C + 1), rect(tl['xt'], -OV_C - 1, W + 1, tl['cy']))
    return reg(g)


def lc_c():
    W = RING_o
    top_c, bot_c = XH + OV_L - h, -OV_L + h               # counter's top / bottom points
    tu = tail(W / 2, top_c, W - v, v, 'r', 'up')
    tl = tail(W / 2, bot_c, W - v, v, 'r', 'down')
    g = Glyph('c', W, SB_ROUND, -(W - tu['xt']) + 48, 0x63)
    lc_bowl(g, W)
    g.sub(tu['disk'], tl['disk'],
          rect(tu['xt'], tu['cy'], W + 1, XH + OV_L + 1), rect(tl['xt'], -OV_L - 1, W + 1, tl['cy']))
    return reg(g)


def brush(path, w0, w1, n=None):
    """single-contour brush stroke: offset the centre line by +-w/2 (w tapers w0->w1)
    and close both ends with round caps. One clean outline, no overlapping dabs."""
    N = len(path)
    L, R = [], []
    for i in range(N):
        x, y = path[i]
        xa, ya = path[max(i - 1, 0)]; xb, yb = path[min(i + 1, N - 1)]
        dx, dy = xb - xa, yb - ya; d = _m.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        r = (w0 + (w1 - w0) * i / (N - 1)) / 2
        L.append((x + nx * r, y + ny * r)); R.append((x - nx * r, y - ny * r))
    def cap(i, start):
        x, y = path[i]
        xa, ya = path[max(i - 1, 0)]; xb, yb = path[min(i + 1, N - 1)]
        ang = _m.atan2(yb - ya, xb - xa)
        r = (w0 + (w1 - w0) * i / (N - 1)) / 2
        if start:   # from the right side round the back to the left side
            return [(x + r * _m.cos(ang - _m.pi / 2 - _m.pi * k / 10), y + r * _m.sin(ang - _m.pi / 2 - _m.pi * k / 10)) for k in range(1, 10)]
        # from the left side round the front to the right side
        return [(x + r * _m.cos(ang + _m.pi / 2 - _m.pi * k / 10), y + r * _m.sin(ang + _m.pi / 2 - _m.pi * k / 10)) for k in range(1, 10)]
    pts = L + cap(N - 1, False) + R[::-1] + cap(0, True)
    return [('add', poly([(round(px, 1), round(py, 1)) for px, py in pts]))]



def mk_breve(hgt=140, half=136, w=78):
    r = half - w / 2
    yc, ry = hgt - w / 2, hgt - w
    pts = [(r * _m.cos(a), yc + ry * _m.sin(a)) for a in [_m.pi + _m.pi * i / 16 for i in range(17)]]
    return brush(pts, w, w)


MARKS['breve'] = mk_breve
MARK_HGT['breve'] = 140


def mk_hook(hgt=188):
    cx, cy, r = 6, hgt - 70, 60
    arc = [(cx + r * _m.cos(a), cy + r * _m.sin(a)) for a in [_m.pi * (0.95 - 1.45 * i / 14) for i in range(15)]]
    tail = lerp_path(arc[-1], (cx - 6, 34), 5)[1:]
    return brush(arc + tail, 80, 60)


MARKS['hook'] = mk_hook
MARK_GAPS['side'] = {'acute': (184, 70), 'grave': (152, 70), 'hook': (152, 70)}   # verified: all gaps >= 41


# =====================================================================
# MARK KIT v2 (review 26/10: "dấu tròn quá, phải đồng bộ nét chữ", "không quá cao",
# "không dính nhau", "chấm giữ tròn") — see marks_flat.py for the construction notes.
# Offsets measured by tune2.py / qa_marks2.py: mark-mark gap ~30-31 (tighter, by review),
# mark-base >= 41.
# =====================================================================
import marks_flat as _mf
_mf.apply({'side': {'acute': (116 + _mf.STRIP_T * V, 56), 'grave': (182 + 0.27 * V, 56), 'hook': (116 + _mf.STRIP_T * V, 56)},   # v0.95c one-thickness marks;   # v0.95 R8d thin strips
           'stack_gap': 36, 'horn_tone_dx': 0})   # v0.95 "Ơ Ư sắc huyền không ngay giữa": tones centred on the letter (caps horn post is clear); v0.94: R8b marks are heavier -> side tones a touch wider; tones on horned letters clear the post   # 26/10 "2 dấu gần hơn": mark-mark gap ~30
