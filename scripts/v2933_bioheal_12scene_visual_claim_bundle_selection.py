#!/usr/bin/env python3
"""v2933 manually reviewed 12 existing BIOHEAL domestic item-gallery photos.
Clean real source scene classification only. Archived sources and old 55 public URLs
remain immutable. Retail rights, stock edition and branding are NOT verified.
"""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

QA=Path("qa-review")
P32=QA/"v2932-bioheal-two-domestic-exact-sku-gallery-12source-QA"
P20=QA/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
OUT=QA/"v2933-bioheal-twelve-source-visual-bundle-claim-and-scene-QA"
assert not OUT.exists(),"Checkpoint already exists; never reprocess."
manifest=json.loads((P32/"manifest.json").read_text(encoding="utf-8"))
state=json.loads((P32/"stock30-incremental-state-v2932.json").read_text(encoding="utf-8"))
old=json.loads((P20/"manifest.json").read_text(encoding="utf-8"))
assert manifest["version"]==state["version"]=="v2932"
assert len(state["families"])==30 and manifest["new_nonduplicate_source_references"]==12
assert manifest["native_at_least_900_source_refs"]==12
byold={r["family"]:r for r in old["results"]}
DECISIONS={
"pending-24":[
 ("REJECT_PROMO_BUNDLE","Includes extra mask/cream and seller promotional overlay; never represent single 30mL serum"),
 ("HOLD_MARKETING_OVERLAY","Product source with Slow Aging and NAD advertising badges"),
 ("HOLD_MARKETING_OVERLAY","Dropper bottle with Slow Aging/NAD/brightening badges; unsupported copy"),
 ("HOLD_MARKETING_OVERLAY","Dropper open, Slow Aging/NAD/brightening advertising badges"),
 ("REJECT_PROMO_BUNDLE","Multiple promotional packages and mask gift, not one serum SKU"),
 ("CLEAN_ALTERNATE_ONLY","Clean full 30mL serum on white; closely resembles existing front bottle references, not a proven new scene")
],
"pending-25":[
 ("HOLD_MARKETING_OVERLAY","Open cream jar with firming/antiaging badges; not a clean marketplace photo"),
 ("HOLD_MARKETING_OVERLAY","Angled open jar with firming/antiaging badges; not claim-cleared"),
 ("HOLD_MODEL_USAGE_RIGHTS","Human model holding cream; commercial model and photo rights unverified"),
 ("CLEAN_DISTINCT_SCENE_CANDIDATE","Opened and inverted jars showing 50mL cream texture; different original product photo composition"),
 ("HOLD_NEAR_DUPLICATE_FRONT","Full 50mL cream jar frontal, similar to prior cropped and frontal source photos"),
 ("HOLD_NEAR_DUPLICATE_FRONT","Full 50mL cream jar frontal, same posture as gallery #5 and prior")
]}
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def dhash(im):
 g=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def prior(fam):
 m=byold[fam]
 p=Path(m["zip_path"])
 assert sha256(p.read_bytes()).hexdigest()==m["zip_sha256"]
 oldhash=[]
 with ZipFile(p) as z:
  assert z.testzip() is None and len(z.namelist())==m["actual_original_source_jpgs_in_zip"]
  for f in z.namelist():
   with Image.open(BytesIO(z.read(f))) as im:
    oldhash.append(dhash(im.convert("RGB")))
 return oldhash
