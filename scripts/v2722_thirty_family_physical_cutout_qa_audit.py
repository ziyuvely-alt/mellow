#!/usr/bin/env python3
"""v2722 inventory the ORIGINAL QA cutout physical files, never recreate them.

A validated PNG/JPG pair means files exist and satisfy technical format only;
it does NOT imply shape, product edition, license, MK authenticity or retail
approval. Previous human visual QA verdict overrides raw geometry.

Append-only in QA branch. Never touch published 11 families / public 55 URLs.
No spreadsheets.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path("qa-review")
OUT=R/"v2722-thirty-family-file-backed-cutout-queue"
assert not OUT.exists()
OUT.mkdir(parents=True)
VERSIONS=[
 "v2711-real-segmentation-four-source-product-heroes",
 "v2712-3-failed-cutouts-high-quality-recovery",
 "v2713-six-new-product-hero-real-alpha-cutouts",
 "v2714-serum-alpha-component-and-pad-alternate-photo",
 "v2715-five-more-original-product-real-alpha-hero-tests",
 "v2716-obge-finisher-and-goodal-alternate-real-alpha",
 "v2717-four-fresh-cushion-cream-real-alpha-candidates",
 "v2719-four-unprocessed-clio-missha-real-photo-cutouts",
 "v2720-missha-moistup-obge-porezero-photo-cutouts",
 "v2721-three-drg-goodal-alpha-photo-QA",
]
# Prior human view checks, not automatic mask guesses. (Status is QA only.)
REVIEW={
 1:("REJECT","compact partially clipped; source artwork wrong for intact single-product hero"),
 2:("HOLD_STOCK","compact plus box; product/shade package stock match not verified"),
 3:("QA_CANDIDATE","old-era gold-pump BB cream shade 23; verify exact inventory edition"),
 4:("REJECT","second-model CLIO mini retained nonproduct background; do not retry same frame"),
 5:("REJECT","CLIO Founwear mini photograph depicts multiple set components"),
 6:("REJECT","CLIO Mesh Glow Essential source is kit/multiple compact artwork"),
 7:("REJECT","CLIO Mesh Blur photograph includes GIFT and extra components"),
 8:("SOURCE_BLOCKED","PERIPERA 01-20 official shade/26AD identity and 004 conflict; no authentic cutout staged"),
 9:("REJECT","OBGE finisher previous alpha retains brown rectangular background"),
 10:("HOLD_STOCK","OBGE Perfect Homme Cushion source says 15g vs possibly owned 13g"),
 11:("QA_CANDIDATE","OBGE double-chamber bottle; do not describe as 2 separate products"),
 12:("HOLD_STOCK","MISSHA Renew Peel Shot photographed 15mL vs inventory 15g"),
 13:("SOURCE_BLOCKED","MISSHA serum slot01 is a fact card, not a product photograph; use already valid v2697 photo set"),
 14:("QA_CANDIDATE","MISSHA PDRN cream original jar/lid intact; verify 70mL not foreign 70g"),
 15:("QA_CANDIDATE","Dr.G Green Mild Up Sun tube intact"),
 16:("QA_CANDIDATE","Dr.G R.E.D Blemish cream jar intact"),
 17:("QA_CANDIDATE","Dr.G Brightening Up Moisture Sun tube intact"),
 18:("QA_CANDIDATE","Dr.G Brightening Up Sun Plus tube intact"),
 19:("QA_CANDIDATE","GOODAL Vita C Cream Alpha jar intact"),
 20:("QA_CANDIDATE","GOODAL Serum Mist 100mL pump and bottle intact"),
 21:("REJECT","GOODAL 30mL eye tube alternate source clipped; cannot reconstruct"),
 22:("QA_CANDIDATE","OBGE Max Waterful 300mL pump and base retained in second model"),
 23:("QA_CANDIDATE","OBGE Pore Zero 50mL cutout largely clean; bottom edge needs 1:1 check"),
 24:("QA_CANDIDATE","BIOHEAL BOH serum detached alpha blob fixed in v2714; edges need 1:1 check"),
 25:("QA_CANDIDATE","BIOHEAL BOH cream base retained in v2712"),
 26:("QA_CANDIDATE","PIXEL PURE Gel-to-Foam 145mL body intact in v2711"),
 27:("QA_CANDIDATE","PIXEL PURE toner 200mL intact"),
 28:("QA_CANDIDATE","PIXEL PURE pads 70ea alternate source fixed in v2714; bottom needs check"),
 29:("QA_CANDIDATE","PIXEL PURE cream 50mL intact"),
 30:("QA_CANDIDATE","PIXEL PURE serum 50mL intact"),
}
KEYS_PNG=("transparent_png","transparent_PNG","alpha_png","cutout_PNG","cutout_png","png","alpha_PNG")
KEYS_JPG=("JPG","jpg","square_jpg","white_hero_JPG","square_JPG","JPG_1080","white_hero_JPG")
attempts={}
for folder in VERSIONS:
 manifest=R/folder/"manifest.json"
 assert manifest.exists(),manifest
 j=json.loads(manifest.read_text())
 for x in j.get("products",j.get("candidates",[])):
  family=x.get("family")
  assert family and family.startswith("pending-")
  num=int(family.split("-")[1])
  p=next((x.get(k) for k in KEYS_PNG if x.get(k)),None)
  q=next((x.get(k) for k in KEYS_JPG if x.get(k)),None)
  entry={"folder":folder,"reported_status":x.get("status"),"png_relative_path":p,"jpg_relative_path":q,
    "physical_pair_valid":False,"reason":None}
  if p and q:
   pn=R/folder/p;jn=R/folder/q
   if pn.is_file() and jn.is_file():
    with Image.open(pn) as a:
     a.load();alpha_ok=a.format=="PNG" and a.mode in ("RGBA","LA")
    with Image.open(jn) as b:
     b.load();jpg_ok=b.format=="JPEG" and b.size==(1080,1080)
    entry["physical_pair_valid"]=bool(alpha_ok and jpg_ok and jn.stat().st_size<2000000)
    entry["png_sha256"]=hashlib.sha256(pn.read_bytes()).hexdigest()
    entry["jpg_sha256"]=hashlib.sha256(jn.read_bytes()).hexdigest()
    entry["jpg_bytes"]=jn.stat().st_size
    if not entry["physical_pair_valid"]:entry["reason"]="VALIDATION_OR_SIZE_FAILED"
   else:entry["reason"]="PHYSICAL_FILE_MISSING"
  else:entry["reason"]="NO_BOTH_PNG_AND_JPG"
  attempts.setdefault(num,[]).append(entry)
allrows=[]
for i in range(1,31):
 label,reason=REVIEW[i]
 trials=attempts.get(i,[])
 validated=[t for t in trials if t["physical_pair_valid"]]
 latest=validated[-1] if validated else None
 if label=="QA_CANDIDATE" and latest is None:
  label="BLOCKED_NO_VERIFIED_PHYSICAL_PAIR"
 # Explicit prioritize latest known successfully human-inspected revision.
 if i in (22,25,24,28) and validated:
  wanted={"22":"v2712","25":"v2712","24":"v2714","28":"v2714"}[str(i)]
  selected=[t for t in validated if t["folder"].startswith(wanted)]
  if selected:latest=selected[-1]
 if i==26 and validated:
  selected=[t for t in validated if t["folder"].startswith("v2711")]
  if selected:latest=selected[-1]
 allrows.append({"family":f"pending-{i:02d}","review_status":label,
  "visual_review_basis":reason,"attempt_count":len(trials),
  "verified_PNG_JPG_pairs":len(validated),
  "selected_QA_pair":latest,
  "all_source_attempts":trials,
  "retail_release":"HOLD_ALL_PENDING_ORIGINAL_MK_PHOTO_RIGHTS_STOCK_EDITION"})
status_counts={}
for row in allrows:
 key=row["review_status"];status_counts[key]=status_counts.get(key,0)+1
report={"version":"v2722","baseline":"v2721","families_audited":30,
 "real_physical_PNG_JPG_pairs_validated":sum(x["verified_PNG_JPG_pairs"] for x in allrows),
 "physical_families_with_at_least_one_pair":sum(bool(x["verified_PNG_JPG_pairs"]) for x in allrows),
 "status_counts":status_counts,"source_status_by_family":allrows,
 "no_product_image_files_modified":True,"previous_11_approved_product_families_unchanged":True,
 "previous_55_published_urls_unchanged":True,"new_retail_approved":0,
 "commercial_photo_reuse_rights_verified":False,"original_round_MK_logo_verified":False,
 "owned_stock_exact_editions_verified":False,"final_excel_or_spreadsheet_shared":False}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
lines=["# v2722 | 30-family source-linked cutout QA queue","","Technical image output is not retail approval. All 11 previously published product families and their 55 verified URLs are immutable.","",
"| Family | QA decision | Verified file pairs | Visual identity issue |","|---|---|---:|---|"]
for x in allrows:
 lines.append(f"| {x['family']} | {x['review_status']} | {x['verified_PNG_JPG_pairs']} | {x['visual_review_basis']} |")
lines.extend(["","## Gates","- All photo rights, original MK logo, and exact physical package variants remain held.",
 "- Do not repeat successful segmentations or retry images marked REJECT without genuinely different source.",
 "- Next focus: obtain authenticated single-product photos for rejected/blocked item families rather than reusing product sets, facts or incomplete tubes.",
 "- Per-product final photo QA must confirm no background remnants, no wrong package sizes and no fake swatches.","- No final XLSX/Spreadsheet."])
(OUT/"next-work-queue.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"families_audited":30,
 "physical_pair_validations":report["real_physical_PNG_JPG_pairs_validated"],
 "unique_families_with_verified_pair":report["physical_families_with_at_least_one_pair"],
 "statuses":status_counts,"sales_approved":0}))
