#!/usr/bin/env python3
"""v2816: source-only discovery of genuinely additional 5g 23N single mini photos.
Previously saved CLIO original mini 5g first-party thumbnails remain byte-identical.
Shopify product JSON/API -> page alt gallery fallback. No commercial rights assumed.
All candidates must belong to Sasa 110722304011 exact item, not recommendations.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
import requests,hashlib,json,re,base64
ROOT=Path('qa-review')
PRE=ROOT/'v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof'/'pending-05'
OUT=ROOT/'v2816-clio-original-mini-5g-23N-real-single-unit-source'
assert PRE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
FIRST_PARTY=[
 PRE/'03-official-7108-m-gif-REFERENCE.jpg',
 PRE/'04-official-7108-b-gif-REFERENCE.jpg',
]
for p in FIRST_PARTY: assert p.is_file()
URL='https://www.sasa.com/products/110722304011'
HEAD={'User-Agent':'Mozilla/5.0','Accept':'text/html,image/avif,image/webp,image/jpeg,image/png,*/*'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
candidates=[]
sources=[]
def add(u,origin):
 if not u:return
 if u.startswith('//'):u='https:'+u
 u=urljoin(URL,u.replace('&amp;','&'))
 netloc=(urlparse(u).netloc or '').lower()
 if not any(x in netloc for x in ('shopify.com','sasa.com','91app.hk')):return
 if re.search(r'\.(?:svg|gif)(?:\?|$)',u,re.I):return
 # Shopify resizing requests may include width; do not construct URLs.
 if u not in {x['url'] for x in candidates}:candidates.append({'url':u,'origin':origin})
try:
 r=requests.get(URL+'.js',headers=HEAD,timeout=16)
 if r.ok:
  obj=r.json()
  assert 'original' in str(obj.get('title','')).lower() and 'mini' in str(obj.get('title','')).lower()
  for v in obj.get('images',[]): add(v['src'] if isinstance(v,dict) else v,'shopify_exact_product_json')
  sources.append({'api':URL+'.js','status':r.status_code,'title':obj.get('title'),'count':len(obj.get('images',[]))})
 else:sources.append({'api':URL+'.js','status':r.status_code})
except Exception as exc:sources.append({'api':URL+'.js','error':str(exc)[:170]})
if len(candidates)<3:
 try:
  r=requests.get(URL,headers=HEAD,timeout=17);r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser')
  title=soup.title.get_text(' ',strip=True) if soup.title else ''
  assert 'clio' in title.lower() and ('23n' in title.lower() or 'original mini' in title.lower()),title
  matched=0
  for im in soup.find_all('img'):
   alt=(im.get('alt') or '').lower()
   if 'clio' not in alt or 'original' not in alt or 'mini' not in alt or '23n' not in alt:continue
   matched+=1
   for k in ('data-src','data-original','src'):
    if im.get(k):add(im.get(k),'exact_product_img_alt')
   for k in ('srcset','data-srcset'):
    if im.get(k):
     for part in im[k].split(','):
      unit=part.strip().split()[0] if part.strip() else None
      if unit:add(unit,'exact_product_img_alt_srcset')
  sources.append({'page':URL,'status':r.status_code,'title':title,'matched_image_alts':matched})
 except Exception as exc:sources.append({'page':URL,'error':str(exc)[:200]})
manifest={'version':'v2816','baseline':'v2815','family':'pending-05',
'product':'CLIO Kill Cover Founwear Cushion The Original Mini 5g',
'Korean_first_party_page':'https://clubclio.co.kr/shop/goodsView/0000007108',
'Korean_first_party_option_labels':['21N','23N'],
'independent_single_23N_5g_listing':URL,
'independent_store_23N_single':'TRUE_PER_PRODUCT_PAGE',
'first_party_reference_files_hash_preserved':[{ 'path':str(p),'sha256':sha(p)} for p in FIRST_PARTY],
'fetch_evidence':sources,'candidate_links_discovered':len(candidates),'candidate_images':[],
'new_distinct_real_source_photos_staged':0,
'sales_approval':False,'actual_owned_stock_edition_verified':False,
'image_commercial_reuse_rights_verified':False,'original_MK_logo_verified':False,
'prior_11_published_families_untouched':True,'prior_55_published_URLs_untouched':True,
'prior_QA_JPGs_untouched':True,'final_excel_shared':False}
seen=set()
for x in candidates[:40]:
 if len(manifest['candidate_images'])>=5:break
 try:
  r=requests.get(x['url'],headers=HEAD,timeout=12)
  r.raise_for_status()
  assert 6000<len(r.content)<8_000_000
  image=Image.open(BytesIO(r.content));image.load()
  if min(image.size)<350:continue
  rgb=ImageOps.exif_transpose(image).convert('RGB')
  sample=rgb.resize((16,16),Image.Resampling.LANCZOS)
  fingerprint=hashlib.sha256(sample.tobytes()).hexdigest()
  if fingerprint in seen:continue
  seen.add(fingerprint)
  slot=len(manifest['candidate_images'])+1
  target=OUT/f'{slot:02d}-original-sasa-23N-5g-photo-1080-QA.jpg'
  full=Image.new('RGB',(1080,1080),'white')
  fit=ImageOps.contain(rgb,(1050,1050),Image.Resampling.LANCZOS)
  full.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  full.save(target,'JPEG',quality=92,optimize=True,subsampling=0)
  assert target.stat().st_size<2_000_000
  manifest['candidate_images'].append({
   'slot':slot,'source_url':x['url'],'source_from':x['origin'],
   'native_dimensions':list(image.size),'preview_file':target.name,
   'JPG_sha256':sha(target),'JPG_bytes':target.stat().st_size,
   'single_23N_5g_listing_source':True,
   'claim_of_photo_reuse_license':False,
   'real_user_owned_stock_edition_proven':False,
   'visual_single_product_approval':'PENDING_QA'})
 except Exception:continue
manifest['new_distinct_real_source_photos_staged']=len(manifest['candidate_images'])
manifest['state']='SOURCE_QA_STAGED_NEED_VISUAL_REVIEW' if manifest['candidate_images'] else 'HOLD_NO_FETCHABLE_NEW_GALLERY'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
listings=[(p,'OFFICIAL 7108 '+str(i)) for i,p in enumerate(FIRST_PARTY,1)]
listings+= [(OUT/a['preview_file'],'SASA 23N '+str(a['slot'])) for a in manifest['candidate_images']]
width=1850
rows=(len(listings)+3)//4
board=Image.new('RGB',(width,85+440*rows),'#efeeec')
d=ImageDraw.Draw(board)
d.text((14,14),'v2816 EXACT 5g MINI / ORIGINAL 7108 OFFICIAL vs SASA 23N SINGLE PHOTO / QA HOLD',font=font,fill='#262626')
for i,(path,label) in enumerate(listings):
 x=12+(i%4)*458;y=60+(i//4)*440
 with Image.open(path) as image:
  tile=image.convert('RGB').resize((375,375),Image.Resampling.LANCZOS)
 board.paste(tile,(x,y))
 d.text((x,y+383),label,font=font,fill='#303030')
proof=OUT/'v2816-official-vs-new-sasa-photo-review.jpg'
board.save(proof,'JPEG',quality=84,optimize=True)
(OUT/'v2816-proof.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode('ascii'))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2816','new_real_images':manifest['new_distinct_real_source_photos_staged'],'state':manifest['state'],'commercial_approved':0}))
