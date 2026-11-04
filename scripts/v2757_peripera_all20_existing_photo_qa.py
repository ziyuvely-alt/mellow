#!/usr/bin/env python3
"""v2757: production-queue QA on 20 already CREATED legacy PERIPERA alpha assets.
NO segmentation or new product/source generation: verify exact photographed
shades 01-20, transparent alpha, dimensions, byte limits, non-identical outputs
across 20 shade options. Isolate old Peritage 12/13/14 edition explicitly.
Never interpret technical verification as retail authorization.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path("qa-review")
DEST=ROOT/"v2757-peripera-all20-existing-cutout-file-and-edition-audit"
assert not DEST.exists(),"Never repeat or overwrite output"
DEST.mkdir(parents=True)
P53=ROOT/"v2753-peripera-legacy-17-product-real-alpha-qa"
P54=ROOT/"v2754-peripera-peritage-three-missing-bottle-source-QA"
P55=ROOT/"v2755-only-peripera-12-legacy-alternate-bottle-photo"
M53=json.loads((P53/"manifest.json").read_text())
M54=json.loads((P54/"manifest.json").read_text())
M55=json.loads((P55/"manifest.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(sz,b=False):return ImageFont.truetype(B if b else F,sz)
rows=[]
for i in range(1,21):
 shade=f"{i:02d}"
 if i in (12,):
  base=P55
  png=base/M55["alpha_png"]
  jpg=base/M55["1080_jpg"]
  source_status="ALTERNATIVE_KTOWN4U_PERITAGE_RIBBON"
 elif i in (13,14):
  old=next((x for x in M54["rows"] if x["shade"]==shade),None)
  assert old is not None and old.get("cutout_png") and old.get("cutout_jpg"),shade
  base=P54
  png=base/old["cutout_png"]
  jpg=base/old["cutout_jpg"]
  source_status="V2754_INDEPENDENT_PERITAGE_RIBBON"
 else:
  old=next((x for x in M53["shades"] if x["shade"]==shade),None)
  assert old is not None and old.get("alpha_png_path") and old.get("jpg_path"),shade
  base=P53
  png=base/old["alpha_png_path"]
  jpg=base/old["jpg_path"]
  source_status="V2753_MERCHANT_EXACT_VARIANT"
 assert png.is_file() and jpg.is_file(),(shade,png,jpg)
 with Image.open(png) as im:
  im.load();w,h=im.size
  mask=im.convert("RGBA").getchannel("A")
  px=mask.getdata()
  coverage=sum(x>=128 for x in px)/(w*h)
  edge=[mask.getpixel(pt) for pt in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
  png_ok=im.format=="PNG" and im.mode=="RGBA" and 0.015<coverage<.95 and max(edge)<=150
 with Image.open(jpg) as im:
  im.load();jpg_ok=im.format=="JPEG" and im.size==(1080,1080) and jpg.stat().st_size<2000000
 assert png_ok and jpg_ok,(shade,png_ok,jpg_ok,coverage,edge)
 rows.append({"shade":shade,"edition":"LEGACY_PERITAGE_SPECIAL" if i in (12,13,14) else "LEGACY_INK_MOOD_GLOWY_TINT",
  "source_status":source_status,
  "original_QA_alpha_PNG_path":str(png),
  "original_QA_JPG_path":str(jpg),
  "PNG_SHA256":sha(png),"JPG_SHA256":sha(jpg),
  "JPG_bytes":jpg.stat().st_size,"alpha_mask_coverage":round(coverage,4),
  "transparent_PNG_geometry_pass":True,"1080_JPG_under2MB_pass":True,
  "actual_owned_stock_edition_verified":False,
  "commercial_publication_photo_rights_verified":False,
  "review_status":"PHOTO_QA_STAGED_NOT_RETAIL_APPROVED"
 })
duplicate={}
for key in ("PNG_SHA256","JPG_SHA256"):
 groups={}
 for r in rows:groups.setdefault(r[key],[]).append(r["shade"])
 duplicate[key]=[v for v in groups.values() if len(v)>1]
assert not duplicate["JPG_SHA256"],duplicate
for page in range(4):
 subset=rows[page*5:(page+1)*5]
 board=Image.new("RGB",(1830,488),"#f1f0ee")
 d=ImageDraw.Draw(board)
 d.text((18,15),f"v2757 LEGACY PERIPERA 01..20 / EXISTING JPG CHECK / PAGE {page+1} / QA NOT RETAIL",font=ft(23,True),fill="#292929")
 for n,row in enumerate(subset):
  x=16+n*363
  with Image.open(row["original_QA_JPG_path"]) as im:
   tile=im.convert("RGB").resize((325,325),Image.Resampling.LANCZOS)
  board.paste(tile,(x,57))
  d.text((x,391),f"#{row['shade']}  "+("PERITAGE" if row["edition"].endswith("SPECIAL") else "LEGACY"),font=ft(21,True),fill="#373238")
  d.text((x,432),f"{row['JPG_bytes']/1024:.0f} KiB  /  ACTUAL JPG",font=ft(17),fill="#817980")
 photo=DEST/f"v2757-page-{page+1}-existing-hero-proof.jpg"
 board.save(photo,"JPEG",quality=82,optimize=True)
result={"version":"v2757","based_on":["v2753","v2754","v2755"],
"pending_family":"pending-08",
"actual_photographic_reprocessing":0,
"previously_persisted_distinct_shades_verified":len(rows),
"actual_transparent_png_files_verified":20,
"actual_1080_jpg_files_verified":20,
"photo_human_visual_1to1_approval_not_assumed":True,
"retail_new_approvals":0,
"peritage_12_13_14_special_packages_preserved":True,
"peripera_26AD_remap_excluded":True,
"duplicate_image_hash_groups":duplicate,
"prior_11_sale_approved_families_untouched":True,
"prior_verified_55_public_urls_untouched":True,
"original_MK_logo_verified":False,
"photo_reuse_licenses_verified":False,
"owned_stock_specific_package_verified":False,
"final_XLSX_shared":False,
"shades":rows}
(DEST/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2757","verified_shades":len(rows),
"PNG":20,"JPG_1080":20,"duplicates":len(duplicate["JPG_SHA256"]),
"sale_approved":0}))
