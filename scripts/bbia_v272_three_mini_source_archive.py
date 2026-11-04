#!/usr/bin/env python3
"""v272: obtain three already verified high-resolution mini detail photos as original immutable bytes.
These sources were URL-verified in v270 but not retained as original artifact; no hero re-creation.
"""
import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
ids=['1000000187','1000000120','1000000208']
master={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
out=Path('/tmp/bbia-v272');out.mkdir(exist_ok=True,parents=True)
def dl(sku):
 url=master[sku]['detail_references'][0]
 info={'goodsNo':sku,'source_url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=22) as r:raw=r.read(12000000)
  img=Image.open(io.BytesIO(raw));img.load()
  path=out/f'BBIA_{sku}_DETAIL_SOURCE_v272.jpg';path.write_bytes(raw)
  info.update(status='SAVED_RAW_SOURCE',filename=path.name,dimensions=list(img.size),sha256=hashlib.sha256(raw).hexdigest())
  return info,img.convert('RGB')
 except Exception as e:return {**info,'status':'HOLD_DOWNLOAD','reason':str(e)[:150]},None
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:received=list(pool.map(dl,ids))
sheet=Image.new('RGB',(1800,900),'#f8f8f8');d=ImageDraw.Draw(sheet)
d.text((12,12),'BBIA v272 3 ORIGINAL MINI DETAIL SOURCES - NO PUBLISHED FILES ALTERED',fill='#222')
for n,(r,img) in enumerate(received):
 x=n*600
 d.text((x+12,50),r['goodsNo']+' '+r['status'],fill='#222')
 if img is None:continue
 img1=img.copy();img1.thumbnail((275,730));sheet.paste(img1,(x+8,78))
 half=min(img.height,1300);img2=img.crop((0,0,img.width,half));img2.thumbnail((290,700))
 sheet.paste(img2,(x+305,85))
sheet.save(out/'BBIA_v272_THREE_ORIGINAL_SOURCE_CONTACT.jpg',quality=88)
(out/'BBIA_v272_MANIFEST.json').write_text(json.dumps({'checkpoint':'v272','parent':'v271','records':[q[0] for q in received],'new_sale_jpg':0,'published_modified':False},ensure_ascii=False,indent=2))
print('V272_ORIGINALS',json.dumps({'ok':sum(r['status']=='SAVED_RAW_SOURCE' for r,_ in received)}))
