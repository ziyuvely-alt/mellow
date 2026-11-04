#!/usr/bin/env python3
"""v2741: ONE new source-quality pass for previously held pending-09 5g OBgE
Oil Control Finisher. Manufacturer storefront original gallery ONLY.

We already have 5 old QA JPGs but the old usable product cutout contains only
274x269 real product pixels. No enlargement to claim a high-res source.
No web search loops, no old assets overwritten, no retail image releases.
Copyright/resharing rights are not presumed from manufacturer listing.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse,urljoin
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,base64,requests,re,html
from bs4 import BeautifulSoup
OUT=Path('qa-review/v2741-obge-finisher-5g-firstparty-original-resolution-QA')
assert not OUT.exists();OUT.mkdir(parents=True)
PAGE='https://obgeglobal.com/products/oil-control-finisher'
HEAD={'User-Agent':'Mozilla/5.0 (compatible; StockPhotoQA/1.0)','Accept':'text/html,application/json,image/*,*/*'}
def hashdata(d):return hashlib.sha256(d).hexdigest()
def is_real_manufacturer_photo(url):
 host=(urlparse(url).hostname or '').lower()
 return host in ('obgeglobal.com','www.obgeglobal.com') and '/cdn/shop/' in urlparse(url).path
report={
 'version':'v2741','family':'pending-09','product':'OBgE Oil Control Finisher 5g',
 'manufacturer_listing':PAGE,'source_kind':'first_party_MANUFACTURER_SHOPIFY_gallery',
 'old_usable_object_resolution':[274,269],
 'new_candidate_sources':[],'discarded':[],
 'same_product_exact_single_unit_5g_stock_verified':False,
 'photo_commercial_rights_verified':False,'original_MK_logo_verified':False,
 'retail_approved':False,'previous_photo_sources_modified':False,
 'old_11_approved_groups_unchanged':True,'old_55_public_URLs_unchanged':True,
 'final_XLSX_shared':False}
candidates=[];seen=set()
def add(src,method):
 if not src or not isinstance(src,str):return
 url=urljoin(PAGE,html.unescape(src).replace('\\/','/'))
 if not url.startswith('https://'):return
 if not is_real_manufacturer_photo(url):return
 # Remove width= and /cdn/shop/files/... resize params only. Manufacturer original retains ?v=.
 url=re.sub(r'[&?]width=\d+','',url)
 if url not in seen:
  seen.add(url);candidates.append({'url':url,'method':method})
try:
 resp=requests.get(PAGE+'.js',headers=HEAD,timeout=18)
 if resp.ok:
  data=resp.json()
  if not all(t in str(data.get('title','')).lower() for t in ('oil','control','finisher')):
   raise ValueError('Manufacturer Shopify JSON wrong product')
  report['manufacturer_product_name']=data.get('title')
  report['manufacturer_variants']=[x.get('title') for x in data.get('variants',[])[:8]]
  for item in data.get('images',[])[:22]:
   add(item if isinstance(item,str) else item.get('src'),'official_product_json')
 else:report['json_access_status']=resp.status_code
except Exception as e:report['json_error']=type(e).__name__+': '+str(e)[:120]
if not candidates:
 try:
  r=requests.get(PAGE,headers=HEAD,timeout=17);r.raise_for_status()
  soup=BeautifulSoup(r.text,'html.parser')
  txt=soup.title.get_text(' ',strip=True) if soup.title else ''
  assert 'Oil Control Finisher' in txt,txt
  report['manufacturer_page_title']=txt
  # Don't include recommendation carousel images. Prefer main og:image and files found
  # in page product media structured data, then use the known manufacturer URL.
  for meta in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
   add(meta.get('content'),'official_meta_image')
  for match in re.findall(r'(?:https?:)?//obgeglobal\.com/cdn/shop/files/[^"\'\s<>]+?\.(?:png|jpe?g|webp)(?:\?v=\d+)?',r.text,re.I):
   add(match,'official_page_embedded_media')
 except Exception as e:report['html_error']=type(e).__name__+': '+str(e)[:180]
# Exact first-party gallery image, visually verified externally as same product:
add('https://obgeglobal.com/cdn/shop/files/83.png?v=1776049524','manufacturer_product_gallery_identified')
usable=[];hashes=set()
for item in candidates[:22]:
 u=item['url']
 try:
  res=requests.get(u,headers=HEAD,timeout=13)
  res.raise_for_status()
  if len(res.content)>8_000_000:raise ValueError('source>8MB')
  with Image.open(BytesIO(res.content)) as origin:
   origin.load()
   source_width,source_height=origin.size
   if min(origin.size)<400:raise ValueError('source<400px')
   rgb=ImageOps.exif_transpose(origin).convert('RGB')
   native_sha=hashdata(res.content)
   if native_sha in hashes:continue
   hashes.add(native_sha)
   # Actual source pixels preserved, no false enlargement for 'high-resolution'.
   # Render 1080 only if source can support 900 pixels in each dimension.
   if min(origin.size)<900:
    report['discarded'].append({'url':u,'reason':'NATIVE_SOURCE_BELOW_900PX','native_px':list(origin.size)})
    continue
   thumb=ImageOps.contain(rgb,(1040,1040),Image.Resampling.LANCZOS)
   card=Image.new('RGB',(1080,1080),'#ffffff')
   card.paste(thumb,((1080-thumb.width)//2,(1080-thumb.height)//2))
   num=len(usable)+1
   name=f'{num:02d}-MANUFACTURER-real-source-1080-QA.jpg'
   jpg=OUT/name
   card.save(jpg,'JPEG',quality=92,optimize=True,subsampling=0)
   assert jpg.stat().st_size<2_000_000
   usable.append({'index':num,'file':name,'url':u,
     'source_origin_px':[source_width,source_height],
     'original_sha256':native_sha,'file_sha256':hashdata(jpg.read_bytes()),
     'jpg_bytes':jpg.stat().st_size,'source_method':item['method'],
     'source_is_manufacturer_domain':True,'commercial_permission_verified':False,
     'product_single_5g_visual_review':'REQUIRED'})
   if len(usable)>=8:break
 except Exception as e:
  report['discarded'].append({'url':u,'reason':type(e).__name__+':'+str(e)[:100]})
report['new_candidate_sources']=usable
report['native_high_resolution_source_count']=len(usable)
report['status']='GALLERY_NATIVE_SOURCE_CANDIDATES_VISUAL_QA_PENDING' if usable else 'HOLD_NO_NATIVE_GE_900_SOURCE'
if usable:
 F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 font=ImageFont.truetype(F,24)
 rows=(len(usable)+3)//4
 board=Image.new('RGB',(1820,75+rows*420),'#f0f0ef')
 d=ImageDraw.Draw(board)
 d.text((16,15),'v2741 OBgE 5g | REAL FIRST-PARTY PHOTO GALLERY | NOT RETAIL CLEARED',font=font,fill='#242424')
 for i,x in enumerate(usable):
  with Image.open(OUT/x['file']) as im:pic=im.convert('RGB').resize((339,339),Image.Resampling.LANCZOS)
  xx=15+(i%4)*451;yy=59+(i//4)*420
  board.paste(pic,(xx,yy))
  d.text((xx,yy+347),f"{x['index']:02d} NATIVE {x['source_origin_px'][0]}px",font=font,fill='#333333')
 proof=OUT/'v2741-firstparty-highres-contact.jpg'
 board.save(proof,'JPEG',quality=82,optimize=True)
 (OUT/'v2741-proof.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2741','first_party_native_ge900_JPGs':len(usable),
 'status':report['status'],'no_sale_approvals':True}))
