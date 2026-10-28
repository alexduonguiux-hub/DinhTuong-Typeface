"""R4c (28/10 01:34, designer: 'lưu ý các điểm loe phải giống nhau — tạo tính đồng bộ'): ONE flare everywhere.

Every free end (stems, diagonals, bar ends; caps, lowercase, figures, symbols) widens by the SAME amount F per side,
measured perpendicular to the stroke, over the SAME length L along the stroke, with the same curve (fstem's).
F follows the weight like every stroke (R2); L is one length in every weight. Before: caps 7/8/9, lowercase 6/7/8,
m 5/6/7, stems L = 0.26 x stem length (78-150), bars L = 0.3 x bar length (<= 110)."""
import os

F = {'regular': 7, 'medium': 8, 'bold': 9}[os.environ.get('A2_WEIGHT', 'regular')]
L = 120.0


def amt(f):
    """the flare of an end that flares at all (f > 0) is always F."""
    return F if f and f > 0 else 0


def length(run):
    """the flare's length along the stroke: L, but at most 0.45 of a short stroke's straight run."""
    return min(L, 0.45 * run)
