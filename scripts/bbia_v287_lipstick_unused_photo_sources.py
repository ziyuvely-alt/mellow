#!/usr/bin/env python3
"""BBIA v287: archive truly unused BBIA goodsNo 200 official detail source indices 0-3.
Avoid any downloads of previously cropped indices 4-6. Fail per item and continue.
"""
import concurrent.futures,io,json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
out=Path('/tmp/bbia-v287');out.mkdir(parents=True,exist_ok=True)
master={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text())['families']}
urls=master['200']['detail_references'][:4]
def fetch(pair):
 i,url=pair
 item={'goodsNo':'200','source_index':i,'url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:raw=r.read(12000000)
  img=Image.open(io.BytesIO(raw));img.load()
  target=out/f'BBIA_200_UNUSED_SOURCE_{i}_v287.jpg';target.write_bytes(raw)
  item.update(status='SAVED_ORIGINAL',file=target.name,dimensions=[img.width,img.height],sha256=hashlib.sha256(raw).hexdigest())
  return item,img.convert('RGB')
 except Exception as e:
  item.update(status='HOLD_SOURCE',error=f'{type(e).__name__}: {str(e)[:120]}')
  return item,None
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:found=list(p.map(fetch,enumerate(urls)))
board=Image.new('RGB',(1800,930),'#f7f6f4');d=ImageDraw.Draw(board)
d.text((15,10),'BBIA 200 v287 ONLY UNUSED OFFICIAL ORIGINALS (0-3)',fill='#242424')
for i,(item,im) in enumerate(found):
 x=i*450+8
 d.text((x,42),f'INDEX {i} {item["status"]}',fill='#222')
 if im is None:continue
 full=im.copy();full.thumbnail((195,750));board.paste(full,(x,80))
 for j in range(2):
  start=int(im.height*j*.47);crop=im.crop((0,start,im.width,min(im.height,start+min(850,im.height))))
  crop.thumbnail((110,450))
  board.paste(crop,(x+205+j*112,120))
 d.text((x,852),f'{im.width}×{im.height}',fill='#333')
board.save(out/'BBIA_200_v287_UNUSED_FOUR_SOURCES_CONTACT.jpg',quality=89)
manifest={'checkpoint':'v287','parent':'v286','goodsNo':'200','original_indices':[0,1,2,3],'saved':sum(x['status']=='SAVED_ORIGINAL' for x,_ in found),'records':[x for x,_ in found],'new_sales_images':0,'old_jpg_modified':False}
(out/'BBIA_v287_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V287_ORIGINALS',json.dumps({'saved':manifest['saved'],'source_indices':[0,1,2,3]}))
