#!/usr/bin/env python3
"""v2447 restore one MK-badge-free photographic main JPG for each of eight empty families.
Reuse five exact earlier successful JPEGs byte-identically; create ONLY three new photos
from visually observed exact source photo crops (no drawn product pixel or invented swatch).
Never presume commercial photo rights or physical package edition verified.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,shutil,zipfile
BASE=Path("prior-v2445b")
OUT=Path("v2447-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(sz,bold=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",sz)
def validate(p):
 with Image.open(p) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2000000,p
sources=[
 ("pending-03",(255,248,777,700),"MISSHA","M Perfect Cover BB Cream","50 mL","SOURCE_QA_HOLD"),
 ("pending-04",(218,263,759,743),"CLIO","Kill Cover Mesh Glow Mini","5 g","SHADE_GENERATION_QA_HOLD"),
 ("pending-25",(283,249,789,746),"BIOHEAL BOH","NAD-PRIZCELL Glow Boost Cream","50 mL","SOURCE_QA_HOLD")
]
results=[]
for gid,crop,brand,name,volume,status in sources:
 row=next(x for x in manifest["asset_rows"] if x["family"]==gid and x["slot"]==1)
 src=BASE/row["file"];assert src.is_file() and digest(src)==row["sha256"]
 with Image.open(src) as old:
  old.load()
  photograph=old.convert("RGB").crop(crop)
  # Actual photographic source colors/pixels retained, resized uniformly, no package inpainting.
  photo=ImageOps.contain(photograph,(730,650),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(canvas);ink=(46,65,56)
  d.text((65,52),brand,font=ff(39,True),fill=ink)
  size=44
  while size>=26 and d.textbbox((0,0),name,font=ff(size,True))[2]>955:size-=1
  assert size>=26
  d.text((65,115),name,font=ff(size,True),fill=ink)
  d.line((65,190,1015,190),fill=(184,191,185),width=2)
  canvas.paste(photo,((1080-photo.width)//2,222))
  d.line((65,913,1015,913),fill=(184,191,185),width=2)
  d.text((66,951),volume,font=ff(54,True),fill=ink)
  path=OUT/"eight-real-main-candidates"/gid/(gid+"_authentic-photo_no-MK_V2447.jpg")
  path.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(path,"JPEG",quality=94,optimize=True)
  validate(path)
  assert digest(src)==row["sha256"]
  results.append({"group_id":gid,"new_image":True,"source":row["file"],
   "source_SHA256":row["sha256"],"output":str(path.relative_to(OUT)),
   "output_SHA256":digest(path),"issue":status,"original_product_pixels_fabricated":False,
   "photographic_rights_confirmed":False,"stock_package_verified":False,
   "manual_visual_QA":"PENDING","sales_approved":False})
reused=[
 ("pending-11",Path("prior-v2437")/"sales-image-drafts/pending-11/pending-11_real_photo_copy_revision_V2437.jpg"),
 ("pending-15",Path("prior-v2437b")/"sales-image-drafts/pending-15/pending-15_actual_photo_copy_revised_V2437b.jpg"),
 ("pending-28",Path("prior-v2436b")/"sales-image-drafts/pending-28/PIXELPURE_full_jar_replacement_V2436b.jpg"),
 ("pending-29",Path("prior-v2436")/"sales-image-drafts/pending-29/pending-29_genuine-photo_no-MK_V2436.jpg"),
 ("pending-30",Path("prior-v2435b")/"sales-image-drafts/pending-30/PIXELPURE_Aura_Radiance_50ml_full_bottle_V2435b.jpg")
]
for gid,src in reused:
 assert src.is_file(),src
 validate(src)
 h=digest(src)
 target=OUT/"eight-real-main-candidates"/gid/(gid+"_previous_success_byteidentical_V2447.jpg")
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,target)
 assert digest(target)==h
 results.append({"group_id":gid,"new_image":False,"source":str(src),
 "source_SHA256":h,"output":str(target.relative_to(OUT)),"output_SHA256":h,
 "issue":"RIGHTS_AND_STOCK_QA_HOLD","original_product_pixels_fabricated":False,
 "photographic_rights_confirmed":False,"stock_package_verified":False,
 "manual_visual_QA":"Previously visually inspected; exact-byte preservation","sales_approved":False})
assert len(results)==8 and len(set(x["group_id"] for x in results))==8
report={"version":"2.4.47","source":"production-assets-v2446b-logo-64-quarantine-86-hold",
"previously_empty_families_receiving_real_nonMK_main_candidates":8,
"actual_new_photo_relayout_JPG":3,"prior_success_JPGs_reused_byte_identical":5,
"fake_product_photography_generated":0,"stock_version_or_photo_rights_confirmed":0,
"final_sale_approved":0,"prior_55_URLs_changed":0,"original_JPGs_overwritten":0,
"manual_visual_QA_new_thumbnails_after_generation":"PENDING",
"future_5frame_sets_still_blocked_by_logo_and_missing_photo_rights":True,
"results":results,"next":["Open and visually inspect all three newly cropped JPGs","Verify no MK seal by known positive-control image comparison","Preserve successful 5 prior exact bytes without redeveloping source photos",
"Continue source-based verified frame restoration for 8 blocked groups, not duplicate five nearly identical photos"]}
(OUT/"v2447_eight_family_mains_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2447_eight_nonMK_real_photo_main_candidates.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
 for r in results:z.write(OUT/r["output"],arcname=r["output"])
 z.write(OUT/"v2447_eight_family_mains_checkpoint.json",arcname="v2447_eight_family_mains_checkpoint.json")
with zipfile.ZipFile(OUT/"v2447_eight_nonMK_real_photo_main_candidates.zip") as z:assert len(z.namelist())==9 and z.testzip() is None
print(json.dumps({k:report[k] for k in ("version","previously_empty_families_receiving_real_nonMK_main_candidates","actual_new_photo_relayout_JPG","prior_success_JPGs_reused_byte_identical","final_sale_approved")},ensure_ascii=False),flush=True)
