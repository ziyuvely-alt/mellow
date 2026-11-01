from pathlib import Path
from PIL import Image
from io import BytesIO
from urllib.request import Request,urlopen
import zipfile,hashlib,json
BASE='https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/'
DATA=[["20","Never Die Mascara","19/03/13/172/172_magnify_092.jpg"],["21","Never Die Mascara Slim","22/08/31/1000000056/1000000056_magnify_07.jpg"],["22","Never Die Eyeliner","19/03/13/207/207_magnify_058.jpg"],["23","Last Eye Primer","19/03/13/205/205_magnify_098.jpg"],["24","Last Auto Eyebrow Pencil","23/05/21/1000000108/1000000108_magnify_013.jpg"],["25","Last Contour Pen Eyeliner 01","22/08/31/1000000057/1000000057_magnify_05.jpg"],["26","Last Pen Eyeliner","19/03/13/173/173_magnify_011.jpg"],["27","Ready To Wear Eye Palette Mini","25/09/36/1000000209/1000000209_magnify_030.jpg"],["28","Last Eye Palette","24/11/46/1000000151/1000000151_magnify_0100.jpg"],["29","Ready To Wear Eye Shadow","19/03/13/238/238_magnify_02.jpg"],["30","Ready To Wear Eye Palette","19/03/13/234/234_magnify_010.jpg"],["31","Essential Eye Palette","23/10/42/1000000118/1000000118_magnify_012.jpg"],["32","Eye And Cheek Primer Balm","26/07/27/1000000247/1000000247_magnify_096.jpg"],["33","Chaltteok Blush","26/02/09/1000000221/1000000221_magnify_051.jpg"],["34","Last Contour Stick","24/05/19/1000000134/1000000134_magnify_043.jpg"],["35","Ready To Wear Downy Cheek","19/03/13/239/239_magnify_065.jpg"],["36","Last Blush","19/03/13/188/188_magnify_061.jpg"],["37","Eau Glow Cushion","24/02/06/1000000122/1000000122_magnify_089.jpg"],["38","Eau Matte Cushion Refill","25/05/20/1000000179/1000000179_magnify_023.jpg"],["39","Eau Matte Cushion","25/05/20/1000000178/1000000178_magnify_057.jpg"],["40","Eau Stay Concealer","24/02/06/1000000125/1000000125_magnify_078.jpg"],["41","Eau Glow Cushion Mini","24/02/06/1000000120/1000000120_magnify_099.jpg"],["42","Eau Glow Cushion Refill","24/02/06/1000000124/1000000124_magnify_061.jpg"],["43","Eau Matte Cushion Puff 2pcs","25/05/21/1000000185/1000000185_magnify_025.jpg"],["44","Eau Cushion Puff 2pcs","24/02/06/1000000126/1000000126_magnify_096.jpg"],["45","Eau Powder Pact Puff 2pcs","25/08/33/1000000200/1000000200_magnify_072.jpg"],["46","Eau Perfect Brush","24/09/39/1000000142/1000000142_magnify_062.jpg"],["47","Eau Finger Puff 2pcs","24/02/06/1000000127/1000000127_magnify_063.jpg"],["48","Chaltteok Rubycell Puff 1pc","26/08/36/1000000251/1000000251_magnify_058.jpg"]]
out=Path('plugin6-bbia-batch02-sources');out.mkdir(exist_ok=True)
rows=[]
for id,name,path in DATA:
  url=BASE+path
  rec={'id':id,'name':name,'url':url,'status':'FETCH_FAILED','verified_product_match':False,'sales_ready':False}
  try:
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bbia.co.kr/'})
    with urlopen(req,timeout=13) as f:raw=f.read(10000001)
    if not raw or len(raw)>10000000:raise ValueError('byte limit')
    with Image.open(BytesIO(raw)) as im:
      form=im.format;size=im.size;im.verify()
    if form not in ('JPEG','PNG','WEBP') or min(size)<450:raise ValueError('unsupported format or too small')
    ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[form]
    filename='family_'+id+ext
    (out/filename).write_bytes(raw)
    rec.update(status='FILE_VERIFIED_NEEDS_PRODUCT_QA',filename=filename,bytes=len(raw),width=size[0],height=size[1],sha256=hashlib.sha256(raw).hexdigest())
  except Exception as e:
    rec['failure']=type(e).__name__+': '+str(e)[:150]
  rows.append(rec)
  print(id,name,rec['status'],flush=True)
(out/'manifest.json').write_text(json.dumps({'total':len(rows),'downloaded':sum(r['status']=='FILE_VERIFIED_NEEDS_PRODUCT_QA' for r in rows),'items':rows},indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'BBIA_BATCH02_SOURCE_CANDIDATES_ONLY.zip','w',zipfile.ZIP_DEFLATED) as z:
  for file in out.glob('*'):
    if file.suffix.lower() in ('.jpg','.png','.webp','.json'):z.write(file,file.name)
with zipfile.ZipFile(out/'BBIA_BATCH02_SOURCE_CANDIDATES_ONLY.zip') as z: assert z.testzip() is None
