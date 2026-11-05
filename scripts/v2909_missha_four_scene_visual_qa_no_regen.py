#!/usr/bin/env python3
"""v2909: visual QA and photo reuse audit for v2908 four new first-party MISSHA references.
Produces ONLY internal review diagnostics. No existing bytes are overwritten, and no release.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, time

ROOT=Path("qa-review")
BASE=ROOT/"v2908-missha-pdrn-twofamily-distinct-official-photo-scenes-QA"
OUT=ROOT/"v2909-missha-pdrn-v2908-four-photo-visual-and-duplicate-QA"
MAN=json.loads((BASE/"manifest.json").read_text())
STATE=json.loads((BASE/"stock30-incremental-state-v2908.json").read_text())
assert MAN["version"]=="v2908" and STATE["version"]=="v2908"
assert len(STATE["families"])==30 and not OUT.exists()

CASES={
 "pending-13":{
  "name":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
  "prior_clean":"qa-review/v2899-missha-serum30-clean-hero-existing-4scene-internal-QA/01-ARCHIVED-EXACT-JPG-INTERNAL-QA.jpg",
  "prior_sha":"f8e426b018c506e65559c4eb0384bf04beec5821737356b04d2a2a0e65ce2fbd",
  "review":[
   {"position":1,"visual_status":"SECONDARY_ONLY","scene":"Dropper, close bottle and large KEY BENEFITS promotional overlay; top and bottle bottom cropped","visible_volume":"30 mL","main_hero":False,"claim_copy":"REVIEW_REQUIRED","reason":"Claim copy is not cleared for shop reuse; full package is cut off"},
   {"position":2,"visual_status":"PRIORITY_CLEAN_PHOTO_CANDIDATE","scene":"Single fully visible red serum dropper bottle; white background with circular gel texture","visible_volume":"30 mL","main_hero":True,"claim_copy":"NO_EXTRA_CLAIMS_VISIBLE","reason":"Full 30mL label, clean composition; stock edition and image rights still unverified"}
  ]},
 "pending-14":{
  "name":"MISSHA PDRN NAD+ Firming Repair Cream 70mL",
  "prior_clean":"qa-review/v2907-missha-pdrn-firstparty-twofamily-source-photo-QA/pending-14/01-manufacturer-1080-INTERNAL-QA.jpg",
  "prior_sha":"b27452c32c5bd1acbf4d3cf6fe2ee193c5a1e55bb358af0de85437b91d3307ec",
  "review":[
   {"position":1,"visual_status":"SECONDARY_ONLY","scene":"Open jelly cream jar with magnifying ring and large KEY BENEFITS promotional overlay","visible_volume":"70 mL","main_hero":False,"claim_copy":"REVIEW_REQUIRED","reason":"Promotional benefit copy, obstructed package and ring graphic"},
   {"position":2,"visual_status":"PRIORITY_CLEAN_PHOTO_CANDIDATE","scene":"Single full red cream jar with white cap and red gel texture behind; white background","visible_volume":"70 mL","main_hero":True,"claim_copy":"NO_EXTRA_CLAIMS_VISIBLE","reason":"Full jar label reads 70 mL on this image; package/rights and local edition hold"}
  ]}
}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(sz):
 try:return ImageFont.truetype(FONT,sz)
 except:return ImageFont.load_default()
def dhash(im):
 gray=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def distance(a,b):return sum(x!=y for x,y in zip(a,b))
def load_image(path):
 with Image.open(path) as im:
  im.load()
  return ImageOps.exif_transpose(im).convert("RGB")
def draw_review(family,label,photos,qa_results):
 W,H=1080,1080
 can=Image.new("RGB",(W,H),"#f7f7f8");d=ImageDraw.Draw(can)
 d.text((30,22),f"{family.upper()}  |  v2909 INTERNAL PHOTO QA",font=font(28),fill="#222222")
 d.text((30,66),label,font=font(23),fill="#393939")
 cols=[(25,"PRIOR SELECTED",(photos[0])),(375,"NEW CLAIM OVERLAY",(photos[1])),(725,"NEW CLEAN PHOTO",(photos[2]))]
 for x,cap,img in cols:
  d.rounded_rectangle((x,138,x+330,856),radius=12,fill="white",outline="#dadada",width=2)
  img=ImageOps.contain(img,(310,590),Image.Resampling.LANCZOS)
  can.paste(img,(x+165-img.width//2,158+(590-img.height)//2))
  d.text((x+10,781),cap,font=font(16),fill="#353535")
  d.text((x+10,812),"NOT APPROVED FOR RETAIL",font=font(14),fill="#9f3232")
 d.text((30,890),"Manufacturer source review; comparison only. NOT a listing image.",font=font(20),fill="#333333")
 d.text((30,931),"Stock edition / photo rights / brand mark: PENDING",font=font(20),fill="#9f3232")
 d.text((30,965),f"New clean vs prior selected dHash distance: {qa_results['clean_to_old_dhash_hamming']}/64",font=font(18),fill="#333333")
 return can

OUT.mkdir(parents=True)
records=[]
for c in MAN["families"]:
 family=c["family"]
 assert family in CASES and c["new_source_count"]==2
 conf=CASES[family]
 prior_path=Path(conf["prior_clean"])
 assert prior_path.is_file() and sha256(prior_path.read_bytes()).hexdigest()==conf["prior_sha"]
 prior=load_image(prior_path)
 current=[]
 for i,item in enumerate(c["new_originals"]):
  p=Path(item["reference_JPG"])
  assert p.is_file() and sha256(p.read_bytes()).hexdigest()==item["reference_sha256"]
  with Image.open(p) as im:
   assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
  photo=load_image(p)
  x=dict(conf["review"][i])
  x.update({"source_url":item["source_url"],"original_path":item["raw_original_path"],"reference_JPG":item["reference_JPG"],
            "reference_SHA256_verified":True,"reference_native_1080_sRGB_review":True,"manufacturer_original_format_validated_v2908":True,
            "commercial_rights_verified":False,"actual_held_KR_stock_edition_verified":False,
            "authentic_original_MK_logo_verified":False,"sale_approved":False})
  current.append((photo,x))
 a=dhash(prior); b=dhash(current[0][0]); z=dhash(current[1][0])
 metric={"claim_to_old_dhash_hamming":distance(a,b),"clean_to_old_dhash_hamming":distance(a,z),"claim_to_clean_dhash_hamming":distance(b,z),
         "threshold_under_6_requires_manual_visual_duplicate_review":True,
         "dhash_is_not_proof_of_distinct_scene":True}
 for photo,x in current:
  dist=distance(a,dhash(photo))
  x["dhash_distance_from_previous_hero"]=dist
  x["dhash_near_duplicate_alert"]=dist<6
  x["reuse_decision"]="REFERENCE_ONLY_NOT_RELEASED"
 out=OUT/(family+"-three-source-visual-comparison-INTERNAL-QA.jpg")
 canvas=draw_review(family,conf["name"],[prior,current[0][0],current[1][0]],metric)
 canvas.save(out,"JPEG",quality=90,optimize=True,subsampling=0)
 with Image.open(out) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
 assert out.stat().st_size<2_000_000
 chosen=current[1][1]
 records.append({"family":family,"product":conf["name"],"compared_sources":3,"new_sources_visual_reviewed":2,
    "selected_clean_reference":chosen["reference_JPG"],"selected_clean_reference_sha256":c["new_originals"][1]["reference_sha256"],
    "selected_clean_reference_is_new_bytes":c["new_originals"][1]["reference_sha256"]!=conf["prior_sha"],
    "prior_clean_reference":conf["prior_clean"],"review": [x for _,x in current],
    "dhash_crosschecks":metric,"visual_comparison_path":str(out),
    "retail_status":"INTERNAL_PHOTO_SELECTION_ONLY_RIGHTS_AND_ACTUAL_STOCK_HOLD"})
 st=STATE["families"][family]
 st.update({"last_delta_version":"v2909",
   "release_status":"TWO_NEW_SCENES_VISUAL_REVIEWED_ONE_CLEAN_CANDIDATE_HELD_RIGHTS_STOCK",
   "v2909_clean_candidate_reference":chosen["reference_JPG"],
   "v2909_marketing_claim_scene_rejected_as_hero":True,
   "v2909_stock_label_volume_visual_seen":conf["review"][1]["visible_volume"],
   "v2909_comparison_photo":str(out),
   "latest_photo_QA_checkpoint":"v2909: 2 v2908 manufacturer scenes visually classified, one clean full-package reference prioritized, one promotional-claims frame NOT HERO; prior selected reference compared. Retail permission and physical stock edition remain unconfirmed.",
   "sale_approved":False})
report={
 "version":"v2909","baseline":"v2908","generated_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "original_photo_sources_new_this_step":0,"new_original_source_photos_reused_without_modifying":4,
 "new_1080_internal_visual_comparisons_created":2,"new_sales_JPG_images_approved":0,
 "new_commercial_release_approvals":0,"new_published_URLs":0,
 "completed_old_11_families_untouched":True,"verified_old_55_public_URLs_untouched":True,
 "previous_QA_images_modified":0,"only_new_qa_review_subfolder_written":True,
 "final_spreadsheet_shared":False,"cases":records,
 "next_unblocked_work":"Inspect other pending families with existing verified originals; do not republish until actual physical stock, rights and authentic MK logo verification."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
STATE["version"]="v2909";STATE["baseline"]="v2908";STATE["new_sales_approvals"]=0;STATE["new_public_URLs"]=0;STATE["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2909.json").write_text(json.dumps(STATE,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2909","visual_checks":4,"comparison_JPGs":2,
  "family_clean_candidates":[r["family"] for r in records],"new_sales_approvals":0},ensure_ascii=False))
