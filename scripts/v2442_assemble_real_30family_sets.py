#!/usr/bin/env python3
"""v2442 build 30 family-specific real asset candidate sets from immutable existing images.
No renders, no invented color charts, no photo pixel editing. Approved originals stay immutable.
Every output is a candidate review bundle, never a live product listing.
"""
from pathlib import Path
from PIL import Image
from collections import defaultdict
import hashlib,json,shutil,zipfile,re
OUT=Path("v2442-output");OUT.mkdir(exist_ok=True)
base=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422"
prior=Path("prior-v2440e"); newest=Path("prior-v2441c")
extra=Path("prior-v2431b"); peripera=Path("prior-v2435")
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p):
 try:
  with Image.open(p) as im:
   im.load()
   return im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2000000
 except Exception:return False
def collect(root,manifest,listkey,pathkey,groupkey):
 m=json.loads((root/manifest).read_text())
 return {gid:[root/v for v in [row[pathkey] for row in m[listkey] if row[groupkey]==gid]]
         for gid in [f"pending-{i:02d}" for i in range(1,31)]}
old=collect(prior,"v2440e-resumable-checkpoint.json","latest_real_customer_JPG_drafts","path","group_id")
new=collect(newest,"v2441c_checkpoint.json","new_customer_jpg","file","group_id")
# An existing approved corrected same-product 200ml photo and verified caption correction
overrides={
"pending-27":[extra/"sales-image-drafts/pending-27/01_correct_200ml_bottle_layout_fixed_V2431b.jpg"],
"pending-08":[peripera/"sales-image-drafts/pending-08/01_peripera_selected_shades_no_20claim_V2435.jpg"]
}
exclusion={
"pending-01":["HERO"], # cover lasting No.21 in source hero cannot be sold without user's permission
"pending-27":["INV_01_1f25c5d0f4"], # original pictured wrong 300mL
}
high_risk={
"pending-01":"Old original cover shade HERO depicts excluded 21; not used",
"pending-04":"CLIO shade swatch/photo generation and 21C/21N/23N exact official evidence needed",
"pending-05":"CLIO founwear 19N/21N/23N/19C/21C official shades unresolved",
"pending-06":"CLIO mesh glow official swatches unresolved",
"pending-07":"CLIO mesh blur official 19C/19N/21N unresolved",
"pending-08":"Peripera 01..20 product generation, 26AD and missing 04/06/07 exact swatches unresolved",
"pending-10":"OBgE cushion 1/2/3 pack and official swatch provenance unresolved",
"pending-20":"Goodal retailer logo in historical source; inspect exact usage rights",
"pending-21":"Goodal eye cream actual photographed original product association unresolved",
"pending-22":"OBgE 300 mL formula ingredients and original package proof unresolved",
"pending-26":"PIXELPURE cleanser 145mL official product photo generation mismatch",
"pending-27":"Original 300mL image mismatched source 200mL SKU; replaced with real 200mL bottle candidate"
}
records=[];sha_by_group=defaultdict(set);all_created=[]
for n in range(1,31):
 gid=f"pending-{n:02d}"
 chosen=[];seen=set();skips=[]
 def add(p,role):
  if not p.is_file() or not check(p):skips.append({"path":str(p),"why":"missing or invalid 1080 JPEG"});return False
  digest=hashfile(p)
  if digest in seen:return False
  if len(chosen)>=5:return False
  chosen.append({"path":p,"sha256":digest,"role":role})
  seen.add(digest)
  return True
 # Prioritize actual newly corrected customer frames. No rerender. Deduplicate exact source bytes.
 for p in overrides.get(gid,[]):add(p,"corrected_product_photo")
 for p in new.get(gid,[]):add(p,"latest_correction")
 for p in old.get(gid,[]):add(p,"previous_recent_correction")
 # Prefer latest existing English customer info and genuine-source photo images.
 candidates=[]
 for label in ["en-photo-captions","en-customer-drafts","en-hero-fixed"]:
  root=base/label/gid
  if root.exists():
   for p in sorted(root.glob("*.jpg")):
    if any(x in p.name.upper() for x in exclusion.get(gid,[])): 
     skips.append({"path":str(p),"why":"known SKU color/package mismatch exclusion"})
     continue
    # pending27 historical source photo shows 300 mL bottle for INV01, and others
    # remain unproven; exact corrected candidate above takes first slot.
    candidates.append((p,"historical_"+label))
 for p,role in candidates:
  if len(chosen)==5:break
  add(p,role)
 # Need not force 5 by adding historically rejected or duplicating the same photo.
 if len(chosen)<5:
  fallback=base/"originals-immutable/preserved-pending-originals"/gid
  if fallback.exists():
   for p in sorted(fallback.glob("*.jpg")):
    if any(x in p.name.upper() for x in exclusion.get(gid,[])):continue
    if len(chosen)==5:break
    add(p,"historical_original_source_fallback_NOT_EN_verified")
 slots=[]
 for i,obj in enumerate(chosen,1):
  target=OUT/"30group-actual-image-candidate-sets"/gid/f"{i:02d}_{obj['path'].name}"
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(obj["path"],target)
  assert hashfile(target)==obj["sha256"]
  all_created.append(target)
  slots.append({"slot":i,"file":str(target.relative_to(OUT)),"sha256":obj["sha256"],
                "input_source":str(obj["path"]),"input_role":obj["role"],
                "source_rights_verified":False,"final_sales_approval":False})
 records.append({"group_id":gid,"candidate_frame_count":len(slots),
   "missing_frames_for_5":5-len(slots),
   "status":"SOURCE_AND_SALES_QA_HOLD",
   "confirmed_product_or_shade_issue":high_risk.get(gid),
   "per_frame_manual_visual_review_complete":False,
   "stock_packaging_verified":False,"commercial_image_rights_verified":False,
   "frames":slots,
   "excluded_historical_candidates":skips})
