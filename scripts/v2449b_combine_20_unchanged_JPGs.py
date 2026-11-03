#!/usr/bin/env python3
"""v2449b consolidate 15 already edited real photo candidates plus 5 new actual photo details.
No rerenders. SHA-256 byte-identical copies. Preserve distinct holds for human likeness,
SKU generation and commercial image rights. No spreadsheets or Shopee publication.
"""
from pathlib import Path
from PIL import Image
from collections import Counter
import hashlib,json,shutil,zipfile
OUT=Path("v2449b-output");OUT.mkdir(exist_ok=True)
A=Path("prior-v2448b");B=Path("prior-v2449")
ma=json.loads((A/"v2448b-15photo-resumable-checkpoint.json").read_text())
mb=json.loads((B/"v2449_checkpoint.json").read_text())
assert len(ma["results"])==15 and len(mb["files"])==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entries=[];used=set()
for base,rows,key,hkey,origin in [
 (A,ma["results"],"file","sha256","v2448b_prior_success"),
 (B,mb["files"],"output","output_sha256","v2449_new_detail")]:
 for r in rows:
  p=base/r[key];assert p.is_file() and sha(p)==r[hkey]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
  gid=r["group_id"]
  k=(gid,r[hkey]);assert k not in used
  used.add(k)
  folder="separately-held-likeness" if gid in ("pending-09","pending-16") and origin=="v2449_new_detail" else "unapproved-real-photo-candidates"
  dst=OUT/folder/gid/(origin+"__"+p.name)
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,dst);assert sha(dst)==r[hkey]
  status=("LIKELINESS_PERMISSION_HOLD" if folder=="separately-held-likeness" else
          "SOURCE_EDITION_AND_COMMERCIAL_RIGHTS_HOLD")
  if gid=="pending-27":status="200ML_EXACT_GENERATION_AND_PHOTO_RIGHTS_HOLD"
  entries.append({"group_id":gid,"source_batch":origin,"file":str(dst.relative_to(OUT)),
       "sha256":r[hkey],"status":status,"full_set_complete":False,"final_sale_approved":False})
assert len(entries)==20
report={
 "version":"2.4.49b",
 "source_branches":["production-assets-v2448b-15-photo-candidate-checkpoint","production-assets-v2449-five-new-photo-details"],
 "prior_exact_images_reused":15,"new_actual_photo_detail_frames":5,
 "unique_JPGs_reverified":20,"distinct_product_families":len(set(x["group_id"] for x in entries)),
 "new_product_photo_pixels_synthesized":False,
 "model_likeness_candidiates_held":2,
 "all_source_JPGs_sha256_preserved":True,
 "all_20_images_1080x1080_under_2MB":True,
 "prior_64_logo_quarantined_images_preserved":True,
 "prior_86_image_candidates_preserved":True,
 "prior_public_55_URL_paths_changed":0,
 "commercial_photo_permission_verified":0,"physical_stock_package_verified":0,
 "FINAL_SALES_APPROVED":0,"new_official_shade_charts":0,
 "NO_SPREADSHEET_SHARED":True,
 "files":entries,
 "next_actions":[
  "Inspect verified source photo assets for additional distinct frames without reproducing already edited 20",
  "Confirm 200mL exact PIXELPURE toner package and photo rights",
  "Commercial permission checks for model-likeness images in pending-09 and pending-16",
  "Continue 30-group manual individual-image QA and official exact color-generation source verification"
 ],
 "notice":"20 photo-based candidates remain draft images, not an approved product-image upload set"
}
(OUT/"v2449b-resumable-checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2449b_20_real_JPG_candidates_rights_HOLD.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for r in entries:z.write(OUT/r["file"],arcname=r["file"])
 z.write(OUT/"v2449b-resumable-checkpoint.json",arcname="v2449b-resumable-checkpoint.json")
with zipfile.ZipFile(OUT/"v2449b_20_real_JPG_candidates_rights_HOLD.zip") as z:
 assert len(z.namelist())==21 and z.testzip() is None
print(json.dumps({k:report[k] for k in ["version","unique_JPGs_reverified","distinct_product_families","model_likeness_candidiates_held","FINAL_SALES_APPROVED","NO_SPREADSHEET_SHARED"]}),flush=True)
