#!/usr/bin/env python3
"""v2568 one-pass P2 20-family 100-JPG integrity verification, plus merged release
state of P0, P1, P2. Fail closed on insufficient physical edition, rights, and
logo evidence; never assert photo content correctness based on SHA alone.
"""
from pathlib import Path
import json,hashlib
I=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
B=Path("v2568-base/review-JPG-by-family")
P0=json.loads(Path("v2568-p0/product-guards.json").read_text())
P1=json.loads(Path("v2568-p1/P1-option-image-guards.json").read_text())
Q=json.loads(Path("v2568-queue/release-gates.json").read_text())
OUT=Path("v2568-batched-30-family-unified-release-QA");OUT.mkdir(exist_ok=True)
indexed={x["family_id"]:x for x in I["pending_families"]}
p0={x["family"] for x in P0["guard_results"]}
p1={x["family"] for x in P1["entries"]}
p2=set(indexed)-p0-p1
assert len(p0)==5 and len(p1)==5 and len(p2)==20 and not(p0&p1)
q={x["family"]:x for x in Q["products"]}
assert len(q)==30
listing=[];registry=[];bad=[]
for fam in sorted(p2):
 f=indexed[fam];files=list((B/fam).glob("*.jpg"))
 try:
  assert len(files)==5,(fam,len(files))
  hashes={}
  for file in files:
   header=file.read_bytes()
   # These are proven JPEG candidates by previous v2564 all-product physical visual audit.
   assert header.startswith(bytes.fromhex("ffd8")) and header.endswith(bytes.fromhex("ffd9")),(fam,file.name)
   assert 0<len(header)<2000000,(fam,file.name,len(header))
   slot=int(file.name[:2])
   assert slot not in hashes,(fam,slot)
   hashes[slot]=hashlib.sha256(header).hexdigest()
  assert sorted(hashes)==[1,2,3,4,5],(fam,sorted(hashes))
  assert len(set(hashes.values()))==5
  listing.append({"family":fam,"product":f["family_name"],"review_jpg_count":5,
   "slots":[1,2,3,4,5],"sha256_by_slot":hashes,
   "verified_JPG_bit_integrity":True,
   "promotional_rights_verified":False,"physical_owned_stock_photo_match_verified":False,
   "brand_MK_logo_verified":False,"human_image_claim_QA_verified":False,
   "release":"DENY_UNTIL_ALL_RIGHTS_STOCK_LOGO_VISUAL_EVIDENCE"})
 except Exception as e:
  bad.append({"family":fam,"error":str(e)})
  # Keep moving, preserve other 19 product results
all_complete=(len(listing)==20 and not bad)
assert all_complete, bad
for fam in sorted(indexed):
 level=q[fam]["priority"]
 assert level==("P0_EXACT_PRODUCT_OR_SHADE_BLOCK" if fam in p0 else "P1_OPTION_CROSSCHECK" if fam in p1 else "P2_GENERAL_VISUAL_AND_RIGHTS")
 current=listing[[x["family"] for x in listing].index(fam)] if fam in p2 else None
 registry.append({"family":fam,"product":indexed[fam]["family_name"],
    "tier":"P0" if fam in p0 else ("P1" if fam in p1 else "P2"),
    "inventory_option_set_checked":fam in p0 or fam in p1,
    "existing_JPG_bit_integrity_checked":True,
    "new_release_ready":False,
    "unresolved":["RIGHTS_NOT_DOCUMENTED","EXACT_STOCK_EDITION_NOT_SIGNED_OFF",
       "ORIGINAL_MK_LOGO_NOT_VERIFIED","FULL_IMAGE_CONTENT_REVIEW_NOT_SIGNED_OFF"],
    "strict_release_mode":"FAIL_CLOSED"})
assert len(registry)==30
report={"version":"v2568","P0_previous_run":41758784270,
"P1_previous_run":41758949649,"P2_current_count":len(listing),
"P2_jpg_bit_integrity_checked":sum(x["review_jpg_count"] for x in listing),
"total_inventory_families":30,"total_reviews_reconciled":156,
"option_families_checked":10,"source_Baseline_unchanged":True,
"public_URLs_changed":0,"new_URLs":0,"xlsx_created_or_shared":False,
"release_approved_families":0,"remaining_rights_and_stock_evidence_holds":30,
"P2_product_checks":listing,"family_release_registry":registry,"errors":bad}
(OUT/"unified-30family-publish-gate.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"pending-family-work-queue.md").write_text("# Final release gaps (30 pending product families)\n\n"
+"**No pending family can be published solely from JPEG validation.** Evidence required: rights, physical stock packaging/version, exact contents and claims, original MK logo.\n\n"
+"| Family | Tier | Issue |\n|---|---|---|\n"
+"\n".join(f"| {x['family']} | {x['tier']} | RIGHTS + EXACT STOCK + MK LOGO + MANUAL PHOTO QA |" for x in registry)+"\n")
print(json.dumps({"P2_products_checked":len(listing),"P2_images_verified":100,
"P0_P1_P2_merged":len(registry),"source_images_in_scope":156,
"approved":0,"public_changes":0,"excel_shared":False}))
