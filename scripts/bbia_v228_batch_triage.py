#!/usr/bin/env python3
"""Batch triage only: no recomposition, no binary overwrites, no invented family approvals."""
from pathlib import Path
from collections import defaultdict
import hashlib,json
ROOT=Path("public/images")
OUT=Path("/tmp/bbia-v228")
OUT.mkdir(exist_ok=True,parents=True)
KNOWN_HOLDS={
"206":"Shade photography approval and frame04 visual QA pending",
"200":"Historical v213 candidates not available in published tree",
"1000000124":"Refill true high-res photo unavailable",
"1000000122":"Fullsize shared photos do not prove refill package"}
families=defaultdict(list)
sha=defaultdict(list)
for p in sorted(ROOT.rglob("*.jpg")):
    family=p.relative_to(ROOT).parts[0]
    data=p.read_bytes()
    h=hashlib.sha256(data).hexdigest()
    row={"file":str(p),"bytes":len(data),"sha256":h}
    families[family].append(row)
    sha[h].append(str(p))
all_keys=sorted(set(families)|set(KNOWN_HOLDS))
results=[]
for key in all_keys:
    imgs=families[key]
    files={x["sha256"] for x in imgs}
    status="HAS_FIVE_CANDIDATES_NEEDS_VISUAL_QA" if len(files)>=5 else "LESS_THAN_FIVE_PUBLISHED_CANDIDATES"
    if key in KNOWN_HOLDS:
        status="HOLD_SPECIFIC_EVIDENCE"
    results.append({"goodsNo":key,"jpg_count":len(imgs),"distinct_hashes":len(files),
      "status":status,"hold_reason":KNOWN_HOLDS.get(key),"auto_sales_approved":False})
report={
 "checkpoint":"v228","type":"BATCH_NON_DESTRUCTIVE_INVENTORY","scope":"Published repository JPGs only, not historical ZIP candidate completion",
 "published_image_count":sum(len(v) for v in families.values()),
 "family_directories":len(families),
 "status_rows":results,
 "duplicate_sha_groups":[v for v in sha.values() if len(v)>1],
 "rules":{"do_not_rerender_finished":True,"do_not_modify_published":True,
          "no_automatic_sales_approval":True,"skip_blocked_and_continue":True,
          "publish_only_after_source_visual_variant_QA":True},
 "separate_historical_48_family_master_required":True,
 "recommended_next_batch":"Map existing selected review archives into distinct creative roles for all 48 products, then queue only missing authenticated roles."
}
(OUT/"BBIA_v228_BATCH_TRIAGE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V228_BATCH",json.dumps({"published_images":report["published_image_count"],
 "published_family_dirs":len(families),"families_with_five_or_more_public":sum(len(set(x["sha256"] for x in a))>=5 for a in families.values()),
 "duplicate_groups":len(report["duplicate_sha_groups"]),"explicit_holds":list(KNOWN_HOLDS)},ensure_ascii=False))
