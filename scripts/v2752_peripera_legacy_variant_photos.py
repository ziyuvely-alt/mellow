#!/usr/bin/env python3
"""v2752 only NEW work: external legacy-edition PERIPERA Ink Mood Glowy Tint
01..20 REAL variant linked source-photo evidence; NOT rendered swatch artwork.
Different editions may reuse shade numbers; never equate 2026 26AD formula,
shade names, packaging, or color swatches with this old Ink Mood Glowy series.
All copied photos are QA-only pending rights and original owned inventory match.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from urllib.parse import urljoin,urlparse
from io import BytesIO
import json,requests,re,hashlib,base64
OUT=Path("qa-review/v2752-peripera-legacy-01to20-variant-photo-evidence")
assert not OUT.exists()
OUT.mkdir(parents=True)
URL="https://wcosmetics.com.au/products/peripera-ink-mood-glowy-tint"
HEAD={"User-Agent":"Mozilla/5.0 (compatible; ExactVariantEvidence/1.0)","Accept":"application/json,text/html,image/webp,image/png,image/jpeg,*/*"}
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(B if b else F,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"version":"v2752","source_product_page":URL,"source_class":"THIRD_PARTY_LEGACY_VARIANT_CATALOG",
 "legacy_item":"PERIPERA Ink Mood Glowy Tint older line (not 26AD Mood Glowy Tint)",
 "selected_shades":"01..20 only","exclude_26AD_and_21_plus":True,
 "retail_authorization":False,"item_inventory_generation_verified":False,
 "original_MK_logo_verified":False,"photo_republication_license_verified":False,
 "approved_11_product_families_untouched":True,"public_55_verified_urls_untouched":True,
 "no_final_spreadsheet_shared":True,"records":[]}
variant_map={}
try:
 res=requests.get(URL+".js",headers=HEAD,timeout=19);res.raise_for_status()
 payload=res.json()
 title=payload.get("title","")
 report["shopify_catalog_product_title"]=title
 if not("ink mood glowy" in title.lower() and "tint" in title.lower()):
  raise ValueError("Catalog product is NOT the legacy Ink Mood Glowy Tint")
 variants=payload.get("variants",[])
 for v in variants:
  raw=str(v.get("public_title") or v.get("title") or "")
  m=re.match(r"^\s*#?\s*(\d{1,2})(?=\D|$)",raw)
  if not m:continue
  shade=int(m.group(1))
  if not 1<=shade<=20:continue
  variant_map.setdefault(shade,[]).append(v)
 report["catalog_numbered_variants_01to20"]=len(variant_map)
 report["same_number_duplicate_variant_options"]={str(k):[str(v.get("title","")) for v in vals] for k,vals in variant_map.items() if len(vals)>1}
 for n in range(1,21):
  shade=f"{n:02d}"
  matches=variant_map.get(n,[])
  row={"shade":shade,"merchant_variant_count":len(matches),"source_present":False,
       "exact_variant_photo_linked":False,"status":"HOLD_MISSING_VARIANT",
       "retail_approved":False}
  if len(matches)!=1:
   row["status"]="HOLD_DUPLICATE_OR_NO_VARIANT"
   report["records"].append(row);continue
  v=matches[0]
  name=str(v.get("public_title") or v.get("title") or "")
  row.update({"merchant_name":name,"variant_id":str(v.get("id") or ""),"sku":str(v.get("sku") or "")})
  pic=v.get("featured_image")
  url=""
  if isinstance(pic,dict):url=pic.get("src") or ""
  elif isinstance(pic,str):url=pic
  # Shopify variant media sometimes only exposes featured_image.id; do not
  # substitute generic top product shot, as shade-specific identity is not proven.
  if not url and v.get("featured_media") and isinstance(v["featured_media"],dict):
   url=(v["featured_media"].get("preview_image") or {}).get("src") or ""
  if not url:
   row["status"]="HOLD_NO_VARIANT_SPECIFIC_IMAGE"
   report["records"].append(row);continue
  url=urljoin(URL,url)
  row["variant_photo_url"]=url
  host=(urlparse(url).hostname or "").lower()
  if not any(host.endswith(x) for x in ["cdn.shopify.com","shopify.com","wcosmetics.com.au"]):
   row["status"]="HOLD_IMAGE_HOST_NOT_APPROVED_FOR_SOURCE_EVIDENCE"
   report["records"].append(row);continue
  try:
   download=requests.get(url,headers=HEAD,timeout=13);download.raise_for_status()
   if len(download.content)>8_000_000:raise ValueError("Image too large")
   orig=Image.open(BytesIO(download.content));orig.load()
   if min(orig.size)<400:raise ValueError("Image too small")
   img=ImageOps.exif_transpose(orig).convert("RGB")
   # Entire source is fitted with no fake product edit or color chip generation.
   target=Image.new("RGB",(1080,1080),"white")
   contained=ImageOps.contain(img,(1040,1040),Image.Resampling.LANCZOS)
   target.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
   save=OUT/f"{shade}-legacy-merchant-variant-linked-source-QA.jpg"
   target.save(save,"JPEG",quality=89,optimize=True,subsampling=0)
   if save.stat().st_size>=2_000_000:raise ValueError("Shopee QA JPG too big")
   row.update({"status":"EXACT_VARIANT_LINKED_PHOTO_NEEDS_PACKAGING_QA",
       "source_present":True,"exact_variant_photo_linked":True,
       "image_file":save.name,"source_dimensions":list(orig.size),
       "source_sha256":hashlib.sha256(download.content).hexdigest(),
       "qa_JPG_sha256":sha(save),"qa_JPG_bytes":save.stat().st_size})
  except Exception as exc:
   row.update({"status":"HOLD_IMAGE_FETCH_OR_FORMAT_FAILED","error":str(exc)[:160]})
  report["records"].append(row)
except Exception as exc:
 report.update({"catalog_request_status":"HOLD_CATALOG_FETCH_OR_IDENTITY",
                "catalog_error_type":type(exc).__name__,
                "catalog_error":str(exc)[:240]})
 if not report["records"]:
  report["records"]=[{"shade":f"{n:02d}","status":"HOLD_UNREADABLE_EXTERNAL_VARIANT_CATALOG","retail_approved":False} for n in range(1,21)]
# Repeat JPG photo bytes could mean variant mapping is fake; do not mark as proven
hashes={}
for row in report["records"]:
 if row.get("qa_JPG_sha256"):
  hashes.setdefault(row["qa_JPG_sha256"],[]).append(row["shade"])
report["same_photo_hash_across_different_shades"]=[{"sha256":h,"shades":v} for h,v in hashes.items() if len(v)>1]
for repeat in report["same_photo_hash_across_different_shades"]:
 for rec in report["records"]:
  if rec["shade"] in repeat["shades"]:
   rec["exact_variant_photo_linked"]=False
   rec["status"]="HOLD_SAME_IMAGE_SHARED_BY_MULTIPLE_VARIANTS"
report["physical_variant_source_JPGs"]=sum(x.get("source_present",False) for x in report["records"])
report["unique_variant_source_JPGs"]=sum(x.get("exact_variant_photo_linked",False) for x in report["records"])
report["old_owned_stock_specific_variant_photos_verified"]=False
report["real_color_swatches_generated"]=0
report["retail_newly_approved"]=0
report["official_brand_gallery_verified"]=False
# Photo contacts, only raw source photos; do not claim the thumbnails are official swatches.
for page in range(2):
 subset=report["records"][page*10:(page+1)*10]
 canvas=Image.new("RGB",(1820,720),"#f1f1f0")
 d=ImageDraw.Draw(canvas)
 d.text((18,14),f"v2752 LEGACY PERIPERA ACTUAL MERCHANT VARIANT SOURCES | {page+1}/2 | NOT RETAIL",font=font(23,True),fill="#292929")
 for index,entry in enumerate(subset):
  px=16+(index%5)*362;py=58+(index//5)*323
  if entry.get("image_file"):
   with Image.open(OUT/entry["image_file"]) as im:
    thumb=im.convert("RGB").resize((272,272),Image.Resampling.LANCZOS)
   canvas.paste(thumb,(px,py))
  d.text((px,py+274),entry["shade"]+" "+str(entry.get("status","HOLD"))[:21],font=font(19),fill="#323232")
 proof=OUT/f"v2752-legacy-peripera-photo-candidates-page-{page+1}.jpg"
 canvas.save(proof,"JPEG",quality=81,optimize=True)
 (OUT/f"v2752-proof-page-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2752","catalog":report.get("catalog_request_status","FETCHED"),
 "numbered_variants":report.get("catalog_numbered_variants_01to20",0),
 "downloaded":report["physical_variant_source_JPGs"],
 "unique_linked":report["unique_variant_source_JPGs"],
 "duplicate_groups":len(report["same_photo_hash_across_different_shades"]),
 "new_sale_approvals":0}))
