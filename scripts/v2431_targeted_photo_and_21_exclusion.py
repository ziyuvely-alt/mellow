#!/usr/bin/env python3
"""v2.4.31: only two targeted real-image revisions from pre-existing photographs.
One corrects 300mL/200mL wrong bottle; one excludes MISSHA cover shade 21.
Never invent packaging, swatches, stock photos, logo or permissions.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,csv
SRC=Path("baseline-v2427b"); OUT=Path("v2431-output");OUT.mkdir(exist_ok=True)
ROOT=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"
HERO=ROOT/"immutable-prev"/"preserved-v2422"/"en-hero-fixed"/"pending-01"/"01_HERO_EN_V2422.jpg"
P200=ROOT/"new-independent-photo-candidates"/"pending-27"/"PRODUCT_PHOTO_01_V2424.jpg"
OLD27=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"eight-single-updated-five-frame-QA"/"pending-27"/"01_INV_01_1f25c5d0f4_EN_V2421C.jpg"
assert all(p.exists() for p in [HERO,P200,OLD27])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
def safe_save(img,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 img.convert("RGB").save(dest,"JPEG",quality=94,optimize=True)
 with Image.open(dest) as ck:
  ck.load()
  assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2_000_000
 return {"path":str(dest.relative_to(OUT)),"sha256":sha(dest),"bytes":dest.stat().st_size,"dimensions":[1080,1080]}
before={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob("*.jpg")}
# 1) Source image with real exact 200mL printed packaging; preserve the original photographed pixels unchanged.
with Image.open(P200) as original:
 original=original.convert("RGB")
 # Verify source matches the known source 1080x1080 image. Original photo is x90..710, y9..909,
 # so keep entirety of product bottle while omitting unrelated stamp badges on right.
 assert original.size==(1080,1080)
 photo=original.crop((91,9,715,912))
 photo=ImageOps.contain(photo,(630,784),Image.Resampling.LANCZOS)
 bg=Image.new("RGB",(1080,1080),(247,242,235));d=ImageDraw.Draw(bg)
 d.text((72,59),"PIXEL PURE",font=font(35,True),fill=(38,57,48))
 d.text((72,115),"Soothing Ampoule Toner",font=font(40,True),fill=(38,57,48))
 d.line((72,177,1008,177),fill=(186,195,181),width=2)
 bg.paste(photo,((1080-photo.width)//2,194))
 d.line((72,983,1008,983),fill=(186,195,181),width=2)
 d.text((72,916),"200 mL",font=font(48,True),fill=(38,57,48))
 d.text((72,1001),"Actual 200 mL bottle photograph",font=font(19),fill=(87,98,87))
 out1=OUT/"sales-image-drafts"/"pending-27"/"01_correct_200ml_bottle_V2431.jpg"
 file1=safe_save(bg,out1)
# 2) MISSHA: use documented actual bitmap and crop out all visual instances of excluded 21.
# Original screenshot has a 4-column shade layout. Crop only existing 23/25/27 swatch area.
# The source itself has not been independently verified as official so DO NOT approve its sales use.
with Image.open(HERO) as original:
 original=original.convert("RGB")
 assert original.size==(1080,1080)
 # Get existing photographic 23/25/27 samples, excluding 21 left-most column.
 # Top part actual swatch strips (x350..915, y225..500), lower original chips (x272..670?):
 # Retain only actual photographed top region; do not reconstruct color chips.
 photo=original.crop((349,225,916,500))
 photo=ImageOps.contain(photo,(936,454),Image.Resampling.LANCZOS)
 bg=Image.new("RGB",(1080,1080),(247,244,239)); d=ImageDraw.Draw(bg)
 d.text((57,57),"MISSHA Magic Cushion",font=font(42,True),fill=(46,61,53))
 d.text((57,116),"Cover Lasting",font=font(33),fill=(46,61,53))
 d.line((57,174,1023,174),fill=(177,185,179),width=2)
 # Unmodified actual-color pixels, not a synthetic gradient or chip.
 bg.paste(photo,((1080-photo.width)//2,272))
 for i,label in enumerate(("23","25","27")):
  x=235+i*310
  d.text((x,747),"No. "+label,font=font(38,True),fill=(46,61,53))
 d.text((57,876),"Shades shown: 23 / 25 / 27",font=font(26),fill=(46,61,53))
 # This is a non-public QA sales-layout draft until origin and generation evidence pass.
 out2=OUT/"shade-source-drafts"/"pending-01"/"MISSHA_Cover_23_25_27_sourcecrop_QA_V2431.jpg"
 file2=safe_save(bg,out2)
# Verify every baseline source remains byte-identical.
assert before=={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob("*.jpg")}
result={
 "version":"2.4.31","latest_prior_checkpoint":"v2.4.30d",
 "actual_new_JPG":2,"retail_layout_drafts":1,"shade_reference_QA_drafts":1,
 "actual_photo_replacement_count":1,"shades_removed_from_current_qa_draft":[21],
 "source_preservation":len(before),"source_hash_changed":0,
 "published_URL_changed":0,"customer_images_published":0,
 "new_official_verified_shade_chart":0,"FINAL_QA_APPROVED":0,
 "photo_permissions_verified":0,"MK_original_binary_verified":False,
 "findings":[
 {"group":"pending-27","old":str(OLD27.relative_to(SRC)),"source":str(P200.relative_to(SRC)),
  "old_sha256":sha(OLD27),"source_sha256":sha(P200),"output":file1,
  "status":"SALES_IMAGE_DRAFT","blocking":["COMMERCIAL_REUSE_PERMISSION_REQUIRED","MK_ORIGINAL_LOGO_REQUIRED","STOCK_PACKAGE_CROSSCHECK_REQUIRED"],
  "evidence":"Manufacturer official listing confirms 200mL; source from preserved authentic photo; 300mL erroneous old frame removed from this draft"},
 {"group":"pending-01","old":str(HERO.relative_to(SRC)),"old_sha256":sha(HERO),"output":file2,
  "status":"SOURCE_QA_HOLD","blocking":["SOURCE_PROVENANCE_REQUIRED","GENERATION_MATCH_REQUIRED","COMMERCIAL_REUSE_PERMISSION_REQUIRED"],
  "evidence":"Actual existing shade photograph cropped to exclude forbidden No.21. The original swatch photo has not independently passed official provenance check; not approved for sale"}
 ],
 "next_recovery":["pending-27 compare source 200mL photo with actual stock photo and rights","pending-01 obtain official 23/25/27 Cover Lasting swatches, replace hold draft","pending-10 approved original cutout","pending-12/13/14/17/19/23 pending verified cutout source","continue remaining frames visual QA"]
}
(OUT/"v2431_checkpoint.json").write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in result.items() if k!="findings"},ensure_ascii=False),flush=True)
