"""Optical auto-kerning + Vietnamese mark-collision guard.
Method: for every pair, measure the horizontal white gap row-by-row inside the shared band,
clamp each row at a max depth (so open counters don't count as infinite space),
compare the mean against the reference pair (HH for caps, nn for lowercase, Hn for mixed)
and kern the difference. Values rounded to 5 units, |k| < 15 dropped."""
import sys, json, unicodedata
import numpy as np
import qa
from geo import CAP, XH

DEPTH = 150          # max white counted per row (units)
MIN_CLEAR = 34       # minimum ink-to-ink distance after kerning (units)
STRENGTH = 0.7
MASK = {}


def mask(g):
    if g.name in MASK:
        return MASK[g.name]
    a, pad = qa.arr(g)
    rows = a.shape[0]
    right = np.full(rows, np.nan); left = np.full(rows, np.nan)
    for r in range(rows):
        xs = np.where(a[r])[0]
        if len(xs):
            left[r] = xs[0] - pad
            right[r] = xs[-1] + 1 - pad
    MASK[g.name] = (left, right, g.advance)
    return MASK[g.name]


def band_rows(y0, y1):
    return slice(qa.TOP - int(y1), qa.TOP - int(y0))


def gaps(L, R, y0, y1, k=0):
    lL, rL, aL = mask(L); lR, rR, aR = mask(R)
    sl = band_rows(y0, y1)
    gl = aL - rL[sl]; gr = lR[sl]
    gl = np.where(np.isnan(gl), DEPTH, gl); gr = np.where(np.isnan(gr), DEPTH, gr)
    d = np.minimum(gl, DEPTH) + np.minimum(gr, DEPTH) + k
    return d


def raw_gap(L, R, y0, y1, k=0):
    """true minimum distance between ink in band (for collision tests)."""
    lL, rL, aL = mask(L); lR, rR, aR = mask(R)
    sl = band_rows(y0, y1)
    d = (aL - rL[sl]) + lR[sl] + k
    d = d[~np.isnan(d)]
    return d.min() if len(d) else 9999


def band_for(a, b):
    top = min(CAP if a.isupper() else XH, CAP if b.isupper() else XH)
    return 0, top


def autokern(G, left_set, right_set, ref):
    out = {}
    for a in left_set:
        for b in right_set:
            y0, y1 = band_for(a, b)
            r = ref[(a.isupper(), b.isupper())]
            refv = gaps(G[r[0]], G[r[1]], y0, y1).mean()
            v = gaps(G[a], G[b], y0, y1).mean()
            k = (refv - v) * STRENGTH
            # hard clearance: ink of the two glyphs never closer than MIN_CLEAR anywhere
            clear = raw_gap(G[a], G[b], -300, 1100)
            k = max(k, MIN_CLEAR - clear) if clear < 9000 else k
            k = int(round(k / 5.0)) * 5
            k = max(-150, min(40, k))
            if abs(k) >= 20:
                out[a + b] = k
    return out


def mark_guard(GL, G, kerns, min_gap=36):
    """For lowercase-with-top-marks after caps with top overhang (T, V, W, Y, F, P...),
    reduce kerning so marks never collide with the cap. Returns exceptions {pair: k}."""
    exc = {}
    lcv = 'aăâeêioôơuưy'
    tones = ['́', '̀', '̉', '̃']
    for pair, k in kerns.items():
        a, b = pair[0], pair[1]
        if not ((a.isupper() or a == 'f') and b in 'aeiouy'):
            continue
        for base in lcv:
            if unicodedata.normalize('NFD', base)[0] != b:
                continue
            for t in [''] + tones:
                ch = unicodedata.normalize('NFC', base + t)
                if ch == b:
                    continue
                g = GL.compose(ch)
                gap = raw_gap(G[a], g, XH + 20, CAP + 400, k)
                if gap < min_gap:
                    need = k + (min_gap - gap)
                    need = int(np.ceil(need / 5.0)) * 5
                    exc[a + ch] = min(0, need)
    return exc
