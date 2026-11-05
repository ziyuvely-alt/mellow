#!/usr/bin/env python3
"""v2908: acquire new manufacturer photo SCENES for MISSHA PDRN 30mL serum / 70mL cream.
Only original binary reference+1080 QA preview; never release/overwrite previously approved files.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageOps
from hashlib import sha256
import requests, json, time

QA=Path("qa-review")
BASE=QA/"v2907-missha-pdrn-firstparty-twofamily-source-photo-QA"
PRE=BASE/"stock30-incremental-state-v2907.json"
OUT=QA/"v2908-missha-pdrn-twofamily-distinct-official-photo-scenes-QA"
assert PRE.is_file() and not OUT.exists()
state=json.loads(PRE.read_text())
assert state["version"]=="v2907" and len(state["families"])==30
TARGETS=[
 {"family":"pending-13","product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
 "sources":[
  {"url":"https://misshaus.com/cdn/shop/files/MS104056___NAD___03.jpg?v=1782916376&width=3840","source_type":"MISSHA_US_FIRST_PARTY","scene":"dropper plus bottle and branded benefits text"},
  {"url":"https://www.misshajp.com/photo/goodsimg/MS104056/ms104056-01.jpg","source_type":"MISSHA_JP_FIRST_PARTY","scene":"bottle and brand styling or texture"},
 ]},
 {"family":"pending-14","product":"MISSHA PDRN NAD+ Firming Repair Cream 70mL",
 "sources":[
  {"url":"https://misshaus.com/cdn/shop/files/MS104031___NAD___03.jpg?v=1782917472&width=3840","source_type":"MISSHA_US_FIRST_PARTY","scene":"cream jar open and branded benefits text"},
  {"url":"https://www.misshajp.com/photo/goodsimg/MS104031/ms104031-01.jpg","source_type":"MISSHA_JP_FIRST_PARTY","scene":"jar and jelly cream texture; JP packaging unit 70g may differ"}
 ]},
]
ALLOWED={"misshaus.com","www.misshaus.com","www.misshajp.com","misshajp.com"}
sess=requests.Session()
sess.headers.update({"User-Agent":"Mozilla/5.0 (compatible; non-commercial original-photo QA archive)"})
OUT.mkdir(parents=True)
prior_manifest=json.loads((BASE/"manifest.json").read_text())
prior_source_hashes={z["source_sha256"] for c in prior_manifest["cases"] for z in c["original_images"]}
total=0
records=[]
for target in TARGETS:
 family=target["family"];saved=[];skipped=[];local_hash=set()
 for item in target["sources"]:
  url=item["url"]; host=urlparse(url).hostname
  if host not in ALLOWED or not url.startswith("https://"):
   skipped.append({"url":url,"reason":"source host not on manufacturer allowlist"});continue
  try:
   r=sess.get(url,timeout=14,allow_redirects=True);r.raise_for_status()
   if urlparse(r.url).hostname not in ALLOWED:raise ValueError("redirected off manufacturer domain")
   b=r.content
   if not 3000<len(b)<10_000_000:raise ValueError("size invalid")
   original=Image.open(BytesIO(b));original.load()
   fmt=original.format
   if fmt not in ("JPEG","PNG","WEBP"):raise ValueError("not supported image")
   photo=ImageOps.exif_transpose(original).convert("RGB")
   w,h=photo.size
   if min(w,h)<900:
    skipped.append({"url":url,"reason":f"native below 900: {w}x{h}"});continue
   digest=sha256(b).hexdigest()
   if digest in local_hash or digest in prior_source_hashes:
    skipped.append({"url":url,"reason":"byte-identical prior first-party photo source"});continue
   local_hash.add(digest)
   ordinal=len(saved)+1
   folder=OUT/family
   folder.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[fmt]
   src=folder/f"{ordinal:02d}-manufacturer-original{ext}"
   src.write_bytes(b)
   canvas=Image.new("RGB",(1080,1080),"white")
   shrunk=ImageOps.contain(photo,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(shrunk,((1080-shrunk.width)//2,(1080-shrunk.height)//2))
   preview=folder/f"{ordinal:02d}-manufacturer-1080-INTERNAL-REFERENCE.jpg"
   canvas.save(preview,"JPEG",quality=90,optimize=True,subsampling=0)
   assert preview.stat().st_size<2_000_000
   with Image.open(preview) as check:assert check.format=="JPEG" and check.size==(1080,1080)
   saved.append({"source_url":url,"source_type":item["source_type"],"source_scene_description_unverified":item["scene"],
      "native_pixels":[w,h],"raw_original_path":str(src),"raw_source_sha256":digest,
      "reference_JPG":str(preview),"reference_sha256":sha256(preview.read_bytes()).hexdigest(),
      "prior_v2907_byte_duplicate":False,
      "unique_photo_scene_visual_QA":"PENDING","product_stock_edition":"PENDING",
      "claims_and_legal_photo_rights":"PENDING",
      "marketing_claim_overlays_and_model_images":"POTENTIAL_NO_RETAIL_REUSE",
      "retail_approved":False})
   total+=1
  except Exception as e:skipped.append({"url":url,"reason":str(e)[:190]})
 records.append({"family":family,"product":target["product"],"new_source_count":len(saved),
    "new_originals":saved,"skips":skipped,"release_status":"ORIGINAL_SOURCE_PHOTO_ARCHIVED_REVIEW_ONLY"})
 if saved:
  st=state["families"][family]
  st["last_delta_version"]="v2908"
  st["release_status"]="NEW_MANUFACTURER_ORIGINAL_SCENES_ARCHIVED_VISUAL_CLAIMS_RIGHTS_EDITION_HOLD"
  st["latest_photo_QA_checkpoint"]=f"v2908 {len(saved)} NEW manufacturer photo scene candidates from MISSHA US/JP, original native >=900 and 1080-reference JPG, no sale use; edition/claims/photo rights hold."
if total==0:raise RuntimeError("No new native >=900 manufacturer original photo; do not create empty QA checkpoint")
manifest={"version":"v2908","baseline":"v2907","date_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "new_manufacturer_photo_originals":total,"new_1080_JPG_internal_references":total,"families":records,
 "photo_distinctness_visual_QA_done":False,"licensed_sales_ready_photos":0,
 "existing_11_published_families_untouched":True,"existing_55_public_URLs_untouched":True,
 "existing_QA_files_modified":0,"new_commercial_sale_approvals":0,"new_published_URLs":0,
 "final_XLSX_shared":False}
state["version"]="v2908";state["baseline"]="v2907";state["new_sale_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2908.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2908","new_originals":total,"counts":{c["family"]:c["new_source_count"] for c in records},"sale_approved":0},ensure_ascii=False))
