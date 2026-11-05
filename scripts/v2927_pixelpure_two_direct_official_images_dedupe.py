#!/usr/bin/env python3
"""v2927: acquire exactly two identified PixelPure manufacturer product-gallery original JPEGs,
compare against existing family-specific v2920 archive photo hashes/scenes; QA only.
No rebuilding old pixels, no fabricated photos, no commercial release.
"""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha256
from urllib.parse import urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,time
Q=Path("qa-review")
BASE=Q/"v2926-30family-26sourcezip-qa-state-and-next-action-ledger"
OUT=Q/"v2927-pixelpure-two-direct-official-source-originals-dedupe-QA"
assert not OUT.exists()
S=json.loads((BASE/"stock30-incremental-state-v2926.json").read_text(encoding="utf-8"))
M=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
assert S["version"]=="v2926" and M["sha256_and_ZIP_CRC_verified_archives"]==26
REC={r["family"]:r for r in M["family_records"]}
T=[
 {"family":"pending-27","product":"PixelPure Soothing Ampoule Toner 200ml",
 "manufacturer_product_page":"https://www.pixelpure.com/product/detail.html?product_no=24",
 "verified_product_gallery_image":"https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/c76386c3a6bb0bedee3ee4a97f03deb3.jpg",
 "observed_scene":"Full 200mL translucent pink toner bottle next to matching carton on pink studio background",
 "source_evidence":"Brand product page picture with matching 200mL bottle and carton"},
 {"family":"pending-30","product":"PixelPure Aura Radiance Serum 50ml",
 "manufacturer_product_page":"https://pixelpure.com/product/detail.html?product_no=25",
 "verified_product_gallery_image":"https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/small/20250430/2b4e82d8d9dbe09c42b2e38f48226df5.jpg",
 "observed_scene":"Five pastel pink 50mL serum bottles arranged on white ledge",
 "source_evidence":"Brand product page picture with identical 50mL product label"}
]
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def dhash(im):
 p=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return "".join("1" if p[x,y]>p[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(c!=d for c,d in zip(a,b))
def original_photos(family):
 ref=REC[family];path=Path(ref["internal_QA_archive"]["path"])
 assert path.is_file()
 out=[]
 with ZipFile(path,"r") as z:
  for entry in z.infolist():
   if not entry.filename.lower().endswith((".jpg",".jpeg")):continue
   b=z.read(entry.filename)
   with Image.open(BytesIO(b)) as x:
    x.load()
    if x.format!="JPEG":continue
    out.append({"name":entry.filename,"sha":sha256(b).hexdigest(),"dhash":dhash(x.convert("RGB"))})
 return out
def contact(family,photo,old_count,native):
 canvas=Image.new("RGB",(1080,1080),"#f7f7f7");d=ImageDraw.Draw(canvas)
 d.text((27,18),family.upper()+" | DIRECT FIRST-PARTY PHOTO DISCOVERY",font=font(27),fill="#333")
 d.text((27,63),"Only a source-photo candidate. Rights / exact stocked edition NOT approved.",font=font(16),fill="#a13b3b")
 box=(45,104,1035,929);d.rounded_rectangle(box,radius=14,fill="white",outline="#ddd",width=2)
 fit=ImageOps.contain(photo,(930,755),Image.Resampling.LANCZOS)
 canvas.paste(fit,(540-fit.width//2,128+(755-fit.height)//2))
 d.text((31,961),f"Original {native[0]}x{native[1]}  |  prior family sources {old_count}",font=font(19),fill="#4a4a4a")
 d.text((31,1006),"QA only, old 11 published families and 55 URLs unchanged.",font=font(18),fill="#a13b3b")
 return canvas
session=requests.Session();session.headers["User-Agent"]="Mozilla/5.0 (pixelpure-archive-photo-integrity-review)"
OUT.mkdir(parents=True)
results=[]
for info in T:
 fam=info["family"];previous=original_photos(fam)
 assert REC[fam]["category"]=="PARTIAL_PHOTO_ARCHIVE" and len(previous)==3
 errors=[];candidate=None;native=None;decision="NOT_COLLECTED"
 try:
  source=info["verified_product_gallery_image"]
  u=urlparse(source)
  if u.scheme!="https" or u.hostname!="ecimg.cafe24img.com" or "/pixelpure/web/product/extra/" not in u.path:raise ValueError("not the manufacturer image CDN")
  r=session.get(source,timeout=16)
  r.raise_for_status()
  if urlparse(r.url).hostname!="ecimg.cafe24img.com":raise ValueError("image redirect different domain")
  b=r.content
  if not 4000<len(b)<10_000_000:raise ValueError("invalid photo byte size")
  with Image.open(BytesIO(b)) as x:
   x.load()
   if x.format not in ("JPEG","PNG","WEBP"):raise ValueError("nonphoto source format")
   native=list(x.size);rgb=ImageOps.exif_transpose(x).convert("RGB")
  if min(native)<900:raise ValueError("native image below 900 pixels")
  h=sha256(b).hexdigest();p=dhash(rgb)
  nearest=min(dist(p,o["dhash"]) for o in previous)
  if h in {o["sha"] for o in previous} or nearest<5:
   decision="EXISTING_SOURCE_NEAR_DUPLICATE_NOT_ADDED"
  else:
   folder=OUT/fam;folder.mkdir(exist_ok=True)
   ext=".jpg" if b.startswith(b"\xff\xd8") else ".png" if b.startswith(b"\x89PNG") else ".webp"
   raw=folder/("01-official-original-unmodified"+ext);raw.write_bytes(b)
   ref=folder/"01-brand-photo-1080-INTERNAL-QA.jpg"
   canvas=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   canvas.save(ref,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(ref) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   assert ref.stat().st_size<2_000_000
   candidate={"original_path":str(raw),"original_sha256":h,"original_native_px":native,
    "reference_path":str(ref),"reference_sha256":sha256(ref.read_bytes()).hexdigest(),
    "near_distance_from_three_previous_sources":nearest,
    "actual_owned_stock_batch_identified":False,"commercial_image_usage_rights_granted":False,
    "brand_ownership_logo_verified":False,"retail_approved":False}
   contactpath=OUT/(fam+"-new-source-visual-CONTACT-1080-INTERNAL.jpg")
   contact(fam,rgb,len(previous),native).save(contactpath,"JPEG",quality=88,optimize=True,subsampling=0)
   decision="NEW_DISTINCT_OFFICIAL_PRODUCT_SOURCE_CANDIDATE_ARCHIVED"
 except Exception as e:
  errors.append(str(e)[:210])
  if decision=="NOT_COLLECTED":decision="OFFICIAL_IMAGE_FETCH_OR_TECH_QA_FAILED_HOLD"
 added=1 if candidate else 0
 st=S["families"][fam]
 st.update({"last_delta_version":"v2927",
  "release_status":"ADDITIONAL_BRAND_PHOTO_REFERENCE_CANDIDATE_RIGHTS_STOCK_HOLD" if added else "PREVIOUS_SOURCES_PRESERVED_OFFICIAL_IMAGE_NOT_ADDED",
  "v2927_new_nonduplicate_official_photo_sources":added,
  "v2927_unresolved_photo_slots_out_of_five":max(0,2-added),
  "v2927_new_source_path":candidate["reference_path"] if candidate else None,
  "latest_photo_QA_checkpoint":f"v2927 direct manufacturer product photo {decision}, {added} unseen original photo reference, {max(0,2-added)} remaining to five-source target; retail licensing and physical stock version still HOLD.",
  "sale_approved":False})
 results.append({**info,"prior_existing_photos":len(previous),"decision":decision,"new_reference":candidate,
  "new_images":added,"remaining_five_photo_shortfall":max(0,2-added),"errors":errors})
manifest={"version":"v2927","baseline":"v2926","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "manufacturer_source_families_attempted":2,"new_native_official_photo_candidates_archived":sum(x["new_images"] for x in results),
 "prior_11_public_image_families_changed":0,"prior_55_verified_public_URLs_changed":0,
 "prior_archive_files_modified":0,"new_sale_approved_images":0,"new_public_URLs":0,
 "previous_missing_11_source_slots":11,
 "new_photo_source_gap_after_this_batch":11-sum(x["new_images"] for x in results),
 "final_spreadsheet_shared":False,"results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
S["version"]="v2927";S["baseline"]="v2926";S["new_sales_approvals"]=0;S["new_public_URLs"]=0;S["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2927.json").write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2927","archived":manifest["new_native_official_photo_candidates_archived"],"remaining":manifest["new_photo_source_gap_after_this_batch"],
 "groups":{x["family"]:x["decision"] for x in results}},ensure_ascii=False))
