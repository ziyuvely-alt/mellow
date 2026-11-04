#!/usr/bin/env python3
"""v2660 safety gate for product-identity and edition claims in future retail
image release manifests. Prevent publish approval without positive stock proof.
No photos generated, altered or published.
"""
import json
from pathlib import Path
E=Path("evidence")
a=json.loads((E/"v2658-three-official-product-claims-and-release-gates-20261104.json").read_text())
b=json.loads((E/"v2659-clio-three-kit-and-peripera-shade-004-conflict-20261104.json").read_text())
assert a["version"]=="v2658" and b["version"]=="v2659"
LOCKS={
 "pending-05":{"forbidden_tokens":["extra puffs","free puffs","shopping bag"],"required_stock_proof":True},
 "pending-06":{"forbidden_tokens":["free puffs","extra refill","mini cushion"],"required_stock_proof":True},
 "pending-07":{"forbidden_tokens":[],"required_stock_proof":True},
 "pending-08":{"forbidden_tokens":["004 저쩔복숭아","004 갓기천사"],"required_stock_proof":True,"required_exact_edition":True},
 "pending-12":{"forbidden_tokens":["15g","15 g"],"required_stock_proof":True,"official_size":"15 ml"},
 "pending-26":{"forbidden_tokens":["150ml","150 ml"],"required_stock_proof":True,"official_size":"145 ml"}
}
def check(record):
    fam=record["family"]
    claims=(record.get("product_name","")+" "+record.get("copy","")+" "+record.get("capacity","")+" "+record.get("kit","")).casefold()
    lock=LOCKS.get(fam)
    issues=[]
    if not lock:return ["NO_VERIFIED_RULE_FOR_FAMILY_MANUAL_REVIEW"]
    if not record.get("owned_stock_package_verified"):issues.append("OWNED_STOCK_VERSION_UNVERIFIED")
    if not record.get("source_photo_commercial_rights_verified"):issues.append("SOURCE_PHOTO_RIGHTS_UNVERIFIED")
    if not record.get("original_MK_logo_available"):issues.append("GENUINE_MK_LOGO_NOT_VERIFIED")
    if not record.get("human_visual_QA_approved"):issues.append("HUMAN_VISUAL_QA_PENDING")
    if not record.get("latest_v2647_exact_photo_compared"):issues.append("LATEST_V2647_NOT_COMPARED")
    for w in lock["forbidden_tokens"]:
        if w.casefold() in claims:issues.append("UNSAFE_OR_UNVERIFIED_COPY:"+w)
    if lock.get("required_exact_edition") and not record.get("exact_edition_shade_chart_verified"):
        issues.append("OFFICIAL_SHADE_CHART_GENERATION_UNVERIFIED")
    return issues
def sample(fam,copy="",**kwargs):
    d={"family":fam,"copy":copy,"owned_stock_package_verified":False,
       "source_photo_commercial_rights_verified":False,
       "original_MK_logo_available":False,"human_visual_QA_approved":False,
       "latest_v2647_exact_photo_compared":False}
    d.update(kwargs);return d
# Important dangerous cases must remain blocked, independent of mistaken manual toggles.
tests=[
 (sample("pending-26","150ml cleanser"),"UNSAFE_OR_UNVERIFIED_COPY:150ml"),
 (sample("pending-12","15g peel shot"),"UNSAFE_OR_UNVERIFIED_COPY:15g"),
 (sample("pending-05","Free puffs included"),"UNSAFE_OR_UNVERIFIED_COPY:free puffs"),
 (sample("pending-06","mini cushion included"),"UNSAFE_OR_UNVERIFIED_COPY:mini cushion"),
 (sample("pending-08","004 갓기천사"),"UNSAFE_OR_UNVERIFIED_COPY:004 갓기천사"),
 (sample("pending-08","001-020"),"OFFICIAL_SHADE_CHART_GENERATION_UNVERIFIED"),
]
for candidate,expected in tests:
    reasons=check(candidate)
    assert expected in reasons,(candidate,reasons)
default_samples=[sample(fam,copy={"pending-12":"15 ml","pending-26":"145 ml"}.get(fam,"")) for fam in LOCKS]
report={"version":"v2660","cases_tested":len(tests),"all_tests_pass":True,
 "release_locks":{f:check(c) for f,c in zip(LOCKS,default_samples)},
 "automatic_new_retail_approvals":0,
 "not_verified_is_not_approved":True,
 "protected_public_55_urls_modified":False,
 "approved_11_family_images_modified":False,
 "xlsx_not_shared":True}
out=Path("v2660-release-copy-guard");out.mkdir(exist_ok=True)
(out/"release-gates.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"tests":len(tests),"passed":len(tests),"release_approved":0,
 "family_gates":len(LOCKS)},ensure_ascii=False))
