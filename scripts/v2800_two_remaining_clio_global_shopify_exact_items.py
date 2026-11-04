#!/usr/bin/env python3
"""v2800 source-only investigation into two still-blocked CLIO global listings.

Search official Shopify products, not the same domestic thumbnails or new
invented photos. Only product IDs with exact keyword/mini matching are eligible.
Stage originals if independently listed, verify high native dimensions.
No retail license or actual owned-stock unit approval, never alter prior QA.
"""
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,hashlib,base64,re
BASE="https://clubclio.shop"
OUT=Path("qa-review/v2800-two-remaining-clio-global-official-item-gallery-investigation")
assert not OUT.exists()
OUT.mkdir(parents=True)
UA={"User-Agent":"Mozilla/5.0 (compatible; ProductGalleryAudit/1.0)","Accept":"application/json"}
CASES=[
 dict(family="pending-05",product="CLIO Founwear Cushion Mini 5g",queries=["Founwear Mini","Founwear Cushion Mini"],pattern=r"founwear",must_mini=True),
 dict(family="pending-07",product="CLIO Mesh Blur Cushion",queries=["Mesh Blur Cushion","Mesh Blur"],pattern=r"mesh blur",must_mini=False)
]
def sha(b):return hashlib.sha256(b).hexdigest()
catalog_products={}
requests_log=[]
# Search suggestions first; do not blindly use ungrounded matched product images.
for item in CASES:
 for q in item["queries"]:
  try:
   r=requests.get(BASE+"/search/suggest.json",params={"q":q,"resources[type]":"product","resources[limit]":10},headers=UA,timeout=12)
   js=r.json() if r.status_code==200 else {}
   products=js.get("resources",{}).get("results",{}).get("products",[])
   requests_log.append({"url":r.url,"status":r.status_code,"product_titles":[x.get("title") for x in products[:10]]})
   for z in products:
    h=z.get("handle") or ""
    if h:catalog_products[h]=z.get("title","")
  except Exception as e:requests_log.append({"query":q,"exception":str(e)[:160]})
# Broader official catalogue fallback only if neither target appears in suggest.
needed=any(("founwear" in t.lower() and "mini" in t.lower()) for t in catalog_products.values())
needed=not needed or not any("mesh blur" in t.lower() for t in catalog_products.values())
if needed:
 for p in (1,2):
  try:
   r=requests.get(BASE+"/products.json",params={"limit":250,"page":p},headers=UA,timeout=16)
   if r.status_code!=200:
    requests_log.append({"url":r.url,"status":r.status_code});break
   js=r.json();data=js.get("products",[])
   requests_log.append({"url":r.url,"status":r.status_code,"returned_count":len(data)})
   for z in data:
    if z.get("handle"):catalog_products[z["handle"]]=z.get("title","")
   if len(data)<250:break
  except Exception as e:
   requests_log.append({"page":p,"exception":str(e)[:160]});break
