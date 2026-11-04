#!/usr/bin/env python3
"""v2824 EXACT per-variant CLIO Mini 5g image QA index.
Source files remain byte-identical. Verify 21C Lingerie and 21N Linen are
independently sourced, 23N Ginger gallery has 5 distinct physical JPGs.
Never copy/relabel 23N as 21C/21N or auto-publish.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2824-clio-mini-5g-three-shade-file-integrity-and-edge-gates"
assert not OUT.exists()
OUT.mkdir(parents=True)
SOURCE=[
 ("21C Lingerie",ROOT/"v2823-clio-mini-5g-21C-true-compact-alpha-QA",
  "01-real-21C-mini5g-1080-hero-QA.jpg",ROOT/"v2822b-clio-original-mini-5g-21C-exact-variant-gallery-proof"/"02-21C-Lila-Beauty-exact-variant-QA.jpg"),
 ("21N Linen",ROOT/"v2821-clio-mini-5g-21N-true-compact-alpha-QA",
  "01-real-21N-mini5g-1080-hero-QA.jpg",ROOT/"v2820-clio-mini-5g-Lila-21N-variant-photo-evidence"/"01-21N-variant-linked-Lila-5g-QA.jpg"),
 ("23N Ginger",ROOT/"v2818-clio-23N-five-distinct-real-photo-QA-set",
  "01-NEURAL_REAL_SINGLE_CLOSED_COMPACT-QA.jpg",ROOT/"v2816-clio-original-mini-5g-23N-real-single-unit-source"/"01-original-sasa-23N-5g-photo-1080-QA.jpg")
]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(bold if b else fontfile,n)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
rows=[]
for variant,folder,filename,original in SOURCE:
 path=folder/filename
 assert path.is_file() and original.is_file(),(path,original)
 with Image.open(path) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
 assert path.stat().st_size<2_000_000
 with Image.open(original) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
 manifest=json.loads((folder/"manifest.json").read_text())
 alpha_bbox=manifest.get("alpha_bbox")
 row={
  "variant":variant,"product":"CLIO Kill Cover Founwear The Original Mini 5g",
  "source_hero_JPG":str(path),"source_hero_sha256":sha(path),
  "explicitly_variant_linked_original_JPG":str(original),
  "original_source_sha256":sha(original),
  "main_JPG_1080_under_2MB":True,
  "visual_QA":"HOLD_CROP_BORDER_1_TO_1_CHECK" if alpha_bbox and alpha_bbox[1]==0 else "QA_CANDIDATE",
  "retail_approved":False,
  "exact_owned_inventory_variant_verified":False,
  "photo_reuse_license_verified":False
 }
 if alpha_bbox:row["source_segmentation_bbox"]=alpha_bbox
 if variant=="23N Ginger":
  archived=sorted(folder.glob("[0-9][0-9]-*.jpg"))
  assert len(archived)==5,(len(archived),archived)
  scene_hashes=[sha(x) for x in archived]
  assert len(set(scene_hashes))==5
  row["prior_23N_gallery_JPGs_count"]=5
  row["prior_23N_gallery_distinct_exact_SHA_count"]=len(set(scene_hashes))
  row["prior_23N_gallery_files"]=[str(x) for x in archived]
 else:
  row["distinct_variant_specific_five_scene_gallery_completed"]=False
  row["missing_required_distinct_scene_count"]=4
 rows.append(row)
assert len({r["source_hero_sha256"] for r in rows})==3
board=Image.new("RGB",(1620,615),"#efefed")
draw=ImageDraw.Draw(board)
draw.text((18,15),"v2824 EXACT SHADE CLIO MINI 5g: 21C vs 21N vs 23N | QA ONLY",font=ft(26,True),fill="#2b282b")
for i,row in enumerate(rows):
 with Image.open(row["source_hero_JPG"]) as img:
  thumb=img.convert("RGB").resize((477,477),Image.Resampling.LANCZOS)
 x=25+i*538
 board.paste(thumb,(x,71))
 draw.text((x,553),row["variant"],font=ft(24,True),fill="#363136")
proof=OUT/"v2824-21C-21N-23N-true-source-comparison.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2824-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2824","baseline":"v2823",
 "pending_family":"pending-05",
 "variants":["21C Lingerie","21N Linen","23N Ginger"],
 "true_distinct_source_by_option_confirmed":True,
 "three_physical_1080_JPGs_checked":3,
 "23N_five_JPG_photo_gallery_validated":True,
 "21C_and_21N_remaining_distinct_gallery_scenes":4,
 "no_variants_relabelled":True,
 "photo_license_and_owned_stock_edition_still_HOLD":True,
 "new_sale_approvals":0,
 "approved_11_groups_modified":False,"approved_55_urls_changed":False,
 "original_image_bytes_modified":0,"final_excel_shared":False,
 "rows":rows
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2824","variants":3,
"real_JPGs_checked":3,"23N_real_gallery":5,
"21C_and_21N_extra_scenes_required_each":4,
"retail_approved":0}))
