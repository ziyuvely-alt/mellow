#!/usr/bin/env python3
"""v2444: correct actual 150-frame review inventory without rerendering prior JPEG.
Replace erroneous BIOHEAL BOH pending25 frame 1 by EXISTING visually inspected corrected
v2430c file. Quarantine pending27 frames 2-5 that were visually confirmed to contain
unverified MK graphic. All released-sounding statuses explicitly forbidden.
Outputs: 30-family QA manifest, 146 nonquarantined original-byte JPGs, 4 isolated source JPEGs
with all exact hashes and review statuses. No commercial publication or public URL changes.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,csv,zipfile
BASE=Path("prior-v2443b"); FIX=Path("prior-v2430c")
OUT=Path("v2444-output");OUT.mkdir(exist_ok=True)
ORIGINAL=json.loads((BASE/"v2443b_full_30family_manifest.json").read_text())
assert ORIGINAL["product_groups"]==30 and ORIGINAL["actual_existing_plus_new_candidate_JPG"]==150
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(p):
 with Image.open(p) as img:
  img.load()
  assert img.format=="JPEG" and img.size==(1080,1080) and p.stat().st_size<2_000_000,p
REPLACEMENT=FIX/"sales-image-drafts/pending-25/pending-25_official_name_corrected_v2430c.jpg"
assert REPLACEMENT.is_file()
valid(REPLACEMENT)
known_badges={("pending-27",2),("pending-27",3),("pending-27",4),("pending-27",5)}
# The audited frames still contain MK seal; definitive visually verified by opening all four.
records=[];ready_files=[];quarantine_files=[];replacement_count=0
for family in ORIGINAL["families"]:
 gid=family["group_id"]
 revised=[]
 for img in family["current_5_actual_jpgs"]:
  slot=img["slot"]
  p=BASE/img["file"]
  assert p.is_file() and digest(p)==img["sha256"]
  valid(p)
  use=REPLACEMENT if (gid=="pending-25" and slot==1) else p
  if use==REPLACEMENT:replacement_count+=1
  hash_value=digest(use)
  known_badge=(gid,slot) in known_badges
  if known_badge:
   target=OUT/"quarantine-known-visual-defects"/gid/(f"{slot:02d}_"+p.name)
   reason="Visually verified unauthenticated MK logo seal on this exact original 200mL photo frame; not usable until licensed original logo/source repair"
   quarantine_files.append(target)
  else:
   target=OUT/"reusable-customer-JPG-candidates"/gid/(f"{slot:02d}_"+use.name)
   reason="Source or prior successfully corrected JPG retained verbatim; NOT independently commercial-approved"
   ready_files.append(target)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(use,target)
  assert digest(target)==hash_value
  revised.append({"slot":slot,"file":str(target.relative_to(OUT)),
   "sha256":hash_value,
   "change":"reused existing v2430c corrected main" if use==REPLACEMENT else "byte-identical preserved historical source",
   "classification":"QUARANTINE_VISUAL_DEFECT" if known_badge else "CANDIDATE_RIGHTS_QA_HOLD",
   "grounded_reason":reason,"photo_reuse_rights":False,
   "stock_generation_match":False,"full_manual_visual_QA_complete":False,
   "sale_release_approved":False})
 records.append({"group_id":gid,
 "candidate_frames_not_known_defective":sum(x["classification"]=="CANDIDATE_RIGHTS_QA_HOLD" for x in revised),
 "known_defective_frames_quarantined":sum(x["classification"]=="QUARANTINE_VISUAL_DEFECT" for x in revised),
 "finished_five_frame_sale_set":False,"release_permission":False,
 "frames":revised})
assert replacement_count==1 and len(ready_files)==146 and len(quarantine_files)==4 and len(records)==30
assert next(x for x in records if x["group_id"]=="pending-27")["known_defective_frames_quarantined"]==4
assert next(x for x in records if x["group_id"]=="pending-25")["candidate_frames_not_known_defective"]==5
report={
 "version":"2.4.44","predecessor":"production-assets-v2443b-30family-150-JPG-review",
 "source_corrected_photo_branch":"production-assets-v2430c-three-copy-revisions",
 "product_families_reviewed_by_manifest":30,
 "prior_total_JPGs_byte_verified":150,
 "known_visual_defects_quarantined":4,
 "candidate_JPGs_not_yet_commercial_approved":146,
 "old_corrected_JPG_reused_without_rerender":1,
 "new_generated_JPGs":0,
 "known_prior_17_actual_edited_customer_JPGs_reproduced":0,
 "original_531_JPGs_modified":0,"old_55_public_URLs_mutated":0,
 "manual_visual_review_all_150_completed":False,
 "new_official_swatch_charts":0,"final_sale_approved_sets":0,
 "quarantine_reason_matrix":[
  {"group_id":"pending-27","slots":[2,3,4,5],"defect":"MK original logo not verified, images show placeholder badge",
   "product_packaging":"200mL bottle photos visible, no 300mL bottle present after prior filter"},
  {"group_id":"pending-25","slots":[1],"defect":"Historical hero misspells NAD-PRIZCELL as NAD Preezcel",
   "resolution":"Reused visually opened corrected v2430c JPEG, but it still has an unverified MK graphic and needs rights QA"}],
 "remaining_unknowns":[
  "MK logo rights and authenticity on many historical frames (only 4 specific pending27 frames quarantined by direct visual observation)",
  "Peripera and cushion same-generation official color/swatches",
  "Exact physical stock package and commercial photo rights for all 30 groups",
  "Complete manual visual QA across the entire 150-frame candidate pool",
  "No authorization for publishing to Shopee or changing prior 55 public URLs"
 ],
 "families":records}
(OUT/"v2444_quarantine_and_reuse_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (OUT/"v2444_frame_disposition.csv").open("w",newline="",encoding="utf-8") as io:
 writer=csv.writer(io);writer.writerow(["group_id","slot","class","SHA256","path","reason"])
 for f in records:
  for x in f["frames"]:
   writer.writerow([f["group_id"],x["slot"],x["classification"],x["sha256"],x["file"],x["grounded_reason"]])
for filename,files in [("v2444_146_reusable_unapproved_candidates.zip",ready_files),("v2444_4_quarantined_mk_images.zip",quarantine_files)]:
 with zipfile.ZipFile(OUT/filename,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,arcname=str(p.relative_to(OUT)))
  z.write(OUT/"v2444_quarantine_and_reuse_manifest.json",arcname="v2444_quarantine_and_reuse_manifest.json")
 with zipfile.ZipFile(OUT/filename) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
print(json.dumps({k:report[k] for k in ["version","prior_total_JPGs_byte_verified","known_visual_defects_quarantined","candidate_JPGs_not_yet_commercial_approved","old_corrected_JPG_reused_without_rerender","new_generated_JPGs","final_sale_approved_sets"]},ensure_ascii=False),flush=True)
