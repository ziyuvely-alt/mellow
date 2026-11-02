from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
import requests,concurrent.futures,re,json,hashlib,zipfile,html
ROOT=Path('plugin6-bbia-batch18-korean-detail');ROOT.mkdir(exist_ok=True)
ITEMS={
'over_glaze':'1000000166',
'last_powder_lipstick':'200',
'lip_oil_balm_shea':'228',
'never_die_mascara_slim':'1000000056',
'never_die_eyeliner':'207',
'eau_perfect_brush':'1000000142',
'chaltteok_rubycell_puff':'1000000251',
'ready_water_lipstick':'1000000074',
'leau_tint_mini':'1000000187',
'leau_tint':'1000000113',
'last_velvet_tint':'1000000135',
'lip_oil_essence':'1000000223',
'last_contour_pen':'1000000057',
'ready_eye_shadow':'238',
'eau_stay_concealer':'1000000125'
}
def one(item):
 slug,gid=item;page='https://www.bbia.co.kr/goods/goods_view.php?goodsNo='+gid;folder=ROOT/slug;folder.mkdir(exist_ok=True)
 row={'family':slug,'goods_id':gid,'official_page':page,'photos':[],'status':'PAGE_FAILED'}
 try:
  req=requests.get(page,timeout=22,headers={'User-Agent':'Mozilla/5.0'})
  req.raise_for_status();row['status']='PAGE_OK';soup=BeautifulSoup(req.text,'html.parser')
  urls=[]
  for tag in soup.find_all(['img','source']):
   for att in ('src','data-src','data-original','data-lazy-src','data-image','srcset'):
    val=tag.get(att)
    if not val:continue
    for v in val.split(','):
     url=urljoin(req.url,html.unescape(v.strip().split(' ')[0]))
     if gid in url and not any(s in url.lower() for s in ('goodsreview','/review/','/board/')):
      urls.append(url)
  for m in re.finditer(r'(?:https?:)?//[^\\s\\\"\\\'<>]+?\\.(?:jpg|jpeg|png|webp)',req.text,re.I):
   url=urljoin(req.url,html.unescape(m.group(0)))
   if gid in url and not any(s in url.lower() for s in ('goodsreview','/review/','/board/')):urls.append(url)
  urls=list(dict.fromkeys(urls))
  def collect(entry):
   i,url=entry
   rec={'url':url,'status':'REJECTED'}
   try:
    r=requests.get(url,timeout=12,headers={'User-Agent':'Mozilla/5.0','Referer':page})
    r.raise_for_status()
    if len(r.content)>12_000_000 or len(r.content)<2000:raise ValueError('file-size')
    photo=Image.open(BytesIO(r.content));photo.load()
    if photo.format not in ('JPEG','PNG','WEBP') or min(photo.size)<500:raise ValueError('dimensions/format')
    name=f'source_{i:03d}.jpg';photo.convert('RGB').save(folder/name,quality=92,optimize=True)
    rec.update(status='OFFICIAL_GOODS_ID_MATCH_BYTES_OK',name=name,width=photo.width,height=photo.height,sha256=hashlib.sha256(r.content).hexdigest())
   except Exception as e:rec['error']=str(e)[:170]
   return rec
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
   row['photos']=list(pool.map(collect,enumerate(urls[:42])))
  row['verified_photo_files']=sum(x['status']=='OFFICIAL_GOODS_ID_MATCH_BYTES_OK' for x in row['photos'])
 except Exception as e:row['error']=str(e)[:180]
 print(slug,row['status'],'photos',row.get('verified_photo_files',0),flush=True)
 (folder/'manifest.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,ITEMS.items()))
(ROOT/'batch_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(ROOT/'BBIA_BATCH18_KOREAN_SOURCES_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'BBIA_BATCH18_KOREAN_SOURCES_QA.zip') as z:assert z.testzip() is None
