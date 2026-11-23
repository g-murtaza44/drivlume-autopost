"""Drivlume batch builder.
Usage:  python3 builder/build.py batch.json            -> builds + writes posts/NNN_key/
        python3 builder/build.py batch.json --preview  -> builds only, writes builder/out/grid.jpg (no posts)
batch.json = list of items:
 {"key":"gtr","photo":"https://images.unsplash.com/photo-...","author":"Martin Katler",
  "num":"48,000","text":"In Aug 2025 Nissan built the **last R35 GT-R** after **18 years**.",
  "body":"Hook line.\\n\\nFact paragraph.\\n\\nQuestion?","pictured":"Nissan GT-R R35","source":"Nissan, Aug 2025",
  "tags":"jdm","mood":"phonk",
  optional: "front":true (number over car, for close-ups), "dim":0.6, "overlap":140, "oy":0,
            "plates":[{"quad":[[x,y],[x,y],[x,y],[x,y]],"dark":false}]   (full-res coords, TL,TR,BR,BL; photo downloaded at w=2160)
 }
"""
import json,os,sys,re,shutil,subprocess
from concurrent.futures import ProcessPoolExecutor
B=os.path.dirname(os.path.abspath(__file__));R=os.path.dirname(B);sys.path.insert(0,B)
OUT=os.path.join(B,'out')
T={'sup':'#jdm #toyota #supra #2jz #carsofinstagram #carfacts #cartok #automotive #drivlume',
'jdm':'#jdm #jdmlegends #japanesecars #carsofinstagram #carfacts #classiccars #cartok #automotive #drivlume',
'it':'#supercar #italiancars #carsofinstagram #carfacts #exoticcars #cartok #automotive #carnews #drivlume',
'de':'#germancars #carsofinstagram #carfacts #performancecars #cartok #automotive #carnews #carlifestyle #drivlume',
'lux':'#luxurycars #carsofinstagram #carfacts #britishcars #cartok #automotive #carnews #carlifestyle #drivlume',
'us':'#americancars #musclecar #carsofinstagram #carfacts #supercar #cartok #automotive #carnews #drivlume',
'ev':'#electriccars #ev #evnews #carsofinstagram #carfacts #cartok #automotive #carnews #drivlume',
'hyp':'#hypercar #carsofinstagram #carfacts #supercar #topspeed #cartok #automotive #carnews #drivlume',
'cn':'#chinesecars #ev #byd #carsofinstagram #carfacts #cartok #automotive #carnews #drivlume'}
def hl(t): return re.sub(r'\*\*(.+?)\*\*',r'<span class="hl2">\1</span>',t)
def fetch(it):
    from PIL import Image
    k=it['key'];d=os.path.join(OUT,k);os.makedirs(d,exist_ok=True);f=os.path.join(d,'orig.jpg')
    for _ in range(3):
        subprocess.run(['curl','-s','--max-time','120','-o',f,it['photo'].split('?')[0]+'?w=2160&q=90&fm=jpg'])
        try: Image.open(f).verify();break
        except Exception: pass
    return k
def cutall(items):
    from rembg import remove,new_session
    from PIL import Image
    s=new_session('u2net')
    for it in items:
        d=os.path.join(OUT,it['key']);im=Image.open(d+'/orig.jpg').convert('RGB')
        sm=im.resize((1080,round(im.height*1080/im.width)))
        remove(sm,session=s,post_process_mask=True).save(d+'/cut.png')
def prep(it):
    from PIL import Image;from plates_lib import plate
    d=os.path.join(OUT,it['key']);im=Image.open(d+'/orig.jpg').convert('RGB')
    for p in it.get('plates',[]):
        L,D=(200,200,195),(22,22,22);im=plate(im,p['quad'],D if p.get('dark') else L,L if p.get('dark') else D)
    im.save(d+'/photo.jpg',quality=95)
def one(it):
    from mkp import build
    d=os.path.join(OUT,it['key']);job=dict(k='b_'+it['key'],photo=d+'/photo.jpg',cut=d+'/cut.png',num=it['num'],text=hl(it['text']))
    for o in('front','dim','overlap','oy','fs','tag'):
        if o in it: job[o]=it[o]
    build(job,d);return it['key']
def main():
    items=json.load(open(sys.argv[1]));prev='--preview' in sys.argv
    with ProcessPoolExecutor(6) as ex: list(ex.map(fetch,items))
    cutall(items)
    for it in items: prep(it)
    with ProcessPoolExecutor(4) as ex: list(ex.map(one,items))
    dirs=[os.path.join(OUT,it['key']) for it in items]
    subprocess.run(['python3',os.path.join(B,'shot.py')]+dirs,check=True)
    for d in dirs: subprocess.run(['bash',os.path.join(B,'vid.sh'),d],check=True)
    from PIL import Image,ImageDraw
    tw,th=216,384;cols=min(9,len(items));rows=(len(items)+cols-1)//cols;S=Image.new('RGB',(tw*cols,th*rows),'white')
    for i,d in enumerate(dirs):
        S.paste(Image.open(d+'/post.png').convert('RGB').resize((tw,th)),((i%cols)*tw,(i//cols)*th));ImageDraw.Draw(S).text(((i%cols)*tw+4,(i//cols)*th+4),items[i]['key'],fill='yellow')
    S.save(os.path.join(OUT,'grid.jpg'),quality=85);print('grid:',os.path.join(OUT,'grid.jpg'))
    if prev: return
    P=os.path.join(R,'posts');n=max([int(x[:3]) for x in os.listdir(P) if x[:3].isdigit()]+[0])
    for it in items:
        n+=1;o=os.path.join(P,f"{n:03d}_{it['key']}");os.makedirs(o,exist_ok=True)
        pr=' (plate replaced)' if it.get('plates') else ''
        cap=f"{it['body']}\n\nPictured: {it['pictured']}.\nSource: {it['source']}.\nPhoto: {it['author']} / Unsplash{pr}\n\n{T.get(it['tags'],it['tags'])}"
        open(o+'/caption.txt','w').write(cap);open(o+'/mood.txt','w').write(it.get('mood','phonk'))
        shutil.copy(os.path.join(OUT,it['key'],'reel.mp4'),o+'/reel.mp4');print('queued',o)
    with open(os.path.join(B,'used.txt'),'a') as u:
        for it in items: u.write(f"{it['key']}\t{it['photo'].split('?')[0]}\t{re.sub(r'[*]','',it['text'])}\n")
if __name__=='__main__': main()
