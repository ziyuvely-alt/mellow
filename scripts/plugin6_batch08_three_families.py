from pathlib import Path
import requests, bs4, re, json, hashlib, io, zipfile, concurrent.futures
from PIL import Image
from urllib.parse import urljoin
SOURCES=[
 ('last_auto_gel_eyeliner','579','Bbia Last Auto Gel Eyeliner'),
 ('ready_to_wear_eye_palette','787','Bbia Ready To Wear Eye Palette'),
 ('ready_to_wear_downy_cheek','799','Bbia Ready To Wear Downy Cheek'),
]
out=Path('plugin6-bbia-batch08-source'); out.mkdir(exist_ok=True)
def capture(info):
 slug,pid,product=info; url='https://www.bbia.co.th/product_info.php?products_id='+pid
 sub=out/slug;sub.mkdir(exist_ok=True)
 row={'family':slug,'product':product,'url':url,'options':[],'assets':[],'errors':[]}
 try:
  r=requests.get(url,timeout=22,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status()
  soup=bs4.BeautifulSoup(r.text,'html.parser')
  images=[]
  for im in soup.find_all('img'):
   u=im.get('src') or im.get('data-src')
   alt=im.get('alt','').strip()
   if not u:continue
   u=urljoin(r.url,u)
   if (product.lower() in alt.lower() or slug=='ready_to_wear_downy_cheek' and 'downy cheek' in alt.lower()) and re.search(r'\b\d{2}\b',alt):
    m=re.search(r'(?:-|\\s)\\s*(\\d{2})\\s+(.+)$',alt,re.I)
    if m:
     opt=int(m.group(1))
     if slug=='last_auto_gel_eyeliner' and opt==10:
      row['options'].append({'number':opt,'name':m.group(2),'status':'EXCLUDED_PREVIOUSLY_DISCONTINUED'});continue
     images.append((opt,m.group(2).strip(),u,alt))
  unique={}
  for item in images:unique.setdefault(item[0],item)
  def dl(item):
   num,name,imgurl,alt=item
   rec={'number':num,'official_name':name,'url':imgurl,'alt':alt,'status':'NOT_DOWNLOADED'}
   try:
    resp=requests.get(imgurl,timeout=13,headers={'User-Agent':'Mozilla/5.0','Referer':url});resp.raise_for_status()
    if not resp.content or len(resp.content)>8_000_000:raise ValueError('oversize/empty')
    image=Image.open(io.BytesIO(resp.content));image.load()
    if min(image.size)<85:raise ValueError('too small')
    fn='option_%02d.jpg'%num;image.convert('RGB').save(sub/fn,quality=93,optimize=True)
    rec.update(status='OFFICIAL_PAGE_FILE_QA_PENDING',file=fn,width=image.width,height=image.height,sha256=hashlib.sha256(resp.content).hexdigest())
   except Exception as ex:rec['error']=str(ex)[:170]
   return rec
  with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
   opts=list(pool.map(dl,unique.values()))
  row['options'].extend(opts);row['fetched']=sum(o['status']=='OFFICIAL_PAGE_FILE_QA_PENDING' for o in opts)
 except Exception as ex: row['errors'].append(str(ex)[:240])
 print(slug,'options',len(row['options']),'downloaded',row.get('fetched',0),flush=True)
 (sub/'option_manifest.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 audit=list(pool.map(capture,SOURCES))
(out/'batch_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'BATCH08_OFFICIAL_OPTION_CANDIDATES_QA_PENDING.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'): z.write(p,p.relative_to(out).as_posix())
with zipfile.ZipFile(out/'BATCH08_OFFICIAL_OPTION_CANDIDATES_QA_PENDING.zip') as z:assert z.testzip() is None
