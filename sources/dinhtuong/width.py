"""C2/C3 (vf-condensed-concept-v1, approved 31/10: 80 %, same VF with a wdth axis, marks keep the Normal size).

DT_WIDTH = body width factor of the Condensed masters (1.0 = Normal, 0.80 = Condensed). Strokes follow the measured
references (Roboto Archivo Encode Saira Barlow, wdth 100 -> 75): vertical stems x 0.93, horizontals x 0.96 at 0.80,
linear in between. Sidebearings x 0.85 at 0.80 (C8). Vietnamese marks are NOT scaled (C7)."""
import os
WID = float(os.environ.get('DT_WIDTH', '1.0'))
_f = (1.0 - WID) / 0.20
SV = 1.0 - 0.07 * _f          # vertical stems
SH = 1.0 - 0.04 * _f          # horizontals
SSB = 1.0 - 0.15 * _f         # sidebearings


def cw(x):
    """a body width (Normal units) in this width."""
    return x * WID


def strokes(d):
    """scale one weight's stroke table: V v (verticals) by SV, H HM h (horizontals) by SH."""
    out = dict(d)
    for k in ('V', 'v'):
        if k in out:
            out[k] = round(out[k] * SV)
    for k in ('H', 'HM', 'h'):
        if k in out:
            out[k] = round(out[k] * SH)
    if 'SB' in out:
        out['SB'] = tuple(round(s * SSB) for s in out['SB'])
    return out
