#!/usr/bin/env python3
"""v2807 official first-party product photo discovery for two previously
failed cutout families. NEVER use previous rectangular/fake-logo archived
frames as product source. Archived sale-approved assets and URL55 stay immutable.

OBgE compact global official source & GOODAL official CLIO global eye cream.
GOODAL 25AD edition is a hard stock-generation hold; presence of same
product name or 30mL is not sufficient to claim a match.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,re,hashlib,base64
OUT=Path("qa-review/v2807-two-official-single-item-product-photo-discovery")
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 ("pending-09","OBgE Oil Control Finisher","https://obgeglobal.com/products/oil-control-finisher"),
 ("pending-21","GOODAL Green Tangerine Vitamin C Dark Circle Eye Cream","https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-dark-circle-eye-cream")
]
HEAD={"User-Agent":"Mozilla/5.0 (compatible; PhotoQA/1.0)","Accept":"application/json,text/html,image/webp,image/jpeg,image/png,*/*"}
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontfile,22)
records=[]
for fid,name,page in CASES:
 folder=OUT/fid;folder.mkdir()
 rec={"family":fid,"product":name,"official_page":page,
  "source_type":"FIRST_PARTY_OFFICIAL_PRODUCT_GALLERY",
  "source_edition_verified_for_owned_inventory":False,
  "photo_commercial_reuse_license_verified":False,
  "retail_approved":False,"photos":[],"status":"HOLD_NO_GALLERY_SOURCE"}
 try:
  sess=requests.Session()
  r=sess.get(page+".js",headers=HEAD,timeout=22)
  urls=[];title=None;variants=[]
  if r.ok:
   try:
    p=r.json();title=p.get("title") or ""
    variants=[{"title":v.get("title"),"sku":v.get("sku")} for v in p.get("variants",[])[:25]]
    for im in p.get("images",[]):
     if isinstance(im,str):urls.append(im)
     elif isinstance(im,dict) and im.get("src"):urls.append(im.get("src"))
   except Exception as e:rec["shopify_json_failure"]=type(e).__name__
  if not urls:
   r=sess.get(page,headers=HEAD,timeout=20);r.raise_for_status()
   soup=BeautifulSoup(r.text,"html.parser")
   title=(soup.find("h1").get_text(" ",strip=True) if soup.find("h1") else soup.title.get_text(" ",strip=True) if soup.title else "")
   for im in soup.select('meta[property="og:image"], img[src], img[data-src]'):
    u=im.get("content") or im.get("src") or im.get("data-src")
    if u:urls.append(u)
  titlelow=title.lower()
  if fid=="pending-09":
   if "oil" not in titlelow or "finisher" not in titlelow:raise ValueError("Wrong OBgE exact product")
  else:
   if ("green tangerine" not in titlelow or "eye cream" not in titlelow) and "dark circle eye cream" not in titlelow:
    raise ValueError("Wrong GOODAL exact product")
  rec["source_title"]=title;rec["variant_list"]=variants
  unique=[];seen=set()
  for u in urls:
   full=urljoin(page,u)
   if full in seen:continue
   seen.add(full);unique.append(full)
  rec["total_source_image_links"]=len(unique)
  rec["sample_urls"]=unique[:30]
  hashes=set()
  for u in unique[:26]:
   try:
    parsed=urlparse(u)
    # Restrict to official-hosted Shopify gallery or Shopify CDN.
    host=(parsed.hostname or "").lower()
    if not(any(host.endswith(x) for x in ("obgeglobal.com","clubclio.shop","shopify.com","shopifycdn.net"))):continue
    resp=sess.get(u,headers=HEAD,timeout=13);resp.raise_for_status()
    if len(resp.content)>8500000:continue
    original=Image.open(BytesIO(resp.content));original.load()
    if min(original.size)<450 or original.width*original.height>100000000:continue
    rgb=ImageOps.exif_transpose(original).convert("RGB")
    # Preserve authentic product pixels, format only 1080x1080 QA reference.
    square=Image.new("RGB",(1080,1080),"white")
    fitted=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
    square.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
    frame=BytesIO()
    square.save(frame,"JPEG",quality=90,optimize=True,subsampling=0)
    raw=frame.getvalue()
    if len(raw)>=2_000_000:continue
    digest=hashlib.sha256(raw).hexdigest()
    if digest in hashes:continue
    hashes.add(digest)
    file=folder/f"{len(rec['photos'])+1:02d}-firstparty-real-item-gallery-QA.jpg"
    file.write_bytes(raw)
    rec["photos"].append({"file":str(file.relative_to(OUT)),"source_url":u,
     "native_dimensions":list(original.size),"actual_encoded_1080_reference":True,
     "sha256":digest,"bytes":len(raw),"commercial_use_allowed":False,
     "exact_stock_edition_proven":False})
    if len(rec["photos"])>=10:break
   except Exception as e:
    rec["last_image_decode_failure"]=type(e).__name__
  rec["status"]="GALLERY_PHOTOS_SAVED_VISUAL_QA_REQUIRED" if rec["photos"] else "HOLD_NO_VALID_FIRST_PARTY_PRODUCT_JPGS"
 except Exception as e:
  rec["error"]=str(e)[:240];rec["status"]="HOLD_OFFICIAL_PAGE_FETCH_OR_IDENTITY"
 records.append(rec)
 for i in range(0,len(rec["photos"]),5):
  batch=rec["photos"][i:i+5]
  if not batch:continue
  canvas=Image.new("RGB",(1850,485),"#f1f0ee")
  d=ImageDraw.Draw(canvas)
  d.text((16,15),f"v2807 {fid} OFFICIAL PHOTO SOURCE PAGE {(i//5)+1} / QA REFERENCE ONLY",font=font,fill="#292929")
  for k,x in enumerate(batch):
   with Image.open(OUT/x["file"]) as im:
    thumb=im.convert("RGB").resize((335,335),Image.Resampling.LANCZOS)
   xx=15+k*369
   canvas.paste(thumb,(xx,62))
   d.text((xx,413),f"REF {i+k+1:02d} | {x['native_dimensions'][0]}px",font=font,fill="#292929")
  proof=OUT/f"v2807-{fid}-contact-{i//5+1}.jpg"
  canvas.save(proof,"JPEG",quality=85,optimize=True)
  (OUT/f"v2807-{fid}-contact-{i//5+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2807","baseline":"v2806",
 "targets":2,"saved_actual_firstparty_JPG_references":sum(len(r["photos"]) for r in records),
 "goodal_25AD_sku_edition_proven":False,
 "obge_korean_official_5g_capacity_reference":"https://www.obge.co.kr/product/detail.html?product_no=1096",
 "photo_redistribution_permission_verified":False,
 "source_gallery_product_photos_only_until_visual_QA":True,
 "original_11_approved_families_untouched":True,
 "original_55_public_urls_untouched":True,
 "previous_QA_assets_untouched":True,"new_retail_approvals":0,
 "final_spreadsheet_shared":False,"cases":records}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2807","products":2,
 "photos":[{"family":x["family"],"count":len(x["photos"]),"status":x["status"]} for x in records],
 "approved":0}))
