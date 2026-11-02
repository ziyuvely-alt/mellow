#!/usr/bin/env python3
"""v2.4.21c actual 87 Korean footer fixes on archived 96 product-photo JPG.
Rectangular lower caption strip is separate from product photo and authentic package.
Do not modify HERO shade art (irregular backdrop), PHOTOs already English, any live URLs or actual product bodies.
"""
import hashlib,json,shutil,csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input-v2421b'
OUT=ROOT/'production-v2421c-photo-en'
shutil.copytree(SRC,OUT,dirs_exist_ok=True)
BASE=SRC/'originals-immutable/preserved-pending-originals'
NAMES={
'pending-01':'MISSHA Magic Cushion Cover Lasting',
'pending-02':'MISSHA Magic Cushion Moist Up',
'pending-03':'MISSHA M Perfect Cover BB Cream',
'pending-04':'CLIO Kill Cover Mesh Glow Essential Cushion Mini 5 g',
'pending-05':'CLIO Kill Cover Founwear Cushion Set',
'pending-06':'CLIO Kill Cover Mesh Glow Essential Cushion Set',
'pending-07':'CLIO Kill Cover Mesh Blur Cushion Set',
'pending-08':'peripera Mood Glowy Tint 4 g',
'pending-09':'OBgE Oil Control Finisher 5 g',
'pending-10':'OBgE Perfect Homme Cushion 15 g',
'pending-11':'OBgE All In One Double Essence 50 mL + 50 mL',
'pending-12':'MISSHA PDRN NAD+ Renew Peel Shot 25 15 mL',
'pending-13':'MISSHA PDRN NAD+ Firming Repair Serum 30 mL',
'pending-14':'MISSHA PDRN NAD+ Firming Repair Cream 70 mL',
'pending-15':'Dr.G Green Mild Up Sun Plus 50 mL',
'pending-16':'Dr.G Red Blemish Clear Soothing Cream 70 mL',
'pending-17':'Dr.G Brightening Up Moisture Sun 50 mL',
'pending-18':'Dr.G Brightening Up Sun Plus 50 mL',
'pending-19':'goodal Green Tangerine Vita C Dark Spot Cream Alpha 50 mL',
'pending-20':'goodal Green Tangerine Vita C Serum Mist 100 mL',
'pending-21':'goodal Green Tangerine Vita C Dark Spot Eye Cream 30 mL',
'pending-22':'OBgE Max Waterful Sun Cream 300 mL',
'pending-23':'OBgE Pore Zero Oil Control Sun Cream 50 mL',
'pending-24':'BIOHEAL BOH NAD Preezcel Glow Power Serum 30 mL',
'pending-25':'BIOHEAL BOH NAD Preezcel Glow Boost Cream 50 mL',
'pending-26':'PIXEL PURE Gentle Gel-to-Foam Cleanser 145 mL',
'pending-27':'PIXEL PURE Soothing Ampoule Toner 200 mL',
'pending-28':'PIXEL PURE Glow Cleansing Serum Pad 210 mL / 70 Pads',
'pending-29':'PIXEL PURE Radiance Aqua Soothing Cream 50 mL',
'pending-30':'PIXEL PURE Aura Radiance Serum 50 mL'
}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changed=[];skipped=[];counter=0
for folder in sorted(BASE.glob('pending-*')):
 fid=folder.name
 for p in sorted(folder.glob('*.jpg')):
  if p.name.startswith(('INFO_','PIXELPURE_INFO_')):continue
  # All of these are proven to have a flat pale Korean caption region below the photograph.
  if not p.name.startswith(('INV_','SOURCE_')):
   skipped.append({'family':fid,'filename':p.name,'reason':'HERO graphic irregular backdrop or already English PHOTO; no automatic destructive edit'})
   continue
  with Image.open(p) as file:
   im=file.convert('RGB')
  # Outer caption below the photographed/graphic product; original package and MK artwork untouched.
  sample=im.getpixel((80,945))
  d=ImageDraw.Draw(im)
  d.rectangle((55,855,1025,946),fill=sample)
  name=NAMES[fid]
  for n in range(35,20,-1):
   f=ImageFont.truetype(BOLD,n)
   w=d.textbbox((0,0),name,font=f)[2]
   if w<935:break
  assert w<935, (fid,name,w)
  d.text((70,876),name,font=f,fill=(43,61,53))
  dest=OUT/'en-photo-captions'/fid/(p.stem+'_EN_V2421C.jpg')
  dest.parent.mkdir(parents=True,exist_ok=True)
  im.save(dest,'JPEG',quality=93,optimize=True)
  with Image.open(dest) as ck:assert ck.format=='JPEG' and ck.size==(1080,1080)
  assert dest.stat().st_size<2000000
  before=sha(p);after=sha(dest);assert before!=after
  changed.append({'family':fid,'old_file':p.name,'en_jpg':dest.name,'source_sha256':before,'new_sha256':after,'status':'PHOTO_LANGUAGE_REVISION_DONE_VISUAL_QA_PENDING'})
  counter+=1
  print('PHOTO_EN',fid,p.name,flush=True)
assert counter==87,(counter,skipped)
assert len(skipped)==9,(len(skipped),skipped)
# Original 215 JPG and 64 EN already fixed in v2421b must remain untouched.
oldcount=0
for p in (SRC/'originals-immutable').rglob('*.jpg'):
 other=OUT/'originals-immutable'/p.relative_to(SRC/'originals-immutable')
 assert sha(p)==sha(other);oldcount+=1
assert oldcount==215
info=sorted((OUT/'en-customer-drafts').rglob('*.jpg'))
assert len(info)==64
def csvout(path,records,fields):
 with (OUT/path).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
csvout('photo_87_english_caption_changes.csv',changed,['family','old_file','en_jpg','source_sha256','new_sha256','status'])
csvout('photo_9_safe_holds.csv',skipped,['family','filename','reason'])
summary=json.loads((OUT/'summary.json').read_text(encoding='utf8'))
summary.update({'version':'2.4.21c','customer_info_en_jpg_preserved':64,'photo_source_jpg_reviewed':96,'photo_korean_footer_revised':counter,'photo_no_destructive_edit_hold':len(skipped),'photo_english_original_reused':4,'photo_hero_irregular_background_held':5,'photo_final_visual_qa_approved':0,'all_215_originals_sha_identical':215,'overall_en_revision_active_jpg':64+counter,'public_live_55_jpg_unchanged':55,'note':'87 Korean outer product-name captions edited to grounded English item names; authentic package print and all photographed content unaltered. Five irregular HERO graphics are held and four already-English PHOTO frames reused.'})
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
