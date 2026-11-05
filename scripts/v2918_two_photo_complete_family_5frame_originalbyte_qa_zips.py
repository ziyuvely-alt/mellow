#!/usr/bin/env python3
"""v2918: two stock families five-photo byte-preserved QA ZIP packages (not retail release).
Sources:
  pending-23 OBgE Pore Zero Sun Cream 50mL: v2912 5 source JPEGs.
  pending-28 PixelPure Glow Cleansing Serum Pad 210mL/70ct: v2914 5 source JPEGs.
Avoid redundant rendering. Original image bytes never changed. Image usage rights,
owned-stock edition and MK branding remain unresolved; NOT for public upload.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
from io import BytesIO
import json,time

ROOT=Path("qa-review")
PRE=ROOT/"v2917-threefamily-official-photo-visual-claim-review-QA"
P12=ROOT/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
P14=ROOT/"v2914-pixelpure-twelve-photo-visual-relevance-claims-and-duplicate-QA"
OUT=ROOT/"v2918-two-family-byte-identical-five-photo-internal-zip-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2917.json").read_text(encoding="utf-8"))
v12=json.loads((P12/"manifest.json").read_text(encoding="utf-8"))
v14=json.loads((P14/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2917" and len(state["families"])==30
p23=next(x for x in v12["family_results"] if x["family"]=="pending-23")
p28=next(x for x in v14["results"] if x["family"]=="pending-28")
assert p23["selected_existing_clean_photo_source_count"]==5
assert p28["combined_independent_scene_candidates_max"]==5
TARGETS=[
 {"family":"pending-23","name":"OBgE Pore Zero Oil Control Sun Cream 50mL",
  "photos":[{"path":x["path"],"sha256":x["sha256"],"role":"PREVIOUS_V2912_CLEAN_PRODUCT_SOURCE"}
   for x in p23["source_photos"]],
  "zip_name":"OBGE_PoreZero_SunCream_50mL_5PHOTO_ORIGINAL_BYTES_INTERNAL_QA.zip",
  "note":"All five product-specific tube/detail frames from v2912 archive; exact owned packaging/photo rights & MK logo hold."},
 {"family":"pending-28","name":"PIXEL PURE Glow Cleansing Serum Pads 210mL 70ct",
  "photos":[{"path":x["source_path"],"sha256":x["sha256"],"role":x["role"],"source":x["origin"]}
   for x in p28["combined_clean_source_candidates"]],
  "zip_name":"PixelPure_GlowCleansingSerumPads_210mL70ct_5PHOTO_ORIGINAL_BYTES_INTERNAL_QA.zip",
  "note":"Three v2912 preflight photos + two v2913 vetted brand source scenes from v2914; exact stock and photo rights hold."}
]
assert len(TARGETS)==2
OUT.mkdir(parents=True)
results=[]
for t in TARGETS:
 f=t["family"]
 assert len(t["photos"])==5
 unique=set();images=[]
 for i,src in enumerate(t["photos"],1):
  path=Path(src["path"]);assert path.is_file(),path
  b=path.read_bytes()
  digest=sha256(b).hexdigest()
  assert digest==src["sha256"],(path,"source bytes changed")
  assert digest not in unique,(f,"duplicate bytes")
  unique.add(digest)
  with Image.open(BytesIO(b)) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080),path
  assert len(b)<2_000_000
  images.append({"slot":i,"source_path":str(path),"original_sha256":digest,
   "original_bytes":len(b),"photo_size":[1080,1080],"format":"JPEG",
   "zip_name":f"{i:02d}-{f}-ARCHIVED-UNMODIFIED-QA.jpg","photo_source_role":src["role"],
   "exact_owner_inventory_edition":"PENDING","retail_photo_use_rights":"PENDING",
   "authentic_owner_MK_logo_verified":False,"marketing_claims_final_approved":False,
   "sale_approved":False})
 zpath=OUT/t["zip_name"]
 with ZipFile(zpath,"w",ZIP_DEFLATED,compresslevel=6) as z:
  for x in images:
   z.writestr(x["zip_name"],Path(x["source_path"]).read_bytes())
 with ZipFile(zpath) as z:
  assert len(z.namelist())==5
  for x in images:
   assert sha256(z.read(x["zip_name"])).hexdigest()==x["original_sha256"]
 assert zpath.stat().st_size>20_000
 result={"family":f,"product":t["name"],"existing_original_photos_packaged":5,
  "source_byte_hashes_validated":5,"new_photo_pixels_generated":0,"old_archive_files_changed":0,
  "all_JPGs_1080_square_under_2MB":True,"five_identical_source_bytes_in_zip":True,
  "internal_QA_zip":str(zpath),"internal_QA_zip_sha256":sha256(zpath.read_bytes()).hexdigest(),
  "zip_bytes":zpath.stat().st_size,"photo_records":images,"source_notes":t["note"],
  "pending_retail_blockers":["physical owned 50mL/210mL bottle/tub exact package edition",
   "photo source commercial usage rights","verified authentic MK owner logo","marketing claim and packaging proof"],
  "commercial_released":False,"public_uploaded":False}
 results.append(result)
 st=state["families"][f]
 st.update({"last_delta_version":"v2918",
  "release_status":"FIVE_EXISTING_TRUE_PHOTO_SOURCE_BYTES_PACKAGED_INTERNAL_QA_RIGHTS_STOCK_HOLD",
  "v2918_original_photo_JPG_count":5,"v2918_photo_byte_integrity_checked":True,
  "v2918_internal_ZIP_path":str(zpath),
  "latest_photo_QA_checkpoint":"v2918: five 1080x1080 original-source JPEGs hash-validated and packaged byte-identically in private QA ZIP, no new pixels; no public release, exact inventory edition, photo rights and authentic MK remain HOLD.",
  "sale_approved":False})
report={"version":"v2918","baseline":"v2917",
 "generated_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_packed":2,"total_original_photos_byte_validated":10,
 "internal_verified_5JPG_ZIPs":2,"new_composite_photo_pixels":0,
 "new_public_retail_images":0,"new_public_urls":0,"retail_approvals":0,
 "previous_11_published_families_preserved":True,
 "previous_55_published_URLs_preserved":True,
 "previous_QA_and_approved_files_modified":0,
 "final_spreadsheet_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2918";state["baseline"]="v2917";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2918.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2918","internal_zip_count":2,"original_photos_validated":10,
 "families":[x["family"] for x in results],"old_files_changed":0,"retail_approvals":0},ensure_ascii=False))
