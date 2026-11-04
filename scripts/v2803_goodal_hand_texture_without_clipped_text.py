#!/usr/bin/env python3
"""v2803: targeted human-QA correction of one GOODAL Cream Alpha 50mL frame.

Prior v2802 frame03 accidentally retained clipped words ("yet Gentle")
from a brand-owned marketing overlay. Build a replacement from the ALREADY
PRESERVED original photographic hand+cream source, excluding both the
headline and marketing paragraph. Preserve frames 01,02,04,05 byte-for-byte.
Never invent product pixels, claims, color variants, or an MK logo.
No public releases or spreadsheet.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,shutil,json,base64
BASE=Path("qa-review")
OLD=BASE/"v2802-goodal-alpha-three-authentic-scenes-two-explicit-detail-crops-QA"
SOURCES=BASE/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"
OUT=BASE/"v2803-goodal-alpha-hand-texture-without-clipped-claim-QA"
assert OLD.is_dir() and SOURCES.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
shasum=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((OLD/"manifest.json").read_text())
assert prior["version"]=="v2802" and len(prior["frames"])==5
original=SOURCES/"03-original-PHOTOGRAPHIC_HAND_TEXTURE-QA.jpg"
assert shasum(original)=="351984d89e0bf23d7cc411d73fa479ae46c20428cd3cb42f3eb9b625554ce17a"
with Image.open(original) as src:
 src.load();assert src.format=="JPEG" and src.size==(1080,1080)
 source=src.convert("RGB").copy()
# Real hand/cream occupies the central/lower photo, while the upper headline
# and bottom claim are OUTSIDE of this crop. Nothing is inpainted.
crop_box=(285,415,1065,820)
detail=source.crop(crop_box)
canvas=Image.new("RGB",(1080,1080),"white")
fit=ImageOps.contain(detail,(1010,820),Image.Resampling.LANCZOS)
canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
corrected=OUT/"03-GOODAL-Alpha-real-hand-cream-no-claim-QA.jpg"
canvas.save(corrected,"JPEG",quality=94,optimize=True,subsampling=0)
assert corrected.stat().st_size<2000000
files=[]
for prior_item in prior["frames"]:
 slot=prior_item["slot"]
 if slot==3:
  dest=corrected
  status="NEW_CROP_OF_AUTHENTIC_HAND_PHOTO_WITHOUT_TEXT"
 else:
  source_old=OLD/prior_item["JPG"]
  assert shasum(source_old)==prior_item["JPG_sha256"],(slot,source_old)
  dest=OUT/source_old.name
  shutil.copy2(source_old,dest)
  assert shasum(dest)==shasum(source_old)
  status="BYTE_FOR_BYTE_PRESERVED_FROM_V2802"
 with Image.open(dest) as jpg:
  jpg.load();assert jpg.format=="JPEG" and jpg.size==(1080,1080)
 assert dest.stat().st_size<2000000
 files.append({"slot":slot,"file":dest.name,"sha256":shasum(dest),
  "bytes":dest.stat().st_size,"status":status,"retail_approved":False})
assert len(files)==5 and len({x["sha256"] for x in files})==5
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(FONT,22)
contact=Image.new("RGB",(1855,500),"#f2f1ef")
draw=ImageDraw.Draw(contact)
draw.text((16,14),"v2803 GOODAL ALPHA 50mL: CLEAN HAND-TEXTURE REPLACEMENT, 4 FILES UNCHANGED | QA ONLY",
  font=font,fill="#292929")
for i,row in enumerate(files):
 with Image.open(OUT/row["file"]) as jpg:
  thumbnail=jpg.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
 xx=15+i*369
 contact.paste(thumbnail,(xx,62))
 draw.text((xx,420),f'FRAME {row["slot"]:02d} '+("CROP FIX" if row["slot"]==3 else "PRESERVED"),
   font=font,fill="#393438")
proof=OUT/"v2803-5-real-image-sources-human-qa-contact.jpg"
contact.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2803-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2803","baseline":"v2802","family":"pending-19",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "actual_five_JPGs_saved":5,"exact_previous_frames_preserved":4,
 "fixed_slot":3,"reason":"v2802 frame03 cropped the phrase 'yet Gentle' from a marketing headline",
 "source_photo":str(original),"original_source_sha256":shasum(original),
 "selected_crop_original_xyxy":list(crop_box),
 "crop_excludes_top_heading":True,"crop_excludes_bottom_marketing_paragraph":True,
 "actual_photo_scene":"human fingers with real cream texture",
 "new_photo_pixels_fabricated":False,
 "original_photographic_JPGs_modified":False,
 "previous_v2802_five_frame_set_untouched":True,
 "commercial_photo_redistribution_permission_verified":False,
 "actual_owned_stock_50mL_edition_verified":False,
 "approved_original_MK_logo_available":False,
 "new_retail_sale_approvals":0,
 "previous_11_approved_families_unchanged":True,
 "previous_55_public_URLs_unchanged":True,
 "final_XLSX_or_spreadsheet_shared":False,
 "frames":files
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2803","qa_five_jpgs":len(files),"corrected_slot":3,
 "prior_frames_byte_preserved":4,"retail_approved":0}))
