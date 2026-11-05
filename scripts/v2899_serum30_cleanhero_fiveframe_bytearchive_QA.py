#!/usr/bin/env python3
"""v2899: ONE pending-13 coherent 5-frame INTERNAL QA bundle by byte-only
copy, using official clean 30mL first frame and prior 2..5 archived scenes.
Protect previous JPGs, no resampling or generative edits. 4th model-image
commercial permission not evidenced. Release stays HOLD.
"""
from pathlib import Path
from hashlib import sha256
from shutil import copyfile
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import json,copy

R=Path("qa-review")
PRE=R/"v2898-two-existing-clean-source-alternatives-and-69-option-crosswalk"/"stock30-incremental-state-v2898.json"
B=R/"v2854-missha30-obge300-recovered-existing-artwork-QA"/"pending-13"/"manifest.json"
OFF=R/"v2896-missha30-brand-official-clean-single-bottle-source"/"manifest.json"
OUT=R/"v2899-missha-serum30-clean-hero-existing-4scene-internal-QA"
assert PRE.is_file() and B.is_file() and OFF.is_file() and not OUT.exists()
state=json.loads(PRE.read_text())
old=json.loads(B.read_text())
new=json.loads(OFF.read_text())
assert state["version"]=="v2898" and len(state["families"])==30
assert old["family"]=="pending-13" and len(old["slots"])==5
assert new["version"]=="v2896" and new["new_firstparty_clean_reference_status"]=="NEW_OFFICIAL_SINGLE_BOTTLE_SOURCE_SAVED_NO_RETRO_ALPHA"
source=Path(new["source_white_background_JPG_1080"])
assert source.exists()
items=[{
 "slot":1,"source":str(source),"expected_SHA256":new["source_1080_sha256"],
 "photo_role":"NEW_OFFICIAL_CLEAN_SINGLE_BOTTLE_WHITE_BG",
 "separate_model_image_rights_hold":False
}]
for oldslot in old["slots"]:
 if oldslot["slot"]==1:continue
 assert oldslot["slot"] in (2,3,4,5)
 items.append({"slot":oldslot["slot"],"source":oldslot["source"],
  "expected_SHA256":oldslot["sha256"],
  "photo_role":{2:"EXISTING_ACTUAL_DROPPER_TEXTURE",3:"EXISTING_ACTUAL_SERUM_BOTTLE_DETAILED",
                4:"EXISTING_LIFESTYLE_MODEL_IMAGE",5:"EXISTING_FACT_SHEET_30ML"}[oldslot["slot"]],
  "separate_model_image_rights_hold":oldslot["slot"]==4})
assert len(items)==5 and [x["slot"] for x in items]==list(range(1,6))
OUT.mkdir(parents=True)
outitems=[]
for it in items:
 src=Path(it["source"])
 assert src.is_file()
 blob=src.read_bytes()
 assert sha256(blob).hexdigest()==it["expected_SHA256"],("source SHA mismatched",src)
 with Image.open(src) as im:
  im.verify()
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080),("invalid archived image",src,im.format,im.size)
 dst=OUT/f"{it['slot']:02d}-ARCHIVED-EXACT-JPG-INTERNAL-QA.jpg"
 assert not dst.exists()
 copyfile(src,dst)
 assert sha256(dst.read_bytes()).hexdigest()==it["expected_SHA256"]
 outitems.append({**it,"copy":str(dst),"sha256":it["expected_SHA256"],
                  "bytes":dst.stat().st_size,
                  "source_untouched":True,"sale_approved":False})
ZIP=OUT/"MISSHA_Serum30ml_5JPG_INTERNAL_QA_NOT_FOR_PUBLIC_UPLOAD.zip"
with ZipFile(ZIP,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
 for item in outitems:
  p=Path(item["copy"])
  z.write(p,arcname=p.name)
with ZipFile(ZIP) as z:
 assert z.testzip() is None and len(z.namelist())==5
manifest={
 "version":"v2899","baseline":"v2898","family":"pending-13",
 "product":"MISSHA Camellia PDRN NAD+ Firming Repair Serum 30mL",
 "deliverable":"5 actual 1080x1080 JPEG files, 1 internal QA ZIP",
 "previous_5JPG_set_left_untouched":True,"source_files_untouched":True,
 "new_image_pixels_rendered":0,"byte_exact_source_files_reused":5,
 "model_lifestyle_image_slot_4_requires_separate_commercial_photo_and_model_rights":True,
 "firstparty_official_catalog_photo_license_verified":False,
 "user_owned_stock_KR_edition_verified":False,
 "authentic_original_MK_logo_verified":False,
 "retail_release_status":"INTERNAL_QA_5JPG_READY_NOT_APPROVED_FOR_SALES",
 "images":outitems,"zip_path":str(ZIP),"zip_sha256":sha256(ZIP.read_bytes()).hexdigest(),
 "zip_bytes":ZIP.stat().st_size,
 "prior_approved_11_families_protected":True,
 "prior_public_55_URLs_unchanged":True,"new_sales_approvals":0,
 "public_JPG_URLs_added":0,"final_spreadsheet_shared":False
}
st=copy.deepcopy(state);st["version"]="v2899";st["baseline"]="v2898"
fam=st["families"]["pending-13"]
fam["last_delta_version"]="v2899"
fam["release_status"]="NEW_CLEAN_HERO_5_SCENE_INTERNAL_QA_ARCHIVE_READY_HOLD_PHOTO_RIGHTS_STOCK_MK"
fam["latest_photo_QA_checkpoint"]="v2899 one firstparty official 30ml clean hero + exact bytes old four archived scenes bundled as 5 actual QA JPG and ZIP; model slide commercial rights and stock edition HOLD"
fam["new_clean_five_scene_internal_QA_set"]={"JPGs":5,"zip":str(ZIP),"new_rendered_pixels":0}
st["v2899_prior_images_modified"]=0;st["new_sale_approvals"]=0;st["new_public_URLs"]=0
st["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2899.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2899","family":"pending-13","JPGs":len(items),"zip":str(ZIP),
                  "zip_sha256":manifest["zip_sha256"],"new_sale_approvals":0},ensure_ascii=False))
