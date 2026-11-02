from pathlib import Path
from urllib.parse import urljoin
from io import BytesIO
import json,hashlib,re,requests,bs4,zipfile
from PIL import Image
root=Path('plugin6-bbia-batch20-editorial');root.mkdir(exist_ok=True)
TERMS={'nudy_lip_pencil':'누디 립 펜슬','over_glaze_stick':'오버 글레이즈 스틱','glow_tint_mini':'글로우 틴트 미니','never_die_mascara_slim':'네버 다이 마스카라 슬림'}
pages=['https://www.bbia.co.kr/board/list.php?bdId=lookbook&page='+str(i) for i in range(1,7)]
session=requests.Session();session.headers.update({'User-Agent':'Mozilla/5.0'})
found={x:[] for x in TERMS}
for page in pages:
 try:
  response=session.get(page,timeout=18);response.raise_for_status()
  soup=bs4.BeautifulSoup(response.text,'html.parser')
  for tag in soup.find_all('a',href=True):
   label=tag.get_text(' ',strip=True);url=urljoin(response.url,tag['href'])
   if 'lookbook' not in url or 'sno=' not in url:continue
   for slug,term in TERMS.items():
    if term in label and url not in found[slug]:found[slug].append(url)
 except Exception as e:print('LIST_ERROR',str(e)[:100],flush=True)
found['nudy_lip_pencil'].append('https://www.bbia.co.kr/board/view.php?bdId=lookbook&sno=70')
found['over_glaze_stick'].append('https://www.bbia.co.kr/board/view.php?bdId=lookbook&sno=39')
report=[]
for slug,urls in found.items():
 sub=root/slug;sub.mkdir(exist_ok=True)
 links=list(dict.fromkeys(urls));record={'family':slug,'pages':links,'photos':[]}
 for article in links[:3]:
  try:
   response=session.get(article,timeout=18);response.raise_for_status()
   soup=bs4.BeautifulSoup(response.text,'html.parser')
   imageurls=[]
   for tag in soup.find_all('img'):
    source=tag.get('src') or tag.get('data-src')
    if not source:continue
    u=urljoin(response.url,source)
    if any(x in u.lower() for x in ('icon','logo','btn_','review','banner','captcha')):continue
    if u not in imageurls:imageurls.append(u)
   for u in imageurls[:85]:
    try:
     r=session.get(u,timeout=10,headers={'Referer':article});r.raise_for_status()
     if len(r.content)>11_000_000 or len(r.content)<1500:continue
     im=Image.open(BytesIO(r.content));im.load()
     if im.format not in ('JPEG','PNG','WEBP') or min(im.size)<480:continue
     hash=hashlib.sha256(r.content).hexdigest()
     if any(x['original_sha256']==hash for x in record['photos']):continue
     fname='editorial_%03d.jpg'%len(record['photos'])
     im.convert('RGB').save(sub/fname,quality=90,optimize=True)
     record['photos'].append({'file':fname,'source_url':u,'article':article,'original_sha256':hash,'size':list(im.size),'status':'PHOTO_BYTES_OK_VISUAL_SKU_QA_PENDING'})
    except Exception:continue
  except Exception as exc:record['error']=str(exc)[:140]
 print(slug,'articles',len(links),'photos',len(record['photos']),flush=True)
 (sub/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 report.append(record)
(root/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'SOURCES_ONLY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(root/'SOURCES_ONLY.zip') as z: assert z.testzip() is None
