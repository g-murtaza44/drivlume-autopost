import os
# Portrait, full-bleed, NO blur. Car cutout (Adobe) sits over the number.
import sys,os,subprocess,numpy as np
from PIL import Image,ImageFilter,ImageChops
W,H=2160,3840;COL=np.array((198,240,60),np.float32)
def build(job,out):
    src=Image.open(job['photo']).convert('RGB');cut=Image.open(job['cut']).convert('RGBA').resize(src.size)
    s=W/src.width;ph=round(src.height*s);oy=job.get('oy',0)
    sp=src.resize((W,ph),Image.LANCZOS);ca_=cut.split()[3].resize((W,ph),Image.LANCZOS)
    can=Image.new('RGB',(W,H),(6,6,6));can.paste(sp,(0,oy))
    if oy+ph<H:  # fade photo bottom into black (no blur)
        g=np.array(can).astype(np.float32);y0=oy+ph-500
        t=np.clip((np.arange(H)-y0)/500,0,1)[:,None,None];g=g*(1-t)+6*t;can=Image.fromarray(g.astype(np.uint8))
    al=Image.new('L',(W,H));al.paste(ca_,(0,oy));ca=np.array(al).astype(np.float32)/255
    rows=np.where((ca>0.5).sum(1)>40)[0];top=rows[0];cols=np.where(ca[top:top+120].sum(0)>5)[0];cx=int(cols.mean())
    k=job['k'];fs=job.get('fs',400 if len(job['num'])<7 else 320)
    open(f'/tmp/n_{k}.html','w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>*{{margin:0}}html,body{{background:transparent;width:1080px;height:1350px}}.a{{position:absolute;left:10px;top:20px;white-space:nowrap;color:#fff;font:400 {fs}px/1 "Anton";letter-spacing:6px}}</style></head><body><div class="a">{job["num"]}</div></body></html>')
    subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'render_t.py'),f'/tmp/n_{k}.html',f'/tmp/n_{k}.png'],check=True)
    gl=Image.open(f'/tmp/n_{k}.png').split()[3];gl=gl.crop(gl.getbbox())
    if gl.width>1480: gl=gl.resize((1480,round(gl.height*1480/gl.width)),Image.LANCZOS)
    cx=int(np.clip(cx,gl.width//2+200,2*(1080-240)-gl.width//2))
    ny=max(top+job.get('overlap',140)-gl.height,480)
    numc=Image.new('L',(W,H));numc.paste(gl,(int(cx-gl.width/2),ny));num=np.array(numc).astype(np.float32)/255
    b=np.array(can).astype(np.float32)
    halo=np.clip(np.array(numc.filter(ImageFilter.MaxFilter(61)).filter(ImageFilter.GaussianBlur(70))).astype(np.float32)/255*1.3,0,1)
    b=b*(1-job.get('dim',0.5)*halo[...,None])  # darken (no blur) behind number for readability
    ds=np.array(numc.filter(ImageFilter.GaussianBlur(30))).astype(np.float32)/255;b=b*(1-0.45*np.roll(ds,16,axis=0)[...,None])  # soft drop shadow only
    ys,_=np.nonzero(num>0.05);a0,a1=ys.min(),ys.max();t=np.clip((np.arange(H)-a0)/(a1-a0),0,1)[:,None,None]
    fill=np.broadcast_to(COL*(1-t)+COL*0.86*t,(H,W,3)).copy()
    shd=np.array(ImageChops.offset(Image.fromarray((ca*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)),0,-8)).astype(np.float32)/255
    if not job.get('front'): fill*=(1-0.5*shd)[...,None]
    aa=np.array(numc.filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)/255
    o=b*(1-aa[...,None])+fill*aa[...,None]
    img=Image.fromarray(o.clip(0,255).astype(np.uint8)).convert('RGBA')
    car=can.convert('RGBA');car.putalpha(al)
    if not job.get('front'): img.alpha_composite(car)
    os.makedirs(out,exist_ok=True);img.convert('RGB').save(f'{out}/scene.jpg',quality=94)
    t=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'tpl.html')).read();i0=t.index('<div class="abs txt">');i1=t.index('</div>',i0)
    t=t[:i0]+'<div class="abs txt">'+(f'<div class="tag">{job["tag"]}</div><br>' if job.get('tag') else '')+job['text']+t[i1:];t=t.replace('src="reel_scene.jpg"',f'src="file://{os.path.abspath(out)}/scene.jpg"')
    open(f'{out}/p.html','w').write(t)
