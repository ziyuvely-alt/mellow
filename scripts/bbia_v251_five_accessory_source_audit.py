import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageDraw
ids=['1000000185','1000000126','1000000200','1000000127','1000000142']
master={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
jobs=[(sku,i,url) for sku in ids for i,url in enumerate(master[sku].get('detail_references',[])[:2])]
def fetch(job):
    sku,i,url=job
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as stream:
            data=stream.read(12000000)
        im=Image.open(io.BytesIO(data));im.load()
        return dict(goodsNo=sku,index=i,uri=url,size=list(im.size),hash=hashlib.sha256(data).hexdigest(),status='OK'),im.convert('RGB')
    except Exception as e:
        return dict(goodsNo=sku,index=i,status='HOLD',reason=str(e)[:160]),None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    rows=list(pool.map(fetch,jobs))
out=Path('/tmp/bbia-v251');out.mkdir(parents=True,exist_ok=True)
board=Image.new('RGB',(1440,1660),'#f8f8f8');pen=ImageDraw.Draw(board)
pen.text((12,12),'BBIA v251 | FIVE UNUSED PRODUCT FAMILIES | SOURCE CONTACT ONLY',fill='black')
for k,(rec,photo) in enumerate(rows):
    row=k//2;col=k%2;x=10+col*720;y=50+row*320
    pen.text((x,y),rec['goodsNo']+' source '+str(col+1),fill='black')
    if photo:
        small=photo.copy();small.thumbnail((310,270))
        board.paste(small,(x,y+22))
        top=photo.crop((0,0,photo.width,min(photo.height,700)))
        top.thumbnail((320,270))
        board.paste(top,(x+330,y+22))
        pen.text((x,y+293),str(photo.size),fill='black')
board.save(out/'BBIA_v251_FIVE_ACCESSORIES_CONTACT.jpg',quality=87)
manifest=dict(checkpoint='v251',parent='v250',families=ids,download_ok=sum(a['status']=='OK' for a,b in rows),records=[a for a,b in rows],new_sale_images=0,source_images_modified=False)
(out/'BBIA_v251_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V251_RESULT',json.dumps(dict(families=len(ids),sources=len(jobs),ok=manifest['download_ok'])))
