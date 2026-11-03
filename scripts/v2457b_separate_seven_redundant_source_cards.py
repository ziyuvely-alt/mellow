#!/usr/bin/env python3
"""v2457b: physical QA-filter of 86 earlier source JPGs.
Human visually inspected all nine pHash-suggested pairs. Seven older, information-
redundant or unsupported generation frames are quarantined. Retain distinct facts.
No JPEG regeneration, no original deletion, no workbook, no publication.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
SRC=Path("prior-v2446b")
AUD=Path("prior-v2457")
OUT=Path("v2457b-output");OUT.mkdir(exist_ok=True)
j=json.loads((SRC/"v2446b_logo_quarantine_manifest.json").read_text())
q=json.loads((AUD/"v2457-86-other-JPG-source-QA.json").read_text())
r=[x for x in j["files"] if x["disposition"]=="RIGHTS_AND_CONTENT_REVIEW_HOLD"]
assert len(r)==86 and q["current_older_JPGs_sha_verified"]==86
# All were opened individually in relevant pair comparisons; remove one redundant OLD version only.
reject={
 ("pending-01",4):"Same Magic Cushion edition card as corrected slot 1, but old ornamental circle overlaps headline",
 ("pending-05",5):"Generic CLIO cushion card superseded by more exact MAIN + REFILL / Founwear slot 1",
 ("pending-10",5):"Same Perfect Cover Cushion 15 g contents as corrected slot 1; old circle overlaps central card",
 ("pending-13",4):"Same Firming Repair Serum 30 mL card as corrected slot 1; old circle overlaps 30 mL title",
 ("pending-19",3):"Same Goodal dual-function info as corrected slot 1, contains unverified 25AD generation phrase",
 ("pending-23",3):"Same Pore Zero features as slot 1 with redundant original circle; corrected clean card preferred",
 ("pending-23",4):"Same Pore Zero 50 mL content as slot 2 in different layout, adds no new distinct customer facts"
}
assert len(reject)==7
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
kept=[];held=[];rows=[]
for x in r:
 src=SRC/x["image_path"]
 assert src.is_file() and sha(src)==x["SHA256"]
 with Image.open(src) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080) and src.stat().st_size<2_000_000
 key=(x["group_id"],x["slot"])
 reason=reject.get(key)
 dst=OUT/("07-content-duplicate-older-version-HOLD" if reason else "79-retained-rights-and-content-QA-HOLD")/x["group_id"]/f"{x['slot']:02d}_{src.name}"
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,dst)
 assert sha(dst)==x["SHA256"]
 item={"group_id":x["group_id"],"slot":x["slot"],"new_copy_file":str(dst.relative_to(OUT)),
 "sha256":x["SHA256"],"disposition":"OLDER_REDUNDANT_FRAME_QUARANTINE" if reason else "RETAIN_AS_UNAPPROVED_CANDIDATE",
 "reason":reason or "No redundant composition confirmed; commercial rights, exact package and independent visual QA still pending",
 "commercial_rights_verified":False,"sale_approved":False}
 rows.append(item);(held if reason else kept).append(dst)
assert len(kept)==79 and len(held)==7 and len(rows)==86
report={
 "version":"2.4.57b","previous":"production-assets-v2457-86-source-image-qa",
 "historical_source_archive":"production-assets-v2446b-logo-64-quarantine-86-hold",
 "JPGs_sha256_and_1080x1080_verified":86,
 "older_redundant_content_frames_isolated":len(held),"retained_not_approved_JPG":len(kept),
 "nine_perceptual_candidate_pairs_directly_visually_reviewed":True,
 "non_duplicate_pairs_retained":[{"group":"pending-08","slots":[4,5],"reason":"Shade range and net content convey distinct facts; shade range itself remains generation QA hold"},
  {"group":"pending-20","slots":[3,5],"reason":"How-to-use instructions and NIACINAMIDE card are distinct; ingredient claim itself still source-verification hold"}],
 "identity_warning":{"group":"pending-21","slot":4,"interpretation":"Low edge count caused by wide clean white background and small yellow real product tube, not proof of blur","QA":"PHOTO_VISIBLE_BUT_EDITION_AND_REUSE_RIGHTS_UNVERIFIED"},
 "no_old_531_JPG_mutations":True,"no_55_public_URL_changes":True,
 "new_JPG_rendered":0,"new_approved_5_or_6_frame_sets":0,
 "XLSX_or_spreadsheets_created_or_shared":False,
 "files":rows,
 "next":[
  "Retain exact bytes, do not recreate seven redundant cards",
  "Find distinct real photo or source-backed factual content for low-card-count groups rather than padding with repeated 5-card art",
  "Official same-edition color sources, physical stock and photo rights still required before publication"
 ]}
(OUT/"v2457b-final-86frame-QA-disposition.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
for name,files in [("v2457b_79_retained_UNAPPROVED_original_JPGs.zip",kept),
                   ("v2457b_07_redundant_versions_QUARANTINE.zip",held)]:
 with zipfile.ZipFile(OUT/name,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zip:
  for file in files:zip.write(file,arcname=str(file.relative_to(OUT)))
  zip.write(OUT/"v2457b-final-86frame-QA-disposition.json",arcname="v2457b-final-86frame-QA-disposition.json")
 with zipfile.ZipFile(OUT/name) as z:
  assert len(z.namelist())==len(files)+1 and z.testzip() is None
print(json.dumps({"version":"2.4.57b","input":86,"retained":len(kept),"redundant_quarantined":len(held),"previous_QA_recreated":False,"XLSX":False}),flush=True)
