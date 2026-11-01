from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image
from io import BytesIO
import json, hashlib, zipfile
sources = {
 "lucky_shine_tint": "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/26/05/22/1000000239/1000000239_magnify_043.jpg",
 "nude_lip_pencil": "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/26/04/15/1000000227/1000000227_magnify_061.jpg",
 "last_velvet_tint": "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/24/06/25/1000000135/1000000135_magnify_035.jpg",
 "lip_oil_essence": "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/26/02/09/1000000223/1000000223_magnify_038.jpg",
 "over_glaze": "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/25/03/12/1000000166/1000000166_magnify_090.jpg",
}
out=Path('plugin6-pilot-output');out.mkdir(exist_ok=True)
results=[]
for name,url in sources.items():
 row={'product_candidate':name,'source_url':url,'status':'FAILED','product_match_approved':False}
 try:
  req=Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://bbia.co.kr/'})
  with urlopen(req,timeout=10) as resp: data=resp.read(12000001)
  if len(data)>12000000:raise ValueError('size limit')
  with Image.open(BytesIO(data)) as im:
   width,height=im.size;fmt=im.format;im.verify()
  if fmt not in ('JPEG','PNG','WEBP') or min(width,height)<500:raise ValueError('image format/dimensions')
  ext={'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt]
  (out/(name+'.'+ext)).write_bytes(data)
  row.update(status='SOURCE_BYTES_VERIFIED_NOT_SALE_READY',bytes=len(data),width=width,height=height,sha256=hashlib.sha256(data).hexdigest())
 except Exception as exc:
  row['reason']=type(exc).__name__+': '+str(exc)[:250]
 results.append(row)
 print(name,row['status'],row.get('reason',''),flush=True)
(out/'audit.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'source_candidates_NOT_SALE_READY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():
  if p.is_file() and p.suffix in ('.jpg','.png','.webp','.json'):z.write(p,p.name)
with zipfile.ZipFile(out/'source_candidates_NOT_SALE_READY.zip') as z: assert z.testzip() is None
