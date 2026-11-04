#!/usr/bin/env python3
"""v2591 checkpoint: reuse prior v2586 thirteen deltas, v2588 three new
MISSHA/DrG JPGs and v2590 one new Goodal factual card. Save only a new JPG and
17-delta provenance manifest. No 156-JPG recheck, public deployment or XLSX.
"""
import json,hashlib
from pathlib import Path
P=Path("v2591-prev")
F=Path("v2591-facts")
O=Path("v2591-seventeen-change-incremental-checkpoint");O.mkdir(exist_ok=True)
m=json.loads((P/"manifest.json").read_text())
f=json.loads((F/"manifest.json").read_text())
assert m["version"]=="v2588" and m["virtual_total_QA_deltas"]==16
assert m["existing_thirteen_preserved"] and len(m["new_changes"])==3
assert f["version"]=="v2590" and f["status"]=="NEW_DISTINCT_FACTS_CARD_QA_ONLY"
assert not f["similarity_holds"]
assert f["family"]=="pending-20"
src=F/f["file"]
assert src.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src)==f["candidate_sha256"]
assert src.stat().st_size<2_000_000
new_key=("pending-20",5)
assert new_key not in {(x["family"],x["slot"]) for x in m["new_changes"]}
dst=O/"pending-20-slot05-100ml-facts-QA.jpg"
dst.write_bytes(src.read_bytes())
assert sha(dst)==sha(src)
r={"version":"v2591","previous_checkpoint_run":41763838259,
 "new_info_card_run":41764148539,"previous_16_QA_deltas_provenance_preserved":True,
 "previous_13_delta_checkpoint_run":41763244120,
 "prior_MISSHA_DrG_changes":m["new_changes"],
 "new_fact_card":{"family":"pending-20","slot":5,"file":dst.name,
  "old_sha256":f["previous_slot05_sha256"],"new_sha256":sha(dst),
  "source":"Verified 100ml source inventory + 25AD label remains unconfirmed",
  "content_status":"QA_ONLY"},
 "all_QA_delta_count":17,"latest_JPGs_newly_copied":1,
 "remaining_original_JPG_slots_unmodified_in_overlay":139,
 "commercial_rights_verified":False,"exact_owned_stock_packaging_verified":False,
 "original_round_MK_logo_verified":False,"human_visual_final_approval":False,
 "newly_published_urls":0,"previous_55_public_URLs_modified":0,
 "XLSX_created_or_shared":False,
 "next_work":"Address actual photo rights, verified own stock package, authentic MK logo; no automatic seller release."}
(O/"manifest.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"previous_deltas_preserved":16,"new_fact_image":1,
"total_QA_deltas":17,"public_url_changes":0,"spreadsheet_shared":False}))
