#!/usr/bin/env python3
"""Recover already verified 1000000118 palette details into a reusable immutable SOURCE_ONLY artifact."""
import json,io,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
out=Path('/tmp/bbia-v259');out.mkdir(parents=True,exist_ok=True)
data=json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf-8'))
row=next(x for x in data['families'] if str(x['product_id'])=='1000000118')
rows=[]
for i,url in enumerate(row['detail_references'][:3]):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=24) as r:
  blob=r.read(12000000)
 im=Image.open(io.BytesIO(blob));im.load()
 name=f'BBIA_1000000118_SOURCE_DETAIL_{i+1}.jpg'
 (out/name).write_bytes(blob)
 rows.append({'index':i,'file':name,'url':url,'dimensions':[im.width,im.height],'sha256':hashlib.sha256(blob).hexdigest()})
board=Image.new('RGB',(1500,1850),'#f5f5f5');d=ImageDraw.Draw(board)
d.text((14,14),'BBIA v259 PALETTE | THREE VERIFIED SOURCE PHOTOS | 6 BANDS EACH',fill='#222222')
for i,row in enumerate(rows):
 im=Image.open(out/row['file']).convert('RGB')
 d.text((i*500+12,49),f"SOURCE {i+1}  |  {im.width}x{im.height}",fill='#222222')
 for k in range(6):
  y0=round(im.height*k/6);y1=round(im.height*(k+1)/6)
  c=im.crop((0,y0,im.width,y1))
  c.thumbnail((480,248),Image.Resampling.LANCZOS)
  board.paste(c,(i*500+(500-c.width)//2,85+k*285))
  d.text((i*500+10,85+k*285+253),f"band {k+1}: y{y0}-{y1}",fill='#555555')
board.save(out/'BBIA_v259_PALETTE_18_BANDS.jpg',quality=92)
(out/'QA_MANIFEST_v259.json').write_text(json.dumps({'checkpoint':'v259','parent':'v258','sources':rows,'new_sales_jpg':0,'source_only':True,'published_modified':False},ensure_ascii=False,indent=2))
print('V259_RECOVERED',json.dumps({'source_count':len(rows),'source_dimensions':[r['dimensions'] for r in rows]}))
