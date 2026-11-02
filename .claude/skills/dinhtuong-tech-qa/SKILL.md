---
name: dinhtuong-tech-qa
description: "Technical QA for Dinh Tuong with Font Bakery (make qa): run after every build and before every release, triage each FAIL / WARN / ERROR against documentation/qa/fontbakery-accepted.txt. Complements type-qa-qc (design QA)."
---

# Dinh Tuong — technical QA (Font Bakery)

`type-qa-qc` proves the drawing is right (stroke, junctions, marks, spacing, weights). This skill proves the
**files** are right: tables, metrics, names, outlines at the unit level, shaping. Font Bakery measures things the
design checks do not (a bar 1 u off level, a point 2 u off a guideline, soft-dotted shaping, metadata). Run both.

## When
- After every build (`make build`, or new binaries from a bundle) and before every PR to `main`, tag or release.
- After any change to a constructor, kerning, metrics, names or features.

## How
```bash
make qa                                     # Font Bakery 1.1.0 (requirements-qa.txt) on fonts/ttf + fonts/otf
python3 scripts/qa_fontbakery.py --no-run   # re-compare existing out/fontbakery/*.json only
```
- Profiles: `check-googlefonts` on `fonts/ttf/*.ttf`, `check-universal` on `fonts/otf/*.otf`, all three weights.
- Reports: `out/fontbakery/googlefonts.{json,md}`, `out/fontbakery/universal.{json,md}` (not committed).
- Long run (a few minutes): start it in the background; do not block on wait loops.
- CI runs the same `make qa` step in `.github/workflows/build.yaml` (next to fontspector, `make test`); it is blocking: a NEW result turns CI red. CI checks the fonts it rebuilds with fontmake, which can differ from `fonts/` by 1 u rounding, so the glyph lists per weight may differ from a local run while the check / code keys stay the same.

## Triage — every non-PASS result gets exactly one verdict
The script reduces results to `(profile, check id, code)` and compares with
`documentation/qa/fontbakery-accepted.txt` (`accept|todo profile check code  # reason`):

| Verdict | Meaning | Action |
|---|---|---|
| **NEW** | not listed | fails `make qa`. Fix it, or list it as `todo` / `accept` **with a reason** |
| **todo** | known defect or open designer decision | fix in the constructor (a fix is a rule), rebuild all weights, delete the line |
| **accept** | intentional or out of scope | keep the reason current; re-check it at each release |
| **network** | ERROR because a service (fonts.google.com, namecheck) was unreachable | not a font defect; re-run where the network is available (CI); `--strict` fails on it |
| **STALE** | listed but no longer reported | delete the line |

Rules:
- **FAIL / FATAL are never `accept`ed silently.** Each needs a written reason the designer agreed to.
- **Unit-level outline warnings are construction bugs, not noise.** `outline_semi_vertical` (a line 1–2 u off
  level/vertical), `outline_alignment_miss` (a point 1–2 u off baseline / x / cap / ascender),
  `outline_colinear_vectors` (a short segment continuing a line), `outline_short_segments`, `outline_jaggy_segments`:
  find the rule that produced the off-by-one (rounding of a sheared or offset construction, an overlap left in a
  union), fix the rule, and re-run on **every glyph that uses that rule**, not only the ones listed.
- An intended overshoot is not a misalignment: write the overshoot rule (amount per weight) and accept the check
  only for the glyphs it covers, listed by name in the reason.
- **Shaping warnings belong to the Vietnamese rule book:** `soft_dotted` → the dotless-ı / ȷ substitution (ccmp)
  for i / j / į / ị + combining marks; `alt_caron` → Ľ ď ľ ť use the comma caron; check NFD = NFC as well.
- Google Fonts-only metadata (vendor id registration, `meta` table, article, METADATA.pb subsets) may be
  `accept`ed while the family is not submitted to Google Fonts; say so in the reason.
- Never change the accepted list to make CI green without the verdict above; never skip or disable a check.

## Report (same order as type-qa-qc)
1. Counts: PASS / FAIL / WARN / ERROR per profile, and NEW / todo / accept / network / STALE.
2. Each NEW and todo item: check, code, weights, glyphs (by name), the rule responsible.
3. What changed in the accepted list and why.

## Baseline (1.003, main e1d0a15, Font Bakery 1.1.0, offline)
- googlefonts (TTF): PASS 283, FAIL 0, WARN 39, ERROR 21 (all network). universal (OTF): PASS 193, FAIL 0, WARN 6,
  ERROR 3 (network).
- 10 todo: outline_semi_vertical (E L Æ Œ S e b … Regular; Z z 7 ß Ħ Bold), outline_colinear_vectors (2, ², ½),
  outline_alignment_miss (77–87 glyphs per weight), soft_dotted, alt_caron, math_signs_width (< > ×),
  contour_count (§ į ť U+00AD), soft_hyphen.
- fontspector in CI (`make test`) additionally FAILs `googlefonts/repo/dirname_matches_nameid_1`: the repo is not in
  the google/fonts directory layout (fonts/ttf, not ofl/dinhtuong) — out of scope while not submitted.
