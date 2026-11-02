from pathlib import Path
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
import requests,re,json,hashlib,zipfile,concurrent.futures
base='https://www.bbia.co.th/'
names={
'glow_tint_mini':['Bbia Glow Tint Mini'],
'last_velvet_tint_mini':['Bbia Last Velvet Tint Mini'],
'over_glaze_mini':['Bbia Over Glaze Mini'],
'nudy_slim_eyeliner':['Bbia Nudy Slim Eyeliner'],
'never_die_mascara':['Bbia Never Die Mascara'],
'never_die_mascara_slim':['Bbia Never Die Mascara Slim'],
'last_contour_pen':['Bbia Last Contour Pen Eyeliner'],
'last_pen_eyeliner':['Bbia Last Pen Eyeliner','Bbia Never Die Brush Eyeliner'],
'ready_eye_shadow':['Bbia Ready To Wear Eye Shadow'],
'essential_eye_palette':['Bbia Essential Eye Palette'],
'eau_matte_cushion_refill':['Bbia Eau Matte Cushion Refill'],
'eau_glow_cushion_mini':['Bbia Eau Glow Cushion Mini'],
'eau_glow_cushion_refill':['Bbia Eau Glow Cushion Refill'],
'eau_matte_puff':['Bbia Eau Matte Cushion Puff'],
'eau_cushion_puff':['Bbia Eau Cushion Puff'],
'eau_powder_puff':['Bbia Eau Powder Pact Puff'],
'eau_perfect_brush':['Bbia Eau Perfect Brush'],
'eau_finger_puff':['Bbia Eau Finger Puff']
}
root=Path('plugin6-bbia-batch22-thai');root.mkdir(exist_ok=True)
sess=requests.Session();sess.headers.update({'User-Agent':'Mozilla/5.0'})
discovery={k:[] for k in names}
for i in range(1,9):
 url=base+'products_new.php?page='+str(i)
 try:
  r=sess.get(url,timeout=20);r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser')
  for a in soup.find_all('a',href=True):
   name=a.get_text(' ',strip=True)
   img=a.find('img')
   if img:name+=' '+img.get('alt','')
   match=re.search(r'products_id=([0-9]+)',a['href'])
   if not match:continue
   for slug,terms in names.items():
    if any(term.lower() in name.lower() for term in terms):
     entry={'id':match.group(1),'catalog_label':name[:160],'catalog_url':url}
     if entry not in discovery[slug]:discovery[slug].append(entry)
 except Exception as e:print('CATALOG_FAIL',i,str(e)[:100],flush=True)
# verified from known official webpage results and source collections
known={'never_die_mascara':'824','last_contour_pen':'806','last_pen_eyeliner':'706'}
def collect(item):
 slug,terms=item
 opts=discovery[slug]
 chosen=next((x for x in opts if x['catalog_label'].lower().startswith(terms[0].lower())),opts[0] if opts else None)
 product_id=(chosen or {}).get('id') or known.get(slug)
 folder=root/slug;folder.mkdir(exist_ok=True)
 record={'slug':slug,'product_expected':terms[0],'catalog_evidence':opts,'product_id':product_id,'candidate_images':[],'status':'MISSING_OFFICIAL_LISTING'}
 if not product_id:return record
 page=base+'product_info.php?products_id='+product_id;record['product_url']=page
 try:
  r=requests.get(page,timeout=25,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser');record['status']='PAGE_OK'
  # capture images from page but screen out unrelated recs using evidence metadata for review
  found={}
  for tag in soup.find_all('img'):
   url=tag.get('src') or tag.get('data-src');alt=tag.get('alt','').strip()
   if not url:continue
   url=urljoin(r.url,url)
   if any(token in url.lower() for token in ('/review/','review_','/board/','logo','icon','banner','payment','cart','button')):continue
   found.setdefault(url,{'url':url,'alt':alt,'classes':tag.get('class'),'parent_classes':tag.parent.get('class') if tag.parent else []})
  # parallel img downloading
  def dl(pair):
   i,v=pair;result={**v,'status':'REJECTED','num':i}
   try:
    response=requests.get(v['url'],timeout=12,headers={'Referer':page,'User-Agent':'Mozilla/5.0'});response.raise_for_status()
    if len(response.content)>10_000_000 or len(response.content)<2200:raise ValueError('invalid bytes')
    im=Image.open(BytesIO(response.content));im.load()
    if min(im.size)<420 or im.format not in ('JPEG','PNG','WEBP'):raise ValueError('not a usable image')
    name=f'{i:03d}.jpg';im.convert('RGB').save(folder/name,quality=91,optimize=True)
    result.update(status='SOURCE_CANDIDATE_VERIFY_PRODUCT',filename=name,width=im.width,height=im.height,sha256=hashlib.sha256(response.content).hexdigest())
   except Exception as e:result['error']=str(e)[:100]
   return result
  with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
   record['candidate_images']=list(ex.map(dl,list(enumerate(list(found.values())[:110]))))
 except Exception as e:record['status']='PAGE_FAILED';record['error']=str(e)[:150]
 count=sum(x['status']=='SOURCE_CANDIDATE_VERIFY_PRODUCT' for x in record['candidate_images'])
 record['downloaded']=count
 print(slug,'product_id',product_id,'downloaded',count,flush=True)
 (folder/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 return record
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: records=list(ex.map(collect,names.items()))
(root/'audit.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'BATCH22_SOURCE_EVIDENCE_ONLY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.jpg','.json'):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(root/'BATCH22_SOURCE_EVIDENCE_ONLY.zip') as z:assert z.testzip() is None
