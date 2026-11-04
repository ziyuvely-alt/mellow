#!/usr/bin/env python3
"""v2575. Close false positive source-code copy warnings for two v2559 cases.
Separate *rendered* fields (title, subtitle, footer, lines) from nonrendered
'caution' metadata. Preserve existing JPG candidates exactly, no OCR/synthesis.
"""
import ast,json,re
from pathlib import Path
SRC=Path("scripts/v2559_missha_goodal_two_composition_candidates.py")
OUT=Path("v2575-remaining-two-copy-verification");OUT.mkdir(exist_ok=True)
tree=ast.parse(SRC.read_text())
cases=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="cases" for t in node.targets):
        cases=ast.literal_eval(node.value)
assert len(cases)==2
BANNED=re.compile(r"\b(?:DRAFT|QA|RIGHTS|PENDING|STOCK EDITION|NOT APPROVED|HOLD)\b",re.I)
results=[]
for item in cases:
    assert item["family"] in ["pending-02","pending-19"]
    rendered=[item["title"],item["subtitle"],item["footer"]]
    rendered += [x for pair in item["lines"] for x in pair]
    problem=[x for x in rendered if BANNED.search(x)]
    metadata=item["caution"]
    assert not problem,(item["family"],problem)
    # Ensure the caution is defined in source metadata, but not sent into a draw.text() call.
    assert all("caution" not in ast.unparse(n.args[1]) for n in ast.walk(tree)
       if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="text" and len(n.args)>=2)
    results.append({"family":item["family"],"source_script":str(SRC),
       "rendered_literal_and_dynamic_values":rendered,
       "banned_customer_text_hits":problem,
       "metadata_only_caution":metadata,
       "dynamic_customer_copy_gate":"PASS_SOURCE_CODE_RENDERED_STRINGS",
       "actual_image_visual_QA_performed":False,
       "sale_release_approved":False})
report={"version":"v2575","prior_copy_scan_run":41760312065,
 "revisited_two_families":2,"source_only_false_positive_copy_holds_closed":2,
 "source_JPGs_regenerated":0,"old_156_images_unchanged":True,
 "original_55_public_URLs_unchanged":True,"xlsx_created_or_shared":False,
 "commercial_rights_confirmed":False,"physical_stock_edition_confirmed":False,
 "original_mk_logo_confirmed":False,"final_sales_approval":False,
 "verified_dynamic_cases":results}
(OUT/"dynamic-copy-source-release-gates.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"dynamic_candidate_copy_checked":2,"internal_text_hits":0,
"regenerated_JPGs":0,"sales_ready":False}))
