from pathlib import Path
from urllib.parse import urljoin
from io import BytesIO
import requests,bs4,re,hashlib,json,zipfile,concurrent.futures
from PIL import Image
ROOT=Path('plugin6-bbia-batch10-source');ROOT.mkdir(exist_ok=True)
NAMES=[('never_die_mascara','Bbia Never Die Mascara','824'),('nudy_slim_eyeliner','Bbia Nudy Slim Eyeliner',None),('aegyosal_pencil','Bbia Aegyosal Pencil',None)]
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0'})
index_url='https://www.bbia.co.th/products_new.php'
r=s.get(index_url,timeout=23);r.raise_for_status();soup=bs4.BeautifulSoup(r.text,'html.parser')
links={}
for a in soup.find_all('a',href=True):
 label=a.get_text(' ',strip=True)
 if label:
  for slug,name,pid in NAMES:
   if name.lower() in label.lower() and re.search(r'products_id=([0-9]+)',a['href']):
    links[slug]=re.search(r'products_id=([0-9]+)',a['href']).group(1)
def collect(entry):
 slug,name,known_id=entry
 pid=known_id or links.get(slug)
 row={'slug':slug,'product':name,'product_id':pid,'status':'NO_PAGE','options':[],'other_assets':[]}
 folder=ROOT/slug;folder.mkdir(exist_ok=True)
 if not pid:
  row['error']='unable to discover official product page';return row
 url='https://www.bbia.co.th/product_info.php?products_id='+pid
 try:
  resp=s.get(url,timeout=20);resp.raise_for_status()
  row['status']='PAGE_FETCHED';row['url']=url
  doc=bs4.BeautifulSoup(resp.text,'html.parser')
  found={}
  for tag in doc.find_all('img'):
   alt=(tag.get('alt') or '').strip()
   src=tag.get('src') or tag.get('data-src')
   if not src or name.lower() not in alt.lower():continue
   shade=re.search(r' - (?:([0-9]{2})|([A-Z][0-9]{1,2})) (.+)$',alt,re.I)
   if not shade:continue
   opt=(shade.group(1) or shade.group(2)).upper()
   found.setdefault(opt,(opt,shade.group(3).strip(),urljoin(resp.url,src),alt))
  def download(item):
   opt,shade,u,alt=item
   entry={'option':opt,'official_name':shade,'url':u,'alt':alt,'status':'FETCH_FAILED'}
   try:
    result=s.get(u,timeout=13,headers={'Referer':url});result.raise_for_status()
    if len(result.content)>7_000_000:raise ValueError('file too large')
    pic=Image.open(BytesIO(result.content));pic.load()
    if pic.format not in ('JPEG','PNG','WEBP') or min(pic.size)<130:raise ValueError('not product image')
    file='option_'+opt+'.jpg'
    pic.convert('RGB').save(folder/file,'JPEG',quality=90,optimize=True)
    entry.update(status='SOURCE_IMAGE_BYTES_VERIFIED',file=file,width=pic.width,height=pic.height,sha256=hashlib.sha256(result.content).hexdigest())
   except Exception as exc:entry['error']=type(exc).__name__+': '+str(exc)[:140]
   return entry
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
   row['options']=list(pool.map(download,found.values()))
  row['verified_image_count']=sum(o['status']=='SOURCE_IMAGE_BYTES_VERIFIED' for o in row['options'])
  # Do not treat plain brand page photos, customer reviews or unverified shade names as option proof.
 except Exception as exc:row['error']=str(exc)[:180]
 print(slug,row['status'],'options',len(row['options']),'images',row.get('verified_image_count',0),flush=True)
 (folder/'manifest.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(collect,NAMES))
(ROOT/'batch_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(ROOT/'OFFICIAL_SHADES_NOT_SALE_READY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'OFFICIAL_SHADES_NOT_SALE_READY.zip') as z:assert z.testzip() is None
