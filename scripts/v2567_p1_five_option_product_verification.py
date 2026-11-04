#!/usr/bin/env python3
"""v2567 P1 inventory-option image gating. Validates exact shades against existing
stock ledger for five more image families. No artificial shade proof: image
content itself requires physical inventory and rights signoff.
"""
from pathlib import Path
import json,hashlib,re
INV=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
G=json.loads(Path("v2567-gates/release-gates.json").read_text())
ROOT=Path("v2567-original/review-JPG-by-family")
OUT=Path("v2567-p1-five-family-option-validation");OUT.mkdir(exist_ok=True)
stock={x["family_id"]:x for x in INV["pending_families"]}
gates={x["family"]:x for x in G["products"]}
# Correct exact-SKU order may differ; sets must agree, no names inferred from shade colors.
EXPECTED={
"pending-03":{"shades":["21","23","25"],"type":"MISSHA M Perfect Cover BB Cream old-stock Korean package, NOT PRO","volume":"Confirm stock label and edition"},
"pending-04":{"shades":["21N","21C","23N"],"type":"CLIO Mesh Glow Essential Mini 5g, NOT 15g set","volume":"5g mini"},
"pending-05":{"shades":["19N","19C","21N","21C","23N"],"type":"CLIO Founwear Cushion promotional set, NOT Mesh Glow/Mesh Blur","volume":"Verify current actual kit/refill"},
"pending-06":{"shades":["19N","19C","21N","21C","23N"],"type":"CLIO Mesh Glow Essential set, NOT mini/Founwear/Mesh Blur","volume":"Verify 15g set plus refill and optional gifts separately"},
"pending-07":{"shades":["19C","19N","21N"],"type":"CLIO Mesh Blur 15g x2, NOT Mesh Glow","volume":"15g x2"}
}
assert len(EXPECTED)==5
lines=[]
for fid,rule in EXPECTED.items():
 d=stock[fid];assert fid in gates
 actual=[]
 for option in d["option_values"]:
  m=re.match(r"^([0-9]{2}[A-Z]?)",option)
  assert m,(fid,option)
  actual.append(m.group(1))
 assert sorted(actual)==sorted(rule["shades"]),(fid,actual,rule["shades"])
 assert len(actual)==len(set(actual))==(3 if fid in ("pending-03","pending-04","pending-07") else 5)
 stored=list((ROOT/fid).glob("*.jpg"))
 assert len(stored)==(5 if fid=="pending-03" else 6)
 original_hash=[hashlib.sha256(f.read_bytes()).hexdigest() for f in stored]
 assert len(original_hash)==len(set(original_hash))
 lines.append({"family":fid,"product":d["family_name"],"expected":rule["shades"],
 "actual":actual,"identity_guard":rule["type"],"volume_guard":rule["volume"],
 "total_picture_candidates":len(stored),"unique_file_sha_verified":True,
 "photo_SHA256":original_hash,
 "shade_chart_source_evidence_verified_for_stock":False,
 "existing_photo_license_verified":False,
 "approved_for_sales":False,
 "disposition":"PASS_STOCK_OPTION_SET_BUT_HOLD_PHYSICAL_COLOR_CHART_RIGHTS_GENERATION"})
assert sum(r["total_picture_candidates"] for r in lines)==29
report={"version":"v2567","p1_families_checked":5,"jpg_hashes_checked":29,
 "exact_option_sets_matched":5,"missing_shade_counts":0,"unexpected_shade_counts":0,
 "rights_verified":False,"exact_edition_match_to_actual_stock_verified":False,
 "manual_color_chart_verification":False,"sales_approved":0,
 "previous_P0_gate_preserved":True,"previous_55_public_urls_modified":0,
 "new_public_urls":0,"old_JPG_files_modified":0,"xlsx_created_or_shared":False,
 "entries":lines}
(OUT/"P1-option-image-guards.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"P1_families":5,"images":29,"option_sets_pass":5,"approved":0,"xls_shared":False}))
