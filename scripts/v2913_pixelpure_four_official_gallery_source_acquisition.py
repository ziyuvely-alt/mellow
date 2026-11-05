#!/usr/bin/env python3
"""v2913: 4 PixelPure manufacturer-only official gallery native-image recovery.
One-pass batch with fallback for verified cream gallery; INTERNAL QA, no release.
Only write new v2913 dir. Does not touch pre-existing assets or URLs.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse,urljoin
from hashlib import sha256
from collections import OrderedDict
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,re,time

ROOT=Path("qa-review")
PRE=ROOT/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
OUT=ROOT/"v2913-pixelpure-four-exact-product-official-gallery-native-source-QA"
assert not OUT.exists()
prior=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
state=json.loads((PRE/"stock30-incremental-state-v2912.json").read_text(encoding="utf-8"))
assert prior["version"]==state["version"]=="v2912" and len(state["families"])==30
FAM={
 "pending-27":{"id":24,"title":"PIXEL PURE Soothing Ampoule Toner 200mL","need":["soothing","ampoule","toner"],"max_images":4},
 "pending-28":{"id":23,"title":"PIXEL PURE Glow Cleansing Serum Pads 70ct / 210mL","need":["glow","cleansing","serum","pad"],"max_images":4},
 "pending-29":{"id":26,"title":"PIXEL PURE Radiance Aqua Soothing Cream 50mL","need":["aqua","soothing","cream"],"max_images":4,
    "verified_direct_sources":[
      "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/small/20260907/791392bae7f687b80fac564a1ac3267f.jpg",
      "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/small/20261021/1b91715d685d4b6378b229a4ab40c9e9.jpg"
    ]},
 "pending-30":{"id":25,"title":"PIXEL PURE Aura Radiance Serum 50mL","need":["aura","radiance","serum"],"max_images":4}
}
ALLOWED_HOST={"pixelpure.com","www.pixelpure.com","ecimg.cafe24img.com"}
S=requests.Session();S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; Shopee private visual QA photo archive)"})
prior_groups={x["family"]:x for x in prior["family_results"]}
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def dhash(rgb):
 g=ImageOps.fit(ImageOps.grayscale(rgb),(9,8)).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def distance(a,b):return sum(x!=y for x,y in zip(a,b))
def gallery_urls(html,pageurl):
 soup=BeautifulSoup(html,"html.parser")
 # Product image gallery first; avoid user reviews, recommendations and thumbnails.
 candidates=OrderedDict()
 gallery_nodes=soup.select(".prdImg img, .listImg img, .keyImg img, .imgArea img, img.BigImage, img.ThumbImage")
 # Bound discovery to early main page prior to review and unrelated recommended product cards.
 if not gallery_nodes:
  h=soup.find(["h1","h2"],string=re.compile("픽셀퓨어"))
  gallery_nodes=soup.find_all("img")[:20]
 for im in gallery_nodes[:12]:
  raw=im.get("data-src") or im.get("src") or im.get("data-original")
  if not raw:continue
  url=urljoin(pageurl,raw)
  u=urlparse(url)
  if u.hostname!="ecimg.cafe24img.com" or "/pixelpure/web/product/" not in u.path:continue
  if not any(z in u.path for z in ("/big/","/small/","/extra/")):continue
  if "/tiny/" in u.path or "/thumb/" in u.path:continue
  candidates[url]=1
 # Include first-party page og:image as secondary only.
 for meta in soup.select('meta[property="og:image"]'):
  url=urljoin(pageurl,meta.get("content",""))
  if urlparse(url).hostname=="ecimg.cafe24img.com" and "/pixelpure/web/product/" in url:candidates[url]=1
 return list(candidates.keys())[:9]
def contact(family,photos):
 width=1080;im=Image.new("RGB",(width,width),"#f8f8f9");d=ImageDraw.Draw(im)
 d.text((22,18),family.upper()+" | v2913 OFFICIAL SOURCE CANDIDATES",font=font(27),fill="#333333")
 d.text((22,55),"PRODUCT GALLERY DOWNLOAD / ORIGINAL FILES ARCHIVED / NO SALES RIGHTS",font=font(16),fill="#aa3333")
 for i,record in enumerate(photos[:4]):
  col=i%2;row=i//2;x=22+col*526;y=102+row*442
  d.rounded_rectangle((x,y,x+512,y+421),radius=12,fill="white",outline="#cccccc",width=2)
  fit=ImageOps.contain(record["image"],(500,344),Image.Resampling.LANCZOS)
  im.paste(fit,(x+256-fit.width//2,y+9+(344-fit.height)//2))
  d.text((x+10,y+366),f"ORIGINAL {i+1}  {record['native'][0]}x{record['native'][1]}",font=font(18),fill="#333333")
  d.text((x+10,y+396),"REFERENCE ONLY • EDITION/CLAIMS/RIGHTS PENDING",font=font(13),fill="#a23636")
 d.text((22,1016),"Brand-owned online imagery; physical KR stock & commercial permission not verified.",font=font(17),fill="#5c5c5c")
 return im

OUT.mkdir(parents=True)
reports=[]
old_refs=set()
# Baseline v2912 photo hashes, to avoid byte duplicate re-archiving for same family.
for r in prior["family_results"]:
 for x in r["source_photos"]:old_refs.add(x["sha256"])
for family,config in FAM.items():
 page=f"https://pixelpure.com/product/detail.html?product_no={config['id']}"
 urls=OrderedDict((x,"VERIFIED_MANUFACTURER_GALLERY") for x in config.get("verified_direct_sources",[]))
 errs=[];page_ok=False;page_title_found=False
 try:
  response=S.get(page,timeout=15);response.raise_for_status()
  page_ok=True
  html=response.text
  normalized="".join(html.lower().split())
  page_title_found=all(s in normalized for s in ["픽셀퓨어","ml"])
  if not page_title_found:raise ValueError("manufacturer page product title unavailable, no automatic gallery adoption")
  for u in gallery_urls(html,page):urls.setdefault(u,"MANUFACTURER_PAGE_GALLERY")
 except Exception as e:
  errs.append("manufacturer page discovery: "+str(e)[:150])
 family_dir=OUT/family
 collected=[];hashes=set()
 for u,source_class in list(urls.items())[:11]:
  if len(collected)>=config["max_images"]:break
  try:
   parsed=urlparse(u)
   if parsed.scheme!="https" or parsed.hostname!="ecimg.cafe24img.com" or "/pixelpure/web/product/" not in parsed.path:continue
   r=S.get(u,timeout=15);r.raise_for_status()
   if urlparse(r.url).hostname!="ecimg.cafe24img.com":raise ValueError("unexpected image redirect")
   b=r.content
   if not 4000<len(b)<9_000_000:raise ValueError("bad image size")
   original=Image.open(BytesIO(b));original.load()
   if original.format not in ("JPEG","PNG","WEBP"):raise ValueError("not a standard photo image")
   image=ImageOps.exif_transpose(original).convert("RGB")
   native=image.size
   if min(native)<900:raise ValueError(f"native below 900: {native}")
   sha=sha256(b).hexdigest()
   if sha in hashes or sha in old_refs:continue
   hashes.add(sha)
   h=dhash(image)
   # Exclude only very close intra-batch scene repeats, not falsely claim other sources are independent.
   if any(distance(h,old)<4 for old in [a["dhash"] for a in collected]):continue
   idx=len(collected)+1
   family_dir.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[original.format]
   raw=family_dir/f"{idx:02d}-firstparty-native-original{ext}"
   raw.write_bytes(b)
   mini=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(image,(1080,1080),Image.Resampling.LANCZOS)
   mini.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   ref=family_dir/f"{idx:02d}-firstparty-1080-REFERENCE-ONLY.jpg"
   mini.save(ref,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(ref) as test:assert test.format=="JPEG" and test.size==(1080,1080)
   assert ref.stat().st_size<2_000_000
   collected.append({"image":image,"native":native,"dhash":h,
    "source":u,"source_class":source_class,"raw":str(raw),"raw_SHA256":sha,"ref":str(ref),
    "ref_SHA256":sha256(ref.read_bytes()).hexdigest(),
    "manufacturer_page":page,"file_format":original.format,
    "exact_stock_edition_verified":False,"distinct_original_scene_approved":False,
    "promo_badges_and_claims_visually_checked":False,"legal_photo_rights_verified":False,
    "sale_approved":False})
  except Exception as e:errs.append("skipped "+u.split("/")[-1][:35]+": "+str(e)[:130])
 contact_path=None
 if collected:
  contact_path=OUT/(family+"-official-gallery-photo-review-CONTACT-INTERNAL.jpg")
  contact(family,collected).save(contact_path,"JPEG",quality=88,optimize=True,subsampling=0)
  with Image.open(contact_path) as ch:assert ch.size==(1080,1080) and ch.format=="JPEG"
  assert contact_path.stat().st_size<2_000_000
 st=state["families"][family]
 st.update({"last_delta_version":"v2913",
  "release_status":"PIXELPURE_MANUFACTURER_SOURCE_REFERENCE_ARCHIVED_STOCK_AND_RIGHTS_HOLD" if collected else "PIXELPURE_MANUFACTURER_SOURCE_SEARCH_NO_NATIVE_MATCH_HOLD",
  "v2913_new_firstparty_native_source_candidates":len(collected),
  "v2913_reference_photo_contact":str(contact_path) if contact_path else None,
  "latest_photo_QA_checkpoint":f"v2913 manufacturer PixelPure product page #{config['id']} gallery image acquisition: {len(collected)} native sources >=900 archived; explicit claims/pack edition and rights check HOLD.",
  "sale_approved":False})
 reports.append({"family":family,"product":config["title"],"manufacturer_page":page,
  "manufacturer_page_loaded":page_ok,"manufacturer_name_in_page":page_title_found,
  "image_candidate_urls_tried":len(urls),"new_source_originals_count":len(collected),
  "new_originals":[{k:(list(v) if k=="native" else v) for k,v in c.items() if k not in ("image","dhash")} for c in collected],
  "contact_sheet":str(contact_path) if contact_path else None,
  "errors":errs[:12],"retail_release":"NOT_APPROVED"})
manifest={"version":"v2913","baseline":"v2912","generated_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "manufacturer_site":"https://pixelpure.com","families_examined":4,
 "new_manufacturer_originals_archived":sum(r["new_source_originals_count"] for r in reports),
 "new_1080_reference_JPGs":sum(r["new_source_originals_count"] for r in reports),
 "new_contact_sheets":sum(bool(r["contact_sheet"]) for r in reports),
 "retail_approved":0,"new_published_URLs":0,
 "old_11_families_untouched":True,"old_55_verified_URLs_unchanged":True,
 "old_QA_assets_untouched":True,"final_excel_shared":False,"results":reports}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2913";state["baseline"]="v2912";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2913.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2913","new_official_originals":manifest["new_manufacturer_originals_archived"],
 "by_family":{r["family"]:r["new_source_originals_count"] for r in reports},"retail_approvals":0},ensure_ascii=False))
