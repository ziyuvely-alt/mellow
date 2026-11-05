#!/usr/bin/env python3
"""v2920 consolidate six partial product-specific source-photo sets without altering prior image bytes.

Each product retains 3 or 4 real 1080 JPGs and explicit missing slots. This is INTERNAL
QA ONLY, never a sales/upload packet. No synthetic product photography, no claim copy.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from zipfile import ZipFile, ZIP_STORED
import io,json,time

ROOT=Path("qa-review")
P12=ROOT/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
P14=ROOT/"v2914-pixelpure-twelve-photo-visual-relevance-claims-and-duplicate-QA"
P17=ROOT/"v2917-threefamily-official-photo-visual-claim-review-QA"
P19=ROOT/"v2919-reconcile-parallel-v2917-and-pixelpure-extra-big-firstparty-QA"
OUT=ROOT/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
assert not OUT.exists()
S=json.loads((P19/"stock30-incremental-state-v2919.json").read_text(encoding="utf-8"))
J12=json.loads((P12/"manifest.json").read_text(encoding="utf-8"))
J14=json.loads((P14/"manifest.json").read_text(encoding="utf-8"))
J17=json.loads((P17/"manifest.json").read_text(encoding="utf-8"))
J19=json.loads((P19/"manifest.json").read_text(encoding="utf-8"))
assert S["version"]=="v2919" and len(S["families"])==30
assert J19["v2918_existing_two_fivephoto_ZIPs_preserved"]==2 and J19["old_55_public_urls_unchanged"]
by12={x["family"]:x for x in J12["family_results"]}
by14={x["family"]:x for x in J14["results"]}
by17={x["family"]:x for x in J17["results"] if x["family"] in ("pending-24","pending-25")}
by19={x["family"]:x for x in J19["pixelpure_results"]}
TARGETS=[
 ("pending-20","GOODAL_VitaC_SerumMist100mL_3OF5_INTERNAL_QA"),
 ("pending-24","BIOHEAL_GlowPowerSerum30mL_4OF5_INTERNAL_QA"),
 ("pending-25","BIOHEAL_GlowBoostCream50mL_3OF5_INTERNAL_QA"),
 ("pending-27","PIXELPURE_SoothingToner200mL_3OF5_INTERNAL_QA"),
 ("pending-29","PIXELPURE_AquaSoothingCream50mL_3OF5_INTERNAL_QA"),
 ("pending-30","PIXELPURE_AuraRadianceSerum50mL_3OF5_INTERNAL_QA")
]
def from_v2912(k):
 return [{"path":z["path"],"sha256":z["sha256"],"source_version":"v2912","role":"existing source photograph",
    "rights_verified":False,"stock_edition_verified":False} for z in by12[k]["source_photos"]]
def from_v2914(k):
 return [{"path":z["source_path"],"sha256":z["sha256"],"source_version":z["origin"],
    "role":z["role"],"rights_verified":False,"stock_edition_verified":False}
    for z in by14[k]["combined_clean_source_candidates"]]
def from_v2917(k):
 d=by17[k]
 return [{"path":d["official_gallery_source_path"],"sha256":d["official_photo_reference_SHA256"],
  "source_version":"v2915_branded_reference_selected_v2917","role":"first-party manufacturer gallery photograph",
  "rights_verified":False,"stock_edition_verified":False}]
def from_v2919(k):
 return [{"path":z["reference_jpg"],"sha256":z["reference_sha256"],"source_version":"v2919",
    "role":"newly acquired manufacturer full-native photo scene, visually reviewed",
    "rights_verified":False,"stock_edition_verified":False} for z in by19[k]["new_images"]]

SELECTIONS={
 "pending-20":lambda:from_v2912("pending-20"),
 "pending-24":lambda:from_v2912("pending-24")+from_v2917("pending-24"),
 "pending-25":lambda:from_v2912("pending-25")+from_v2917("pending-25"),
 "pending-27":lambda:from_v2914("pending-27"),
 "pending-29":lambda:from_v2914("pending-29")+from_v2919("pending-29"),
 "pending-30":lambda:from_v2914("pending-30")
}
OUT.mkdir(parents=True)
res=[];total=0
for fam,stem in TARGETS:
 srcs=SELECTIONS[fam]()
 assert 1<=len(srcs)<=5,(fam,len(srcs))
 unique=set();data=[]
 for i,record in enumerate(srcs,1):
  p=Path(record["path"])
  assert p.is_file(),("missing existing source",str(p))
  b=p.read_bytes()
  assert sha256(b).hexdigest()==record["sha256"],("source bytes changed",str(p))
  assert record["sha256"] not in unique,("byte duplicate within family",fam,str(p))
  unique.add(record["sha256"])
  with Image.open(io.BytesIO(b)) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080) and len(b)<2_000_000, (str(p),im.size,len(b))
  record.update({"source_index":i,"source_bytes":len(b),"native_format":"JPEG","pixels":[1080,1080],
    "zip_filename":f"{i:02d}-{fam}-UNCHANGED-SOURCE-QA.jpg",
    "sale_approved":False,"photo_scene_distinctness_final_QA":"PENDING",
    "model_rights_approved":False,"image_claims_approved":False})
  data.append((record,b))
 zip_path=OUT/(stem+".zip")
 with ZipFile(zip_path,"w",compression=ZIP_STORED) as zipf:
  for item,b in data:zipf.writestr(item["zip_filename"],b)
 with ZipFile(zip_path,"r") as zipf:
  assert len(zipf.namelist())==len(data)
  for item,b in data:assert zipf.read(item["zip_filename"])==b
 total+=len(srcs)
 missing=5-len(srcs)
 st=S["families"][fam]
 st.update({"last_delta_version":"v2920",
   "release_status":"REAL_SOURCE_PARTIAL_QA_ZIP_ORIGINAL_BYTES_ONLY_NO_RETAIL_APPROVAL",
   "v2920_actual_source_photo_count":len(srcs),
   "v2920_missing_photo_slots_to_five":missing,
   "v2920_partial_source_zip":str(zip_path),"sale_approved":False,
   "latest_photo_QA_checkpoint":f"v2920 {len(srcs)}/5 existing authentic-source 1080 JPG bytes SHA-verified and archived in separate internal ZIP (no pixel edits), {missing} remaining scenes. No commercial rights, owned stock edition or authentic MK verified."})
 res.append({"family":fam,"product":st["product"],"actual_original_source_jpgs_in_zip":len(srcs),
  "five_source_target_shortfall":missing,"zip_path":str(zip_path),
  "zip_sha256":sha256(zip_path.read_bytes()).hexdigest(),"zip_size_bytes":zip_path.stat().st_size,
  "image_records":[item for item,_ in data],
  "old_approved_11_families_unchanged":True,"new_commercial_use_approvals":0,"published":False})
assert total==19,(total,"unexpected source count")
manifest={"version":"v2920","baseline":"v2919","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "six_partial_product_groups":len(res),"real_unchanged_photo_sources_in_QA_ZIPs":total,
 "new_internal_source_photo_ZIPs":len(res),
 "still_missing_five_photo_slots":sum(x["five_source_target_shortfall"] for x in res),
 "new_photography_generated":0,"old_original_photos_modified":0,
 "existing_11_published_families_unchanged":True,"existing_55_public_URLs_unchanged":True,
 "v2918_completed_two_fivephoto_ZIPs_preserved":True,
 "no_financial_spreadsheet_shared":True,"new_sale_approvals":0,"new_published_urls":0,
 "not_upload_ready":True,"results":res}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
S["version"]="v2920";S["baseline"]="v2919";S["new_sales_approvals"]=0;S["new_public_URLs"]=0;S["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2920.json").write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2920","real_photo_sources":total,"new_qa_zips":len(res),
  "still_missing":manifest["still_missing_five_photo_slots"],
  "counts":{x["family"]:x["actual_original_source_jpgs_in_zip"] for x in res},
  "sale_approved":0},ensure_ascii=False))
