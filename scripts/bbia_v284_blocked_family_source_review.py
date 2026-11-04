#!/usr/bin/env python3
"""v284: new photo evidence for held families, only source slots not previously selected."""
import json,hashlib,io,concurrent.futures
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageDraw
OUT=Path('/tmp/bbia-v284');OUT.mkdir(parents=True,exist_ok=True)
SLOTS={'200':[4,5,6],'1000000135':[3],'1000000124':[5,6],'1000000179':[5,6]}
master={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf-8'))['families']}
jobs=[(sku,i,master[sku]['detail_references'][i]) for sku,slots in SLOTS.items() for i in slots]
def fetch(task):
 sku,i,url=task; rec={'goodsNo':sku,'detail_index':i,'url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as r: b=r.read(12000000)
  im=Image.open(io.BytesIO(b));im.load()
  name=f'BBIA_{sku}_DETAIL_SOURCE_{i}_v284.jpg';(OUT/name).write_bytes(b)
  rec.update(status='SOURCE_SAVED',file=name,dimensions=[im.width,im.height],sha256=hashlib.sha256(b).hexdigest())
  return rec,im.convert('RGB')
 except Exception as ex:
  rec.update(status='HOLD_FETCH',error=str(ex)[:140]);return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: result=list(p.map(fetch,jobs))
board=Image.new('RGB',(1940,4*490+70),'#f7f7f7');d=ImageDraw.Draw(board)
d.text((15,12),'BBIA v284 - 4 HELD FAMILIES / UNUSED ORIGINAL DETAIL SOURCES / READ ONLY',fill='#202020')
for row,sku in enumerate(SLOTS):
 y=43+row*490;d.text((15,y),sku+' '+master[sku]['family'],fill='#222222')
 entries=[r for r in result if r[0]['goodsNo']==sku]
 for col,(rec,im) in enumerate(entries):
  x=col*640+8
  if im is None:
   d.text((x,y+50),'SOURCE HOLD',fill='#a22');continue
  thumb=im.copy();thumb.thumbnail((275,350));board.paste(thumb,(x,y+32))
  mid=im.crop((0,min(int(im.height*.35),max(0,im.height-850)),im.width,min(im.height,min(int(im.height*.35),max(0,im.height-850))+850)))
  mid.thumbnail((305,350));board.paste(mid,(x+292,y+32))
  d.text((x+10,y+415),f'SOURCE {rec["detail_index"]}: {im.width}x{im.height}',fill='#555')
board.save(OUT/'BBIA_v284_EIGHT_NEW_SOURCE_CONTACT.jpg',quality=90)
report={'checkpoint':'v284','parent':'v283','source_attempts':len(jobs),'source_success':sum(r['status']=='SOURCE_SAVED' for r,_ in result),'families':list(SLOTS),'records':[r for r,_ in result],'sales_approved':0,'existing_jpg_modified':False}
(OUT/'BBIA_v284_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V284_RESULT',json.dumps({'attempted':len(jobs),'success':report['source_success']}))
