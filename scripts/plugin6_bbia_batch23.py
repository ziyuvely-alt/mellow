from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image
import requests,json,re,hashlib,zipfile,concurrent.futures
GOODS={
'glow_tint_mini':'1000000163',
'last_velvet_tint_mini':'1000000186',
'over_glaze_mini':'1000000208',
'never_die_mascara_slim':'1000000056',
'last_pen_eyeliner':'173',
'ready_eye_shadow':'238',
'essential_eye_palette':'1000000118',
'eau_matte_cushion_refill':'1000000179',
'eau_glow_cushion_mini':'1000000120',
'eau_glow_cushion_refill':'1000000124',
'eau_matte_puff':'1000000185',
'eau_cushion_puff':'1000000126',
'eau_powder_puff':'1000000200',
'eau_perfect_brush':'1000000142',
'eau_finger_puff':'1000000127'}
OUT=Path('plugin6-bbia-batch23-korean-detail');OUT.mkdir(exist_ok=True)
U='https://www.bbia.co.kr/goods/goods_view.php?goodsNo='
def one(entry):
 slug,gid=entry;folder=OUT/slug;folder.mkdir(exist_ok=True)
 page=U+gid; rec={'family':slug,'goodsNo':gid,'official_page':page,'status':'FAILED','candidates':[],'page_title':''}
 try:
  r=requests.get(page,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
  r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser')
  rec['status']='PAGE_OK';rec['page_title']=(soup.title.get_text(' ',strip=True) if soup.title else '')[:170]
  # Collect official merchandise detail images, not store navigation or customer reviews.
  candidates={}
  for tag in soup.find_all('img'):
   src=tag.get('src') or tag.get('data-src') or tag.get('data-original') or tag.get('data-lazy-src')
   if not src:continue
   u=urljoin(r.url,src)
   if not u.startswith('http'):continue
   if any(bad in u.lower() for bad in ['/board/','/review/','goodsreview','captcha','btn_','icon','logo','rating','payment','flag','/banner/']):continue
   ancestors=[((p.get('id') or '')+' '+(' '.join(p.get('class',[])))).lower() for p in list(tag.parents)[:7]]
   position=' | '.join(ancestors)[:300]
   if gid not in u and not any(k in position for k in ('detail','goods','prd','product','content')):continue
   candidates.setdefault(u,{'url':u,'alt':tag.get('alt','')[:160],'ancestors':position})
  def dl(it):
   i,row=it;item={**row,'status':'DOWNLOAD_FAILED'}
   try:
    rsp=requests.get(row['url'],timeout=12,headers={'Referer':page,'User-Agent':'Mozilla/5.0'})
    rsp.raise_for_status()
    if len(rsp.content)>13_000_000 or len(rsp.content)<1500:raise ValueError('file size')
    im=Image.open(BytesIO(rsp.content));im.load()
    if min(im.size)<490 or im.format not in ('JPEG','PNG','WEBP'):raise ValueError('small/invalid')
    fname=f'{i:03d}.jpg';im.convert('RGB').save(folder/fname,quality=89,optimize=True)
    item.update(status='OFFICIAL_PAGE_CANDIDATE_UNVERIFIED_IMAGE',file=fname,width=im.width,height=im.height,sha256=hashlib.sha256(rsp.content).hexdigest())
   except Exception as e:item['error']=str(e)[:140]
   return item
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rec['candidates']=list(pool.map(dl,enumerate(list(candidates.values())[:55])))
  rec['valid_count']=sum(x['status']=='OFFICIAL_PAGE_CANDIDATE_UNVERIFIED_IMAGE' for x in rec['candidates'])
 except Exception as e: rec['error']=str(e)[:170]
 print(slug,rec['status'],rec.get('valid_count',0),flush=True)
 (folder/'manifest.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(one,GOODS.items()))
(OUT/'audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(OUT/'SOURCES_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(OUT/'SOURCES_QA.zip') as z:assert z.testzip() is None
