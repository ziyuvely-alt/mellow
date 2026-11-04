#!/usr/bin/env python3
"""v2749: independently trace shade 25 & 27 official product-variant photography.
Do not fabricate shaded compacts by recoloring N21/N23 photos; unknown or generic
product galleries never count as per-shade source evidence. QA-only, original
11 released families and 55 public URLs immutable.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,re,json,hashlib,base64
OUT=Path("qa-review/v2749-MISSHA-coverlasting-N25-N27-official-variant-source-proof")
assert not OUT.exists();OUT.mkdir(parents=True)
PAGE="https://www.misshame.com/products/magic-cushion-cover-lasting"
HEAD={"User-Agent":"Mozilla/5.0 (compatible; QA-evidence/1.0)","Accept":"application/json,text/html,image/jpeg,image/png,image/webp,*/*"}
report={"version":"v2749","baseline":"v2748","family":"pending-01",
 "product":"MISSHA Magic Cushion Cover Lasting 15g",
 "brand_operated_store":PAGE,
 "N21_photo_already_preserved":"v2748",
 "N23_photo_already_preserved":"v2747",
 "new_source_colors_requested":["25","27"],
 "do_not_copy_N21_N23_compacts_into_25_27":True,
 "no_fake_swatch_generation":True,"photo_license_verified":False,
 "exact_user_owned_Korean_stock_generation_verified":False,
 "new_retail_approved":0,"original_11_approved_untouched":True,
 "previous_55_URLs_unchanged":True,"final_spreadsheet_shared":False,
 "source_status":"NOT_ATTEMPTED","shades":[]}
def num(text):
 m=re.search(r"(?:no[. ]*|#)?(21|23|25|27)(?:\D|$)",str(text),re.I)
 return m.group(1) if m else None
def url(photo):
 if isinstance(photo,str):return photo
 if isinstance(photo,dict):return photo.get("src") or photo.get("url")
 return None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 r=requests.get(PAGE+".js",headers=HEAD,timeout=20);r.raise_for_status()
 data=r.json()
 title=data.get("title") or ""
 if "magic cushion cover lasting" not in title.lower():
  raise ValueError("Incorrect product title: "+title[:140])
 report["source_product_title"]=title
 variants=data.get("variants",[])
 for k in ("25","27"):
  candidates=[v for v in variants if num(v.get("title"))==k]
  row={"shade":k,"variants_count":len(candidates),"status":"HOLD_NO_EXACT_VARIANT_PHOTO",
   "source_item_title":None,"sku":None,"variant_id":None,
   "source_photos":[],"manual_packaging_and_shade_review_required":True}
  if not candidates:
   row["status"]="HOLD_SHADE_NOT_LISTED_BY_SOURCE"
   report["shades"].append(row);continue
  v=candidates[0]
  row.update({"source_item_title":v.get("title"),"sku":v.get("sku"),"variant_id":v.get("id")})
  vc=v.get("featured_image")
  linked=[]
  if url(vc):linked.append((url(vc),"variant_featured_image"))
  if vc and isinstance(vc,dict):
   fid=str(vc.get("id") or "")
  else:fid=""
  for item in data.get("images",[]):
   if not isinstance(item,dict):continue
   vid=[str(x) for x in item.get("variant_ids",[])]
   if str(v.get("id")) in vid or (fid and str(item.get("id"))==fid):
    if url(item):linked.append((url(item),"explicit_variant_id"))
  # Shopify JSON can expose variant-id mapping under media as well.
  for item in data.get("media",[]):
   if not isinstance(item,dict):continue
   vids=[str(x) for x in item.get("variant_ids",[])]
   if str(v.get("id")) in vids:
    u=url(item.get("preview_image")) or url(item)
    if u:linked.append((u,"variant_specific_media"))
  seen=set()
  for u,reason in linked:
   u=urljoin(PAGE,u)
   host=(urlparse(u).hostname or "").lower()
   if not host.endswith("shopify.com") and not host.endswith("shopifycdn.net"):continue
   if u in seen:continue
   seen.add(u)
   try:
    raw=requests.get(u,headers=HEAD,timeout=15);raw.raise_for_status()
    if len(raw.content)>8000000:continue
    pic=Image.open(BytesIO(raw.content));pic.load()
    if min(pic.size)<380:continue
    folder=OUT/f"shade-{k}";folder.mkdir(exist_ok=True)
    src=folder/f"01-real-variant-linked-{k}-source-reference-QA.jpg"
    rgb=ImageOps.exif_transpose(pic).convert("RGB")
    canvas=Image.new("RGB",(1080,1080),"white")
    fitted=ImageOps.contain(rgb,(1040,1040),Image.Resampling.LANCZOS)
    canvas.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
    canvas.save(src,"JPEG",quality=92,optimize=True)
    if src.stat().st_size>=2_000_000:
      src.unlink();continue
    row["source_photos"].append({"file":str(src.relative_to(OUT)),"source_url":u,
      "photo_native_px":list(pic.size),"sha256":sha(src),"variant_relation":reason})
    row["status"]="VARIANT_LINKED_PHOTO_CAPTURED_VISUAL_QA_REQUIRED"
    break
   except (requests.RequestException,OSError,ValueError) as e:
    row["last_source_error"]=str(e)[:160]
  report["shades"].append(row)
 report["variant_titles"]=[x.get("title") for x in variants]
 report["source_status"]="OFFICIAL_PRODUCT_VARIANTS_INSPECTED"
except Exception as exc:
 report["source_status"]="HOLD_OFFICIAL_VARIANT_CATALOG_UNAVAILABLE"
 report["failure_type"]=type(exc).__name__
 report["failure_message"]=str(exc)[:300]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",26)
board=Image.new("RGB",(1150,645),"#f0f0ee")
d=ImageDraw.Draw(board)
d.text((15,13),"v2749 NO.25 / NO.27 EXPLICIT VARIANT PHOTOGRAPHS | QA ONLY",font=font,fill="#252525")
for i,row in enumerate(report["shades"]):
 x=18+i*555
 d.text((x,64),"NO."+row["shade"],font=font,fill="#252525")
 if row["source_photos"]:
  imgfile=OUT/row["source_photos"][0]["file"]
  with Image.open(imgfile) as im:thumb=im.convert("RGB").resize((432,432),Image.Resampling.LANCZOS)
  board.paste(thumb,(x,110))
 else:
  d.text((x,195),"NO VERIFIED SHADE PHOTO",font=font,fill="#575757")
 d.text((x,565),row["status"][:30],font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18),fill="#575757")
proof=OUT/"v2749-independent-shade-sources.jpg"
board.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2749-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["actual_new_independently_variant_linked_photo_count"]=sum(len(x["source_photos"]) for x in report["shades"])
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2749","official_catalog":report["source_status"],
 "N25_and_N27":{x["shade"]:x["status"] for x in report["shades"]},
 "genuine_independent_photo_count":report["actual_new_independently_variant_linked_photo_count"],
 "retail_approved":0}))
