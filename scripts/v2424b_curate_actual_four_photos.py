#!/usr/bin/env python3
"""v2424b: actual targeted 4 frame replacements in eight FIVE_FRAME_DRAFT review sets.
The 4 replacements are exact product images visually inspected from manufacturer official galleries.
Never touch published 55 images; source commercial reuse rights/physical inventory remain QA HOLD.
"""
import csv,hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
ORIG=ROOT/'input-v2423'
OFF=ROOT/'input-v2424-official'
OUT=ROOT/'production-v2424b-curated-eight'
OUT.mkdir(exist_ok=True)
SELECTION={
 ('pending-09',1):('pending-09','PRODUCT_PHOTO_01_V2424.jpg','brand official photo open compact'),
 ('pending-09',2):('pending-09','PRODUCT_PHOTO_02_V2424.jpg','brand official closed compact'),
 ('pending-22',1):('pending-22','PRODUCT_PHOTO_01_V2424.jpg','brand official actual pump bottle'),
 ('pending-28',3):('pending-28','PRODUCT_PHOTO_01_V2424.jpg','brand official pads and open jar composition')
}
WRONG_PRODUCT={'pending-22':['PRODUCT_PHOTO_02_V2424.jpg']}
IDS=['pending-09','pending-22','pending-24','pending-25','pending-27','pending-28','pending-29','pending-30']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Archive previous sources exactly, all file versions.
for dirname in ('immutable-prev','authentic-photo-originals','new-independent-photo-candidates'):
 src=OFF/dirname
 if src.exists():shutil.copytree(src,OUT/'prior-immutable'/dirname,dirs_exist_ok=True)
before_new=[]
for p in OFF.rglob('*.jpg'):
 if p.is_file() and p.relative_to(OFF).parts[0] in ('immutable-prev','new-independent-photo-candidates'):
  dst=OUT/'prior-immutable'/p.relative_to(OFF)
  assert dst.exists() and sha(dst)==sha(p)
# Preserve exact previous curated eight 5-frame packages for before/after.
shutil.copytree(ORIG/'8-single-product-5frame-review',OUT/'previous-five-frame-originals',dirs_exist_ok=True)
rows=[];families=[];changed=0
for fid in IDS:
 prev=sorted((ORIG/'8-single-product-5frame-review'/fid).glob('*.jpg'))
 assert len(prev)==5,(fid,len(prev))
 dest=OUT/'eight-single-updated-five-frame-QA'/fid
 dest.mkdir(parents=True,exist_ok=True)
 for slot,old in enumerate(prev,1):
  which=SELECTION.get((fid,slot))
  if which:
   candidate=OFF/'new-independent-photo-candidates'/which[0]/which[1]
   if not candidate.exists():raise FileNotFoundError(candidate)
   final=dest/(f'{slot:02d}_NEW_AUTHENTIC_PHOTO_V2424.jpg')
   shutil.copy2(candidate,final)
   rows.append({'family':fid,'slot':slot,'old_file':old.name,'new_file':final.name,'old_sha256':sha(old),'new_sha256':sha(final),'verification':'MANUFACTURER_PHOTO_CORRECT_PRODUCT_VISUAL','source_class':'OFFICIAL_BRAND','qa_status':'PHOTO_CANDIDATE_RIGHTS_AND_STOCK_HOLD'})
   changed+=1
   compare=OUT/'before-after-authentic-photos'/fid/(f'{slot:02d}_comparison.jpg')
   compare.parent.mkdir(parents=True,exist_ok=True)
   with Image.open(old) as a,Image.open(final) as b:
    composite=Image.new('RGB',(1080,585),(250,250,248))
    composite.paste(ImageOps.contain(a.convert('RGB'),(530,530)),(6,37))
    composite.paste(ImageOps.contain(b.convert('RGB'),(530,530)),(544,37))
    d=ImageDraw.Draw(composite)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    d.text((8,8),'EXISTING FRAME',font=f,fill=(40,57,49))
    d.text((545,8),'OFFICIAL SOURCE NEW VERSION',font=f,fill=(40,57,49))
    composite.save(compare,'JPEG',quality=89,optimize=True)
  else:
   final=dest/old.name
   shutil.copy2(old,final)
  assert sha(final)==(sha(OFF/'new-independent-photo-candidates'/which[0]/which[1]) if which else sha(old))
  with Image.open(final) as im:assert im.size==(1080,1080) and im.format=='JPEG'
  assert final.stat().st_size<2_000_000
 families.append({'family':fid,'frames':len(list(dest.glob('*.jpg'))),'actual_frame_replacements_for_reviewer':sum(k[0]==fid for k in SELECTION),'license_verified':False,'inventory_exact_package_verified':False,'source_qa_state':'FIVE_FRAME_DRAFT_SOURCE_QA_HOLD','ready_except_logo':False,'final_qa_approved':False})
 print('CURATED',fid,'revisions',families[-1]['actual_frame_replacements_for_reviewer'],flush=True)
assert changed==4
# Official manufacturer cross-check record with rejected false-product candidate intentionally excluded.
proof={'v':'2.4.24b','accepted_visual_candidate_source_photos':4,'rejected_wrong_product_photo':'pending-22/PRODUCT_PHOTO_02_V2424.jpg','reason':'Photo is OBgE Oil Control Finisher compact, not Max Waterful Sun Cream 300ml bottle','other_8_official_photo_candidates':'Not automatically used; old approved subject-matched images retained','all_live_55_urls_intact':True,'rights_approval':False,'exact_inventory_package_verified':False}
(OUT/'reviewer_photo_filtering.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding='utf8')
def csvout(p,entries,fields):
 with (OUT/p).open('w',encoding='utf-8-sig',newline='') as file:
  w=csv.DictWriter(file,fieldnames=fields);w.writeheader();w.writerows(entries)
csvout('four_actual_frame_replacements.csv',rows,['family','slot','old_file','new_file','old_sha256','new_sha256','verification','source_class','qa_status'])
csvout('eight_single_5frame_current_status.csv',families,['family','frames','actual_frame_replacements_for_reviewer','license_verified','inventory_exact_package_verified','source_qa_state','ready_except_logo','final_qa_approved'])
summary={'version':'2.4.24b','prior_v2423_371_source_jpg_preserved':371,'v2423_extra_2_fixes_preserved':2,'official_photo_candidates_generated_earlier':12,'wrong_product_candidate_rejected':1,'new_qa_replacement_jpg':4,'updated_five_frame_review_family_sets':8,'five_frame_total_qa_current':40,'new_photo_rights_cleared':0,'stock_package_verified':0,'ready_except_logo':0,'production_complete_qa_pending':0,'final_qa_approved':0,'original_MK_binary':False,'official_shade_charts':0,'public_URLs_changed':0,'note':'Four true distinct manufacturer product photographs replace model-heavy or redundant frames ONLY in private eight-family QA sets. No public Shopee swap. Copyright and inventory package remain gating.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
