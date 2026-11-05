#!/usr/bin/env python3
"""v2942: make four genuinely new, FACT-ONLY English fifth image frames from existing
four-photo stock archives. NOT a new source photograph, NOT approved for marketplace.
Exact product, volume and use instructions only. No logos invented or old files replaced.
"""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, time, textwrap

Q=Path('qa-review')
BASE=Q/'v2941-five-option-pack-generation-unit-conflict-resolution-QA'
PRE=Q/'v2940-four-final-source-gaps-photo-archive-integrity-and-approval-gate'
OUT=Q/'v2942-four-missing-fifth-slot-fact-only-English-visual-QA'
assert not OUT.exists(), 'v2942 checkpoint already exists; do not regenerate'
s=json.loads((BASE/'stock30-incremental-state-v2941.json').read_text(encoding='utf-8'))
m=json.loads((PRE/'manifest.json').read_text(encoding='utf-8'))
assert s['version']=='v2941' and m['version']=='v2940' and len(s['families'])==30
missing={x['family']:x for x in m['four_missing_source_families']}
assert set(missing)=={'pending-25','pending-27','pending-29','pending-30'}
SPECS={
 'pending-25':{
  'brand':'BIOHEAL BOH','name':['NAD-PRIZCELL','GLOW BOOST CREAM'],
  'category':'CREAM','amount':'50 mL','headline':'APPLICATION',
  'lines':['Use in your cream step','morning or evening.','Smooth gently over skin.'],
  'source':'https://www.lotteon.com/m/product/LO2653694326',
  'bg':'#F9F5F5','accent':'#752936','ink':'#41262C',
  'evidence':'Retailer 50mL label and generic instructed application'},
 'pending-27':{
  'brand':'PIXELPURE','name':['SOOTHING','AMPOULE TONER'],
  'category':'TONER','amount':'200 mL','headline':'APPLICATION',
  'lines':['After cleansing, apply','with clean hands or','a cotton pad.'],
  'source':'https://m.shilladfs.com/estore/kr/ko/p/5885751',
  'bg':'#FFF4F8','accent':'#A45E79','ink':'#5B3846',
  'evidence':'Duty-free published 200mL volume and two application methods'},
 'pending-29':{
  'brand':'PIXELPURE','name':['RADIANCE AQUA','SOOTHING CREAM'],
  'category':'CREAM','amount':'50 mL','headline':'APPLICATION',
  'lines':['Apply an appropriate','amount to the face.','Gently pat to absorb.'],
  'source':'https://m.shilladfs.com/estore/kr/ko/p/5885759',
  'bg':'#F9F2F6','accent':'#9E6A88','ink':'#53344A',
  'evidence':'Duty-free published 50mL volume and general application instructions'},
 'pending-30':{
  'brand':'PIXELPURE','name':['AURA RADIANCE','SERUM'],
  'category':'FACIAL SERUM','amount':'50 mL','headline':'PRODUCT DETAILS',
  'lines':['Product type','Facial serum','Net volume 50 mL'],
  'source':'https://pixelpure.com/product/detail.html?product_no=25',
  'bg':'#FBF1F7','accent':'#AD6488','ink':'#623B52',
  'evidence':'First-party product name, serum category and 50mL volume'}
}
def font(size,bold=False):
 options=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
 for p in options:
  try:return ImageFont.truetype(p,size)
  except OSError:pass
 return ImageFont.load_default()
def color(code):
 v=code.lstrip('#')
 return tuple(int(v[i:i+2],16) for i in (0,2,4))
