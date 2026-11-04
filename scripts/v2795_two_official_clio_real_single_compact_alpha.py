#!/usr/bin/env python3
"""v2795: crop and alpha-mask two known exact-product official CLUBCLIO JPGs.

Candidate-only QA: pending-05 Founwear Mini official 7108 and pending-07
Mesh Blur Cushion official 6455. V2794 found no larger native originals.
Use only the region containing the target compact, not full promo kits.
Do not call synthetic upscale a native high-resolution photo.
Never modify any previous JPG or published URL, no commercial approval.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from rembg import remove, new_session
import base64, hashlib, json, numpy as np
ROOT=Path("qa-review")
SOURCE=ROOT/"v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof"
OUT=ROOT/"v2795-clio-mini-meshblur-target-only-single-case-cutout-tests"
assert SOURCE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 dict(family="pending-05",product="CLIO Kill Cover Founwear Mini 5g",
      native_resolution="600x600",
      file="04-official-7108-b-gif-REFERENCE.jpg",
      bbox=(558,410,1005,850),
      source_id=7108,
      note="Smaller compact at right side of official multi-compact image; packaging/shade edition unverified; not true 1080 native."),
 dict(family="pending-07",product="CLIO Kill Cover Mesh Blur Cushion",
      native_resolution="600x600",
      file="02-official-6455-b-gif-REFERENCE.jpg",
      bbox=(185,196,870,893),
      source_id=6455,
      note="Open lavender cushion and applicator in official image; set/refill remains a stock-version hold."),
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
records=[]
for c in CASES:
 source=SOURCE/c["family"]/c["file"]
 assert source.is_file(),source
 with Image.open(source) as img:
  img.load();assert img.format=="JPEG" and img.size==(1080,1080)
  image=img.convert("RGBA")
 crop=image.crop(c["bbox"])
 row={
  "family":c["family"],"product":c["product"],
  "source_official_product_id":c["source_id"],"source_saved_path":str(source),
  "source_sha256":sha(source),
  "declared_official_photo_native_resolution":c["native_resolution"],
  "source_crop_xyxy":list(c["bbox"]),"rights_verified":False,
  "exact_owned_stock_variant_verified":False,"commercial_retail_approved":False,
  "known_blocker":c["note"],"status":"HOLD_TECHNICAL_OR_VISUAL_REVIEW"}
 try:
  segmented=remove(crop,session=session,alpha_matting=True,
    alpha_matting_foreground_threshold=235,
    alpha_matting_background_threshold=18,
    alpha_matting_erode_size=4)
  assert segmented.mode=="RGBA"
  a=segmented.getchannel("A");box=a.getbbox()
  assert box is not None
  mask=np.asarray(a)
  ratio=float(np.mean(mask>=128))
  # Don't mask away almost everything, or preserve full rectangular backgrounds.
  assert .035<ratio<.74 and box[2]-box[0]>=100 and box[3]-box[1]>=105, (ratio,box)
  tight=segmented.crop(box)
  out=OUT/c["family"];out.mkdir()
  png=out/"01-exact-cushion-compacted-alpha-QA.png"
  tight.save(png,optimize=True)
  jpg=out/"01-sourced-single-compact-cutout-1080-QA.jpg"
  art=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(art)
  d.rounded_rectangle((45,45,1035,1035),radius=34,outline="#e5e4e8",width=2)
  d.text((98,88),"CLIO",font=font(42,True),fill="#363138")
  name=c["product"].replace("CLIO ","")
  size=32
  while d.textbbox((0,0),name,font=font(size))[2]>875:size-=1
  d.text((98,150),name,font=font(size),fill="#776d74")
  target=ImageOps.contain(tight,(810,765),Image.Resampling.LANCZOS)
  art.paste(target,((1080-target.width)//2,220+(765-target.height)//2),target)
  d.text((96,982),"OFFICIAL 600px SOURCE  |  CUTOUT QA ONLY",font=font(20),fill="#99939a")
  art.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  with Image.open(jpg) as check:
   check.load();assert check.format=="JPEG" and check.size==(1080,1080)
  assert jpg.stat().st_size<2_000_000
  row.update({"status":"REAL_ALPHA_CUTOUT_STAGED_FOR_VISUAL_QA",
    "foreground_coverage":round(ratio,4),"foreground_bbox":list(box),
    "native_png":str(png.relative_to(OUT)),
    "1080_jpg":str(jpg.relative_to(OUT)),
    "sha256_jpg":sha(jpg)})
 except Exception as e:
  row.update({"status":"REJECTED_MASK_OR_SHAPE","reason":str(e)[:190]})
 records.append(row)
# Three columns to give reviewers original, product crop, segmented result.
board=Image.new("RGB",(1650,965),"#f0f0ef")
d=ImageDraw.Draw(board)
d.text((18,12),"v2795 Official source / exact ROI / alpha output  |  NOT PUBLISHED",font=font(25,True),fill="#252525")
for n,rec in enumerate(records):
 y=56+n*450
 with Image.open(rec["source_saved_path"]) as im:
  original=im.convert("RGB").resize((380,380),Image.Resampling.LANCZOS)
 board.paste(original,(12,y))
 with Image.open(rec["source_saved_path"]) as im:
  c=im.convert("RGB").crop(rec["source_crop_xyxy"])
  preview=ImageOps.contain(c,(380,380))
  crop_tile=Image.new("RGB",(380,380),"white");crop_tile.paste(preview,((380-preview.width)//2,(380-preview.height)//2))
 board.paste(crop_tile,(414,y))
 if rec.get("1080_jpg"):
  with Image.open(OUT/rec["1080_jpg"]) as im:
   result=im.convert("RGB").resize((380,380),Image.Resampling.LANCZOS)
  board.paste(result,(824,y))
 d.text((1221,y+23),rec["family"],font=font(30,True),fill="#333")
 d.text((1221,y+81),rec["status"],font=font(18),fill="#555")
 d.text((1221,y+125),"RETAIL RIGHTS: HOLD",font=font(19),fill="#555")
proof=OUT/"v2795-official-photo-crop-alpha-visual-proof.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2795-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2795","baseline":"v2794",
 "actual_two_product_single-case_alpha_trials":len(records),
 "actual_png_jpg_pairs_written":sum(bool(x.get("1080_jpg")) for x in records),
 "do_not_treat_600px_as_native_1080":True,
 "image_publish_permissions_verified":False,
 "user_owned_single_sku_edition_confirmed":False,
 "new_retail_approvals":0,
 "old_11_sale_approved_families_untouched":True,
 "old_55_verified_public_urls_untouched":True,
 "previous_QA_files_untouched":True,
 "final_spreadsheet_shared":False,"products":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2795","saved_cutouts":manifest["actual_png_jpg_pairs_written"],
 "statuses":[r["status"] for r in records],"new_approved":0}))
