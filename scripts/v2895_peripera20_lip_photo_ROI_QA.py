#!/usr/bin/env python3
"""v2895 / Actual peripera 26AD 20 shade lip-photo ROI QA, no artwork writes.
Previous global-image dHash produces false similarity on fixed layout, so
compare only the real lipstick swatch panel on the 20 preserved QA JPGs.
No customer-use rights or owned physical stock claims are inferred.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageChops, ImageStat
import json, copy, itertools, statistics
R=Path("qa-review")
INPUT=R/"v2880-peripera-26AD-twenty-original-lipswatch-plus-common-tube-QA"/"manifest.json"
BASE=R/"v2894-only-48-option-specific-JPG-technical-QA"/"manifest.json"
STATE=R/"v2894-only-48-option-specific-JPG-technical-QA"/"stock30-incremental-state-v2894.json"
OUT=R/"v2895-peripera20-lip-photo-ROI-similarity-check"
assert not OUT.exists() and all(p.is_file() for p in (INPUT,BASE,STATE))
m=json.loads(INPUT.read_text())
base=json.loads(BASE.read_text())
state=json.loads(STATE.read_text())
assert m["version"]=="v2880" and len(m["rows"])==20
assert base["version"]=="v2894" and base["technical_1080_jpeg_pass"]==48
assert state["version"]=="v2894" and len(state["families"])==30
data={}
for row in m["rows"]:
 shade=row["shade"]
 assert shade not in data
 p=Path(row["new_card_1080"])
 assert p.is_file() and sha256(p.read_bytes()).hexdigest()==row["card_SHA256"]
 with Image.open(p) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
  # Exact swatch area (right), exclude common product photo on left and captions.
  crop=im.convert("RGB").crop((565,324,991,779)).resize((96,96),Image.Resampling.LANCZOS)
 data[shade]={"source_sha":row["source_SHA256"],"card_sha":row["card_SHA256"],
              "image_path":str(p),"name_KO":row["brand_shade_name_KO"],"roi":crop}
assert len(data)==20
pairs=[]
for a,b in itertools.combinations(sorted(data),2):
 left,right=data[a],data[b]
 delta=ImageStat.Stat(ImageChops.difference(left["roi"],right["roi"])).mean
 dist=round(sum(delta)/3,4)
 pairs.append({"shades":[a,b],"mean_RGB_abs_diff":dist,
               "source_sha_equal":left["source_sha"]==right["source_sha"],
               "card_sha_equal":left["card_sha"]==right["card_sha"]})
ordered=sorted(pairs,key=lambda x:x["mean_RGB_abs_diff"])
same_source=sum(int(x["source_sha_equal"]) for x in pairs)
close=[x for x in ordered if x["mean_RGB_abs_diff"]<=4]
report={
 "version":"v2895","baseline":"v2894",
 "scope":"20 peripera 26AD exact shade 4g photographed lip region only",
 "prior_v2894_full_template_207_near_dhash_pairs_not_auto_used":True,
 "crop_box_pixels":[565,324,991,779],
 "metric":"unweighted mean per-channel absolute RGB difference across 96x96 ROI; not calibrated swatch colorimetry",
 "variants_checked":20,"unique_variant_source_sha_count":len(set(r["source_SHA256"] for r in m["rows"])),
 "pairs_checked":len(pairs),"same_source_SHA_pairs":same_source,
 "min_roi_RGB_diff":ordered[0]["mean_RGB_abs_diff"],
 "median_roi_RGB_diff":round(statistics.median(x["mean_RGB_abs_diff"] for x in pairs),4),
 "close_pairs_le4":len(close),
 "potential_duplicate_lip_scene_needs_human_review":close,
 "closest_30":ordered[:30],
 "new_images_created":0,"old_images_modified":0,"new_sale_approvals":0,
 "source_photo_rights_verified":False,"actual_owned_26AD_item_verified":False,
 "authentic_MK_logo_verified":False,"old_11_published_families_preserved":True,
 "old_55_public_URLs_preserved":True,"final_spreadsheet_shared":False,
 "followup":"Escalate only visually close lip swatches; never assume shared template means duplicate, no repeat downloads."
}
newstate=copy.deepcopy(state)
newstate["version"]="v2895";newstate["baseline"]="v2894"
newstate["families"]["pending-08"]["last_delta_version"]="v2895"
newstate["families"]["pending-08"]["latest_photo_QA_checkpoint"]="v2895 20 26AD lip photo ROI-specific analysis; false dHash template similarity filtered; physical edition and image license HOLD"
newstate["families"]["pending-08"]["release_status"]="LIP_REGION_QA_COMPLETE_HOLD_OWNED_26AD_AND_RIGHTS"
newstate["v2895_real_lip_ROI_pairs_reviewed"]=len(pairs)
newstate["v2895_near_lip_ROI_pairs"]=len(close)
newstate["v2895_generated_images"]=0
newstate["new_sale_approvals"]=0
newstate["new_public_URLs"]=0
newstate["final_spreadsheet_shared"]=False
OUT.mkdir(parents=True)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2895.json").write_text(json.dumps(newstate,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2895","shades":len(data),"pairs":len(pairs),"same_source":same_source,
                  "median_diff":report["median_roi_RGB_diff"],"near_pairs":len(close),"sales_approved":0},ensure_ascii=False))
