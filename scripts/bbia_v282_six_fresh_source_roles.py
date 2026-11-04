#!/usr/bin/env python3
"""v282 batch untouched later detail slots for 3 families lacking clean secondary roles.
No old source refetch or sale-image writes. One source call per slot.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
import io,json,hashlib,concurrent.futures
TARGETS={"1000000227":[5,6],"1000000247":[4,5],"1000000244":[3,4]}
MASTER={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
OUT=Path('/tmp/bbia-v282');OUT.mkdir(parents=True,exist_ok=True)
jobs=[(sku,i,MASTER[sku]['detail_references'][i]) for sku,idxs in TARGETS.items() for i in idxs]
def fetch(job):
 sku,i,url=job; d={"goodsNo":sku,"source_index":i,"url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as r: raw=r.read(12_000_000)
  img=Image.open(io.BytesIO(raw));img.load()
  fn=f'BBIA_{sku}_DETAIL_SOURCE_{i}_v282.jpg'
  (OUT/fn).write_bytes(raw)
  d.update(status="ORIGINAL_SAVED",dimensions=[img.width,img.height],sha256=hashlib.sha256(raw).hexdigest(),filename=fn)
  return d,img.convert('RGB')
 except Exception as e:
  d.update(status="HOLD_FETCH",error=f'{type(e).__name__}: {str(e)[:120]}');return d,None
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:result=list(pool.map(fetch,jobs))
board=Image.new('RGB',(1740,1600),'#f8f7f5');dr=ImageDraw.Draw(board)
dr.text((15,12),'BBIA v282 | THREE INCOMPLETE FAMILIES | SIX NEVER-USED DETAIL SOURCE SLOTS',fill='#222222')
for row,sku in enumerate(TARGETS):
 y=46+row*505
 dr.text((15,y),sku+' '+MASTER[sku]['family'],fill='#222222')
 for col,(rec,img) in enumerate([r for r in result if r[0]['goodsNo']==sku]):
  x=10+col*870
  if img is None:dr.text((x,y+45),"HOLD",fill='#d33');continue
  small=img.copy();small.thumbnail((320,395),Image.Resampling.LANCZOS)
  board.paste(small,(x,y+35))
  crop=img.crop((0,int(img.height*.15),img.width,min(img.height,int(img.height*.15)+1000)))
  crop.thumbnail((420,395),Image.Resampling.LANCZOS)
  board.paste(crop,(x+370,y+35))
  dr.text((x+10,y+447),f'DETAIL {rec["source_index"]} {img.width}x{img.height}',fill='#444444')
board.save(OUT/'BBIA_v282_SIX_OTHER_DETAIL_SOURCE_CONTACT.jpg',quality=88)
manifest={"checkpoint":"v282","parent":"v281","source_attempts":len(jobs),"downloaded":sum(x["status"]=="ORIGINAL_SAVED" for x,_ in result),"families":list(TARGETS.keys()),"records":[x for x,_ in result],"sale_approved":0,"prior_images_modified":False}
(OUT/'BBIA_v282_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V282_SOURCES',json.dumps({'attempted':len(jobs),'downloaded':manifest['downloaded']}))
