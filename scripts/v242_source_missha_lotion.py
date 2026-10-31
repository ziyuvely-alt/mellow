import requests,hashlib,json,io
from PIL import Image
from pathlib import Path
out=Path("evidence/v242-missha-lotion-130ml-candidates");out.mkdir(parents=True,exist_ok=True)
targets=[
("official_ableshop","https://static.ableshop.kr/ext/images/goods/top/24/05/24/03/BO00112469/0000342808.jpg"),
("moyo_box","https://i.moyo.ua/img/products/5777/25_600.jpg"),
("sweetcare_pack","https://static.sweetcare.pt/img/prd/max/v-638428971694852599/missha-017073hs_01.jpg"),
("perlanera_lifestyle","https://www.perlaneraskin.com/cdn/shop/files/ecbcd4af-1846-4238-9931-329f6219e831.jpg?v=1717253436&width=1445")
]
record=[]
for name,url in targets:
 try:
  response=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*','Referer':'https://www.ableshop.kr/'})
  response.raise_for_status()
  image=Image.open(io.BytesIO(response.content));image.load()
  if image.width<250 or image.height<250:raise ValueError("too small")
  outpath=out/(name+".jpg");image.convert("RGB").save(outpath,quality=93,optimize=True)
  blob=outpath.read_bytes()
  record.append({'name':name,'url':url,'dimensions':list(image.size),'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'status':'CANDIDATE_TO_VISUALLY_REVIEW'})
  print('OK',name,image.size,flush=True)
 except Exception as e:record.append({'name':name,'url':url,'error':str(e)[:250],'status':'FAILED'});print('FAIL',name,str(e)[:130],flush=True)
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
