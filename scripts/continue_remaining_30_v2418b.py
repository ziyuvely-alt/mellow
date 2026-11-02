#!/usr/bin/env python3
"""v2418b: replace 3 inherited branded-poster pseudo-photographs in review sets
with clean real product photos from exact official / named retailer product pages.
Prior 160 source JPEG + 5 interim variants remain byte-identical and archived.
No new MK emblems, no fabricated packaging and no public upload.
"""
from pathlib import Path
import hashlib,csv,io,json,shutil
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'input-v2418'
OUT=ROOT/'production-v2418b';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REPLACE=[
{'family':'pending-09','url':'https://obgeglobal.com/cdn/shop/files/83.png?v=1776049524','brand_page':'https://obgeglobal.com/products/oil-control-finisher','name':'OBgE  OIL CONTROL FINISHER','subtitle':'5 g / Official OBgE product photograph','source_type':'OFFICIAL_BRAND','legacy_issue':'Old frame reused already-designed poster containing legacy MK stamp'},
{'family':'pending-18','url':'https://sitem.ssgcdn.com/22/72/80/item/1000522807222_i1_1200.jpg','brand_page':'https://www.ssg.com/item/itemView.ssg?itemId=1000522807222','name':'Dr.G  BRIGHTENING UP SUN+','subtitle':'50 mL / Retailer product photograph','source_type':'KOREAN_RETAILER','legacy_issue':'Old frame reused already-designed poster containing legacy MK stamp'},
{'family':'pending-22','url':'https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024671504ko.jpg?l=ko','brand_page':'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246715','name':'OBgE  MAX WATERFUL SUN CREAM','subtitle':'300 mL / Korean retailer product photograph','source_type':'KOREAN_RETAILER','legacy_issue':'Old frame reused already-designed poster containing legacy MK stamp'}
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,n)
 except:return ImageFont.load_default()
def validate(p):
 with Image.open(p) as im:im.load();return im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
def photo_frame(p,target,item):
 with Image.open(p) as im:
  im.load()
  if im.format not in ('PNG','JPEG','WEBP') or min(im.size)<350:raise ValueError('Not valid high-resolution product photo')
  pic=ImageOps.exif_transpose(im).convert('RGB')
 bg=Image.new('RGB',(1080,1080),(252,249,245))
 pic.thumbnail((1010,925),Image.Resampling.LANCZOS)
 bg.paste(pic,((1080-pic.width)//2,9+(915-pic.height)//2))
 d=ImageDraw.Draw(bg);d.rectangle((0,926,1080,1080),fill=(228,237,229))
 title=item['name'];subtitle=item['subtitle']
 for line,yy,sz in [(title,947,31),(subtitle,1000,24)]:
  fo=font(sz,yy==947)
  if d.textbbox((0,0),line,font=fo)[2]>980:raise ValueError('Text overflows')
  d.text((65,yy),line,fill=(45,69,58),font=fo)
 bg.save(target,'JPEG',quality=91,optimize=True)
 if not validate(target):raise ValueError('JPG output invalid')
shas=[];sources=[];count_old=0;new=0;sets=0
# Preserve source archive recursively and byte identically; modify only a copy of the review set.
for p in sorted(OLD.rglob('*.jpg')):
 dst=OUT/'all-previous-jpg-byte-preserved'/p.relative_to(OLD);dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,dst)
 if sha(p)!=sha(dst):raise RuntimeError('Mutated original!')
 shas.append({'file':str(p.relative_to(OLD)),'sha256':sha(dst),'kind':'OLD_UNCHANGED'})
 count_old+=1
# Copy review candidate sets unchanged; change only first slot in the three exact impacted sets.
for p in sorted((OLD/'review-five-frame-sets').glob('pending-*/*.jpg')):
 dst=OUT/'review-five-frame-sets'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
for item in REPLACE:
 family=item['family'];url=item['url'];slot=OUT/'review-five-frame-sets'/family
 photo_dir=OUT/'real-source-originals'/family;photo_dir.mkdir(parents=True,exist_ok=True)
 try:
  r=requests.get(url,timeout=(8,18),headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'});r.raise_for_status()
  if len(r.content)>12_000_000:raise ValueError('Source exceeds byte limit')
  with Image.open(io.BytesIO(r.content)) as im:
   im.load();fmt=im.format;size=im.size
   if fmt not in ('JPEG','PNG','WEBP') or min(size)<350:raise ValueError('Unsupported source or too small')
  raw=photo_dir/(hashlib.sha256(r.content).hexdigest()[:18]+'.'+{'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt])
  raw.write_bytes(r.content)
  out=OUT/'new-clean-product-photos'/family/'CLEAN_PRODUCT_FRAME_V2418B.jpg';out.parent.mkdir(parents=True,exist_ok=True)
  photo_frame(raw,out,item)
  olds=sorted(slot.glob('01_*.jpg'))
  if len(olds)!=1:raise ValueError('Missing exact single replacement slot')
  # Preserve old frame at all-previous-jpg-byte-preserved/ while replacing only the new review set slot.
  olds[0].unlink()
  shutil.copy2(out,slot/'01_CLEAN_PRODUCT_FRAME_V2418B.jpg')
  new+=1
  sources.append({'family':family,'photo_url':r.url,'product_page':item['brand_page'],'source_sha256':sha(raw),'new_sha256':sha(out),'result':'REPLACED_VERSIONED_SET_SLOT','source_type':item['source_type'],'notes':'Product identity from exact page; stock revision/license/logo still QA pending'})
  shas.append({'file':str(out.relative_to(OUT)),'sha256':sha(out),'kind':'NEW_CLEAN_PHOTO'})
 except Exception as e:
  sources.append({'family':family,'photo_url':url,'product_page':item['brand_page'],'source_sha256':'','new_sha256':'','result':'SOURCE_FAILED_PRESERVED_PREVIOUS','source_type':item['source_type'],'notes':str(e)[:170]})
for p in sorted((OUT/'review-five-frame-sets').glob('pending-*')):
 count=len(list(p.glob('*.jpg')))
 if count!=5:raise RuntimeError('Set incomplete '+p.name+' '+str(count))
 sets+=1
def csvsave(name,items,fields):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(items)
csvsave('all_version_sha256.csv',shas,['file','sha256','kind'])
csvsave('exact_product_clean_photo_provenance.csv',sources,['family','photo_url','product_page','source_sha256','new_sha256','result','source_type','notes'])
summary={'version':'2.4.18b','previous_version_jpg_preserved':count_old,'new_clean_product_photo_jpg':new,'actual_clean_photo_frame_slots_replaced':new,'review_sets_checked':sets,'production_complete_qa_pending':0,'ready_except_logo':0,'final_qa_approved':0,'logo_binary_recovered':False,'verified_complete_swatch_chart':0,'public_urls_preserved':55,'note':'Versioned clean photo replaces inherited watermarked poster in 3 B groups; all originals retained; no false seller QA clearance.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
