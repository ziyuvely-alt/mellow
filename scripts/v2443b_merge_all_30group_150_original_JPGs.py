#!/usr/bin/env python3
"""v2443b merge exact already saved JPG bytes into complete 30-group review package.
No re-render or modification to 29 existing 5-frame family candidates.
Change only pending-26 3+2 verified factual frames; all source SHA256 verified.
"""
from pathlib import Path
from PIL import Image
import shutil,hashlib,json,zipfile
OUT=Path("v2443b-output");OUT.mkdir(exist_ok=True)
OLD=Path("prior-v2442b")
NEW=Path("prior-v2443")
m=json.loads((OLD/"v2442b_30group_candidate_manifest.json").read_text())
n=json.loads((NEW/"v2443_pending26_checkpoint.json").read_text())
assert m["families_attempted"]==30 and m["total_copied_existing_JPG_frames"]==148
assert n["five_candidate_set_assembled"] and len(n["frames"])==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p):
 with Image.open(p) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
family_results=[];all_files=[]
for family in m["families"]:
 gid=family["group_id"]
 if gid=="pending-26":
  selected=[{"source":NEW/x["path"],"sha256":x["sha256"],"role":x["role"]} for x in n["frames"]]
 else:
  selected=[{"source":OLD/x["file"],"sha256":x["sha256"],"role":x["input_role"]} for x in family["frames"]]
 assert len(selected)==5,(gid,len(selected))
 new_f=[]
 for i,entry in enumerate(selected,1):
  p=entry["source"]
  assert p.exists(),p
  assert sha(p)==entry["sha256"]
  check(p)
  dst=OUT/"all-30-family-5frame-candidate-JPGs"/gid/(f"{i:02d}_"+p.name.replace(f"{i:02d}_","",1))
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,dst)
  assert sha(dst)==entry["sha256"]
  new_f.append({"slot":i,"file":str(dst.relative_to(OUT)),
   "sha256":entry["sha256"],"role":entry["role"],
   "full_manual_visual_QA":"NOT_COMPLETE",
   "commercial_photo_rights":"UNVERIFIED","physical_stock_verified":False})
  all_files.append(dst)
 family_results.append({"group_id":gid,"candidate_images":5,
    "source_risk":family.get("confirmed_product_or_shade_issue"),
    "commercial_sale_approved":False,
    "exact_shade_set_source_confirmed":False,
    "current_5_actual_jpgs":new_f})
assert len(family_results)==30 and len(all_files)==150
assert len({(x["group_id"],f["slot"]) for x in family_results for f in x["current_5_actual_jpgs"]})==150
report={
"version":"2.4.43b",
"previous":"production-assets-v2442b-thirty-safety-filtered-sets",
"pending26_addendum":"production-assets-v2443-pixelpure-five-145ml",
"new_generated_photographic_images":0,"new_generated_factual_info_images_in_prior_stage":2,
"product_groups":30,"actual_existing_plus_new_candidate_JPG":150,
"groups_with_exactly_five_actual_JPG_candidates":30,
"other_29_groups_images_re_rendered":False,
"prior_17_customer_JPG_modified":False,
"original_531_JPG_overwritten":0,"public_55_URL_overwritten":0,
"image_format_all":"1080x1080 JPG under 2MB",
"all_byte_SHA256_source_match":True,
"FINAL_QA_APPROVED":0,"no_official_swatch_generated":True,
"commercial_rights_verified":0,"physical_stock_package_verified":0,
"remaining_critical_holds":[
 "pending-01 MISSHA Cover Lasting original 21 excluded, no approved cover shade-chart",
 "pending-08 Peripera 01..20 official same-generation shade chart; 26AD conflicts",
 "pending-10 OBgE cushion renewed edition swatch/photo provenance",
 "pending-21 Goodal exact eye-care source photo match",
 "pending-22 OBgE 300mL original 300mL INCI exact proof",
 "pending-26 PIXELPURE stock 145mL product photo rights and final commercial approval",
 "pending-27 PIXELPURE 200mL toner actual physical stock photo and source rights",
 "All 30 groups five customer JPGs full manual per-frame content and photo-rights approval"
],
"families":family_results,
"next":"Audit each family JPG content/packaging visually and independently, do not imply ZIP means sale-ready"
}
report_file=OUT/"v2443b_full_30family_manifest.json"
report_file.write_text(json.dumps(report,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2443b_30family_150_real_candidate_JPGs.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in all_files:z.write(p,arcname=str(p.relative_to(OUT)))
 z.write(report_file,arcname=report_file.name)
with zipfile.ZipFile(OUT/"v2443b_30family_150_real_candidate_JPGs.zip") as z:
 assert len(z.namelist())==151 and z.testzip() is None
print(json.dumps({k:report[k] for k in ["version","product_groups","actual_existing_plus_new_candidate_JPG","groups_with_exactly_five_actual_JPG_candidates","all_byte_SHA256_source_match","FINAL_QA_APPROVED"]},ensure_ascii=False),flush=True)
