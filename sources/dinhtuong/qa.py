"""Measured QA of the glyph geometry (1 px = 1 font unit)."""
import json, sys, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from geo import flatten, CAP, XH, ASC, DESC

TOP, BOT = 1250, -400
H_IMG = TOP - BOT


def render(ops, width, ox, m=None):
    if m is None:
        m = Image.new('L', (int(width) + 2, H_IMG), 0)
    d = ImageDraw.Draw(m)
    for op, c in ops:
        if op == 'group':
            gm = render(c, width, ox)
            m = ImageChops.lighter(m, gm); d = ImageDraw.Draw(m); continue
        pts = [(x + ox, TOP - y) for x, y in flatten(c, 24)]
        d.polygon(pts, fill=255 if op == 'add' else 0)
    return m


def arr(g):
    pad = 300
    m = render(g.ops, g.advance + 2 * pad, g.lsb + pad)
    return (np.array(m) > 127), pad


def bbox(g):
    a, pad = arr(g)
    ys, xs = np.where(a)
    if len(xs) == 0:
        return None
    return xs.min() - pad, xs.max() + 1 - pad, TOP - ys.max() - 1, TOP - ys.min()


def runs_row(g, y):
    a, pad = arr(g)
    row = a[TOP - int(y)]
    out, x, n = [], 0, len(row)
    while x < n:
        if row[x]:
            s = x
            while x < n and row[x]:
                x += 1
            out.append((s - pad, x - s))
        x += 1
    return out


def runs_col(g, x):
    a, pad = arr(g)
    col = a[:, int(x) + pad]
    out, y, n = [], 0, len(col)
    while y < n:
        if col[y]:
            s = y
            while y < n and col[y]:
                y += 1
            out.append((TOP - y, y - s))
        y += 1
    return out


def ink(g, zone_top):
    a, pad = arr(g)
    return a.sum() / (g.advance * zone_top)