report={"version":"2.4.42","base":"production-assets-v2441c-five-new-drafts",
 "goal":"Assemble all 30 families actual pre-existing customer images for hands-on per-frame QA, no image rerendering",
 "families_attempted":30,
 "families_with_5_candidates":sum(x["candidate_frame_count"]==5 for x in records),
 "families_under_5":sum(x["candidate_frame_count"]<5 for x in records),
 "total_copied_existing_JPG_frames":len(all_created),
 "unique_family_ids":30,"new_pixels_generated":False,
 "previous_new_17_JPG_modified":False,"public_55_URLs_overwritten":0,
 "PHOTO_REUSE_RIGHTS_CONFIRMED":0,"FINAL_QA_APPROVED":0,
 "original_source_overwritten":0,
 "candidate_data_rule":"These candidate images require full manual per-frame visual QA; a five-frame folder does NOT mean the set is sales-ready",
 "families":records,
 "next_work":["Review each candidate JPG directly, not collages; reject mismatched products and unverifiable color, package or badges",
 "Use current original package 1/2/3 evidence for OBgE and Cover Lasting exclude No.21",
 "No Shopee upload or public URL publish until actual permission, stock and swatch proof"]}
(OUT/"v2442_30group_candidate_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2442_30group_actual_candidate_sets.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for file in all_created:archive.write(file,arcname=str(file.relative_to(OUT)))
 archive.write(OUT/"v2442_30group_candidate_manifest.json",arcname="v2442_30group_candidate_manifest.json")
with zipfile.ZipFile(OUT/"v2442_30group_actual_candidate_sets.zip") as z:
 assert z.testzip() is None and len(z.namelist())==len(all_created)+1
print(json.dumps({k:report[k] for k in ["families_attempted","families_with_5_candidates","families_under_5","total_copied_existing_JPG_frames","new_pixels_generated","FINAL_QA_APPROVED"]},ensure_ascii=False),flush=True)
