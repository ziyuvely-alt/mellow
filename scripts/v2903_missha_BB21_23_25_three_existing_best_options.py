#!/usr/bin/env python3
"""v2903: curate exactly three source-specific old gold-pump MISSHA BB shade QA files.
Reuses v2902 new 21, v2780 accurate old 23, v2897 new 25. Reject v2902
23 source with distorted small lettering. Byte-preserving copy only, NO
new sales release; no old 5-card photo modification or unsupported MK logo.
"""
from pathlib import Path
from shutil import copyfile
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,copy

ROOT=Path("qa-review")
PRE=ROOT/"v2902-missha-BB-21-23-two-independent-native-merchants-QA"/"stock30-incremental-state-v2902.json"
M21=ROOT/"v2902-missha-BB-21-23-two-independent-native-merchants-QA"/"manifest.json"
M25=ROOT/"v2897-missha-bb25-legacy-goldpump-new-independent-source-QA"/"manifest.json"
OLD23=ROOT/"v2780-four-unfinished-missha-obge-photo-first-QA"/"pending-03"/"01-real-product-cutout-prior-QA.jpg"
OUT=ROOT/"v2903-missha-BB-21-23-25-best-existing-source-option-QA"
assert PRE.exists() and M21.exists() and M25.exists() and OLD23.exists()
assert not OUT.exists()
st=json.loads(PRE.read_text())
m=json.loads(M21.read_text())
m25=json.loads(M25.read_text())
assert st["version"]=="v2902" and m["version"]=="v2902" and m25["version"]=="v2897"
assert len(st["families"])==30
shade21=next(x for x in m["results"] if x["shade"]=="21")
shade23=next(x for x in m["results"] if x["shade"]=="23")
assert shade21["qa_JPG_1080"] and shade23["qa_JPG_1080"]
files=[
 {"shade":"21","stock_source_index":8,"sales_from_20261101_snapshot":53,"label":"Light Beige",
  "source":shade21["qa_JPG_1080"],"expected_sha256":shade21["qa_JPG_sha256"],
  "provenance":"v2902 separate 1200px merchant photo; visible printed No.21, legacy gold-pump",
  "visual_label_status":"NO_21_VISIBLE_SMALL_TEXT_REVIEW_NOT_COMPLETE"},
 {"shade":"23","stock_source_index":9,"sales_from_20261101_snapshot":45,"label":"Natural Beige",
  "source":str(OLD23),"expected_sha256":None,
  "provenance":"v2780 existing 1080 No.23 gold pump; v2902 different seller candidate disqualified due suspect small-print legibility",
  "visual_label_status":"NO_23_VISIBLE_OLD_GOOD_REFERENCE_RETAINED"},
 {"shade":"25","stock_source_index":10,"sales_from_20261101_snapshot":25,"label":"Warm Beige",
  "source":m25["new_internal_1080_JPG"],"expected_sha256":m25["new_internal_1080_JPG_sha256"],
  "provenance":"v2897 new independent 1024px merchant photo No.25 gold pump, no legacy left-side ghost",
  "visual_label_status":"NO_25_VISIBLE_CLEAN_BACKGROUND"}
]
OUT.mkdir(parents=True)
new=[]
for x in files:
 src=Path(x["source"])
 data=src.read_bytes()
 digest=sha256(data).hexdigest()
 if x["expected_sha256"] is not None:assert digest==x["expected_sha256"]
 with Image.open(src) as im: im.verify()
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080),("not actual archived 1080 JPEG",x["shade"])
 dst=OUT/f"MISSHA_BB_Legacy_No{x['shade']}_OPTION_QA_NOT_FOR_PUBLIC.jpg"
 assert not dst.exists()
 copyfile(src,dst)
 assert sha256(dst.read_bytes()).hexdigest()==digest
 new.append({**x,"selected_copy":str(dst),"sha256":digest,"bytes":dst.stat().st_size,
    "original_image_bytes_unchanged":True,"sale_approved":False,
    "source_photo_usage_rights_verified":False,"physical_stock_edition_confirmed":False})
