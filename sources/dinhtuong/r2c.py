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

# W2 (1.010, designer: 'Khi bold lên các chữ hoa bị rộng ra quá nhiều làm hư form chữ'): capitals and figures take
# CAP_K of their class growth (Bold caps were +4.8 % wide, Extra Bold +6.3 %, the diagonals and T up to +9-10 %); the
# rest of the stroke goes inside, so the heavier capitals keep Regular's proportions. Lowercase unchanged.
CAP_K = float(os.environ.get('CAP_K', '0.25'))   # W4 (1.011, 'các chữ bold lên vẫn rộng hơn chữ regular nhiều quá'): a quarter (1.010: half)
# W3 (1.010, designer: 'các chữ thường bold cũng hơi rộng'): lowercase takes LC_K of its width growth too (Bold
# lowercase was +7.5 % wide, Extra Bold +10 %; v x y z 14-16 %, n h m u s 9-10 %)
LC_K = float(os.environ.get('LC_K', '0.25'))   # W4 (1.011): a quarter (1.010: half)
K = dict(straight=1.0, bowl=0.9, round=0.7, s=0.75, one=0.55, diag=1.0, multi=1.3, fig=0.8)
ON = os.environ.get('R2C', '1') == '1'


def grow(kind, d):
    """extra body width for a glyph of class `kind` whose case's stroke grew by d over Regular."""
    return K[kind] * d if ON else 0.0


def grow_caps(kind, d):
    """R2c for capitals and figures (W2): CAP_K of the class growth."""
    return CAP_K * grow(kind, d)
