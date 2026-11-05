#!/usr/bin/env python3
"""v2904 -- OBgE 300mL: 3 preserved real-source photo scenes + 2 fact frames.
No regeneration of pixel content, no old file replacement, no retail release.
"""
from pathlib import Path
from shutil import copyfile
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image
import json, copy

ROOT=Path("qa-review")
PRE=ROOT/"v2903-missha-BB-21-23-25-best-existing-source-option-QA"/"stock30-incremental-state-v2903.json"
OLD=ROOT/"v2854-missha30-obge300-recovered-existing-artwork-QA"/"pending-22"/"manifest.json"
NEW=ROOT/"v2888-obge300-highnative-official-merchant-source-candidates-QA"/"manifest.json"
OUT=ROOT/"v2904-obge300-three-photo-two-fact-5frame-internal-QA"
assert PRE.is_file() and OLD.is_file() and NEW.is_file() and not OUT.exists()
state=json.loads(PRE.read_text())
old=json.loads(OLD.read_text())
new=json.loads(NEW.read_text())
assert state["version"]=="v2903" and len(state["families"])==30
assert old["family"]=="pending-22" and len(old["slots"])==5
assert new["version"]=="v2888" and new["owned_inventory_original_capacity"]=="NOT_RECORDED"
qapath=OLD.parent
oldslots={s["slot"]:s for s in old["slots"]}
candidate=next(x for x in new["candidate_source_results"] if x["name"]=="SoonsuShopify-candid-angle")
assert candidate["status"]=="HIGH_NATIVE_SOURCE_SAVED_PENDING_PRODUCT_VISUAL_AND_RIGHTS"
assert candidate["original_pixels"]==[1000,1000]
arr=[
 {"slot":1,"role":"existing_full_bottle_600_native_cutout_visual",
  "path":str(qapath/oldslots[1]["file"]),"sha256":oldslots[1]["sha256"],
  "source_category":"reused_600_native_bottle","source_native_at_least_900":False},
 {"slot":2,"role":"preserved_1000native_distinct_diagonal_real_bottle",
  "path":candidate["QA_JPG"],"sha256":candidate["QA_JPG_SHA256"],
  "source_category":"merchant_photo_unknown_commercial_rights","source_native_at_least_900":True},
 {"slot":3,"role":"existing_beige_packshot_600_native_source",
  "path":str(qapath/oldslots[2]["file"]),"sha256":oldslots[2]["sha256"],
  "source_category":"reused_600_native_bottle","source_native_at_least_900":False},
 {"slot":4,"role":"existing_factual_300mL_product_name_card",
  "path":str(qapath/oldslots[3]["file"]),"sha256":oldslots[3]["sha256"],
  "source_category":"fact_only_brand_product_label_not_owned_stock","source_native_at_least_900":None},
 {"slot":5,"role":"existing_factual_300mL_10.14floz_capacity_card",
  "path":str(qapath/oldslots[4]["file"]),"sha256":oldslots[4]["sha256"],
  "source_category":"fact_only_brand_product_label_not_owned_stock","source_native_at_least_900":None}
]
OUT.mkdir(parents=True)
results=[]
for item in arr:
 src=Path(item["path"])
 blob=src.read_bytes()
 assert sha256(blob).hexdigest()==item["sha256"],"Source hash unexpectedly modified"
 with Image.open(src) as im: im.verify()
 with Image.open(src) as im:
  assert im.format=="JPEG" and im.size==(1080,1080),("bad archived JPG",src)
 dest=OUT/f"{item['slot']:02d}-OBGE300-SOURCE-EXACT-1080-INTERNAL-QA.jpg"
 copyfile(src,dest)
 assert sha256(dest.read_bytes()).hexdigest()==item["sha256"]
 assert dest.stat().st_size < 2_000_000
 results.append({**item,"saved_copy":str(dest),"bytes":dest.stat().st_size,
                 "source_bytes_preserved":True,"retail_approved":False})
assert len({x["sha256"] for x in results})==5
zpath=OUT/"OBGE300_three_photo_two_fact_5JPG_INTERNAL_QA_ONLY.zip"
with ZipFile(zpath,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
 for x in results:z.write(x["saved_copy"],arcname=Path(x["saved_copy"]).name)
with ZipFile(zpath) as z:
 assert len(z.namelist())==5 and z.testzip() is None
manifest={
 "version":"v2904","baseline":"v2903","family":"pending-22",
 "product":"OBgE Max Waterful Sun Cream SPF50+ PA++++ 300mL",
 "qa_JPG_count":5,"real_product_photo_slots":3,"factual_info_slots":2,
 "distinct_sha256_count":5,"new_product_image_pixels_rendered":0,
 "prior_source_JPGs_modified":0,
 "new_highnative_photo_reuses_existing_v2888_one":True,
 "old_jpg_600native_hard_quality_blocker_not_misrepresented_as_native1080":True,
 "real_owner_stock_capacity_record":"NOT RECORDED IN 2026-11-01 SNAPSHOT",
 "official_catalog_sku_is_300mL":True,
 "exact_owned_bottle_300mL_confirmed":False,
 "commercial_photo_reuse_permission_verified":False,
 "original_MK_logo_authenticated":False,
 "one_untested_FACE_BODY_claim_frame_5_excluded":True,
 "reused_exact_photo_scenes":results,
 "internal_QA_ZIP":str(zpath),
 "internal_QA_ZIP_sha256":sha256(zpath.read_bytes()).hexdigest(),
 "previous_11_sale_approved_families_protected":True,
 "previous_55_public_URLs_unchanged":True,"new_retail_approvals":0,
 "final_XLSX_shared":False,
 "next":"Owner must verify physical 300mL inventory plus commercial photo rights; native 600px photo bottleneck remains. This bundle is NOT for sales upload."
}
st=copy.deepcopy(state)
st["version"]="v2904";st["baseline"]="v2903"
fam=st["families"]["pending-22"]
fam["last_delta_version"]="v2904"
fam["release_status"]="THREE_REAL_PHOTOS_TWO_FACTS_JPG_QA_READY_HOLD_VOLUME_RIGHTS_NATIVE_600"
fam["latest_photo_QA_checkpoint"]="v2904 3 existing real product source photos (one previously archived 1000-native) + 2 fact slides byte-reused into five 1080 JPG and internal ZIP. Exact owned stock 300mL and rights HOLD, 2 old source native 600px lower fidelity."
fam["v2904_three_photo_two_fact_internal_ZIP"]=str(zpath)
fam["v2904_distinct_real_photo_scenes"]=3
fam["v2904_legacy_600_native_photo_scenes"]=2
st["new_sale_approvals"]=0;st["new_public_URLs"]=0;st["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2904.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2904","3_actual_photo_frames":3,"all_JPG":5,"new_pixels":0,
 "zip_sha256":manifest["internal_QA_ZIP_sha256"],"approved":0},ensure_ascii=False))
