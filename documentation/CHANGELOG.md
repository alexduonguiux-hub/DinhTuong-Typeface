# Changelog

## 1.004 (unreleased)
- **Parentheses ( )** redrawn (R17, after the designer: "sửa phần cắt của dấu ()"). They are now a true compass ring, an outer oval minus a counter oval, like the hook mark and the ?. The old polygon band left a wavy counter, and short kinked segments in Bold. Each end is cut square to the stroke, with 90° corners; the outer corner sits on the bracket lines (790 / −140) shared with [ ] { }. The old end was half a level cut and half the band's own end, which made a bevel. The ends are about 25 units shorter. Kerning of every pair with ( or ) was re-measured.
- **Straight runs are exactly level or vertical** (outline rule R-axis). Rounding after the boolean unions had left lines 1–2 units off level or vertical: the foot bar of E L Æ Œ and every accented E / L (Ê Ế … Ệ included), the bar of e æ œ and every ê, S, b, $, @, € in Regular, Ħ in Medium, Z z 7 ß b Ħ and their accented forms in Bold. Each run is made exactly level or vertical by moving the end that does not continue along it; no outline moves by more than 1 unit (@: 2 units).
- **Near-collinear points removed** (outline rule R-colinear): 2 and the tabular 2 (Regular), ² ½ ¾ and the comma / quote shapes (Medium) had a point within 1 unit of a straight line. Bold 7ï is kerned 10 (was 15) after the 7's cut was straightened.
- **Diagonal weight evened out** (D1, after the designer: "độ dày các chữ x, W, Y hoa so với các chữ khác có vẻ cũng chưa cân bằng"; chosen: "B, M bằng W luôn"). Measured square to the stroke against the stem:
  - **W w** are drawn with the same diagonal weight as V v (0.86–0.88; they were 0.80–0.82, lighter by rule). The Regular W keeps its width. The accented forms (Ẁ Ẃ Ŵ Ẅ and lowercase) follow.
  - **M**: its diagonals match W's at mid-height in every weight, with the same ink trap as every vertex (0.85–0.86; they were 0.73, because the stroke had been solved on the wrong run). ™ follows.
  - **x**: 0.88 / 0.87 / 0.88 in Regular / Medium / Bold (was 0.88 / 0.90 / 0.93: it grew heavier with the weight). The Regular x is unchanged.
  - Y is unchanged: its arms already measure as V (0.84–0.88).
  - Kerning re-measured for every pair with a changed glyph (e.g. Bold AW −85 → −90).
