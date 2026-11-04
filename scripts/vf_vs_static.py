"""Check that the variable font at wght 400 / 500 / 700 draws exactly like the static Regular / Medium / Bold:
every character (HarfBuzz, shaped): advance, outline area (<= 0.5 %) and bbox (<= 2 u); kerning on ~11 800 pairs."""
import uharfbuzz as hb, unicodedata, itertools, sys
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VF=os.path.join(ROOT,'fonts/variable/DinhTuong[wght].ttf'); ST=os.path.join(ROOT,'fonts/ttf/DinhTuong-%s.ttf')
def mk(path,var=None):
    f=hb.Font(hb.Face(open(path,'rb').read()))
    if var: f.set_variations(var)
    return f
class P:   # hb draw -> fontTools pens
    def __init__(s,*pens): s.p=pens
    def moveTo(s,pt): [x.moveTo(pt) for x in s.p]
    def lineTo(s,pt): [x.lineTo(pt) for x in s.p]
    def qCurveTo(s,*a): [x.qCurveTo(*a) for x in s.p]
    def curveTo(s,*a): [x.curveTo(*a) for x in s.p]
    def closePath(s): [x.closePath() for x in s.p]
def geom(font,gid):
    a=AreaPen(); b=BoundsPen(None); font.draw_glyph_with_pen(gid,P(a,b)); return abs(a.value), b.bounds
def shape(font,t):
    buf=hb.Buffer(); buf.add_str(t); buf.guess_segment_properties(); hb.shape(font,buf,{'kern':True})
    return buf.glyph_infos, buf.glyph_positions
cm=TTFont(ST%'Regular').getBestCmap()
chars=[chr(u) for u in sorted(cm) if unicodedata.category(chr(u))[0] in 'LNPSM']
letters=[c for c in chars if unicodedata.category(c)[0]=='L']
vn='aăâbcdđeêghiklmnoôơpqrstuưvxyAĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXY'
pairs=[a+b for a in vn for b in vn]+[a+b for a in letters for b in 'AVTYoaenvy.,']+[a+b for a in 'AVTYoaenvyLFP' for b in letters]
for name,wv in [('Regular',400),('Medium',500),('Bold',700)]:
    st=mk(ST%name); vf=mk(VF,{'wght':wv})
    adv=geo=0; worst_a=worst_b=0; wa=wb=''; bad=[]
    for c in chars:
        (gi_s,gp_s),(gi_v,gp_v)=shape(st,c),shape(vf,c)
        if len(gi_s)!=len(gi_v): bad.append(c); continue
        for i_s,p_s,i_v,p_v in zip(gi_s,gp_s,gi_v,gp_v):
            if p_s.x_advance!=p_v.x_advance: adv+=1; bad.append(c)
            A1,B1=geom(st,i_s.codepoint); A2,B2=geom(vf,i_v.codepoint)
            if B1 is None and B2 is None: continue
            da=abs(A1-A2)/max(A1,1)*100; db=max(abs(x-y) for x,y in zip(B1,B2))
            if da>worst_a: worst_a,wa=da,c
            if db>worst_b: worst_b,wb=db,c
            if da>0.5 or db>2: geo+=1; bad.append(c)
    kd=0; kx=[]
    for t in pairs:
        (gi_s,gp_s),(gi_v,gp_v)=shape(st,t),shape(vf,t)
        a=[p.x_advance+p.x_offset for p in gp_s]; b=[p.x_advance+p.x_offset for p in gp_v]
        if a!=b: kd+=1; kx.append((t,a,b))
    print(f'{name} (VF wght {wv}): {len(chars)} ký tự · advance khác {adv} · hình khác >0,5% / >2u: {geo} (lệch lớn nhất: diện tích {worst_a:.2f}% [{wa}], khung {worst_b:.1f}u [{wb}]) · {len(pairs)} cặp kerning, khác {kd} {kx[:5]} · ký tự lỗi {sorted(set(bad))[:20]}')
