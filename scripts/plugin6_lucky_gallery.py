from pathlib import Path
import requests,re,json,html
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw
from io import BytesIO
import hashlib,zipfile
root=Path('plugin6-lucky-gallery');root.mkdir(exist_ok=True)
url='https://www.bbia.co.kr/goods/goods_view.php?goodsNo=1000000239'
r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status()
(root/'page_extract_info.txt').write_text('status '+str(r.status_code)+' bytes '+str(len(r.content))+' final_url '+r.url,encoding='utf-8')
soup=BeautifulSoup(r.text,'html.parser')
raw=[]
for tag in soup.find_all(['img','source']):
 for k in ['src','data-src','data-original','data-lazy','data-lazy-src','srcset','data-image']:
  v=tag.get(k)
  if v:
   for c in v.split(','):
    c=c.strip().split(' ')[0]
    if c:raw.append((urljoin(url,html.unescape(c)),k))
for match in re.finditer(r'(?:https?:)?//[^\s\"\'<>\\]+?\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"\'<>\\]*)?',r.text,re.I):
 raw.append((urljoin(url,html.unescape(match.group(0))), 'html_text'))
dedup={}
for u,origin in raw:
 if u.startswith('http') and u not in dedup:dedup[u]=origin
items=[]
for i,(u,origin) in enumerate(dedup.items()):
 if i>170:break
 rec={'url':u,'origin':origin,'status':'FAILED'}
 try:
  resp=requests.get(u,timeout=11,headers={'User-Agent':'Mozilla/5.0','Referer':url},stream=True)
  resp.raise_for_status()
  data=resp.raw.read(12_000_001)
  if len(data)>12_000_000:raise ValueError('too big')
  im=Image.open(BytesIO(data));im.load()
  w,h=im.size
  if w<480 or h<480:raise ValueError(f'small {w}x{h}')
  if im.format not in ('JPEG','PNG','WEBP'):raise ValueError('format')
  name=f'candidate_{i:03d}.jpg'
  if im.mode!='RGB':im=im.convert('RGB')
  im.thumbnail((1600,1600))
  im.save(root/name,'JPEG',quality=91)
  rec.update({'status':'CANDIDATE','file':name,'width':w,'height':h,'sha256':hashlib.sha256(data).hexdigest()})
 except Exception as ex:rec['error']=str(ex)[:90]
 items.append(rec)
accepted=[x for x in items if x['status']=='CANDIDATE']
# create contact sheet with stable index
cells=[]
for rec in accepted:
 im=Image.open(root/rec['file']).convert('RGB'); im.thumbnail((240,230))
 tile=Image.new('RGB',(270,280),'white');tile.paste(im,((270-im.width)//2,10))
 d=ImageDraw.Draw(tile);d.text((8,246),rec['file']+' '+str(rec['width'])+'x'+str(rec['height']),fill='black')
 cells.append(tile)
if cells:
 cols=4; rows=(len(cells)+cols-1)//cols
 sheet=Image.new('RGB',(cols*270,rows*280),'#eeeeee')
 for i,im in enumerate(cells):sheet.paste(im,((i%cols)*270,(i//cols)*280))
 sheet.save(root/'CONTACT_SHEET.jpg',quality=86)
(root/'audit.json').write_text(json.dumps({'product_page':url,'html_bytes':len(r.content),'url_candidates':len(dedup),'downloaded_candidates':len(accepted),'items':items},ensure_ascii=False,indent=2),encoding='utf-8')
print('CANDIDATES',len(dedup),'DOWNLOADED',len(accepted))
with zipfile.ZipFile(root/'SOURCE_GALLERY_UNREVIEWED.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in root.iterdir():
  if p.suffix in ('.jpg','.json','.txt'): z.write(p,p.name)
