"""Kerning for one style (A2_WEIGHT / A2_ITALIC): optical autokern on the base letters,
then classes by base letter and a collision guard over every accented member of each class."""
import json, unicodedata, sys, time
import numpy as np
import family as FM
import kern

KCLASS_MAP = {'Đ': 'D', 'đ': 'd', 'Ð': 'D', 'Ø': 'O', 'ø': 'o', 'ı': 'i', 'æ': 'a', 'œ': 'o', 'Æ': 'A', 'Œ': 'O',
              'Ł': 'L', 'ł': 'l', 'Ħ': 'H', 'ħ': 'h', 'ẞ': 'B', 'ȷ': 'j'}   # GF Latin Core: stroked letters kern as their base (guard checks the strokes)
KCLASS_L_MAP = {'æ': 'e', 'œ': 'e', 'Æ': 'E', 'Œ': 'E'}   # F14: a ligature's RIGHT side is its last letter's
MIN_MARK_GAP = 36


HORN = '\u031b'


def kclassL(ch):
    """left-side class: a horned letter (ơ ư and their tones) kerns as itself, not as o/u,
    because the horn changes its right profile."""
    if ch in KCLASS_L_MAP:
        return KCLASS_L_MAP[ch]
    d = unicodedata.normalize('NFD', ch)
    if HORN in d[1:]:
        return unicodedata.normalize('NFC', d[0] + HORN)
    return kclass(ch)


def kclass(ch):
    if ch in KCLASS_MAP:
        return KCLASS_MAP[ch]
    d = unicodedata.normalize('NFD', ch)
    return d[0] if len(d) > 1 and d[0].isalpha() else ch


