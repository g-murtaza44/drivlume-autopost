import cv2,numpy as np,os
from PIL import Image,ImageDraw,ImageFont
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Anton-Regular.ttf')
def plate(img,quad,bgc,fg,text='DRIVLUME'):
    q=np.float32(quad);w=np.linalg.norm(q[1]-q[0]);h=np.linalg.norm(q[3]-q[0]);W=440;H=max(60,int(W*h/w))
    pl=Image.new('RGB',(W,H),bgc);d=ImageDraw.Draw(pl);fs=int(min(H*0.72,78));f=ImageFont.truetype(F,fs)
    bb=d.textbbox((0,0),text,font=f);d.text(((W-bb[2]-bb[0])/2,(H-bb[3]-bb[1])/2-bb[1]/2),text,font=f,fill=fg)
    d.rectangle([1,1,W-2,H-2],outline=tuple(int(c*0.6) for c in bgc),width=3)
    a=np.array(img);M=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),q)
    pw=cv2.warpPerspective(np.array(pl),M,(img.width,img.height),flags=cv2.INTER_CUBIC);pw=cv2.GaussianBlur(pw,(3,3),0)
    mk=cv2.warpPerspective(np.full((H,W),255,np.uint8),M,(img.width,img.height))
    a[mk>128]=pw[mk>128];return Image.fromarray(a)
