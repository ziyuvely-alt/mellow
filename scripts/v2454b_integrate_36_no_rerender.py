#!/usr/bin/env python3
"""v2454b preserve 34 prior real photo candidates + 2 new OBgE 300mL fact cards.
All previous JPGs copied byte-identically, no rerender or workbook exposure.
No 5/6-frame family final release; OBgE proper pump product photo missing.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
A=Path("prior-v2453b")
B=Path("prior-v2454")
OUT=Path("v2454b-output");OUT.mkdir(exist_ok=True)
p=json.loads((A/"v2453b_34-JPG-resumable-checkpoint.json").read_text())
q=json.loads((B/"v2454_fact_cards_checkpoint.json").read_text())
assert len(p["candidate_images"])==34 and len(q["files"])==2
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
allrows=[]
for src,rs,k,h,category in [
 (A,p["candidate_images"],"file","sha256","reused-photo-review-candidates"),
 (B,q["files"],"file","sha256","factual-info-only-no-product-photo")]:
 for item in rs:
  gid=item.get("group_id","pending-22")
  f=src/item[k]
  assert f.is_file() and sha(f)==item[h]
  with Image.open(f) as im:
   im.load(); assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2_000_000
  out=OUT/category/gid/f.name
  out.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(f,out)
  assert sha(out)==item[h]
  allrows.append({"group_id":gid,"category":category,"file":str(out.relative_to(OUT)),
                  "SHA256":item[h],"sales_approved":False,
                  "stock_package_rights_verified":False})
assert len(allrows)==36
assert len(set(x["group_id"] for x in allrows))==28
report={
 "version":"2.4.54b",
 "source_branches":["production-assets-v2453b-34-photo-JPG-27families","production-assets-v2454-obge-300ml-official-facts-only"],
 "review_candidate_JPGs":36,"previously_completed_JPGs_reused_byte_identical":34,
 "new_source_fact_cards_reused_byte_identical":2,
 "families_with_some_actual_asset":28,
 "groups_without_any_suitable_sale_asset":["pending-01","pending-08"],
 "groups_without_correct_actual_product_photo":["pending-01","pending-08","pending-22"],
 "OBgE_300mL_wrong_cushion_photo_permanently_rejected":True,
 "approved_brand_shade_charts":0,"approved_complete_product_image_sets":0,
 "original_public_55_URL_changes":0,"original_531_source_JPG_overwrites":0,
 "commercial_photo_reuse_rights_verified":0,"actual_stock_packaging_verified":0,
 "spreadsheet_shared":False,
 "manifest":allrows,
 "next":["Inspect and safely recover authentic non-swatch MISSHA Cover Lasting product photo without excluded shade 21",
         "Inspect peripera accurate 01-20 packaging photo without mixing 26AD generation",
         "OBgE 300mL actual verified pump photo still missing and must not be approximated",
         "Each 5 or 6 frame set remains unapproved until rights and shade QA"]}
(OUT/"v2454b-resumable-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2454b_36_actual_photo_and_facts_QA_HOLD.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in allrows:z.write(OUT/x["file"],arcname=x["file"])
 z.write(OUT/"v2454b-resumable-checkpoint.json",arcname="v2454b-resumable-checkpoint.json")
with zipfile.ZipFile(OUT/"v2454b_36_actual_photo_and_facts_QA_HOLD.zip") as z:
 assert z.testzip() is None and len(z.namelist())==37
print(json.dumps({"version":"2.4.54b","assets":36,"families":28,"spreadsheet_shared":False}),flush=True)
