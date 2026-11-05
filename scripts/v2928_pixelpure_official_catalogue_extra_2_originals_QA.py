#!/usr/bin/env python3
"""v2928 direct PixelPure official catalogue image recovery, only genuinely unseen originals.
Never re-package or modify prior QA/published files. Two official-site CDN source images,
both with independently confirmed product name/volume. Internal QA only.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, requests, time

Q=Path("qa-review")
PRE=Q/"v2927-pixelpure-two-direct-official-source-originals-dedupe-QA"
BASE=Q/"v2926-30family-26sourcezip-qa-state-and-next-action-ledger"
P19=Q/"v2919-reconcile-parallel-v2917-and-pixelpure-extra-big-firstparty-QA"
OUT=Q/"v2928-pixelpure-2-known-official-catalogue-images-conditional-new-QA"
assert not OUT.exists()
s=json.loads((PRE/"stock30-incremental-state-v2927.json").read_text(encoding="utf-8"))
m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
p19=json.loads((P19/"manifest.json").read_text(encoding="utf-8"))
assert s["version"]=="v2927" and len(s["families"])==30 and m["sha256_and_ZIP_CRC_verified_archives"]==26
prior={x["family"]:x for x in m["family_records"]}
cfg=[
 {"family":"pending-29","product":"PixelPure Radiance Aqua Soothing Cream 50ml","source":
 "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/f8d51ba2fbbf7cb558808d00a2f1317a.jpg",
 "official_page":"https://eng.pixelpure.com/product/detail.html?product_no=26",
 "role":"manufacturer official 50 mL closed cream jar with product name legible"},
 {"family":"pending-30","product":"PixelPure Aura Radiance Serum 50ml","source":
 "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/small/20260213/b1538dd05d1d8b3a354a3690e007b309.jpg",
 "official_page":"https://eng.pixelpure.com/category/best/50/",
 "role":"manufacturer catalogue 50 mL pink serum three bottles and lotion stream"}
]
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def dhash(img):
 gray=ImageOps.grayscale(ImageOps.fit(img,(9,8))).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def hamming(a,b):return sum(x!=y for x,y in zip(a,b))
def image_bytes_to_hash(b):
 with Image.open(BytesIO(b)) as im:
  im.load()
  if im.format!="JPEG":return None
  return dhash(ImageOps.exif_transpose(im).convert("RGB"))
def existing(family):
 row=prior[family]
 result=[]
 with ZipFile(row["internal_QA_archive"]["path"],"r") as z:
  for name in z.namelist():
   b=z.read(name);h=image_bytes_to_hash(b)
   if h:result.append({"source":"legacy ZIP "+name,"sha256":sha256(b).hexdigest(),"dhash":h})
 for p in p19["pixelpure_results"]:
  if p["family"]!=family:continue
  for photo in p["new_images"]:
   b=Path(photo["reference_jpg"]).read_bytes()
   result.append({"source":photo["reference_jpg"],"sha256":sha256(b).hexdigest(),"dhash":image_bytes_to_hash(b)})
 if family=="pending-30":
  prev=PRE/"pending-30/01-brand-photo-1080-INTERNAL-QA.jpg"
  b=prev.read_bytes()
  result.append({"source":str(prev),"sha256":sha256(b).hexdigest(),"dhash":image_bytes_to_hash(b)})
 return result
def card(fam,image,px):
 c=Image.new("RGB",(1080,1080),"#f7f7f8");d=ImageDraw.Draw(c)
 d.text((25,18),fam.upper()+" / OFFICIAL CATALOGUE PHOTO v2928",font=font(26),fill="#2b2b2b")
 d.text((25,62),"Source-reference candidate only. Commercial use and owned stock HOLD.",font=font(16),fill="#9a3030")
 fit=ImageOps.contain(image,(1020,866),Image.Resampling.LANCZOS)
 c.paste(fit,((1080-fit.width)//2,91+(866-fit.height)//2))
 d.text((25,994),f"Native official source {px[0]} x {px[1]}  |  no photo fabrication",font=font(17),fill="#535353")
 return c
sess=requests.Session();sess.headers.update({"User-Agent":"Mozilla/5.0 (internal original-image product-edition QA)"})
OUT.mkdir(parents=True)
records=[]
for x in cfg:
 fam=x["family"];old=existing(fam);errors=[];new=None;reason="NO_NEW_ORIGINAL_ADDED"
 assert len(old)>=4 and len(old)<=7, (fam,len(old))
 try:
  u=urlparse(x["source"])
  assert u.scheme=="https" and u.hostname=="ecimg.cafe24img.com" and "/pixelpure/web/product/" in u.path
  rsp=sess.get(x["source"],timeout=16);rsp.raise_for_status()
  assert urlparse(rsp.url).hostname=="ecimg.cafe24img.com"
  b=rsp.content
  if not 4000<len(b)<8_000_000:raise ValueError("invalid source byte size")
  with Image.open(BytesIO(b)) as z:
   z.load()
   if z.format not in ("JPEG","PNG","WEBP"):raise ValueError("source not an image")
   px=list(z.size);im=ImageOps.exif_transpose(z).convert("RGB")
  if min(px)<900:raise ValueError("source below original-native 900px")
  h=sha256(b).hexdigest();p=dhash(im)
  min_dist=min(hamming(p,z["dhash"]) for z in old)
  if any(z["sha256"]==h for z in old) or min_dist<5:
   reason="PRIOR_SOURCE_DUPLICATE_OR_NEAR_DUPLICATE_SKIP"
  else:
   sub=OUT/fam;sub.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[Image.open(BytesIO(b)).format]
   raw=sub/("01-brand-original-byte-unchanged"+ext)
   raw.write_bytes(b)
   cv=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(im,(1080,1080),Image.Resampling.LANCZOS)
   cv.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   jpg=sub/"01-official-photo-1080-NOT-RETAIL.jpg"
   cv.save(jpg,"JPEG",quality=89,optimize=True,subsampling=0)
   with Image.open(jpg) as chk: assert chk.format=="JPEG" and chk.size==(1080,1080)
   assert jpg.stat().st_size<2_000_000
   v=OUT/(fam+"-official-catalogue-CONTACT-INTERNAL.jpg")
   card(fam,im,px).save(v,"JPEG",quality=88,optimize=True,subsampling=0)
   new={"source_original":str(raw),"source_original_sha256":h,"native_px":px,
    "reference_1080":str(jpg),"reference_sha256":sha256(jpg.read_bytes()).hexdigest(),
    "dhash_distance_to_closest_prior":min_dist,"internal_visual_contact":str(v),
    "retail_rights_cleared":False,"physical_inventory_edition_verified":False,"retail_approved":False}
   reason="NEW_OFFICIAL_SITE_IMAGE_CANDIDATE_ADDED"
 except Exception as e:
  errors.append(str(e)[:230]);reason="FETCH_OR_NATIVE_PHOTO_QA_FAILED"
 add=int(new is not None)
 state=s["families"][fam]
 state.update({"last_delta_version":"v2928","sale_approved":False,
  "release_status":"NEW_BRAND_IMAGE_QA_CANDIDATE_STOCK_RIGHTS_HOLD" if add else "PRIOR_SOURCES_ONLY_NEW_CANDIDATE_DUPLICATE_OR_FAILED",
  "v2928_extra_verified_native_image_candidates":add,
  "v2928_additional_reference_image":new["reference_1080"] if new else None,
  "latest_photo_QA_checkpoint":f"v2928 official PixelPure photo {reason}; {add} new original candidate, no previous image altered, commercial usage rights and physical stock still HOLD."})
 records.append({**x,"prior_sources_screened":len(old),"decision":reason,"new_source_count":add,"new_candidate":new,"errors":errors})
manifest={"version":"v2928","baseline":"v2927","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "official_product_CDN_images_attempted":2,"new_unique_native_originals_saved":sum(x["new_source_count"] for x in records),
 "prior_total_missing_source_slots":9,"remaining_source_slots":9-sum(x["new_source_count"] for x in records),
 "approved_families_changed":0,"old_55_verified_public_URLs_changed":0,"old_QA_files_overwritten":0,
 "new_retail_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False,"results":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s["version"]="v2928";s["baseline"]="v2927";s["new_sales_approvals"]=0;s["new_public_URLs"]=0;s["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2928.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2928","new_originals":manifest["new_unique_native_originals_saved"],
 "missing_remaining":manifest["remaining_source_slots"],
 "results":{x["family"]:x["decision"] for x in records},
 "retail_approvals":0},ensure_ascii=False))