def run():
    t0 = time.time()
    G = FM.style_glyphs()
    U = [chr(i) for i in range(65, 91)]; L = [c for c in (chr(i) for i in range(97, 123)) if c in G]   # [] caps-only
    N = list('0123456789')
    ref = {(True, True): 'HH', (True, False): 'Hn', (False, False): 'nn', (False, True): 'nH'}
    if 'n' not in G:                     # caps-only: every pair is measured against HH
        ref = {key: 'HH' for key in ref}
    k = {}
    k.update(kern.autokern(G, U, U, ref))
    k.update(kern.autokern(G, U, L, ref))
    k.update(kern.autokern(G, L, L, ref))
    # R16 (28/10 02:18 'điều chỉnh kerning chữ và số cho phù hợp'): figures with figures, capitals and lowercase
    # (the lowercase build measures them as interactions against H / n, like the letters)
    k.update(kern.autokern(G, N, N, ref)); k.update(kern.autokern(G, U, N, ref)); k.update(kern.autokern(G, N, U, ref))
    if L:
        k.update(kern.autokern(G, N, L, ref)); k.update(kern.autokern(G, L, N, ref))
    HU, HL = ['Ơ', 'Ư'], [c for c in ['ơ', 'ư'] if c in G]
    k.update(kern.autokern(G, HU, U + L, ref)); k.update(kern.autokern(G, HL, L, ref))
    P_after = ['.', ',', '…', '’', '”', ':', ';', '!', '?', ')', ']', '}', '»', '›']
    P_before = ['‘', '“', '(', '[', '{', '«', '‹', '¿', '¡']
    k.update(kern.autokern(G, U + L + N + HU + HL, P_after, ref))
    k.update(kern.autokern(G, P_before, U + L + N, ref))
    k.update(kern.autokern(G, ['/'], U + N, ref)); k.update(kern.autokern(G, U + N, ['/'], ref))
    k0 = dict(k)
    for side, plist in (('after', P_after + ['/']), ('before', P_before + ['/'])):
        for p in plist:
            for x in U + L + N + HU + HL:
                key = x + p if side == 'after' else p + x
                if key not in k:
                    continue
                base = '0' if x.isdigit() else ('n' if x.islower() else 'H')
                refk = (base + p) if side == 'after' else (p + base)
                v = k0[key] - k0.get(refk, 0)
                if abs(v) >= 20:
                    k[key] = int(round(v / 5.0)) * 5
                else:
                    del k[key]
            for x in ('H', 'n', '0'):
                k.pop((x + p) if side == 'after' else (p + x), None)
    # K2 (28/10 11:17 'lưu ý lại kerning các chữ GA, GÂ'): an OPEN round (C G) never comes closer to the next
    # letter than the closed round O does. The mean-white measure counts the mouth of C / G as white between the
    # letters and tucks the next letter in until G's bar corner (C's lower lip) points into it: GA came to 42 units
    # of ink against OA's 63, CA 32. Inter sets GA at OA's closest approach (147 / 149 at 1000 px); Liberation,
    # DejaVu at ~0.8 of it. So: kern(Xb) is opened until the closest ink X|b (letters only, baseline..band top)
    # equals O|b's. Only ever opens a pair; |k| < 20 is dropped as everywhere.
    if 'O' in G:
        for a in ('C', 'G'):
            if a not in G:
                continue
            for b in U + L:
                y0, y1 = kern.band_for(a, b)
                g_o = kern.raw_gap(G['O'], G[b], y0, y1, k.get('O' + b, 0))
                kv = k.get(a + b, 0)
                g_a = kern.raw_gap(G[a], G[b], y0, y1, kv)
                if g_a < g_o - 2 and kv < 0:
                    kv = min(0, int(np.ceil((kv + g_o - g_a) / 5.0)) * 5)
                    if abs(kv) >= 20:
                        k[a + b] = kv
                    else:
                        k.pop(a + b, None)
    # classes: every glyph joins the class of its base letter
    members, membersL = {}, {}
    for ch in G:
        if ch in FM.COMBINING or len(ch) != 1:
            continue
        members.setdefault(kclass(ch), []).append(ch)
        membersL.setdefault(kclassL(ch), []).append(ch)
    exc = {}
    nchk = 0
    for pair, kv in k.items():
        a, b = pair[0], pair[1]
        if kv >= 0:
            continue
        g0 = kern.raw_gap(G[a], G[b], -400, 1240, kv)
        floor = min(MIN_MARK_GAP, g0) - 2
        for la in membersL.get(a, [a]):
            for rb in members.get(b, [b]):
                if la == a and rb == b:
                    continue
                nchk += 1
                gap = kern.raw_gap(G[la], G[rb], -400, 1240, kv)
                if gap < floor:
                    need = int(np.ceil((kv + floor + 2 - gap) / 5.0)) * 5
                    exc[la + rb] = min(0, need)
    # every realistic letter pair with a mark: guard even where no class kerning applies
    TONES = set('̣́̀̉̃')
    lat1 = set(chr(c) for c in range(0xC0, 0x100))
    mk = lambda c: set(unicodedata.normalize('NFD', c)[1:])
    letters = [c for c in G if len(c) == 1 and c.isalpha()]
    withm = set(c for c in letters if mk(c) or c in KCLASS_MAP)
    def kv_of(a, b):
        if a + b in exc: return exc[a + b]
        return k.get(kclassL(a) + kclass(b), 0)
    lefts = letters + P_before
    rights = letters + P_after + ['/']
    for a in lefts:
        for b in rights:
            if a not in withm and b not in withm: continue
            if not (a.isalpha() and b.isalpha()) and not (a in withm or b in withm): continue
            if b.isalpha() and a.isalpha() and b.isupper() and a.islower(): continue                    # 'aB' does not occur
            if (mk(a) & TONES) and (mk(b) & TONES) and not (a in lat1 and b in lat1): continue
            kv = kv_of(a, b)
            ba, bb = kclassL(a), kclass(b)
            ref_a = unicodedata.normalize('NFD', ba)[0] if HORN in unicodedata.normalize('NFD', ba) else ba   # v0.94: a horned letter keeps the air of its plain base (ơt >= ot)
            g0 = kern.raw_gap(G[ref_a], G[bb], -400, 1240, k.get(ref_a + bb, 0)) if ref_a in G and bb in G else 999
            floor = min(MIN_MARK_GAP, g0) - 2
            gap = kern.raw_gap(G[a], G[b], -400, 1240, kv)
            nchk += 1
            if gap < floor:
                exc[a + b] = min(160, int(np.ceil((kv + floor + 2 - gap) / 5.0)) * 5)
    out = {'pairs': k, 'exceptions': exc,
           'classesL': {c: m for c, m in membersL.items() if len(m) > 1},
           'classesR': {c: m for c, m in members.items() if len(m) > 1}}
    name = f"kern_{FM.WEIGHT}{'_it' if FM.ITALIC else ''}.json"
    json.dump(out, open(name, 'w'), ensure_ascii=False, indent=0)
    print(name, 'pairs', len(k), 'exceptions', len(exc), 'checked', nchk, 'sec', round(time.time() - t0))
    return out


if __name__ == '__main__':
    run()
