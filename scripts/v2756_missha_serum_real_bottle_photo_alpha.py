#!/usr/bin/env python3
"""v2756: ONE genuinely new work item. MISSHA PDRN NAD+ Firming Repair Serum 30mL
authentic single-bottle source04 from previously saved official Korean gallery.
Never run previous slot01 facts card again. Do not touch any approved image or URL.
Save real alpha PNG/JPG and honest original-versus-derived QA contact.
No source rights/actual stock generation verified; never auto approve for retail.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from rembg import new_session, remove
import hashlib, json, base64
ROOT=Path("qa-review")
SRC=ROOT/"v2696-missha-serum-official-gallery-proof/source-04-REVIEW-ONLY.jpg"
OUT=ROOT/"v2756-missha-pdrn-serum-one-bottle-real-alpha"
assert SRC.is_file() and not OUT.exists(), "Do not redo or replace previous output"
OUT.mkdir(parents=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldpath="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(sz,bold=False):return ImageFont.truetype(boldpath if bold else fontpath,sz)
with Image.open(SRC) as im:
    im.load()
    assert im.format=="JPEG" and min(im.size)>=400
    photo=ImageOps.exif_transpose(im).convert("RGBA")
# The photographed single serum is centrally positioned in the official
# image; use a generous crop to keep complete dropper, bottle and base.
roi_xyxy=(round(photo.width*.10),round(photo.height*.01),
          round(photo.width*.88),round(photo.height*.99))
crop=photo.crop(roi_xyxy)
report={
 "version":"v2756","family":"pending-13",
 "product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
 "source_original_path":str(SRC),"source_original_sha256":digest(SRC),
 "source_original_dimensions":list(photo.size),
 "source_image_identity":"source04 SAME PRODUCT SINGLE 30mL SERUM; not information card",
 "source_original_bytes_unchanged":True,
 "old_failed_input_slot01_NOT_retried":True,
 "cropped_region_xyxy":list(roi_xyxy),
 "status":"HOLD_REAL_ALPHA_QA",
 "retail_approved":False,"output_png":None,"output_jpg":None
}
try:
    cut=remove(crop,session=new_session("isnet-general-use"),
        alpha_matting=True,alpha_matting_foreground_threshold=230,
        alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
    assert cut.mode=="RGBA"
    mask=cut.getchannel("A")
    bbox=mask.getbbox()
    if not bbox:raise ValueError("No foreground")
    coverage=sum(x>=128 for x in mask.getdata())/(cut.width*cut.height)
    assert .025<coverage<.82 and bbox[2]-bbox[0]>=95 and bbox[3]-bbox[1]>=200,(coverage,bbox)
    isolated=cut.crop(bbox)
    png=OUT/"pending-13-official-30mL-single-serum-true-alpha-QA.png"
    isolated.save(png,optimize=True)
    card=Image.new("RGB",(1080,1080),"#ffffff")
    d=ImageDraw.Draw(card)
    d.rounded_rectangle((54,54,1026,1026),radius=36,fill="#ffffff",outline="#ece6e8",width=2)
    d.text((95,94),"MISSHA",font=ft(45,True),fill="#42333c")
    d.text((95,160),"PDRN NAD+ Firming Repair Serum 30mL",font=ft(25),fill="#74666f")
    fitted=ImageOps.contain(isolated,(840,765),Image.Resampling.LANCZOS)
    card.paste(fitted,((1080-fitted.width)//2,223+(765-fitted.height)//2),fitted)
    d.text((95,989),"ORIGINAL SINGLE-PRODUCT PHOTO  |  QA ONLY",font=ft(19),fill="#958b90")
    jpg=OUT/"pending-13-official-serum-true-alpha-1080-QA.jpg"
    card.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    assert jpg.stat().st_size<2_000_000
    with Image.open(jpg) as check:check.load();assert check.format=="JPEG" and check.size==(1080,1080)
    report.update({"status":"REAL_ALPHA_PNG_AND_JPG_PRODUCED_VISUAL_QA_REQUIRED",
       "output_png":png.name,"output_jpg":jpg.name,
       "output_png_sha256":digest(png),"output_jpg_sha256":digest(jpg),
       "jpg_bytes":jpg.stat().st_size,"alpha_mask_coverage":round(coverage,4),
       "mask_bbox":list(bbox)})
except Exception as exc:
    report.update({"status":"HOLD_SEGMENTATION_NOT_RETAIL",
       "error_type":type(exc).__name__,"error":str(exc)[:220]})
side=Image.new("RGB",(1200,660),"#f1f0ef")
d=ImageDraw.Draw(side)
d.text((22,14),"v2756 MISSHA ONE 30mL SERUM | ORIGINAL LEFT / ACTUAL ALPHA RIGHT | QA ONLY",font=ft(22,True),fill="#2d2c2d")
left=ImageOps.contain(photo.convert("RGB"),(520,520),Image.Resampling.LANCZOS)
side.paste(left,((550-left.width)//2,80+(520-left.height)//2))
if report["output_jpg"]:
    with Image.open(OUT/report["output_jpg"]) as im:right=im.convert("RGB").resize((520,520),Image.Resampling.LANCZOS)
    side.paste(right,(630,80))
d.text((20,620),report["status"],font=ft(18),fill="#565056")
proof=OUT/"v2756-official-serum-original-vs-actual-alpha.jpg"
side.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2756-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report.update({
 "photo_redistribution_license_proven":False,
 "owned_30mL_stock_generation_verified":False,
 "approved_round_MK_logo_verified":False,
 "new_retail_approved":0,
 "prior_11_approved_product_families_untouched":True,
 "prior_55_public_urls_untouched":True,
 "prior_all_photo_and_qa_artifacts_untouched":True,
 "final_XLSX_shared":False
})
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2756","real_new_alpha_pair_created":bool(report["output_jpg"]),
 "status":report["status"],"sale_approved":0}))
