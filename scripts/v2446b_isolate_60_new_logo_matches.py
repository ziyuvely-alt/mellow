#!/usr/bin/env python3
"""v2446b: physically separate all 64 high-confidence template-matched MK graphics
(4 previous + 60 new), preserving 86 other JPGs as unapproved risk-held candidates.
Copy bytes only; no JPEG regeneration, never advertise logo-free or sale approval.
"""
from pathlib import Path
from PIL import Image
import csv,hashlib,json,shutil,zipfile
SRC=Path("prior-v2445b");QA=Path("prior-v2446")
OUT=Path("v2446b-output");OUT.mkdir(exist_ok=True)
orig=json.loads((SRC/"v2445b-resumable-checkpoint.json").read_text())
test=json.loads((QA/"v2446_visual_logo_detection_manifest.json").read_text())
rows=orig["asset_rows"];scores={(r["group_id"],r["slot"]):r for r in test["frames"]}
assert len(rows)==150 and len(scores)==150
assert test["candidate_likely_logo_count"]==60 and min(test["known_positive_control_scores"])>=0.99
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
safe=[];hold=[];items=[]
for item in rows:
 k=(item["family"],item["slot"]);t=scores[k]
 src=SRC/item["file"];assert src.is_file() and sha(src)==item["sha256"]==t["sha256"]
 with Image.open(src) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080) and src.stat().st_size<2_000_000
 prior_quarantined=(item["disposition"]=="KNOWN_MK_BADGE_QUARANTINE")
 newhigh=t["auto_qa"]=="LIKELY_MK_LOGO_REVIEW" and t["MK_visual_template_max_corr"]>=0.995
 mark=prior_quarantined or newhigh
 # If positive controls failed the detector, this script aborts without approving anything.
 dest=OUT/("64-automated-logo-quarantine" if mark else "86-unapproved-candidates-logo-not-matched")/item["family"]/f"{item['slot']:02d}_{src.name}"
 dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,dest)
 assert sha(dest)==item["sha256"]
 (hold if mark else safe).append(dest)
 items.append({
 "group_id":item["family"],"slot":item["slot"],"image_path":str(dest.relative_to(OUT)),
 "SHA256":item["sha256"],"correlation":t["MK_visual_template_max_corr"],
 "logo_detection":"PREVIOUSLY_CONFIRMED_BY_VISUAL_INSPECTION" if prior_quarantined else ("HIGH_CONFIDENCE_TEMPLATE_MATCH_ISOLATED" if newhigh else "NOT_MATCHED_BY_THIS_TEST"),
 "disposition":"QUARANTINE" if mark else "RIGHTS_AND_CONTENT_REVIEW_HOLD",
 "requires_complete_manual_visual_QA":True,"commercial_photo_rights_verified":False,
 "actual_stock_package_verified":False,"sales_approved":False})
assert len(hold)==64 and len(safe)==86 and len(items)==150
groups=[]
for n in range(1,31):
 gid=f"pending-{n:02d}"
 subset=[i for i in items if i["group_id"]==gid]
 kept=[i for i in subset if i["disposition"]!="QUARANTINE"]
 assert len(subset)==5
 # Name-pattern only as a triage signal, not manual verification.
 photo_patterns=["INV_","PHOTO_","SOURCE_","HERO_","actual_photo","original_photo","real_photo","full_bottle","full_jar"]
 photo_like=[x for x in kept if any(z.lower() in x["image_path"].lower() for z in photo_patterns)]
 groups.append({"group_id":gid,"total_photos_in_previous_five_frame_group":5,
 "logo_template_quarantined":5-len(kept),"remaining_unapproved_JPGs":len(kept),
 "remaining_names_indicating_possible_product_photo":len(photo_like),
 "product_photo_was_visually_verified":False,
 "five_frame_sales_set_complete":False,
 "content_rights_swatch_and_stock_hold":True})
report={
 "version":"2.4.46b","previous":"production-assets-v2445b-corrected-QA-hold-146",
 "detector_source":"production-assets-v2446-all-150-logo-QA",
 "original_150_JPGs_SHA256_reverified":True,
 "original_531_source_overwrites":0,
 "new_JPGs_rendered":0,
 "prior_logo_quarantine_count":4,
 "new_high_confidence_logo_matches_quarantined":60,
 "total_quarantined_frames":len(hold),
 "remaining_unapproved_candidate_frames":len(safe),
 "photo_template_CCOEFF_min_of_new_high_matches":min(x["correlation"] for x in items if x["logo_detection"]=="HIGH_CONFIDENCE_TEMPLATE_MATCH_ISOLATED"),
 "old_55_public_URL_path_changes":0,"new_final_sales_approvals":0,
 "not_detected_not_equivalent_to_logo_free":True,
 "no_rights_proof_from_template_matching":True,
 "groups_with_zero_nonquarantined_frames":[g["group_id"] for g in groups if g["remaining_unapproved_JPGs"]==0],
 "groups_without_photo_name_candidates":[g["group_id"] for g in groups if g["remaining_names_indicating_possible_product_photo"]==0],
 "all_30_group_dispositions":groups,
 "files":items,
 "remaining":["Source-rights verified original MK PNG still unavailable","Each isolated JPG requires original asset/rights and exact package; no invented MK badges","Check 86 other customer images visually, not all are logo free","Many families now lack five eligible pictures; never fill with duplicate/fake photos","Official option swatch shade generation mismatch unresolved"]
}
(OUT/"v2446b_logo_quarantine_manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with (OUT/"v2446b_150_JPG_dispositions.csv").open("w",encoding="utf-8",newline="") as f:
 cols=["group_id","slot","image_path","SHA256","correlation","logo_detection","disposition"];wr=csv.writer(f);wr.writerow(cols)
 for i in items:wr.writerow([i[c] for c in cols])
for name,files in [("v2446b_64_highconf_MK_isolated.zip",hold),("v2446b_86_remaining_rights_hold_JPGs.zip",safe)]:
 with zipfile.ZipFile(OUT/name,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,arcname=str(p.relative_to(OUT)))
  z.write(OUT/"v2446b_logo_quarantine_manifest.json",arcname="v2446b_logo_quarantine_manifest.json")
 with zipfile.ZipFile(OUT/name) as z:assert len(z.namelist())==len(files)+1 and z.testzip() is None
print(json.dumps({k:report[k] for k in ("version","new_high_confidence_logo_matches_quarantined","total_quarantined_frames","remaining_unapproved_candidate_frames","groups_with_zero_nonquarantined_frames","groups_without_photo_name_candidates","new_JPGs_rendered")},ensure_ascii=False),flush=True)
