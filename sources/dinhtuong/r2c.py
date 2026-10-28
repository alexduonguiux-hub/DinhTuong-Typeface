"""R2c (28/10/2026, designer: 'nếu bold lên to hơn thì các chữ phải to đồng bộ'; chose the world standard).

ONE width-progression rule for caps, lowercase and figures. A heavier weight widens each glyph's body
by K[class] x (its case's stroke growth over Regular), so the extra stroke is shared between inside and
outside the same way everywhere and every counter shrinks by a similar amount (Regular units). Regular is
the master drawing: with zero stroke growth every width is exactly Regular's.

Classes and factors are the medians measured Regular -> Bold on Inter, Liberation Sans, DejaVu Sans and
Carlito (ink growth / stroke growth, same scan as width_audit.py):
  straight  two straight sides (H N U)                         1.0
  bowl      straight side + round side (B D P R)               0.9
  round     round both sides (O C G Q, o c e, figures 0 2 3 5 6 8 9 ?)  0.7
  s         S / s                                              0.75
  one       one straight side, open other side (E F L T Z, 7)  0.55
  diag      two diagonals (A V X Y)                            1.0
  multi     three or more sides (K M W)                        1.3
Single-stem glyphs (I l i 1) need no factor: their stroke is their width.
"""
import os

K = dict(straight=1.0, bowl=0.9, round=0.7, s=0.75, one=0.55, diag=1.0, multi=1.3, fig=0.8)
ON = os.environ.get('R2C', '1') == '1'


def grow(kind, d):
    """extra body width for a glyph of class `kind` whose case's stroke grew by d over Regular."""
    return K[kind] * d if ON else 0.0