def make_frame(rgb,cfg):
 bg=color(cfg['bg']);accent=color(cfg['accent']);ink=color(cfg['ink'])
 board=Image.new('RGB',(1080,1080),bg)
 d=ImageDraw.Draw(board)
 d.rounded_rectangle((40,40,1040,1040),radius=38,fill=(255,255,255),outline=(232,217,224),width=2)
 # The unmodified product source is displayed inside a photo panel. This is not new product photography.
 photo=ImageOps.contain(rgb,(510,764),Image.Resampling.LANCZOS)
 d.rounded_rectangle((66,91,600,949),radius=25,fill=(251,248,249))
 board.paste(photo,(333-photo.width//2,515-photo.height//2))
 d.rounded_rectangle((622,103,1010,152),radius=22,fill=accent)
 d.text((649,115),'PRODUCT INFORMATION',font=font(19,True),fill='white')
 y=198
 d.text((624,y),cfg['brand'],font=font(26,True),fill=accent)
 y+=75
 for line in cfg['name']:
  # Prevent overflow of full product names at the current font.
  use=33
  while use>19 and d.textbbox((0,0),line,font=font(use,True))[2]>366:use-=1
  d.text((624,y),line,font=font(use,True),fill=ink);y+=51
 d.line((624,y+16,994,y+16),fill=(227,209,217),width=3)
 y+=66
 d.text((624,y),cfg['category'],font=font(23),fill=accent)
 d.text((624,y+40),cfg['amount'],font=font(43,True),fill=ink)
 y+=154
 d.text((624,y),cfg['headline'],font=font(22,True),fill=accent)
 y+=48
 for ln in cfg['lines']:
  size=23
  while size>16 and d.textbbox((0,0),ln,font=font(size))[2]>368:size-=1
  d.text((624,y),ln,font=font(size),fill=ink);y+=42
 # Meaningful and visible noncommercial review mark. No unauthorized retailer/MK logo overlay.
 d.line((623,901,991,901),fill=(229,209,216),width=2)
 d.text((624,917),'EN • INTERNAL IMAGE QA',font=font(17,True),fill=accent)
 d.text((624,943),'Rights / stock / logo HOLD',font=font(15),fill=(130,115,121))
 d.text((74,971),'SOURCE PHOTO REUSED  •  NEW INFORMATION FRAME',font=font(16),fill=(125,110,116))
 return board
OUT.mkdir(parents=True)
records=[]
for fam,cfg in SPECS.items():
 x=missing[fam];v=x['verified_archive']
 path=Path(v['path'])
 assert path.is_file() and sha256(path.read_bytes()).hexdigest()==v['sha256']
 with ZipFile(path) as z:
  assert z.testzip() is None and len(z.namelist())==4
  first=z.read(z.namelist()[0])
  with Image.open(BytesIO(first)) as photo:
   photo.load()
   assert photo.format=='JPEG' and photo.size==(1080,1080)
   img=ImageOps.exif_transpose(photo).convert('RGB')
 frame=make_frame(img,cfg)
 outfile=OUT/(fam+'-English-product-info-slot05-1080-QA.jpg')
 frame.save(outfile,'JPEG',quality=90,optimize=True,subsampling=0)
 with Image.open(outfile) as chk:assert chk.format=='JPEG' and chk.size==(1080,1080)
 assert outfile.stat().st_size<2000000
 assert sha256(path.read_bytes()).hexdigest()==v['sha256']
 record={'family':fam,'product':s['families'][fam]['product'],
  'prior_source_photo_count':4,'new_information_frame_count':1,
  'total_internal_QA_frames':5,'distinct_source_photo_count':4,
  'fifth_source_photo_still_missing':True,
  'source_archive':str(path),'source_archive_sha256':v['sha256'],
  'fifth_frame':str(outfile),'fifth_frame_sha256':sha256(outfile.read_bytes()).hexdigest(),
  'output_dimensions':[1080,1080],'output_bytes':outfile.stat().st_size,
  'first_product_photo_sha256':sha256(first).hexdigest(),
  'copy_source':cfg['source'],'evidence':cfg['evidence'],
  'new_original_photography':False,'source_photo_edited':False,
  'claim_review_status':'FACT_ONLY_PENDING_FINAL_PROOF',
  'photo_redistribution_rights':'NOT_VERIFIED',
  'actual_stock_edition':'NOT_VERIFIED','original_MK_logo':'NOT_APPLIED',
  'retail_release_approved':False}
 records.append(record)
 s['families'][fam].update({
  'last_delta_version':'v2942',
  'release_status':'FOUR_SOURCE_PHOTOS_PLUS_ONE_NEW_INFO_FRAME_INTERNAL_ONLY',
  'v2942_new_5th_info_frame':str(outfile),
  'v2942_total_QA_frames':5,
  'v2942_distinct_original_photo_count':4,
  'v2942_missing_source_photo_count':1,
  'latest_photo_QA_checkpoint':'v2942 4 original archived product source JPGs unchanged, plus one new factual English info frame. Five internal QA frames but only four unique photos; rights/stock/MK and final text QA HOLD.',
  'sale_approved':False})
assert len(records)==4
report={'version':'v2942','baseline':'v2941','created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'four_product_families_processed':4,'new_original_English_information_images_created':4,
 'new_actual_product_source_photos':0,'new_complete_five_frame_INTERNAL_QA_sets':4,
 'remaining_missing_distinct_photograph_slots':4,
 'old_archives_modified':0,'old_11_completed_families_modified':0,
 'old_55_public_URLs_changed':0,'marketplace_retail_approvals':0,
 'new_public_image_URLs':0,'final_spreadsheet_shared':False,
 'preserve_source_photography_vs_info_frames_distinction':True,
 'records':records}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s.update({'version':'v2942','baseline':'v2941','new_sales_approvals':0,'new_public_URLs':0,'final_spreadsheet_shared':False})
(OUT/'stock30-incremental-state-v2942.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'v':'v2942','new_info_images':4,'5frame_internal_sets':4,'missing_original_scenes':4,'new_retail_approval':0},ensure_ascii=False))
