#!/usr/bin/env python3
"""v2593: create real fully reconstructible 156-JPG internal review corpus from
immutable base v2560 + v2582 eleven deltas + v2583 + v2585 + v2588 three
+ v2592 latest corrected Goodal JPG. Prior v2591 incorrectly points to the
now superseded v2590 Goodal footer; never use it.
Preserve original 11 published families and 55 public URLs.
Issue a concrete SKU inconsistency quarantine for MISSHA pending12 15G/15mL.
No sales approval, no spreadsheets.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
BASE=Path("sources/base/review-JPG-by-family")
OUT=Path("v2593-latest-156-physical-QA-corpus")
TARGET=OUT/"review-JPG-by-family"
S=Path("sources")
def load(path):return json.loads(path.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m11=load(S/"eleven/manifest.json")
m12=load(S/"double/manifest.json")
m13=load(S/"waterful/manifest.json")
m16=load(S/"missha-drg/manifest.json")
m17=load(S/"goodal-corrected/manifest.json")
assert m11["version"]=="v2582" and len(m11["changes"])==11
assert m12["version"]=="v2583" and m13["version"]=="v2585"
assert m16["version"]=="v2588" and len(m16["new_changes"])==3
assert m17["version"]=="v2592"
assert m13["status"]=="DISTINCT_PRODUCT_PHOTO_QA_ONLY"
assert m16["virtual_total_QA_deltas"]==16 and m17["QA_overlay_count_unchanged"]==17
replacements={}
def add(fam,slot,file,expected,provenance):
 key=(fam,slot)
 assert key not in replacements,(key,"duplicate change slot")
 assert file.is_file(),file
 assert sha(file)==expected,(key,"candidate source hash mismatch")
 replacements[key]={"file":file,"sha256":expected,"provenance":provenance}
for row in m11["changes"]:
 add(row["family"],row["slot"],S/"eleven"/row["qa_file"],row["new_sha256"],"v2582")
add("pending-11",5,S/"double"/m12["new_qa_image_file"],m12["QA_candidate_sha256"],"v2583")
add("pending-22",4,S/"waterful"/m13["file"],m13["candidate_sha256"],"v2585")
for row in m16["new_changes"]:
 add(row["family"],row["slot"],S/"missha-drg"/row["file"],row["new_sha256"],"v2588")
add("pending-20",5,S/"goodal-corrected"/m17["new_candidate_file"],m17["new_sha256"],"v2592_NOT_v2590")
assert len(replacements)==17,len(replacements)
old=sorted(BASE.glob("pending-*/*.jpg"))
assert len(old)==156,len(old)
TARGET.mkdir(parents=True,exist_ok=True)
images=[];untouched=0;mods=[];source_sha={}
for family_idx in range(1,31):
 family=f"pending-{family_idx:02d}"
 paths=sorted((BASE/family).glob("*.jpg"))
 assert len(paths)==(6 if family_idx in (1,2,4,5,6,7) else 5)
 (TARGET/family).mkdir(exist_ok=True)
 slots=set()
 for prior in paths:
  slot=int(prior.name[:2])
  assert slot not in slots,(family,slot);slots.add(slot)
  key=(family,slot)
  basehash=sha(prior)
  source_sha[f"{family}:{slot:02d}"]=basehash
  chosen=replacements.get(key)
  if chosen:
   incoming=chosen["file"]
   target=TARGET/family/f"{slot:02d}_v2593_QA_ONLY_{chosen['provenance']}.jpg"
  else:
   incoming=prior
   target=TARGET/family/prior.name
   untouched+=1
  shutil.copy2(incoming,target)
  digest=sha(target)
  assert digest==(chosen["sha256"] if chosen else basehash)
  im=Image.open(target);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and target.stat().st_size<2_000_000
  images.append({"family":family,"slot":slot,"path":str(target.relative_to(OUT)),
    "sha256":digest,"old_sha256":basehash,"source":chosen["provenance"] if chosen else "v2560-immutable"})
  if chosen:
   assert digest!=basehash,(key,"claimed replacement identical to original")
   mods.append(key)
assert len(images)==156 and len(mods)==17 and untouched==139
assert set(mods)==set(replacements)
for family_idx in range(1,31):
 family=f"pending-{family_idx:02d}"
 subset=[x for x in images if x["family"]==family]
 assert len({x["sha256"] for x in subset})==len(subset)
inv=load(Path("evidence/inventory-30-family-crosswalk-20261104.json"))
stock=next(x for x in inv["pending_families"] if x["family_id"]=="pending-12")
assert "15ml" in stock["family_name"].lower()
assert "15G" in stock["option_values"],stock
quarantine={"family":"pending-12","product":stock["family_name"],
 "inventory_option":stock["option_values"][0],"displayed_family_unit":"15ml",
 "status":"HOLD_REAL_STOCK_PACKAGING_UNIT_DISCREPANCY",
 "instruction":"Compare actual physical Korean stock printed label for grams versus milliliters; do NOT auto-convert 15g to 15mL.",
 "image_public_release":False}
manifest={"version":"v2593","base_run":41753618979,
 "overlay_input_runs":[41762644574,41762824246,41763143287,41763838259,41764357199],
 "latest_17_JPG_verified_and_assembled":17,"unchanged_originals_sha_verified":139,
 "fully_reconstructed_physical_JPGs":156,"family_count":30,
 "stale_v2590_Goodal_footer_excluded":True,
 "latest_Goodal_source":"v2592","cross_SKU_stock_quarantine":[quarantine],
 "no_photo_rights_approval":True,"MK_original_logo_not_inserted":True,
 "physical_stock_edition_QA_incomplete":True,"commercial_sales_approved_families":0,
 "old_55_verified_public_URLs_changed":0,"new_public_URLs":0,
 "xlsx_generated_or_shared":False,"files":images}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"quarantine.json").write_text(json.dumps([quarantine],ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"latest_corpus_JPG":156,"updated":17,"unaltered":139,
 "Goodal_latest_footer":"v2592","inventory_unit_conflicts":1,
 "published":0,"xlsx":False}))
