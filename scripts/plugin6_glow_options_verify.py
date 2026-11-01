from pathlib import Path
import requests,bs4,json,re,io,zipfile,hashlib
from PIL import Image
from urllib.parse import urljoin
OUT=Path('plugin6-glow-official-thai');OUT.mkdir(exist_ok=True)
url='https://www.bbia.co.th/product_info.php?products_id=1315'
r=requests.get(url,timeout=22,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status()
soup=bs4.BeautifulSoup(r.text,'html.parser')
notes=[]
for tag in soup.find_all(['img','option','input','label','a']):
 txt=' '.join(tag.get_text(' ',strip=True).split())
 attrs={k:str(v)[:220] for k,v in tag.attrs.items() if k in ('src','data-src','alt','title','value','data-image','id','name','class')}
 if re.search(r'\b(?:00|01|02|03|04|05|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30)\b',str(attrs)+' '+txt):notes.append({'tag':tag.name,'text':txt[:140],**attrs})
urls=[]
for tag in soup.find_all('img'):
 u=tag.get('src') or tag.get('data-src')
 if u: urls.append((urljoin(url,u),tag.get('alt','')))
urls=list(dict(((x,y),None) for x,y in urls))
images=[]
for i,(u,alt) in enumerate(urls):
 if i>=180:break
 try:
  rr=requests.get(u,timeout=8,headers={'User-Agent':'Mozilla/5.0','Referer':url})
  if rr.status_code!=200 or len(rr.content)>8_000_000:continue
  im=Image.open(io.BytesIO(rr.content));im.load()
  w,h=im.size
  if min(w,h)<85:continue
  im=im.convert('RGB')
  if max(w,h)>1400:im.thumbnail((1400,1400))
  filename=f'{i:03d}.jpg';im.save(OUT/filename,quality=90,optimize=True)
  images.append({'name':filename,'url':u,'alt':alt,'width':w,'height':h,'sha256':hashlib.sha256(rr.content).hexdigest()})
 except Exception:pass
(OUT/'options_dom.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'images_manifest.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
print('option_tags',len(notes),'downloaded_images',len(images))
with zipfile.ZipFile(OUT/'OFFICIAL_GLOW_TINT_OPTION_EVIDENCE_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.iterdir():
  if p.suffix.lower() in ('.json','.jpg'):z.write(p,p.name)
