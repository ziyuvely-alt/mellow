#!/usr/bin/env python3
"""v2787 two real next steps from v2786:
(A) Correct the last failing GOODAL 50mL Alpha macro crop from already saved
    authentic brand photo pixels, preserving all four other good JPGs by SHA.
(B) Discover verifiable single MINI 5g official CLUBCLIO photo URLs from the
    exact 0000006954 product page, never use 15g set/gifts or old #3 Linen
    overseas color cards. No fabrications or commercial releases.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from io import BytesIO
import requests,hashlib,json,re,base64,shutil,html
QA=Path('qa-review')
P=QA/'v2786-goodal-cream-alpha-photo-crop-visual-fix-QA'
ORIG=QA/'v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA'
OUT=QA/'v2787-goodal-fifth-photo-fix-and-clio-mini-official-source'
assert P.is_dir() and ORIG.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((P/'manifest.json').read_text())
src=json.loads((ORIG/'manifest.json').read_text())
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
good=OUT/'pending-19';good.mkdir()
frames=[]
for f in old['frames']:
 i=f['slot']
 if i==5:continue
 orig=P/f['file'];dest=good/f['file']
 shutil.copy2(orig,dest)
 assert sha(orig)==sha(dest)
 frames.append({'slot':i,'path':str(dest.relative_to(OUT)),'sha256':sha(dest),'exact_previous_bytes':True})
# Crop the real opened cream jar's bowl and capsule texture, avoiding BOTH
# top claim and bottom sentence. Crop is deliberately a macro, not full jar.
source=ORIG/src['curated_photos'][1]['file']
with Image.open(source) as im:
 im.load()
 assert im.size==(1080,1080)
 roi=(425,325,1060,820)
 crop=im.convert('RGB').crop(roi)
 new=ImageOps.fit(crop,(1080,1080),method=Image.Resampling.LANCZOS)
target=good/'05-open-alpha-cream-texture-real-photo-crop-QA.jpg'
new.save(target,'JPEG',quality=94,optimize=True,subsampling=0)
frames.append({'slot':5,'path':str(target.relative_to(OUT)),
 'source':str(source),'source_crop_xyxy':list(roi),
 'description':'Real opened Alpha cream texture macro, not complete jar photo',
 'new_product_pixels_generated':False,'sha256':sha(target),'exact_previous_bytes':False})
assert len(frames)==5
for f in frames:
 p=OUT/f['path']
 with Image.open(p) as im:
  im.load();assert im.size==(1080,1080) and im.format=='JPEG'
 assert p.stat().st_size<2_000_000
 f['bytes']=p.stat().st_size
board=Image.new('RGB',(1830,488),'#f1f0ee')
d=ImageDraw.Draw(board)
d.text((16,16),'v2787 GOODAL PHOTO-ONLY FIVE FRAMES / 4 PRESERVED / LAST ONE TEXT-FREE MACRO CANDIDATE',font=font,fill='#222')
for j,f in enumerate(frames):
 with Image.open(OUT/f['path']) as im:
  thumb=im.convert('RGB').resize((335,335),Image.Resampling.LANCZOS)
 xx=16+j*362
 board.paste(thumb,(xx,68))
 d.text((xx,414),f"FRAME {j+1:02d} "+('NEW REAL MACRO' if j==4 else 'UNCHANGED'),font=font,fill='#262626')
proof=OUT/'goodal-photo-visual-review.jpg'
board.save(proof,'JPEG',quality=83,optimize=True)
(OUT/'goodal-contact.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
# Product image discovery from exact official page. Be deliberately strict:
# no global website imagery and no stale overseas e-commerce editions.
URL='https://clubclio.co.kr/shop/goodsView/0000006954'
clio={'family':'pending-04','official_exact_product_page':URL,
      'product':'CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g',
      'official_net_weight':'5g','source_url_candidates':[],
      'photo_assets_saved':[],'site_access':'NOT_RUN',
      'retail_release':'HOLD_STOCK_OPTIONS_PHOTO_RIGHTS_MK_ORIGINAL',
      'photo_rights_verified':False,
      'identity_warning':'Never substitute new full 15g essential cushion set, gift, or historic #3 Linen overseas pack'}
try:
 r=requests.get(URL,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'ko-KR,ko;q=0.9'},timeout=20)
 r.raise_for_status()
 soup=BeautifulSoup(r.text,'html.parser')
 actual=' '.join(soup.get_text(' ',strip=True).split())
 clio['site_access']=f"HTTP {r.status_code}"
 clio['page_title']=soup.title.get_text(' ',strip=True) if soup.title else None
 clio['exact_product_title_visible']=('메쉬 글로우' in actual and '쿠션 미니' in actual)
 if not clio['exact_product_title_visible']:raise ValueError('Exact official Mini product text not in page')
 urls=[]
 # Product-linked social meta images and structured Product JSON are strong
 # candidates only if the exact product's title is in the JSON schema.
 for meta in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
  u=meta.get('content','')
  if u:urls.append({'url':urljoin(URL,u),'evidence':'PRODUCT_PAGE_META'})
 for el in soup.select('script[type="application/ld+json"]'):
  try:v=json.loads(el.string or el.get_text())
  except (ValueError,TypeError):continue
  for obj in (v if isinstance(v,list) else [v]):
   if not isinstance(obj,dict):continue
   if 'Product' not in str(obj.get('@type','')):continue
   if not ('미니' in str(obj.get('name','')) or 'Mini' in str(obj.get('name',''))):continue
   ims=obj.get('image',[])
   if isinstance(ims,str):ims=[ims]
   for u in ims[:20]:
    if isinstance(u,str):urls.append({'url':urljoin(URL,u),'evidence':'EXACT_PRODUCT_JSON_LD'})
 # Site's HTML product-gallery image src/ lazy attributes with explicit 6954
 for el in soup.find_all('img'):
  for attr in ('data-src','data-original','src','data-lazy-src'):
   u=el.get(attr,'')
   if not u:continue
   tag_alt=(el.get('alt','') or '').lower()
   if '6954' in u or ('메쉬' in tag_alt and '미니' in tag_alt):
    urls.append({'url':urljoin(URL,u),'evidence':'EXACT_PRODUCT_TAG_OR_IMAGE_ID'})
 uniq={}
 for e in urls:
  u=e['url'];parsed=urlparse(u)
  if parsed.scheme!='https' or not parsed.netloc:continue
  if any(x in u.lower() for x in ['logo','sprite','banner','icon','placeholder']):continue
  uniq.setdefault(u,e)
 clio['source_url_candidates']=list(uniq.values())[:30]
 cliodir=OUT/'pending-04';cliodir.mkdir(exist_ok=True)
 headers={'User-Agent':'Mozilla/5.0','Referer':URL}
 for item in clio['source_url_candidates'][:12]:
  try:
   rr=requests.get(item['url'],headers=headers,timeout=12)
   rr.raise_for_status()
   if len(rr.content)>8_000_000:continue
   pic=Image.open(BytesIO(rr.content));pic.load()
   if min(pic.size)<500:continue
   rgb=ImageOps.exif_transpose(pic).convert('RGB')
   # No artificial product pixels; only white letterboxing when needed.
   fitted=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas=Image.new('RGB',(1080,1080),'white')
   canvas.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
   destination=cliodir/f"{len(clio['photo_assets_saved'])+1:02d}-official-page-single-mini-photo-CANDIDATE.jpg"
   canvas.save(destination,'JPEG',quality=91,optimize=True,subsampling=0)
   if destination.stat().st_size>=2_000_000:
    destination.unlink();continue
   clio['photo_assets_saved'].append({'jpg':str(destination.relative_to(OUT)),
     'original_url':item['url'],'source_evidence':item['evidence'],
     'original_size_px':list(pic.size),'JPG_sha256':sha(destination),
     'image_shows_exact_one_mini_object_verified':False,
     'edition_shade_approved':False,'retail_approval':False})
   if len(clio['photo_assets_saved'])>=8:break
  except (OSError,requests.RequestException,ValueError):continue
 clio['status']='SOURCE_PHOTOS_CANDIDATE_QA_REQUIRED' if clio['photo_assets_saved'] else 'NO_VERIFIED_OFFICIAL_SINGLE_PHOTO_DOWNLOADED'
except Exception as e:
 clio['status']='OFFICIAL_PRODUCT_PAGE_OR_GALLERY_ACCESS_BLOCKED'
 clio['error_type']=type(e).__name__;clio['error']=str(e)[:300]
if clio['photo_assets_saved']:
 arr=clio['photo_assets_saved']
 rows=(len(arr)+3)//4
 c=Image.new('RGB',(1500,75+365*rows),'#f0f0ef')
 dr=ImageDraw.Draw(c)
 dr.text((15,13),'v2787 CLIO EXACT 5g OFFICIAL PAGE SOURCE / NOT RETAIL APPROVED',font=font,fill='#262626')
 for i,rec in enumerate(arr):
  with Image.open(OUT/rec['jpg']) as im:thumb=im.convert('RGB').resize((306,306),Image.Resampling.LANCZOS)
  px=14+(i%4)*367;py=60+(i//4)*365
  c.paste(thumb,(px,py))
  dr.text((px,py+315),f"OFFICIAL PAGE CANDIDATE {i+1:02d}",font=font,fill='#303030')
 preview=OUT/'clio-mini-official-candidate-contact.jpg'
 c.save(preview,'JPEG',quality=83,optimize=True)
 (OUT/'clio-contact.b64.txt').write_text(base64.b64encode(preview.read_bytes()).decode())
record={'version':'v2787','baseline':'v2786','date':'2026-11-05',
        'goodal':{'family':'pending-19','actual_five_frames':5,
                  'existing_4_unmodified':True,
                  'photo_frame5':frames[-1],
                  'frames':frames,
                  'photo_license_approved':False,'retail_approved':False},
        'clio':clio,
        'existing_11_approved_families_untouched':True,
        'existing_55_verified_public_URLs_untouched':True,
        'old_QA_art_not_overwritten':True,'final_excel_shared':False}
(OUT/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2787','goodal_photo_frame5_real_crop_saved':True,
 'clio_official_site_status':clio['status'],
 'clio_exact_product_image_candidates_saved':len(clio['photo_assets_saved']),
 'previous_approved_images_changed':0}))
