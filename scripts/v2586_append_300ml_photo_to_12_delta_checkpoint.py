#!/usr/bin/env python3
"""v2586 append-only QA delta checkpoint for authentic OBgE 300ml source.
Reuses v2584 twelve established delta records without re-running 156 originals.
No public assets, no spreadsheet, no sales approval.
"""
import json,hashlib
from pathlib import Path
OLD=Path("v2586-prior")
NEW=Path("v2586-new")
OUT=Path("v2586-thirteen-incremental-photo-checkpoint")
OUT.mkdir(exist_ok=True)
old=json.loads((OLD/"manifest.json").read_text())
add=json.loads((NEW/"manifest.json").read_text())
assert old["version"]=="v2584" and old["total_approved_for_QA_overlay"]==12
assert len(old["previous_eleven"])==11
assert add["version"]=="v2585" and add["status"]=="DISTINCT_PRODUCT_PHOTO_QA_ONLY"
assert not add["similarity_alerts"] and not add["photo_commercial_reuse_rights_confirmed"]
source=NEW/add["file"]
assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()==add["candidate_sha256"]
assert source.stat().st_size<2_000_000
ids={(x["family"],x["slot"]) for x in old["previous_eleven"]}
ids.add((old["new_delta"]["family"],old["new_delta"]["slot"]))
assert len(ids)==12
family="pending-22"
slot=4
assert (family,slot) not in ids
target=OUT/"pending-22-slot04-authentic-300ml-official-photo-QA.jpg"
target.write_bytes(source.read_bytes())
assert hashlib.sha256(target.read_bytes()).hexdigest()==add["candidate_sha256"]
new={"family":family,"slot":slot,"qa_file":target.name,
 "sha256":add["candidate_sha256"],"source_photo_run":41763143287,
 "status":"QA_HOLD_EXACT_STOCK_RIGHTS_ORIGINAL_MK_LOGO"}
m={"version":"v2586","previous_checkpoint_run":41762993639,
 "previous_twelve_deltas_reused_without_regenerating":12,
 "newly_included_exact_official_OBGE300ml_photo":1,
 "delta_count":13,"remaining_base_slots_unchanged_in_virtual_overlay":143,
 "previous_55_public_URLs_modified":0,"new_public_URLs":0,
 "xlsx_created_or_shared":False,
 "product_photo_original_licensed":False,"physical_stock_package_verified":False,
 "original_mellowkr_logo_verified":False,"sales_ready":False,
 "previous_eleven":old["previous_eleven"],"twelfth":old["new_delta"],"thirteenth":new}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"reused_unchanged_deltas":12,"new_obge_official_photo":1,
 "checkpoint_total_deltas":13,"public_url_changes":0,"xlsx_shared":False}))
