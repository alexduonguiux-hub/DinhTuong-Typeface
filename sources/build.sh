#!/bin/sh
# Dinh Tuong: one-step build (Google Fonts: sources/build.sh).
# The generators in sources/dinhtuong/ draw every glyph from its construction rules and compile the fonts;
# gf_release.py writes the Google Fonts names / metadata; export_ufo.py writes the UFO copies to sources/ufo/.
set -e
VERSION=${VERSION:-0.980}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT/sources/dinhtuong"
for w in regular medium bold; do LC_OPT=f A2_WEIGHT=$w python3 lcsym.py; done
for w in regular medium bold; do
  LC_OPT=f A2_WEIGHT=$w REL=$VERSION OUTD="$ROOT/sources/out" sh -c "python3 lcfont.py && python3 build96.py" &
done
wait
python3 gf_release.py "$ROOT/sources/out" "$ROOT" "$VERSION"
for s in Regular Medium Bold; do
  w=$(echo $s | tr 'A-Z' 'a-z')
  python3 export_ufo.py "$ROOT/fonts/otf/DinhTuong-$s.otf" "$ROOT/sources/out/kern_v096_$w.json" \
    "$ROOT/sources/out/DINHTUONG60s-$s.fea" "$ROOT/sources/ufo/DinhTuong-$s.ufo"
done
echo "built: $ROOT/fonts"
