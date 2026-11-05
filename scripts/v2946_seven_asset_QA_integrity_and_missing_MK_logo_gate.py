#!/usr/bin/env python3
"""v2946 QA seal, evidence-based missing logo asset hold, no asset mutation.
This is a checkpoint for new 4 x 5-frame internal ZIPs and 3 new 1080 QA cards.
"""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from PIL import Image
import json,time
Q=Path("qa-review")
V44=Q/"v2944-four-5frame-product-first-internal-only-QA-ZIPs"
V45=Q/"v2945-missha-official-15ml-and-clio-edition-distinction-info-QA"
OUT=Q/"v2946-seven-new-QA-assets-original-logo-source-hold-checkpoint"
assert not OUT.exists()
m44=json.loads((V44/"manifest.json").read_text(encoding="utf-8"))
m45=json.loads((V45/"manifest.json").read_text(encoding="utf-8"))
s=json.loads((V45/"stock30-incremental-state-v2945.json").read_text(encoding="utf-8"))
assert s["version"]==m45["version"]=="v2945" and m44["version"]=="v2944"
assert len(s["families"])==30 and m44["new_internal_product_ZIPs_created"]==4 and m45["new_1080_information_review_images"]==3
data=[]
for item in m44["results"]:
 zfile=Path(item["internal_zip"])
 assert sha256(zfile.read_bytes()).hexdigest()==item["internal_zip_sha256"]
 with ZipFile(zfile) as z:
  assert z.testzip() is None and len(z.namelist())==5
  sigs=[]
  for p in z.namelist():
   b=z.read(p);sigs.append(sha256(b).hexdigest())
   with Image.open(BytesIO(b)) as im:
    im.load()
    assert im.format=="JPEG" and im.size==(1080,1080) and len(b)<2_000_000
  assert sigs==item["sha256_of_each_frame"]
 data.append({"product":item["family"],"asset_type":"FOUR_SOURCE_PLUS_ONE_ENG_INFO_INTERNAL_ZIP",
  "path":str(zfile),"sha256":item["internal_zip_sha256"],"frames_verified":5,"ZIP_CRC":"PASS","photo_rights_verified":False})
for item in m45["results"]:
 path=Path(item["image"])
 assert sha256(path.read_bytes()).hexdigest()==item["sha256"]
 with Image.open(path) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and path.stat().st_size<2_000_000
 data.append({"product":item["family"],"edition":item["edition"],
  "asset_type":"UNIT_CORRECTED_OR_PACK_EDITION_INTERNAL_QA_IMAGE",
  "path":str(path),"sha256":item["sha256"],"dimensions":[1080,1080],"photo_rights_verified":False})
assert len(data)==7
# The purported original brand asset must never be substituted with an invented logo.
# Missing path was independently tested in main, active QA, and three legacy production branches.
MK="references/mellowkr-brand/mellowkr-mk-original.png"
assert not Path(MK).exists(), "If the original logo is later provided, rerun a different approval-gated workflow"
for fam in ("pending-25","pending-27","pending-29","pending-30","pending-06","pending-12"):
 s["families"][fam]["v2946_logo_source_status"]="NO_VERIFIED_MK_ORIGINAL_FILE_IN_CURRENT_QA_TREE"
 s["families"][fam]["v2946_logo_action"]="NO_INVENTED_LOGO; HOLD UNTIL OWNER ORIGINAL IS MATERIALIZED"
 s["families"][fam]["sale_approved"]=False
report={"version":"v2946","baseline":"v2945","date_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "new_internal_ZIPs_integrity_checked":4,"new_QA_card_images_integrity_checked":3,
 "new_independent_photographs_created":0,"unresolved_distinct_source_photo_slots":4,
 "logo_expected_source_path":MK,
 "logo_source_checked_refs":["main","qa-assets/v2662-immutable-14-candidates",
 "production-assets-v2416d-visual-qa","production-assets-v2420-en-master","production-assets-v249"],
 "logo_verified_source_at_expected_path":False,
 "logo_policy":"NO_FABRICATION_OR_REPLACEMENT; NEVER_RENDER_UNVERIFIED_MK",
 "current_retail_release_gate":"HOLD_MK_STOCK_EDITION_COMMERCIAL_PHOTO_RIGHTS",
 "prior_completed_product_families_preserved":11,"prior_public_verified_URLs_preserved":55,
 "new_sale_approvals":0,"final_spreadsheet_shared":False,
 "newly_verified_assets":data}
OUT.mkdir(parents=True)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s.update({"version":"v2946","baseline":"v2945","new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False})
(OUT/"stock30-incremental-state-v2946.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2946","internal_qa_ZIPs":4,"new_QA_images":3,
  "missing_logo_asset_recorded":True,"source_photo_shortfall":4,"retail_approvals":0},ensure_ascii=False))
