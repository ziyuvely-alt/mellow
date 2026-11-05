#!/usr/bin/env python3
"""v2944 create four real internal 5-frame packs: 4 untouched SHA-authenticated sources
plus one v2943 true-alpha based English info frame. 5 QA FRAMES != 5 PHOTO SCENES.
Source-photo rights/physical stock/approved logo are not validated. Never publish.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from io import BytesIO
from hashlib import sha256
from PIL import Image
import json,time

Q=Path("qa-review")
PRE=Q/"v2943-four-English-frame-clean-truealpha-product-panel-QA"
ORIG=Q/"v2940-four-final-source-gaps-photo-archive-integrity-and-approval-gate"
OUT=Q/"v2944-four-5frame-product-first-internal-only-QA-ZIPs"
assert not OUT.exists(),"v2944 already exists; do not rebuild."
state=json.loads((PRE/"stock30-incremental-state-v2943.json").read_text(encoding="utf-8"))
alpha=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
src=json.loads((ORIG/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]==alpha["version"]=="v2943" and src["version"]=="v2940"
assert len(state["families"])==30 and alpha["actual_new_clean_photo_panel_frames"]==4
previous={x["family"]:x for x in src["four_missing_source_families"]}
clean={x["family"]:x for x in alpha["results"]}
assert set(previous)==set(clean)=={"pending-25","pending-27","pending-29","pending-30"}

def image_ok(data):
 assert len(data)<2_000_000
 with Image.open(BytesIO(data)) as photo:
  photo.load()
  assert photo.format=="JPEG" and photo.size==(1080,1080)
 return True

OUT.mkdir(parents=True)
results=[]
for fam in sorted(previous):
 meta=previous[fam]["verified_archive"]
 existing=Path(meta["path"])
 assert existing.is_file() and sha256(existing.read_bytes()).hexdigest()==meta["sha256"]
 old_four=[]
 with ZipFile(existing,"r") as z:
  assert len(z.namelist())==4 and z.testzip() is None
  for idx,name in enumerate(z.namelist(),1):
   data=z.read(name);image_ok(data)
   old_four.append({"order":idx,"bytes":data,"sha256":sha256(data).hexdigest(),"old_entry":name})
 fifth=clean[fam]
 assert fifth["visual_quality"]=="TRUE_ALPHA_PRODUCT_PHOTO_PANEL_COMPOSED_NEEDS_HUMAN_QA"
 info_path=Path(fifth["new_clean_panel_img"])
 info_bytes=info_path.read_bytes();image_ok(info_bytes)
 assert sha256(info_bytes).hexdigest()==fifth["new_sha256"]
 all_bytes=[x["bytes"] for x in old_four]+[info_bytes]
 assert len({sha256(b).hexdigest() for b in all_bytes})==5
 folder=OUT/fam;folder.mkdir()
 dst=folder/(fam+"-FOUR-PHOTOS-PLUS-ONE-EN-INFO-INTERNAL.zip")
 with ZipFile(dst,"w",compression=ZIP_STORED) as z:
  for i,data in enumerate(all_bytes,1):
   z.writestr(f"{i:02d}-"+("SOURCE-PHOTO-UNMODIFIED" if i<=4 else "ENGLISH-FACT-INFO-TRUEALPHA-QA")+".jpg",data)
 with ZipFile(dst) as z:
  assert z.testzip() is None and len(z.namelist())==5
  for i,data in enumerate(all_bytes):
   assert z.read(z.namelist()[i])==data
 # Confirm no old source was rewritten by checkpoint.
 assert sha256(existing.read_bytes()).hexdigest()==meta["sha256"]
 assert sha256(info_path.read_bytes()).hexdigest()==fifth["new_sha256"]
 result={
   "family":fam,"product":state["families"][fam]["product"],
   "internal_zip":str(dst),"internal_zip_sha256":sha256(dst.read_bytes()).hexdigest(),
   "ZIP_CRC":"PASS","source_original_photo_count":4,"new_info_frame_count":1,
   "total_QA_frames":5,"fifth_independent_photo_still_missing":True,
   "sha256_of_each_frame":[sha256(data).hexdigest() for data in all_bytes],
   "old_archive_unchanged":True,"old_four_source_sha256":meta["sha256"],
   "new_info_file":str(info_path),"new_info_sha256":fifth["new_sha256"],
   "readiness":"INTERNAL_QA_ONLY_RIGHTS_STOCK_PHOTO_ADCLAIMS_HOLD",
   "retail_approved":False,"image_rights_verified":False,
   "actual_stock_edition_verified":False,"MK_logo_verified_and_applied":False,
   "final_spreadsheet_shared":False}
 results.append(result)
 state["families"][fam].update({
   "last_delta_version":"v2944",
   "release_status":"FOUR_SOURCE_PHOTOS_PLUS_ENGLISH_INFO_INTERNAL_ZIP_COMPLETE_RETAIL_HOLD",
   "v2944_5frame_internal_zip":str(dst),
   "v2944_5frame_internal_zip_sha256":result["internal_zip_sha256"],
   "v2944_total_QA_frames":5,
   "v2944_independent_source_photo_count":4,
   "v2944_unresolved_distinct_photo_count":1,
   "sale_approved":False,
   "latest_photo_QA_checkpoint":"v2944 5-frame internal ZIP SHA+CRC verified: 4 original JPG bytes unchanged + 1 v2943 English fact image. Rights, stock, genuine MK and one distinct photo still HOLD."})
assert len(results)==4
manifest={
 "version":"v2944","baseline":"v2943",
 "generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "new_internal_product_ZIPs_created":4,
 "new_archived_image_count":20,
 "old_photo_JPG_bytes_preserved":16,
 "new_English_info_JPGs_reused":4,
 "new_original_photo_scenes":0,
 "still_missing_independent_photo_slots":4,
 "retail_approved_images":0,
 "previous_11_approved_families_untouched":True,
 "previous_55_public_URLs_untouched":True,
 "old_QA_file_modifications":0,
 "new_public_URLs":0,
 "final_spreadsheet_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state.update({"version":"v2944","baseline":"v2943","new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False})
(OUT/"stock30-incremental-state-v2944.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2944","five_frame_ZIPs":4,"old_photos_preserved":16,
 "reused_truealpha_English_info_frames":4,"distinct_photo_shortfall":4,
 "retail_approved":0},ensure_ascii=False))
