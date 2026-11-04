#!/usr/bin/env python3
"""v2783 retrieve NEW exact Goodal Vita-C Cream Alpha official brand image sources.

Source is Club Clio / Goodal's product-specific store page. Reuse NOTHING from
the previously blocked generic v2781 routine card. Exact title and product
product-gallery media are required. Raw pixels are source-only references;
no commercial photo/model rights or stock edition attested. No existing QA or
published images changed.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse,urljoin
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,base64,hashlib
OUT=Path("qa-review/v2783-goodal-cream-alpha-official-distinct-photo-sources")
assert not OUT.exists()
OUT.mkdir(parents=True)
PAGE="https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-cream-advanced-ver"
headers={"User-Agent":"Mozilla/5.0 (compatible; SourceQA/1.0)","Accept":"application/json,image/avif,image/webp,image/jpeg,image/png,*/*"}
def digest(raw):return hashlib.sha256(raw).hexdigest()
report={"version":"v2783","family":"pending-19","baseline":"v2782",
"page":PAGE,"product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
"raw_same_product_gallery_urls":[],"new_source_photo_candidates":[],
"commercial_photo_redistribution_rights_verified":False,
"actual_user_stock_edition_verified":False,
"old_11_approved_families_unchanged":True,
"old_55_published_URLs_unchanged":True,
"newly_retail_approved":False,"final_XLSX_shared":False}
try:
 resp=requests.get(PAGE+".js",headers=headers,timeout=20);resp.raise_for_status()
 item=resp.json();title=item.get("title","")
 assert "goodal" in title.lower() and "cream" in title.lower()
 assert ("advanced" in title.lower() or "alpha" in title.lower()),title
 if "bundle" in title.lower() or "set" in title.lower():raise ValueError("Gallery is not a single-cream item")
 report["actual_english_brand_item_title"]=title
 report["product_variant_skus"]=[{"title":x.get("title"),"sku":x.get("sku")} for x in item.get("variants",[])[:10]]
 photos=[]
 for obj in item.get("images",[]):
  u=obj if isinstance(obj,str) else (obj.get("src") or "")
  if not u:continue
  u=urljoin(PAGE,u)
  host=(urlparse(u).hostname or "").lower()
  if not (host.endswith("shopify.com") or host.endswith("shopifycdn.com") or host.endswith("clubclio.shop")):continue
  if u not in photos:photos.append(u)
 report["raw_same_product_gallery_urls"]=photos[:30]
 if not photos:raise ValueError("Exact-product gallery has no valid images")
 hashes=set()
 for u in photos[:18]:
  try:
   response=requests.get(u,headers=headers,timeout=15);response.raise_for_status()
   raw=response.content
   if len(raw)>8_000_000:continue
   if digest(raw) in hashes:continue
   pic=Image.open(BytesIO(raw));pic.load()
   if min(pic.size)<450:continue
   # Ignore tiny thumbnail variants; preserve only exact product-gallery sources.
   photo=ImageOps.exif_transpose(pic).convert("RGB")
   frame=Image.new("RGB",(1080,1080),"white")
   scaled=ImageOps.contain(photo,(1060,1060),Image.Resampling.LANCZOS)
   frame.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
   target=OUT/f"{len(report['new_source_photo_candidates'])+1:02d}-official-product-gallery-QA.jpg"
   frame.save(target,"JPEG",quality=90,optimize=True,subsampling=0)
   if target.stat().st_size>=2_000_000:target.unlink();continue
   hashes.add(digest(raw))
   report["new_source_photo_candidates"].append({
       "candidate":target.name,"official_original_url":u,
       "original_size_px":list(pic.size),
       "original_sha256":digest(raw),
       "jpg_sha256":digest(target.read_bytes()),
       "bytes":target.stat().st_size,
       "visually_exact_50ml_alpha_generation_verified":False,
       "license_clearance":"HOLD"})
   if len(report["new_source_photo_candidates"])>=12:break
  except (OSError,ValueError,requests.RequestException):continue
 report["status"]="CANDIDATES_STAGED_FOR_REAL_FRAME_VISUAL_QA" if report["new_source_photo_candidates"] else "HOLD_NO_DOWNLOADABLE_EXACT_PRODUCT_PHOTOS"
except Exception as e:
 report["status"]="HOLD_PRODUCT_PAGE_OR_GALLERY_INACCESSIBLE"
 report["error_type"]=type(e).__name__
 report["error"]=str(e)[:400]
if report["new_source_photo_candidates"]:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
 cols=4;size=300;stride=374
 rows=(len(report["new_source_photo_candidates"])+3)//4
 contact=Image.new("RGB",(1510,90+rows*375),"#f0f0ee")
 draw=ImageDraw.Draw(contact)
 draw.text((16,16),"v2783 GOODAL CREAM ALPHA / BRAND PRODUCT GALLERY / PHOTO RIGHTS HOLD",font=font,fill="#303030")
 for ix,r in enumerate(report["new_source_photo_candidates"]):
  with Image.open(OUT/r["candidate"]) as im:thumb=im.convert("RGB").resize((300,300),Image.Resampling.LANCZOS)
  px=16+ix%4*stride;py=62+ix//4*375
  contact.paste(thumb,(px,py))
  draw.text((px,py+309),f"BRAND GALLERY {ix+1:02d}  /  QA ONLY",font=font,fill="#303030")
 preview=OUT/"v2783-official-goodal-contact.jpg"
 contact.save(preview,"JPEG",quality=84,optimize=True)
 (OUT/"v2783-contact.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2783","status":report["status"],
 "same_product_gallery_candidates":len(report["new_source_photo_candidates"]),
 "total_gallery_urls":len(report["raw_same_product_gallery_urls"]),
 "retail_approved":False}))
