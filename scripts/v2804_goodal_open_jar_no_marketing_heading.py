#!/usr/bin/env python3
"""v2804 correct only GOODAL Cream Alpha 50mL frame 02.
The previous cropped photo retained clipped "Results" promotional heading.
Reframe the previously verified actual open-jar photo, below large heading
and above the small bottom marketing paragraph. Do not invent pixels.
Frames 01,03,04,05 must remain byte-for-byte identical to v2803.
NO customer-facing release, no change to 11 approved groups or 55 URLs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("qa-review")
OLD=ROOT/"v2803-goodal-alpha-hand-texture-without-clipped-claim-QA"
SOURCES=ROOT/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"
OUT=ROOT/"v2804-goodal-alpha-open-jar-no-clipped-marketing-copy-QA"
assert OLD.is_dir() and SOURCES.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OLD/"manifest.json").read_text())
assert m["version"]=="v2803" and len(m["frames"])==5
src=SOURCES/"02-original-PHOTOGRAPHIC_OPEN_JAR_AND_CREAM-QA.jpg"
assert sha(src)=="05f61715a52e968fb94fc37e12213c975cd038c23dc75962d9078f19f6ef15b5"
with Image.open(src) as image:
 image.load();assert image.format=="JPEG" and image.size==(1080,1080)
 # Original source preserved: explicit photographic open-jar region.
 # Upper large "Faster Visible Results" line and lower caption excluded.
 crop_box=(340,485,1065,925)
 photo=image.convert("RGB").crop(crop_box)
 square=Image.new("RGB",(1080,1080),"#ffffff")
 fitted=ImageOps.contain(photo,(1012,990),Image.Resampling.LANCZOS)
 square.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
 new=OUT/"02-GOODAL-Alpha-open-jar-no-marketing-heading-QA.jpg"
 square.save(new,"JPEG",quality=94,optimize=True,subsampling=0)
assert new.stat().st_size<2_000_000
files=[]
for prev in m["frames"]:
 slot=prev["slot"]
 if slot==2:
  dest=new
  status="ONE_ACTUAL_PHOTO_CROP_REPLACED_NO_CLAIM_TEXT"
 else:
  srcprior=OLD/prev["file"]
  assert sha(srcprior)==prev["sha256"],(slot,"source mismatch")
  dest=OUT/srcprior.name
  shutil.copy2(srcprior,dest)
  assert sha(dest)==sha(srcprior)
  status="V2803_EXACT_BYTES_PRESERVED"
 with Image.open(dest) as chk:
  chk.load();assert chk.format=="JPEG" and chk.size==(1080,1080)
 assert dest.stat().st_size<2_000_000
 files.append({"slot":slot,"file":dest.name,"sha256":sha(dest),"bytes":dest.stat().st_size,
  "integrity":status,"retail_approved":False})
assert len(files)==5 and len({x["sha256"] for x in files})==5
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(FONT,22)
board=Image.new("RGB",(1860,500),"#f2f1ee")
draw=ImageDraw.Draw(board)
draw.text((14,14),"v2804 GOODAL Cream Alpha 50mL / 1 OPEN-JAR PHOTO CROP FIX + 4 EXACTLY PRESERVED / QA ONLY",
 font=font,fill="#303030")
for i,item in enumerate(files):
 with Image.open(OUT/item["file"]) as photo:
  tile=photo.convert("RGB").resize((336,336),Image.Resampling.LANCZOS)
 x=16+i*369
 board.paste(tile,(x,62))
 draw.text((x,425),f"FRAME {item['slot']:02d}  "+("NEW DETAIL" if item["slot"]==2 else "UNCHANGED"),
  font=font,fill="#353535")
proof=OUT/"v2804-photo-proof-5-JPG.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2804-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2804","baseline":"v2803",
 "family":"pending-19","product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "actual_five_1080_JPGs_saved":5,"single_slot_fixed":2,
 "previous_four_JPGs_SHA_preserved":True,
 "issue_resolved_for_review":"Removed clipped word Results from slot 02 source crop; frame 03 remains prior corrected clean hand texture",
 "official_product_photo_original":str(src),"original_photo_sha256":sha(src),
 "new_crop_region_xyxy":list(crop_box),
 "new_crop_is_source_photo_pixels_not_independent_4th_photo":True,
 "marketing_copy_automatically_reused":False,
 "other_QA_files_untouched":True,"all_original_photo_sources_untouched":True,
 "original_MK_logo_authenticated":False,"photo_commercial_use_rights_verified":False,
 "physical_stock_generation_verified":False,"sale_approved":False,
 "approved_11_families_untouched":True,"published_55_URLs_untouched":True,
 "final_excel_shared":False,"frames":files
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2804","JPGs":5,"changed_photo_crop_slots":1,
 "exact_old_JPG_preserved":4,"commercially_approved":0}))