- **Soft-dotted i j į ị** (SD1, Font Bakery soft_dotted). The dot of i, j, į, ị now goes whenever a combining mark is set above it, also with a mark below or the horn in between: i + ◌̊, j + ◌̀, į + ◌́, ị + ◌̂ and the other 37 test sequences. The ccmp feature swaps in ı, ȷ and two new glyphs, į and ị without their dot. Precomposed letters and Vietnamese input (NFC or NFD) render exactly as before.
- **į has its dot again.** It had been drawn on ı in every weight. It is now built on i, which makes it 6 units narrower; kerning was re-measured for its pairs.
- **ť**: the comma-form caron came down onto the crossbar (it touched the t, the gap was 0). It now stands 40 units over the x-height with its top on the ascender, like ď and ľ. It is scaled to that room (about 170 units; Inter, Liberation, DejaVu and Carlito use 155–185). The mark-to-letter gap is 41–42 units, against the rule of ≥ 38. ť is narrower (Regular 364 → 328), and its kerning was re-measured. Ľ ď ľ were checked and are unchanged.
- **Math signs share one width** (M1): × < > now sit on the 560-unit width of + − = ÷ ± ¬ (they were 500 and 512), with the ink centred. Their outlines are unchanged; only the sidebearings change, so the signs line up in tabular settings.
- **§ redrawn** (R0c, after the designer: "vẽ lại §"). It was two s stacked 370 units apart, so the bowls overlapped off-centre and the middle filled solid. It is now built from the s: its lower ring, used whole as the shared middle loop; its upper half (upper ring and spine); and that half turned 180° about the ring's centre. The counter is the ring's own counter ellipse, cut last, so it is smooth, centred and point-symmetric, open in every weight (after the designer: "smooth và cân"). No terminal cut is left on or inside the loop. Every stroke, terminal and the spine are exactly the s's. The § is point-symmetric, with its top on the lowercase ascender line (it was 53 units above it), and it has two contours like the reference fonts.
- **Soft hyphen (U+00AD)** is an empty, zero-width glyph (designer's choice; it was a copy of the hyphen). Renderers draw the hyphen where they break the line.
- **Micro segments absorbed** (outline rule R-absorb). A straight segment shorter than 6.5 units that continues a curve smoothly is taken over by that curve; the corner at its other end stays, and the outline moves by at most 1 unit (measured: 0.92 at most). These segments were left by rounding after the unions: at stem / bowl notches (b d g p q đ ď ģ), bar joins (t ț Ħ), terminals (? ¿), braces and the Vietnamese ỏ ở ỷ … family. The rule applies in 32 / 28 / 34 glyphs (Regular / Medium / Bold). Short segments in the design drop from 101 / 99 / 129 to 76 / 81 / 109. The rest are designed cuts that Font Bakery flags only because it measures them against the contour's length.
- Font Bakery: outline_semi_vertical, outline_colinear_vectors, soft_dotted, math_signs_width and contour_count now pass in every weight; alt_caron, outline_alignment_miss and outline_short_segments were checked and accepted with their reasons (documentation/qa/fontbakery-accepted.txt).
- **Even-stroke corners** (R-conc / R-conc2, after the designer: "đường cong trong và ngoài nên đồng tâm", then "dựng đường trong bằng offset cho nét đều tuyệt đối"). The turns of the cedilla (Ç ç Ş ş and the combining cedilla), the ogonek (Ą ą Ę ę Į į Ų ų and the combining ogonek) and { } swelled because the inner and outer arcs did not match. The inner curve is now the true offset of the outer one: each outer point moves inward along its normal by the stroke weight in that direction (vertical stroke → horizontal stroke), and one cubic is fitted to the result. The outer corner also keeps its design radius. Before, it was cut to half the side of its box, which no offset could follow. Thickness across the turn now never exceeds the stroke: ogonek Regular 76 → 70 (stroke 70), Bold 107 → 101 (stroke 101); cedilla Regular 64 → 62 (61), Bold 91 → 87 (88). The corners of { } are noticeably rounder. Kerning was re-measured for the pairs with these glyphs.
- **The released glyphs now match the UFO sources exactly** (designer 04/11: "chuyển toàn bộ sang bản UFO"). Earlier releases replaced only the glyphs a change touched, so 150–180 glyphs per weight kept outlines from older builds. Most of these were only TTF curve-conversion differences, but some differed in design: the horn of Ư ư and Ơ ơ with their accented forms (the Ơ family was mixed), the commas below Ģ Ķ Ļ Ņ Ț ķ ļ ņ ț, ¬, F, ¥, 3 and ³, the ogonek of Ą Ų, Ħ and Œ. Every glyph in the OTF and TTF is now the fontmake build of the UFO, with overlaps removed. No advance width changed, and the vertical extents and metrics are unchanged.
- **e family unified on the tapered tail (designer 04/11: "chuyển sang e thuôn trong UFO").** In Medium and Bold, 1.003 mixed two e tails. é ê ě ẽ ệ, rebuilt in 1.002 for the new marks, came from the UFO with the tapered tail, which follows the revert of R5i/R5j. e è ē ĕ ė ë ę ẹ æ œ still carried the 1.001 full-stroke cut. All of them now use the UFO e (7–9 units at the tail). The Regular e was already consistent; Regular œ was aligned too.

## 1.003 (2026-11-01)
- Kerning floor (R16d): every pair of letters, figures and . , : ; ! ? - was measured against Inter, Poppins, Liberation and Carlito, over the cap height whenever a capital is involved. Pairs tighter than the tightest of them are opened to it (357 / 293 / 411 base pairs, accented forms included; only ever opens). The largest change is F + lowercase, which had lost the white above the x-height: Fa −90 → −35, Fr −90 → −30, Fe / Fo −55 → −35 in Regular; also T, P, K + lowercase and r + capitals. 67 / 76 and the diagonal capital pairs keep the values chosen above.

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
- Kerning of capitals whose diagonals meet at one point (K A, X A, A X, A A, R A, R X, K V W X Y, and V W X Y with each other, accented forms included): these were held open by the 26-unit ink floor although the white opens into a wide V right above the contact. Their feet / arm tips now overlap by 40 / 42 / 44 units (Regular / Medium / Bold); KA = −61 / −57 / −52 (was +10 / +15 / +20). Marks of accented forms keep at least 26 units from the other letter. No other pair changes.
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