result=[]
for c in CASES:
 folder=OUT/c["family"];folder.mkdir()
 matched=[(h,t) for h,t in catalog_products.items() if re.search(c["pattern"],t,re.I) and (not c["must_mini"] or bool(re.search("mini|미니",t,re.I)))]
 record={"family":c["family"],"name":c["product"],"matching_official_handles":[],
 "native_new_photos":[],"official_shopping_page_id_verified":False,
 "stock_unit_and_edition_verified":False,"photo_commercial_rights_verified":False,
 "retail_approved":False,"status":"HOLD_NO_EXACT_GLOBAL_PRODUCT"}
 for handle,title in matched[:4]:
  entry={"handle":handle,"search_title":title,"detail_status":"NOT_VERIFIED"}
  try:
   rr=requests.get(f"{BASE}/products/{handle}.js",headers=UA,timeout=16)
   if rr.status_code!=200:entry["detail_status"]="JSON_UNAVAILABLE";record["matching_official_handles"].append(entry);continue
   product=rr.json()
   verified=str(product.get("title",""))
   if not re.search(c["pattern"],verified,re.I) or (c["must_mini"] and not re.search("mini|미니",verified,re.I)):
    entry["detail_status"]="TITLE_NOT_EXACT";record["matching_official_handles"].append(entry);continue
   entry["detail_status"]="FIRSTPARTY_TITLE_EXACT"
   entry["title"]=verified
   entry["variants"]=[{"name":v.get("title"),"sku":v.get("sku"),"available":v.get("available")} for v in product.get("variants",[])[:20]]
   record["official_shopping_page_id_verified"]=True
   gallery=product.get("images",[])
   for candidate in gallery[:18]:
    url=(candidate if isinstance(candidate,str) else candidate.get("src") or candidate.get("url"))
    if not url:continue
    if url.startswith("//"):url="https:"+url
    if url.startswith("/"):url=BASE+url
    pu=urlparse(url)
    if pu.scheme!="https" or pu.hostname not in ("cdn.shopify.com","clubclio.shop","www.clubclio.shop"):continue
    if len(record["native_new_photos"])>=10:break
    try:
     img_response=requests.get(url,headers={"User-Agent":UA["User-Agent"],"Referer":f"{BASE}/products/{handle}"},timeout=14)
     if img_response.status_code!=200 or not(15000<len(img_response.content)<12000000):continue
     im=Image.open(BytesIO(img_response.content));im.load()
     if max(im.size)<850 or min(im.size)<500:continue
     ph=sha(img_response.content)
     if any(x["source_sha256"]==ph for x in record["native_new_photos"]):continue
     n=len(record["native_new_photos"])+1
     original=folder/f"{n:02d}-official-gallery-native-photo.jpg"
     ImageOps.exif_transpose(im).convert("RGB").save(original,"JPEG",quality=95,optimize=True)
     square=Image.new("RGB",(1080,1080),"white")
     image=ImageOps.contain(ImageOps.exif_transpose(im).convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
     square.paste(image,((1080-image.width)//2,(1080-image.height)//2))
     out=folder/f"{n:02d}-product-original-1080-QA.jpg"
     square.save(out,"JPEG",quality=90,optimize=True)
     if out.stat().st_size>=2000000:
      original.unlink();out.unlink();continue
     record["native_new_photos"].append({"official_product_handle":handle,"official_url":url,
       "native_dimensions":list(im.size),"source_sha256":ph,"stored_native_file":original.name,
       "qa_jpg":out.name,"qa_bytes":out.stat().st_size,"photo_edition_visual_QA":"PENDING",
       "commercial_reuse_permitted":False})
    except (OSError,requests.RequestException,ValueError):continue
  except (requests.RequestException,ValueError) as e:entry["detail_status"]="FETCH_ERROR";entry["error"]=str(e)[:160]
  record["matching_official_handles"].append(entry)
 record["status"]="OFFICIAL_NATIVE_PHOTOS_STAGED_VISUAL_QA" if record["native_new_photos"] else ("OFFICIAL_PRODUCT_FOUND_NO_NEW_NATIVE_PHOTO" if record["official_shopping_page_id_verified"] else "HOLD_NO_EXACT_GLOBAL_PRODUCT")
 result.append(record)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
for record in result:
 pics=record["native_new_photos"]
 rows=max(1,(len(pics)+3)//4)
 board=Image.new("RGB",(1690,70+rows*395),"#f0f0ef")
 d=ImageDraw.Draw(board)
 d.text((15,12),"v2800 "+record["family"]+" global exact-item official photo references | QA ONLY",font=font,fill="#242424")
 for i,info in enumerate(pics):
  with Image.open(OUT/record["family"]/info["qa_jpg"]) as img:
   tile=img.convert("RGB").resize((322,322),Image.Resampling.LANCZOS)
  x=20+(i%4)*415;y=52+(i//4)*395
  board.paste(tile,(x,y))
  d.text((x,y+332),f"{info['native_dimensions'][0]}x{info['native_dimensions'][1]}",font=font,fill="#292929")
 if not pics:d.text((20,105),"No exact official high-resolution item photo found; do not substitute wrong set or new design.",font=font,fill="#444444")
 proof=OUT/f"v2800-{record['family']}-contact.jpg"
 board.save(proof,"JPEG",quality=82,optimize=True)
 (OUT/f"v2800-{record['family']}-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2800","baseline":"v2799","cases":result,
 "official_search_requests":requests_log,
 "new_native_photo_assets":sum(len(x["native_new_photos"]) for x in result),
 "previous_11_approved_families_untouched":True,
 "previous_55_public_urls_unchanged":True,
 "existing_QA_photos_unchanged":True,
 "new_retail_approvals":0,"final_excel_shared":False}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2800","new_native_photos":report["new_native_photo_assets"],
"results":[{"family":x["family"],"status":x["status"],"matched":len(x["matching_official_handles"]),"photos":len(x["native_new_photos"])} for x in result],"approved":0}))
