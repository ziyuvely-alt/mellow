#!/usr/bin/env python3
"""v2930 GOODAL 100mL mist exact manufacturer page photo source recovery.
Only take images from exact official item goodsView/0000003795, not review/customer or
other SKU thumbnails. Archive original bytes, hold images with claims and photo rights.
Do not change prior published URLs or modify preceding QA checkpoints.
"""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from urllib.parse import urlparse,urljoin
from hashlib import sha256
from collections import OrderedDict
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,re,json,time

ROOT=Path("qa-review")
BASE=ROOT/"v2929-pixelpure-three-four-photo-pack-source-integrity-QA"
PRE=ROOT/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
OUT=ROOT/"v2930-goodal-mist100-clubclio-official-gallery-native-photo-QA"
assert not OUT.exists()
m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
s=json.loads((BASE/"stock30-incremental-state-v2929.json").read_text(encoding="utf-8"))
p20=json.loads((PRE/"manifest.json").read_text(encoding="utf-8"))
assert m["version"]==s["version"]=="v2929"
assert m["remaining_five_photo_slots_across_all_6_partial_families"]==8
assert m["original_55_published_URLs_unchanged"]
FAMILY="pending-20"
PRODUCT="GOODAL Green Tangerine Vita-C Serum Mist 100mL"
URL="https://clubclio.co.kr/shop/goodsView/0000003795"
P20=next(x for x in p20["results"] if x["family"]==FAMILY)
assert P20["actual_original_source_jpgs_in_zip"]==3
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def phash(im):
 g=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def hamming(a,b):
 return sum(x!=y for x,y in zip(a,b))
def old_refs():
 hashes=set(); hashes_perceptual=[]
 zfile=Path(P20["zip_path"])
 assert sha256(zfile.read_bytes()).hexdigest()==P20["zip_sha256"]
 with ZipFile(zfile,"r") as z:
  assert len(z.namelist())==3 and z.testzip() is None
  for n in z.namelist():
   b=z.read(n);hashes.add(sha256(b).hexdigest())
   with Image.open(BytesIO(b)) as im:
    im.load()
    hashes_perceptual.append(phash(im.convert("RGB")))
 return hashes,hashes_perceptual
def is_brand_url(raw):
 try:
  u=urljoin(URL,raw.strip().replace("&amp;","&"))
  p=urlparse(u)
  if p.scheme!="https":return None
  host=(p.hostname or "").lower()
  if host!="clubclio.co.kr" and not host.endswith(".clubclio.co.kr"):return None
  if not re.search(r"\.(?:jpg|jpeg|png|webp)(?:$|[?])",p.path+"?"):return None
  bad_parts=("review","bbs","profile","goodsList","recommend","thumbnail/60","icon","logo","event/banner")
  if any(t in p.path.lower() for t in bad_parts):return None
  return u
 except:return None
def add_image_tags(node,urls,scope):
 if node is None:return
 for img in node.select("img")[:40]:
  for a in ("data-original","data-src","data-zoom-image","data-large","src","data-image"):
   value=img.get(a)
   if not isinstance(value,str) or not value:continue
   u=is_brand_url(value)
   if u:urls.setdefault(u,scope+":"+a)
