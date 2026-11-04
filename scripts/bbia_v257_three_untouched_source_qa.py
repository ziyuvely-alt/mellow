import concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
IDS=['1000000118','1000000128','1000000179']
m={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf-8'))['families']}
tasks=[(sku,i,u) for sku in IDS for i,u in enumerate(m[sku].get('detail_references',[])[:3])]
def fetch(t):
 sku,i,url=t
 rec=dict(goodsNo=sku,index=i,url=url)
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:
   b=r.read(12000000)
  image=Image.open(io.BytesIO(b));image.load()
  rec.update(status='OK',size=list(image.size),source_sha256=hashlib.sha256(b).hexdigest())
  return rec,image.convert('RGB')
 except Exception as e:
  rec.update(status='HOLD',error=str(e)[:130])
  return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 rows=list(pool.map(fetch,tasks))
out=Path('/tmp/bbia-v257');out.mkdir(parents=True,exist_ok=True)
board=Image.new('RGB',(1740,3*540+60),'#f7f7f7')
draw=ImageDraw.Draw(board)
draw.text((15,12),'BBIA v257 | THREE UNTOUCHED FAMILIES / REAL DETAIL SOURCE QA ONLY',fill='#222222')
for ri,sku in enumerate(IDS):
 y=45+ri*540
 draw.text((16,y),f"{sku} {m[sku]['family']}",fill='#222222')
 for col,(rec,img) in enumerate([r for r in rows if r[0]['goodsNo']==sku]):
  x=10+col*580
  if img is None:
   draw.text((x,y+80),'FETCH HOLD',fill='red');continue
  full=img.copy();full.thumbnail((230,380))
  board.paste(full,(x,y+35))
  for i in range(2):
   top=round(img.height*i/2)
   crop=img.crop((0,top,img.width,min(img.height,top+min(750,img.height//2))))
   crop.thumbnail((150,380))
   board.paste(crop,(x+245+i*160,y+35))
  draw.text((x,y+435),f"reference {col+1} {img.width}x{img.height}",fill='#333333')
board.save(out/'BBIA_v257_THREE_FAMILY_SOURCE_CONTACT.jpg',quality=88)
report=dict(checkpoint='v257',source_families=IDS,requested=len(tasks),downloaded=sum(a['status']=='OK' for a,b in rows),
            source_rows=[a for a,b in rows],published_assets_modified=False,new_sales_approved=0,
            caution='Shared compact images are not refill packshot evidence; exact photos and variants need QA.')
(out/'BBIA_v257_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V257_SOURCE',json.dumps(dict(families=3,requested=len(tasks),downloaded=report['downloaded'])))
