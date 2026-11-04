#!/usr/bin/env python3
"""v2601: Four distinct photo-backed customer-image *review-only* replacements.
Existing 156 source JPEGs are immutable. Source photographs are real photos
from the latest already-vetted corpus, no package redraw or generated fake
product. Final MK logo, commercial photo rights and stock edition remain HOLD.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat, ImageChops
import json,hashlib,shutil

BASE=Path("review/review-JPG-by-family")
OUT=Path("v2601-four-photo-backed-product-info-QA")
OUT.mkdir(exist_ok=True)
INV=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
BY_ID={r["family_id"]:r for r in INV["pending_families"]}
CASES=[
 {"family":"pending-12","original_slot":3,"candidate_slot":4,
  "brand":"MISSHA","title":"RENEW PEEL SHOT 25",
  "copy":"PDRN NAD+  |  15 mL","color":(117,54,65),
  "bg":(250,246,245),"cropped_bottom":730},
 {"family":"pending-13","original_slot":4,"candidate_slot":1,
  "brand":"MISSHA","title":"FIRMING REPAIR SERUM",
  "copy":"PDRN NAD+  |  30 mL","color":(94,58,79),
  "bg":(249,245,249),"cropped_bottom":900},
 {"family":"pending-14","original_slot":1,"candidate_slot":5,
  "brand":"MISSHA","title":"FIRMING REPAIR CREAM",
  "copy":"PDRN NAD+  |  70 mL","color":(105,60,90),
  "bg":(249,243,247),"cropped_bottom":900},
 {"family":"pending-28","original_slot":2,"candidate_slot":5,
  "brand":"PIXEL PURE","title":"GLOW CLEANSING SERUM PAD",
  "copy":"210 mL  |  70 PADS","color":(56,99,87),
  "bg":(244,250,248),"cropped_bottom":900},
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,heavy=False:ImageFont.truetype(BOLD if heavy else FONT,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for case in CASES:
 family=case["family"]
 originals=sorted((BASE/family).glob("*.jpg"))
 assert len(originals)==5
 orig=[p for p in originals if int(p.name[:2])==case["original_slot"]]
 assert len(orig)==1
 orig=orig[0]
 im=Image.open(orig).convert("RGB")
 assert im.size==(1080,1080)
 cropped=case["cropped_bottom"]
 scene=Image.new("RGB",(1080,1080),case["bg"])
 scene.paste(im.crop((0,0,1080,cropped)),(0,0))
 d=ImageDraw.Draw(scene)
 fade_start=650 if family=="pending-12" else 730
 fade_span=145 if family=="pending-12" else 210
 for y in range(fade_start,1080):
  a=min(1,max(0,(y-fade_start)/fade_span))**1.35
  if y<cropped:
   from_photo=scene.crop((0,y,1080,y+1))
   background=Image.new("RGB",(1080,1),case["bg"])
   scene.paste(Image.blend(from_photo,background,a),(0,y))
  else:
   d.line((0,y,1079,y),fill=case["bg"])
 d=ImageDraw.Draw(scene)
 accent=case["color"]
 dark=tuple(int(x*.7) for x in accent)
 d.rounded_rectangle((65,830,255,873),radius=15,fill=accent)
 d.text((82,837),"PRODUCT DETAIL",font=font(17,True),fill="white")
 title_size=43 if len(case["title"])>24 else 54
 d.text((65,894),case["title"],font=font(title_size,True),fill=dark)
 d.text((67,971),case["copy"],font=font(31),fill=accent)
 saved=OUT/(family+"-slot"+str(case["candidate_slot"]).zfill(2)+"-photo-backed-QA.jpg")
 scene.save(saved,"JPEG",quality=92,subsampling=0,optimize=True)
 assert saved.stat().st_size<2000000 and Image.open(saved).size==(1080,1080)
 # Report candidate vs intended prior scene; no unreviewed replacement.
 old=[p for p in originals if int(p.name[:2])==case["candidate_slot"]]
 assert len(old)==1
 # Source scene itself is genuine existing image; this new layout reuses those pixels.
 row={"family":family,"candidate_slot":case["candidate_slot"],
  "reference_original_photo_slot":case["original_slot"],
  "reference_original_sha256":sha(orig),"previous_candidate_sha256":sha(old[0]),
  "new_candidate_sha256":sha(saved),"candidate_jpg":saved.name,
  "size_bytes":saved.stat().st_size,
  "source_photo_same_family":True,"old_edition_matching_stock_physical_label_verified":False,
  "picture_reuse_rights_confirmed":False,"original_mk_logo_applied":False,
  "final_sale_approved":False}
 rows.append(row)
assert len(rows)==4
manifest={"version":"v2601","base_run":41765900358,
 "prior_fact_only_run":41767372681,
 "new_product_photo_backed_QA_cuts":4,
 "new_customer_image_photo_sources":4,
 "previous_156_source_JPEGs_overwritten":0,
 "old_11_published_groups_overwritten":0,"verified_55_live_urls_changed":0,
 "new_live_urls":0,"xlsx_created_or_shared":False,
 "external_rights_verified":False,"actual_owned_stock_edition_verified":False,
 "actual_MK_original_logo_applied":False,
 "review_cut_release":"HOLD_UNTIL_PHOTO_RIGHTS_STOCK_LOGO_FINAL_VISUAL_APPROVAL",
 "scenes":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_JPG":4,"existing_source_images_modified":0,
  "commercially_released":0,"xlsx_shared":False}))
