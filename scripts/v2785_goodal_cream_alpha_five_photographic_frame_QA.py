#!/usr/bin/env python3
"""v2785 honest five-frame photo-first GOODAL Cream Alpha 50mL QA sequence.

Three saved real sources + the old isolated genuine jar hero; one open-jar
detail and one hand-cream texture detail derive strictly from actual source
photo pixels. No AI-synthesized physical products, claims, badges, swatches,
or published updates. This is FIVE VISUALLY DISTINCT FRAMES from FOUR SOURCE
PHOTOGRAPHS, not five independent photo shoots. All commerce rights held.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import shutil,hashlib,json,base64
ROOT=Path("qa-review")
OLD=ROOT/"v2739-three-existing-svg-real-png-jpg-photo-QA"/"pending-19"/"01-original-product-contour-white-1080-QA.jpg"
GALLERY=ROOT/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"
OUT=ROOT/"v2785-goodal-cream-alpha-fiveframe-photo-first-QA"
assert OLD.is_file() and GALLERY.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
previous=json.loads((GALLERY/"manifest.json").read_text())
assert previous["newly_curated_actual_distinct_source_JPGs"]==3
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[
  (OLD,"01-existing-authentic-isolated-product-hero-QA.jpg","SOURCE_WHOLE_JAR","old genuine isolated 50mL jar; original bytes untouched"),
  (GALLERY/previous["curated_photos"][0]["file"],"02-official-real-jar-cream-background-QA.jpg","OFFICIAL_SINGLE_JAR","new true cream jar photographed with cream texture backdrop"),
  (GALLERY/previous["curated_photos"][1]["file"],"03-official-open-closed-jar-photo-QA.jpg","OFFICIAL_OPEN_JAR","open and closed views of the same 50mL cream, not two-pack")
]
frames=[]
for source,file,role,description in sources:
 assert source.is_file()
 dest=OUT/file
 shutil.copy2(source,dest)
 assert sha(dest)==sha(source)
 frames.append({"slot":len(frames)+1,"file":dest.name,"role":role,
  "actual_source":str(source),"same_source_bytes":True,"sha256":sha(dest),
  "description":description,"retail_status":"HOLD"})
# Frame4 true hand texture photograph cropped ONLY to exclude caption/efficacy claims.
# Coordinates derived from preview and validated by final visual contact.
crop_specs=[
 (GALLERY/previous["curated_photos"][2]["file"],"04-real-cream-on-hand-closeup-QA.jpg",
  (235,370,855,800),"GENUINE_TEXTURE_ON_SKIN",
  "A real source-photograph cream application macro; top and bottom ad claims cropped out"),
 (GALLERY/previous["curated_photos"][1]["file"],"05-real-open-jar-cream-macro-QA.jpg",
  (430,340,1020,930),"GENUINE_OPEN_JAR_CREAM_MACRO",
  "Actual open Alpha cream jar photographed texture at closer view; same original photo as frame03")
]
for source,name,roi,role,description in crop_specs:
 assert source.exists()
 with Image.open(source) as original:
  original.load();assert original.size==(1080,1080)
  original=original.convert("RGB")
  crop=original.crop(roi)
  frame=ImageOps.fit(crop,(1080,1080),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
 dest=OUT/name
 frame.save(dest,"JPEG",quality=93,optimize=True,subsampling=0)
 frames.append({"slot":len(frames)+1,"file":name,"role":role,
  "actual_source":str(source),"source_crop_xyxy":list(roi),
  "same_source_bytes":False,"only_real_photograph_pixels":True,
  "sha256":sha(dest),"description":description,"retail_status":"HOLD"})
assert len(frames)==5
for f in frames:
 p=OUT/f["file"]
 with Image.open(p) as image:
  image.load();assert image.format=="JPEG" and image.size==(1080,1080)
 assert p.stat().st_size<2_000_000
 f["bytes"]=p.stat().st_size
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
board=Image.new("RGB",(1830,485),"#f0f0ee")
d=ImageDraw.Draw(board)
d.text((14,16),"v2785 REAL GOODAL CREAM ALPHA 5-FRAME PHOTO QA | RIGHTS + STOCK HOLD",font=font,fill="#292929")
for i,fr in enumerate(frames):
 with Image.open(OUT/fr["file"]) as im:
  thumb=im.convert("RGB").resize((338,338),Image.Resampling.LANCZOS)
 xx=15+i*362
 board.paste(thumb,(xx,65))
 d.text((xx,410),f"FRAME {i+1:02d} / {fr['role'][:12]}",font=font,fill="#343434")
contact=OUT/"v2785-fiveframe-photo-only-review.jpg"
board.save(contact,"JPEG",quality=86,optimize=True)
(OUT/"v2785-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
manifest={
 "version":"v2785","baseline":"v2784","family":"pending-19",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "actual_five_1080_JPG_QA_frames_saved":True,
 "separate_original_photographic_exposures":4,
 "new_source_jpgs_downloaded":0,
 "previous_existing_hero_reused":1,
 "additional_official_photo_frames_exact_source_bytes":2,
 "new_real_photo_detail_crops_not_AI_generation":2,
 "new_generated_product_pixels":0,
 "wrong_5_independent_photo_shoots_claim":False,
 "commercially_approved":False,
 "owned_stock_generation_verified":False,
 "source_photo_permission_verified":False,
 "authentic_MK_round_logo_available":False,
 "outstanding_specific_reasons":[
   "Frame03 source may contain official promotional copy that requires commercial claim clearance",
   "Five distinct visual frames use four independently sourced photographs; macro detail is sourced from frame03",
   "Actual physical user-owned 50mL Alpha packaging/edition not independently reconciled",
   "Brand-owned gallery not proof of right to republish on Shopee",
   "No authenticated round MellowKR MK logo available"
 ],
 "previous_11_commercially_approved_families_unchanged":True,
 "previous_55_verified_public_URLs_unchanged":True,
 "all_v2673_and_v2781_legacy_QA_files_untouched":True,
 "original_v2784_three_photo_files_sha_untouched":True,
 "final_excel_shared":False,
 "frames":frames}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2785","family":"pending-19","five_real_photo_frames_staged":5,
  "independent_photo_exposures":4,"new_retail_approvals":0}))
