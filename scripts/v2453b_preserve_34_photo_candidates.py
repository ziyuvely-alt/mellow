#!/usr/bin/env python3
"""v2453b exactly 34 source-backed JPG review candidates, no regeneration.
Source batches: v2452 32 SHA-verified, v2453 2 actual visually checked CLIO
recovery images. Source rights, shades, and stock still unapproved.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile,csv
A=Path("prior-v2452");B=Path("prior-v2453")
OUT=Path("v2453b-output");OUT.mkdir(exist_ok=True)
old=json.loads((A/"v2452-resumable-checkpoint.json").read_text())
new=json.loads((B/"v2453_checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];uniques=set();source_hashes=[]
for root,items,filekey,hashkey,role in [(A,old["reviewable_files"],"file","SHA256","v2452-reuse"),
                                      (B,new["new_photo_crops"],"actual_JPG","SHA256","v2453-quality-fixed")]:
 for item in items:
  gid=item["group_id"];src=root/item[filekey]
  assert src.is_file() and sha(src)==item[hashkey]
  with Image.open(src) as chk:
   chk.load();assert chk.size==(1080,1080) and chk.format=="JPEG" and src.stat().st_size<2000000
  assert (gid,item[hashkey]) not in uniques
  uniques.add((gid,item[hashkey]))
  target=OUT/"34-actual-source-JPGs-QA-HOLD"/gid/(role+"__"+src.name)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(src,target);assert sha(target)==item[hashkey]
  rows.append({"group_id":gid,"file":str(target.relative_to(OUT)),"sha256":item[hashkey],
               "source_version":role,"visual_design_QA": "PASS_PHOTO_FRAMING" if role=="v2453-quality-fixed" else "PREVIOUSLY_INSPECTED_OR_QA_HOLD",
               "commercial_photo_license":False,"physical_stock_edition_verified":False,
               "official_shade_chart_verified":False,"final_sales_approved":False})
assert len(rows)==34
groups=sorted({x["group_id"] for x in rows})
missing=sorted(set(f"pending-{i:02d}" for i in range(1,31))-set(groups))
assert len(groups)==27 and missing==["pending-01","pending-08","pending-22"],(groups,missing)
bad_new_obge=new["wrong_product_photo_quarantine"]
assert bad_new_obge["group_id"]=="pending-22" and "wrong product" in bad_new_obge["reason"].lower()
report={"version":"2.4.53b","base":"production-assets-v2452-32-source-JPGs-five-groups-hold",
"new_source":"production-assets-v2453-two-CLIO-repaired-plus-obge-reject",
"all_real_customer_JPGs_checked_and_byte_preserved":34,
"old_32_photo_JPGs_regenerated":0,
"recovered_v2453_real_CLIO_photo_JPGs":2,
"groups_with_some_photographic_candidate":27,
"groups_still_without_usable_photo_candidate":missing,
"old_CLIO_two_failed_crops_still_quarantined":True,
"original_531_JPGs_unchanged":True,"published_55_URLs_unchanged":True,
"additional_official_shade_charts_approved":0,
"commercial_photo_rights_verified":0,"physical_stock_generation_verified":0,
"five_or_six_frame_sale_sets_final_approved":0,
"XLSX_or_Google_Sheets_shared":False,
"source_wrong_product_permanent_hold":bad_new_obge,
"remain":[
"MISSHA Cover Lasting shade #21 excluded but archived hero visibly includes #21; no wrong-shade reuse",
"peripera Glow Tint must remain 01 to 20 only, missing shade photographs and user source verification",
"OBgE MAX 300mL original blurry 300mL pump; alternative source second photo is a cushion case, permanently rejected",
"All 34 draft product photographs require stock package and commercial photo rights QA",
"All 30 families lack fully approved six-frame customer sale-ready sets"
],
"candidate_images":rows}
(OUT/"v2453b_34-JPG-resumable-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (OUT/"v2453b-34-JPG-source-hashes.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with zipfile.ZipFile(OUT/"v2453b_34_true_photo_candidates_QA-HOLD.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for r in rows:z.write(OUT/r["file"],arcname=r["file"])
 z.write(OUT/"v2453b_34-JPG-resumable-checkpoint.json",arcname="v2453b_34-JPG-resumable-checkpoint.json")
with zipfile.ZipFile(OUT/"v2453b_34_true_photo_candidates_QA-HOLD.zip") as z:
 assert z.testzip() is None and len(z.namelist())==35
print(json.dumps({"version":"2.4.53b","actual_JPGs":34,"families":27,"remaining":missing,"spreadsheets_shared":False,"final_approved":0}),flush=True)
