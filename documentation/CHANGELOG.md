# Changelog

## 1.002 (2026-10-31)
- New **acute** (dấu sắc), after the designer's sample. It is the grave strip (huyền) sheared up to the right: both ends cut vertically, the same vertical thickness as every mark, rising 27°, 195 units wide. Huyền stays level and sắc now leans, so the two read apart at any size.
  - Alone (Á É Í Ó Ú Ý Ớ Ứ, á é í ó ú ý …): it sits on the mark zone, centred on the letter.
  - On the breve (Ắ ắ): it keeps 35 units from the breve and sits 62 units right of the axis.
  - On the circumflex (Ấ Ế Ố ấ ế ố): it rides behind the circumflex, over its right arm. Its centre is 189 units (capitals) / 212 units (lowercase) right of the circumflex's centre, but never further right than the letter's own ink. Capitals sit on Ắ's line; lowercase keep 40 units from the circumflex.
  - The spacing acute ´, the combining acute and the acute of Ć Ĺ Ń Ŕ Ś Ź Ẃ (and lowercase) use the same mark.
- New **double acute** (Ő Ű ő ű ˝ and the combining mark). It follows the new acute, the same way most typefaces derive it (6 of 8 reference fonts keep the single acute's angle; the pair spans 0.55–0.68 of the O). Two parallel acute strips, each 0.75 of the acute's width, at the same 27° rise, on one foot line, with a 40-unit ink gap between them. The pair is about 0.62 of the O.
- New **circumflex** (mũ), after the designer's sample. Two strips of the new acute meeting in a pointed apex, inside and out. Each arm rises 30°, the outer ends are cut vertically, the vertical thickness is that of every mark, and the mark is 240 units wide. It sits 40 units above its letter's ink (Â 720, Ê 739, â 563 in Bold), so each letter keeps the same gap. Hỏi beside the circumflex (Ẩ ẩ) also keeps 40 units from it.
  - The same mark serves Ĉ Ĝ Ĥ Ĵ Ŝ Ŵ Ŷ and their lowercase, the spacing ˆ, the combining circumflex and ^.
  - The caron (Č Ě Ň Ř Š Ž and lowercase, ˇ) is this circumflex turned over, as before.
- New **tilde** (ngã), after the designer's sample. Its curve is balanced: the crest and trough sit at 0.29 / 0.71 of the width, the left end's lower corner on the trough line and the right end's upper corner on the crest line. The old tilde stopped at mid height and read as leaning down to the right. Each edge is three smooth curves with nodes only at its ends and extremes. Applies to Ã Ẽ Ĩ Õ Ũ Ỹ Ñ, the stacked Ẫ Ễ Ỗ, ˜, ~ and the combining tilde.
- All marks share one stroke weight, measured square to the stroke: the sloped strips of the acute, double acute, circumflex and caron are cut T / cos(angle) thick vertically, so they read as heavy as the level grave, breve, tilde, hook and dot below (before: 0.89–0.92 T).
- **S s** (and Ś Š Ş Ŝ Ș $ with their lowercase): the spine now joins both bowls tangentially in every weight. The boolean re-fit had left 4–18° kinks at the joins; the largest break is now 0.7–2.4°. The masters are also point-compatible, so the static fonts and the coming variable font draw the same outlines.
- Kerning re-run for every pair with a changed letter (acute, double acute, circumflex, caron). Every Vietnamese marked-letter pair inside a Vietnamese syllable (lowercase, Capitalised, ALL CAPS) keeps at least 26 units of ink gap. The only exceptions are the Bold É / Ế + t, v, y pairs, which are as tight as E + t, v, y in 1.001.
- Figure kerning: 6 7 and 7 6 are set as close as 6 9 and 9 6 (67: −50 / −45 / −40, 76: −40 / −35 / −35 in Regular / Medium / Bold); they were 26–32 units looser.
- The highest point of the font drops from 1102 to 1097 (Bold Ế). Vertical metrics are unchanged.

## 1.001 (2026-10-29)
- Lowercase **ß**, **ð** and **þ** are drawn as true lowercase letters. Until now ß was replaced by "SS" (a `ccmp` rule left from the capitals-only edition) and ð þ were typed as the capitals Ð Þ.
  - þ = the b and the p on one stem: the p's bowl, the stem running from the descender to the ascender.
  - ð = the o with the straight diagonal of the 6 and 9 (tangent to the ring, 12° off vertical, level cut on the ascender) and the bar of đ / ħ.
  - ß = a stem with two stacked elliptic rings (like s and 3): the upper ring springs from the stem and ends near it with a vertical cut (the e's aperture), the lower ring ends in the house tail, clear of the stem's foot.
- The `ccmp` rule ß → SS is removed. Kerning: þ kerns like p, ð like o, ß like h on the left and b on the right; every pair keeps at least 26 units of ink gap.

## 1.000 (2026-10-28) — first Google Fonts release
- Family renamed **Dinh Tuong** (was DINHTUONG / DINHTUONG60s). Files `DinhTuong-Regular / -Medium / -Bold`.
- Licensed under the SIL Open Font License 1.1.
- Character set extended to **GF Latin Core** (79 new characters): Ā Ą Ċ Č Ď Ē Ė Ę Ě Ġ Ģ Ħ Ī Į İ Ķ Ļ Ľ Ł Ņ Ň Ő Ř Ş Ť Ū Ů Ű Ų Ż Ș Ț Ẁ Ẃ Ẅ ẞ and their lowercase, ȷ, ˘ ˙ ˛ ˝ and the combining dot above, double acute, comma below and ogonek. New mark rules, all cut from the existing kit: dot above, double acute (two 18° acutes), ogonek (the mirrored cedilla), comma below (also for Latvian Ģ Ķ Ļ Ņ; ģ takes the turned comma), the apostrophe caron on ď ľ ť Ľ, the Ł slash and the Ħ / ħ bar.
- Figures 1, 6, 9 redrawn after the designer's "196" sample: the 6 and 9 are a circular counter in an elliptic ring with one straight diagonal tangent to it (6 = 9 turned 180°); the 1 has the diagonal's thickness and a longer wedge flag.
- Figure 2 redrawn after the designer's sample (0.915 of the 9, strokes synchronised with the other figures). Figure 5: the tail is cut flush with the stem, the bowl sits higher (0.645 cap) and the head is pulled in by half a figure stem. Figure 3: the lower tail is cut flush under the upper one. Figure 4: 1.04 × the 0 in every weight.
- Capitals re-proportioned for optical balance, measured as ratios against Inter, Liberation, DejaVu, Carlito and Poppins while keeping the narrow upright-ellipse O C G Q: U = H + 1.5 %, D = 0.977 O, B = 0.95 R, P = 0.96 B, K = 1.02 H; T and Z keep their ratio to H in the heavier weights; the 3 is wider (0.95 of the 8).
- The macron is the house mark strip cut to 0.6 of its length, so Ā ā Ē ē Ī ī Ū ū no longer read like À à (the Vietnamese grave is the full-length strip lying).
- Dutch: J́ and j́ (íj́ ÍJ́) through ccmp.
- Vertical metrics 1050 / −350 (line 1.40): the capitals sit centred in the line box, so text centres in UI containers; Vietnamese stacks stay inside the line.
- Bar ends lying on the baseline or the cap height no longer flare past it (T E F L Z 7 5 are exactly 700 tall, like H I).
- Lowercase joints: the arch of n m r h u leaves the stem through a deeper cut (0.14 x-height), so the shoulder thins into the joint.
- Kerning: lowercase pairs never close in at one point tighter than the references (eg, eo, ru …).
- S and s: each spine edge is one curve with a true inflection, joined to the bowls with matching tangent and curvature (no ripple at the centre); the spine weighs 0.96 of the side stroke in every weight, like the reference fonts (no bulge in Bold).
- Kerning: every pair checked (about 135,000 per weight) and kept inside the envelope of Inter, Liberation, DejaVu, Carlito and Poppins (figure pairs never looser than their median, e.g. 96); no pair closer than an ink gap of 26 units.

## 0.973
- Lowercase r ends in a vertical cut (50° inner corner, like c); g keeps Regular's tail curve in every weight; capital G with one vertical cut and a stretched round; I i l spacing; z diagonal weight.

## 0.972
- Capital Ư horn depth per weight; visual-weight review.

## 0.971
- Full-length grave on ì Ì.

## 0.970
- Acute tilted 18°, one top line for stacked acutes (ấ ắ ế ố); C G kerning never closer than O.

## 0.969
- Complete Vietnamese, English, French and Spanish; lowercase æ œ ø; narrow no-break spaces.

## 0.961 – 0.968
- Lowercase (option F) added to the capitals; consistent weight growth (R2c); spacing by optical white (S1c).
