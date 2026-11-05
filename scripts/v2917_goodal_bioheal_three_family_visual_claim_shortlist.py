#!/usr/bin/env python3
"""v2917: non-destructive human visual QA of 8 new brand firstparty photos:
GOODAL advanced cream six; BIOHEAL BOH serum and cream one each.
Add only source-eligible photos, not claims/before-after slides, and don't rename SKUs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from hashlib import sha256
import json,time

QA=Path("qa-review")
PRE=QA/"v2916-goodal-cream50-eyecream-official-media-gallery-only-QA"
B=QA/"v2915-biohealboh-two-firstparty-hk-source-and-cream-name-discrepancy-QA"
C=QA/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
OUT=QA/"v2917-threefamily-official-photo-visual-claim-review-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2916.json").read_text(encoding="utf-8"))
goodal=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
boh=json.loads((B/"manifest.json").read_text(encoding="utf-8"))
v2912=json.loads((C/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2916" and len(state["families"])==30
prev={x["family"]:x for x in v2912["family_results"]}
g19=next(x for x in goodal["results"] if x["family"]=="pending-19")
assert len(g19["images"])==6
b24=next(x for x in boh["results"] if x["family"]=="pending-24")
b25=next(x for x in boh["results"] if x["family"]=="pending-25")
def fnt(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def grab(path,expected):
 p=Path(path)
 assert p.is_file()
 b=p.read_bytes()
 assert sha256(b).hexdigest()==expected
 with Image.open(p) as image:
  image.load(); assert image.format=="JPEG" and image.size==(1080,1080)
  return ImageOps.exif_transpose(image).convert("RGB")
def make_sheet(name,photos,notes):
 canvas=Image.new("RGB",(1080,1080),"#f5f5f6");d=ImageDraw.Draw(canvas)
 d.text((25,19),name+" | v2917 RETAIL PRE-FLIGHT QA",font=fnt(29),fill="#252525")
 d.text((25,61),"PRODUCT RIGHTS, ACTUAL KR STOCK, BRAND MARK: NOT CLEARED",font=fnt(17),fill="#a43c3c")
 for i,(im,label) in enumerate(zip(photos[:5],notes[:5])):
  col=i%3;row=i//3;x=24+col*349;y=115+row*444
  d.rounded_rectangle((x,y,x+330,y+420),radius=12,fill="white",outline="#cccccc",width=2)
  fit=ImageOps.contain(im,(314,324),Image.Resampling.LANCZOS)
  canvas.paste(fit,(x+165-fit.width//2,y+8+(324-fit.height)//2))
  d.text((x+12,y+348),label[:30],font=fnt(15),fill="#244839")
  d.text((x+12,y+385),"REFERENCE NOT SALE",font=fnt(14),fill="#a33a3a")
 for j in range(len(photos),5):
  col=j%3;row=j//3;x=24+col*349;y=115+row*444
  d.rounded_rectangle((x,y,x+330,y+420),radius=12,fill="white",outline="#dddddd",width=2)
  d.text((x+28,y+200),"NO NEW VERIFIED PHOTO",font=fnt(15),fill="#9f4646")
 d.text((24,1030),"This review contact is NOT a customer-facing marketplace photo.",font=fnt(16),fill="#666666")
 return canvas

OUT.mkdir(parents=True)
goodal_decisions={
 1:("SELECT_CLEAN_REFERENCE","Goodal 50mL Alpha jar with cream smear; clean promotional-free photo, volume and physical stock unresolved"),
 2:("HOLD_PROMOTIONAL_CLAIM","Faster visible results headline; promotional unverified claim"),
 3:("REJECT_CLAIM_SCIENCE","3.5x stronger and comparative illustration claim, not for retail"),
 4:("REJECT_CLINICAL_PERCENT","50.1/29.7/39.6/7.54% clinical percentage overlays"),
 5:("REJECT_BEFORE_AFTER_PERSON","Before after facial pigment photos; model/claims rights absent"),
 6:("HOLD_INGREDIENT_MARKETING","High-potency active ingredients advertising overlay; not product photograph")
}
goodal_photos=[]
g19_reviews=[]
for i,z in enumerate(g19["images"],1):
 img=grab(z["reference_path"],z["reference_sha256"])
 verdict,description=goodal_decisions[i]
 g19_reviews.append({"frame":i,"source_path":z["reference_path"],"sha256":z["reference_sha256"],
  "verdict":verdict,"visual_reason":description,"sale_approved":False,
  "claim_cleared":False,"physical_25AD_edition_verified":False,"reuse_rights":False})
 if verdict=="SELECT_CLEAN_REFERENCE":goodal_photos.append((img,"ONE CLEAN ALPHA JAR PHOTO"))
g19sheet=OUT/"pending-19-v2916-official-six-photo-claims-screen-INTERNAL-QA.jpg"
# Contact should show all six original references for transparent rejected sources, not just selected.
claim_canvas=Image.new("RGB",(1080,1080),"#f6f6f6");draw=ImageDraw.Draw(claim_canvas)
draw.text((24,18),"PENDING-19 | GOODAL 6 BRAND SCENES v2917",font=fnt(28),fill="#282828")
draw.text((24,59),"ONE CLEAN / FIVE CLAIMS OR MODEL PHOTOS HELD",font=fnt(18),fill="#a33939")
for i,x in enumerate(g19_reviews):
 img=grab(x["source_path"],x["sha256"])
 col=i%3;row=i//3;x0=20+col*352;y0=110+row*435
 draw.rounded_rectangle((x0,y0,x0+337,y0+414),radius=10,fill="white",outline="#dddddd",width=2)
 fit=ImageOps.contain(img,(319,321),Image.Resampling.LANCZOS)
 claim_canvas.paste(fit,(x0+168-fit.width//2,y0+10+(321-fit.height)//2))
 label="SELECT CLEAN" if x["verdict"]=="SELECT_CLEAN_REFERENCE" else "HOLD/EXCLUDE"
 draw.text((x0+12,y0+355),label,font=fnt(17),fill="#226344" if i==0 else "#9d2c2c")
 draw.text((x0+12,y0+387),x["verdict"][:31],font=fnt(12),fill="#555555")
draw.text((20,1012),"NO PUBLIC PHOTO USE UNTIL EXACT STOCK EDITION AND RIGHTS ARE VERIFIED",font=fnt(17),fill="#a33939")
claim_canvas.save(g19sheet,"JPEG",quality=88,optimize=True,subsampling=0)
assert g19sheet.stat().st_size<2_000_000

case_results=[]
case_results.append({"family":"pending-19","new_firstparty_originals_inspected":6,
  "new_clean_product_photo_candidates":1,"new_brand_promo_hold_count":5,
  "selected_reference_path":g19_reviews[0]["source_path"],
  "visual_decisions":g19_reviews,"new_qa_visual_sheet":str(g19sheet),
  "existing_legacy_five_scenes_preserved":True,
  "stock_25AD_global_edition_verified":False,
  "sale_approved":False})
state["families"]["pending-19"].update({"last_delta_version":"v2917",
 "release_status":"ONE_CLEAN_ALPHA_SOURCE_SELECTED_FIVE_CLAIM_SCENES_EXCLUDED_HOLD_STOCK_RIGHTS",
 "v2917_clean_from_new_six":1,"v2917_unverified_claim_sources":5,
 "v2917_qa_visual_sheet":str(g19sheet),
 "latest_photo_QA_checkpoint":"v2917 manually classified 6 firstparty sources: clean product jar 1, 5 promo/claims/before-after held; existing 5-photo batch preserved. Physical 25AD batch and photo rights pending.",
 "sale_approved":False})
for brand in [b24,b25]:
 family=brand["family"]
 old=prev[family]["source_photos"]
 firstparty=brand["image_records"][0]
 assert len(brand["image_records"])==1
 prior=[(grab(x["path"],x["sha256"]),"PRIOR PRODUCT CANDIDATE") for x in old]
 new=(grab(firstparty["reference_path"],firstparty["reference_SHA256"]),"HK BRAND ORIGINAL 2250px")
 entries=prior+[new]
 contacts=OUT/(family+"-previous-plus-firstparty-four-or-three-INTERNAL-QA.jpg")
 make_sheet(family,[a for a,b in entries],[b for a,b in entries]).save(contacts,"JPEG",quality=89,optimize=True,subsampling=0)
 with Image.open(contacts) as ck: assert ck.size==(1080,1080) and ck.format=="JPEG"
 assert contacts.stat().st_size<2_000_000
 mismatch=family=="pending-25"
 claim_hold="HK product page says Glow Power Cream, while actual front label and Korean record say Glow Boost Cream" if mismatch else "Serum page and bottle label read Glow Power Serum"
 report={"family":family,"prior_clean_source_candidates":len(old),
  "new_official_source_visual_added":1,"provisional_combined_photo_scenes":len(entries),
  "additional_five_photo_target_shortfall":max(0,5-len(entries)),
  "brand_website_product_title":brand["official_shopify_title"],"title_vs_label_conflict":mismatch,
  "title_and_photo_label_note":claim_hold,
  "official_gallery_source_path":firstparty["reference_path"],
  "official_photo_reference_SHA256":firstparty["reference_SHA256"],
  "review_contact":str(contacts),
  "model_or_claim_overlay":"Brand logo visible but no extra clinical efficacy wording",
  "need_physical_KR_batch_check":True,"need_photo_commercial_license":True,"sale_approved":False}
 case_results.append(report)
 state["families"][family].update({"last_delta_version":"v2917",
  "release_status":"HQ_OFFICIAL_BRAND_PHOTO_PLUS_OLD_CANDIDATES_5SLOT_AUDITED_HOLD_STOCK_RIGHTS" if not mismatch else "BRAND_PAGE_TITLE_VS_PHYSICAL_LABEL_CONFLICT_BOOST_POWER_HOLD",
  "v2917_combined_clean_candidate_count":len(entries),
  "v2917_source_shortfall_to_five":max(0,5-len(entries)),
  "v2917_qa_visual_sheet":str(contacts),
  "latest_photo_QA_checkpoint":f"v2917 product scene visual QA: {len(old)} prior archived clean sources + one 2250px manufacturer scene = {len(entries)}/5 provisional, no retail rights; "+claim_hold,
  "sale_approved":False})
manifest={"version":"v2917","baseline":"v2916","date_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_updated":3,"firstparty_new_reference_scenes_screened":8,
 "new_clean_product_photo_candidates":3,"new_claim_scenes_quarantined":5,
 "new_internal_qa_comparisons":3,
 "retail_approved":0,"new_public_URLs":0,"previous_QA_bytes_changed":0,
 "existing_11_published_families_preserved":True,"existing_55_public_urls_preserved":True,
 "final_spreadsheet_shared":False,"results":case_results}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
state["version"]="v2917";state["baseline"]="v2916";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2917.json").write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"version":"v2917","new_reviewed":8,"new_clean_sources":3,
  "claim_sources_held":5,"new_internal_contact_JPGs":3,
  "bioheal_shortfall":{x["family"]:x["additional_five_photo_target_shortfall"] for x in case_results[1:]},
  "sale_approvals":0},ensure_ascii=False))