def contact(fam,imgs,decision):
 board=Image.new("RGB",(1080,1080),"#f5f6f8");dr=ImageDraw.Draw(board)
 dr.text((22,14),fam.upper()+" | v2933 VISUAL SOURCE DECISIONS",font=font(28),fill="#222222")
 dr.text((22,52),"Retail promotion and unlicensed marketing images NOT accepted",font=font(17),fill="#a33333")
 for i,(im,category) in enumerate(zip(imgs,decision)):
  col=i%3;row=i//3;x=16+col*354;y=101+row*440
  dr.rounded_rectangle((x,y,x+342,y+420),radius=10,fill="white",outline="#dddddd",width=2)
  fit=ImageOps.contain(im,(326,330),Image.Resampling.LANCZOS)
  board.paste(fit,(x+171-fit.width//2,y+7+(330-fit.height)//2))
  label=category[:36]
  dr.text((x+10,y+350),f"{i+1} {label}",font=font(12),fill="#23735a" if category=="CLEAN_DISTINCT_SCENE_CANDIDATE" else "#9e3939")
  dr.text((x+10,y+385),"REFERENCE ONLY; NOT RETAIL",font=font(13),fill="#ab3838")
 dr.text((22,1034),"Old assets, existing 11 completed families and 55 URLs remain unchanged.",font=font(17),fill="#444444")
 return board

OUT.mkdir(parents=True)
results=[]
for group in manifest["results"]:
 fam=group["family"];assert fam in DECISIONS
 entries=group["new_gallery_photos"];verdicts=DECISIONS[fam]
 assert len(entries)==len(verdicts)==6
 hashes=prior(fam);photos=[];rows=[]
 for i,(entry,(category,note)) in enumerate(zip(entries,verdicts),1):
  p=Path(entry["reference_1080"])
  assert p.is_file() and sha256(p.read_bytes()).hexdigest()==entry["reference_sha256"]
  with Image.open(p) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080)
   rgb=ImageOps.exif_transpose(im).convert("RGB")
  hd=min([dist(dhash(rgb),a) for a in hashes],default=64)
  # Visual scene selection is manual, while the metric is only a duplicate warning.
  eligible=category=="CLEAN_DISTINCT_SCENE_CANDIDATE"
  rows.append({"slot":i,"gallery_photo":entry["reference_1080"],
   "sha256":entry["reference_sha256"],"source_url":entry["source_url"],
   "source_native_px":entry["native"],"classification":category,"visual_reason":note,
   "closest_prior_dhash_hamming":hd,"pHash_requires_manual_comparison_if_lt_5":hd<5,
   "provisional_distinct_scene":eligible,
   "commercial_use_rights":False,"owned_KR_stock_edition":False,
   "retail_approved":False})
  photos.append(rgb)
 new_sheet=OUT/(fam+"-six-source-classifications-INTERNAL-ONLY.jpg")
 contact(fam,photos,[r["classification"] for r in rows]).save(new_sheet,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(new_sheet) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
 assert new_sheet.stat().st_size<2_000_000
 selected=[r for r in rows if r["provisional_distinct_scene"]]
 st=state["families"][fam]
 st.update({"last_delta_version":"v2933",
    "release_status":"DOMESTIC_GALLERY_CLAIMS_BUNDLES_REVIEWED_ONLY_CLEAN_SCENES_PROVISIONAL",
    "v2933_scanned_and_classified":6,
    "v2933_distinct_scene_candidate_references":[r["gallery_photo"] for r in selected],
    "v2933_six_scene_classification_sheet":str(new_sheet),
    "latest_photo_QA_checkpoint":f"v2933 visually screened 6 domestic exact-SKU photo sources, {len(selected)} provisional distinct clean scene(s); remaining are bundle/claims/model/near-front duplicate holds. Physical stock and commercial photo rights not verified.",
    "sale_approved":False})
 results.append({"family":fam,"existing_archived_source_photo_count":byold[fam]["actual_original_source_jpgs_in_zip"],
  "reviewed_brand_photo_sources":len(rows),
  "clear_provisional_distinct_scene_count":len(selected),
  "holds_or_rejections":6-len(selected),"visual_decisions":rows,
  "review_contact":str(new_sheet),"sale_approved":False})
report={"version":"v2933","baseline":"v2932",
 "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_reviewed":2,"source_images_screened":12,
 "clean_new_scene_candidates":sum(r["clear_provisional_distinct_scene_count"] for r in results),
 "marketing_model_or_duplicate_sources_held":sum(r["holds_or_rejections"] for r in results),
 "old_image_bytes_changed":0,"old_55_verified_URLs_changed":0,
 "existing_11_retail_families_changed":0,"new_sales_image_approvals":0,
 "new_public_urls":0,"final_spreadsheet_shared":False,"results":results}
assert report["clean_new_scene_candidates"]==1 and report["marketing_model_or_duplicate_sources_held"]==11
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2933";state["baseline"]="v2932";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2933.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2933","originals_screened":12,
 "clean_provisional_candidates":1,"ad_bundles_and_lookalikes_held":11,
 "retail_approved":0},ensure_ascii=False))
