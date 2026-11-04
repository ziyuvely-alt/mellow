#!/usr/bin/env python3
"""v2689 product-photo first repair for PIXEL PURE pending29/pending30.
Only images linked to each official same-SKU product page can be used.
Preserve 4/5 previous JPGs byte-for-byte; replace one generic card *only if*
the fetched genuine product image differs perceptually from 2 preexisting photos.
All assets are QA-only, commercial reproduction rights and stock edition HOLD.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,hashlib,shutil,base64,re
BASES={'pending-26':Path('qa-review/v2681-two-eyecleanser-five-frame-qa/pending-26'), 'pending-28':Path('qa-review/v2668-pixelpure-5card-actual-draft')}
OUT=Path('qa-review/v2689-pixelpure-official-photo-candidate-upgrades')
assert all(p.is_dir() for p in BASES.values()) and not OUT.exists()
OUT.mkdir(parents=True)
PRODUCTS=[
 {'family':'pending-26','page':'https://pixelpure.com/product/detail.html?product_no=21',
  'expected_title':'젤투폼 클렌저','correct_volume':'145ml'},
 {'family':'pending-28','page':'https://pixelpure.com/product/detail.html?product_no=23',
  'expected_title':'클렌징 세럼 패드','correct_volume':'70매'},
]def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
def allowed(url):
 host=(urlparse(url).hostname or '').lower()
 return host=='pixelpure.com' or host.endswith('.pixelpure.com') or host.endswith('.cafe24.com') or host.endswith('.cafe24img.com')
headers={'User-Agent':'Mozilla/5.0 (compatible; Product-Image-QA/1.0)','Accept':'text/html,image/avif,image/webp,image/png,image/jpeg,*/*'}
rows=[]
for spec in PRODUCTS:
 fam=spec['family'];original=BASES[fam]
 old=sorted(original.glob('[0-9][0-9]-*.jpg'))
 assert len(old)==5,(fam,len(old))
 result={'family':fam,'official_page':spec['page'],'sale_approved':False,
 'status':'HOLD_SOURCE_PHOTO_PENDING','source_urls_considered':[],
 'four_prior_frames_modified':0,'new_photo_slot':None}
 try:
  response=requests.get(spec['page'],headers=headers,timeout=18)
  response.raise_for_status()
  response.encoding=response.apparent_encoding or 'utf-8'
  html=response.text
  soup=BeautifulSoup(html,'html.parser')
  title=soup.title.get_text(' ',strip=True) if soup.title else ''
  result['official_page_title']=title
  if spec['expected_title'] not in title and spec['expected_title'] not in soup.get_text(' ',strip=True)[:3000]:
   raise ValueError('Product official page title differs from expected same-SKU product')
  # Select images only from official product image metadata and main/gallery elements,
  # never review uploads, related-product carousel or uncertain remote domains.
  candidates=[]
  for m in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
   v=m.get('content')
   if v:candidates.append(urljoin(spec['page'],v))
  for sel in ('.keyImg img','.prdImgView img','#zoomImg','.xans-product-image img',
              'img.BigImage','.thumbnail img','#prdImg img'):
   for tag in soup.select(sel):
    for key in ('src','data-src','data-original','data-zoom'):
     v=tag.get(key)
     if v and not v.startswith('data:'):
      candidates.append(urljoin(spec['page'],v))
  # The standard Cafe24 product-main image path is an additional fallback.
  if not candidates:
   for img in soup.find_all('img'):
    v=img.get('src') or ''
    if '/web/product/big/' in v or '/web/product/medium/' in v:
     candidates.append(urljoin(spec['page'],v))
  uniq=[];seen=set()
  for u in candidates:
   if u.startswith('http') and allowed(u) and u not in seen:
    uniq.append(u);seen.add(u)
  result['source_urls_considered']=uniq[:15]
  with Image.open(old[0]) as img:existing_hashes=[dhash(img.convert('RGB'))]
  with Image.open(old[1]) as img:existing_hashes.append(dhash(img.convert('RGB')))
  selected=None
  for u in uniq[:12]:
   try:
    resp=requests.get(u,headers=headers,timeout=13)
    resp.raise_for_status()
    if len(resp.content)>9_000_000:continue
    image=Image.open(BytesIO(resp.content));image.load()
    if min(image.size)<450:continue
    source=image.convert('RGB')
    candidate_hash=dhash(source)
    distances=[(candidate_hash^x).bit_count() for x in existing_hashes]
    if min(distances)<14:continue
    selected=(source,u,image.size,distances)
    break
   except (requests.RequestException, OSError, ValueError):
    continue
  if selected is None:
   result['status']='HOLD_NO_DISTINCT_VALID_OFFICIAL_PRODUCT_PHOTO'
  else:
   product_photo,url,source_size,distances=selected
   folder=OUT/fam;folder.mkdir()
   # Never crop a retail image. Contain within white square, preserving product proportions.
   square=Image.new('RGB',(1080,1080),'#ffffff')
   contained=ImageOps.contain(product_photo,(1040,1040),Image.Resampling.LANCZOS)
   square.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
   dest=folder/'05-official-product-photo-new-QA-ONLY.jpg'
   square.save(dest,'JPEG',quality=92,optimize=True,subsampling=0)
   persisted=[]
   for p in old:
    slot=int(p.name[:2])
    if slot==5:continue
    target=folder/p.name
    shutil.copy2(p,target)
    assert h(target)==h(p)
    persisted.append({'slot':slot,'sha256':h(target),'file':target.name,'unchanged':True})
   persisted.append({'slot':5,'sha256':h(dest),'file':dest.name,'unchanged':False,
      'official_image_url':url,'official_input_dimensions':list(source_size)})
   for p in folder.glob('*.jpg'):
    with Image.open(p) as img:
     img.load();assert img.format=='JPEG' and img.size==(1080,1080)
    assert p.stat().st_size<2_000_000
   result.update({'status':'NEW_FIVE_JPG_QA_REVISION_BUILT_NOT_RETAIL',
    'prior_four_frames_preserved_exact':True,
    'original_info_frame_replaced':5,'new_photo_slot':5,
    'selected_official_photo_url':url,
    'distinct_phash_distance_existing':distances,
    'files':sorted(persisted,key=lambda x:x['slot'])})
 except Exception as e:
  result['status']='HOLD_OFFICIAL_IMAGE_ACCESS_OR_PRODUCT_IDENTITY'
  result['error_type']=type(e).__name__;result['error_detail']=str(e)[:180]
 rows.append(result)
# One contact image for successfully completed revisions, if any.
successful=[r for r in rows if r.get('new_photo_slot') is not None]
if successful:
 board=Image.new('RGB',(1850,420*len(successful)+76),'#f2f2f2')
 d=ImageDraw.Draw(board)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 d.text((18,13),'v2689 EXACT OFFICIAL PHOTO REPLACEMENTS / QA ONLY',font=font,fill='black')
 for ri,r in enumerate(successful):
  for q in r['files']:
   im=Image.open(OUT/r['family']/q['file']).convert('RGB')
   thumb=im.resize((345,345),Image.Resampling.LANCZOS)
   x=16+(q['slot']-1)*368;y=53+ri*420
   board.paste(thumb,(x,y))
   d.text((x,y+353),r['family']+' '+str(q['slot']),font=font,fill='black')
 p=OUT/'v2689-two-product-photo-preview.jpg'
 board.save(p,'JPEG',quality=81,optimize=True)
 (OUT/'v2689-preview.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
report={'version':'v2689','baseline':'v2687',
 'total_products_checked':len(PRODUCTS),'product_photo_families_upgraded':len(successful),
 'new_sale_approved':0,'existing_11_families_untouched':True,
 'existing_55_public_urls_untouched':True,
 'photo_license_explicitly_verified':False,
 'owned_stock_exact_edition_verified':False,
 'latest_v2647_binary_compared':False,
 'prior_v2680_qa_JPGs_unchanged':True,
 'no_xlsx_shared':True,'products':rows}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'official_pages_checked':len(rows),
 'actual_5JPG_photo_upgraded_sets':len(successful),
 'states':[{'family':r['family'],'status':r['status']} for r in rows],
 'new_sale_approved':0}))
