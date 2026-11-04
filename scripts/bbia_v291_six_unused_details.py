#!/usr/bin/env python3
"""BBIA v291: collect only unused manufacturer slots (5,6) for three active incomplete families.
Preserve original bytes; unsupported URLs are held individually.
"""
import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
TARGET={"1000000221":[5,6],"1000000178":[5,6],"1000000136":[5,6]}
MASTER={str(a["product_id"]):a for a in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
OUT=Path('/tmp/bbia-v291');OUT.mkdir(parents=True,exist_ok=True)
tasks=[(sku,idx,MASTER[sku]['detail_references'][idx]) for sku,indices in TARGET.items() for idx in indices]
def fetch(task):
 sku,idx,url=task;d={'goodsNo':sku,'detail_index':idx,'url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as stream:raw=stream.read(12_000_000)
  im=Image.open(io.BytesIO(raw));im.load()
  file=f'BBIA_{sku}_OFFICIAL_UNUSED_{idx}_v291.jpg'
  (OUT/file).write_bytes(raw)
  d.update(status='SOURCE_SAVED',file=file,dimensions=list(im.size),sha256=hashlib.sha256(raw).hexdigest())
  return d,im.convert('RGB')
 except Exception as e:
  d.update(status='HOLD_DOWNLOAD',error=f'{type(e).__name__}: {str(e)[:135]}')
  return d,None
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:res=list(pool.map(fetch,tasks))
contact=Image.new('RGB',(1680,1630),'#f7f6f5');d=ImageDraw.Draw(contact)
d.text((14,12),'BBIA v291 | 3 FAMILIES / 6 UNUSED OFFICIAL DETAIL SOURCE IMAGES',fill='#222222')
for row,sku in enumerate(TARGET):
 y=48+row*525;d.text((14,y),sku+' '+MASTER[sku]['family'],fill='#222222')
 for col,(data,img) in enumerate([x for x in res if x[0]['goodsNo']==sku]):
  x=col*840+6
  if img is None:
   d.text((x,y+60),'HOLD SOURCE',fill='red');continue
  full=img.copy();full.thumbnail((300,420),Image.Resampling.LANCZOS)
  contact.paste(full,(x+10,y+32))
  region=img.crop((0,min(int(img.height*.3),max(0,img.height-900)),img.width,min(img.height,min(int(img.height*.3),max(0,img.height-900))+900)))
  region.thumbnail((470,420),Image.Resampling.LANCZOS)
  contact.paste(region,(x+325,y+32))
  d.text((x+12,y+465),f"DETAIL {data['detail_index']} / {img.width}x{img.height}",fill='#444444')
contact.save(OUT/'BBIA_v291_SIX_UNUSED_DETAIL_CONTACT.jpg',quality=89)
manifest={'checkpoint':'v291','parent':'v290','source_count':len(tasks),'saved':sum(x['status']=='SOURCE_SAVED' for x,_ in res),'sources':[x for x,_ in res],'new_sales_approved':0,'published_changed':False}
(OUT/'BBIA_v291_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V291_RESULT',json.dumps({'saved':manifest['saved'],'requested':len(tasks)}))
