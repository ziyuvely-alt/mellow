#!/usr/bin/env python3
"""v2.4.22: real five-HERO English caption retouch; preserve all 215 originals,
151 accepted EN draft modifications, no releases or invented logo/swatch.
"""
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
import cv2, numpy as np, shutil, hashlib, json, csv
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input-v2421c'
GALLERY=ROOT/'input-v2421-gallery'
OUT=ROOT/'production-v2422';OUT.mkdir(exist_ok=True)
LABELS={
 'pending-01':'MISSHA Magic Cushion Cover Lasting',
 'pending-07':'CLIO Kill Cover Mesh Blur Cushion Set',
 'pending-08':'peripera Mood Glowy Tint 4 g | Shades 01-20',
 'pending-19':'goodal Green Tangerine Vita C Dark Spot Cream Alpha 50 mL',
 'pending-23':'OBgE Pore Zero Oil Control Sun Cream 50 mL'
}
ONE={
 'pending-09':('OBgE Oil Control Finisher 5g','SOURCE_QA_HOLD'),
 'pending-22':('OBgE Max Waterful Sun Cream 300ml','SOURCE_QA_HOLD'),
 'pending-24':('BIOHEAL BOH NAD Preezcel Glow Power Serum 30ml','SOURCE_QA_HOLD'),
 'pending-25':('BIOHEAL BOH NAD Preezcel Glow Boost Cream 50ml','SOURCE_QA_HOLD'),
 'pending-27':('PIXEL PURE Soothing Ampoule Toner 200ml','SOURCE_QA_HOLD'),
 'pending-28':('PIXEL PURE Glow Cleansing Serum Pad 210ml / 70pcs','SOURCE_QA_HOLD'),
 'pending-29':('PIXEL PURE Radiance Aqua Soothing Cream 50ml','SOURCE_QA_HOLD'),
 'pending-30':('PIXEL PURE Aura Radiance Serum 50ml','SOURCE_QA_HOLD')
}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jpg_ok(p):
 with Image.open(p) as f:return f.format=='JPEG' and f.size==(1080,1080) and p.stat().st_size<2000000
def make(old,dst,label):
 before=np.array(Image.open(old).convert('RGB'))
 roi=before[882:961,50:1040,:]
 dark=(roi[:,:,0]<155)&(roi[:,:,1]<165)&(roi[:,:,2]<155)
 mask=np.zeros(before.shape[:2],dtype=np.uint8)
 mask[882:961,50:1040]=(dark*255).astype('uint8')
 mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
 img=cv2.inpaint(cv2.cvtColor(before,cv2.COLOR_RGB2BGR),mask,5,cv2.INPAINT_TELEA)
 result=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
 draw=ImageDraw.Draw(result)
 for n in range(37,21,-1):
  font=ImageFont.truetype(FONT,n)
  if draw.textbbox((0,0),label,font=font)[2]<944:break
 draw.text((68,897),label,font=font,fill=(42,59,51))
 dst.parent.mkdir(parents=True,exist_ok=True)
 result.save(dst,'JPEG',quality=94,optimize=True)
 assert jpg_ok(dst) and sha(dst)!=sha(old)
 # JPEG lossy difference outside target editing stripe must be tiny.
 after=np.array(Image.open(dst).convert('RGB'))
 diff=np.abs(before[:870].astype('int16')-after[:870].astype('int16'))
 return float(diff.mean())
# Preserve exact current v2421c 151 EN derivatives and all original immutable products.
count=0
for subtree in ('originals-immutable','en-customer-drafts','en-photo-captions'):
 for p in (SRC/subtree).rglob('*.jpg'):
  dest=OUT/subtree/p.relative_to(SRC/subtree)
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(p,dest)
  assert sha(dest)==sha(p);count+=1
assert count==215+64+87,count
manifest=[]
for fid,text in LABELS.items():
 src=SRC/'originals-immutable/preserved-pending-originals'/fid/'01_HERO_CANDIDATE.jpg'
 dst=OUT/'en-hero-fixed'/fid/'01_HERO_EN_V2422.jpg'
 error=make(src,dst,text)
 assert error<3.5,('photo_changed',fid,error)
 manifest.append({'family':fid,'previous_sha256':sha(src),'new_sha256':sha(dst),'new_jpg':str(dst.relative_to(OUT)),'photo_upper_region_avg_pixel_drift':round(error,4),'status':'EN_HERO_CAPTION_PATCHED_VISUAL_QA_PENDING'})
 print('HERO',fid,'upper_photo_diff',round(error,3),flush=True)
# Clio official independent photo remains inventory edition and image rights HOLD.
clio='clio-kill-cover-founwear-cushion-original-mini-sourcephoto-v245b-cutout-20261101'
orig=SRC/'originals-immutable/preserved-public-http/images'/clio
review=OUT/'public-16-review-only'/clio;review.mkdir(parents=True,exist_ok=True)
for p in orig.glob('*.jpg'):shutil.copy2(p,review/('ORIGINAL_'+p.name))
option=next((GALLERY/'new-version-photo-candidates'/clio).glob('*.jpg'),None)
if option:
 shutil.copy2(option,review/'OFFICIAL_ALTERNATE_CLIO_QA_HOLD.jpg')
 assert jpg_ok(review/'OFFICIAL_ALTERNATE_CLIO_QA_HOLD.jpg')
with (OUT/'hero_five_sha256.csv').open('w',newline='',encoding='utf-8-sig') as fp:
 cols=list(manifest[0]);w=csv.DictWriter(fp,fieldnames=cols);w.writeheader();w.writerows(manifest)
single=[]
for fid,(name,status) in ONE.items():
 allphotos=list((SRC/'originals-immutable/preserved-pending-originals'/fid).glob('*.jpg'))
 info=list((SRC/'en-customer-drafts'/fid).glob('*.jpg'))
 photo=list((SRC/'en-photo-captions'/fid).glob('*.jpg'))
 single.append({'id':fid,'name':name,'original_jpg':len(allphotos),'en_information':len(info),'en_photo_revisions':len(photo),'status':status,'reason':'Original MK binary, exact inventory version, distinct 5 roles and/or commercial reuse rights unverified'})
with (OUT/'eight_single_product_release_gates.csv').open('w',newline='',encoding='utf-8-sig') as fp:
 cols=list(single[0]);w=csv.DictWriter(fp,fieldnames=cols);w.writeheader();w.writerows(single)
# Public images untouched; any alternative kept outside publish paths.
assert sum(1 for p in (OUT/'originals-immutable/preserved-public-http').rglob('*.jpg'))==55
assert len(manifest)==5
summary={'version':'2.4.22','preserved_215_original_jpg_sha':215,'preserved_151_active_en_jpg_sha':151,'hero_images_edited':5,'hero_image_damage_hold':0,'hero_option_family_final_qa_hold':['pending-01','pending-07','pending-08'],'public_16_previously_flagged':16,'public_16_actual_final_approved_replacements':0,'public_clio_independent_scene_held_for_inventory_rights':int(bool(option)),'public_source_39_fully_cleared':0,'single_product_eight_reviewed':8,'ready_except_logo':0,'production_complete_qa_pending':0,'final_qa_approved':0,'original_mk_logo_binary':False,'official_shade_charts_complete':0,'live_55_urls_unchanged':55,'note':'Five actual HERO captions repainted via constrained mask inpainting; no product pixels above y870 altered beyond JPEG encoding noise. Public 16 require independent confirmed packaging and image reuse rights before final photo swap.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
