#!/usr/bin/env python3
"""v289: 7 unused official photo sources across 3 separate families, per-item error isolation."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib,io,concurrent.futures
from PIL import Image,ImageDraw
SLOTS={"1000000251":[0,1,2,3],"1000000166":[1],"1000000142":[2,3]}
OUT=Path('/tmp/bbia-v289');OUT.mkdir(exist_ok=True,parents=True)
master={str(r["product_id"]):r for r in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
jobs=[(sku,i,master[sku]["detail_references"][i]) for sku,items in SLOTS.items() for i in items]
def fetch(job):
 sku,i,url=job;rec={"goodsNo":sku,"index":i,"url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as f:body=f.read(12000000)
  img=Image.open(io.BytesIO(body));img.load()
  name=f'BBIA_{sku}_ORIGINAL_SOURCE_{i}_v289.jpg';(OUT/name).write_bytes(body)
  rec.update(status="ORIGINAL_PRESERVED",file=name,dimensions=[img.width,img.height],sha256=hashlib.sha256(body).hexdigest())
  return rec,img.convert('RGB')
 except Exception as exc:
  rec.update(status="HOLD",error=str(exc)[:145]);return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:results=list(pool.map(fetch,jobs))
board=Image.new('RGB',(1920,1560),'#f8f7f6');p=ImageDraw.Draw(board)
p.text((15,13),'BBIA v289 | 7 UNUSED ORIGINALS | 3 PRODUCT FAMILIES | NO AUTO-APPROVAL',fill='#222222')
for n,sku in enumerate(SLOTS):
 y=40+n*495;p.text((10,y),sku+" "+master[sku]["family"],fill='#202020')
 for col,(rec,im) in enumerate([v for v in results if v[0]['goodsNo']==sku]):
  x=col*480+8
  if im is None:
   p.text((x,y+60),'SOURCE HOLD',fill='#bb1111');continue
  full=im.copy();full.thumbnail((200,380));board.paste(full,(x,y+32))
  mid=im.crop((0,min(int(im.height*.22),max(0,im.height-750)),im.width,min(im.height,min(int(im.height*.22),max(0,im.height-750))+750)))
  mid.thumbnail((230,380));board.paste(mid,(x+230,y+32))
  p.text((x,y+425),f"source {rec['index']} {im.width}x{im.height}",fill='#555555')
board.save(OUT/'BBIA_v289_SEVEN_REAL_SOURCE_CONTACT.jpg',quality=88)
report={"checkpoint":"v289","parent":"v288","requested":len(jobs),"preserved":sum(x['status']=='ORIGINAL_PRESERVED' for x,y in results),"source_rows":[x for x,y in results],"prior_jpg_modified":False,"sales_approved":0}
(OUT/'BBIA_v289_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V289_SOURCE_RESULT',json.dumps({'requested':len(jobs),'saved':report['preserved']}))
