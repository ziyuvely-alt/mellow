#!/usr/bin/env python3
"""v268 recover and visually slice only two confirmed MINI branded detail original photographs.
No reprocessing the third unresolved mini and no edits to published files.
"""
import io,json,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
OUT=Path('/tmp/bbia-v268');OUT.mkdir(exist_ok=True,parents=True)
SOURCES=[('1000000163','https://images002.sabangnet.co.kr/v1/AUTH_c55e59a8ec2149e7ad5e61ca73645bd9/mw169402/image/1781219858925.jpg'),('1000000186','https://images002.sabangnet.co.kr/v1/AUTH_c55e59a8ec2149e7ad5e61ca73645bd9/mw169402/image/1781219858268.jpg')]
def fetch(row):
 sku,url=row
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as req: data=req.read(12_000_000)
  im=Image.open(io.BytesIO(data));im.load()
  path=OUT/(sku+'_ORIGINAL_MINI_DETAIL.jpg')
  path.write_bytes(data)
  return {'sku':sku,'status':'RECOVERED','file':path.name,'dimensions':list(im.size),'sha256':hashlib.sha256(data).hexdigest(),'url':url},im.convert('RGB')
 except Exception as e:return {'sku':sku,'status':'HOLD','reason':str(e)[:150]},None
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:r=list(pool.map(fetch,SOURCES))
contact=Image.new('RGB',(1400,1350),'#f8f8f8');d=ImageDraw.Draw(contact)
d.text((10,10),'BBIA v268 | MINI PRODUCT 2 ORIGINAL DETAIL SOURCES | PHOTO CROP GATE',fill='#222222')
for index,(entry,im) in enumerate(r):
 if im is None:continue
 x=index*700
 d.text((x+10,36),entry['sku']+' '+str(im.size),fill='#222222')
 for k in range(5):
  top=round(im.height*k/5);bottom=round(im.height*(k+1)/5)
  crop=im.crop((0,top,im.width,bottom))
  crop.thumbnail((660,235),Image.Resampling.LANCZOS)
  contact.paste(crop,(x+(700-crop.width)//2,68+k*250))
  d.text((x+15,68+k*250+232),f'band{k+1}: {top}..{bottom}',fill='#4a4a4a')
contact.save(OUT/'BBIA_v268_TWO_MINI_FIVE_BANDS.jpg',quality=92)
report={'checkpoint':'v268','parent':'v267','fetched_originals':sum(e['status']=='RECOVERED' for e,_ in r),
        'sources':[e for e,_ in r],'output_purpose':'SOURCE_PHOTO_ARCHIVE_ONLY','new_sales_approved':0,'public_files_changed':False}
(OUT/'BBIA_v268_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V268_SOURCE',json.dumps({'recovered':report['fetched_originals']}))
