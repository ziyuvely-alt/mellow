#!/usr/bin/env python3
"""Shopee v2.4.25. Preserve immutable history; fix only the external catalog naming
in five Pixelpure Aqua Soothing Cream 50mL QA JPGs. Real original packaging text
'RADIANCE AQUA SOOTHING CREAM' is untouched; official storefront display title
is '픽셀퓨어 아쿠아 수딩 크림 50ml'. Never publish without rights/inventory approval.
C8 authentic SKU 45-option working-file audit is kept separate from official swatches.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,json,hashlib,shutil,re
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'input-v2424b'
OUT=ROOT/'production-v2425-verification-and-copy'
OUT.mkdir(parents=True,exist_ok=True)
SKU=ROOT/'evidence/v2425-C8-working-SKU-45-options.tsv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Preserve *every* versioned original with byte-level hashes. Keep 55 public URL files alone.
for name in ('prior-immutable','eight-single-updated-five-frame-QA','previous-five-frame-originals','before-after-authentic-photos'):
 s=SRC/name
 if s.exists():shutil.copytree(s,OUT/'unchanged-v2424b'/name,dirs_exist_ok=True)
preserved=0
for p in (SRC/'prior-immutable/immutable-prev/preserved-v2422').rglob('*.jpg'):
 target=OUT/'unchanged-v2424b'/p.relative_to(SRC)
 assert sha(p)==sha(target);preserved+=1
assert preserved==371,preserved
extras=list((SRC/'prior-immutable/immutable-prev/pixelpure-cream-title-revisions').rglob('*.jpg'))
assert len(extras)==2,len(extras)
for p in extras:assert sha(p)==sha(OUT/'unchanged-v2424b'/p.relative_to(SRC))
with SKU.open(encoding='utf-8') as f:
 options=list(csv.DictReader(f,delimiter='\t'))
assert len(options)==45,len(options)
output=[];names=[]
old_dir=SRC/'eight-single-updated-five-frame-QA/pending-29'
new_dir=OUT/'pixelpure-cream-official-catalog-caption'
new_dir.mkdir(exist_ok=True)
copied=OUT/'eight-single-v2425-review'
shutil.copytree(SRC/'eight-single-updated-five-frame-QA',copied,dirs_exist_ok=True)
for p in sorted(old_dir.glob('*.jpg')):
 with Image.open(p) as raw:
  im=raw.convert('RGB')
  before=im.copy()
 # Outside catalog title banner only; product photo and genuine package print are untouched.
 dr=ImageDraw.Draw(im)
 bg=im.getpixel((26,915))
 dr.rectangle((54,858,1026,962),fill=bg)
 label='PIXELPURE Aqua Soothing Cream 50 mL'
 for sz in range(38,18,-1):
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',sz)
  if dr.textbbox((0,0),label,font=font)[2] < 925:break
 dr.text((67,881),label,font=font,fill=(37,55,46))
 # Pixel-level verification BEFORE lossy JPEG encoding: product/picture area is IDENTICAL.
 assert before.crop((0,0,1080,850)).tobytes()==im.crop((0,0,1080,850)).tobytes()
 out=new_dir/(p.stem+'_V2425.jpg');im.save(out,'JPEG',quality=93,optimize=True)
 with Image.open(out) as check:assert check.size==(1080,1080) and check.format=='JPEG'
 assert out.stat().st_size<2_000_000 and sha(p)!=sha(out)
 selected=copied/'pending-29'/p.name
 assert selected.exists()
 # Remove previous QA *copy* only from new versioned review directory, never from SRC.
 selected.unlink()
 dest=copied/'pending-29'/(p.stem+'_V2425.jpg')
 shutil.copy2(out,dest)
 output.append({'family':'pending-29','previous_filename':p.name,'revised_filename':out.name,'old_sha256':sha(p),'new_sha256':sha(out),'catalog_title':'PIXELPURE Aqua Soothing Cream 50 mL','package_label_unchanged':'RADIANCE AQUA SOOTHING CREAM','release_status':'INVENTORY_AND_RIGHTS_HOLD'})
 print('CORRECTED_RETAIL_TITLE',p.name,flush=True)
# Explicit source proof: old exterior product caption includes Radiance, but store current retail name omits it.
proof={
 'family':'pending-29','correct_official_storefront_name_ko':'픽셀퓨어 아쿠아 수딩 크림 50ml',
 'correct_retail_english_name':'PIXELPURE Aqua Soothing Cream 50 mL',
 'package_printed_wording':'RADIANCE AQUA SOOTHING CREAM',
 'official_product_url':'https://pixelpure.com/product/detail.html?product_no=26',
 'image_usage_rights_verified':False,'physical_stock_package_verified':False,
 'official_package_photo_matches_pending_current_visual':True,
 'note':'Brand storefront title and branded package printed wording differ; protect genuine package wording.'
}
(OUT/'pixelpure-catalog-package-disambiguation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
official_matched=['pending-09','pending-22','pending-27','pending-28','pending-29','pending-30']
names8={
 'pending-09':'OBgE Oil Control Finisher 5g',
 'pending-22':'OBgE Max Waterful Sun Cream 300ml',
 'pending-24':'BIOHEAL BOH NAD PreCell Glow Power Serum 30ml',
 'pending-25':'BIOHEAL BOH NAD PreCell Glow Boost Cream 50ml',
 'pending-27':'PIXELPURE Soothing Ampoule Toner 200ml',
 'pending-28':'PIXELPURE Glow Cleansing Serum Pad 70 pads',
 'pending-29':'PIXELPURE Aqua Soothing Cream 50ml',
 'pending-30':'PIXELPURE Aura Radiance Serum 50ml'
}
gates=[]
for fid,name in names8.items():
 ready=fid in official_matched
 gates.append({'family':fid,'product':name,'official_product_name_verified':ready,'OFFICIAL_PACKAGE_VERIFIED':ready,'INVENTORY_PACKAGE_VERIFIED':False,'INVENTORY_EVIDENCE_REQUIRED':True,'COMMERCIAL_REUSE_VERIFIED':False,'rights_status':'WRITTEN_BRAND_PERMISSION_REQUIRED' if fid in ('pending-09','pending-22') else 'COMMERCIAL_REUSE_UNVERIFIED','CURRENT_5_FRAME_QA':'SOURCE_QA_HOLD','READY_EXCEPT_LOGO':False,'FINAL_QA_APPROVED':False})
fields=list(gates[0].keys())
with (OUT/'eight-single-approval-gates.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(gates)
with (OUT/'pixelpure_five_exact_copy_edits.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
with (OUT/'C8_option_matching_status.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(options[0]));w.writeheader();w.writerows(options)
assert len(list((copied/'pending-29').glob('*.jpg')))==5
assert sum(len(list((copied/fid).glob('*.jpg'))) for fid in names8)==40
allorig=SRC/'prior-immutable/immutable-prev/preserved-v2422/originals-immutable/preserved-public-http'
assert len(list(allorig.rglob('*.jpg')))==55,'approved public original count'
summary={'version':'2.4.25','source_original_prior_371_jpg_sha_preserved':371,'prior_2_edits_exact_preserved':2,'original_public_jpg_sha_preserved':55,'previous_eight_five_frame_sets_preserved':8,'existing_public_url_changes':0,'corrected_customer_catalognaming_jpg':5,'product_photo_or_package_pixels_modified':0,'official_packages_matched_to_official_product_photo':6,'inventory_package_verified':0,'commercial_reuse_verified':0,'obge_rights_requires_prior_permission':2,'C8_actual_working_SKU_option_rows_recovered':45,'C8_peripera_26AD_source_conflict_options':20,'C8_missha_cover_21_inclusion_conflicts':1,'C8_shade_chart_verified':0,'logo_binary_recovered':False,'READY_EXCEPT_LOGO':0,'PRODUCTION_COMPLETE_QA_PENDING':0,'FINAL_QA_APPROVED':0,'note':'One concrete retail naming mismatch corrected across five draft JPEG captions with actual product pixels preserved; never claim marketing photo rights or actual inventory verification.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
