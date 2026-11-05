#!/usr/bin/env python3
"""v2917 GOODAL source photo claim audit and 2-SKU package identity comparison.
Read only v2916/v2906 archived bytes, never rebuild originals or change 55 public URLs.
No unverified marketing, model, or before-after image approved for retail.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,time

QA=Path("qa-review")
PRE=QA/"v2916-goodal-cream50-eyecream-official-media-gallery-only-QA"
EYE=QA/"v2906-two-goodal-obge-official-source-photo-recovery-QA"
OUT=QA/"v2917-goodal-cream-six-source-claims-and-eye-source-edition-QA"
assert not OUT.exists()
manifest=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
st=json.loads((PRE/"stock30-incremental-state-v2916.json").read_text(encoding="utf-8"))
eye_manifest=json.loads((EYE/"manifest.json").read_text(encoding="utf-8"))
assert manifest["version"]==st["version"]=="v2916" and len(st["families"])==30
cream=next(x for x in manifest["results"] if x["family"]=="pending-19")
eye=next(x for x in eye_manifest["families"] if x["family"]=="pending-21")
assert cream["new_brand_original_sources"]==6 and len(cream["images"])==6 and eye["source_candidates_saved"]==1
def f(nt):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",nt)
 except:return ImageFont.load_default()
def read(path,digest):
 p=Path(path)
 assert p.is_file() and sha256(p.read_bytes()).hexdigest()==digest, ("changed archived photo",path)
 with Image.open(p) as src:
  src.load()
  assert src.format=="JPEG" and src.size==(1080,1080) and p.stat().st_size<2000000
  return ImageOps.exif_transpose(src).convert("RGB")
flags=[
 ("PROVISIONAL_PRODUCT_HERO","Clean 50mL cream jar labeled Dark Spot Care Cream alpha; used as internal package candidate, not proof of stock lot"),
 ("HOLD_MARKETING_CLAIMS","Text Faster Visible Results over 2 cream jars, no independent sales claim or pack license"),
 ("HOLD_STRONGER_NUMERIC_CLAIM","Claims 3.5X stronger and fades spots in 1 week, clinical proof/permission missing"),
 ("HOLD_QUANTIFIED_SKIN_CLAIMS","Model face graphic with 50.1/29.7/39.6/7.54 percentages, usage/clinical rights missing"),
 ("HOLD_MODEL_BEFORE_AFTER","Close-ups of faces labeled BEFORE / AFTER 4 WEEKS, image/model consent unverified"),
 ("HOLD_INGREDIENT_PROMISES","Ingredient chart and High-Potency Actives for Radiant-Looking Skin claims, source rights unverified")
]
review=[]
for i,z in enumerate(cream["images"]):
 a,b=flags[i]
 assert read(z["reference_path"],z["reference_sha256"]).size==(1080,1080)
 review.append({"index":i+1,"source_path":z["reference_path"],"source_sha256":z["reference_sha256"],
  "visual_classification":a,"reason":b,"candidate_for_internal_identity_reference":i==0,
  "new_distinct_sale_approved_photo":False,"claims_verified":False,
  "physical_stock_lot_confirmed":False,"commercial_photo_rights_confirmed":False})
eyeimg=eye["items"][0]
eyi=read(eyeimg["jpeg_reference"],eyeimg["jpeg_sha256"])
creami=read(cream["images"][0]["reference_path"],cream["images"][0]["reference_sha256"])
out=Image.new("RGB",(1080,1080),"#f4f4f5");d=ImageDraw.Draw(out)
d.text((28,15),"GOODAL | v2917 TWO DIFFERENT PRODUCTS",font=f(29),fill="#252525")
d.text((28,56),"MANUFACTURER-PHOTO SOURCE IDENTITIES: INTERNAL QA ONLY",font=f(18),fill="#8f3535")
for i,(im,heading,sub) in enumerate([
 (creami,"CREAM 50mL","DARK SPOT CARE CREAM alpha"),
 (eyi,"EYE CREAM","DARK SPOT CARE EYE CREAM")]):
 x=25+528*i; y=112
 d.rounded_rectangle((x,y,x+510,y+826),radius=10,fill="white",outline="#cccccc",width=2)
 scaled=ImageOps.contain(im,(488,608),Image.Resampling.LANCZOS)
 out.paste(scaled,(x+255-scaled.width//2,y+15+(608-scaled.height)//2))
 d.text((x+16,y+646),heading,font=f(25),fill="#303030")
 d.text((x+16,y+692),sub,font=f(16),fill="#555555")
 d.text((x+16,y+749),"NOT APPROVED FOR RETAIL",font=f(17),fill="#963737")
d.text((27,976),"Cream 5/6 other marketing frames held. Eye 25AD cap/lot still unverified.",font=f(17),fill="#963737")
d.text((27,1015),"Existing originals/rights/stock generation untouched; 0 newly published URLs.",font=f(16),fill="#555555")
OUT.mkdir(parents=True)
comparison=OUT/"GOODAL-cream50-vs-eye-25AD-1080-INTERNAL-QA.jpg"
out.save(comparison,"JPEG",quality=89,optimize=True,subsampling=0)
assert comparison.stat().st_size<2_000_000
with Image.open(comparison) as check:assert check.format=="JPEG" and check.size==(1080,1080)
for fam in ["pending-19","pending-21"]:
 s=st["families"][fam]
 s.update({"last_delta_version":"v2917","sale_approved":False,
  "v2917_product_identity_comparison_path":str(comparison)})
st["families"]["pending-19"].update({
 "release_status":"SIX_MANUFACTURER_FRAMES_CLAIMS_VISUALLY_SCREENED_CLEAN_HERO_ONLY_QA",
 "v2917_firstparty_clean_product_reference_count":1,
 "v2917_claim_or_model_marketing_frames_held":5,
 "latest_photo_QA_checkpoint":"v2917 6 archived official gallery images visually classified: 1 clean 50mL alpha cream package reference, 5 unverified clinical/marketing/model before-after frames held. No retail permission / stock match."})
st["families"]["pending-21"].update({
 "release_status":"ONE_OLD_FIRSTPARTY_EYE_CREAM_PHOTO_VERIFIED_NO_NEW_SITE_SOURCE",
 "v2917_existing_firstparty_eye_cream_hero_reused":eyeimg["jpeg_reference"],
 "v2917_new_originals":0,
 "latest_photo_QA_checkpoint":"v2917 compared unchanged v2906 1200 native yellow silver-cap eye cream bottle to cream alpha 50mL. Official current page 404 in v2916; no new source or 25AD lot proof. No replacement photo synthesized."})
report={"version":"v2917","baseline":"v2916","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family_count":2,"existing_cream_photos_visually_reviewed":6,"existing_eye_photos_reused":1,
 "cream_clean_internal_source_count":1,"held_claim_marketing_model_sources":5,
 "eye_current_official_page_status":"404_RECORDED_IN_V2916",
 "existing_eye_native_product_source_px":[1200,1200],
 "new_original_photos_downloaded":0,"new_comparison_internal_QA_JPGs":1,
 "new_sales_approvals":0,"new_public_image_URLs":0,"old_11_published_families_modified":0,
 "old_55_published_URLs_modified":0,"prior_QA_assets_modified":0,
 "final_spreadsheet_shared":False,
 "cream_visual_review":review,
 "eye_reference":{"path":eyeimg["jpeg_reference"],"reference_sha256":eyeimg["jpeg_sha256"],
    "visible_identity":"Goodal Green Tangerine Vita-C Dark Spot Care Eye Cream yellow silver-cap tube",
    "edition_25AD_unverified":True,"retail_approved":False},
 "comparison_JPG":str(comparison)}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
st["version"]="v2917";st["baseline"]="v2916";st["new_sales_approvals"]=0;st["new_public_URLs"]=0;st["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2917.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2917","reviewed":6,"cream_clean_candidates":1,
 "marketing_sources_rejected":5,"eye_prior_reused":1,"new_review_JPGs":1,
 "sale_approvals":0},ensure_ascii=False))
