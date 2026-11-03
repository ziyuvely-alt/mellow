#!/usr/bin/env python3
"""v2446 run deterministic visual watermark-presence audit over 146 EXISTING JPEGs.
The four known MK seal frames are training/positive controls, NOT sale outputs.
Copies no JPGs; produces source-hash-verified per-frame risk assessment only.
No OCR, artificial imagery, contact sheets, auto-approval or publication.
"""
from pathlib import Path
import hashlib,json,csv
import cv2,numpy as np
ROOT=Path("prior-v2445b")
OUT=Path("v2446-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((ROOT/"v2445b-resumable-checkpoint.json").read_text())
rows=manifest["asset_rows"];assert len(rows)==150
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def image(path):
 im=cv2.imread(str(path),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[:2]==(1080,1080)
 return im
positives=[r for r in rows if r["disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
candidates=[r for r in rows if r["disposition"]=="REUSABLE_ONLY_AFTER_FULL_APPROVAL"]
assert len(positives)==4 and len(candidates)==146
# Fixed position based on direct visual review; logo circle typically x826..917 y728..830.
# Define multiple slightly offset positive-control templates to tolerate JPEG re-encoding
# and subtly different source treatments. We audit right-bottom visual region only.
templates=[]
for r in positives:
 p=ROOT/r["file"];assert p.is_file() and digest(p)==r["sha256"]
 im=image(p)
 for (x,y,w,h) in [(834,736,77,82),(842,748,61,68),(827,733,90,88)]:
  gray=cv2.cvtColor(im[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY)
  if float(np.std(gray))>12:templates.append(gray)
assert templates,len(templates)
checks=[]
for r in rows:
 p=ROOT/r["file"];assert p.is_file() and digest(p)==r["sha256"]
 im=image(p)
 roi=cv2.cvtColor(im[675:895,760:996],cv2.COLOR_BGR2GRAY)
 best=-1;where=None
 for idx,temp in enumerate(templates):
  response=cv2.matchTemplate(roi,temp,cv2.TM_CCOEFF_NORMED)
  _,value,_,loc=cv2.minMaxLoc(response)
  if value>best: best=float(value);where=[int(loc[0]+760),int(loc[1]+675)]
 # This is NOT official visual approval. Detection confidence is not product accuracy.
 result={
  "group_id":r["family"],"slot":r["slot"],"source_path":r["file"],
  "sha256":r["sha256"],"legacy_disposition":r["disposition"],
  "MK_visual_template_max_corr":round(best,5),"peak_x_y":where,
  "auto_qa":"LIKELY_MK_LOGO_REVIEW" if best>=0.68 else ("MAYBE_MK_LOGO_REVIEW" if best>=0.48 else "NOT_DETECTED_BY_THIS_TEMPLATE"),
  "source_photo_rights_approved":False,"stock_packaging_approved":False,
  "final_sales_approved":False
 }
 checks.append(result)
assert len(checks)==150
positive_scores=[x["MK_visual_template_max_corr"] for x in checks if x["legacy_disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
if min(positive_scores)<0.68:
 # An inadequate logo detector must not imply safety. Flag every frame as unverified.
 for x in checks:x["auto_qa"]="DETECTOR_POSITIVE_CONTROL_FAILED_REVIEW"
candidates_checked=[x for x in checks if x["legacy_disposition"]!="KNOWN_MK_BADGE_QUARANTINE"]
likely=[x for x in candidates_checked if x["auto_qa"]=="LIKELY_MK_LOGO_REVIEW"]
maybe=[x for x in candidates_checked if x["auto_qa"]=="MAYBE_MK_LOGO_REVIEW"]
report={
 "version":"2.4.46","source_checkpoint":"production-assets-v2445b-corrected-QA-hold-146",
 "algorithm":"OpenCV normalized cross-correlation, 4 known-MK photo positive controls, 3 right-lower circular-logo templates per photo, ROI x760:996 y675:895",
 "candidate_JPG_sha256_and_dimensions_reverified":len(candidates_checked),
 "known_logo_positive_controls_verified":len(positives),
 "known_positive_control_scores":positive_scores,
 "candidate_likely_logo_count":len(likely),"candidate_maybe_logo_count":len(maybe),
 "other_candidate_not_detected_count":len(candidates_checked)-len(likely)-len(maybe),
 "known_quarantine_images_retained":4,
 "new_user_JPG_generated":0,"previous_customer_JPG_regenerated":0,"published_55_URLs_changed":0,
 "logo_template_does_not_establish_logo_authenticity":True,
 "not_detected_does_not_mean_rights_approved":True,
 "complete_manual_visual_review_146":False,"sale_approved":0,
 "likely_by_group":{group:len([x for x in likely if x["group_id"]==group]) for group in sorted(set(x["group_id"] for x in likely))},
 "must_visually_confirm_before_new_quarantine":True,
 "next":["Open each top-scoring newly flagged JPG in GitHub and confirm the mark by visual inspection",
         "Quarantine only verified defective frames; no false sales release for other images",
         "Continue edition and original-photo licensing checks, no altered/fabricated packaging"],
 "frames":checks
}
(OUT/"v2446_visual_logo_detection_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (OUT/"v2446_150frame_logo_QA.csv").open("w",newline="",encoding="utf-8") as handle:
 keys=list(checks[0]);w=csv.DictWriter(handle,fieldnames=keys);w.writeheader();w.writerows(checks)
print(json.dumps({k:report[k] for k in ["version","candidate_JPG_sha256_and_dimensions_reverified","known_positive_control_scores","candidate_likely_logo_count","candidate_maybe_logo_count","other_candidate_not_detected_count","new_user_JPG_generated"]},ensure_ascii=False),flush=True)
