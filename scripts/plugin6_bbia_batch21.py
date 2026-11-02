import requests,re,json,zipfile,io,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image,ImageDraw
P=Path('plugin6-bbia-batch21-thai');P.mkdir(exist_ok=True)
F={'never_die_mascara_slim':'Bbia Never Die Mascara Slim','lip_oil_balm_shea':'Bbia Lip Oil Balm','never_die_brush_eyeliner':'Bbia Never Die Brush Eyeliner'}
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0'})
pages={}
for url in ['https://www.bbia.co.th/products_new.php?page=2','https://www.bbia.co.th/index.php?cPath=3','https://www.bbia.co.th/index.php?cPath=4']:
 try:
  r=s.get(url,timeout=15);r.raise_for_status()
  for a in BeautifulSoup(r.text,'html.parser').find_all('a',href=True):
   label=a.get_text(' ',strip=True);im=a.find('img')
   if im:label+=' '+im.get('alt','')
   for key,name in F.items():
    if name.lower() in label.lower():
     m=re.search(r'products_id=([0-9]+)',a['href'])
     if m:pages[key]=urljoin(r.url,a['href'])
 except Exception as e:print('CATALOG_ERROR',str(e)[:80])
pages['never_die_brush_eyeliner']='https://www.bbia.co.th/product_info.php?products_id=706'
rows=[]
for key,name in F.items():
 folder=P/key;folder.mkdir(exist_ok=True);page=pages.get(key)
 rec={'family':key,'official_name':name,'page':page,'images':[]}
 if not page:rows.append(rec);continue
 try:
  r=s.get(page,timeout=18);r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser')
  originals={}
  for i,tag in enumerate(soup.find_all('img')):
   alt=tag.get('alt','');source=tag.get('src') or tag.get('data-src')
   if not source:continue
   u=urljoin(r.url,source)
   if any(x in u.lower() for x in ('logo','cart','banner','btn_','icon','review','captcha')):continue
   originals.setdefault(u,(i,u,alt))
  def dl(item):
   i,u,alt=item;v={'url':u,'alt':alt,'status':'SKIP'}
   try:
    q=s.get(u,timeout=10,headers={'Referer':page});q.raise_for_status()
    if not 2500<len(q.content)<7000000:raise ValueError('size')
    im=Image.open(io.BytesIO(q.content));im.load()
    if min(im.size)<400 or im.format not in ('JPEG','PNG','WEBP'):raise ValueError('dimensions')
    fname=f'{i:03d}.jpg';im.convert('RGB').save(folder/fname,quality=89,optimize=True)
    v.update(status='PHOTO_QA_PENDING',file=fname,size=list(im.size))
   except Exception as e:v['error']=str(e)[:100]
   return v
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
   rec['images']=list(pool.map(dl,list(originals.values())[:120]))
  ok=[x for x in rec['images'] if x['status']=='PHOTO_QA_PENDING']
  cells=[]
  for x in ok:
   im=Image.open(folder/x['file']);im.thumbnail((190,170))
   tile=Image.new('RGB',(215,210),'white');tile.paste(im,((215-im.width)//2,5))
   ImageDraw.Draw(tile).text((7,182),x['file']+' '+x['alt'][:13],fill='black');cells.append(tile)
  if cells:
   canvas=Image.new('RGB',(1075,((len(cells)+4)//5)*210),'#eee')
   for i,tile in enumerate(cells):canvas.paste(tile,((i%5)*215,(i//5)*210))
   canvas.save(folder/'CONTACT.jpg',quality=80)
 except Exception as e:rec['error']=str(e)[:140]
 print(key, 'images',len([x for x in rec['images'] if x['status']=='PHOTO_QA_PENDING']),flush=True)
 rows.append(rec)
(P/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(P/'SOURCE_CANDIDATES_QA_PENDING.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in P.rglob('*'):
  if f.is_file() and f.suffix.lower() in ('.jpg','.json'):z.write(f,f.relative_to(P).as_posix())
