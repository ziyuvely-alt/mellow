#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
S=Path("v2427b-source");A=Path("v2430-source");O=Path("v2430b-output");O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
done=[]
# 1: EXACT observed wrong customer caption, change only label area below authentic source photo.
orig=S/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions/pending-10/SOURCE_01_363f13d61_EN_V2421C.jpg"
assert orig.exists()
with Image.open(orig) as input:
 im=input.convert("RGB")
 d=ImageDraw.Draw(im)
 # Original caption panel beige; touch y860..951, below photograph ending ~710.
 bg=im.getpixel((105,960))
 d.rectangle((64,860,997,944),fill=bg)
 d.text((70,877),"OBgE Perfect Cover Cushion 15 g",font=font(36,True),fill=(45,65,53))
 dst=O/"actual-sales-drafts/pending-10/OBGE_photo_caption_name_corrected_V2430b.jpg"
 dst.parent.mkdir(parents=True,exist_ok=True)
 im.save(dst,"JPEG",quality=94,optimize=True)
 done.append({"source":str(orig.relative_to(S)),"output":str(dst.relative_to(O)),"sha256":sha(dst),"reason":"Visible caption says Perfect Homme; correct project product name is Perfect Cover Cushion","status":"SALES_IMAGE_DRAFT","whitespace_rectangle_unresolved":True})
# 2: remove confirmed duplicate NET CONTENT / NET WEIGHT from actual V2430 info draft.
prior=A/"actual-sales-drafts/pending-10/OBGE_INFO_05_EN_copy_revised_V2430.jpg"
assert prior.exists()
with Image.open(prior) as input:
 im=input.convert("RGB");d=ImageDraw.Draw(im)
 bg=im.getpixel((540,755))
 d.rounded_rectangle((126,334,955,729),radius=22,fill=bg)
 for message,y,size,bold in [("15 g",430,80,True),("AVAILABLE SHADES",545,34,False),("1 Ivory   /   2 Beige   /   3 Sand",620,28,False)]:
  f=font(size,bold);bb=d.textbbox((0,0),message,font=f)
  d.text((540-(bb[2]-bb[0])//2,y),message,font=f,fill=(45,65,53))
 dest=O/"actual-sales-drafts/pending-10/OBGE_INFO_05_copy_deduplicated_V2430b.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 im.save(dest,"JPEG",quality=94,optimize=True)
 done.append({"source":str(prior.relative_to(A)),"output":str(dest.relative_to(O)),"sha256":sha(dest),"reason":"Visually observed duplicate NET CONTENT/NET WEIGHT headers; preserve outer NET CONTENT title and simplify inner panel","status":"SALES_IMAGE_DRAFT"})
for x in done:
 f=O/x["output"]
 with Image.open(f) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2000000
# Explicit first-hand image findings, NOT a false 156-frame human review.
findings=[
 {"group":"pending-01","image":"01_HERO_EN_V2422.jpg","status":"SHADE_CHART_REQUIRED","observed":"Contains shade 21 although excluded from Cover Lasting; circular shade icons and source panel require exact official evidence","do_not_publish":True},
 {"group":"pending-07","image":"01_HERO_EN_V2422.jpg","status":"SOURCE_QA_HOLD","observed":"Authentic retail package includes Korean printed marketing content; cannot erase package print; verify kit SKU and generation","do_not_publish":True},
 {"group":"pending-08","image":"01_HERO_EN_V2422.jpg","status":"SHADE_CHART_REQUIRED","observed":"Only a subset of 01–20 is visible, despite caption suggesting shades 01–20. Exact generation and comprehensive chart not verified","do_not_publish":True},
 {"group":"pending-10","image":"SOURCE_01_363f13d61_EN_V2421C.jpg","status":"CUTOUT_REVISION_REQUIRED","observed":"White rectangle around product and mismatching Perfect Homme caption; caption only corrected, white inset retained pending approved source","do_not_publish":True},
 {"group":"pending-02","image":"SOURCE_01_640302217_EN_V2421C.jpg","status":"SOURCE_QA_HOLD","observed":"White product studio background remains; source product photo and box exist, stock generation unverified","do_not_publish":True},
 {"group":"pending-04","image":"INV_01_3194e3273f_EN_V2421C.jpg","status":"SOURCE_QA_HOLD","observed":"Image contains apparent MK logo graphic; original MK binary not verified, therefore no release approval","do_not_publish":True},
 {"group":"pending-05","image":"SOURCE_01_041b164bb_EN_V2421C.jpg","status":"SOURCE_QA_HOLD","observed":"Set product photograph visible but kit-version and exact SKU photo match not yet verified","do_not_publish":True},
 {"group":"pending-06","image":"SOURCE_01_8053457df_EN_V2421C.jpg","status":"SOURCE_QA_HOLD","observed":"Retail packaging retains Korean print in genuine image; source generation and permission unresolved","do_not_publish":True}
]
report={"version":"2.4.30b","actual_image_edits_in_this_batch":2,"actual_edits_total_v2430_plus_v2430b":3,
 "active_sales_image_draft_latest":2,"retained_prior_version_but_superseded":"OBGE_INFO_05_EN_copy_revised_V2430.jpg",
 "distinct_product_families_modified":1,"genuinely_visually_opened_frames":len(findings),
 "frame_count_by_script_prior":156,"human_visual_qa_of_all_156":False,
 "new_official_shade_chart":0,"FINAL_QA_APPROVED":0,"rights_verified":0,
 "white_rectangle_resolved":False,"source_jpg_modified":0,"public_urls_mutated":0,
 "edits":done,"observed_image_findings":findings,"next":"Inspect 22 remaining family representative customer frames, then prioritize safe copy fixes; ensure official shade evidence and rights before promotion"}
(O/"v2430b_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("edits","observed_image_findings")},flush=True))
