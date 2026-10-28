"""Minimum ink distance between every pair of parts (base, mark1, mark2) in all 134 Vietnamese letters."""
import sys, unicodedata, json
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from geo import flatten

def raster(ops, ox=400, oy=1300, W=1600, H=1800):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for op, c in ops:
        if op == 'group':
            gm = Image.fromarray(raster(c, ox, oy, W, H).astype(np.uint8) * 255)
            m = ImageChops.lighter(m, gm); d = ImageDraw.Draw(m); continue
        d.polygon([(x + ox, oy - y) for x, y in flatten(c, 20)], fill=255 if op == 'add' else 0)
    return np.array(m) > 127

def edge_pts(a):
    e = a & ~(np.roll(a, 1, 0) & np.roll(a, -1, 0) & np.roll(a, 1, 1) & np.roll(a, -1, 1))
    ys, xs = np.where(e); return np.stack([xs, ys], 1).astype(np.float32)

def min_dist(a, b):
    if (a & b).any(): return 0.0
    pa, pb = edge_pts(a), edge_pts(b)
    best = 1e9
    for i in range(0, len(pa), 400):
        d = np.sqrt(((pa[i:i+400, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()
        best = min(best, d)
    return float(best)

def run(GL, label):
    lcv = 'aăâeêioôơuưy'; tones = ['', '́', '̀', '̉', '̃', '̣']
    chars = []
    for b in lcv:
        for t in tones:
            ch = unicodedata.normalize('NFC', b + t)
            if ch not in 'aeiouy': chars.append(ch)
    chars += [c.upper() for c in chars]
    rows = []
    for ch in chars:
        g = GL.compose(ch)
        rs = [(n, raster(o)) for n, o in g.parts]
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                rows.append((ch, rs[i][0], rs[j][0], round(min_dist(rs[i][1], rs[j][1]), 1)))
    return rows
