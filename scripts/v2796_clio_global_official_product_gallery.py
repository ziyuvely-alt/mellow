#!/usr/bin/env python3
"""v2796 first-party global CLUBCLIO Shopify exact product gallery source.
Domestic ClubClio goodsView pages blocked high-res detail HTML extraction in v2794.
Use product-specific Shopify JSON from https://clubclio.shop exactly matching
CLIO Mesh Glow Essential Cushion, which was set-image only in pending-06.

STRICT: store *new* native-resolution photo references under isolated QA branch.
No fake logo, no stock edition claim, no retail use until photograph licensing.
Do not stage image if source SKU/edition not same product. Preserve old files.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json,requests,hashlib,base64,re
BASE="https://clubclio.shop"
HANDLE="clio-kill-cover-mesh-glow-cushion-set-refill"
OUT=Path("qa-review/v2796-clio-meshglow-essential-global-original-gallery-source")
assert not OUT.exists();OUT.mkdir(parents=True)
UA={"User-Agent":"Mozilla/5.0 (compatible; StockPhotoQualityAudit/1.0)","Accept":"application/json,text/javascript,*/*"}
def sha(a):return hashlib.sha256(a).hexdigest()
sources=[]
candidate_json_paths=[
 f"{BASE}/products/{HANDLE}.js",
 f"{BASE}/products/{HANDLE}.json"
]
gallery=[];product={}
for url in candidate_json_paths:
 try:
  r=requests.get(url,headers=UA,timeout=17)
  if r.status_code!=200:continue
  raw=r.json();obj=raw.get("product",raw)
  title=str(obj.get("title",""))
  if "mesh glow" not in title.lower() and "메쉬 글로우" not in title:
   continue
  if "cushion" not in title.lower() and "쿠션" not in title:
   continue
  product={"url":url,"title":title,"handle":obj.get("handle"),"body_snippet":str(obj.get("body_html",""))[:350],
           "variants":[{"title":v.get("title"),"sku":v.get("sku"),"available":v.get("available"),
                         "grams":v.get("grams"),"option1":v.get("option1")} for v in obj.get("variants",[])[:20]],
           "source_json_sha256":sha(r.content)}
  imgs=obj.get("images",[])
  for item in imgs:
   if isinstance(item,str):gallery.append({"url":item,"alt":""})
   elif isinstance(item,dict):
    u=item.get("src") or item.get("url") or ""
    gallery.append({"url":u,"alt":item.get("alt") or ""})
  # Also nested product media can expose image URLs missing from images.
  for m in obj.get("media",[]):
   if not isinstance(m,dict):continue
   src=m.get("src") or (m.get("preview_image") or {}).get("src")
   if src:gallery.append({"url":src,"alt":m.get("alt") or ""})
  break
 except (requests.RequestException,ValueError,TypeError):continue
dedup=set();photos=[]
for candidate in gallery[:22]:
 u=candidate["url"]
 if not u:continue
 if u.startswith("//"):u="https:"+u
 if u.startswith("/"):u=BASE+u
 p=urlparse(u)
 if p.scheme!="https" or p.hostname not in ("cdn.shopify.com","clubclio.shop","www.clubclio.shop"):
  continue
 # Shopify official photo URLs only, not links from random web search.
 if u in dedup:continue
 dedup.add(u)
 if len(photos)>=12:break
 try:
  rr=requests.get(u,headers={"User-Agent":UA["User-Agent"],"Referer":f"{BASE}/products/{HANDLE}"},timeout=18)
  if rr.status_code!=200 or not(15000<len(rr.content)<12000000):continue
  pic=Image.open(BytesIO(rr.content));pic.load()
  w,h=pic.size
  if min(w,h)<500 or max(w,h)<850:continue
  rgb=ImageOps.exif_transpose(pic).convert("RGB")
  ph=sha(rr.content)
  if any(x["original_source_sha256"]==ph for x in photos):continue
  n=len(photos)+1
  if pic.format=="JPEG":
   original=OUT/f"{n:02d}-official-global-gallery-NATIVE-original.jpg"
   original.write_bytes(rr.content)
  else:
   original=OUT/f"{n:02d}-official-global-gallery-NATIVE-original.png"
   pic.save(original,optimize=True)
  thumb=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white")
  canvas.paste(thumb,((1080-thumb.width)//2,(1080-thumb.height)//2))
  jpg=OUT/f"{n:02d}-source-photo-1080-only-QA.jpg"
  canvas.save(jpg,"JPEG",quality=90,optimize=True)
  if jpg.stat().st_size>=2_000_000:
   original.unlink();jpg.unlink();continue
  photos.append({"source_url":u,"source_alt":candidate["alt"],"source_native_dimensions":[w,h],
     "original_source_sha256":ph,"native_file":original.name,"QA_1080_JPG":jpg.name,
     "QA_SHA256":sha(jpg.read_bytes()),"QA_file_bytes":jpg.stat().st_size,
     "stock_variant_confirmed":False,"standalone_photo_confirmed":False,
     "photo_rights_for_redistribution_verified":False,"retail_approved":False})
 except (OSError,ValueError,requests.RequestException):continue
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
ncols=4;rows=max(1,(len(photos)+ncols-1)//ncols)
sheet=Image.new("RGB",(1690,80+390*rows),"#f0f0ef")
d=ImageDraw.Draw(sheet)
d.text((16,16),"v2796 CLIO Global Official Product Gallery | source QA | NOT FOR SALE",font=font,fill="#333333")
for idx,x in enumerate(photos):
 with Image.open(OUT/x["QA_1080_JPG"]) as im:
  tile=im.convert("RGB").resize((328,328),Image.Resampling.LANCZOS)
 px=18+(idx%4)*415;py=60+(idx//4)*390
 sheet.paste(tile,(px,py))
 d.text((px,py+338),f"{idx+1} | {x['source_native_dimensions'][0]}x{x['source_native_dimensions'][1]} native",font=font,fill="#282828")
if not photos:d.text((23,110),"No new exact-item official full-res product gallery photographs accessible.",font=font,fill="#444444")
contact=OUT/"v2796-global-official-photo-contact.jpg"
sheet.save(contact,"JPEG",quality=83,optimize=True)
(OUT/"v2796-photo-contact.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
manifest={
 "version":"v2796","baseline":"v2795",
 "target_family":"pending-06","product":"CLIO Kill Cover Mesh Glow Essential Cushion",
 "source_product_url":f"{BASE}/products/{HANDLE}",
 "product_identity_from_firstparty_json":product,
 "new_official_gallery_highres_reference_images":len(photos),
 "old_502_600px_catalog_thumbnail_downloads_repeated":0,
 "photo_records":photos,
 "release_status":"HOLD_ORIGINAL_PHOTO_RIGHTS_OWNED_STOCK_AND_BUNDLE_CONTENT",
 "old_approved_11_groups_modified":False,"old_55_public_URLs_modified":False,
 "previous_QA_files_modified":False,"new_retail_approvals":0,
 "final_excel_or_sheets_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2796","json_title":product.get("title"),
"gallery_urls":len(gallery),"new_highres_photos":len(photos),
"new_approvals":0},ensure_ascii=False))
