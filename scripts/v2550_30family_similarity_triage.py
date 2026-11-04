#!/usr/bin/env python3
"""v2550: non-destructive image diversity triage on v2549 156-JPEG archive.
QA outputs only: no image overwrite, no URL publishing, no spreadsheet.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json, math
R=Path("v2550-input/manifest.json")
assert R.is_file(), "Missing v2549 manifest"
m=json.loads(R.read_text())
assert m["total_physical_JPEGs"]==156 and m["total_families"]==30
records=m["file_records"]
assert len(records)==156
OUT=Path("v2550-30family-diversity-triage");OUT.mkdir(exist_ok=True)
base=Path("v2550-input")
family={}
for n in range(1,31):
    key=f"pending-{n:02d}"
    group=[x for x in records if x["family"]==key]
    assert len(group)==(6 if n in (1,2,4,5,6,7) else 5)
    exact=len({x["sha256"] for x in group})!=len(group)
    pairs=[]
    for a,b in combinations(group,2):
        d=(int(a["dhash"])^int(b["dhash"])).bit_count()
        if d<=10:
            pairs.append({"slots":[a["slot"],b["slot"]],"distance":d,
             "level":"HIGH_SIMILARITY" if d<=6 else "REVIEW_SIMILARITY"})
    flags=[]
    if exact:flags.append("EXACT_DUPLICATE")
    if pairs:flags.append("MANUAL_VISUAL_DIVERSITY_REVIEW")
    family[key]={"image_count":len(group),"similarity_pairs":pairs,
      "review_flags":flags,"status":"QA_REVIEW_NOT_SALES_APPROVED"}
review=sorted(family, key=lambda k:(-len(family[k]["similarity_pairs"]),k))
out={"version":"v2550","source":"v2549 successful workflow artifact",
 "source_artifact_manifest_image_count":156,"families":30,
 "product_images_edited":0,"new_public_urls":0,"xlsx_created":False,
 "original_55_urls_preserved":True,
 "candidate_pairs_0_to_6":sum(sum(p["distance"]<=6 for p in v["similarity_pairs"]) for v in family.values()),
 "candidate_pairs_7_to_10":sum(sum(7<=p["distance"]<=10 for p in v["similarity_pairs"]) for v in family.values()),
 "priority_review_order":review,"by_family":family,
 "release_gates":[
  "Source image commercial usage rights require affirmative verification",
  "MellowKR original round MK logo asset is not available in this run",
  "Pixelpure cleanser inventory 145 ml vs photographed 150 ml mismatch unresolved",
  "Official swatch/shade verification incomplete for some option groups",
  "Full human visual and product-claim validation remains mandatory"],
 "commercial_release_approved":False,
 "notes":"Similarity candidates are not proof of duplicate or bad imagery. Never auto-delete."}
(OUT/"triage.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
lines=["# v2550 | 30-family similarity triage","","No images were modified or published.","",
"| Family | Images | Pairs <=6 | Pairs 7-10 | State |","|---|---:|---:|---:|---|"]
for k in review:
    v=family[k]; a=sum(p["distance"]<=6 for p in v["similarity_pairs"])
    b=sum(7<=p["distance"]<=10 for p in v["similarity_pairs"])
    lines.append(f"| {k} | {v['image_count']} | {a} | {b} | QA hold |")
lines+=["","## Important","Automated perceptual screening is only a candidate queue.",
 "Original 11 approved families and 55 verified URLs remain unchanged.",
 "No Excel and no release approval."]
(OUT/"review-order.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"images":156,"families":30,"pairs_le6":out["candidate_pairs_0_to_6"],"pairs_7to10":out["candidate_pairs_7_to_10"],"url_changes":0}))