# A pure comparison contact board is NOT product listing media. No color alteration
# of source images, titles are external to the original photos.
sheet=Image.new("RGB",(1656,640),"white")
for idx,x in enumerate(new):
 with Image.open(x["selected_copy"]) as im:
  im.load()
  small=ImageOps.contain(im.convert("RGB"),(520,520),Image.Resampling.LANCZOS)
  sheet.paste(small,(16+552*idx+(520-small.width)//2,12+(520-small.height)//2))
 from PIL import ImageDraw
 d=ImageDraw.Draw(sheet)
 d.text((32+552*idx,545),"No."+x["shade"]+" | QA SOURCE ONLY",fill="#262626")
contact=OUT/"v2903-N21-N23-N25-three-verified-option-photos-contact-QA.jpg"
sheet.save(contact,"JPEG",quality=90,optimize=True)
zpath=OUT/"MISSHA_BB_N21_N23_N25_SOURCE_QA_3JPG_NOT_FOR_PUBLIC.zip"
with ZipFile(zpath,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
 for x in new:z.write(x["selected_copy"],arcname=Path(x["selected_copy"]).name)
with ZipFile(zpath) as z:
 assert z.testzip() is None and len(z.namelist())==3
manifest={
 "version":"v2903","baseline":"v2902","family":"pending-03",
 "item":"MISSHA M Perfect Cover BB Cream legacy gold-pump 50mL",
 "three_exact_shade_1080_JPGs_copied_from_existing_without_pixel_change":3,
 "shades":[21,23,25],"source_images":new,
 "discarded_mbeautyplus_23_source":shade23["qa_JPG_1080"],
 "discard_reason":"printed small English lettering appears distorted/garbled on direct visual comparison; NOT a safe proof for authentic Korean stock",
 "source_23_recovered_from_existing_v2780":True,
 "new_source_photos_downloaded":0,"new_product_image_pixels_synthesized":0,
 "new_photo_frames_byte_copied":3,
 "source_photo_licenses_confirmed":False,"owned_stock_specific_generation_verified":False,
 "actual_original_MK_logo_authenticated":False,
 "contact_path":str(contact),"ZIP_path":str(zpath),
 "zip_SHA256":sha256(zpath.read_bytes()).hexdigest(),
 "previous_commercial_approved_groups_preserved":11,"previous_public_image_URLs_preserved":55,
 "old_source_artwork_modified":False,"new_retail_approvals":0,"final_spreadsheet_shared":False,
 "next":"Maintain 3 valid shade-specific internal reference heroes. Need rights-cleared source original, actual physical stock edition and authentic original MK before sale. Do not use MBeautyPlus distorted No23."
}
newState=copy.deepcopy(st)
newState["version"]="v2903";newState["baseline"]="v2902"
f=newState["families"]["pending-03"]
f["last_delta_version"]="v2903"
f["release_status"]="THREE_SHADE_SPECIFIC_SOURCE_QA_3JPG_ARCHIVED_HOLD_OWNER_RIGHTS_MK"
f["latest_photo_QA_checkpoint"]="v2903 N21 v2902, N23 trusted prior v2780, N25 v2897 3 distinct existing 1080 QA JPG copied with hashes; v2902 N23 distorted product label rejected. Rights/physical owned generation/MK hold."
f["v2903_three_shade_QA_ZIP"]=str(zpath)
f["v2903_bad23_new_source_quarantined"]=True
newState["new_sale_approvals"]=0;newState["new_public_URLs"]=0
newState["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2903.json").write_text(json.dumps(newState,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2903","three_shades":[x["shade"] for x in new],
 "sha_verified":True,"discarded":"v2902 No23","zip":str(zpath),
 "new_approvals":0},ensure_ascii=False))
