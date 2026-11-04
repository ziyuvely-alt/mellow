#!/usr/bin/env python3
"""v2692 exact official MISSHA 70mL photo, selective QA candidate frame5 only.
No stock-generation inference; reject 70g Japanese separate edition and unrelated
shop assets. Preserve 4 original JPG SHA bytes without rewriting published images.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,re,json,hashlib,shutil,base64
PREVIOUS=Path("qa-review/v2675-missha-two-five-frame-photo-sets/pending-14")
OUT=Path("qa-review/v2692-missha-pdrn-70ml-official-source-candidate")
assert PREVIOUS.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
URL="https://missha.com/en/m/skincare/product_detail?prdmCd=1081"
headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml,image/jpeg,image/png,*/*'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
report={'version':'v2692','family':'pending-14','product':'MISSHA PDRN NAD+ Firming Repair Cream',
'KR_global_stock_spec':'70mL','Japan_variant_note':'Japanese launch has 70g, not same stock specification',
'official_page':URL,'status':'HOLD_OFFICIAL_IMAGE_NOT_VALIDATED',
'retail_approved':False,'source_license_confirmed':False,
'owned_stock_edition_matched':False,
'approved_11_families_unchanged':True,'public_55_urls_unchanged':True,
'original_4_qa_photos_modified':False,'final_xlsx_shared':False}
try:
 res=requests.get(URL,headers=headers,timeout=18);res.raise_for_status()
 res.encoding=res.apparent_encoding or 'utf-8'
 soup=BeautifulSoup(res.text,'html.parser')
 text=' '.join(soup.stripped_strings)
 title=soup.title.get_text(' ',strip=True) if soup.title else ''
 report['page_title']=title
 identity=(title+' '+text[:6500]).lower()
 if 'firming repair cream' not in identity or not ('70ml' in identity or '70 ml' in identity):
  raise ValueError('Official page must explicitly prove MISSHA firming repair cream 70mL')
 urls=[]
 for m in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
  u=m.get('content')
  if u:urls.append((urljoin(URL,u),'metadata'))
 for im in soup.find_all('img'):
  alt=(im.get('alt') or '').lower()
  attrs=' '.join(str(im.get(k) or '') for k in ('src','class','data-src')).lower()
  # Product key visuals (not blog, review, footer, promotions, recommended).
  if ('pdrn' in alt or 'firming repair' in alt or
      any(x in attrs for x in ['mainimg','product_image','product-img','prdimg','swiper-slide','visualimg'])):
   for k in ('src','data-src','data-original','data-lazy-src'):
    u=im.get(k)
    if u and not u.startswith('data:'):urls.append((urljoin(URL,u),'product_gallery'))
 # A next.js inline JSON data may provide image links when lazy loading omits <img>.
 for u in re.findall(r'https?://[^"<>\\\s]+?\.(?:jpg|jpeg|png|webp)',res.text,re.I)[:40]:
  if 'product' in u or 'prd' in u:urls.append((u,'json_product_image'))
 uniq=[];seen=set()
 for u,kind in urls:
  host=(urlparse(u).hostname or '').lower()
  if not(host=='missha.com' or host.endswith('.missha.com') or
         host.endswith('cloudfront.net') or host.endswith('cafe24img.com') or host.endswith('amazonaws.com')):
   continue
  if u not in seen:
   seen.add(u);uniq.append((u,kind))
 report['candidate_urls_considered']=[x[0] for x in uniq[:20]]
 originals=sorted(PREVIOUS.glob("*.jpg"))
 assert len(originals)==5
 old=[]
 for p in originals[:4]:
  with Image.open(p) as img:old.append(dhash(img.convert('RGB')))
 selected=None
 for u,kind in uniq[:25]:
  try:
   r=requests.get(u,headers=headers,timeout=12);r.raise_for_status()
   if len(r.content)>8000000:continue
   image=Image.open(BytesIO(r.content));image.load()
   if min(image.size)<450:continue
   im=ImageOps.exif_transpose(image).convert('RGB')
   sig=dhash(im)
   dist=[(sig^x).bit_count() for x in old]
   if min(dist)<16:continue
   selected=(im,u,kind,list(image.size),dist)
   break
  except (requests.RequestException,ValueError,OSError):continue
 if selected:
  im,u,kind,sz,dist=selected
  candidate=Image.new('RGB',(1080,1080),'white')
  contained=ImageOps.contain(im,(1040,1040),Image.Resampling.LANCZOS)
  candidate.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
  new=OUT/'05-official-70mL-product-photo-review-only.jpg'
  candidate.save(new,'JPEG',quality=92,optimize=True,subsampling=0)
  previous=[]
  for p in originals[:4]:
   dest=OUT/p.name
   shutil.copy2(p,dest)
   assert sha(p)==sha(dest)
   previous.append({'file':dest.name,'sha256':sha(dest)})
  report.update({'status':'FIVE_JPG_QA_PHOTO_CANDIDATE_BUILT_NEEDS_EYES_ON_ITEM_ID',
   'new_candidate':new.name,'new_photo_sha256':sha(new),
   'official_image_url':u,'official_gallery_source_kind':kind,
   'original_source_dimensions':sz,
   'new_to_old_dhash_distance':dist,
   'four_unchanged_previous_sha256':previous})
  proof=Image.new('RGB',(1810,450),'#eeeeed')
  draw=ImageDraw.Draw(proof)
  for idx,p in enumerate(sorted(OUT.glob('[0-9][0-9]-*.jpg'))):
   with Image.open(p) as image:
    thumb=image.convert('RGB').resize((333,333),Image.Resampling.LANCZOS)
   proof.paste(thumb,(12+idx*360,60))
  f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
  draw.text((15,17),'MISSHA PDRN CREAM 70mL / QA CANDIDATE / NOT APPROVED',fill='#232323',font=f)
  preview=OUT/'v2692-photo-proof.jpg'
  proof.save(preview,'JPEG',quality=81,optimize=True)
  (OUT/'v2692-preview.b64.txt').write_text(base64.b64encode(preview.read_bytes()).decode())
 else:report['status']='HOLD_NO_DISTINCT_OFFICIAL_70ML_IMAGE'
except Exception as e:
 report.update({'status':'HOLD_OFFICIAL_SOURCE_ACCESS_OR_IDENTITY','exception_type':type(e).__name__,'exception_detail':str(e)[:220]})
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2692','status':report['status'],'photo_replacement_staged':bool(report.get('new_candidate')),'retail_approved':0}))
