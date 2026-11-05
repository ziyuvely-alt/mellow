#!/usr/bin/env python3
"""v2916 GOODAL 2-family official CLIO media asset discovery and archive.
No existing references are overwritten, only NEW original manufacturer-owned images
from whitelisted product pages, held until visual claims, owned-stock edition and rights QA.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from urllib.parse import urlparse, urljoin
from PIL import Image, ImageOps, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests, json, re, time

QA=Path("qa-review")
PRE=QA/"v2915-biohealboh-two-firstparty-hk-source-and-cream-name-discrepancy-QA"
OLD=QA/"v2906-two-goodal-obge-official-source-photo-recovery-QA"
OUT=QA/"v2916-goodal-cream50-eyecream-official-media-gallery-only-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2915.json").read_text())
old=json.loads((OLD/"manifest.json").read_text())
assert state["version"]=="v2915" and len(state["families"])==30
old_hashes={x["raw_sha256"] for f in old["families"] for x in f.get("items",[])}
TARGETS=[
 {"family":"pending-19","name":"GOODAL Green Tangerine Vita-C Dark Spot Care Cream Alpha 50mL",
  "url":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-cream-advanced-ver",
  "must":["green tangerine","cream"],
  "seed":["https://clubclio.shop/cdn/shop/files/1_83005dbd-050d-4026-887e-95132d160429_1200x.jpg?v=1772777724",
          "https://clubclio.shop/cdn/shop/files/2_d5a44fc5-ef3a-4f38-a569-24dd62525257_1200x.jpg?v=1772777724"]},
 {"family":"pending-21","name":"GOODAL Green Tangerine Vita C Dark Circle Eye Cream, 25AD version unverified",
  "url":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-dark-circle-eye-cream",
  "must":["green tangerine","eye cream"],
  "seed":["https://clubclio.shop/cdn/shop/files/1_30e9f92e-4405-4f2f-894f-b5d078b75cc5.jpg?v=1772779151"]},
]
SESSION=requests.Session(); SESSION.headers.update({"User-Agent":"Mozilla/5.0 (noncommercial firstparty-source QA)"})
ALLOWED={"clubclio.shop","cdn.shopify.com"}
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def parse_urls(html,page,token):
 soup=BeautifulSoup(html,"html.parser")
 candidates=OrderedDict()
 # Shopify media gallery, product-specific ALT only. No review/related products.
 product_nodes=soup.select("media-gallery img, product-gallery img, .product__media-list img, .product-gallery img, .product-single__photos img, .product__thumbs img, .product__main-photos img")
 if not product_nodes:
  product_nodes=[x for x in soup.select("img") if "goodal" in (x.get("alt") or "").lower() and token in (x.get("alt") or "").lower()]
 for node in product_nodes[:32]:
  alt=(node.get("alt") or "").lower()
  if "toner pad" in alt or "serum [advanced" in alt:continue
  keys=["data-src","data-zoom-src","data-master","src"]
  for k in keys:
   raw=node.get(k)
   if not raw:continue
   url=urljoin(page,raw)
   host=urlparse(url).hostname
   if host not in ALLOWED or "/cdn/shop/files/" not in url and "s/files/" not in url:continue
   if re.search(r"_(?:85x|165x|200x|300x|400x)\.",url):continue
   candidates[url]=1
  for attr in ["srcset","data-srcset"]:
   srcset=node.get(attr) or ""
   items=[]
   for part in srcset.split(","):
    part=part.strip().split()
    if not part:continue
    url=urljoin(page,part[0])
    m=re.search(r"(\d+)w",part[1]) if len(part)>1 else None
    width=int(m.group(1)) if m else 0
    if width>=900 and urlparse(url).hostname in ALLOWED:items.append((width,url))
   if items:
    width,url=sorted(items,key=lambda z:(z[0]<=1800,z[0]),reverse=True)[0]
    candidates[url]=1
 return list(candidates.keys())[:17]
def dhash(im):
 g=ImageOps.fit(ImageOps.grayscale(im),(9,8)).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(x,y):return sum(a!=b for a,b in zip(x,y))
def review_sheet(family,frames):
 im=Image.new("RGB",(1080,1080),"#f7f7f8");d=ImageDraw.Draw(im)
 d.text((23,17),family.upper()+" | GOODAL OFFICIAL PHOTO CANDIDATES v2916",font=font(28),fill="#333333")
 d.text((23,58),"Brand product page media; no claims/rights/physical-stock approval",font=font(17),fill="#aa3333")
 for i,z in enumerate(frames[:6]):
  row,col=divmod(i,3);x=18+col*353;y=102+row*435
  d.rounded_rectangle((x,y,x+336,y+410),radius=10,fill="white",outline="#dadada",width=2)
  thumb=ImageOps.contain(z["rgb"],(325,323),Image.Resampling.LANCZOS)
  im.paste(thumb,(x+168-thumb.width//2,y+13+(323-thumb.height)//2))
  d.text((x+12,y+345),f"IMAGE {i+1} | {z['size'][0]}x{z['size'][1]}",font=font(15),fill="#555555")
  d.text((x+12,y+375),"INTERNAL ONLY",font=font(15),fill="#a33838")
 d.text((24,1035),"Do not publish manufacturer promotional copy or claimed clinical outcomes.",font=font(16),fill="#333333")
 return im

OUT.mkdir(parents=True)
reports=[]
for t in TARGETS:
 urls=OrderedDict((u,"HAND_VERIFIED_OFFICIAL_PAGE") for u in t["seed"])
 errors=[];page_ok=False
 try:
  resp=SESSION.get(t["url"],timeout=15);resp.raise_for_status()
  soup=BeautifulSoup(resp.text,"html.parser")
  title=(soup.title.get_text(" ",strip=True) if soup.title else "").lower()
  page_ok=all(z in title for z in t["must"])
  if not page_ok:errors.append("product page title did not fully match expected item, gallery discovery rejected: "+title[:100])
  else:
   for u in parse_urls(resp.text,t["url"],"cream"):urls.setdefault(u,"BRAND_PAGE_MEDIA")
 except Exception as exc:errors.append("page failed: "+str(exc)[:140])
 saved=[];seen=set();seen_phash=[]
 for url,typ in list(urls.items())[:20]:
  if len(saved)>=6:break
  try:
   h=urlparse(url).hostname
   if h not in ALLOWED or not url.startswith("https:"):continue
   rr=SESSION.get(url,timeout=15);rr.raise_for_status()
   if urlparse(rr.url).hostname not in ALLOWED:raise ValueError("redirect to unexpected host")
   data=rr.content
   if not 3000<len(data)<12_000_000:raise ValueError("unexpected image bytes")
   with Image.open(BytesIO(data)) as raw:
    raw.load()
    if raw.format not in ("JPEG","PNG","WEBP"):raise ValueError("not photo")
    fmt=raw.format
    rgb=ImageOps.exif_transpose(raw).convert("RGB")
   size=rgb.size
   if min(size)<900:raise ValueError(f"native below 900: {size}")
   hash=sha256(data).hexdigest()
   if hash in seen or hash in old_hashes:continue
   d=dhash(rgb)
   if min((dist(d,x) for x in seen_phash),default=64)<4:continue
   seen.add(hash);seen_phash.append(d)
   idx=len(saved)+1
   folder=OUT/t["family"];folder.mkdir(exist_ok=True)
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[fmt]
   rawpath=folder/f"{idx:02d}-brand-native-original.{ext}";rawpath.write_bytes(data)
   canvas=Image.new("RGB",(1080,1080),"white")
   scaled=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
   jpg=folder/f"{idx:02d}-brand-1080-INTERNAL-QA.jpg"
   canvas.save(jpg,"JPEG",quality=89,optimize=True,subsampling=0)
   assert jpg.stat().st_size<2_000_000
   saved.append({"rgb":rgb,"size":size,"source_url":url,"source_type":typ,"original_path":str(rawpath),
      "original_sha256":hash,"reference_path":str(jpg),"reference_sha256":sha256(jpg.read_bytes()).hexdigest(),
      "visual_product_edition_check":"PENDING","claims_review":"PENDING","commercial_photo_permission":False,"retail_approved":False})
  except Exception as exc:errors.append("image skipped "+url.split("/")[-1][:45]+": "+str(exc)[:100])
 cpath=None
 if saved:
  cpath=OUT/(t["family"]+"-gallery-review-INTERNAL.jpg")
  review_sheet(t["family"],saved).save(cpath,"JPEG",quality=87,optimize=True,subsampling=0)
  with Image.open(cpath) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
  assert cpath.stat().st_size<2_000_000
 s=state["families"][t["family"]]
 s.update({"last_delta_version":"v2916","release_status":"GOODAL_FIRSTPARTY_SOURCE_PHOTOS_ARCHIVED_EDITION_CLAIMS_RIGHTS_HOLD" if saved else "GOODAL_OFFICIAL_SEARCH_NO_NEW_CLEAN_SOURCE_HOLD",
  "v2916_new_official_photo_originals":len(saved),"v2916_firstparty_photo_contact":str(cpath) if cpath else None,
  "latest_photo_QA_checkpoint":f"v2916 archived {len(saved)} additional firstparty brand image references (>=900 native), not retail approved, exact stock edition and photo rights HOLD.",
  "sale_approved":False})
 reports.append({"family":t["family"],"product":t["name"],"manufacturer_page":t["url"],"product_page_title_matched":page_ok,
   "gallery_urls_evaluated":len(urls),"new_brand_original_sources":len(saved),
   "images":[{k:(list(v) if k=="size" else v) for k,v in x.items() if k!="rgb"} for x in saved],
   "contact_path":str(cpath) if cpath else None,"errors":errors[:12],
   "stock_generation_verified":False,"image_licenses_verified":False,"sale_approved":False})
report={"version":"v2916","baseline":"v2915","date_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_processed":2,"new_originals_saved":sum(x["new_brand_original_sources"] for x in reports),
 "new_QA_reference_1080":sum(x["new_brand_original_sources"] for x in reports),
 "new_internal_contacts":sum(bool(x["contact_path"]) for x in reports),
 "existing_11_approved_families_unmodified":True,"existing_55_URLs_unchanged":True,"prior_QA_files_unmodified":True,
 "commercial_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False,"results":reports}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
state["version"]="v2916";state["baseline"]="v2915";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2916.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2916","official_originals":report["new_originals_saved"],
 "families":{x["family"]:x["new_brand_original_sources"] for x in reports},
 "retail_approvals":0},ensure_ascii=False))
