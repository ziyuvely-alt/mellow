#!/usr/bin/env python3
"""BBIA v267 batch inspect 3 MINI families, isolate packaging evidence before source-photo sales design.
Avoid repeating v266 or touching any published JPGs.
"""
import io,json,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
OUT=Path('/tmp/bbia-v267');OUT.mkdir(parents=True,exist_ok=True)
IDS=['1000000163','1000000186','1000000209']
master={str(f['product_id']):f for f in json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf-8'))['families']}
jobs=[(sku,i,u) for sku in IDS for i,u in enumerate([master[sku]['official_photo_url']]+master[sku].get('detail_references',[])[:2])]
def fetch(job):
 sku,i,u=job
 info={'goodsNo':sku,'source_index':i,'source_url':u,'kind':'HERO' if i==0 else 'DETAIL'}
 try:
  with urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=23) as stream:
   blob=stream.read(12_000_000)
  im=Image.open(io.BytesIO(blob));im.load()
  info.update(status='SOURCE_DOWNLOADED',dimensions=[im.width,im.height],sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob))
  return info,im.convert('RGB')
 except Exception as e:
  info.update(status='HOLD_SOURCE_FAILED',error=str(e)[:170]);return info,None
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:result=list(pool.map(fetch,jobs))
contact=Image.new('RGB',(1620,1410),'#f7f6f5');draw=ImageDraw.Draw(contact)
draw.text((15,12),'BBIA v267 - 3 MINI FAMILIES | 9 REAL SOURCE PHOTOS | IDENTITY REVIEW',fill='#222222')
for ri,sku in enumerate(IDS):
 y=42+ri*450
 draw.text((15,y),sku+' '+master[sku]['family'],fill='#292929')
 for j,(d,im) in enumerate([q for q in result if q[0]['goodsNo']==sku]):
  x=10+j*540
  if im is None:
   draw.text((x,y+35),'SOURCE HOLD',fill='#a22');continue
  small=im.copy();small.thumbnail((235,345))
  contact.paste(small,(x,y+38))
  top=im.crop((0,0,im.width,min(im.height,800)))
  top.thumbnail((250,345))
  contact.paste(top,(x+260,y+38))
  draw.text((x,y+390),f'{d["kind"]} {im.width} x {im.height}',fill='#555')
contact.save(OUT/'BBIA_v267_THREE_MINI_PRODUCT_SOURCE_CONTACT.jpg',quality=90)
report={'checkpoint':'v267','parent':'v266','families':IDS,'sources_requested':len(jobs),
 'downloads_ok':sum(q[0]['status']=='SOURCE_DOWNLOADED' for q in result),
 'sources':[q[0] for q in result],
 'mini_vs_regular_packaging':'HOLD_VISUAL_VERIFICATION','new_sale_jpg':0,
 'preexisting_public_assets_modified':False,'verified_55_urls_modified':False}
(OUT/'BBIA_v267_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('V267_MINI_BATCH',json.dumps({'families':3,'requested':len(jobs),'success':report['downloads_ok']}))
