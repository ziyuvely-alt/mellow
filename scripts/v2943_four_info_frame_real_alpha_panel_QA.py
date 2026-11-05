#!/usr/bin/env python3
"""v2943 selective photo-panel quality repair for 4 NEW v2942 QA info cards.
Replaces embedded QA-marked archived preview inside NEW copies only, with original alpha
product-only PNG (if genuinely transparent). Preserves all v2942 JPGs and 55 URLs.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageDraw,ImageOps
import json,time

Q=Path("qa-review")
BASE=Q/"v2942-four-missing-fifth-slot-fact-only-English-visual-QA"
OUT=Q/"v2943-four-English-frame-clean-truealpha-product-panel-QA"
assert not OUT.exists()
m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
s=json.loads((BASE/"stock30-incremental-state-v2942.json").read_text(encoding="utf-8"))
assert m["version"]==s["version"]=="v2942" and m["new_original_English_information_images_created"]==4
P={
 "pending-25":"qa-review/v2712-3-failed-cutouts-high-quality-recovery/pending-25/01-actual-alpha-cutout-high-res-QA.png",
 "pending-27":"qa-review/v2713-six-new-product-hero-real-alpha-cutouts/pending-27/01-truly-transparent-product-QA.png",
 "pending-29":"qa-review/v2713-six-new-product-hero-real-alpha-cutouts/pending-29/01-truly-transparent-product-QA.png",
 "pending-30":"qa-review/v2713-six-new-product-hero-real-alpha-cutouts/pending-30/01-truly-transparent-product-QA.png"
}
records=[]
OUT.mkdir(parents=True)
for rec in m["records"]:
 fam=rec["family"];candidate=Path(P[fam]);src=Path(rec["fifth_frame"])
 assert sha256(src.read_bytes()).hexdigest()==rec["fifth_frame_sha256"]
 result={"family":fam,"new_clean_panel_img":None,"source_alpha":str(candidate),
   "previous_QA_frame_untouched":True,"photo_bytes_and_color_unchanged":True,
   "new_sale_approval":False,"visual_quality":"PENDING"}
 try:
  with Image.open(candidate) as original:
   original.load()
   if original.format!="PNG":raise ValueError("not PNG")
   if not ("A" in original.getbands() or "transparency" in original.info):raise ValueError("cutout without real alpha")
   product=original.convert("RGBA")
  w,h=product.size
  if min(w,h)<200 or max(w,h)>3000:raise ValueError("unusable product cutout dimensions")
  alpha=product.getchannel("A")
  hist=alpha.histogram();fraction=sum(hist[:255])/(w*h)
  if fraction<0.035:raise ValueError("less than 3.5% real transparency")
  with Image.open(src) as old:
   old.load()
   assert old.format=="JPEG" and old.size==(1080,1080)
   frame=old.convert("RGB")
  d=ImageDraw.Draw(frame)
  d.rounded_rectangle((66,91,600,949),radius=25,fill="#FBF8F9")
  scaled=ImageOps.contain(product,(475,795),Image.Resampling.LANCZOS)
  x=333-scaled.width//2;y=515-scaled.height//2
  frame.paste(scaled,(x,y),scaled)
  path=OUT/(fam+"-English-information-clean-source-photo-panel-1080-INTERNAL-QA.jpg")
  frame.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
  with Image.open(path) as chk:
   chk.load()
   assert chk.format=="JPEG" and chk.size==(1080,1080)
  assert path.stat().st_size<2000000
  assert sha256(src.read_bytes()).hexdigest()==rec["fifth_frame_sha256"]
  result.update({"new_clean_panel_img":str(path),"new_sha256":sha256(path.read_bytes()).hexdigest(),
   "native_product_alpha_pixels":[w,h],"source_alpha_sha256":sha256(candidate.read_bytes()).hexdigest(),
   "alpha_nonopaque_fraction":round(fraction,6),
   "new_frame_bytes":path.stat().st_size,
   "visual_quality":"TRUE_ALPHA_PRODUCT_PHOTO_PANEL_COMPOSED_NEEDS_HUMAN_QA"})
  s["families"][fam].update({
   "last_delta_version":"v2943",
   "v2943_clean_fifth_info_frame":str(path),
   "v2943_real_cutout_source":str(candidate),
   "release_status":"INFO_FRAME_TRUE_ALPHA_PRODUCT_PANEL_INTERNAL_QA_STOCK_RIGHTS_HOLD",
   "sale_approved":False})
 except Exception as e:
  result["visual_quality"]="SOURCE_ALPHA_HOLD_NOT_RENDERED"
  result["error"]=str(e)
 records.append(result)
manifest={"version":"v2943","baseline":"v2942","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_inspected":4,"actual_new_clean_photo_panel_frames":sum(bool(x["new_clean_panel_img"]) for x in records),
 "old_v2942_four_images_modified":0,"old_55_public_urls_changed":0,
 "old_11_complete_families_modified":0,
 "new_photo_sources_generated":0,"new_retail_approvals":0,
 "new_public_image_URLs":0,"remaining_distinct_photo_scene_shortfall":4,
 "final_spreadsheet_shared":False,"results":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s.update({"version":"v2943","baseline":"v2942","new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False})
(OUT/"stock30-incremental-state-v2943.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2943","new_refined_internal_info_frames":manifest["actual_new_clean_photo_panel_frames"],"records":[{"fam":x["family"],"status":x["visual_quality"]} for x in records]},ensure_ascii=False))
