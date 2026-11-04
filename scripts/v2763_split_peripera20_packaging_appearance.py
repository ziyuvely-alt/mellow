#!/usr/bin/env python3
"""v2763 split the existing twenty legacy PERIPERA shade QA media into package
appearance groups without altering, reencoding or approving any images.

Important:
- This is a PHOTO-PACKAGING reference grouping, NOT a claim of actual inventory
  generation, brand release edition, licensing or single unified listing.
- 26AD variants and shades 21..26 explicitly excluded.
- Exact PNG/JPG source SHA256 values preserved for all twenty old QA variants.
- PREVIOUS 11 approved product families and 55 public URLs immutable.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import Counter
import hashlib,shutil,json,base64
R=Path("qa-review")
SOURCE=R/"v2762-peripera20-variant-QA-and-missha-serum-hero-upgrade"
OUT=R/"v2763-peripera20-separated-package-appearance-QA"
assert SOURCE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
v2762=json.loads((SOURCE/"manifest.json").read_text())
items=v2762["peripera_variants"]
assert len(items)==20
byshade={int(x["shade_number"]):x for x in items}
assert sorted(byshade)==list(range(1,21))
GROUPS=[
 ("01-core-standard-pink-tube", [1,2,3,4,5,6,9,10,11],
  "Older standard pink packaging without a visible collaborative sticker or ribbon; color-background strokes are decorative and NOT clean product-only cutouts."),
 ("02-choigosim-character-artwork",[7,8],
  "Character and custom package label printed visibly; never replace with standard package without verifying stock."),
 ("03-peritage-ribbon-artwork",[12,13,14],
  "Old Peritage ribbon packaging; external reference does not establish actual current sale permission."),
 ("04-maltese-character-artwork",[15,16,17],
  "Maltese character/sticker printing on tube; separate from ordinary older package generation."),
 ("05-honey-k-ookie-pink-artwork",[18,19,20],
  "Honey K-Ookie shade packaging reference; #18/#19 decorative painted swatch is an attached photo graphic, NOT clean single-bottle silhouette.")
]
font_regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(font_bold if b else font_regular,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
groups=[]
for gid,shades,description in GROUPS:
 folder=OUT/gid
 folder.mkdir()
 group_rows=[]
 for number in shades:
  rec=byshade[number]
  src_png=SOURCE/rec["png_file"]
  src_jpg=SOURCE/rec["jpg_file"]
  assert src_png.exists() and src_jpg.exists(),number
  dst_png=folder/f"{number:02d}-exact-legacy-shade-original-alpha-QA.png"
  dst_jpg=folder/f"{number:02d}-exact-legacy-shade-1080-QA.jpg"
  shutil.copy2(src_png,dst_png)
  shutil.copy2(src_jpg,dst_jpg)
  assert sha(src_png)==sha(dst_png)==rec["png_sha256"]
  assert sha(src_jpg)==sha(dst_jpg)==rec["jpg_sha256"]
  with Image.open(dst_png) as png:
   png.load(); assert png.format=="PNG" and png.mode=="RGBA"
  with Image.open(dst_jpg) as jpg:
   jpg.load(); assert jpg.format=="JPEG" and jpg.size==(1080,1080)
  assert dst_jpg.stat().st_size<2_000_000
  group_rows.append({
   "shade_number":f"{number:02d}",
   "package_appearance_group":gid,
   "source_QA_version":rec["source_QA_version"],
   "source_sha_unchanged":True,
   "png_file":str(dst_png.relative_to(OUT)),
   "jpg_file":str(dst_jpg.relative_to(OUT)),
   "png_sha256":sha(dst_png),
   "jpg_sha256":sha(dst_jpg),
   "old_v2762_manual_hold":rec["manual_photo_qa"],
   "additional_hold":rec["known_issue"],
   "photo_detail_vs_clean_hero":"PHOTO_DETAIL_REFERENCE_ONLY",
   "physical_owned_stock_edition_verified":False,
   "commercial_reuse_permission_verified":False,
   "retail_sale_approved":False
  })
 cols=5
 rows=(len(group_rows)+cols-1)//cols
 board=Image.new("RGB",(1850,58+rows*408),"#f2f0ef")
 d=ImageDraw.Draw(board)
 d.text((14,15),"v2763 "+gid+" / PHOTO PACKAGE ARTWORK ONLY / QA NOT RETAIL",font=font(23,True),fill="#282828")
 for j,item in enumerate(group_rows):
  p=OUT/item["jpg_file"]
  with Image.open(p) as image:
   frame=image.convert("RGB").resize((331,331),Image.Resampling.LANCZOS)
  x=15+(j%cols)*368
  y=58+(j//cols)*408
  board.paste(frame,(x,y))
  d.text((x,y+340),"SHADE "+item["shade_number"],font=font(23),fill="#333333")
 preview=OUT/(gid+"-contact-QA.jpg")
 board.save(preview,"JPEG",quality=82,optimize=True)
 (OUT/(gid+"-contact-QA.b64.txt")).write_text(base64.b64encode(preview.read_bytes()).decode())
 groups.append({"group_id":gid,"description":description,"shades":[f"{n:02d}" for n in shades],
                "count":len(shades),"variant_files":group_rows,
                "preview":str(preview.relative_to(OUT)),
                "not_an_approved_product_option_group":True})
complete=[int(y["shade_number"]) for group in groups for y in group["variant_files"]]
assert sorted(complete)==list(range(1,21)) and len(complete)==len(set(complete))
manifest={
 "version":"v2763",
 "baseline":"v2762",
 "distinct_old_package_appearance_QA_groups":5,
 "peripera_numbered_legacy_variant_count":20,
 "peripera_total_exact_original_PNG_JPG_pairs":20,
 "prior_PNGs_JPGs_SHA256_unchanged":True,
 "new_image_segmentation_or_rendering":False,
 "new_product_listing_published":False,
 "actual_26AD_package_edition_identity_not_implied":True,
 "user_owned_stock_version_confirmed":False,
 "original_MK_brand_logo_approved":False,
 "photo_copyright_redistribution_permissions_verified":False,
 "all_shades_21to26_excluded":True,
 "all_11_previously_approved_retail_groups_unchanged":True,
 "all_55_verified_public_urls_unchanged":True,
 "new_retail_approved":0,
 "final_XLSX_or_spreadsheet_shared":False,
 "release_caution":"These photo appearance groupings are NOT official variant classification, and must never be merged with 26AD or treated as stock-confirmed. All photograph use rights unverified.",
 "groups":groups
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"edition-guard.md").write_text(
"# v2763 PERIPERA legacy image package appearance guard\n\n"
+"Photo-side visual grouping only, not licensing or official product edition proof.\n\n"
+"\n".join(f"- {g['group_id']}: {', '.join(g['shades'])}; {g['description']}" for g in groups)
+"\n\n- Do not add shades 21-26 or interpolate a 26AD swatch chart.\n"
+"- Do not use these gallery groups to assert actual user-owned inventory edition.\n"
+"- Previous 11 retail approved families and 55 public URLs unchanged.\n"
+"- No final XLSX/Spreadsheet shared.\n")
print(json.dumps({"version":"v2763","groups":len(groups),"original_png_jpg_pairs":len(complete),
 "name_groups":[{"id":g["group_id"],"count":g["count"]} for g in groups],
 "new_retail_approved":0}))
