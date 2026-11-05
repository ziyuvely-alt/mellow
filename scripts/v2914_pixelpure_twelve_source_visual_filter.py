#!/usr/bin/env python3
"""v2914: human-reviewed v2913 12 official source photos for four PixelPure stock items.
Do not count marketing badges, unrelated mask-promo, or lookalike views as new five-photo slots.
All files and outputs are internal QA. Existing 11 published groups and 55 URLs immutable.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

Q=Path("qa-review")
OLD=Q/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
PRE=Q/"v2913-pixelpure-four-exact-product-official-gallery-native-source-QA"
OUT=Q/"v2914-pixelpure-twelve-photo-visual-relevance-claims-and-duplicate-QA"
assert not OUT.exists()
old=json.loads((OLD/"manifest.json").read_text(encoding="utf-8"))
m=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
state=json.loads((PRE/"stock30-incremental-state-v2913.json").read_text(encoding="utf-8"))
assert m["version"]==state["version"]=="v2913" and len(state["families"])==30
old_groups={x["family"]:x for x in old["family_results"]}
# Hand-checked against each four-up manufacturer's official source comparison.
DECISIONS={
 "pending-27":{
   1:("EXCLUDE_CLAIM_OVERLAY","manufacturer promotional vegan & test stamp text: not cleared"),
   2:("RESERVE_POSSIBLE_DUPLICATE","clear toner pouring close-up resembles existing selected original; no incremental count"),
   3:("INCLUDE_DISTINCT_SCENE","two 200 mL pink toner bottles on pale studio background; distinct no promo overlay"),
   4:("EXCLUDE_SIMILAR_SCENE","liquid pour closeup near-identical to source #2; does not add new scene")},
 "pending-28":{
   1:("EXCLUDE_GIFT_PROMOTION","serum pad tub displayed with mask product and mini ad card; product bundle not supported"),
   2:("INCLUDE_DISTINCT_SCENE","single saturated cotton cleansing pad under falling serum; texture demo, no claims"),
   3:("INCLUDE_DISTINCT_SCENE","serum pads layered over closed jar with green leaf and clear liquid; different product composition"),
   4:("RESERVE_SIMILAR_HERO","closed tub alone on pink plinth; similar to previously selected closed-tub hero, no additional slot")},
 "pending-29":{
   1:("INCLUDE_DISTINCT_SCENE","50 mL jar open with visible white cream and second jar blurred at rear"),
   2:("RESERVE_SIMILAR_HERO","closed 50 mL jar on white scene, similar to old full-jar clean hero"),
   3:("EXCLUDE_CLAIM_OVERLAY","brand vegan + dermatology/skin test claim badges on photo without sales claim clearance")},
 "pending-30":{
   1:("INCLUDE_DISTINCT_SCENE","three pink 50 mL serum bottles on pink background with white fluid thread, no promise overlay")}
}
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def read_jpg(path,expected):
 p=Path(path); b=p.read_bytes()
 assert sha256(b).hexdigest()==expected,(path,"source bytes changed")
 with Image.open(p) as raw:
  raw.load()
  assert raw.format=="JPEG" and raw.size==(1080,1080) and len(b)<2_000_000,path
  return ImageOps.exif_transpose(raw).convert("RGB")
def contact(family,product,slots):
 im=Image.new("RGB",(1080,1080),"#f5f5f6");d=ImageDraw.Draw(im)
 d.text((22,18),family.upper()+" | v2914 CLEAN SOURCE CANDIDATES",font=font(28),fill="#292929")
 d.text((22,57),product[:66],font=font(19),fill="#4a4a4a")
 d.text((22,88),"EXISTING + NEW FIRST-PARTY  |  PHOTO / RIGHTS / STOCK: HOLD",font=font(17),fill="#a13535")
 for i in range(5):
  col=i%3;row=i//3;x=20+col*350;y=135+row*437
  d.rounded_rectangle((x,y,x+336,y+408),radius=10,fill="white",outline="#cccccc",width=2)
  if i<len(slots):
   z=slots[i];thumb=ImageOps.contain(z["img"],(320,318),Image.Resampling.LANCZOS)
   im.paste(thumb,(x+168-thumb.width//2,y+12+(318-thumb.height)//2))
   d.text((x+10,y+342),("OLD" if z["origin"]=="v2912" else "NEW")+" "+str(z["slot"]),font=font(17),fill="#2b5849")
   d.text((x+10,y+372),"REFERENCE ONLY / NOT APPROVED",font=font(12),fill="#9d3535")
  else:
   d.text((x+20,y+169),"MISSING PHOTO",font=font(20),fill="#9d3535")
   d.text((x+20,y+202),"Do not fabricate",font=font(15),fill="#666666")
 d.text((22,1038),f"{min(5,len(slots))}/5 proposed distinct scenes • 0 retail approvals",font=font(18),fill="#555555")
 return im
OUT.mkdir(parents=True)
results=[]
for original in m["results"]:
 family=original["family"];review=DECISIONS[family]
 assert len(review)==original["new_source_originals_count"],family
 previous=old_groups[family]
 previous_count=previous["selected_existing_clean_photo_source_count"]
 slots=[];decisions=[]
 for i,z in enumerate(previous["source_photos"]):
  # v2912 may contain similar pictures; still provisional, do not overstate independence.
  slots.append({"origin":"v2912","slot":i+1,"img":read_jpg(z["path"],z["sha256"]),
    "path":z["path"],"sha256":z["sha256"],"role":"PREVIOUS_SCREENED_SOURCE"})
 for i,new in enumerate(original["new_originals"],1):
  d,why=review[i]
  item={"source_index":i,"decision":d,"reason":why,"original_path":new["raw"],"source_url":new["source"],
     "reference_path":new["ref"],"reference_sha256":new["ref_SHA256"],
     "marketing_claims_cleared":False,"product_stock_edition_verified":False,
     "commercial_redistribution_permitted":False,"retail_approved":False}
  source=read_jpg(new["ref"],new["ref_SHA256"])
  if d=="INCLUDE_DISTINCT_SCENE":
   slots.append({"origin":"v2913","slot":i,"img":source,"path":new["ref"],
      "sha256":new["ref_SHA256"],"role":why})
  decisions.append(item)
 # preview up to five, but preserve additional eligible source references in the manifest
 contact_path=OUT/(family+"-combined-five-scene-internal-QA.jpg")
 contact(family,original["product"],slots).save(contact_path,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(contact_path) as tmp:assert tmp.size==(1080,1080) and tmp.format=="JPEG"
 added=sum(d["decision"]=="INCLUDE_DISTINCT_SCENE" for d in decisions)
 combined=previous_count+added
 shortage=max(0,5-combined)
 selected=[{"origin":x["origin"],"source_path":x["path"],"sha256":x["sha256"],"role":x["role"]}
  for x in slots]
 results.append({"family":family,"product":original["product"],
  "prior_v2912_candidate_photos":previous_count,
  "new_v2913_originals_visually_reviewed":len(review),
  "v2913_distinct_scene_photo_candidates_added":added,
  "v2913_hold_or_reject_count":len(review)-added,
  "combined_independent_scene_candidates_max":combined,
  "target_5_image_photo_shortfall":shortage,
  "source_visual_review":decisions,
  "combined_clean_source_candidates":selected,
  "five_slot_internal_contact":str(contact_path),
  "sale_approved":False,"release_status":"SOURCE_CANDIDATES_PRELIMINARY_RIGHTS_AND_OWNED_STOCK_HOLD"})
 st=state["families"][family]
 st.update({"last_delta_version":"v2914",
  "release_status":"BRAND_GALLERY_VISUALLY_FILTERED_CLEAN_PHOTO_SOURCE_HOLD_RIGHTS_STOCK",
  "v2914_new_distinct_firstparty_photo_candidates":added,
  "v2914_source_shortfall_out_of_5":shortage,
  "v2914_combined_visual_contact":str(contact_path),
  "latest_photo_QA_checkpoint":f"v2914: {len(review)} first-party references visually screened, {added} distinct-source candidates added, {len(review)-added} claim/near-duplicate/bundle promotions held, {combined} provisional photos total, need {shortage} more; retail rights/physical stock HOLD.",
  "sale_approved":False})
report={"version":"v2914","baseline":"v2913","generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "pixelpure_groups":4,"official_photos_visually_screened":12,
 "new_distinct_scene_candidates_added":sum(x["v2913_distinct_scene_photo_candidates_added"] for x in results),
 "held_or_rejected_sources":sum(x["v2913_hold_or_reject_count"] for x in results),
 "four_family_combined_photo_shortfall":sum(x["target_5_image_photo_shortfall"] for x in results),
 "previous_11_published_families_preserved":True,"previous_55_public_urls_preserved":True,
 "new_photo_sale_approvals":0,"new_published_urls":0,"old_file_modifications":0,
 "new_QA_five_slot_images":4,"final_spreadsheet_shared":False,"results":results}
assert report["new_distinct_scene_candidates_added"]+report["held_or_rejected_sources"]==12
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2914";state["baseline"]="v2913";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2914.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2914","screened":12,"added":report["new_distinct_scene_candidates_added"],
 "blocked":report["held_or_rejected_sources"],"remaining_4_family":report["four_family_combined_photo_shortfall"],
 "by_family":{x["family"]:{"added":x["v2913_distinct_scene_photo_candidates_added"],"missing":x["target_5_image_photo_shortfall"]} for x in results},
 "new_sales_approvals":0},ensure_ascii=False))
