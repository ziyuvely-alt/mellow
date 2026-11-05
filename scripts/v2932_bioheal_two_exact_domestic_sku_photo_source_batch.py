#!/usr/bin/env python3
"""v2932: one-pass source-accurate 12 domestic product gallery image checks for two BIOHEAL BOH SKUs.
A retail product listing provides identity evidence, NOT photo reuse/redistribution permission.
This step archives original references for INTERNAL QA only. No new sales photo approval.
Preserve completed 11 groups, verified 55 URLs, all v2931 prior assets.
"""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests,json,time

Q=Path("qa-review")
V20=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
V15=Q/"v2915-biohealboh-two-firstparty-hk-source-and-cream-name-discrepancy-QA"
V31=Q/"v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA"
OUT=Q/"v2932-bioheal-two-domestic-exact-sku-gallery-12source-QA"
assert not OUT.exists()
state=json.loads((V31/"stock30-incremental-state-v2931.json").read_text(encoding="utf-8"))
m20=json.loads((V20/"manifest.json").read_text(encoding="utf-8"))
m15=json.loads((V15/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2931" and len(state["families"])==30
by20={x["family"]:x for x in m20["results"]}
by15={x["family"]:x for x in m15["results"]}
assert {x["family"] for x in m15["results"]}=={"pending-24","pending-25"}
T=[
 {"family":"pending-24","product":"NAD PRIZCELL Glow Power Serum 30 mL","sku":"A000000233882",
  "retailer_product_page":"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000233882",
  "urls":[
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388235ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388202ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388225ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388224ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388216ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388234ko.jpeg"
  ]},
 {"family":"pending-25","product":"NAD PRIZCELL Glow Boost Cream 50 mL","sku":"A000000246299",
  "retailer_product_page":"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246299",
  "urls":[
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629910ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629911ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629905ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629904ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629906ko.jpg",
   "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629909ko.jpeg"
  ]}
]
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def dhash(rgb):
 g=ImageOps.grayscale(ImageOps.fit(rgb,(9,8))).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def prior_images(family):
 zmeta=by20[family]
 assert zmeta["actual_original_source_jpgs_in_zip"] in (2,3)
 old_hash=set();old_ph=[]
 zpath=Path(zmeta["zip_path"])
 assert sha256(zpath.read_bytes()).hexdigest()==zmeta["zip_sha256"]
 with ZipFile(zpath,"r") as z:
  assert z.testzip() is None
  for name in z.namelist():
   data=z.read(name);old_hash.add(sha256(data).hexdigest())
   with Image.open(BytesIO(data)) as im:old_ph.append(dhash(im.convert("RGB")))
 for x in by15[family]["image_records"]:
  p=Path(x["reference_path"])
  assert sha256(p.read_bytes()).hexdigest()==x["reference_SHA256"]
  old_hash.add(x["reference_SHA256"])
  with Image.open(p) as im:old_ph.append(dhash(im.convert("RGB")))
 return old_hash,old_ph
def contact(family,images):
 can=Image.new("RGB",(1080,1080),"#f6f6f7"); d=ImageDraw.Draw(can)
 d.text((23,17),family.upper()+" | RETAIL GALLERY SOURCE-IDENTITY QA",font=font(25),fill="#262626")
 d.text((23,57),"NOT MANUFACTURER-LICENSED / NOT APPROVED FOR SHOP SALE",font=font(16),fill="#9f3737")
 for i,v in enumerate(images[:6]):
  row,col=divmod(i,3);x=18+col*353;y=101+row*441
  d.rounded_rectangle((x,y,x+339,y+417),radius=9,fill="white",outline="#ddd",width=2)
  img=ImageOps.contain(v["img"],(326,337),Image.Resampling.LANCZOS)
  can.paste(img,(x+169-img.width//2,y+5+(337-img.height)//2))
  d.text((x+10,y+351),"PHOTO "+str(i+1)+" | "+str(v["native"][0])+"x"+str(v["native"][1]),font=font(15),fill="#333")
  text="LOW-NATIVE HOLD" if not v["native_900_plus"] else "VISUAL CLAIMS REVIEW"
  d.text((x+10,y+386),text,font=font(13),fill="#a33c3c")
 d.text((22,1032),"Product / bundle / claim / edition / usage permissions remain unverified.",font=font(17),fill="#9f3737")
 return can

OUT.mkdir(parents=True)
sess=requests.Session()
sess.headers.update({"User-Agent":"Mozilla/5.0 (internal-source-photo-integrity-QA)"})
results=[]
for t in T:
 fam=t["family"]
 prior_sha,prior_hashes=prior_images(fam)
 new=[];skipped=[];errors=[];observed={}
 for idx,url in enumerate(t["urls"],1):
  try:
   u=urlparse(url)
   if u.scheme!="https" or u.hostname!="image.oliveyoung.co.kr" or t["sku"] not in u.path:
    raise ValueError("source host/SKU whitelist failed")
   r=sess.get(url,timeout=16);r.raise_for_status()
   if urlparse(r.url).hostname!="image.oliveyoung.co.kr":raise ValueError("unexpected image redirect")
   b=r.content
   if not 4000<len(b)<9_000_000:raise ValueError("unusable image response bytes")
   source=Image.open(BytesIO(b));source.load()
   if source.format not in ("JPEG","PNG","WEBP"):raise ValueError("not a product photo file")
   rgb=ImageOps.exif_transpose(source).convert("RGB")
   native=list(rgb.size)
   if min(native)<400 or max(native)>10000:raise ValueError("invalid size for product image")
   digest=sha256(b).hexdigest();h=dhash(rgb)
   min_dist=min([dist(h,x) for x in prior_hashes+[z["dhash"] for z in new]],default=64)
   if digest in prior_sha or any(z["native_sha256"]==digest for z in new):
    skipped.append({"url":url,"reason":"EXACT_SOURCE_ALREADY_EXISTS"});continue
   if min_dist<5:
    skipped.append({"url":url,"reason":"NEAR_DUPLICATE_SOURCE","hamming":min_dist});continue
   pos=len(new)+1; folder=OUT/fam;folder.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[source.format]
   raw=folder/f"{pos:02d}-domestic-retail-sku-source-NOT-RETAIL{ext}"
   raw.write_bytes(b)
   # 1080 white-framed reference is for visual comparison only; never claim native 1080 if smaller.
   ref=folder/f"{pos:02d}-1080-photo-REFERENCE-NOT-RETAIL.jpg"
   frame=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   frame.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   frame.save(ref,"JPEG",quality=89,optimize=True,subsampling=0)
   with Image.open(ref) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   assert ref.stat().st_size<2_000_000
   new.append({"img":rgb,"dhash":h,"source_url":url,
    "native":native,"native_900_plus":min(native)>=900,"native_sha256":digest,
    "raw_original":str(raw),"reference_1080":str(ref),
    "reference_sha256":sha256(ref.read_bytes()).hexdigest(),
    "min_dhash_from_existing":min_dist,
    "source_listing_sku":t["sku"],"brand_identity_photo_reviewed":False,
    "single_not_bundle_verified":False,"claims_cleared":False,
    "commercial_reuse_rights_granted":False,"retail_approved":False})
  except Exception as e:errors.append({"url":url,"error":str(e)[:150]})
 contactpath=None
 if new:
  contactpath=OUT/(fam+"-six-candidate-source-comparison-INTERNAL.jpg")
  contact(fam,new).save(contactpath,"JPEG",quality=89,optimize=True,subsampling=0)
  with Image.open(contactpath) as c:assert c.size==(1080,1080)
 st=state["families"][fam]
 st.update({"last_delta_version":"v2932",
  "release_status":"DOMESTIC_EXACT_SKU_SOURCE_REFERENCE_PHOTO_ARCHIVED_CLAIMS_AND_RIGHTS_HOLD" if new else "DOMESTIC_SKU_PHOTO_SOURCE_SCAN_NO_NEW_CANDIDATES",
  "v2932_domestic_photo_candidates":len(new),
  "v2932_native_900_photo_candidates":sum(x["native_900_plus"] for x in new),
  "v2932_visual_contact":str(contactpath) if contactpath else None,
  "latest_photo_QA_checkpoint":f"v2932 exact domestic retail SKU {t['sku']} gallery photo scan: {len(new)} unseen references, {sum(x['native_900_plus'] for x in new)} native >=900. All require visual brand/product/edition and legal image license check. No sale release.",
  "sale_approved":False})
 results.append({"family":fam,"product":t["product"],"retailer_sku":t["sku"],
  "source_list_page":t["retailer_product_page"],"discovered_urls_checked":len(t["urls"]),
  "new_distinct_archived_references":len(new),"highnative_candidate_count":sum(x["native_900_plus"] for x in new),
  "potential_product_scene_sufficiency_not_confirmed":True,
  "new_gallery_photos":[{k:v for k,v in z.items() if k not in ("img","dhash")} for z in new],
  "duplicate_sources_skipped":skipped,"errors":errors,
  "internal_contact":str(contactpath) if contactpath else None,"retail_sale_ready":False})
manifest={"version":"v2932","baseline":"v2931",
 "generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family_count":2,"source_links_scanned":12,
 "new_nonduplicate_source_references":sum(z["new_distinct_archived_references"] for z in results),
 "native_at_least_900_source_refs":sum(z["highnative_candidate_count"] for z in results),
 "source_licensing_and_stock_verified":False,
 "new_sales_approved_images":0,"new_public_URLs":0,
 "original_11_published_families_unchanged":True,"original_55_verified_public_URLs_unchanged":True,
 "no_prior_asset_overwrites":True,"final_spreadsheet_shared":False,
 "results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2932";state["baseline"]="v2931";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2932.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2932","scanned":12,
 "new_references":manifest["new_nonduplicate_source_references"],
 "highnative":manifest["native_at_least_900_source_refs"],
 "by_family":{z["family"]:z["new_distinct_archived_references"] for z in results},
 "retail_approvals":0},ensure_ascii=False))
