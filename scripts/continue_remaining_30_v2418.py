#!/usr/bin/env python3
"""Shopee v2.4.18: preserve 160 source JPGs and create evidence-backed
versioned photo-led replacement frames for B-tier families.
No photo alterations that invent package, shade or logo, no public upload.
"""
from pathlib import Path
import csv, hashlib, json, shutil, io, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input-v2417'
OUT=ROOT/'production-v2418'
OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
B12=['09','15','16','18','21','22','24','25','27','28','29','30']
def find_family(fid):return 'pending-'+fid
def font(sz,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,sz)
 except:return ImageFont.load_default()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(img):
 a=list(ImageOps.grayscale(img).resize((9,8)).getdata())
 return sum(1<<i for i in range(64) if a[(i//8)*9+i%8]>a[(i//8)*9+i%8+1])
def verify_jpg(p):
 with Image.open(p) as im:
  im.load()
  return im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
def make_photo_detail(src,dst,info):
 with Image.open(src) as im:
  im.load()
  if im.format not in ('JPEG','PNG','WEBP') or min(im.size)<450:raise ValueError('Unsupported input source photo')
  image=ImageOps.exif_transpose(im).convert('RGB')
 # Full-source photo, not synthetically extracted package or an invented cutout.
 bg=Image.new('RGB',(1080,1080),(244,237,229))
 photo=ImageOps.contain(image,(1030,840),Image.Resampling.LANCZOS)
 bg.paste(photo,((1080-photo.width)//2,30+(840-photo.height)//2))
 draw=ImageDraw.Draw(bg)
 draw.rectangle((0,889,1080,1080),fill=(225,237,225))
 draw.line((55,913,1024,913),fill=(127,164,138),width=2)
 title,subtitle=info['title'],info['subtitle']
 f1=font(32,True);f2=font(28)
 if draw.textbbox((0,0),title,font=f1)[2]>960:raise ValueError('Title would clip')
 if draw.textbbox((0,0),subtitle,font=f2)[2]>960:raise ValueError('Subtitle would clip')
 draw.text((72,937),title,font=f1,fill=(48,67,57))
 draw.text((73,1000),subtitle,font=f2,fill=(67,86,72))
 bg.save(dst,'JPEG',quality=91,optimize=True)
 assert verify_jpg(dst)
INSTRUCTIONS={
'pending-09':{'src':'public/owned86/20261029/obge-oil-control-finisher-5g/e5d4be633715_05.jpg','title':'OBgE / OIL CONTROL FINISHER','subtitle':'5 g  •  Product detail','old_photo':'INV_05_121547b5c9.jpg','chosen':['INV_02_02a7beb90a.jpg','INV_03_1859a75292.jpg','INFO_04_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],'source':'OWNER_STOCK_ARCHIVE','identity':'5g product; source photo original from owned86'},
'pending-15':{'src':'input-v2417/source-originals/pending-15/ff1bd32db4957d8902.jpg','title':'Dr.G / GREEN MILD UP SUN+','subtitle':'50 mL  •  Product and texture','old_photo':'INV_01_6b3a4a3666.jpg','chosen':['INV_02_7f3ea992bc.jpg','INV_03_8d52f556bc.jpg','INFO_04_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],'source':'MUSINSA_3505223','identity':'Prior 2022 package, cannot assert latest 2026 packaging'},
'pending-18':{'src':'public/owned86/20261029/drg-brightening-up-sun-plus-50ml/254aee0e0f1a_02.jpg','title':'Dr.G / BRIGHTENING UP SUN+','subtitle':'50 mL  •  Product detail','old_photo':'INV_01_254aee0e0f.jpg','chosen':['INV_02_66493f8937.jpg','INV_04_e3df9b823a.jpg','INFO_03_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],'source':'OWNER_STOCK_ARCHIVE','identity':'Brightening Up Sun PLUS, not Moisture Sun'},
'pending-21':{'src':'input-v2417/source-originals/pending-21/20f5008034caf02a61.jpg','title':'GOODAL / VITA-C EYE CREAM','subtitle':'30 mL  •  Standalone tube + box','old_photo':'PHOTO_01_V2413.jpg','chosen':['PHOTO_02_V2413.jpg','INFO_03_V2413.jpg','INFO_04_V2413.jpg','INFO_05_V2413.jpg'],'source':'COUPANG_SINGLE_ITEM','identity':'Caution: physical 25AD packaging not verified by stock sample'},
'pending-22':{'src':'public/owned86/20261029/obge-max300ml/8629d1d381fa_01.jpg','title':'OBgE / MAX WATERFUL SUN','subtitle':'300 mL  •  Full size product','old_photo':'INV_05_8629d1d381.jpg','chosen':['INV_02_0ab7541042.jpg','INV_03_688df5a1bc.jpg','INFO_03_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],'source':'OWNER_STOCK_ARCHIVE','identity':'300ml package detail verified against owned86 picture, stock version still QA pending'}
}
NOCHANGE={
'pending-16':'Four different real product image roles plus volume panel already present; no justified replacement',
'pending-24':'Existing product images include distinct package, texture and detail scenes; verify stock packaging later',
'pending-25':'Five visually different actual product scenes present; preserve without regeneration',
'pending-27':'Five different toner product scenes present; no evidence-backed replacement needed',
'pending-28':'Five pad/jar product detail scenes present; no evidence-backed replacement needed',
'pending-29':'Five soothing cream scenes present; no evidence-backed replacement needed',
'pending-30':'Five serum product / texture scenes present; no evidence-backed replacement needed'
}
manifest=[];source_rows=[];families=[];pairs=[];reused=0;made=0
# Every existing source JPG is copied unchanged and validated; never modified.
for p in sorted((SRC/'original-preserved').glob('pending-*/*.jpg')):
 dst=OUT/'original-preserved'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,dst)
 if not verify_jpg(dst) or digest(dst)!=digest(p):raise RuntimeError('Previous JPG mutated or invalid: '+str(p))
 manifest.append({'family':p.parent.name,'file':p.name,'sha256':digest(dst),'bytes':dst.stat().st_size,'kind':'PRESERVED_ORIGINAL'})
 reused+=1
for fid in B12:
 group=find_family(fid);folder=OUT/'review-five-frame-sets'/group;folder.mkdir(parents=True,exist_ok=True)
 data=INSTRUCTIONS.get(group)
 selected=[]
 if data:
  src=ROOT/data['src']
  if not src.is_file():raise RuntimeError('Missing grounded source photo '+str(src))
  newpath=OUT/'new-photo-led-frames'/group/('REPLACEMENT_PHOTO_DETAIL_V2418.jpg')
  newpath.parent.mkdir(parents=True,exist_ok=True)
  make_photo_detail(src,newpath,data)
  selected=[newpath]+[SRC/'original-preserved'/group/name for name in data['chosen']]
  if any(not p.is_file() for p in selected):raise RuntimeError('Missing selected real frame '+group)
  made+=1
  source_rows.append({'family':group,'source_path':data['src'],'source_sha256':digest(src),'new_sha256':digest(newpath),'replaces_candidate':data['old_photo'],'status':'PHOTO_LED_VERSIONED_REPLACEMENT_QA_PENDING','identity_notes':data['identity']})
  manifest.append({'family':group,'file':newpath.name,'sha256':digest(newpath),'bytes':newpath.stat().st_size,'kind':'NEW_VERSIONED_PHOTO_CANDIDATE'})
 else:
  selected=sorted((SRC/'original-preserved'/group).glob('*.jpg'))
  assert len(selected)==5, (group,len(selected))
 hashlist=[]
 for i,p in enumerate(selected,1):
  if not verify_jpg(p):raise RuntimeError('Invalid reviewed frame '+str(p))
  with Image.open(p) as im:h=dhash(im)
  for name,ph in hashlist:
   distance=(h^ph).bit_count()
   if distance<=5:pairs.append({'family':group,'a':name,'b':p.name,'dhash_distance':distance})
  hashlist.append((p.name,h))
  shutil.copy2(p,folder/(f'{i:02d}_'+p.name))
 families.append({'family':group,'frames':len(selected),'improved_candidate':bool(data),'replacement_slot':data['old_photo'] if data else '', 'review_result':'REVISE','ready_except_logo':False,'official_swatch_complete':False,'reason':data['identity'] if data else NOCHANGE[group]})
 print('B12',group,'new=',bool(data),'frames=',len(selected),'duplicate_pairs=',sum(p['family']==group for p in pairs),flush=True)
def csvsave(name,rows,fields):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
csvsave('all_original_sha256.csv',manifest,['family','file','sha256','bytes','kind'])
csvsave('replacement_provenance.csv',source_rows,['family','source_path','source_sha256','new_sha256','replaces_candidate','status','identity_notes'])
csvsave('B12_review_status.csv',families,['family','frames','improved_candidate','replacement_slot','review_result','ready_except_logo','official_swatch_complete','reason'])
csvsave('revised_sets_visual_similarity.csv',pairs,['family','a','b','dhash_distance'])
result={'version':'2.4.18','original_jpg_unchanged':reused,'new_photo_led_jpg':made,'versioned_frame_slots_replaced':made,'improved_B_families':made,'B_families_reviewed':len(families),'unchanged_B_families':len(NOCHANGE),'five_frame_candidate_sets':len(families),'near_duplicate_candidate_pairs_in_sets':len(pairs),'final_qa_approved':0,'ready_except_logo':0,'production_complete_qa_pending':0,'true_mk_logo_binary':False,'official_swatch_charts_complete':0,'published_public_urls_unchanged':55,'note':'Five distinct source-photo improvements in versioned sets; packaging editions, original logo, exact SKUs and redistribution rights require final QA.'}
(OUT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(result,ensure_ascii=False),flush=True)
