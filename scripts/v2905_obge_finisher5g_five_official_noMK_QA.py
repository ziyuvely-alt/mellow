#!/usr/bin/env python3
"""v2905 OBgE Oil Control Finisher 5g: curate FIVE actual archived scenes, NO
unverified MK badge, NO unsupported 36% pore reduction, NO model before-after.
Exact-byte copy: original clean 5g hero + four first-party catalog QA photos.
Commercial rights and actual owned inventory generation remain unverified.
"""
from pathlib import Path
from shutil import copyfile
from hashlib import sha1,sha256
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import json,copy

ROOT=Path("qa-review")
STATE=ROOT/"v2904-obge300-three-photo-two-fact-5frame-internal-QA"/"stock30-incremental-state-v2904.json"
SOURCE=ROOT/"v2807-two-official-single-item-product-photo-discovery"/"manifest.json"
PREV=ROOT/"v2772-goodal-obge-five-frame-photo-QA"/"pending-09"/"manifest.json"
OUT=ROOT/"v2905-obge-finisher5g-five-official-no-unverified-MK-internal-QA"
assert all(x.is_file() for x in (STATE,SOURCE,PREV)) and not OUT.exists()
st=json.loads(STATE.read_text())
official=json.loads(SOURCE.read_text())
prior=json.loads(PREV.read_text())
assert st["version"]=="v2904" and len(st["families"])==30
assert official["version"]=="v2807" and prior["family"]=="pending-09"
case=next(x for x in official["cases"] if x["family"]=="pending-09")
assert len(case["photos"])==9
hero=next(x for x in prior["frames"] if x["slot"]==1)
assert hero["scene"]=="actual compact alpha product hero"
# 1/3/4/7 refer to official archived gallery images (indexed 1..9).
# Exclude model before/after, unverified clinical 36% and face-model usage.
chosen=[
 {"slot":1,"role":"existing_true_alpha_open_5g_compact_hero",
  "path":hero["path"],"expected_git_blob":hero["source_git_blob_sha1"],
  "claim_review":"No extra efficacy claims in frame"},
 {"slot":2,"role":"brand_gallery_product_with_puff_and_texture",
  "official_index":1,"claim_review":"Product photo, not evidence of 5g owned SKU edition"},
 {"slot":3,"role":"brand_gallery_open_compact_two_views",
  "official_index":4,"claim_review":"Brand marketing phrase matte in one tap; retain only for internal QA pending claim authorization"},
 {"slot":4,"role":"brand_gallery_puff_product_handling",
  "official_index":7,"claim_review":"Application instruction; verify package and approved local claim wording"},
 {"slot":5,"role":"brand_gallery_skin_texture_questions",
  "official_index":3,"claim_review":"Skin texture examples only, not verified evidence of efficacy"},
]
for item in chosen:
 if "official_index" in item:
  o=case["photos"][item["official_index"]-1]
  item["path"]=str(SOURCE.parent/o["file"])
  item["expected_SHA256"]=o["sha256"]
assert len({x["path"] for x in chosen})==5
# Require all five inputs and source hashes before allocating outputs.
for item in chosen:
 path=Path(item["path"])
 assert path.is_file(),("Missing QA archive",path)
 b=path.read_bytes()
 if "expected_SHA256" in item:assert sha256(b).hexdigest()==item["expected_SHA256"]
 if "expected_git_blob" in item:assert sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()==item["expected_git_blob"]
 with Image.open(path) as im:
  im.verify()
 with Image.open(path) as im:
  assert im.format=="JPEG" and im.size==(1080,1080),str(path)
OUT.mkdir(parents=True)
results=[]
for item in chosen:
 src=Path(item["path"])
 dst=OUT/f"{item['slot']:02d}-OBGE-OIL-CONTROL-5G-EXACT-ARCHIVE-QA.jpg"
 copyfile(src,dst)
 assert src.read_bytes()==dst.read_bytes()
 assert dst.stat().st_size<2_000_000
 results.append({**item,"copy":str(dst),"sha256":sha256(dst.read_bytes()).hexdigest(),
                 "bytes":dst.stat().st_size,"old_source_file_changed":False,
                 "sale_approved":False})
zpath=OUT/"OBGE_Oil_Control_Finisher5g_5JPG_INTERNAL_QA_NOT_PUBLIC.zip"
with ZipFile(zpath,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
 for item in results:z.write(item["copy"],arcname=Path(item["copy"]).name)
with ZipFile(zpath) as z:
 assert z.testzip() is None and len(z.namelist())==5
m={
 "version":"v2905","baseline":"v2904","family":"pending-09",
 "product":"OBgE Oil Control Finisher 5g single compact",
 "actual_5g_product_photo_scenes_selected":4,
 "contextual_skin_questions_photo_scenes_selected":1,
 "all_five_JPGs_actual_existing_source_byte_identical":True,
 "unverified_legacy_MK_logo_frames_reused":0,
 "unlicensed_model_before_after_frames_reused":0,
 "unsubstantiated_36percent_clinical_frame_reused":0,
 "original_images_mutated":0,"rendered_new_pixels":0,
 "original_photo_commercial_reuse_rights_verified":False,
 "actual_user_owned_5g_packaging_generation_verified":False,
 "original_MK_logo_authenticated":False,
 "marketing_claims_and_skin_use_photo_rights_final_review_required":True,
 "frames":results,"internal_zip_path":str(zpath),
 "internal_zip_sha256":sha256(zpath.read_bytes()).hexdigest(),
 "previous_11_approved_groups_preserved":True,
 "previous_55_verified_public_URLs_preserved":True,
 "new_commercial_sale_approvals":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False
}
updated=copy.deepcopy(st)
updated["version"]="v2905";updated["baseline"]="v2904"
f=updated["families"]["pending-09"]
f["last_delta_version"]="v2905"
f["release_status"]="FIVE_REAL_OFFICIAL_PHOTO_QA_ARCHIVED_HOLD_RIGHTS_OWNED_EDITION"
f["latest_photo_QA_checkpoint"]="v2905 five archived photo scenes (4 product/puff scenes + 1 contextual skin photo) copied from 5g hero and official gallery, 0 old unverified MK/model before-after/36% ads. No new pixels; stock edition/rights/some claims HOLD."
f["v2905_five_real_photo_internal_zip"]=str(zpath)
updated["new_sale_approvals"]=0
updated["new_public_URLs"]=0
updated["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2905.json").write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2905","frames":5,"source_shas_confirmed":True,"new_pixels":0,
                  "new_retail_approvals":0,"zip":str(zpath)},ensure_ascii=False))
