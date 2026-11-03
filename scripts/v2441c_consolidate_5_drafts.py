#!/usr/bin/env python3
"""v2441c consolidate five new distinct corrected customer JPEGs, no rerender.
Reuse prior v2440e without touching its 12 completed JPGs.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
OUT=Path("v2441c-output");OUT.mkdir(exist_ok=True)
entries=[]
branches=[
 ("v2441-source","v2441_checkpoint.json","edits","updated_path","updated_sha256"),
 ("v2441b-source","v2441b_checkpoint.json","results","file","sha256")
]
seen=set()
for branch,manifest,key,filename,hashfield in branches:
 base=Path(branch)
 rows=json.loads((base/manifest).read_text())[key]
 for x in rows:
  group=x["group_id"]
  p=base/x[filename]
  assert p.exists()
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  assert digest==x[hashfield]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2000000
  k=(group,x.get("source_path") or x.get("source"))
  assert k not in seen, k
  seen.add(k)
  dest=OUT/"new-only-5-JPGs"/group/p.name
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,dest)
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
  entries.append({"group_id":group,"file":str(dest.relative_to(OUT)),"sha256":digest,
     "state":"SALES_IMAGE_DRAFT","individual_visual_design_review":"PASS",
     "exact_stock_package_verification":"PENDING","commercial_photo_rights":"PENDING"})
assert len(entries)==5 and len(set(x["group_id"] for x in entries))==5
report={
"version":"2.4.41c",
"prior_immutable_checkpoint":"production-assets-v2440e-12-drafts-consolidated",
"prior_12_customer_JPG_recreated":False,"new_real_JPGs":len(entries),
"new_groups":len(set(x["group_id"] for x in entries)),
"groups":["pending-13","pending-18","pending-19","pending-22","pending-24"],
"new_customer_jpg":entries,
"original_source_JPG_overwrites":0,"public_URL_changes":0,
"published_55_URL_HTTP_check":False,
"photo_permission_granted":0,"stock_package_checked":0,"FINAL_QA_APPROVED":0,
"independent_holds":[
{"group":"pending-22","source":"INFO_04_OFFICIAL_V2412_EN_V2421.jpg","reason":"Unverified Panthenol Ectoin hyaluronic acid derivatives ingredient source; not re-created or approved"},
{"group":"pending-19","source":"INFO_FUNCTION_01_V2414B_EN_V2421.jpg","reason":"Dual brightening + wrinkle care claim inherited from existing source pending official Korean package verification"},
{"group":"pending-24","reason":"NAD-PRIZCELL spelling visually matches recorded previous actual package, but commercial rights and stock still not proved"}],
"next_resume":["Continue actual customer frame checks for unreviewed images beyond current 5","Prioritize product and edition mismatch rather than decorative edits","Verify C8 official shade chart generation and actual brand original usage permissions","Keep past 11 approved public groups and 55 URLs immutable"],
"caution":"Public GitHub branch images are not confidential; no Shopee publishing"
}
(OUT/"v2441c_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2441c-five-new-JPGs.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
 for x in entries:z.write(OUT/x["file"],arcname=x["file"])
 z.write(OUT/"v2441c_checkpoint.json",arcname="v2441c_checkpoint.json")
with zipfile.ZipFile(OUT/"v2441c-five-new-JPGs.zip") as z:
 assert len(z.namelist())==6 and z.testzip() is None
print(json.dumps({"version":"2.4.41c","new_jpg":len(entries),"new_groups":len(set(x["group_id"] for x in entries)),"prior_completed_12_untouched":True,"zip":"v2441c-five-new-JPGs.zip"}))
