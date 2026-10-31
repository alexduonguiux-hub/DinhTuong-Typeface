#!/bin/sh
# 1.002 release rebuild (marks R8i-R8m, kerning rules), keeping every unchanged glyph byte-identical to 1.001.
# Needs: S = scratch dir with r2 (mode 2 = 1.001 rules) and r4 (current rules) generator copies, fonts-1.001, ufo_1001.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); S=${S:?}
for f in marks_flat.py glyphs_c.py lcfont.py latin1_c.py latin_core_c.py build96.py; do cp "$ROOT/sources/dinhtuong/$f" "$S/r4/sources/dinhtuong/"; done
(cd "$S/r4" && sh sources/generate.sh > "$S/r4.log" 2>&1)
python3 "$S/transplant.py"                                  # UFO = 1.001 + changed glyphs, fea / fontinfo from r4
(cd "$ROOT/sources/dinhtuong" && python3 vf_compat.py ../ufo/DinhTuong-Regular.ufo ../ufo/DinhTuong-Medium.ufo ../ufo/DinhTuong-Bold.ufo >/dev/null \
  && python3 s_spine_fix.py spine_data.json ../ufo/DinhTuong-Regular.ufo ../ufo/DinhTuong-Medium.ufo ../ufo/DinhTuong-Bold.ufo >/dev/null \
  && python3 vf_compat.py ../ufo/DinhTuong-Regular.ufo ../ufo/DinhTuong-Medium.ufo ../ufo/DinhTuong-Bold.ufo | head -1)
