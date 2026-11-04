#!/usr/bin/env python3
"""v2573 static customer-facing image-copy QA for 8 staged candidate JPEGs.
Inspects the exact text-rendering source expressions rather than guessing via OCR.
No regeneration, source mutation, public publication, or spreadsheets.
"""
from pathlib import Path
import ast,json,re
O=Path("v2573-copy-release-gates");O.mkdir(exist_ok=True)
SOURCES=[
("pending-21",5,"scripts/v2552_goodal_21_slot05_real_photo_candidate.py"),
("pending-16",4,"scripts/v2555_drg_old_package_slot04_candidate.py"),
("pending-15",5,"scripts/v2556_drg_green_mild_photo_application.py"),
("pending-26",5,"scripts/v2557_pixelpure_official_145_only.py"),
("pending-02",4,"scripts/v2559_missha_goodal_two_composition_candidates.py"),
("pending-19",5,"scripts/v2559_missha_goodal_two_composition_candidates.py"),
("pending-01",5,"scripts/v2562_two_frame05_candidate_layout.py"),
("pending-06",5,"scripts/v2562_two_frame05_candidate_layout.py")
]
DENY_RE=re.compile(r"\b(?:DRAFT|QA|RIGHTS|PENDING|STOCK EDITION|NOT APPROVED)\b",re.I)
RISK_RE=re.compile(r"(?:original (?:packaging|jar|product|brand|photograph|photo)|old package|stock version)",re.I)
rows=[]
for fam,slot,path in SOURCES:
    source=Path(path)
    content=source.read_text()
    tree=ast.parse(content)
    printed=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute) or node.func.attr!="text":
            continue
        # ImageDraw.text(position, text, ...) is materially different from logging/metadata.
        if len(node.args)<2:continue
        arg=node.args[1]
        strings=[]
        if isinstance(arg,ast.Constant) and isinstance(arg.value,str):
            strings=[arg.value]
        elif isinstance(arg,ast.JoinedStr):
            strings=[str(part.value) for part in arg.values if isinstance(part,ast.Constant)]
        for value in strings:
            printed.append({"line":node.lineno,"text":value,
                "blocker":"INTERNAL_QA_TEXT_IN_IMAGE" if DENY_RE.search(value) else
                    ("CUSTOMER_COPY_PHOTO_PROVENANCE_NOTE_REVIEW" if RISK_RE.search(value) else None)})
    # dynamic labels are known per family in scripts; do not claim static inspection detects all.
    if fam in ("pending-02","pending-19"):
        printed.append({"line":None,"text":"Dynamic case footer and step labels",
           "blocker":"DYNAMIC_RENDER_TEXT_REQUIRES_MANUAL_CONFIRMATION"})
    if fam in ("pending-01","pending-06"):
        assert any(x["blocker"]=="INTERNAL_QA_TEXT_IN_IMAGE" for x in printed)
    if fam=="pending-26":
        assert any(x["blocker"]=="INTERNAL_QA_TEXT_IN_IMAGE" for x in printed)
    blockers=[x for x in printed if x["blocker"]]
    rows.append({"family":fam,"slot":slot,"source_recipe":path,"literal_render_strings_inspected":len(printed),
        "customer_copy_flags":blockers,
        "content_copy_approved":not blockers,
        "visual_actual_JPEG_manual_QA_complete":False,
        "safe_for_public_release":False})
assert len(rows)==8
flagged=[r for r in rows if r["customer_copy_flags"]]
report={"version":"v2573","checked_staged_candidates":8,
"source_recipes_examined":6,"possible_customer_copy_issues":len(flagged),
"certain_internal_QA_text_in_frames":sum(any(x["blocker"]=="INTERNAL_QA_TEXT_IN_IMAGE" for x in r["customer_copy_flags"]) for r in rows),
"flagged_by_family_slot":[{"family":r["family"],"slot":r["slot"],"flags":r["customer_copy_flags"]} for r in flagged],
"source_JPG_bytes_changed":0,"released_images":0,"previous_public_55_URLs_changed":0,
"xlsx_created_or_shared":False,
"next_action":"Recreate ONLY flagged candidates from documented genuine product-photo source after replacing internal-copy with customer-safe factual text; do not change published originals, do not assert photo rights or stock match.",
"limitations":"Static render-call string inspection does not read embedded text on product photographs or strings derived from expressions."}
(O/"customer-copy-render-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"candidates":8,"flagged":len(flagged),"certain_internal_QA_frame_count":report["certain_internal_QA_text_in_frames"],
"flagged_families":[r["family"] for r in flagged],"source_edits":0,"xlsx":False},ensure_ascii=False))
