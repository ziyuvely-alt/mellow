#!/usr/bin/env python3
"""v2458 resume project after v2457b: assemble 38 independently checked newer JPGs
and 79 retained older JPGs without generating a single pixel.
Exclude two individually visually verified unsupported *claims* from useable-review pool:
- pending08 #4 says selling shades 01-20, while original option generation conflicts.
- pending19 #1 claims dual brightening/wrinkle care, official exact-edition function
  evidence not authenticated.
All 531 historical source bytes and 55 published URLs remain unchanged.
Everything remains a candidate subject to copyright, SKU generation and manual QA.
"""
from pathlib import Path
from PIL import Image
from collections import defaultdict
import hashlib,json,shutil,zipfile
A=Path("prior-v2455b")
B=Path("prior-v2457b")
OUT=Path("v2458-output");OUT.mkdir(exist_ok=True)
m=json.loads((A/"v2455b-current-38jpg-checkpoint.json").read_text())
n=json.loads((B/"v2457b-final-86frame-QA-disposition.json").read_text())
assert len(m["files"])==38 and n["retained_not_approved_JPG"]==79
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=[x for x in n["files"] if x["disposition"]=="RETAIN_AS_UNAPPROVED_CANDIDATE"]
assert len(old)==79
manual_claim_hold={
 ("pending-08",4):"Selling 01-20 claim conflicts with unresolved 26AD/official same-generation shade matching; do not claim complete official color range.",
 ("pending-19",1):"Brightening + wrinkle care dual-functional claim lacks exact-edition Korean regulatory/brand source; do not publish without official proof."
}
assets=[];known=set();hold=[];carry=[];duplicate=[]
for base,records,path_field,hash_field,origin in [
 (A,m["files"],"file","sha256","v2455b_verified_38"),
 (B,old,"new_copy_file","sha256","v2457b_older_79")]:
 for x in records:
  group=x["group_id"];slot=x.get("slot")
  p=base/x[path_field]
  assert p.is_file() and sha(p)==x[hash_field]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
  key=(group,x[hash_field])
  if key in known:
   duplicate.append({"group_id":group,"original_file":str(p),"sha256":x[hash_field]})
   continue
  known.add(key)
  claim=manual_claim_hold.get((group,slot)) if origin=="v2457b_older_79" else None
  category="02-manually-verified-unsupported-claims-HOLD" if claim else "01-actual-JPG-SKU-review-queue"
  target=OUT/category/group/(origin+"__"+p.name)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,target)
  assert sha(target)==x[hash_field]
  entry={"group_id":group,"source_slot":slot,"source_archive":origin,
  "stored_path":str(target.relative_to(OUT)),"sha256":x[hash_field],
  "status":"HOLD_UNSUPPORTED_PRODUCT_CLAIM" if claim else "CANDIDATE_FULL_QA_REQUIRED",
  "claim_hold_reason":claim,"exact_stock_edition_verified":False,
  "official_swatch_generation_verified":False,"photo_rights_confirmed":False,
  "full_manual_frame_qa_completed":False,"sales_approved":False}
  assets.append(entry)
  (hold if claim else carry).append(target)
assert len(assets)+len(duplicate)==117
assert len(hold)==2 and len(carry)+len(hold)==len(assets)
counts=defaultdict(int)
for x in assets:
 if x["status"]=="CANDIDATE_FULL_QA_REQUIRED":counts[x["group_id"]]+=1
rows=[{"group_id":f"pending-{i:02d}","candidate_original_JPGs_still_pending_full_QA":counts.get(f"pending-{i:02d}",0),
 "full_5_or_6_sales_JPG_set_APPROVED":False} for i in range(1,31)]
assert len(rows)==30
report={"version":"2.4.58",
 "source_newer_38":"production-assets-v2455b-38-JPGs-official-shade-evidence",
 "source_prior_79":"production-assets-v2457b-79-retained-seven-quarantine",
 "newer_38_verified_exact_bytes":38,"older_79_verified_exact_bytes":79,
 "total_nonduplicate_file_copies":len(assets),
 "duplicates_only_if_exact_group_and_SHA":len(duplicate),
 "unsupported_claims_independently_isolated":2,
 "remaining_full_QA_candidate_JPG_count":len(carry),
 "30_product_group_count":30,
 "product_families_with_at_least_5_source_candidates":sum(x["candidate_original_JPGs_still_pending_full_QA"]>=5 for x in rows),
 "product_families_with_no_source_candidates":[x["group_id"] for x in rows if x["candidate_original_JPGs_still_pending_full_QA"]==0],
 "previous_64_unverified_MK_logo_JPG_quarantine_preserved":True,
 "previous_7_redundant_cards_quarantine_preserved":True,
 "original_531_JPGs_overwritten":0,"previous_public_55_URLs_modified":0,
 "new_JPGs_rendered":0,"new_shade_swatch_images_generated":0,
 "commercial_rights_verified":0,"physical_stock_editions_approved":0,
 "FINAL_SALES_APPROVED_PRODUCT_FAMILIES":0,"spreadsheet_created_or_shared":False,
 "all_30_status":rows,"claims_hold":[x for x in assets if x["status"]=="HOLD_UNSUPPORTED_PRODUCT_CLAIM"],
 "exact_duplicate_info":duplicate,"assets":assets,
 "next":["Use current photo/official-source information to replace claim-held facts only after direct documentation",
 "Do not falsely publish or pad 5/6 frame sets with repeated facts",
 "Continue per-frame visual QA and authentic same-generation shade sourcing",
 "Keep all XLSX and spreadsheet artifacts withheld until entire project complete"]
}
(OUT/"v2458-30group-current-image-manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
for fname,items in [("v2458-current-unapproved-original-JPG-candidates.zip",carry),
("v2458-2-unsubstantiated-claim-JPGs-HOLD.zip",hold)]:
 with zipfile.ZipFile(OUT/fname,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in items:z.write(p,arcname=str(p.relative_to(OUT)))
  z.write(OUT/"v2458-30group-current-image-manifest.json",arcname="v2458-30group-current-image-manifest.json")
 with zipfile.ZipFile(OUT/fname) as z:
  assert z.testzip() is None and len(z.namelist())==len(items)+1
print(json.dumps({k:report[k] for k in ("version","total_nonduplicate_file_copies","remaining_full_QA_candidate_JPG_count","unsupported_claims_independently_isolated","product_families_with_at_least_5_source_candidates","new_JPGs_rendered","spreadsheet_created_or_shared")}),flush=True)
