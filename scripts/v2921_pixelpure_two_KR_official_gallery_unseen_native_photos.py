#!/usr/bin/env python3
"""v2921: discover NEW PixelPure brand gallery source photos for toner 200ml and Aura serum 50ml.
Use verified KR product pages, strict product-gallery scope, original SHA and perceptual dedupe.
No previously uploaded/published photo or QA asset is modified. No retail releases.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse
from hashlib import sha256
from io import BytesIO
from collections import OrderedDict
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,re,time

Q=Path("qa-review")
BASE=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
P13=Q/"v2913-pixelpure-four-exact-product-official-gallery-native-source-QA"
P19=Q/"v2919-reconcile-parallel-v2917-and-pixelpure-extra-big-firstparty-QA"
OUT=Q/"v2921-pixelpure-KR-two-family-unseen-product-gallery-source-QA"
assert not OUT.exists()
state=json.loads((BASE/"stock30-incremental-state-v2920.json").read_text(encoding="utf-8"))
old13=json.loads((P13/"manifest.json").read_text(encoding="utf-8"))
old19=json.loads((P19/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2920" and len(state["families"])==30
targets=[
 {"family":"pending-27","no":24,"title":"픽셀퓨어 수딩 앰플 토너 200ml",
  "must":["수딩","앰플","토너","200ml"]},
 {"family":"pending-30","no":25,"title":"픽셀퓨어 아우라 래디언스 세럼 50ml",
  "must":["아우라","래디언스","세럼","50ml"]}
]
session=requests.Session();session.headers.update({"User-Agent":"Mozilla/5.0 (product manufacturer original photo internal QA)"})
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def phash(img):
 gray=ImageOps.fit(ImageOps.grayscale(img),(9,8)).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def cleanurl(u,base):
 u=urljoin(base,u.strip()).replace("&amp;","&")
 u=u.split("?")[0]
 p=urlparse(u)
 if p.scheme!="https" or p.hostname!="ecimg.cafe24img.com" or "/pixelpure/web/product/" not in p.path:return None
 if not re.search(r"/(big|small|extra/(?:big|small))/",p.path):return None
 return u
def collect_page_urls(soup,page):
 urls=OrderedDict()
 selectors=[".imgArea",".prdImg",".listImg",".keyImg",".product_detail_image",".product-thumb",".thumbnail"]
 nodes=[]
 for selector in selectors:
  nodes.extend(soup.select(selector))
 if not nodes: nodes=soup.select("img")[:20]
 for root in nodes[:20]:
  els=[root] if root.name=="img" else root.select("img")[:20]
  for im in els:
   for field in ("src","data-src","data-original","data-zoom","data-zoom-src","data-image","data-large"):
    raw=im.get(field)
    if isinstance(raw,str):
     u=cleanurl(raw,page)
     if u:urls[u]=field
   for field in ("srcset","data-srcset"):
    raw=im.get(field)
    if not raw:continue
    for item in raw.split(","):
     p=item.strip().split(" ")[0]
     u=cleanurl(p,page)
     if u:urls[u]=field
 # Product page may have extra thumbnails as literal URLs in the product image area.
 html=str(soup.select_one(".imgArea") or soup.select_one(".prdImg") or "")
 for raw in re.findall(r'(?:(?:https?:)?//)?ecimg\.cafe24img\.com/[^"\\\s<>]+\.(?:jpg|jpeg|png|webp)',html):
  u=cleanurl(raw if raw.startswith("https:") else "https:"+raw if raw.startswith("//") else "https://"+raw,page)
  if u:urls[u]="contained_product_media_HTML"
 return urls
def make_contact(fam,imgs):
 board=Image.new("RGB",(1080,1080),"#f6f7f8");d=ImageDraw.Draw(board)
 d.text((24,20),fam.upper()+" | v2921 KR OFFICIAL GALLERY",font=font(28),fill="#242424")
 d.text((24,62),"New brand source candidates only; stock / rights / claims unapproved",font=font(18),fill="#a03535")
 for i,z in enumerate(imgs[:6]):
  row,col=divmod(i,3);x=18+col*353;y=108+row*439
  d.rounded_rectangle((x,y,x+338,y+410),radius=10,fill="white",outline="#ccc",width=2)
  view=ImageOps.contain(z["rgb"],(324,326),Image.Resampling.LANCZOS)
  board.paste(view,(x+169-view.width//2,y+9+(326-view.height)//2))
  d.text((x+12,y+349),f"{i+1:02}  {z['size'][0]}x{z['size'][1]}",font=font(17),fill="#444")
  d.text((x+12,y+379),"NOT SALES-APPROVED",font=font(16),fill="#a03535")
 d.text((24,1040),"Original photo files and previously approved URLs are not changed.",font=font(18),fill="#444")
 return board
def prior_for(fam):
 hashes=set();features=[]
 for f in old13["results"]:
  if f["family"]!=fam:continue
  for img in f["new_originals"]:
   hashes.add(img["raw_SHA256"])
   path=Path(img["ref"])
   with Image.open(path) as im:features.append(phash(im.convert("RGB")))
 for f in old19["pixelpure_results"]:
  if f["family"]!=fam:continue
  for img in f["new_images"]:
   hashes.add(img["raw_original_sha256"])
   path=Path(img["reference_jpg"])
   with Image.open(path) as im:features.append(phash(im.convert("RGB")))
 return hashes,features

OUT.mkdir(parents=True)
report=[]
for t in targets:
 fam=t["family"];page=f"https://www.pixelpure.com/product/detail.html?product_no={t['no']}"
 old_hashes,old_features=prior_for(fam)
 urls=OrderedDict();warnings=[];valid_page=False;title=""
 try:
  r=session.get(page,timeout=15);r.raise_for_status()
  soup=BeautifulSoup(r.text,"html.parser")
  title=(soup.select_one("h1") or soup.select_one("h2")).get_text(" ",strip=True)
  main=soup.select_one("meta[property='og:title']")
  heading=(main.get("content","") if main else "")+" "+title+" "+soup.title.get_text(" ",strip=True) if soup.title else title
  check="".join(heading.lower().split())
  valid_page=all(x.lower().replace(" ","") in check for x in t["must"])
  if valid_page:urls=collect_page_urls(soup,page)
  else:warnings.append("KR manufacturer product page heading not exact match; no photo adopted")
 except Exception as e:warnings.append("page error: "+str(e)[:140])
 found=[];seen=set();features=list(old_features);dupes=0
 for u,src in list(urls.items())[:24]:
  if len(found)>=6:break
  try:
   rq=session.get(u,timeout=14);rq.raise_for_status()
   if urlparse(rq.url).hostname!="ecimg.cafe24img.com":raise ValueError("redirected")
   b=rq.content
   if not 4000<len(b)<10_000_000:raise ValueError("bad source size")
   raw=Image.open(BytesIO(b));raw.load()
   if raw.format not in ("JPEG","PNG","WEBP"):raise ValueError("not a photo")
   im=ImageOps.exif_transpose(raw).convert("RGB")
   size=im.size
   if min(size)<900:raise ValueError("native under 900")
   h=sha256(b).hexdigest();p=phash(im)
   if h in old_hashes or h in seen or any(dist(p,x)<5 for x in features):
    dupes+=1;continue
   seen.add(h);features.append(p)
   i=len(found)+1;sub=OUT/fam;sub.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[raw.format]
   path=sub/f"{i:02}-unseen-brand-gallery-native{ext}"
   path.write_bytes(b)
   display=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(im,(1080,1080),Image.Resampling.LANCZOS)
   display.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   ref=sub/f"{i:02}-1080-visual-QA.jpg"
   display.save(ref,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(ref) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
   assert ref.stat().st_size<2_000_000
   found.append({"rgb":im,"size":size,"source_url":u,"source_discovery":src,
    "raw_path":str(path),"raw_sha256":h,
    "reference_path":str(ref),"reference_sha256":sha256(ref.read_bytes()).hexdigest(),
    "manufacturer_photo_rights_approved":False,"product_edition_confirmed":False,
    "manual_scene_and_badge_QA_pending":True,"retail_approved":False})
  except Exception as e:warnings.append("image skip "+u.split("/")[-1][:35]+": "+str(e)[:90])
 contact=None
 if found:
  contact=OUT/(fam+"-unseen-originals-INTERNAL-CONTACT.jpg")
  make_contact(fam,found).save(contact,"JPEG",quality=89,optimize=True,subsampling=0)
 st=state["families"][fam]
 st.update({"last_delta_version":"v2921",
  "release_status":"KR_BRAND_GALLERY_NATIVE_SOURCE_DISCOVERY_STOCK_RIGHTS_HOLD" if found else "KR_OFFICIAL_PRODUCT_GALLERY_NO_NEW_DISTINCT_NATIVE_SOURCE",
  "v2921_new_distinct_originals":len(found),
  "v2921_photo_contact":str(contact) if contact else None,
  "latest_photo_QA_checkpoint":f"v2921 verified KR official item #{t['no']}, {len(found)} additional previously unseen >=900 native first-party photos archived; {dupes} prior duplicates skipped. No sale approval, physical edition or rights verified.",
  "sale_approved":False})
 report.append({"family":fam,"page":page,"page_title":title,"exact_KR_page_verified":valid_page,
  "urls_checked":len(urls),"archive_new_native_originals":len(found),"duplicate_assets_skipped":dupes,
  "items":[{k:(list(v) if k=="size" else v) for k,v in z.items() if k!="rgb"} for z in found],
  "contact":str(contact) if contact else None,"errors":warnings[:12]})
manifest={"version":"v2921","baseline":"v2920","created_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "KR_brand_page_families_processed":2,
 "new_distinct_native_original_images":sum(r["archive_new_native_originals"] for r in report),
 "new_internal_1080_JPGs":sum(r["archive_new_native_originals"] for r in report),
 "new_contacts":sum(bool(r["contact"]) for r in report),
 "prior_duplicate_scenes_skipped":sum(r["duplicate_assets_skipped"] for r in report),
 "source_url_image_rights_verified":False,"physical_owned_stock_verified":False,
 "old_11_approved_family_images_changed":0,"old_55_public_URLs_changed":0,
 "previous_QA_sources_changed":0,"retail_approvals":0,"public_URLs_added":0,
 "final_spreadsheet_shared":False,"results":report}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2921";state["baseline"]="v2920";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2921.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2921","additional_official_photos":manifest["new_distinct_native_original_images"],
  "by_family":{r["family"]:r["archive_new_native_originals"] for r in report},
  "dupes":manifest["prior_duplicate_scenes_skipped"],"new_retail_approvals":0},ensure_ascii=False))
