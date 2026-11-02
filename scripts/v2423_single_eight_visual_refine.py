#!/usr/bin/env python3
"""v2423: preserve v2422; retouch only two redundant editorial headings on
Pixelpure 50 mL cream, and assemble eight 5-frame QA candidate sets.
No fictional packaging or logo, no public URL writes, no final QA approvals.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from collections import defaultdict
import cv2,numpy as np,shutil,hashlib,json,csv
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/'input-v2422'
OUT=ROOT/'production-v2423-single-qa';OUT.mkdir(exist_ok=True)
IDS=['pending-09','pending-22','pending-24','pending-25','pending-27','pending-28','pending-29','pending-30']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
# Immutable sources; retain every previous frame, unchanged.
for subtree in ['originals-immutable','en-customer-drafts','en-photo-captions','en-hero-fixed']:
 src=IN/subtree
 if src.is_dir():shutil.copytree(src,OUT/'preserved-v2422'/subtree,dirs_exist_ok=True)
source_count=0
for subtree in ['originals-immutable','en-customer-drafts','en-photo-captions','en-hero-fixed']:
 src=IN/subtree
 if src.is_dir():
  for p in src.rglob('*.jpg'):
   match=OUT/'preserved-v2422'/subtree/p.relative_to(src)
   assert sha(match)==sha(p)
   source_count+=1
assert source_count==215+64+87+5,source_count
fixed=[];holds=[]
changes={
 'INV_02_1a858dfc39_EN_V2421C.jpg':('JAR DETAILS','The 50 mL cream jar'),
 'INV_03_2ebc3d949d_EN_V2421C.jpg':('CREAM TEXTURE','The product and cream')
}
for srcname,(heading,subtitle) in changes.items():
 old=IN/'en-photo-captions/pending-29'/srcname
 with Image.open(old) as f:before=np.asarray(f.convert('RGB'))
 mask=np.zeros(before.shape[:2],dtype=np.uint8)
 # Only black headline and subtitle pixels, above y234 and x193:720.
 region=before[144:238,193:720]
 darkness=np.max(region,axis=2)<165
 mask[144:238,193:720]=(darkness*255).astype(np.uint8)
 mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
 clean=cv2.inpaint(cv2.cvtColor(before,cv2.COLOR_RGB2BGR),mask,5,cv2.INPAINT_TELEA)
 im=Image.fromarray(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(im)
 d.text((197,151),heading,font=font(36,True),fill=(36,51,31))
 d.text((197,205),subtitle,font=font(21),fill=(36,51,31))
 dest=OUT/'pixelpure-cream-title-revisions/pending-29'/(old.stem+'_V2423.jpg')
 dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,'JPEG',quality=94,optimize=True)
 with Image.open(dest) as check:assert check.format=='JPEG' and check.size==(1080,1080)
 assert dest.stat().st_size<2_000_000 and sha(dest)!=sha(old)
 delta=np.abs(np.array(im).astype('int16')-before.astype('int16'))
 assert np.max(delta[260:810])==0,'photo body edited'
 fixed.append({'family':'pending-29','from':srcname,'to':dest.name,'old_sha':sha(old),'new_sha':sha(dest),'status':'EN_PHOTO_TITLE_REVISE_VISUAL_QA_PENDING'})
 print('PIXELPURE_TITLE_REVISED',srcname,flush=True)
# Each review set: actual product scenes + distinct evidence-backed info if available.
sets=[]
for fid in IDS:
 originals=sorted((IN/'en-photo-captions'/fid).glob('*.jpg'))
 infos=sorted((IN/'en-customer-drafts'/fid).glob('*.jpg'))
 # Build 5-frame candidates with source assets only, no duplication or synthetic photo creation.
 if fid=='pending-09':
  # Original 5 predominantly model images, pick 2 authentic photographs + 3 distinct info roles.
  photos=originals[:2]; selected=photos+infos[:3]
 elif fid=='pending-22':
  photos=originals[:2]; selected=photos+infos[:3]
 elif fid=='pending-24':
  selected=originals[:4]+infos[:1]
 else:selected=originals[:5]
 if len(selected)!=5:raise ValueError((fid,len(selected)))
 folder=OUT/'8-single-product-5frame-review'/fid
 folder.mkdir(parents=True,exist_ok=True)
 for index,p in enumerate(selected,1):
  changed_path=OUT/'pixelpure-cream-title-revisions'/fid/(p.stem+'_V2423.jpg')
  actual=changed_path if changed_path.exists() else p
  dest=folder/(f'{index:02d}_{actual.name}')
  shutil.copy2(actual,dest)
  assert sha(dest)==sha(actual)
 # Resolve final stages only if legal permission, stock identity and original logo all verified.
 sets.append({'family':fid,'five_frame_files':5,'photo_frames':len(photos) if fid in ('pending-09','pending-22') else 4 if fid=='pending-24' else 5,'information_frames':3 if fid in ('pending-09','pending-22') else 1 if fid=='pending-24' else 0,'new_revised_frames':2 if fid=='pending-29' else 0,'status':'SOURCE_QA_HOLD','ready_except_logo':False,'approved':False,'reason':'Exact stock package/independent scene visual verification, original MK PNG and image commercial rights not yet cleared'})
 print('SINGLE_QA',fid,5,flush=True)
def outcsv(path,rows,fields):
 with (OUT/path).open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
outcsv('pixelpure_title_revision_sha.csv',fixed,['family','from','to','old_sha','new_sha','status'])
outcsv('single_eight_5frame_gates.csv',sets,['family','five_frame_files','photo_frames','information_frames','new_revised_frames','status','ready_except_logo','approved','reason'])
summary={'version':'2.4.23-single-qa-continuation','source_prior_jpg_preserved_sha':source_count,'original_source_jpg_preserved':215,'older_en_151_jpg_preserved':151,'hero_five_jpg_preserved':5,'new_real_jpg_title_revisions':2,'single_five_frame_review_packs':8,'ready_except_logo':0,'production_complete_qa_pending':0,'final_qa_approved':0,'public_urls_unchanged':55,'actual_mk_logo_binary_recovered':False,'official_shade_charts_complete':0,'notes':'Two actual Pixelpure 50mL cream editorial text overlays fixed on genuine archived images, body pixels exactly unchanged; 8 candidate sets curated, all are QA hold until stock package and usage rights verified.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
