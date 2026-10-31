"""Write spine_data.json: the R11b spine of S (concept_v1.Build.g_S) and s (lc96f.LF.g_s) for each weight, read by
s_spine_fix.py (VF4-S). Run from sources/dinhtuong after the generators (LC_OPT=f)."""
import os, sys, json, subprocess
if len(sys.argv) > 1 and sys.argv[1] == '--one':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import concept_v1 as CV
    rec = []
    orig = CV.s_spine
    def spy(W, T, ov, sx, sy, sm, ti, G=None, k=None):
        path, yu, yl = orig(W, T, ov, sx, sy, sm, ti, G, k)
        top = [path[0][1:3], path[1][1:3], path[1][3:5], path[1][5:7]]
        bot = [path[3][5:7], path[3][3:5], path[3][1:3], path[2][1:3]]
        rec.append(dict(args=[W, T, ov, sx, sy, sm, ti], k=k, top=top, bot=bot))
        return path, yu, yl
    CV.s_spine = spy
    import lc96f
    w = os.environ['A2_WEIGHT']
    CV.Build(w).g_S(); lc96f.LF(w).g_s()
    print(json.dumps({'S': rec[0], 's': rec[1]}))
else:
    out = {}
    for w in ('regular', 'medium', 'bold'):
        env = dict(os.environ, LC_OPT='f', A2_WEIGHT=w)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), '--one'], env=env, capture_output=True, text=True,
                           cwd=os.path.dirname(os.path.abspath(__file__)), check=True)
        out[w.capitalize()] = json.loads(r.stdout.strip().splitlines()[-1])
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'spine_data.json', 'w'), indent=1)
    print('spine data:', ', '.join(out))
