#!/usr/bin/env python3
"""v2789 targeted QA only: finish GOODAL frame05 from previously inspected
real source crop; create CLIO 5g mini's first *logo-free* five-scene photo
reference using already archived, product-specific source photographs.
No product, shade, unverified MK badge or promotional claim is generated.
The original 11 published products and 55 URLs are immutable.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,shutil,base64
QA=Path("qa-review")
OUT=QA/"v2789-goodal-frame5-and-clio-mini-no-fake-MK-five-scene-QA"
assert not OUT.exists();OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
# 1) GOODAL four old QA files exactly unchanged, frame 05 only from the
# selected b-formula-swirl (an image verified visually to have no ad text).
prior=QA/"v2787-goodal-fifth-photo-fix-and-clio-mini-official-source"
alts=QA/"v2788-goodal-new-source-texture-options-clio-mini-native"
good=OUT/"pending-19";good.mkdir()
good_frames=[]
for n in range(1,5):
 orig=next((prior/"pending-19").glob(f"{n:02d}-*.jpg"))
 target=good/orig.name
 shutil.copy2(orig,target)
 assert sha(orig)==sha(target)
 good_frames.append({"slot":n,"file":target.name,"sha256":sha(target),"unchanged_from_v2787":True})
new_source=alts/"pending-19"/"02-b-formula-swirl-real-photo-QA.jpg"
assert new_source.is_file()
final=good/"05-real-cream-formula-closeup-without-ad-copy-QA.jpg"
shutil.copy2(new_source,final)
assert sha(final)==sha(new_source)
good_frames.append({"slot":5,"file":final.name,"sha256":sha(final),
    "source":str(new_source),"unchanged_original_photo_pixels":True,
    "same_photo_exposure_as_frame02":True,
    "visual_role":"cream capsule formula and jar cap genuine texture close-up"})
# 2) CLIO four genuine old scenes cropped to eliminate unverified bottom MK
# and old headline. The official 600px mini is the separate fifth visual.
old=QA/"v2706-six-archival-five-real-source-families"/"pending-04"
assert old.is_dir()
official=alts/"pending-04"/"02-official-mini-b-gif-QA.jpg"
# Use exact suffix resolution file from v2788, rather than guessing.
if not official.is_file():
 candidates=list((alts/"pending-04").glob("*official-mini-b-gif-QA.jpg"))
 assert len(candidates)==1,candidates
 official=candidates[0]
clio=OUT/"pending-04";clio.mkdir()
clio_frames=[]
crops=[
 (1,(95,205,980,922),"full opened mini cushion compact"),
 (2,(95,215,985,919),"real finger-puff / opened compact"),
 (3,(175,245,905,895),"close-up of real cushion sponge and applicator"),
 (4,(165,250,915,918),"compact transparent case and cushion detail")
]
for slot,rect,desc in crops:
 orig=next(old.glob(f"{slot:02d}-*.jpg"))
 with Image.open(orig) as im:
  im.load();assert im.size==(1080,1080) and im.format=="JPEG"
  roi=im.convert("RGB").crop(rect)
  # Letterbox on white avoids silently clipping the real compact width.
  photo=ImageOps.contain(roi,(1080,1080),Image.Resampling.LANCZOS)
  image=Image.new("RGB",(1080,1080),"white")
  image.paste(photo,((1080-photo.width)//2,(1080-photo.height)//2))
 target=clio/f"{slot:02d}-archived-mini-photo-no-unknown-MK-reference-QA.jpg"
 image.save(target,"JPEG",quality=92,optimize=True,subsampling=0)
 clio_frames.append({"slot":slot,"file":target.name,"sha256":sha(target),
   "source":str(orig),"source_crop_xyxy":list(rect),
   "original_unverified_logo_corner_excluded":True,
   "contains_only_actual_prior_photo_pixels":True,
   "visual_role":desc,
   "exact_stock_shade_approved":False})
with Image.open(official) as im:
 im.load();assert im.size==(1080,1080) and im.format=="JPEG"
# The official same-item 600px photo was already letterboxed to 1080, do NOT
# enhance the actual 600px detail and misrepresent it as a 1080px native shot.
fifth=clio/"05-official-mini-5g-handheld-600native-on-1080-QA.jpg"
shutil.copy2(official,fifth);assert sha(official)==sha(fifth)
clio_frames.append({"slot":5,"file":fifth.name,"sha256":sha(fifth),
  "source":str(official),"source_native_pixels":[600,600],
  "original_official_5g_product_ID":"0000006954",
  "not_native_1080":True,"new_picture_created":False,
  "visual_role":"official page hand holding one closed mini cushion",
  "exact_stock_shade_approved":False})
assert len(good_frames)==5 and len(clio_frames)==5
def emit_contact(family,frames):
 board=Image.new("RGB",(1830,487),"#f0f0ef")
 d=ImageDraw.Draw(board)
 d.text((15,14),f"v2789 {family} / PHOTO-ONLY 5 IMAGE QA / RETAIL HOLD",font=font,fill="#282828")
 for idx,f in enumerate(frames):
  p=OUT/family/f["file"]
  with Image.open(p) as im:
   im.load();assert im.size==(1080,1080) and im.format=="JPEG"
   thumb=im.convert("RGB").resize((337,337),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  f["bytes"]=p.stat().st_size
  x=14+idx*362
  board.paste(thumb,(x,64))
  d.text((x,415),f"FRAME {idx+1:02d}",font=font,fill="#313131")
 preview=OUT/f"v2789-{family}-contact.jpg"
 board.save(preview,"JPEG",quality=84,optimize=True)
 (OUT/f"v2789-{family}-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
emit_contact("pending-19",good_frames)
emit_contact("pending-04",clio_frames)
record={
 "version":"v2789","base":"v2788",
 "family_pending_19":{"product":"GOODAL Vita C Dark Spot Care Cream Alpha 50mL",
   "five_distinct_view_1080_JPGs_staged":True,"original_frames_1_to_4_unchanged":True,
   "fifth_real_source_macro_no_ad_banner":True,
   "four_unique_source_photographic_exposures_not_five":True,
   "frame3_unverified_claims_require_clearance":True,
   "frames":good_frames,"retail_approved":False},
 "family_pending_04":{"product":"CLIO Mesh Glow Essential Mini Cushion 5g",
   "five_source_photo_reference_JPGs_staged":True,
   "old_unverified_MK_badge_regions_removed_by_non-destructive_crop":True,
   "native_image_5_original_resolution":"600x600",
   "old_image_1_and_4_similar_case_angle":True,
   "confirmed_item_and_shade_edition_on_user_physical_stock":False,
   "actual_5g_photo_rights_held":True,
   "frames":clio_frames,"retail_approved":False},
 "old_verified_11_sales_families_untouched":True,
 "old_55_public_images_URLs_unchanged":True,
 "no_prior_v2706_v2788_original_overwrites":True,
 "newly_retail_approved":0,"final_XLSX_shared":False,
 "next":["Photo quality review 1:1 for 10 newly staged JPGs",
         "Physical item/shade capacity checks",
         "Actual source licensing and authentic MK logo before publication",
         "Continue other noncurated 05 06 07 08 12 pending families"]}
(OUT/"manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2789","new_QA_5_JPG_groups":2,
   "physically_staged_JPGs":10,"sale_approved":0}))
