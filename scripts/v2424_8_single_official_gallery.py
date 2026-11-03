#!/usr/bin/env python3
"""v2.4.24: authentic manufacturer/verified retailer photo candidates for 8 single SKUs.
Output exact-page product-image candidate JPEGs, original SHA conservation, visual similarity evidence.
No commercially unlicensed approval, no guessed MK/packaging, no live asset edits.
"""
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import csv,json,hashlib,shutil,requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input-v2423'
OUT=ROOT/'production-v2424-official-singles'
OUT.mkdir(exist_ok=True)
SPECS={
'pending-09':('https://m.obge.co.kr/product/detail.html?cate_no=1&display_group=7&product_no=1096','오일 컨트롤 피니셔','OBgE Oil Control Finisher 5 g','BRAND_OFFICIAL'),
'pending-22':('https://m.obge.co.kr/product/detail.html?cate_no=1&display_group=7&product_no=1251','맥스 워터풀 선크림','OBgE Max Waterful Sun Cream 300 mL','BRAND_OFFICIAL'),
'pending-24':('https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000233882','프리즈셀 글로우 파워 세럼','BIOHEAL BOH NAD Preezcel Glow Power Serum 30 mL','RETAILER'),
'pending-25':('https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246299','프리즈셀 글로우 부스트 크림','BIOHEAL BOH NAD Preezcel Glow Boost Cream 50 mL','RETAILER'),
'pending-27':('https://www.pixelpure.com/product/detail.html?product_no=24','수딩 앰플 토너','PIXELPURE Soothing Ampoule Toner 200 mL','BRAND_OFFICIAL'),
'pending-28':('https://www.pixelpure.com/product/detail.html?product_no=23','글로우 클렌징 세럼 패드','PIXELPURE Glow Cleansing Serum Pad 70 Pads','BRAND_OFFICIAL'),
'pending-29':('https://pixelpure.com/product/detail.html?product_no=26','아쿠아 수딩 크림','PIXELPURE Aqua Soothing Cream 50 mL','BRAND_OFFICIAL'),
'pending-30':('https://pixelpure.com/product/detail.html?product_no=25','아우라 래디언스 세럼','PIXELPURE Aura Radiance Serum 50 mL','BRAND_OFFICIAL')
}
HEAD={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Accept':'text/html,application/xhtml+xml,image/avif,image/webp,image/png,image/jpeg,*/*'}
def sha(data):return hashlib.sha256(data).hexdigest()
def d_hash(im):
 vals=list(ImageOps.grayscale(im.convert('RGB')).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if vals[(k//8)*9+k%8]>vals[(k//8)*9+k%8+1])
def art(im,path,english_title):
 # This is only source QA candidate, not a fabricated cutout or altered package.
 src=ImageOps.exif_transpose(im).convert('RGBA')
 bg=Image.new('RGBA',(1080,1080),(252,247,239,255))
 src.thumbnail((1020,900),Image.Resampling.LANCZOS)
 bg.alpha_composite(src,((1080-src.width)//2,10+(900-src.height)//2))
 draw=ImageDraw.Draw(bg)
 draw.rectangle((0,936,1080,1080),fill=(232,239,230,255))
 for n in range(29,19,-1):
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
  if draw.textbbox((0,0),english_title,font=font)[2]<985:break
 draw.text((43,978),english_title,fill=(43,63,53,255),font=font)
 bg.convert('RGB').save(path,'JPEG',quality=90,optimize=True)
 with Image.open(path) as chk:
  assert chk.format=='JPEG' and chk.size==(1080,1080)
 assert path.stat().st_size<2_000_000
def gallery_urls(soup,page,source_class):
 imgs=[]
 # Each og:image is intended for EXACT requested product after product title verification.
 for sel in ("meta[property='og:image']","meta[name='twitter:image']"):
  for m in soup.select(sel):
   if m.get('content'):imgs.append(m['content'])
 if source_class=='BRAND_OFFICIAL':
  for img in soup.select('.keyImg img, .thumbnail img, .prdImg img, .xans-product-detail img, .xans-product-addimage img'):
   raw=img.get('data-src') or img.get('data-original') or img.get('src')
   if raw:imgs.append(raw)
 result=[]
 for x in imgs:
  x=urljoin(page,x.strip())
  h=(urlsplit(x).hostname or '').lower()
  if not x.startswith('https://') or any(k in x.lower() for k in ('logo','icon','btn','banner','review','event')):continue
  if source_class=='BRAND_OFFICIAL' and not any(domain in h for domain in ('obge.co.kr','pixelpure.com','cafe24','echosting')):continue
  if source_class=='RETAILER' and 'oliveyoung.co.kr' not in h:continue
  if x not in result:result.append(x)
 return result[:9]
# Preserve EXACT prior 371 + 2 versioned fixes without replating or recompression.
sources=['preserved-v2422','pixelpure-cream-title-revisions','8-single-product-5frame-review']
src_count=0
for dirname in sources:
 p=SRC/dirname
 if not p.exists():continue
 shutil.copytree(p,OUT/'immutable-prev'/dirname,dirs_exist_ok=True)
 for f in p.rglob('*.jpg'):
  copied=OUT/'immutable-prev'/dirname/f.relative_to(p)
  assert sha(f.read_bytes())==sha(copied.read_bytes())
  src_count+=1
records=[];family_status=[];created=0
for fid,(page,expected,title,source_type) in SPECS.items():
 capture=0;urls=[];verified=False
 try:
  resp=requests.get(page,headers=HEAD,timeout=(9,22));resp.raise_for_status()
  soup=BeautifulSoup(resp.text,'html.parser')
  titletext=(soup.title.get_text(' ',strip=True) if soup.title else '')
  for meta in soup.select("meta[property='og:title'], meta[name='description']"):
   titletext+=' '+meta.get('content','')
  visible=soup.get_text(' ',strip=True)[:3500]
  verified=expected.replace(' ','') in (titletext+' '+visible).replace(' ','')
  if not verified:raise ValueError('PRODUCT_TITLE_NOT_EXACT_MATCH')
  urls=gallery_urls(soup,resp.url,source_type)
 except Exception as e:
  records.append({'family':fid,'url':page,'state':'PAGE_HOLD','source_sha':'','jpg_sha':'','reason':str(e)[:130]})
 current=list((SRC/'8-single-product-5frame-review'/fid).glob('*.jpg'))
 existing_hashes=[]
 for orig in current:
  try:
   with Image.open(orig) as im:existing_hashes.append(d_hash(im))
  except:pass
 for url in urls:
  if capture>=2:break
  try:
   r=requests.get(url,headers={**HEAD,'Accept':'image/*'},timeout=(8,20));r.raise_for_status()
   raw=r.content
   if len(raw)>12_000_000:raise ValueError('SIZE_LIMIT')
   with Image.open(BytesIO(raw)) as im:
    im.load()
    if im.format not in ('JPEG','PNG','WEBP') or min(im.size)<450:raise ValueError('SMALL_OR_UNSUPPORTED')
    ratio=im.width/max(1,im.height)
    if not .48<=ratio<=1.85:raise ValueError('BANNER_OR_STRIP')
    ph=d_hash(im)
    if any((ph^old).bit_count()<=6 for old in existing_hashes):raise ValueError('VISUAL_REPEAT')
    srcpath=OUT/'authentic-photo-originals'/fid/(sha(raw)[:19]+'.'+('png' if im.format=='PNG' else 'jpg'))
    srcpath.parent.mkdir(parents=True,exist_ok=True);srcpath.write_bytes(raw)
    candidate=OUT/'new-independent-photo-candidates'/fid/f'PRODUCT_PHOTO_{capture+1:02d}_V2424.jpg'
    candidate.parent.mkdir(parents=True,exist_ok=True)
    art(im,candidate,title)
   created+=1;capture+=1;existing_hashes.append(ph)
   records.append({'family':fid,'url':r.url,'state':'PHOTO_CANDIDATE_RELEASE_HOLD','source_sha':sha(raw),'jpg_sha':sha(candidate.read_bytes()),'reason':'Brand/product page confirmed; exact stock photo contents and commercial reuse rights not cleared'})
  except Exception as e:
   records.append({'family':fid,'url':url,'state':'PHOTO_REJECTED','source_sha':'','jpg_sha':'','reason':str(e)[:140]})
 family_status.append({'family':fid,'name':title,'product_title_verified':verified,'source_class':source_type,'found_new_unique_photo_candidates':capture,'stock_package_verified':False,'commercial_reuse_verified':False,'ready_except_logo':False,'state':'SOURCE_QA_HOLD'})
 print('FAMILY',fid,'page',verified,'new_distinct_photo',capture,flush=True)
def csvout(name,items,cols):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(items)
csvout('photo_candidates_source_url_SHA.csv',records,['family','url','state','source_sha','jpg_sha','reason'])
csvout('eight_products_fact_and_rights_gates.csv',family_status,['family','name','product_title_verified','source_class','found_new_unique_photo_candidates','stock_package_verified','commercial_reuse_verified','ready_except_logo','state'])
summary={'version':'2.4.24','eight_single_sku_source_pages_checked':8,'eight_single_original_5frame_sets_preserved':8,'prior_371_jpg_preserved':371,'prior_v2423_2_edits_preserved':2,'all_staged_prior_jpg_sha_preserved':src_count,'official_product_title_verified':sum(x['product_title_verified'] for x in family_status),'new_independent_product_photo_candidate_jpg':created,'product_photo_copyright_cleared':0,'stock_package_exactly_matched':0,'ready_except_logo':0,'production_complete_qa_pending':0,'final_qa_approved':0,'mk_original_binary_recovered':False,'official_color_chart_complete':0,'live_public_55_urls_changed':0,'note':'Source-side authentic product photography candidates, cannot be sold until package and commercial usage rights reviewed. Official page product name checked for each candidate; no other product/photo taken.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
