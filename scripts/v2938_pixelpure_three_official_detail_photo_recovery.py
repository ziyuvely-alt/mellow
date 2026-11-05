from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha256
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps
from bs4 import BeautifulSoup
import requests,re,json,time
Q=Path('qa-review');OLD=Q/'v2929-pixelpure-three-four-photo-pack-source-integrity-QA';PRE=Q/'v2937-goodal-serummist-100ml-two-unique-action-and-still-photo-source-QA';OUT=Q/'v2938-pixelpure-three-official-detail-product-scene-recovery-QA'
assert not OUT.exists()
prev=json.loads((OLD/'manifest.json').read_text());state=json.loads((PRE/'stock30-incremental-state-v2937.json').read_text())
assert prev['version']=='v2929' and state['version']=='v2937' and len(state['families'])==30
cases=[('pending-27',24,['수딩','앰플','토너']),('pending-29',26,['아쿠아','수딩','크림']),('pending-30',25,['아우라','래디언스','세럼'])]
by={r['family']:r for r in prev['results']};session=requests.Session();session.headers['User-Agent']='Mozilla/5.0 (noncommercial product image audit)'
def dh(im):
 p=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load();return ''.join('1' if p[x,y]>p[x+1,y] else '0' for y in range(8) for x in range(8))
def dist(x,y):return sum(a!=b for a,b in zip(x,y))
def reference(fam):
 x=by[fam];zpath=Path(x['archive_ZIP']);assert sha256(zpath.read_bytes()).hexdigest()==x['archive_ZIP_sha256'];h=[];ss=set()
 with ZipFile(zpath) as z:
  assert z.testzip() is None and len(z.namelist())==4
  for n in z.namelist():
   b=z.read(n);ss.add(sha256(b).hexdigest())
   with Image.open(BytesIO(b)) as im:h.append(dh(im.convert('RGB')))
 return ss,h
def qualify(raw,page):
 if not isinstance(raw,str):return None
 u=urljoin(page,raw.strip().replace('&amp;','&'));p=urlparse(u)
 if p.scheme!='https' or p.hostname not in ('ecimg.cafe24img.com','www.pixelpure.com','pixelpure.com'):return None
 if not re.search(r'\.(jpg|jpeg|png|webp)(\?|$)',u,re.I):return None
 if any(a in p.path.lower() for a in ('/banner/','/review/','/icon/','/logo/')):return None
 return u
OUT.mkdir(parents=True);results=[]
for fam,product_no,tokens in cases:
 page=f'https://www.pixelpure.com/product/detail.html?product_no={product_no}';errors=[];urls=[];valid=False;names=[];scopes=[]
 try:
  r=session.get(page,timeout=17);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
  names=[x.get('content','') if x.name=='meta' else x.get_text(' ',strip=True) for x in soup.select('meta[property="og:title"],.infoArea h2,.headingArea h2,.prdName,h1')[:15]]
  normalized=re.sub(r'\s+','',' '.join(names)).lower();valid=all(t in normalized for t in tokens)
  if valid:
   for selector in ('#prdDetail','#prdDetailContent','.prdDetail','.prd_detail','.detail_cont','#product_detail'):
    for region in soup.select(selector)[:2]:
     scopes.append(selector)
     for img in region.select('img')[:120]:
      for field in ('data-src','data-original','src','data-large'):
       u=qualify(img.get(field),page)
       if u and u not in urls:urls.append(u)
     for raw in re.findall(r'(?:https?:)?//ecimg\.cafe24img\.com/[^"\'<>\s)]+\.(?:jpg|png|webp)',str(region))[:100]:
      u=qualify(raw if raw.startswith('https') else 'https:'+raw,page)
      if u and u not in urls:urls.append(u)
  else:errors.append('exact manufacturer heading not verified')
 except Exception as e:errors.append('page: '+str(e)[:180])
 oldsha,oldhash=reference(fam);photos=[];excluded=0
 for u in urls[:40]:
  if len(photos)>=4:break
  try:
   r=session.get(u,timeout=14);r.raise_for_status();assert urlparse(r.url).hostname in ('ecimg.cafe24img.com','www.pixelpure.com','pixelpure.com')
   data=r.content;assert 5000<len(data)<10_000_000
   im=Image.open(BytesIO(data));im.load();assert im.format in ('JPEG','PNG','WEBP')
   rgb=ImageOps.exif_transpose(im).convert('RGB');w,h=rgb.size
   if min(w,h)<900 or max(w,h)/min(w,h)>1.65:excluded+=1;continue
   sha=sha256(data).hexdigest();ph=dh(rgb)
   if sha in oldsha or any(z['sha256']==sha for z in photos) or min([dist(ph,p) for p in oldhash+[z['_hash'] for z in photos]],default=64)<5:
    excluded+=1;continue
   folder=OUT/fam;folder.mkdir(exist_ok=True);native=folder/f'{len(photos)+1:02d}-official-detail-original.{im.format.lower()}';native.write_bytes(data)
   sq=Image.new('RGB',(1080,1080),'white');fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS);sq.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   qa=folder/f'{len(photos)+1:02d}-photo-reference-1080.jpg';sq.save(qa,'JPEG',quality=90,optimize=True)
   photos.append({'source_url':u,'source_path':str(native),'reference':str(qa),'sha256':sha,'reference_sha256':sha256(qa.read_bytes()).hexdigest(),'native_px':[w,h],'stock_edition_verified':False,'photo_rights_verified':False,'claims_reviewed':False,'retail_approved':False,'_hash':ph})
  except Exception as e:errors.append('candidate '+u.split('/')[-1][:30]+': '+str(e)[:110])
 state['families'][fam].update({'last_delta_version':'v2938','release_status':'OFFICIAL_PRODUCT_DETAIL_REFERENCES_NEED_VISUAL_QA' if photos else 'OFFICIAL_PRODUCT_DETAIL_SCANNED_NO_NEW_SOURCE','v2938_new_detail_photo_refs':len(photos),'sale_approved':False,'latest_photo_QA_checkpoint':f'v2938 manufacturer detail page #{product_no} verified={valid}, {len(urls)} source links, {len(photos)} candidate images, {excluded} duplicates/size rejects. Stock, rights and claims HOLD.'})
 results.append({'family':fam,'product_no':product_no,'exact_product_page_confirmed':valid,'page_title_evidence':names,'detail_scopes':list(dict.fromkeys(scopes)),'candidate_urls_examined':len(urls),'new_refs':[{k:v for k,v in x.items() if not k.startswith('_')} for x in photos],'excluded_duplicates_or_dimensions':excluded,'errors':errors[:15]})
report={'version':'v2938','baseline':'v2937','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'official_products_checked':3,'new_provisional_native_photo_sources':sum(len(x['new_refs']) for x in results),'total_detail_photo_urls':sum(x['candidate_urls_examined'] for x in results),'old_11_published_families_unchanged':True,'old_55_public_urls_unchanged':True,'old_source_pixels_unchanged':True,'new_sale_approvals':0,'new_public_urls':0,'final_spreadsheet_shared':False,'results':results}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');state.update({'version':'v2938','baseline':'v2937','new_sales_approvals':0,'new_public_URLs':0,'final_spreadsheet_shared':False});(OUT/'stock30-incremental-state-v2938.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2938','new_refs':report['new_provisional_native_photo_sources'],'detail_urls':report['total_detail_photo_urls'],'by_family':{x['family']:len(x['new_refs']) for x in results}}))