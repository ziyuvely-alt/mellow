#!/usr/bin/env python3
"""v2445b patch four genuinely corrected caption JPEG bytes into v2444 QA-hold pool.
All other candidates preserve original source hashes and 4 known MK-badge images
remain quarantined. No output called final sales release.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,csv,zipfile
A=Path("prior-v2444"); B=Path("prior-v2445")
OUT=Path("v2445b-output");OUT.mkdir(exist_ok=True)
old=json.loads((A/"v2444_quarantine_and_reuse_manifest.json").read_text())
new=json.loads((B/"v2445_checkpoint.json").read_text())
assert old["candidate_JPGs_not_yet_commercial_approved"]==146
assert old["known_visual_defects_quarantined"]==4
assert len(new["new_frames"])==4
corrected={x["slot"]:x for x in new["new_frames"]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];keep=[];hold=[];fixed_count=0
for family in old["families"]:
 group=family["group_id"]
 for image in family["frames"]:
  slot=image["slot"]
  isquarantine=image["classification"]=="QUARANTINE_VISUAL_DEFECT"
  if group=="pending-25" and slot in corrected:
   ent=corrected[slot]
   src=B/ent["new_corrected_jpg"];expected=ent["new_sha256"]
   assert not isquarantine
   fixed_count+=1
   origin="v2445_new_caption_fix"
  else:
   src=A/image["file"];expected=image["sha256"]
   origin="v2444_byte_unchanged"
  assert src.is_file() and sha(src)==expected
  with Image.open(src) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080) and src.stat().st_size<2_000_000
  groupdir="quarantine-verified-MK-badges" if isquarantine else "146-QA-hold-candidate-images"
  target=OUT/groupdir/group/f"{slot:02d}_{src.name}"
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(src,target)
  assert sha(target)==expected
  row={"family":group,"slot":slot,"file":str(target.relative_to(OUT)),
   "sha256":expected,"disposition":"KNOWN_MK_BADGE_QUARANTINE" if isquarantine else "REUSABLE_ONLY_AFTER_FULL_APPROVAL",
   "byte_source":origin,"prior_image_reproduced":False,"sale_approved":False,
   "MK_rights_confirmed":False,"photo_rights_confirmed":False,"physical_stock_checked":False}
  rows.append(row)
  (hold if isquarantine else keep).append(target)
assert len(rows)==150 and len(keep)==146 and len(hold)==4 and fixed_count==4
report={
"version":"2.4.45b","sources":["production-assets-v2444-reviewed-146-and-quarantine-4","production-assets-v2445-four-bioheal-caption-corrections"],
"all_review_candidate_files_reconciled":150,"quarantined_bad_MK_logo_photos":4,
"QA_hold_candidate_files":146,"corrected_only_existing_BIOHEAL_slots":4,
"prior_531_source_JPG_unchanged":True,"old_55_published_URL_paths_changed":0,
"sales_sets_final_approved":0,"MK_logo_authenticity_or_rights_confirmed":0,
"commercial_photo_reuse_licenses_verified":0,
"all_150_frames_human_visual_review_done":False,"generated_or_fabricated_product_photo_count":0,
"critical_remaining":["Authentic MK logo PNG and actual permission","Peripera 01..20 shade source exact product generation","MISSHA 21 excluded from cover hero; official remaining shade swatches","OBgE cushion renewed packaging and shade-chart rights","200mL toner correct same-generation photo and rights","Individual product 5-frame visual QA for 30 groups not completed"],
"asset_rows":rows}
(OUT/"v2445b-resumable-checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with (OUT/"v2445b-150-image-QA-disposition.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for filename,files in [("v2445b-146-current-candidates-NOT_SALE_READY.zip",keep),("v2445b-4-logo-quarantined.zip",hold)]:
 with zipfile.ZipFile(OUT/filename,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,arcname=str(p.relative_to(OUT)))
  z.write(OUT/"v2445b-resumable-checkpoint.json",arcname="v2445b-resumable-checkpoint.json")
 with zipfile.ZipFile(OUT/filename) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
print(json.dumps({k:report[k] for k in ["version","QA_hold_candidate_files","quarantined_bad_MK_logo_photos","corrected_only_existing_BIOHEAL_slots","sales_sets_final_approved"]},ensure_ascii=False),flush=True)
