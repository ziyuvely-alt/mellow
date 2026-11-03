#!/usr/bin/env python3
"""v2448b consolidate 8 existing logo-template-negative main JPGs and 7 new detail JPGs.
Reverify SHA256, 1080x1080, <2 MB, and check MK logo templating against the four
previous positive controls. All 15 remain strictly DRAFT until stock and rights QA.
"""
from pathlib import Path
from PIL import Image
import cv2,numpy as np
import json,hashlib,shutil,zipfile,csv
A=Path("prior-v2447");B=Path("prior-v2448");CONTROLS=Path("prior-v2445b")
OUT=Path("v2448b-output");OUT.mkdir(exist_ok=True)
ma=json.loads((A/"v2447_eight_family_mains_checkpoint.json").read_text())
mb=json.loads((B/"v2448_checkpoint.json").read_text())
mc=json.loads((CONTROLS/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imread(p):
 im=cv2.imread(str(p),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[:2]==(1080,1080)
 return im
positive=[r for r in mc["asset_rows"] if r["disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
assert len(positive)==4
template=[]
for row in positive:
 p=CONTROLS/row["file"]
 assert sha(p)==row["sha256"]
 im=imread(p)
 for x,y,w,h in [(834,736,77,82),(842,748,61,68),(827,733,90,88)]:
  template.append(cv2.cvtColor(im[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY))
def score(p):
 roi=cv2.cvtColor(imread(p)[675:895,760:996],cv2.COLOR_BGR2GRAY)
 return max(float(cv2.minMaxLoc(cv2.matchTemplate(roi,t,cv2.TM_CCOEFF_NORMED))[1]) for t in template)
assert min(score(CONTROLS/r["file"]) for r in positive)>0.99
results=[];seen=set()
for source,rows,pathkey,sha_key,role in [(A,ma["results"],"output","output_SHA256","photo_main"),(B,mb["new_frame_results"],"new_JPG","new_sha256","photo_detail")]:
 for row in rows:
  gid=row["group_id"]
  p=source/row[pathkey]
  assert p.is_file() and sha(p)==row[sha_key]
  with Image.open(p) as check:
   check.load()
   assert check.format=="JPEG" and check.size==(1080,1080) and p.stat().st_size<2_000_000
  key=(gid,role);assert key not in seen,key
  seen.add(key)
  corr=score(p)
  # Positive logo match means no promotion and no merging into potentially usable candidate pool.
  status="MK_LOGO_REVIEW_HOLD" if corr>=0.68 else "NO_KNOWN_MK_PATTERN_RIGHTS_QA_HOLD"
  dst=OUT/"15-real-photo-review-candidates"/gid/(role+"__"+p.name)
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,dst)
  assert sha(dst)==row[sha_key]
  results.append({"group_id":gid,"frame_kind":role,"file":str(dst.relative_to(OUT)),
   "sha256":row[sha_key],"MK_pattern_corr":round(corr,5),"status":status,
   "right_to_reuse_photograph_verified":False,"source_package_version_verified":False,
   "approved_for_Shopee":False})
assert len(results)==15 and len(seen)==15
groups=sorted(set(x["group_id"] for x in results))
assert len(groups)==8,groups
report={"version":"2.4.48b","source_new":"production-assets-v2448-seven-photo-details",
 "source_reused":"production-assets-v2447-eight-real-source-mains",
 "source_MK_positive_controls":"production-assets-v2445b-corrected-QA-hold-146",
 "JPG_exact_byte_verified":15,"groups_with_one_or_two_JPG":8,
 "photo_main_reused":8,"new_photo_detail_JPG_from_v2448":7,
 "known_MK_template_matches":sum(x["status"]=="MK_LOGO_REVIEW_HOLD" for x in results),
 "all_15_no_template_logo_match":all(x["status"]!="MK_LOGO_REVIEW_HOLD" for x in results),
 "all_15_actual_photographs_1080x1080_under_2MB":True,
 "original_531_jpg_overwrites":0,"existing_public_55_urls_changed":0,
 "historic_64_MK_images_quarantined_unmodified":True,
 "historic_86_hold_JPG_unmodified":True,
 "official_same_generation_shade_charts_approved":0,
 "commercial_image_rights_verified":0,"new_final_sale_approved_sets":0,
 "unverified_MISSHA_23_25_swatch_did_not_generate":True,
 "results":results,
 "next_actions":["No regeneration of 15 validated draft images","Continue first-hand per-frame checks on remaining historical 86 sources",
 "Obtain authentic brand photo usage rights, MK source PNG if brand logo needed",
 "Verify exact product package/shade generation and stock prior to publishing"]
}
(OUT/"v2448b-15photo-resumable-checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with (OUT/"v2448b-15photo-verification.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
with zipfile.ZipFile(OUT/"v2448b_15_source-backed_JPGs_NOT_FINAL.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for row in results:z.write(OUT/row["file"],arcname=row["file"])
 z.write(OUT/"v2448b-15photo-resumable-checkpoint.json",arcname="v2448b-15photo-resumable-checkpoint.json")
with zipfile.ZipFile(OUT/"v2448b_15_source-backed_JPGs_NOT_FINAL.zip") as z:assert z.testzip() is None and len(z.namelist())==16
print(json.dumps({k:report[k] for k in ["version","JPG_exact_byte_verified","groups_with_one_or_two_JPG","known_MK_template_matches","all_15_no_template_logo_match","new_final_sale_approved_sets"]},ensure_ascii=False),flush=True)
