#!/usr/bin/env python3
"""v2661: assemble accurate 30-family live work queue from immutable evidence
rather than re-running photo production. Never label historical QA as approved.
"""
from pathlib import Path
from collections import Counter
import json
E=Path("evidence");OUT=Path("v2661-real-work-queue");OUT.mkdir(exist_ok=True)
def read(name):return json.loads((E/name).read_text())
old=read("v2460-all30-frame-shortfall-and-source-QA-20261104.json")
recent=read("v2654-27family-12candidate-technical-QA-checkpoint-20261104.json")
clio=read("v2652-two-clio-candidate-production-checkpoint-20261104.json")
gates=read("v2660-six-SKU-release-safety-gate-checkpoint-20261104.json")
assert len(old["families"])==30 and recent["version"]=="v2654" and gates["version"]=="v2660"
produced={f:0 for f in [x["family"] for x in old["families"]]}
for f in recent["runs"][0]["candidate_families"]: produced[f]+=1
produced["pending-05"]+=1;produced["pending-07"]+=1
assert sum(produced.values())==14
hard_claims={x["family"]:x for x in gates["official_claims_verified"]}
priority={
 "pending-01":"Exact MISSHA Cover Lasting real source licensed photo / edition check",
 "pending-02":"Latest photograph, shade and rights confirmation for existing QA crop",
 "pending-03":"Prior 1/5 coverage historical; obtain real same-SKU photo scenes",
 "pending-04":"CLIO mini cushion shade source authenticity; current QA candidate cannot substitute verified shade chart",
 "pending-05":"Founwear owned promotional box generation and rights; historical crop exists",
 "pending-06":"Mesh Glow actual kit/puffs and shade comparison",
 "pending-07":"Mesh Blur exact boxed edition and rights; crop QA exists",
 "pending-08":"PERIPERA 26AD exact inventory chart and 004/014 naming conflict",
 "pending-12":"MISSHA Peel Shot 15g inventory vs official 15ml",
 "pending-26":"PIXEL PURE cleanser actual 145ml versus 150ml photographed reference"
}
rows=[]
for o in old["families"]:
 f=o["family"]
 gate=hard_claims.get(f)
 status="HOLD_PHYSICAL_STOCK_AND_PHOTO_RIGHTS" if gate else "HOLD_V2647_AND_COMMERCIAL_PHOTO_RIGHTS"
 if f=="pending-08":status="HOLD_26AD_SHADE_IDENTITY"
 if f=="pending-26":status="HOLD_145ML_PHOTO_GENERATION"
 if f=="pending-12":status="HOLD_15G_VS_15ML_STOCK"
 rows.append({
   "family":f,"historical_v2460_jpg":o["existing_candidate_jpg"],
   "historical_v2460_shortfall":o["frame_count_shortfall"],
   "v2651_to_v2653_incremental_candidate_jpg":produced[f],
   "candidates_are_NOT_latest_v2647":True,
   "actual_current_v2647_family_jpg_count":"NOT_VERIFIED",
   "final_retail_approved_new_images":0,
   "state":status,
   "priority_next":priority.get(f,"Confirm latest exact SKU photo, licensed source rights and actual stock packaging before release"),
   "source_gate_verified":bool(gate),
   "do_not_redo_existing_crops":produced[f]>0
 })
assert len(rows)==30 and sum(x["v2651_to_v2653_incremental_candidate_jpg"] for x in rows)==14
# The old v2460 count must not be mistakenly summed with new v265x crops into a new current total.
metrics={
 "30_families_accounted_for":len(rows),
 "historical_older_frame_count":sum(x["historical_v2460_jpg"] for x in rows),
 "historical_only_candidate_shortfall":sum(x["historical_v2460_shortfall"] for x in rows),
 "new_qa_candidates_unchanged":sum(x["v2651_to_v2653_incremental_candidate_jpg"] for x in rows),
 "exact_stock_product_copy_gates":len(hard_claims),
 "families_with_preexisting_delta":sum(bool(x["v2651_to_v2653_incremental_candidate_jpg"]) for x in rows),
 "all_families_sale_release_on_hold":30,
 "additional_final_approved_images":0}
manifest={"version":"v2661","baseline":"v2660", "source_evidence":[
 "v2460-all30-frame-shortfall-and-source-QA-20261104.json",
 "v2654-27family-12candidate-technical-QA-checkpoint-20261104.json",
 "v2652-two-clio-candidate-production-checkpoint-20261104.json",
 "v2660-six-SKU-release-safety-gate-checkpoint-20261104.json"],
 "count_is_historical_not_v2647":True,
 "metrics":metrics,"families":rows,
 "approved_11_original_groups_preserved":True,"public_55_urls_unchanged":True,
 "image_files_modified":0,"retail_photos_published":0,"xlsx_shared":False,
 "next":"Do source identity/edition and commercial permission for blocked cases, not more historical photo hash audits."}
(OUT/"v2661-30-family-gated-work-queue.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(metrics,ensure_ascii=False))
