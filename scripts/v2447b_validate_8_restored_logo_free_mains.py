#!/usr/bin/env python3
"""v2447b check eight actual previous source-backed logo-free photo candidates.
Compare with four real-known MK seal images; do not mutate or re-render prior JPGs.
Produce verified manifest with exact source SHA-256 and content/stock/rights holds.
"""
from pathlib import Path
import cv2,numpy as np
import hashlib,json,csv
SRC=Path("prior-v2447")
BASE=Path("prior-v2445b")
OUT=Path("v2447b-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((SRC/"v2447_eight_family_mains_checkpoint.json").read_text())
old=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def img(p):
 a=cv2.imread(str(p),cv2.IMREAD_COLOR)
 assert a is not None and a.shape[:2]==(1080,1080),p
 return a
templates=[]
positive=[r for r in old["asset_rows"] if r["disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
assert len(positive)==4
for row in positive:
 p=BASE/row["file"];assert sha(p)==row["sha256"]
 data=img(p)
 for x,y,w,h in [(834,736,77,82),(842,748,61,68),(827,733,90,88)]:
  templates.append(cv2.cvtColor(data[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY))
assert len(templates)==12
def score(p):
 roi=cv2.cvtColor(img(p)[675:895,760:996],cv2.COLOR_BGR2GRAY)
 return max(float(cv2.minMaxLoc(cv2.matchTemplate(roi,tmp,cv2.TM_CCOEFF_NORMED))[1]) for tmp in templates)
pos_scores=[score(BASE/r["file"]) for r in positive]
assert min(pos_scores)>0.99,pos_scores
result=[]
for x in manifest["results"]:
 p=SRC/x["output"];assert p.is_file() and sha(p)==x["output_SHA256"]
 value=score(p)
 result.append({"group_id":x["group_id"],"file_in_existing_v2447_branch":x["output"],"SHA256":x["output_SHA256"],
   "original_or_reused": "NEW_REAL_PHOTO_CROP" if x["new_image"] else "PRIOR_SUCCESS_REUSED",
   "known_MK_template_similarity":round(value,5),
   "MK_template_result":"MATCH_REVIEW_REQUIRED" if value>=0.68 else "NOT_MATCHED_BY_KNOWN_TEMPLATE",
   "commercial_photo_license_verified":False,"stock_packaging_verified":False,"photo_real_photo":True,
   "complete_five_frame_set":False,"sales_approved":False})
assert len(result)==8
report={"version":"2.4.47b",
 "source":"production-assets-v2447-eight-real-source-mains",
 "audited_8_candidate_JPGs":len(result),
 "positive_known_logo_reference_count":len(pos_scores),
 "positive_controls_min_corr":min(pos_scores),
 "potential_logo_matches":sum(x["MK_template_result"]=="MATCH_REVIEW_REQUIRED" for x in result),
 "new_photo_pixels_drawn":0,"new_JPGs_in_this_QA_pass":0,
 "already_reused_previous_5_unchanged":True,
 "prior_64_quarantined_unpublished":True,
 "prior_86_rights_hold_candidates_preserved":True,
 "restored_families_with_one_logo-template-nonmatch_photo":len(result)-sum(x["MK_template_result"]=="MATCH_REVIEW_REQUIRED" for x in result),
 "logo_not_detected_does_not_prove_license_or_stock":True,
 "original_published_55_URLs_modified":0,
 "final_sales_approved":0,
 "results":result,
 "next_work":["Identify real product full-photo commercial reuse permissions for 8 recovered photo candidates",
              "Continue individual frame inspection, false-shade and exact package generation QA for other 30 groups",
              "Never turn MK logo-detected 64 sources into registered product assets until source ownership resolved"]}
(OUT/"v2447b_eight_restored_visual_logo_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (OUT/"v2447b_eight_restored_visual_logo_QA.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
print(json.dumps({k:report[k] for k in ("audited_8_candidate_JPGs","positive_controls_min_corr","potential_logo_matches","restored_families_with_one_logo-template-nonmatch_photo","new_JPGs_in_this_QA_pass","final_sales_approved")},ensure_ascii=False))
