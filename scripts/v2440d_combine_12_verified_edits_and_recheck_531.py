#!/usr/bin/env python3
"""v2440d consolidate only actual modified customer JPEGs from v2439/v2439b/v2440.
Verify all 531 original source JPEG hashes against the prior complete audit. No originals,
existing published JPGs or URLs are modified. Never claim full manual visual QA.
"""
from pathlib import Path
from PIL import Image
from collections import defaultdict
import csv,hashlib,json,shutil,zipfile
ROOT=Path("v2440d-output")
ROOT.mkdir(exist_ok=True)
BASE=Path("baseline-v2427b")
SOURCES=[("v2439-source","v2439_checkpoint.json","edits","edited_jpg","edited_sha256"),
         ("v2439b-source","v2439b_checkpoint.json","results","output","new_sha256"),
         ("v2440-source","v2440_checkpoint.json","edits","updated","updated_sha256")]
fams=defaultdict(list)
results=[]
for folder,check,field,pathkey,hashkey in SOURCES:
 origin=Path(folder)
 checkpoint=json.loads((origin/check).read_text())
 assert isinstance(checkpoint[field],list)
 for row in checkpoint[field]:
  rel=row[pathkey]; expected=row[hashkey]; p=origin/rel
  assert p.is_file(),p
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  assert actual==expected,(rel,actual,expected)
  with Image.open(p) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
  group=row.get("group_id") or row.get("group")
  assert group and group.startswith("pending-")
  target=ROOT/"new-customer-JPG-drafts"/group/(folder+"__"+p.name)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,target)
  assert hashlib.sha256(target.read_bytes()).hexdigest()==expected
  entry={"group_id":group,"source_batch":folder,"immutable_sha256":actual,
         "path":str(target.relative_to(ROOT)),"size":target.stat().st_size,
         "state":"SALES_IMAGE_DRAFT","visual_design_checked":True,
         "commercial_reuse_permission":"NOT_VERIFIED","product_stock_package":"NOT_VERIFIED",
         "official_shade_match":"NOT_CONFIRMED_WHERE_REQUIRED"}
  results.append(entry);fams[group].append(entry["path"])
assert len(results)==12,(len(results),results)
assert len(fams)==11,len(fams)
index=list(csv.DictReader((Path("v2439-source")/"source_SHA256_index.csv").open(encoding="utf-8")))
assert len(index)==531,len(index)
for line in index:
 source=BASE/line["relative_path"]
 assert source.is_file(),source
 assert hashlib.sha256(source.read_bytes()).hexdigest()==line["SHA256"],source
# The 15 off-size historical assets are raw source photos/contact sheets, not active sales drafts.
inv=json.loads((Path("v2439-source")/"source_inventory_30groups.json").read_text())
assert len(inv)==30
invalid_source=[{"group_id":g["group_id"],"source":x["source"],"dimensions":x["dimensions"]}
                for g in inv for x in g["source_frames"] if not x["meets_1080_under_2mb"]]
assert len(invalid_source)==15,len(invalid_source)
family_status=[]
for f in inv:
 name=f["group_id"]
 family_status.append({
  "group_id":name,"historical_JPG_count":f["source_frame_count"],
  "fresh_edited_frames":len(fams[name]),
  "fresh_edited_paths":fams[name],
  "5_or_6_frame_manual_complete_visual_QA":False,
  "group_final_sale_approval":False,
  "source_rights_hold":True,
  "stock_package_check_hold":True,
  "exact_generation_shade_chart_hold":name in {"pending-01","pending-02","pending-04","pending-05","pending-06","pending-07","pending-08","pending-10"},
 })
report={
"version":"2.4.40d",
"baseline":"production-assets-v2438c-consolidated-checkpoint",
"source_batches":["production-assets-v2439-four-edits-30group-audit",
                  "production-assets-v2439b-five-real-card-fixes",
                  "production-assets-v2440-three-card-repairs"],
"run_ids":[41653189335,41653531478,41654177516],
"artifact_ids":[13237522920,13238042991,13237799199],
"customer_jpg_latest_edits_copied_exactly":len(results),"distinct_groups_with_edits":len(fams),
"all_30_groups_historical_JPG_inventory":"included",
"original_JPG_count_SHA256_reverified":len(index),
"historical_source_or_QA_images_not_1080x1080":len(invalid_source),
"historical_source_nonspec_images_not_sales_assets":True,
"altered_historical_JPG":0,"modified_existing_public_image_paths":0,
"published_URLs_retested_over_HTTP":False,"official_shade_charts_new":0,
"FINAL_QA_APPROVED_new":0,"all_30_groups_full_visual_QA_complete":False,
"original_MK_logo_binary_recovered":False,
"stock_package_verified":0,"commercial_photo_reuse_rights_verified":0,
"latest_real_customer_JPG_drafts":results,
"historical_nonspec_source_files":invalid_source,
"families":family_status,
"remaining_priority":[
 "pending-01 Cover Lasting: exclude No.21 and verify official 23/25/27 same generation shade source",
 "pending-08 Peripera: 01..20 generation exact 04/06/07 and 12 naming, do not mix 26AD",
 "pending-10 OBgE Cushion: officially authorized real transparent photo + current 1 Ivory/2 Beige/3 Sand package",
 "pending-21 goodal eye-care exact physical product identity, source ingredients",
 "Additional active 5/6 image frames manual per-frame QA beyond partial reviewed subset",
 "Reacquire original MK logo PNG bytes; verify each commercial photo's usage permission and stock packaging",
 "Do not upload drafts to Shopee or change prior 55 URLs until approvals complete"
 ],
"notice":"GitHub branches are not access-private if repository public; no external messages or Shopee publishing occurred"
}
(ROOT/"v2440d-resumable-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ROOT/"v2440d-12-actual-modified-JPGs.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for item in results:
  p=ROOT/item["path"];z.write(p,arcname=item["path"])
 z.write(ROOT/"v2440d-resumable-checkpoint.json",arcname="v2440d-resumable-checkpoint.json")
with zipfile.ZipFile(ROOT/"v2440d-12-actual-modified-JPGs.zip") as z:
 assert z.testzip() is None and len(z.namelist())==13
print(json.dumps({k:report[k] for k in ("version","customer_jpg_latest_edits_copied_exactly","distinct_groups_with_edits","original_JPG_count_SHA256_reverified","historical_source_or_QA_images_not_1080x1080","altered_historical_JPG","modified_existing_public_image_paths")}))
