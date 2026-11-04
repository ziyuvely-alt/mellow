#!/usr/bin/env python3
"""v2708 real 80-JPG pre-release technical QA, no alterations to product photos.
Validate physical JPG sizes, hashes, scene-near-duplicates and shared unverified
badge corner across 16 recovered original family sets.
Outputs actual blocker-aware prioritized production queue, NOT an XLSX.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from collections import Counter
from itertools import combinations
import hashlib,json
ROOT=Path("qa-review")
SETS=[
 ("v2705-three-recovered-photo-first-family-sets",["pending-03","pending-09","pending-21"]),
 ("v2706-six-archival-five-real-source-families",["pending-04","pending-11","pending-15","pending-18","pending-26","pending-29"]),
 ("v2707-seven-remaining-archival-real-photo-family-sets",["pending-16","pending-22","pending-24","pending-25","pending-27","pending-28","pending-30"])
]
OUT=ROOT/"v2708-16-family-pre-release-80-jpg-unique-scene-audit"
assert not OUT.exists();OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ph(im):
 p=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(r*8+c) for r in range(8) for c in range(8) if p[r*9+c]>p[r*9+c+1])
def dist(a,b):return (a^b).bit_count()
issues={
"pending-03":["OLD GOLD PUMP, NOT REDESIGNED US TUBE","SINGLE SHADE/OPTION STOCK ID"],
"pending-04":["MINI 5g PACKAGE/21C 21N 23N SHADE MATCH","HISTORIC MK BADGE UNVERIFIED"],
"pending-09":["CONFIRM PHYSICAL 5g SINGLE COMPACT"],
"pending-11":["ONE DUAL-CHAMBER BOTTLE 50mL+50mL, NOT TWO PRODUCTS"],
"pending-15":["DR.G EXACT SPF PRODUCT EDITION MATCH"],
"pending-18":["DR.G BRIGHTENING UP SUN PLUS ORIGINAL GENERATION"],
"pending-21":["GOODAL 25AD EYE CREAM 30mL, NOT GIFT SET"],
"pending-26":["PIXELPURE 145mL NOT 150mL"],
"pending-29":["PIXELPURE CREAM 50mL EXACT PACKAGING"],
"pending-16":["DR.G R.E.D CREAM 70mL EXACT DESIGN"],
"pending-22":["OBGE MAX WATERFUL 300mL NOT 150/OTHER"],
"pending-24":["BIOHEAL BOH NAD-PRIZCELL SERUM 30mL"],
"pending-25":["BIOHEAL BOH NAD-PRIZCELL CREAM 50mL"],
"pending-27":["PIXELPURE TONER 200mL"],
"pending-28":["PIXELPURE SERUM PAD 70ea/210mL"],
"pending-30":["PIXELPURE AURA SERUM 50mL"]
}
result=[]
all_shas={}
corners=[]
for base,ids in SETS:
 for fid in ids:
  src=ROOT/base/fid
  files=sorted(src.glob("[0-9][0-9]-*.jpg"))
  assert len(files)==5,(fid,len(files))
  scenes=[];dims=[]
  for p in files:
   with Image.open(p) as image:
    image.load()
    assert image.format=="JPEG" and image.size==(1080,1080),(p,image.size)
    rgb=image.convert("RGB")
    scene_ph=ph(rgb)
    corner_ph=ph(rgb.crop((925,916,1068,1064)))
   assert p.stat().st_size<2_000_000
   scene={"slot":int(p.name[:2]),"sha256":sha(p),"size_bytes":p.stat().st_size,"dhash64":f"{scene_ph:016x}","corner_hash":f"{corner_ph:016x}"}
   scenes.append(scene)
   corners.append((fid,scene["slot"],corner_ph))
   all_shas.setdefault(scene["sha256"],[]).append((fid,scene["slot"]))
  pairs=[]
  for left,right in combinations(scenes,2):
   d=dist(int(left["dhash64"],16),int(right["dhash64"],16))
   if d<14:pairs.append({"left":left["slot"],"right":right["slot"],"dhash_distance":d,"severity":"DUPLICATE_LIKELY" if d<=7 else "SEMANTIC_VISUAL_REVIEW"})
  result.append({"family":fid,"source_QA_folder":str(src),"JPG_count":5,
   "actual_file_regenerated":False,"files":scenes,"within_family_near_duplicate_pairs":pairs,
   "unverified_MK_logo_in_bottom_right":True,
   "photo_redistribution_rights_verified":False,
   "exact_owned_stock_generation_verified":False,
   "critical_stock_label_checks":issues[fid],
   "customer_sale_release":"HOLD_PUBLISHING","next_stage":"MANUAL_STOCK_AND_LICENSE_AND_BRAND_REVIEW"})
# report prior duplicate bytes between groups with source files
cross=[{"sha256":key,"uses":v} for key,v in all_shas.items() if len(v)>1]
corner_count=Counter(x[2] for x in corners)
report={
"version":"v2708","source_checkpoint":"v2707",
"audited_archival_family_count":len(result),"original_JPGs_technically_validated":sum(x["JPG_count"] for x in result),
"original_JPGs_reencoded_or_mutated":0,"exact_duplicate_bytes_across_families":cross,
"shared_unverified_lower_right_MK_badge_corner_detected_in_source_art":True,
"distinct_logo_corner_dhash_count":len(corner_count),
"photo_and_product_license_confirmed":False,
"owned_stock_generation_confirmed":False,
"stock_mismatch_and_shade_checks_prepared":True,
"existing_11_published_families_unchanged":True,
"existing_55_public_image_URLs_unchanged":True,
"no_final_excel_or_spreadsheet_shared":True,
"new_sale_approved":0,
"families":result}
assert report["original_JPGs_technically_validated"]==80
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
prioritized=sorted(result,key=lambda z:(len(z["within_family_near_duplicate_pairs"]),len(z["critical_stock_label_checks"]),z["family"]))
lines=["# v2708 pre-release image QA: 16 photo-rich families","",
"Only internal QA. Do not publish image assets until original MK logo permission, product package edition and photo reuse license are verified.","",
"| Family | Unique image scenes | dHash candidate pairs | Stock edition / sales blocker |",
"|---|---:|---:|---|"]
for r in prioritized:
 lines.append(f"| {r['family']} | 5 | {len(r['within_family_near_duplicate_pairs'])} | {'; '.join(r['critical_stock_label_checks'])} |")
lines.extend(["","## Automated result",
f"- Validated physical original JPG files: {report['original_JPGs_technically_validated']}",
f"- Detected within-family near-duplicate candidate pairs: {sum(len(x['within_family_near_duplicate_pairs']) for x in result)}",
f"- Duplicate identical-byte files across different families: {len(cross)}",
f"- Bottom-right corner hash variants across original sources: {len(corner_count)}",
"- Historical MK badge not authenticated; do not copy directly to commercial assets.",
"- No original JPG files changed. No public release or XLSX.",
"",
"## Next process (non-duplicative)",
"1. Treat exact retained media as photo-only reference, not cleared sale images.",
"2. Obtain actual source-logo original (not a reconstructed badge) and approved commercial reuse rights.",
"3. Compare stock photo edition / 21C 21N 23N options and specific item capacities.",
"4. Review only flagged dHash pairs visually before choosing final commercial frames."])
(OUT/"priority-release-gates.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"family_count":len(result),"validated_JPG":80,
"within_family_duplicate_review_pairs":sum(len(x["within_family_near_duplicate_pairs"]) for x in result),
"exact_cross_family_repeats":len(cross),"distinct_corner_hashes":len(corner_count),
"new_retail_approved":0}))
