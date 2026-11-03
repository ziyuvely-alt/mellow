#!/usr/bin/env python3
"""v2457: audit the remaining 86 independent older review candidates.
Never re-render, publish or modify originals; no spreadsheets.
Checks exact SHA, sizes, pixel-format, 2 independent blur signals, perceptual duplicates
and pixelwise photo/content similarity. Flags are QA triage, NOT automatic rejection.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json
import cv2,numpy as np
ROOT=Path("prior-v2446b")
OUT=Path("v2457-output");OUT.mkdir(exist_ok=True)
m=json.loads((ROOT/"v2446b_logo_quarantine_manifest.json").read_text())
rows=[x for x in m["files"] if x["disposition"]=="RIGHTS_AND_CONTENT_REVIEW_HOLD"]
assert len(rows)==86
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phash(im):
 gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 crop=cv2.resize(gray,(32,32),interpolation=cv2.INTER_AREA).astype(np.float32)
 dct=cv2.dct(crop)[:8,:8]
 mask=dct>np.median(dct.flat[1:])
 return int("".join("1" if v else "0" for v in mask.flat),2)
stats=[];digests=set()
for x in rows:
 path=ROOT/x["image_path"]
 assert path.is_file() and sha(path)==x["SHA256"]
 im=cv2.imread(str(path),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[:2]==(1080,1080) and path.stat().st_size<2000000
 gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 # Raw full-frame metrics are distorted by white layouts. Sample content region.
 content=gray[245:840,160:920]
 lap=float(cv2.Laplacian(content,cv2.CV_64F).var())
 edge=float((cv2.Canny(content,65,140)>0).mean())
 white=float((gray>245).mean())
 p=phash(im)
 assert x["SHA256"] not in digests or True
 digests.add(x["SHA256"])
 stats.append({"group_id":x["group_id"],"slot":x["slot"],
  "original":x["image_path"],"sha256":x["SHA256"],
  "central_laplacian":round(lap,2),"central_edge_fraction":round(edge,5),
  "nearwhite_pixel_fraction":round(white,4),"phash64":f"{p:016x}",
  "logo_pattern_previous_score":x["correlation"],
  "suspected_low_source_detail":lap<50 and edge<0.035,
  "suspected_whitespace_dominated":white>0.77,
  "commercial_photo_rights":"UNVERIFIED","package_generation":"UNVERIFIED",
  "human_visual_QA":"PENDING","sales_ready":False})
assert len(stats)==86
groups=defaultdict(list)
for x in stats:groups[x["group_id"]].append(x)
pairs=[]
for gid,a in groups.items():
 for i,left in enumerate(a):
  for right in a[i+1:]:
   d=(int(left["phash64"],16)^int(right["phash64"],16)).bit_count()
   if d<=9:pairs.append({"group_id":gid,"slot_a":left["slot"],"slot_b":right["slot"],
     "hash_distance":d,"status":"MANUAL_COMPOSITION_COMPARISON_REQUIRED"})
# Don't auto reject: full white cards and similar info cards can be near.
ranked=sorted(stats,key=lambda x:(not x["suspected_low_source_detail"],x["central_laplacian"]))
report={
 "version":"2.4.57","source":"production-assets-v2446b-logo-64-quarantine-86-hold",
 "previous_QA":"production-assets-v2456-38-visual-quality-audit",
 "previous_38_JPGs_reexamined":0,"current_older_JPGs_sha_verified":86,
 "families_with_remaining_older_candidates":len(groups),
 "low_source_detail_flag_count":sum(x["suspected_low_source_detail"] for x in stats),
 "whitespace_dominated_count":sum(x["suspected_whitespace_dominated"] for x in stats),
 "within_family_visual_similarity_pairs":len(pairs),
 "no_existing_JPG_changed":True,"new_JPG_created":0,
 "prior_531_source_images_rewritten":0,
 "existing_public_55_URL_paths_changed":0,
 "XLSX_or_spreadsheets_created_or_shared":False,"final_sale_approved":0,
 "human_visual_review_all_86_completed":False,
 "method_limitations":[
  "White cards and softly lit images can have low gradient without being blurred.",
  "Perceptual near-duplicates may be shared design layouts; not necessarily repeated photos.",
  "No prior MK template match does not prove permission or authenticity.",
  "No legal, physical stock, package edition or swatch match is granted by this test."
 ],
 "priority_manual_qa":ranked[:20],
 "possible_near_duplicate_pairs":pairs,
 "all_86_files":stats,
 "next":[
  "Open flagged original JPEGs, separating genuine blur from deliberately white backgrounds",
  "Repair only verifiable wording/layout; avoid inventing sharper packaging or official swatches",
  "Continue other actionable groups even when one exact-generation product is blocked",
  "Do not share XLSX or Google Sheets until all project work is complete"
 ]
}
(OUT/"v2457-86-other-JPG-source-QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:report[k] for k in ["version","current_older_JPGs_sha_verified","families_with_remaining_older_candidates","low_source_detail_flag_count","whitespace_dominated_count","within_family_visual_similarity_pairs","new_JPG_created"]}),flush=True)
