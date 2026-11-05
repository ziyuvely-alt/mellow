#!/usr/bin/env python3
"""v2855: Correct decorative red alpha residue beside MISSHA 30mL serum dropper.
Edit ONLY a new QA candidate; immutable v2801 5-JPG set and all public URLs.
Use existing RGB and alpha; deterministic feathered matte only, no AI reprocessing.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,hashlib,json,math

R=Path("qa-review")
SRC=R/"v2801-missha-pdrn-serum-30ml-real-single-bottle-alpha-and-five-frame-QA"
OUT=R/"v2855-missha30ml-dropper-residue-precision-alpha-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir()
src_png=SRC/"01-actual-single-bottle-transparent-foreground-QA.png"
src_hero=SRC/"01-final-QA-real-single-serum-photo.jpg"
assert src_png.is_file() and src_hero.is_file()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_png_sha=sha(src_png)
original_hero_sha=sha(src_hero)
with Image.open(src_png) as im:
 im.load();original=im.convert("RGBA")
w,h=original.size
assert 200<=w<=1080 and 500<=h<=1080,(w,h)
rgb=np.asarray(original.convert("RGB")).copy()
before=np.asarray(original.getchannel("A")).astype(np.float32)
yy,xx=np.mgrid[0:h,0:w]
# Only upper-right side of white dropper cap. This fixes known bright-red
# detached decoration. Preserve all original RGB and the bottle below neck.
# Signed distance to a linearly widening allowed silhouette boundary.
right_limit=np.interp(yy.astype(np.float32),
 [0,0.12*h,0.18*h,0.225*h,0.30*h,h],
 [0.65*w,0.66*w,0.71*w,0.80*w,1.01*w,1.01*w])
# 10px anti-aliased taper; all rows beyond 30% image height unchanged.
clearance=(right_limit-xx)/10.0
clip=np.clip(clearance,0,1)
clip=clip*clip*(3-2*clip)
after=np.rint(before*clip).astype(np.uint8)
removed=int((before-after).sum()/255)
affected=int(np.count_nonzero(before!=after))
assert affected>0,"No red upper-right decoration was affected"
assert np.array_equal(after[round(.34*h):],before[round(.34*h):].astype(np.uint8))
assert np.array_equal(rgb,np.asarray(original.convert("RGB")))
# Prevent massive destructive mask correction, intentionally small local repair.
assert affected < w*h*.035,(affected,w*h)
corrected=Image.fromarray(np.dstack((rgb,after)),"RGBA")
png=OUT/"01-MISSHA30ml-dropper-residue-cleaned-original-RGB-QA.png"
corrected.save(png,optimize=True)
# Alpha composite on white. Keep entire bottle plus cap inside >= 35px margin.
bbox=Image.fromarray(after,"L").getbbox()
assert bbox and bbox[2]>bbox[0] and bbox[3]>bbox[1]
part=corrected.crop(bbox)
target=Image.new("RGB",(1080,1080),"white")
fit=ImageOps.contain(part,(910,930),Image.Resampling.LANCZOS)
x=(1080-fit.width)//2;y=68+(930-fit.height)//2
target.paste(fit,(x,y),fit.getchannel("A"))
name="01-MISSHA30ml-clean-foreground-1080-QA.jpg"
dest=OUT/name
target.save(dest,"JPEG",quality=94,optimize=True,subsampling=0)
assert dest.stat().st_size<2_000_000
with Image.open(dest) as im:im.load();assert im.size==(1080,1080) and im.format=="JPEG"
# Human QA visual contact, before and after side-by-side, no fake logo.
def composite_on_white(image):
 base=Image.new("RGBA",image.size,"white");base.alpha_composite(image)
 return base.convert("RGB")
board=Image.new("RGB",(1510,840),"#f2f0ef")
draw=ImageDraw.Draw(board)
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
bf=ImageFont.truetype(bold,25)
sf=ImageFont.truetype(font,20)
draw.text((20,12),"v2855 MISSHA PDRN NAD+ 30mL | upper-right dropper alpha residue | QA ONLY",fill="#322c34",font=bf)
for i,arr in enumerate([original,corrected]):
 preview=ImageOps.contain(composite_on_white(arr),(675,715),Image.Resampling.LANCZOS)
 board.paste(preview,(30+745*i+(675-preview.width)//2,76+(715-preview.height)//2))
draw.text((30,791),"BEFORE: original v2801 alpha",fill="#645c64",font=sf)
draw.text((770,791),"AFTER: isolated local alpha cleanup; original RGB preserved",fill="#645c64",font=sf)
board.save(OUT/"v2855-before-after-visual-QA.jpg","JPEG",quality=87,optimize=True)
assert sha(src_png)==original_png_sha and sha(src_hero)==original_hero_sha
report={"version":"v2855","baseline":"v2854","family":"pending-13",
 "product":"MISSHA Camellia PDRN + NAD+ Firming Repair Serum 30mL",
 "original_png":str(src_png),"original_png_sha256":original_png_sha,
 "original_hero":str(src_hero),"original_hero_sha256":original_hero_sha,
 "original_alpha_dimensions":[w,h],
 "correction":"Only upper-right cap perimeter alpha; no RGB pixel regeneration, no model inference",
 "source_rgb_bytes_exact_after_render":True,
 "affected_alpha_pixels":affected,"approx_removed_255_equivalent_pixels":removed,
 "new_alpha_png":png.name,"new_alpha_png_sha256":sha(png),
 "new_JPG_1080":name,"new_JPG_SHA256":sha(dest),"new_jpg_bytes":dest.stat().st_size,
 "old_five_frame_QA_set_preserved":True,"old_11_sale_approved_families_preserved":True,
 "old_55_public_URLs_preserved":True,
 "new_sales_approvals":0,"mask_human_edge_review":"PENDING",
 "unverified_photo_license":True,"owned_exact_stock_edition_unverified":True,
 "original_MK_logo_authenticated":False,"new_public_URLs":0,
 "final_spreadsheet_shared":False,"status":"PRECISION_ALPHA_CANDIDATE_HOLD_SALES",
 "next":"Review new cap edge and main-bottle silhouette at 100%; no automatic commercial release."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2855","corrected":True,"alpha_pixels_changed":affected,"JPG_bytes":dest.stat().st_size,"status":report["status"]}))
