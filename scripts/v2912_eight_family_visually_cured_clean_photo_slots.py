#!/usr/bin/env python3
"""v2912: Eight-family visual shortlist from existing v2911 contact sheets.
This is a STRICT PRE-FLIGHT ORIGINAL PHOTO shortlist, not a commercial release.
Do not invent 5 images if fewer fit. Never edit/copy prior approved 55 public URLs.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json, time, math

ROOT=Path("qa-review")
PRE=ROOT/"v2911-eight-unscored-stock-family-existing-photo-index-QA"
OUT=ROOT/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
assert not OUT.exists()
old=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
state=json.loads((PRE/"stock30-incremental-state-v2911.json").read_text(encoding="utf-8"))
assert old["version"]=="v2911" and state["version"]=="v2911" and len(state["families"])==30
assert old["family_record_count"]==8 and old["existing_source_candidate_selection"]==71
# Human visual evaluation of the 8 v2911 contact sheets, 2026-11-05.
# Indices are 1-based in the v2911 contact sheet and refer to exact archived hashes.
# Strictly allow clean product/source photos only; exclude unverified MK, models,
# official store marketing badges and claim stamps, and low-native crop.
PICKS={
 "pending-20":[2,4,6],
 "pending-23":[1,3,4,5,6],
 "pending-24":[1,8,9],
 "pending-25":[2,3],
 "pending-27":[1,9],
 "pending-28":[1,2,9],
 "pending-29":[1],
 "pending-30":[1,9],
}
ISSUES={
 "pending-20":{
 "exclusions":{"1":"KOREAN_OFFICIAL_STORE_BADGE","3":"TEXT_ONLY_USAGE_GUIDE_UNVERIFIED","5":"FACT_ONLY_SLIDE_NOT_PHOTO","7":"OFFICIAL_STORE_BADGE_OVERLAY","8":"LOW_NATIVE_359x582_OFFICIAL_BADGE"},
 "selected_roles":{"2":"FULL_BOTTLE_PLAIN","4":"ANGLED_BOTTLE","6":"PRODUCT_ONLY_1080"},
 "next":"Request independent full-size actual spray/hand/texture photos from brand-cleared source; verify 100mL / 25AD package."},
 "pending-23":{
 "exclusions":{"2":"NEAR_REDUNDANT_PRODUCT_INFO_HERO","7":"BLACK_BACKGROUND_ALPHA_UNVERIFIED","8":"NATIVE_BELOW_900","9":"NATIVE_BELOW_900"},
 "selected_roles":{"1":"FULL_TUBE_WHITE","3":"TUBE_LEAF_ICE","4":"TUBE_ANGLED_DETAIL","5":"TUBE_TEXTURE","6":"TWO_TUBE_PRESENTATION"},
 "next":"Exact owned 50mL tube edition / source image licensing and claims review."},
 "pending-24":{
 "exclusions":{"2":"PRIOR_ART_MK_LOGO","3":"PRIOR_ART_MK_AND_PROMO","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_LOGO","6":"PRIOR_ART_MK_LOGO","7":"FACT_ONLY_NONPHOTO"},
 "selected_roles":{"1":"BOTTLE_CLEAN_WHITE","8":"SOURCE_PRODUCT_SCENE_A","9":"SOURCE_PRODUCT_SCENE_B"},
 "next":"Two more distinct full-size brand-cleared product/texture scenes; check 30mL old stock package."},
 "pending-25":{
 "exclusions":{"1":"BRAND_PROMO_KOREAN_BADGES","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_LOGO","6":"PRIOR_ART_MK_LOGO","7":"PRIOR_ART_MK_AND_MODEL_RIGHTS","8":"PRIOR_ART_MK_LOGO","9":"NATIVE_BELOW_900_SIMILAR_HERO"},
 "selected_roles":{"2":"CREAM_JAR_CLEAN_HERO_A","3":"CREAM_JAR_CLEAN_HERO_B_SIMILAR"},
 "next":"Both chosen jar views may overlap; acquire actual opened jar + texture scene, no model/claim stickers, 50mL stock proof."},
 "pending-27":{
 "exclusions":{"2":"PRIOR_ART_MK_LOGO","3":"PRIOR_ART_MK_LOGO","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_AND_HANDS_RIGHTS","6":"PRIOR_ART_MK_LOGO","7":"NATIVE_BELOW_900","8":"FACT_ONLY_NONPHOTO"},
 "selected_roles":{"1":"TONER_BOTTLE_CLEAN_HERO","9":"WATER_TEXTURE_WITH_BOTTLE_SOURCE"},
 "next":"Find 3 independent photos: full label/angled bottle and liquid texture; stock lot 200mL and photo rights verification."},
 "pending-28":{
 "exclusions":{"3":"PRIOR_ART_MK_LOGO_CROPPED","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_LOGO","6":"PRIOR_ART_MK_LOGO","7":"PRIOR_ART_MK_LOGO","8":"PRIOR_ART_MK_LOGO"},
 "selected_roles":{"1":"CLOSED_PADS_JAR_210ML_70EA","2":"OPENED_JAR_PAD_PICKUP","9":"OPEN_JAR_SERUM_PADS"},
 "next":"Need 2 more independent source photos: actual cotton pad texture and package back; stock 210mL / 70 sheets verify."},
 "pending-29":{
 "exclusions":{"2":"PRIOR_ART_MK_LOGO","3":"PRIOR_ART_MK_LOGO","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_LOGO","6":"PRIOR_ART_MK_LOGO_CROPPED","7":"PRIOR_ART_MK_LOGO","8":"NATIVE_BELOW_900_SIMILAR_HERO","9":"FACT_ONLY_NONPHOTO"},
 "selected_roles":{"1":"CREAM_JAR_CLEAN_FRONT"},
 "next":"Highest shortage: 4 additional rights-cleared original full-res opened jar / cream texture / lifestyle photos for exact 50mL version."},
 "pending-30":{
 "exclusions":{"2":"PRIOR_ART_MK_LOGO","3":"PRIOR_ART_MK_LOGO","4":"PRIOR_ART_MK_LOGO","5":"PRIOR_ART_MK_LOGO","6":"PRIOR_ART_MK_LOGO","7":"FACT_ONLY_NONPHOTO","8":"VEGAN_CHINESE_UNVERIFIED_CLAIM_STAMPS"},
 "selected_roles":{"1":"SERUM_CLEAN_SINGLE_BOTTLE","9":"SERUM_DROPPER_TEXTURE"},
 "next":"Need three new full-res brand-cleared product photo scenes; avoid unverified vegan/Chinese claim stamp frame."}
}
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def canvas(family,product,items):
 im=Image.new("RGB",(1080,1080),"#f4f4f5");d=ImageDraw.Draw(im)
 d.text((30,18),family.upper()+" | v2912 EXACT PHOTO SHORTLIST",font=font(31),fill="#222222")
 d.text((30,60),product[:65],font=font(18),fill="#4f4f4f")
 d.text((30,91),"QA ONLY  •  No retail rights, stock edition or MK logo verified",font=font(17),fill="#a52626")
 for i in range(5):
  col=i%3;row=i//3;x=27+col*348;y=133+row*435
  d.rounded_rectangle((x,y,x+328,y+406),radius=11,fill="white",outline="#dddddd",width=2)
  if i<len(items):
   orig=items[i]["img"]
   fit=ImageOps.contain(orig,(306,321),Image.Resampling.LANCZOS)
   im.paste(fit,(x+164-fit.width//2,y+9+(321-fit.height)//2))
   d.text((x+10,y+339),f"SLOT {i+1}: EXISTING SOURCE PHOTO",font=font(15),fill="#245541")
   d.text((x+10,y+363),items[i]["role"][:35],font=font(13),fill="#444444")
  else:
   d.text((x+25,y+160),"PHOTO STILL MISSING",font=font(18),fill="#a54444")
   d.text((x+25,y+198),"Not fabricated",font=font(15),fill="#666666")
 d.text((30,1030),f"{len(items)}/5 PRE-FLIGHT PHOTO SLOTS  •  {5-len(items)} UNSOURCED  •  0 retail approvals",font=font(18),fill="#4b4b4b")
 return im

OUT.mkdir(parents=True)
reports=[]
for record in old["families"]:
 family=record["family"];product=record["product"]
 assert family in PICKS and len(record["selected_original_paths"])>=max(PICKS[family])
 issue=ISSUES[family];ins=[];source_pool=record["selected_original_paths"]
 for no in PICKS[family]:
  cand=source_pool[no-1]
  p=Path(cand["path"])
  assert p.is_file() and sha256(p.read_bytes()).hexdigest()==cand["sha256"]
  with Image.open(p) as raw:
   raw.load()
   assert raw.format=="JPEG" and raw.size==(1080,1080) and p.stat().st_size<2_000_000
   photo=ImageOps.exif_transpose(raw).convert("RGB")
  ins.append({"idx":no,"img":photo,"role":issue["selected_roles"][str(no)] ,"path":str(p),
   "sha256":cand["sha256"],"bytes":p.stat().st_size,
   "internal_preflight_only":True,"reused_existing_bytes":True,
   "owned_physical_stock_edition_verified":False,"commercial_photo_license_verified":False,
   "photo_uniqueness_independent_scene_confirmed":False,
   "true_MK_brand_asset_verified":False,"retail_approved":False})
 out=OUT/(family+"-five-slot-clean-source-shortlist-INTERNAL-QA.jpg")
 canvas(family,product,ins).save(out,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(out) as c:assert c.format=="JPEG" and c.size==(1080,1080)
 assert out.stat().st_size<2_000_000
 exclusions=[{"source_index":int(i),"reason":reason,"path":source_pool[int(i)-1]["path"]} for i,reason in issue["exclusions"].items()]
 assert len(ins)+len(exclusions)==len(source_pool),(family,len(ins),len(exclusions),len(source_pool))
 reports.append({"family":family,"product":product,"selected_existing_clean_photo_source_count":len(ins),
  "minimum_five_photo_source_shortfall":5-len(ins),
  "source_photos":[{k:v for k,v in z.items() if k!="img"} for z in ins],
  "excluded_by_visual_preflight":exclusions,
  "internal_five_slot_contact_sheet":str(out),
  "highest_priority_next":issue["next"],
  "release_state":"PRE_FLIGHT_PHOTO_CANDIDATES_ONLY_NO_RIGHTS_OR_OWNED_STOCK"})
 st=state["families"][family]
 st.update({"last_delta_version":"v2912",
  "release_status":"VISUAL_SCREENING_DONE_PRELIMINARY_CLEAN_PHOTOS_STAGED_NO_RETAIL_RIGHTS",
  "v2912_existing_clear_photos":len(ins),
  "v2912_source_shortfall_out_of_five":5-len(ins),
  "v2912_new_five_slot_QA_contact":str(out),"sale_approved":False,
  "latest_photo_QA_checkpoint":f"v2912 visually screened {len(source_pool)} archived source images, selected {len(ins)}/5 clean-source candidates (not retail approved), rejected {len(exclusions)} risky/no-source candidates. Need exact stock/rights and {5-len(ins)} additional photos."})
manifest={"version":"v2912","baseline":"v2911","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "visual_contact_sheets_reviewed":8,"previous_image_candidates_reviewed":71,
 "preliminary_clean_candidate_source_photos":sum(len(r["source_photos"]) for r in reports),
 "quarantined_or_excluded_photo_candidates":sum(len(r["excluded_by_visual_preflight"]) for r in reports),
 "missing_slots_from_eight_five_photo_targets":sum(r["minimum_five_photo_source_shortfall"] for r in reports),
 "internal_five_slot_review_JPGs_created":8,
 "old_11_published_families_unchanged":True,"existing_55_public_urls_unchanged":True,
 "previous_QA_files_modified":0,"commercial_photo_licenses_cleared":0,
 "sale_approved_count":0,"public_images_published":0,"final_excel_shared":False,
 "family_results":reports}
assert manifest["previous_image_candidates_reviewed"]==manifest["preliminary_clean_candidate_source_photos"]+manifest["quarantined_or_excluded_photo_candidates"]
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
state["version"]="v2912";state["baseline"]="v2911";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2912.json").write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2912","photos_reviewed":71,
 "selected_clean":manifest["preliminary_clean_candidate_source_photos"],
 "excluded":manifest["quarantined_or_excluded_photo_candidates"],
 "missing_sources":manifest["missing_slots_from_eight_five_photo_targets"],
 "family_counts":{r["family"]:r["selected_existing_clean_photo_source_count"] for r in reports},
 "new_qa_contacts":8,"retail_approvals":0},ensure_ascii=False))
