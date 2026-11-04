#!/usr/bin/env python3
"""BBIA v263: download 4 existing listed detail references in parallel; export images plus contact for targeted QA."""
import io,json,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageDraw
OUT=Path('/tmp/bbia-v263');OUT.mkdir(parents=True,exist_ok=True)
MASTER={str(x['product_id']):x for x in json.loads(Path('evidence/bbia-image-review-input.json').read_text(encoding='utf8'))['families']}
IDS=['205','173']
jobs=[(sku,i,url) for sku in IDS for i,url in enumerate(MASTER[sku]['detail_references'][:2])]
def get(job):
 sku,i,url=job
 rec={'goodsNo':sku,'detail_index':i,'url':url}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=22) as resp:b=resp.read(12000000)
  im=Image.open(io.BytesIO(b));im.load()
  rec.update(status='OK',source_dimensions=list(im.size),sha256=hashlib.sha256(b).hexdigest())
  name='BBIA_'+sku+'_OFFICIAL_DETAIL_SOURCE_'+str(i+1)+'.jpg'
  # Retain original compressed bytes for offline crop production.
  (OUT/name).write_bytes(b);rec['file']=name
  return rec,im.convert('RGB')
 except Exception as e:
  rec.update(status='HOLD',error=f'{type(e).__name__}: {e}'[:170]);return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:found=list(pool.map(get,jobs))
board=Image.new('RGB',(1500,1980),'#f5f5f5');d=ImageDraw.Draw(board)
d.text((20,10),'BBIA v263 | PRODUCT 205 & 173 | FOUR ORIGINAL DETAIL SOURCE PHOTOS',fill='#252525')
for n,(rec,im) in enumerate(found):
 x=n%2*750;y=n//2*970+45
 d.text((x+10,y),str(rec['goodsNo'])+' source '+str(rec['detail_index']+1),fill='#252525')
 if im is None:continue
 preview=im.copy();preview.thumbnail((310,790));board.paste(preview,(x+8,y+28))
 for j in range(3):
  low=round(im.height*j/3);high=round(im.height*(j+1)/3)
  crop=im.crop((0,low,im.width,high));crop.thumbnail((135,250))
  board.paste(crop,(x+340+j*135,y+48))
  d.text((x+345+j*135,y+305),'PART '+str(j+1),fill='#343434')
 d.text((x+10,y+845),f"{im.width}x{im.height}",fill='#333333')
board.save(OUT/'BBIA_v263_FOUR_REAL_SOURCES_CONTACT.jpg',quality=90)
report={'checkpoint':'v263','parent':'v262','families':IDS,'source_count':len(jobs),'download_ok':sum(x['status']=='OK' for x,y in found),'sources':[x for x,y in found],'new_sale_images':0,'public_modified':False}
(OUT/'QA_MANIFEST_v263.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V263_REAL_SOURCES',json.dumps({'families':IDS,'ok':report['download_ok']}))
