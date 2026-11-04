#!/usr/bin/env python3
"""v307: only indices 5/6 of BBIA Lucky Shine Tint that were not reviewed in earlier source gates."""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
import hashlib,io,json,concurrent.futures
OUT=Path('/tmp/bbia-v307');OUT.mkdir(parents=True,exist_ok=True)
master=json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']
row=next(x for x in master if str(x['product_id'])=='1000000239')
indices=(5,6)
def fetch(i):
  url=row['detail_references'][i]
  record={'goodsNo':'1000000239','detail_index':i,'source_url':url}
  try:
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=19) as resp: raw=resp.read(12000000)
    im=Image.open(io.BytesIO(raw));im.load()
    filename=f'BBIA_1000000239_ORIGINAL_UNSEEN_{i}_v307.jpg'
    (OUT/filename).write_bytes(raw)
    record.update(status='SOURCE_SAVED',filename=filename,dimensions=[im.width,im.height],sha256=hashlib.sha256(raw).hexdigest())
    return record,im.convert('RGB')
  except Exception as e:record.update(status='HOLD_SOURCE',error=str(e)[:180]);return record,None
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:results=list(e.map(fetch,indices))
board=Image.new('RGB',(1600,1000),'#f8f7f6');d=ImageDraw.Draw(board)
d.text((12,12),'BBIA v307 - LUCKY SHINE TINT / TWO GENUINELY UNUSED OFFICIAL SOURCES',fill='#222222')
for col,(record,pic) in enumerate(results):
  x=col*800
  d.text((x+10,45),f"Source {record['detail_index']} / {record['status']}",fill='#252525')
  if pic is None:continue
  pic1=pic.copy();pic1.thumbnail((350,790),Image.Resampling.LANCZOS)
  board.paste(pic1,(x+10,85))
  top=pic.crop((0,0,pic.width,min(pic.height,1000)));top.thumbnail((380,790),Image.Resampling.LANCZOS)
  board.paste(top,(x+410,85))
  d.text((x+15,904),f"{pic.width}x{pic.height}",fill='#444444')
board.save(OUT/'BBIA_v307_LUCKY_TINT_TWO_SOURCE_CONTACT.jpg',quality=90)
result={'checkpoint':'v307','parent':'v306','requested':2,'saved':sum(r['status']=='SOURCE_SAVED' for r,_ in results),'sources':[r for r,_ in results],'new_images':0,'published_modified':False}
(OUT/'BBIA_v307_MANIFEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('V307_SOURCES',json.dumps({'saved':result['saved']}))
