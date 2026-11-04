#!/usr/bin/env python3
"""v2664 enforce actual visual QA verdicts before any sales asset promotion.
Runs from verified evidence; no image generation, mutation, or deployment.
"""
import json
from pathlib import Path
src=Path("evidence/v2663-actual-14-photo-visual-qa-hold-and-reject-20261104.json")
d=json.loads(src.read_text()); rows=d["files"]
assert len(rows)==14 and len({x["family"] for x in rows})==14
reject=[x for x in rows if x["status"].startswith("REJECT")]
hold=[x for x in rows if x["status"].startswith("HOLD")]
assert len(reject)==9 and len(hold)==5
assert len(reject)==d["counts"]["explicit_visual_reject"]
assert len(hold)==d["counts"]["hold_for_proof"]
for x in rows:
 assert x["status"]!="APPROVED",x
 assert x["evidence"] and len(x["evidence"])>20,x
review={"version":"v2664","source":"v2663 manual contact sheet review of real QA image candidates",
        "qa_candidate_total":14,"reject_visual_content":len(reject),
        "hold_version_rights_evidence":len(hold),"retail_approved":0,
        "release_decision":"BLOCK_ALL_14_CANDIDATES",
        "reject_families":[x["family"] for x in reject],
        "hold_families":[x["family"] for x in hold],
        "requires_new_distinct_product_composition_not_blind_zoom":True,
        "historic_sha_verifications_pass_not_equivalent_to_visual_pass":True,
        "existing_55_public_urls_unchanged":True,"existing_11_approved_families_unchanged":True,
        "final_excel_shared":False}
out=Path("v2664-visual-sale-release-gate");out.mkdir(exist_ok=True)
(out/"gate.json").write_text(json.dumps(review,indent=2)+"\n")
print(json.dumps({"examined":14,"reject":len(reject),"hold":len(hold),"retail_approval":0}))
