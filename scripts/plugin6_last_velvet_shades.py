from pathlib import Path
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests,json,re,hashlib,zipfile,concurrent.futures
url='https://www.bbia.co.th/product_info.php?products_id=1387'
out=Path('plugin6-last-velvet-official');out.mkdir(exist_ok=True)
session=requests.Session();session.headers.update({'User-Agent':'Mozilla/5.0'})
r=session.get(url,timeout=20);r.raise_for_status()
soup=BeautifulSoup(r.text,'html.parser')
raw=[]
for tag in soup.find_all('img'):
  src=tag.get('src') or tag.get('data-src');alt=tag.get('alt','')
  if src:raw.append({'src':urljoin(r.url,src),'alt':alt,'title':tag.get('title','')})
raw=list({x['src']:x for x in raw}.values())
rec=[]
def get(i,x):
 row={**x,'i':i,'status':'SKIP'}
 try:
  s=session.get(x['src'],timeout=12,headers={'Referer':url});s.raise_for_status()
  if len(s.content)>7_000_000:raise ValueError('large')
  image=Image.open(BytesIO(s.content));image.load()
  w,h=image.size
  if min(w,h)<85:raise ValueError('small')
  name=f'{i:03d}.jpg'; image.convert('RGB').save(out/name,quality=92,optimize=True)
  row.update(status='IMAGE_BYTES_VERIFIED',name=name,width=w,height=h,sha256=hashlib.sha256(s.content).hexdigest())
 except Exception as e: row['error']=str(e)[:130]
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:rec=list(ex.map(lambda it:get(*it),enumerate(raw)))
options=[]
for x in rec:
 m=re.search(r'(?:Last Velvet Tint.*?)\s*-\s*V?(\d{2})\s+(.+)',x['alt'],re.I)
 if m:
  options.append({'number':int(m.group(1)),'official_name':m.group(2).strip(),'asset':x.get('name'),'url':x['src'],'status':x['status']})
# Also retain exact page option text as received
textdata=soup.get_text(' ',strip=True)
(out/'audit.json').write_text(json.dumps({'source':url,'image_urls':len(raw),'verified_image_files':sum(x['status']=='IMAGE_BYTES_VERIFIED' for x in rec),'options':options,'assets':rec,'official_page_text_excerpt':textdata[:15000]},ensure_ascii=False,indent=2),encoding='utf-8')
print('VERIFIED_FILES',sum(x['status']=='IMAGE_BYTES_VERIFIED' for x in rec),'OFFICIAL_SHADE_MATCHES',len(options),flush=True)
for x in options:print('SHADE',x['number'],x['official_name'][:40],x['status'],flush=True)
with zipfile.ZipFile(out/'LAST_VELVET_OFFICIAL_PHOTO_CANDIDATES_NOT_SALE_READY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.glob('*'):
  if p.suffix.lower() in ('.jpg','.json'):z.write(p,p.name)
