#!/usr/bin/env python3
"""v2808: OBgE Oil Control Finisher 5g. Reuse 5 DISTINCT brand-gallery
photo/instruction scenes from v2807 without any re-encoding. Create 1
real machine-alpha product-only cutout from 01 brand hero, not a rectangle.

This is QA-only: owned stock variant, reuse license and MK logo unverified.
Never rewrite approved 11 families, their 55 URLs or earlier QA folders.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from rembg import new_session, remove
import hashlib, json, shutil, base64
ROOT=Path("qa-review")
SRC=ROOT/"v2807-two-official-single-item-product-photo-discovery"
DEST=ROOT/"v2808-obge-oil-finisher-five-official-scenes-true-alpha-QA"
assert SRC.is_dir() and not DEST.exists()
DEST.mkdir(parents=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((SRC/"manifest.json").read_text())
case=next(x for x in m["cases"] if x["family"]=="pending-09")
assert len(case["photos"])>=9
# These five are DIFFERENT recorded brand gallery scenes, not fabricated
# advertising claims, color swatches or independently cleared product images.
slots=[
 (1,1,"product case and included applicator","official standalone product photo"),
 (2,4,"puff and compact configuration","official branded promotion; claims remain unapproved"),
 (3,7,"puff application demonstration","official original instructions; no invented content"),
 (4,8,"product shown with person","official branded model scene; image license held"),
 (5,9,"application and directions","official branded instructions; no invented content"),
]
frames=[]
for slot,source_id,role,hold in slots:
 entry=case["photos"][source_id-1]
 source=SRC/entry["file"]
 assert source.is_file()
 target=DEST/f"{slot:02d}-actual-brand-gallery-{source_id:02d}-QA.jpg"
 shutil.copy2(source,target)
 assert sha(source)==sha(target)==entry["sha256"]
 with Image.open(target) as pic:
  pic.load();assert pic.format=="JPEG" and pic.size==(1080,1080)
 assert target.stat().st_size<2_000_000
 frames.append({"slot":slot,"brand_gallery_index":source_id,"role":role,"caution":hold,
  "filename":target.name,"source":str(source),"sha256":sha(target),
  "bytes":target.stat().st_size,"source_bytes_unchanged":True})
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
bf=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",31)
cutout={"status":"HOLD_NOT_ATTEMPTED"}
# Source #1 shows actual product, unlike earlier v2716 brown backplate.
source=SRC/case["photos"][0]["file"]
with Image.open(source) as img:
 img.load(); assert img.size==(1080,1080)
 rgba=img.convert("RGBA")
crop_box=(95,70,950,990)
crop=rgba.crop(crop_box)
try:
 model=new_session("isnet-general-use")
 isolated=remove(crop,session=model,alpha_matting=True,
    alpha_matting_foreground_threshold=230,
    alpha_matting_background_threshold=18,
    alpha_matting_erode_size=4)
 assert isolated.mode=="RGBA"
 alpha=isolated.getchannel("A")
 rect=alpha.getbbox();assert rect
 proportion=sum(x>=128 for x in alpha.getdata())/(isolated.width*isolated.height)
 assert .045<proportion<.78 and rect[2]-rect[0]>200 and rect[3]-rect[1]>280,(proportion,rect)
 isolated=isolated.crop(rect)
 png=DEST/"01-OBgE-5g-real-transparent-product-cutout-QA.png"
 isolated.save(png,optimize=True)
 canvas=Image.new("RGB",(1080,1080),"#ffffff")
 pen=ImageDraw.Draw(canvas)
 pen.rounded_rectangle((55,55,1024,1024),radius=36,outline="#ece6e2",width=2)
 pen.text((94,101),"OBgE",font=bf,fill="#3d3632")
 pen.text((94,157),"Oil Control Finisher 5g",font=f,fill="#7d6d65")
 fitted=ImageOps.contain(isolated,(850,774),Image.Resampling.LANCZOS)
 xy=((1080-fitted.width)//2,217+(774-fitted.height)//2)
 canvas.paste(fitted,xy,fitted)
 pen.text((94,982),"ACTUAL PHOTO CUTOUT | VISUAL QA ONLY",font=f,fill="#998f8b")
 jpg=DEST/"01-OBgE-5g-true-alpha-white-hero-1080-QA.jpg"
 canvas.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
 with Image.open(jpg) as v:
  v.load();assert v.format=="JPEG" and v.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000
 cutout={"status":"REAL_ALPHA_STAGED_VISUAL_QA_REQUIRED","source":str(source),
  "source_sha256":sha(source),"source_crop":list(crop_box),
  "alpha_coverage":round(proportion,4),"bbox":list(rect),
  "transparent_png":png.name,"jpg":jpg.name,"jpg_sha256":sha(jpg),
  "retail_approved":False}
except Exception as e:
 cutout={"status":"HOLD_MASK_TECHNICAL_REJECT","type":type(e).__name__,
  "error":str(e)[:200],"retail_approved":False}
# Visual proof panels. No fake source logo injected.
board=Image.new("RGB",(1850,500),"#f1f0ed")
d=ImageDraw.Draw(board)
d.text((15,17),"v2808 OBgE OFFICIAL 5 DISTINCT GALLERY SCENES | QA ONLY",font=f,fill="#292929")
for z in frames:
 with Image.open(DEST/z["filename"]) as pic:
  tile=pic.convert("RGB").resize((338,338),Image.Resampling.LANCZOS)
 xx=15+(z["slot"]-1)*367
 board.paste(tile,(xx,61))
 d.text((xx,416),f"SLOT {z['slot']:02d}   SRC {z['brand_gallery_index']:02d}",font=f,fill="#292929")
proof=DEST/"v2808-five-frame-proof.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(DEST/"v2808-five-frame-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
if cutout.get("jpg"):
 review=Image.new("RGB",(970,525),"#f1f0ed")
 with Image.open(source) as img:before=img.convert("RGB").resize((435,435),Image.Resampling.LANCZOS)
 with Image.open(DEST/cutout["jpg"]) as img:after=img.convert("RGB").resize((435,435),Image.Resampling.LANCZOS)
 review.paste(before,(20,62));review.paste(after,(510,62))
 ImageDraw.Draw(review).text((15,18),"v2808 Original source vs genuine neural cutout | HOLD retail",font=f,fill="#292929")
 p=DEST/"v2808-alpha-visual-proof.jpg";review.save(p,"JPEG",quality=86,optimize=True)
 (DEST/"v2808-alpha-visual-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
report={"version":"v2808","baseline":"v2807","family":"pending-09",
"product":"OBgE Oil Control Finisher 5g",
"five_1080_brand_source_scenes_saved":len(frames),
"original_five_photographic_source_bytes_preserved":True,
"true_transparent_alpha_preview":cutout,
"retail_approved":False,
"licensed_marketing_claims_or_model_photos":False,
"actual_owned_5g_stock_generation_verified":False,
"original_MK_logo_verified":False,
"old_11_approved_families_untouched":True,"old_55_public_urls_untouched":True,
"all_prior_QA_assets_untouched":True,"final_spreadsheet_shared":False,
"frames":frames,"next":"Visual check cutout; if bad reject only alpha, five physical brand originals remain. GOODAL 30mL 25AD stay on hold."}
(DEST/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2808","five_photo_references":len(frames),
"alpha_status":cutout["status"],"sale_approved":0}))