def page_images(html):
 soup=BeautifulSoup(html,"html.parser")
 urls=OrderedDict()
 title=soup.title.get_text(" ",strip=True) if soup.title else ""
 main=soup.select_one('meta[property="og:title"]')
 og=(main.get("content","") if main else "")+" "+title
 title_valid=("청귤" in og and "미스트" in og and "100ml" in og.lower().replace(" ",""))
 # Title from common product detail element, never count related search snippets alone.
 for selector in (".goodsName",".goods_name",".prdName",".item_tit",".goods-title","h1"):
  el=soup.select_one(selector)
  if el:
   text=el.get_text(" ",strip=True)
   if "청귤" in text and "미스트" in text and "100" in text:title_valid=True
 product_only_selectors=(
  ".goodsImg",".goods_img",".goods-image",".item_img",".itemImg",
  ".goodsView .thumb",".goodsView .gallery",".prdImg",".goods-photo",
  "#goodsView .thumb",".goods_detail .photo",".goods_view .main_image",
  ".gallery-top",".goodsInfo .goodsImg",".goods-img-wrap",
 )
 for sel in product_only_selectors:
  for el in soup.select(sel)[:5]:
   add_image_tags(el,urls,sel)
 if title_valid:
  for el in soup.select('meta[property="og:image"]'):
   u=is_brand_url(el.get("content",""))
   if u:urls.setdefault(u,"EXACT_PRODUCT_OG_IMAGE")
  # As a strict fallback, inspect images with alt text naming the specific SKU.
  for img in soup.select("img[alt]")[:150]:
   alt=img.get("alt","")
   if "청귤" in alt and "미스트" in alt:
    for field in ("src","data-src"):
     u=is_brand_url(img.get(field,""))
     if u:urls.setdefault(u,"EXACT_PRODUCT_ALT_IMAGE")
 return title_valid,title,list(urls.items())[:24]
