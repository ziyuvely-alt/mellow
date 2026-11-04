#!/usr/bin/env python3
"""v2570 evidence-backed PERIPERA option-name preflight. 20 inventory choices,
no swatch fabrication, no spreadsheet edits, no customer JPG/publishing.
"""
import json,re
from pathlib import Path
IN=Path("evidence/inventory-30-family-crosswalk-20261104.json")
E=Path("evidence/v2569-peripera-004-006-007-014-naming-verified-20261104.json")
OUT=Path("v2570-peripera-option-preflight");OUT.mkdir(exist_ok=True)
stock=json.loads(IN.read_text())
fact=json.loads(E.read_text())
family=next(x for x in stock["pending_families"] if x["family_id"]=="pending-08")
raw=family["option_values"]
expected=[f"{i:03d}" for i in range(1,21)]
assert len(raw)==20
by_num={}
for option in raw:
    m=re.match(r"^(\d{3})\s+(.+)$",option)
    assert m,option
    number,name=m.groups()
    assert number not in by_num,number
    by_num[number]=name
assert list(by_num)==expected,list(by_num)
verified={x["shade"]:x for x in fact["verified_retailer_results"]}
assert set(verified)=={"004","006","007","014"}
assert by_num["004"]=="저쩔복숭아"
assert by_num["006"]=="갓기천사"
assert by_num["007"]=="자두뿜뿜"
assert by_num["014"]=="로지워시" and verified["014"]["retailer"]=="로지위시"
resolved={}
for code in expected:
    canonical=verified.get(code,{}).get("retailer",by_num[code])
    resolved[code]={"inventory_source_name":by_num[code],
        "candidate_customer_label":canonical,
        "source_name_corrected":canonical!=by_num[code],
        "verification_status":"RETAIL_REFERENCE_MATCH" if code in verified else "STOCK_INVENTORY_ONLY_NOT_INDEPENDENTLY_VERIFIED"}
assert sum(x["source_name_corrected"] for x in resolved.values())==1
assert all(int(k)<=20 for k in resolved)
report={"version":"v2570","sku_family":"pending-08","option_codes":expected,
"options_total":20,"source_inventory_preserved":True,
"future_candidate_014_label":"014 로지위시",
"changed_in_output_reference_only":["014"],
"004_006_007_independently_named_from_retailer":True,
"corrected_and_noninvented_labels":resolved,
"legacy_26AD_edition_policy_conflict":"UNRESOLVED_REQUIRE_STOCK_PHOTO",
"official_20_color_swatch_license_confirmed":False,
"commercial_release_approved":False,"source_photo_and_MK_rights_verified":False,
"old_images_changed":0,"original_55_urls_changed":0,
"xlsx_created_or_shared":False,
"release_gate":"HOLD_NO_REAL_OFFICIAL_OPTION_SHADE_IMAGE"}
(OUT/"canonical-option-reference.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"options":20,"typos_corrected_in_REFERENCE_ONLY":1,
 "validated_retailer_names":4,"inventory_file_changed":0,
 "eligible_commercial_shade_charts":0,"xlsx_shared":False}))
