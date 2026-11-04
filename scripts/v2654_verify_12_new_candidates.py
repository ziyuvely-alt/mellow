#!/usr/bin/env python3
"""v2654 independent acceptance gate for exactly v2653 new QA image files.
Verifies outputs, photo composition statistics, release-blocker classifications.
No original image rebuild, no approval/publication, no spreadsheet.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageStat
import json,hashlib
SRC=Path("source/v2653")
OUT=Path("v2654-qa-gated-candidates");OUT.mkdir(exist_ok=True)
report=json.loads((SRC/"summary.json").read_text())
assert report["version"]=="v2653" and report["new_QA_candidate_files"]==12
known={
 "pending-08":"26AD inventory edition and licensed exact shade chart required",
 "pending-26":"145mL actual physical stock; mixed 150mL source gallery quarantine",
 "pending-29":"v2646 changed frame01; compare latest real photographs before merge",
 "pending-02":"Verify exact option/edition and color photo before using"
}
candidates=[];no_candidate=[]
for row in report["results"]:
    fam=row["family"]
    cand=row.get("staged_candidate")
    if not cand:
        if row["historical_candidate_pairs"]:
            no_candidate.append({"family":fam,"reason":row.get("no_candidate_reason","unknown")})
        continue
    p=SRC/cand["file"]
    assert p.exists(),p
    image=Image.open(p);image.load()
    assert image.format=="JPEG" and image.size==(1080,1080) and p.stat().st_size<2_000_000
    assert hashlib.sha256(p.read_bytes()).hexdigest()==cand["sha256"]
    assert image.getextrema()!=((0,0),)*3
    grey=ImageOps.grayscale(image)
    std=ImageStat.Stat(grey).stddev[0]
    is_retail_blocked=bool(known.get(fam))
    candidates.append({
     "family":fam,"file":p.name,"file_SHA256":cand["sha256"],"bytes":p.stat().st_size,
     "previous_pair":cand["slots"],"dhash_distance":cand["dhash_distance"],
     "grayscale_stdev":round(std,2),
     "tech_QA":"PASS",
     "visual_release_status":"HOLD_MORE_EVIDENCE",
     "commercial_photo_rights":"UNVERIFIED",
     "exact_packaging_version":"UNVERIFIED",
     "specific_warning":known.get(fam,"Latest v2647 original and actual stock edition not compared"),
     "candidate_not_sales_ready":True
    })
assert len(candidates)==12
summary={"version":"v2654","source_v2653_run":41824399357,
 "files_inspected":len(candidates),"technical_pass":12,
 "commercial_approved":0,"cross_revision_hold":12,
 "missing_candidate_families":no_candidate,
 "image_hashes_verified":True,"source_is_historical":True,
 "old_11_approved_groups_untouched":True,"existing_public_55_urls_untouched":True,
 "never_share_xlsx":True,
 "results":candidates,
 "next":"Acquire true latest v2647 image bytes; manual proof product detail and licensing for 12 candidates; no automatic retail replacement"}
(OUT/"v2654-independent-candidate-QA.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"checked":len(candidates),"tech_pass":len(candidates),
                  "retail_approved":0,"missing_candidate_groups":no_candidate},ensure_ascii=False))
