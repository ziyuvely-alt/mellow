#!/usr/bin/env python3
"""v2922: package 25 previously reviewed, byte-identical archive JPGs in 5 internal-only QA ZIPs.
Pending-15/18/21 reuse v2889 archived hash-verified files.
Pending-16/17 reuse v2910 immutable historical git commit bytes (even if absent from current branch).
Nothing is a new sale image, new source photograph, or photo-rights/edition approval.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_STORED
from hashlib import sha256
from io import BytesIO
from PIL import Image
import subprocess,json,time

QA=Path("qa-review")
PRE=QA/"v2921-pixelpure-KR-two-family-unseen-product-gallery-source-QA"
V89=QA/"v2889-goodal25ad-drg2022-two-edition-15photo-QA"
V10=QA/"v2910-drg-2022-red-and-2023-moisture-sun-10-existing-image-qa"
V18=QA/"v2918-two-family-byte-identical-five-photo-internal-zip-QA"
V20=QA/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
OUT=QA/"v2922-five-legacy-stock-family-original-25photo-internal-only-archive-ZIP"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2921.json").read_text(encoding="utf-8"))
a=json.loads((V89/"manifest.json").read_text(encoding="utf-8"))
b=json.loads((V10/"manifest.json").read_text(encoding="utf-8"))
old_complete=json.loads((V18/"manifest.json").read_text(encoding="utf-8"))
old_partial=json.loads((V20/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2921" and len(state["families"])==30
assert old_complete["internal_verified_5JPG_ZIPs"]==2 and old_partial["new_internal_source_photo_ZIPs"]==6
assert old_complete["previous_55_published_URLs_preserved"] and old_partial["existing_55_public_URLs_unchanged"]
by89={p["family"]:p for p in a["frame_provenance"]}
by10={p["family"]:p for p in b["cases"]}
targets=[
 ("pending-15","DRG_GreenMildUpSunPlus_2022_50mL_5ARCHIVED_SOURCE_QA"),
 ("pending-16","DRG_RedBlemishCream_2022_70mL_5HISTORIC_SOURCE_QA"),
 ("pending-17","DRG_BrighteningMoistureSun_2023_50mL_5HISTORIC_SOURCE_QA"),
 ("pending-18","DRG_BrighteningUpSunPlus_50mL_5ARCHIVED_SOURCE_QA"),
 ("pending-21","GOODAL_VitaCDarkCircleEyeCream_25AD_5ARCHIVED_SOURCE_QA")
]
def original_sources(family):
 if family in by89:
  return [{
   "index":f["slot"],"path":f["path"],"expected_sha256":f["source_SHA256"],
   "expected_bytes":f["size_bytes"],"origin":"v2889 source still present in historical QA branch",
   "get_bytes":lambda p=f["path"]:Path(p).read_bytes()} for f in by89[family]["files"]]
 c=by10[family]
 return [{
  "index":f["slot"],"path":f["existing_immutable_history_source"],
  "expected_sha256":f["source_bytes_sha256"],"expected_bytes":f["image_bytes"],
  "origin":"v2910 historical Git commit object, no existing file restored",
  "get_bytes":lambda obj=f["existing_immutable_history_source"]:subprocess.check_output(["git","show",obj])
 } for f in c["frames"]]
OUT.mkdir(parents=True)
results=[]
for family,stem in targets:
 srcs=original_sources(family)
 assert len(srcs)==5 and sorted(x["index"] for x in srcs)==[1,2,3,4,5]
 recs=[];payload=[];unique=set()
 for x in srcs:
  raw=x["get_bytes"]()
  digest=sha256(raw).hexdigest()
  assert digest==x["expected_sha256"],("unexpected source bytes",family,x["path"])
  assert len(raw)==x["expected_bytes"],("unexpected byte count",family,x["path"])
  assert digest not in unique,("exact duplicate photograph",family,x["index"])
  unique.add(digest)
  with Image.open(BytesIO(raw)) as jpg:
   jpg.load()
   assert jpg.format=="JPEG" and jpg.size==(1080,1080) and len(raw)<2_000_000, (family,x["path"])
  entry=f"{x['index']:02d}-{family}-UNCHANGED-ARCHIVED-REFERENCE.jpg"
  payload.append((entry,raw))
  recs.append({
   "slot":x["index"],"origin":x["origin"],"existing_source":x["path"],
   "sha256":digest,"bytes":len(raw),"format":"JPEG","pixels":[1080,1080],
   "zip_member":entry,"photo_edition_verified":False,
   "rights_for_sale_verified":False,"authentic_MK_logo_verified":False,
   "marketing_claims_approved":False,"retail_approved":False})
 path=OUT/(stem+".zip")
 with ZipFile(path,"w",compression=ZIP_STORED) as z:
  for name,raw in payload:z.writestr(name,raw)
 with ZipFile(path,"r") as z:
  assert len(z.namelist())==5
  for name,raw in payload:assert z.read(name)==raw
 st=state["families"][family]
 st.update({"last_delta_version":"v2922",
   "release_status":"FIVE_ARCHIVED_ORIGINAL_BYTES_GROUPED_INTERNAL_ONLY_EDITION_RIGHTS_MK_HOLD",
   "v2922_archived_five_immutable_original_photos_count":5,
   "v2922_internal_only_photo_zip":str(path),
   "v2922_owned_stock_edition_verified":False,
   "v2922_retail_photo_use_approved":False,
   "latest_photo_QA_checkpoint":"v2922 five preexisting historical 1080 JPGs hash-checked and grouped in an internal QA ZIP. Exact 2022/2023/25AD stock edition, commercial rights, authentic MK and claims HOLD. No photos regenerated or released.",
   "sale_approved":False})
 results.append({"family":family,"product":st["product"],"existing_source_photos":5,
    "old_source_bytes_modified":0,"new_photo_generation":0,"zip_path":str(path),
    "zip_sha256":sha256(path.read_bytes()).hexdigest(),
    "archive_originals":[x for x in recs],
    "sale_approved":False,"not_upload_ready":True})
manifest={"version":"v2922","baseline":"v2921",
 "generated_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "archive_groups":len(results),"existing_unchanged_JPGs_integrity_validated":sum(x["existing_source_photos"] for x in results),
 "new_internal_5JPG_ZIPs":len(results),"new_original_photos_created":0,
 "v2918_existing_2_completed_QA_ZIPs_unchanged":True,
 "v2920_existing_6_partial_QA_ZIPs_unchanged":True,
 "legacy_11_commercial_families_untouched":True,
 "existing_55_public_URLs_unchanged":True,"all_original_archival_sources_unchanged":True,
 "new_sale_approvals":0,"new_public_images":0,"final_spreadsheet_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2922";state["baseline"]="v2921";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2922.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2922","families":5,"source_JPGs_validated":25,"new_QA_ZIPs":5,"old_source_modified":0,"retail_approvals":0},ensure_ascii=False))