def visual_card(new):
 can=Image.new("RGB",(1080,1080),"#f5f6f8");d=ImageDraw.Draw(can)
 d.text((23,21),"GOODAL 100ml | OFFICIAL PRODUCT PHOTO SOURCES",font=font(25),fill="#303030")
 d.text((23,61),"INTERNAL QA ONLY • Physical stock / image license / claim proof HOLD",font=font(17),fill="#a33737")
 for i,c in enumerate(new[:4]):
  x=22+(i%2)*525;y=109+(i//2)*436
  d.rounded_rectangle((x,y,x+508,y+413),radius=12,fill="white",outline="#cccccc",width=2)
  fit=ImageOps.contain(c["rgb"],(486,338),Image.Resampling.LANCZOS)
  can.paste(fit,(x+254-fit.width//2,y+7+(338-fit.height)//2))
  d.text((x+14,y+359),f"NEW CANDIDATE {i+1} {c['size'][0]}x{c['size'][1]}",font=font(17),fill="#333333")
  d.text((x+14,y+387),"NOT A RETAIL AD PHOTO",font=font(14),fill="#a33737")
 d.text((25,1033),"No past source files rewritten; only new archive candidates and audit logs.",font=font(17),fill="#666")
 return can

session=requests.Session();session.headers.update({"User-Agent":"Mozilla/5.0 (manufacturer-image-internal-edition-QA)"})
OUT.mkdir(parents=True)
oldhash,oldphash=old_refs()
errors=[];urls=[];page_title="";exact_product_page=False
try:
 resp=session.get(URL,timeout=18);resp.raise_for_status()
 exact_product_page,page_title,urls=page_images(resp.text)
 if not exact_product_page:errors.append("Official page product title not independently verified; photo candidate adoption suppressed")
except Exception as ex:errors.append("Official product page access: "+str(ex)[:175])
new=[];near_skipped=0
if exact_product_page:
 for source,discovery in urls:
  if len(new)>=4:break
  try:
   resp=session.get(source,timeout=17);resp.raise_for_status()
   if is_brand_url(resp.url) is None:raise ValueError("image redirected away from official domain")
   b=resp.content
   if not 5000<len(b)<8_000_000:raise ValueError("bytes outside photo range")
   im=Image.open(BytesIO(b));im.load()
   if im.format not in ("JPEG","PNG","WEBP"):raise ValueError("unsupported photo format")
   rgb=ImageOps.exif_transpose(im).convert("RGB")
   px=list(rgb.size)
   if min(px)<900:raise ValueError(f"native under 900 px: {px}")
   if max(px)/min(px)>1.5:raise ValueError("long marketing infographic; NOT a product-scene photo")
   digest=sha256(b).hexdigest();h=phash(rgb)
   distance=min([hamming(h,x) for x in oldphash+[z["phash"] for z in new]],default=64)
   if digest in oldhash or any(digest==x["raw_sha256"] for x in new) or distance<6:
    near_skipped+=1;continue
   i=len(new)+1;folder=OUT/FAMILY;folder.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[im.format]
   orig=folder/f"{i:02d}-official-mist-original-unchanged{ext}";orig.write_bytes(b)
   base=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   base.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   ref=folder/f"{i:02d}-official-mist-1080-NOT-RETAIL.jpg"
   base.save(ref,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(ref) as verify:assert verify.format=="JPEG" and verify.size==(1080,1080)
   assert ref.stat().st_size<2_000_000
   new.append({"rgb":rgb,"size":px,"phash":h,"raw_sha256":digest,
     "manufacturer_photo_source":source,"discovery":discovery,
     "raw_path":str(orig),"reference_path":str(ref),
     "reference_sha256":sha256(ref.read_bytes()).hexdigest(),
     "minimum_phash_distance_to_existing":distance,
     "visual_review_of_claims":"PENDING","photo_license_verified":False,
     "owned_stock_25AD_confirmed":False,"retail_approved":False})
  except Exception as ex:errors.append("image ignored "+source.split("/")[-1][:40]+": "+str(ex)[:120])
contact=None
if new:
 contact=OUT/(FAMILY+"-manufacturer-scenes-INTERNAL-CONTACT.jpg")
 visual_card(new).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(contact) as c:assert c.format=="JPEG" and c.size==(1080,1080)
 assert contact.stat().st_size<2_000_000
# Do not count as a finished fifth photo until manually reviewing product identity and rights.
st=s["families"][FAMILY]
st.update({"last_delta_version":"v2930",
 "release_status":"CLUBCLIO_PRODUCT_ONLY_GALLERY_SCANNED_NEW_REFERENCES_STOCK_RIGHTS_HOLD" if new else "CLUBCLIO_OFFICIAL_PRODUCT_PAGE_SCANNED_NO_NEW_SOURCE_STOCK_RIGHTS_HOLD",
 "v2930_manufacturer_100ml_product_page":URL,
 "v2930_new_unapproved_source_candidate_count":len(new),
 "v2930_new_photo_QA_contact":str(contact) if contact else None,
 "v2930_photo_rights_approved":False,
 "latest_photo_QA_checkpoint":f"v2930 checked Clubclio official item goodsView/0000003795, identified {len(new)} full-size distinct original photo candidate(s), {near_skipped} near duplicates skipped, marketing claims and owned 25AD batch HOLD.",
 "sale_approved":False})
manifest={"version":"v2930","baseline":"v2929","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family":FAMILY,"product":PRODUCT,"manufacturer_url":URL,
 "manufacturer_page_product_title":page_title,
 "exact_manufacturer_product_identity_page_confirmed":exact_product_page,
 "manufacturer_page_image_links_screened":len(urls),
 "new_full_native_photo_candidates_archived":len(new),
 "near_duplicate_candidates_excluded":near_skipped,
 "previous_source_photos_unchanged":3,
 "remaining_photos_to_five_if_all_visual_candidates_validated":max(0,2-len(new)),
 "original_11_published_groups_changed":0,"old_55_verified_urls_changed":0,
 "previous_QA_paths_changed":0,"retail_approved":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,"errors":errors[:15],
 "internal_contact":str(contact) if contact else None,
 "new_references":[{k:(list(v) if k=="size" else v) for k,v in c.items() if k not in ("rgb","phash")} for c in new]}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s["version"]="v2930";s["baseline"]="v2929";s["new_sales_approvals"]=0;s["new_public_URLs"]=0;s["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2930.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2930","manufacturer_page_verified":exact_product_page,
 "new_official_mist_originals":len(new),"image_urls_screened":len(urls),
 "errors":len(errors),"new_retail_approved":0},ensure_ascii=False))
