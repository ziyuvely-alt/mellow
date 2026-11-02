#!/usr/bin/env python3
"""v2421 official detail photo alternatives for 4 recurring public product sets.
Collect only official exact-product gallery images, preserve all live originals.
Not approved for commercial reuse or automatic Shopee replacements.
"""
import csv,json,hashlib,io,re,shutil
from urllib.parse import urljoin,urlparse
from pathlib import Path
from PIL import Image,ImageOps
from bs4 import BeautifulSoup
import requests
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'input-v2421b'
OUT=ROOT/'production-v2421-official-gallery';OUT.mkdir(exist_ok=True)
PRODUCTS={
 'lamelin-miracle-nmn-pdrn-biotox-cream-50ml-sourcephoto-v243-20261101':('https://lamelin.co.kr/product/detail.html?product_no=186','라멜린','CREAM'),
 'lamelin-miracle-nmn-pdrn-biotox-mask-pack-v244-20261101':('https://lamelin.co.kr/product/detail.html?product_no=238','라멜린','MASK PACK'),
 'lamelin-miracle-nmn-pdrn-needle-shot-hair-serum-22-v244-20261101':('https://lamelin.co.kr/product/detail.html?product_no=259','라멜린','HAIR SERUM'),
 'clio-kill-cover-founwear-cushion-original-mini-sourcephoto-v245b-cutout-20261101':('https://clubclio.co.kr/shop/goodsView/0000007108','킬커버','CUSHION MINI')
}
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36','Accept':'text/html,image/jpeg,image/png,image/webp,*/*'}
def sha(s):return hashlib.sha256(s).hexdigest()
def hashphoto(im):
 a=list(ImageOps.grayscale(im.convert('RGB')).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if a[k//8*9+k%8]>a[k//8*9+k%8+1])
def get_urls(html,base):
 s=BeautifulSoup(html,'html.parser')
 candidates=[]
 for tag in s.select('meta[property="og:image"],meta[name="twitter:image"]'):
  if tag.get('content'):candidates.append(urljoin(base,tag['content']))
 for selector in ['#prdDetail img','.keyImg img','.prdImg img','.xans-product-detail img','.xans-product-addimage img','.prod_detail img','.detail_info img']:
  for tag in s.select(selector):
   u=tag.get('data-src') or tag.get('data-original') or tag.get('src')
   if u and not u.startswith('data:'):candidates.append(urljoin(base,u))
 # Main product image has exact product name in alt, not unrelated recommendation.
 for tag in s.select('img[alt]'):
  if any(x in tag.get('alt','') for x in ('NMN+PDRN','미라클 NMN','파운웨어쿠션')):
   u=tag.get('data-src') or tag.get('src')
   if u and not u.startswith('data:'):candidates.append(urljoin(base,u))
 result=[]
 for url in candidates:
  host=(urlparse(url).hostname or '').lower()
  if not url.startswith('https://') or any(x in url.lower() for x in ('logo','icon','header','footer','btn','review','banner','event','recommend','wishlist')):continue
  if not any(x in host for x in ('lamelin.co.kr','cafe24','echosting','clubclio.co.kr')):continue
  if url not in result:result.append(url)
 return result[:30]
records=[];num=0
for family,(page,expected,short) in PRODUCTS.items():
 try:
  resp=requests.get(page,headers=UA,timeout=(10,22));resp.raise_for_status()
  soup=BeautifulSoup(resp.text,'html.parser')
  title=soup.title.get_text(' ',strip=True) if soup.title else ''
  if expected not in title and expected not in soup.get_text(' ',strip=True)[:2000]:
   raise ValueError('PRODUCT_TITLE_NOT_CONFIRMED')
  urls=get_urls(resp.text,resp.url)
 except Exception as e:
  records.append({'family':family,'url':page,'status':'SOURCE_HOLD','raw_sha256':'','jpeg_sha256':'','reason':str(e)[:150]})
  print('PAGE_HOLD',family,str(e)[:90],flush=True);continue
 old=OLD/'originals-immutable/preserved-public-http/images'/family
 olds=[]
 for p in old.glob('*.jpg'):
  with Image.open(p) as im:olds.append(hashphoto(im))
 created=0
 for url in urls:
  if created>=3:break
  try:
   rsp=requests.get(url,headers={**UA,'Accept':'image/*'},timeout=(9,22));rsp.raise_for_status()
   dat=rsp.content
   if len(dat)>12_000_000:raise ValueError('SOURCE_TOO_LARGE')
   with Image.open(io.BytesIO(dat)) as im:
    im.load()
    if im.format not in ('PNG','JPEG','WEBP') or min(im.size)<500:raise ValueError('SMALL_SOURCE')
    ratio=im.width/im.height
    if not 0.48 <= ratio <= 1.9:raise ValueError('BANNER_RATIO')
    h=hashphoto(im)
    if any((h^x).bit_count()<=6 for x in olds):raise ValueError('VISUALLY_REPETITIVE')
    src=ImageOps.exif_transpose(im).convert('RGBA')
    white=Image.new('RGBA',(1080,1080),(255,255,255,255))
    src.thumbnail((990,990),Image.Resampling.LANCZOS)
    white.alpha_composite(src,((1080-src.width)//2,(1080-src.height)//2))
    canvas=white.convert('RGB')
   p=OUT/'official-photo-originals'/family/(sha(dat)[:18]+('.png' if im.format=='PNG' else '.jpg'))
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(dat)
   jpg=OUT/'new-version-photo-candidates'/family/(f'OFFICIAL_DETAIL_{created+1:02d}_V2421.jpg')
   jpg.parent.mkdir(parents=True,exist_ok=True)
   canvas.save(jpg,'JPEG',quality=89,optimize=True)
   assert jpg.stat().st_size<2000000
   with Image.open(jpg) as verify:assert verify.size==(1080,1080) and verify.format=='JPEG'
   records.append({'family':family,'url':url,'status':'CANDIDATE_SOURCE_VERIFIED_QA_PENDING','raw_sha256':sha(dat),'jpeg_sha256':sha(jpg.read_bytes()),'reason':'Exact stock package/copyright/copy design must be checked before production'})
   num+=1;created+=1;olds.append(h)
  except Exception as e:
   records.append({'family':family,'url':url,'status':'SOURCE_HOLD','raw_sha256':'','jpeg_sha256':'','reason':str(e)[:130]})
 print('OFFICIAL_PRODUCT',family,created,'of',len(urls),'URLs evaluated',flush=True)
with (OUT/'official_photo_candidate_qa.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['family','url','status','raw_sha256','jpeg_sha256','reason']);w.writeheader();w.writerows(records)
summary={'v':'2.4.21-official-gallery','public_16_previously_flagged':16,'official_photo_candidates_generated':num,'public_live_urls_changed':0,'public_frame_swaps_final_qa_approved':0,'page_families_checked':4,'logo_original_png_applied':False,'rights_clearance_obtained':False,'note':'Exact brand page vetted; new gallery photo candidates only, no assertion that source provides reuse rights or a different physical inventory edition.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
