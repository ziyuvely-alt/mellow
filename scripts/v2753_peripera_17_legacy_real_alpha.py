#!/usr/bin/env python3
"""v2753 peripera 01..20 existing LEGACY variant-linked real merchant source JPGs
-> actual alpha product-only QA test; no false 26AD color swatches or edit to
already published 11 families/55 URLs. Exclude 12-14 whose exact variant-linked
images show only lips (not separable retail product bottles).

These photographs have no established commercial redistribution rights.
The resulting transparencies are QA ONLY, never auto-release.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import json,base64,hashlib,math
ROOT=Path("qa-review")
SOURCE=ROOT/"v2752-peripera-legacy-01to20-variant-photo-evidence"
OUT=ROOT/"v2753-peripera-legacy-17-product-real-alpha-qa"
assert SOURCE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
source=json.loads((SOURCE/"manifest.json").read_text())
assert len(source["records"])==20 and source["unique_variant_source_JPGs"]==20
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(bold_path if b else font_path,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
rows=[]
for src in source["records"]:
 num=int(src["shade"]);shade=src["shade"]
 row={"shade":shade,"merchant_variant":src.get("merchant_name"),"source_filename":src.get("image_file"),
      "source_sha256":src.get("qa_JPG_sha256"),"retail_approved":False}
 if num in (12,13,14):
  row.update({"status":"HOLD_LIP_SWATCH_ONLY_NO_INTACT_PRODUCT_TUBE",
     "reason":"Product variant image mainly shows applied lips, not a complete standalone tube; must not invent tube or use generic other shade"})
  rows.append(row);continue
 imgpath=SOURCE/src["image_file"]
 assert imgpath.is_file() and sha(imgpath)==src["qa_JPG_sha256"]
 try:
  with Image.open(imgpath) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   photo=im.convert("RGBA")
  # The 18-20 group is a split label with lips on the right; crop only
  # the left-side real product photograph, never include someone's lip image.
  region=(88,205,568,930) if num>=18 else (240,175,910,930)
  crop=photo.crop(region)
  cut=remove(crop,session=session,alpha_matting=True,
      alpha_matting_foreground_threshold=231,
      alpha_matting_background_threshold=18,
      alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  alpha=cut.getchannel("A")
  bbox=alpha.getbbox();assert bbox is not None
  mask=list(alpha.getdata());fraction=sum(p>=128 for p in mask)/len(mask)
  bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
  assert .016<fraction<.83 and bw>70 and bh>180,(fraction,bbox)
  isolated=cut.crop(bbox)
  folder=OUT/f"shade-{shade}";folder.mkdir()
  png=folder/f"{shade}-exact-legacy-product-true-alpha-QA.png"
  isolated.save(png,optimize=True)
  hero=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(hero)
  d.rounded_rectangle((56,52,1024,1026),radius=34,outline="#eee6e9",width=2)
  d.text((95,91),"PERIPERA",font=ft(39,True),fill="#40343a")
  raw=str(src.get("merchant_name") or f"{shade}")
  label="Legacy "+raw
  sz=26
  while d.textbbox((0,0),label,font=ft(sz))[2]>875 and sz>16:sz-=1
  d.text((95,151),label,font=ft(sz),fill="#796c74")
  fit=ImageOps.contain(isolated,(850,768),Image.Resampling.LANCZOS)
  pos=((1080-fit.width)//2,218+(768-fit.height)//2)
  hero.paste(fit,pos,fit)
  d.text((95,994),"EXACT-SHADE SOURCE CUTOUT  |  QA ONLY",font=ft(18),fill="#9c969b")
  jpg=folder/f"{shade}-legacy-real-cutout-1080-JPG-QA.jpg"
  hero.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as ver:
   ver.load();assert ver.format=="JPEG" and ver.size==(1080,1080)
  row.update({"status":"ACTUAL_ALPHA_PNG_JPG_CREATED_VISUAL_QA_PENDING",
   "alpha_png_path":str(png.relative_to(OUT)),"jpg_path":str(jpg.relative_to(OUT)),
   "source_region":list(region),"mask_coverage":round(fraction,4),
   "foreground_bbox":list(bbox),"jpg_sha256":sha(jpg),
   "jpg_bytes":jpg.stat().st_size})
 except Exception as exc:
  row.update({"status":"HOLD_SEGMENTATION_GEOMETRY_OR_SOURCE",
    "failure_type":type(exc).__name__,"failure":str(exc)[:210]})
 rows.append(row)
for p in range(4):
 ss=rows[p*5:(p+1)*5]
 if not ss:continue
 board=Image.new("RGB",(1850,965),"#f1f1f0")
 d=ImageDraw.Draw(board)
 d.text((18,16),f"v2753 ACTUAL LEGACY PERIPERA 01-20 SOURCE vs ALPHA | PAGE {p+1} | NOT RETAIL",font=ft(24,True),fill="#2f2930")
 for ix,r in enumerate(ss):
  x=18+ix*365
  with Image.open(SOURCE/r["source_filename"]) as im:
   orig=im.convert("RGB").resize((332,332),Image.Resampling.LANCZOS)
  board.paste(orig,(x,58))
  d.text((x,398),f"#{r['shade']} ORIGINAL",font=ft(20),fill="#373036")
  if r.get("jpg_path"):
   with Image.open(OUT/r["jpg_path"]) as im:
    new=im.convert("RGB").resize((332,332),Image.Resampling.LANCZOS)
   board.paste(new,(x,465))
  d.text((x,810),r["status"].split("_")[0]+" | "+r["shade"],font=ft(18),fill="#5c5057")
 proof=OUT/f"v2753-real-cutout-visual-page-{p+1}.jpg"
 board.save(proof,"JPEG",quality=79,optimize=True)
 (OUT/f"v2753-proof-page-{p+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
result={"version":"v2753","family":"pending-08","baseline":"v2752",
 "legacy_source_count":20,"attempted_real_product_photographs":17,
 "source_image_is_from_variant_linked_merchant":True,
 "source_photo_licensing_verified":False,
 "not_a_26AD_swatches_or_color_chart":True,"product_edition_matches_owned_stock_verified":False,
 "actual_transparent_png_1080jpg_pairs_saved":sum(bool(x.get("jpg_path")) for x in rows),
 "lip_only_source_shades_intentionally_skipped":["12","13","14"],
 "previous_approved_11_families_unchanged":True,"previous_55_public_URLs_unchanged":True,
 "source_jpgs_unchanged":True,"no_fake_swatches_created":True,"new_retail_approvals":0,
 "final_spreadsheet_shared":False,"shades":rows}
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2753","total":20,"real_alpha_rendered":result["actual_transparent_png_1080jpg_pairs_saved"],
"lip_only_blocked":3,"sale_approved":0}))
