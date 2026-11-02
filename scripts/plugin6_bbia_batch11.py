from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image
import requests,concurrent.futures,re,json,hashlib,zipfile,time
BASE="https://www.bbia.co.th/"
TARGETS={
"chaltteok_blush":["Bbia Chaltteok Blush"],
"eau_matte_cushion":["Bbia Eau Matte Cushion"],
"eau_glow_cushion":["Bbia Eau Glow Cushion"],
"eau_stay_concealer":["Bbia Eau Stay Concealer"],
"eau_powder_pact":["Bbia Eau Powder Pact"],
"last_auto_eyebrow_slim":["Bbia Last Auto Eyebrow Pencil Slim"],
"last_eye_palette":["Bbia Last Eye Palette"],
"last_eye_primer":["Bbia Last Eye Primer"],
"last_contour_pen":["Bbia Last Contour Pen Eyeliner"],
"last_powder_pencil":["Bbia Last Powder Pencil"],
"eye_cheek_primer":["Bbia Eye & Cheek Primer Balm"],
"aegyosal_pencil":["Bbia Aegyosal Pencil"],
"nudy_lip_pencil":["Bbia Nudy Lip Pencil"],
"lip_oil_essence":["Bbia Lip Oil Essence"],
"eau_matte_cushion_puff":["Bbia Eau Matte Cushion Puff"]
}
out=Path("plugin6-bbia-batch11-official");out.mkdir(exist_ok=True)
session=requests.Session();session.headers.update({"User-Agent":"Mozilla/5.0"})
# Search categories and multiple new-product pages; no guess-based product identity matching.
catalog={}
pages=[f"{BASE}products_new.php?page={i}" for i in range(1,9)]+[BASE+"Brand/Bbia/",BASE+"index.php?cPath=5",BASE+"index.php?cPath=7",BASE+"index.php?cPath=4",BASE+"index.php?cPath=3",BASE+"index.php?cPath=2",BASE+"index.php?cPath=1"]
for page in pages:
 try:
  res=session.get(page,timeout=15);res.raise_for_status()
  soup=BeautifulSoup(res.text,'html.parser')
  for a in soup.select('a[href]'):
   href=urljoin(res.url,a['href'])
   match=re.search(r'products_id=([0-9]+)',href)
   if not match:continue
   title=' '.join(a.get_text(' ',strip=True).split())
   img=a.find('img')
   if img:title+=' '+img.get('alt','')
   if not title:continue
   for slug,values in TARGETS.items():
    if any(value.lower() in title.lower() for value in values):
     catalog.setdefault(slug,{})[match.group(1)]={"product_id":match.group(1),"name_seen":title[:160],"discovery_url":page}
 except Exception as exc:print('CATALOG_PAGE_ERROR',str(exc)[:90],flush=True)
def one(target):
 slug,terms=target
 choices=list(catalog.get(slug,{}).values())
 row={"slug":slug,"wanted_names":terms,"discovered":choices,"options":[],"status":"NO_OFFICIAL_PAGE_FOUND"}
 folder=out/slug;folder.mkdir(exist_ok=True)
 if not choices:return row
 # Prefer exact name match; retain alternatives without silently conflating families.
 exact=[x for x in choices if x['name_seen'].lower().startswith(terms[0].lower())]
 pick=(exact or choices)[0]
 page=BASE+'product_info.php?products_id='+pick['product_id']
 row['product_page']=page
 try:
  res=requests.get(page,timeout=20,headers={'User-Agent':'Mozilla/5.0'});res.raise_for_status()
  row['status']='PAGE_ACCESSED'
  soup=BeautifulSoup(res.text,'html.parser')
  imgs=[]
  for tag in soup.find_all('img'):
   src=tag.get('src') or tag.get('data-src')
   alt=tag.get('alt','').strip()
   if not src or not any(term.lower() in alt.lower() for term in terms):continue
   # Only alts that clearly label a 2-digit or letter+digit option. Distinct package/product photo is not assumed yet.
   m=re.search(r' - ([A-Za-z]?[0-9]{1,2}) (.+)$',alt)
   if not m:continue
   opt=m.group(1).upper();name=m.group(2).strip()
   imgs.append((opt,name,urljoin(res.url,src),alt))
  unique={}
  for img in imgs:unique.setdefault(img[0],img)
  def dl(item):
   opt,name,url,alt=item
   result={"option":opt,"name":name,"url":url,"alt":alt,"status":"DOWNLOAD_FAILED"}
   try:
    resp=requests.get(url,timeout=11,headers={'User-Agent':'Mozilla/5.0','Referer':page});resp.raise_for_status()
    if len(resp.content)>8_000_000:raise ValueError('large')
    im=Image.open(BytesIO(resp.content));im.load()
    if im.format not in ('JPEG','PNG','WEBP') or min(im.size)<120:raise ValueError('not usable image')
    file='shade_'+opt+'.jpg';im.convert('RGB').save(folder/file,quality=90,optimize=True)
    result.update(status='PHOTO_FETCHED_NEEDS_SKU_VISUAL_QA',file=file,width=im.width,height=im.height,sha256=hashlib.sha256(resp.content).hexdigest())
   except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)[:130]
   return result
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:row['options']=list(pool.map(dl,unique.values()))
  row['downloaded']=sum(x['status'].startswith('PHOTO_FETCHED') for x in row['options'])
 except Exception as exc:row['status']='PAGE_FAILED';row['error']=str(exc)[:170]
 print(slug,row['status'],'photos',row.get('downloaded',0),flush=True)
 (folder/'manifest.json').write_text(json.dumps(row,indent=2,ensure_ascii=False),encoding='utf-8')
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(one,TARGETS.items()))
(out/'DISCOVERY_AND_PHOTO_AUDIT.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'BBIA_BATCH11_OFFICIAL_OPTIONS_NOT_SALE_READY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(out).as_posix())
with zipfile.ZipFile(out/'BBIA_BATCH11_OFFICIAL_OPTIONS_NOT_SALE_READY.zip') as z:assert z.testzip() is None
