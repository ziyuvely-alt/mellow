#!/usr/bin/env python3
"""Shopee v2761. Two SPECIFIC previously rejected product-image improvement tasks.

(A) PERIPERA old Ink Mood Glowy Tint 19 Mauve Chaos:
    crop an already archived exact-shade source panel, excluding RHS text,
    lip photograph, and the wrong half. True-alpha mask on that product panel.
    This is a source-photo detail QA candidate, not a clean no-swatch packshot.
(B) MISSHA PDRN NAD+ Firming Repair Serum 30mL:
    switch from old source04 (has round red decorative circle) to existing
    source03 exact single serum + original dropper photograph.

Both products, their photos and their other staged files are immutable.
NEVER infer retail or photo copyright approval from segmentation.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,base64,json
ROOT=Path("qa-review")
DEST=ROOT/"v2761-peripera19-no-lip-panel-and-missha30ml-source03-qa"
assert not DEST.exists()
DEST.mkdir(parents=True)
src19=ROOT/"v2760-peripera-18-19-alternate-actual-photo-alpha/shade-19/19-alternate-actual-photograph.jpg"
src13=ROOT/"v2696-missha-serum-official-gallery-proof/source-03-REVIEW-ONLY.jpg"
assert src19.is_file() and src13.is_file()
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(sz,b=False):return ImageFont.truetype(B if b else F,sz)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[
  {"family":"pending-08","shade":"19","brand":"PERIPERA",
    "product":"Old Ink Mood Glowy Tint #19 Mauve Chaos",
    "source":src19,"crop":(0,0,400,800),
    "photo_role":"EXACT_SHADE_PRODUCT_AND_SWATCH_DETAIL_EXCLUDES_ALL_LIP_AND_TITLE_PANEL",
    "release_hold":"Colour swatch decoration may remain behind bottle; needs full-size visual QA. Old K-ookie packaging and photo rights unverified."},
  {"family":"pending-13","shade":None,"brand":"MISSHA",
    "product":"PDRN NAD+ Firming Repair Serum 30mL",
    "source":src13,"crop":None,
    "photo_role":"OFFICIAL_SAME_30ML_SERUM_WITH_APPLICATOR_FROM_SOURCE03_NO_RED_DECORATIVE_CIRCLE",
    "release_hold":"Dropper top may be off source photo edge; distinguish pictured pipette from extra bottle. Stock edition and photo reuse rights unverified."},
]
model=new_session("isnet-general-use")
rows=[]
for spec in cases:
 src=spec["source"]
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and min(im.size)>=400
  whole=ImageOps.exif_transpose(im).convert("RGBA")
 rect=spec["crop"] or (0,0,whole.width,whole.height)
 assert rect[2]<=whole.width and rect[3]<=whole.height
 inp=whole.crop(rect)
 label=spec["shade"] or "serum"
 row={
 "family":spec["family"],"shade":spec["shade"],"product":spec["product"],
 "source":str(src),"source_sha256":sha(src),"original_source_dimensions":list(whole.size),
 "cropped_source_xyxy":list(rect),"composition_role":spec["photo_role"],
 "release_hold":spec["release_hold"],"retail_approved":False,
 "status":"HOLD_SEGMENTATION_OR_VISUAL_QA","output_png":None,"output_jpg":None
 }
 try:
  foreground=remove(inp,session=model,alpha_matting=True,
   alpha_matting_foreground_threshold=230,
   alpha_matting_background_threshold=18,
   alpha_matting_erode_size=4)
  assert foreground.mode=="RGBA"
  alpha=foreground.getchannel("A")
  bbox=alpha.getbbox()
  if bbox is None:raise ValueError("No foreground")
  alpha_coverage=sum(z>=128 for z in alpha.getdata())/(alpha.width*alpha.height)
  if not (.018<alpha_coverage<.85 and bbox[2]-bbox[0]>85 and bbox[3]-bbox[1]>175):
   raise ValueError(f"Unusable mask coverage or bbox: {alpha_coverage:.4f}, {bbox}")
  corners=[alpha.getpixel(p) for p in ((0,0),(alpha.width-1,0),(0,alpha.height-1),(alpha.width-1,alpha.height-1))]
  sub=DEST/("shade-19" if spec["shade"] else "pending-13")
  sub.mkdir()
  trimmed=foreground.crop(bbox)
  png=sub/(label+"-source-detail-genuine-alpha-QA.png")
  trimmed.save(png,optimize=True)
  jpg=sub/(label+"-exact-photo-detail-1080-QA.jpg")
  hero=Image.new("RGB",(1080,1080),"#ffffff")
  d=ImageDraw.Draw(hero)
  d.rounded_rectangle((56,54,1024,1027),radius=34,fill="#ffffff",outline="#e9e4e8",width=2)
  d.text((96,96),spec["brand"],font=ft(43,True),fill="#342f36")
  size=29
  while d.textbbox((0,0),spec["product"],font=ft(size))[2]>870 and size>18:size-=1
  d.text((96,160),spec["product"],font=ft(size),fill="#796d75")
  fitted=ImageOps.contain(trimmed,(848,758),Image.Resampling.LANCZOS)
  hero.paste(fitted,((1080-fitted.width)//2,226+(758-fitted.height)//2),fitted)
  d.text((96,992),"AUTHENTIC SOURCE-PHOTO DETAIL  |  QA, NOT RETAIL",font=ft(18),fill="#9d9499")
  hero.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
  with Image.open(jpg) as check:
   check.load()
   assert check.format=="JPEG" and check.size==(1080,1080)
  if jpg.stat().st_size>=2000000:raise ValueError("Output JPG >=2MB")
  row.update({
    "status":"QA_ASSET_SAVED_NEEDS_VISUAL_REVIEW",
    "output_png":str(png.relative_to(DEST)),
    "output_jpg":str(jpg.relative_to(DEST)),
    "png_sha256":sha(png),"jpg_sha256":sha(jpg),
    "JPG_bytes":jpg.stat().st_size,
    "alpha_coverage":round(alpha_coverage,4),
    "source_foreground_bbox":list(bbox),
    "source_crop_corner_alpha":corners,
    "not_clean_packshot_claimed":True
  })
 except Exception as exc:
  row.update({"status":"HOLD_MODEL_OR_SOURCE_BAD","failure_type":type(exc).__name__,
   "reason":str(exc)[:200]})
 rows.append(row)
board=Image.new("RGB",(1460,1048),"#f0f0ee")
d=ImageDraw.Draw(board)
d.text((20,17),"v2761 TWO DIFFERENT PHOTO-COMPOSITION FIXES | ORIGINAL vs ALPHA | QA",font=ft(24,True),fill="#292629")
for idx,row in enumerate(rows):
 y=60+idx*490
 with Image.open(row["source"]) as im:
  left=ImageOps.contain(im.convert("RGB"),(424,424),Image.Resampling.LANCZOS)
 board.paste(left,(14+(424-left.width)//2,y+(424-left.height)//2))
 d.text((465,y+18),row["family"]+(" #19" if row["shade"] else ""),font=ft(31,True),fill="#333")
 d.text((465,y+69),row["status"],font=ft(18),fill="#726a70")
 if row.get("output_jpg"):
  with Image.open(DEST/row["output_jpg"]) as im:
   after=im.convert("RGB").resize((424,424),Image.Resampling.LANCZOS)
  board.paste(after,(1030,y))
proof=DEST/"v2761-original-versus-photo-detail.jpg"
board.save(proof,"JPEG",quality=81,optimize=True)
(DEST/"v2761-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
m={"version":"v2761","baseline":"v2760","product_families":["pending-08","pending-13"],
  "source_photos_collected_new":0,
  "reused_two_existing_exact_product_photos":True,
  "actual_new_alpha_png_and_1080_jpg_pairs":sum(bool(x.get("output_jpg")) for x in rows),
  "wrong_right_side_lip_and_English_text_excluded_from_shade19_input":True,
  "original_MISSHA_source04_decorative_circle_not_reused":True,
  "source_editions_and_redistribution_permissions_verified":False,
  "new_approved_retail_families":0,
  "prior_11_published_families_modified":False,
  "prior_55_published_URLs_changed":False,
  "no_final_spreadsheet_shared":True,
  "results":rows}
(DEST/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2761","new_photo_QA_pairs":m["actual_new_alpha_png_and_1080_jpg_pairs"],
 "statuses":[x["status"] for x in rows],"new_retail_approvals":0}))
