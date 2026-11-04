#!/usr/bin/env python3
"""v2691: hard-exclude previous unrelated R.E.D Blemish image; only real
single-unit Dr.G Korea official 50mL product pages. No marketing or kit photos
without exact same-item visible labeling. Retail release stays HOLD.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,hashlib,base64,re
OUT=Path('qa-review/v2691-DRG-correct-Korean-source-only')
assert not OUT.exists();OUT.mkdir(parents=True)
SPEC=[
 {'family':'pending-15','page':'https://www.dr-g.co.kr/item/9637',
  'expected':'그린 마일드 업 선 플러스','forbid':['1+1','기획','선물포장']},
 {'family':'pending-18','page':'https://www.dr-g.co.kr/item/9638',
  'expected':'브라이트닝 업 선 플러스','forbid':['1+1','기획','선물포장']}
]
HEAD={'User-Agent':'Mozilla/5.0','Accept':'text/html,image/avif,image/webp,image/png,image/jpeg,*/*'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(img):
 p=list(ImageOps.grayscale(img.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
rows=[]
for s in SPEC:
 entry={'family':s['family'],'single_item_page':s['page'],
       'status':'HOLD_OFFICIAL_PRODUCT_IMAGE_NOT_CONFIRMED',
       'wrong_red_blemish_candidate_from_v2690_rejected':True,
       'candidate_images':[],'retail_approved':False}
 try:
  response=requests.get(s['page'],headers=HEAD,timeout=16)
  response.raise_for_status()
  response.encoding=response.apparent_encoding or 'utf-8'
  soup=BeautifulSoup(response.text,'html.parser')
  title=soup.title.get_text(' ',strip=True) if soup.title else ''
  ptext=' '.join(el.get_text(' ',strip=True) for el in soup.select('h1,h2,h3')[:20])
  official_identity=(title+' '+ptext)
  entry['official_title']=title
  entry['official_visible_headings']=ptext[:350]
  if s['expected'] not in official_identity:
   raise ValueError('Exact Korean product name not proven on page')
  if not ('50mL' in official_identity or '50ml' in official_identity):
   raise ValueError('50mL capacity not proven from page heading')
  # Only product gallery and main image tags, not general page banners.
  elems=soup.select('.swiper-slide img,.prdImg img,.product-detail img,.product-image img,.item-detail img,.goods-detail img')
  if not elems:
   elems=soup.find_all('img')
  urls=[]
  for el in elems:
   alt=str(el.get('alt') or '')
   attrs=' '.join([str(el.get(k) or '') for k in ('src','data-src','data-original')])
   if not (s['expected'] in alt or (s['expected'].replace(' ','') in alt.replace(' ',''))):
    # Explicit product thumbnail asset classes can be allowed only with same-item alt.
    continue
   for k in ('src','data-src','data-original'):
    v=el.get(k)
    if v and not v.startswith('data:'):
     urls.append(urljoin(s['page'],v))
  entry['same_item_alt_sourced_candidate_urls']=list(dict.fromkeys(urls))[:12]
  chosen=[];chosen_dhash=[]
  for uri in entry['same_item_alt_sourced_candidate_urls']:
   if '/review/' in uri or '/banner/' in uri:continue
   try:
    r=requests.get(uri,headers=HEAD,timeout=12);r.raise_for_status()
    if len(r.content)>7000000:continue
    decoded=Image.open(BytesIO(r.content));decoded.load()
    if min(decoded.size)<350:continue
    im=ImageOps.exif_transpose(decoded).convert('RGB')
    sig=dhash(im)
    if chosen_dhash and min((sig^q).bit_count() for q in chosen_dhash)<14:continue
    chosen.append((im,uri,list(decoded.size)));chosen_dhash.append(sig)
    if len(chosen)==2:break
   except (requests.RequestException,OSError,ValueError):
    continue
  if chosen:
   familydir=OUT/s['family'];familydir.mkdir()
   for n,(img,source,sz) in enumerate(chosen,1):
    result=Image.new('RGB',(1080,1080),'white')
    contained=ImageOps.contain(img,(1040,1040),Image.Resampling.LANCZOS)
    result.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
    dst=familydir/f'{n:02d}-Korean-DrG-exact-50ml-source-only-QA.jpg'
    result.save(dst,'JPEG',quality=92,optimize=True,subsampling=0)
    assert dst.stat().st_size<2000000
    entry['candidate_images'].append({'file':dst.name,'source_url':source,'sha256':digest(dst),'source_dimensions':sz})
   entry['status']='KOREAN_OFFICIAL_EXACT_ITEM_PHOTO_CANDIDATES_STAGED_FOR_VISUAL_EDITION_REVIEW'
  else:entry['status']='HOLD_NO_DECODABLE_EXACT_SAME_ITEM_PHOTO'
 except Exception as exc:
  entry['status']='HOLD_PAGE_OR_ITEM_IDENTITY_VALIDATION'
  entry['error_type']=type(exc).__name__
  entry['error_message']=str(exc)[:220]
 rows.append(entry)
total=sum(len(x['candidate_images']) for x in rows)
if total:
 canvas=Image.new('RGB',(1280,625*len(rows)+75),'#eeeef0')
 d=ImageDraw.Draw(canvas)
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 d.text((18,18),'v2691 DrG KOREAN OFFICIAL 50mL EXACT ITEM ONLY | QA',font=f,fill='black')
 for i,row in enumerate(rows):
  for j,c in enumerate(row['candidate_images']):
   with Image.open(OUT/row['family']/c['file']) as image:
    thumb=image.convert('RGB').resize((500,500),Image.Resampling.LANCZOS)
   x=30+j*610;y=75+i*625
   canvas.paste(thumb,(x,y))
   d.text((x,y+507),row['family']+' / '+str(j+1),font=f,fill='#222222')
 p=OUT/'v2691-source-photo-proof.jpg'
 canvas.save(p,'JPEG',quality=81,optimize=True)
 (OUT/'v2691-contact.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
report={
 'version':'v2691','baseline':'v2690','wrong_previous_red_blemish_candidate_excluded':True,
 'wrong_v2690_new_overseas_package_edition_not_automatically_accepted':True,
 'target_families':2,'actual_exact_product_photo_candidates':total,
 'families':rows,'brand_logo_original_verified':False,
 'photo_publication_rights_verified':False,
 'physical_stock_package_generation_verified':False,
 'new_customer_sale_approved':0,
 'existing_11_sale_approved_unchanged':True,'published_55_urls_unchanged':True,
 'other_30_product_QA_families_untouched':True,'final_xlsx_shared':False
}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'DrG_exact_family_count':len(rows),'same_item_candidate_JPGs':total,
'status':[r['status'] for r in rows],'new_sales_approved':0}))
