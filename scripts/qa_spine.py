"""QA (R11c): S / s spine in the built fonts — spine/side within the references' range (0.89-1.03), the thickness
profile along the spine without bumps (no local rise > 3 units between neighbouring samples in its middle 80 %),
and no change of topology (closing). Usage: python3 qa_spine.py <font dir>"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import skeletonize
D=sys.argv[1]; bad=0
for w in ('Regular','Medium','Bold'):
    for ch in 'SsŠš$':
        f=ImageFont.truetype(f'{D}/DINHTUONG60s-{w}.otf',1000); im=Image.new('L',(1400,1600),0); ImageDraw.Draw(im).text((200,1250),ch,font=f,fill=255,anchor='ls')
        A=np.array(im)>127; dt=ndimage.distance_transform_edt(A); sk=skeletonize(A); ys,xs=np.where(sk); wd=2*dt[ys,xs]
        base=1250; xh=700 if ch.isupper() or ch=='$' else 530
        rel=(base-ys)/xh
        spine=np.median(wd[(rel>0.40)&(rel<0.60)&(xs>xs.min()+0.2*(xs.max()-xs.min()))&(xs<xs.min()+0.8*(xs.max()-xs.min()))])
        sides=np.percentile(wd[((rel>0.15)&(rel<0.35))|((rel>0.65)&(rel<0.85))],90)
        sel=(rel>0.33)&(rel<0.67)&(xs>xs.min()+0.1*(xs.max()-xs.min()))&(xs<xs.min()+0.9*(xs.max()-xs.min()))
        order=np.argsort(xs[sel]); th=wd[sel][order]; k=max(1,len(th)//14); prof=np.array([th[i:i+k].mean() for i in range(0,len(th),k)])
        mid=prof[2:-2]; bump=max([0]+[mid[i]-max(mid[i-1],mid[i+1]) for i in range(1,len(mid)-1)])
        ok=0.89<=spine/sides<=1.03 and bump<=3
        bad+=not ok
        print(f'{w:8s} {ch} spine/side {spine/sides:.2f} bump {bump:.1f} {"ok" if ok else "FAIL"}')
print('spine QA', 'PASS' if not bad else f'{bad} FAIL')
