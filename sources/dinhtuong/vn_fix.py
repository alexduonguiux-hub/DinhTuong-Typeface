"""v0.962 Vietnamese kerning fixes (27/10 15:51 'kerning chưa tối ưu tiếng Việt'; audit kqa_vn.py; sources: Trương
'Việt Type', Glyphs 'Kerning', Kern On manual). Applied by lcfont right after the capitals are built.

S1c  (measured, not applied) Caps spacing: every capital side is set so that its optical white against H equals H|H (the same row-by-row
     measure, counters 40 u deep, as the kerning and as the lowercase S1). Kerning then carries only the
     interaction of two shapes, not a side that was spaced too loose (C O S Z were kerned negative against
     nearly every capital). Accented capitals take their base letter's change; H and I are the reference.
S1i  Narrow capitals with a wide mark (Ì Í Î Ï Ĩ Ỉ Ị) keep I's sidebearings; the mark may overhang (it sits above
     the cap line, clear of the neighbours' ink). Opening I for the mark made HĨ, ĨN 22-36 u looser than HI, IN.
R8c2 Horn reach (Trương: 'shortening the length of the U-horn is preferred over the overlapping of the two
     letters'): the Ư / ư horn's tip may pass the stem only by the white a straight neighbour leaves, minus the
     letter clearance: reach = rsb(U) + lsb(U) + k(UU) - 26 (caps), rsb(u) + lsb(n) - 26 (lowercase). The post keeps
     its width (0.60 V) and height; the slot closes first, then the post stands over the stem. The horn no
     longer widens the advance. Ơ / ơ unchanged (their post is already flush with the O).
F13  đ bar: 25 (Regular units) past the stem on the right, sidebearing + 10 (was 50 / + 20): đĩ = đi.
"""
import unicodedata
import kern

HORN = '̛'
PAIR_MIN = 26
REF = 'HI'
TUNE = 'ABCDEFGJKLMNOPQRSTUVWXYZÆŒØÐÞĐ'


def narrow_caps(CAPS):
    """S1i only."""
    I = CAPS['I']
    n = 0
    for ch, g in CAPS.items():
        if len(ch) == 1 and ch != 'I' and unicodedata.normalize('NFD', ch)[0] == 'I':
            g.lsb, g.rsb = I.lsb, I.rsb; n += 1
    return n


def tune_caps(CAPS, cap=700, rounds=3, k=0.85):
    """S1c + S1i (measured 27/10: the caps' R13 sides already equal H|H white within 6 u, except C right +14;
    NOT applied in v0.962, kept for the record). Returns {letter: (dl, dr)}."""
    depth0, kern.DEPTH = kern.DEPTH, 40
    H = CAPS['H']
    names = [c for c in TUNE if c in CAPS]
    orig = {c: (CAPS[c].lsb, CAPS[c].rsb) for c in names}
    for _ in range(rounds):
        kern.MASK.clear()
        ref = kern.gaps(H, H, 0, cap).mean()
        for c in names:
            g = CAPS[c]
            dl = ref - kern.gaps(H, g, 0, cap).mean()
            dr = ref - kern.gaps(g, H, 0, cap).mean()
            g.lsb = max(4, g.lsb + k * dl)
            g.rsb = max(4, g.rsb + k * dr)
            kern.MASK.pop(g.name, None)
    kern.MASK.clear()
    kern.DEPTH = depth0
    delta = {c: (CAPS[c].lsb - orig[c][0], CAPS[c].rsb - orig[c][1]) for c in names}
    I = CAPS['I']
    for ch, g in CAPS.items():
        if len(ch) != 1 or not ch.isupper() or ch in delta:
            continue
        b = unicodedata.normalize('NFD', ch)[0]
        if b == 'I' and ch != 'I':
            g.lsb, g.rsb = I.lsb, I.rsb                      # S1i
        elif b in delta:
            g.lsb += delta[b][0]; g.rsb += delta[b][1]
    if 'ß' in CAPS and 'S' in delta:                         # ß is typed as S S (slot drawn as S)
        CAPS['ß'].lsb, CAPS['ß'].rsb = CAPS['S'].lsb, CAPS['S'].rsb
    return delta


HORN_SLOT_U = -21   # R8c3 (28/10 13:34 'dấu Ư hoa khi bold bị sát vào thân quá' / 13:37 'Bold chấp nhận thụt vào xíu để không
                    # đụng chữ kế bên'): the post's slot to the stem never sinks deeper than it must. Old rule: the slot was
                    # refitted to the room left by U's own NEGATIVE kerning (UU −30 Bold), so Bold's post sank 73 into the
                    # stem (Medium 44, Regular 21). New: the horn may use the letter's full side bearings (ƯU kern 0, still
                    # PAIR_MIN clear of the next letter) but never stands shallower than Regular's slot (−21):
                    # slot = max(fit to the kerned room, min(−21, fit to the unkerned room)) → R −21 · M −21 · B −43.


def horn_fit(x_wall, y_top, upper, reach, reach0=None):
    """R8c2: the v0.95b L-plate with its tip `reach` past the stem's right wall."""
    import marks_flat as MF, glyphs_c as GL, os
    st = GL.V if upper else GL.v
    g = min(MF.HP_G, reach / st - MF.HP_W)
    if upper and reach0 is not None and os.environ.get('HORN_SLOT', '1') == '1':
        g = max(g, min(HORN_SLOT_U / st, reach0 / st - MF.HP_W))     # R8c3
    save, MF.HP_G = MF.HP_G, g
    try:
        return MF.horn_ops(x_wall, y_top, upper)
    finally:
        MF.HP_G = save


def caps_horn(CAPS, cap=700):
    """R8c2 on Ư and its toned forms."""
    U, H = CAPS['U'], CAPS['H']
    # the tightest straight neighbour in Vietnamese caps is U itself (HƯU, CỨU, MƯU): its own kerning counts
    kuu = kern.autokern(CAPS, ['U'], ['U'], {(True, True): 'HH'}).get('UU', 0)
    kern.MASK.clear()
    reach = U.rsb + U.lsb + min(0, kuu) - PAIR_MIN
    reach0 = U.rsb + U.lsb - PAIR_MIN                     # R8c3: the room without U's negative kerning
    h = horn_fit(U.body, cap, True, reach, reach0)
    n = 0
    for ch, g in CAPS.items():
        d = unicodedata.normalize('NFD', ch)
        if len(ch) != 1 or d[0] != 'U' or HORN not in d[1:]:
            continue
        rest = [op for _, ops in g.parts[1:] for op in ops]
        g.parts[0] = ('base', list(U.ops) + h)
        g.ops = list(U.ops) + h + rest
        g.lsb, g.rsb = U.lsb, U.rsb
        n += 1
    return reach, n
