#!/usr/bin/env python3
"""v2915: manufacturer's Hong Kong official BIOHEAL BOH products two family archival QA.
This resolves Power-vs-Boost marketing name mismatch without renaming user SKU or
mutating the prior source/stock. No images are ever retailer approved here.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from urllib.parse import urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,time

Q=Path("qa-review")
BASE=Q/"v2914-pixelpure-twelve-photo-visual-relevance-claims-and-duplicate-QA"
OLD=Q/"v2912-eight-family-preflight-visual-picks-no-fabricated-slots-QA"
OUT=Q/"v2915-biohealboh-two-firstparty-hk-source-and-cream-name-discrepancy-QA"
assert not OUT.exists()
state=json.loads((BASE/"stock30-incremental-state-v2914.json").read_text(encoding="utf-8"))
prior=json.loads((OLD/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2914" and len(state["families"])==30
prior_by={x["family"]:x for x in prior["family_results"]}
CASES=[
 {"family":"pending-24","handle":"nad-prizcell-glow-power-serum-30ml",
  "owned_stock_name":"NAD PRIZCELL Glow Power Serum 30mL","brand_expected":["nad","prizcell","serum"],
  "expected_unit":"30ml"},
 {"family":"pending-25","handle":"nad-prizcell-glow-boost-cream-50ml",
  "owned_stock_name":"NAD PRIZCELL Glow Boost Cream 50mL",
  "brand_expected":["nad","prizcell","cream"],"expected_unit":"50ml"}
]
ALLOWED={"cdn.shopify.com","biohealboh.hk","www.biohealboh.hk"}
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 (noncommercial product photo source catalog QA)"})
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def dhash(im):
 g=ImageOps.fit(ImageOps.grayscale(im),(9,8)).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def ham(a,b):return sum(x!=y for x,y in zip(a,b))
def read_existing(x):
 p=Path(x["path"]);assert p.is_file() and sha256(p.read_bytes()).hexdigest()==x["sha256"]
 with Image.open(p) as orig:
  assert orig.format=="JPEG" and orig.size==(1080,1080)
  return ImageOps.exif_transpose(orig).convert("RGB")
def contact(family,actual,items):
 a=Image.new("RGB",(1080,1080),"#f4f4f5");d=ImageDraw.Draw(a)
 d.text((26,19),family.upper()+" | OFFICIAL HK BRAND SOURCE QA",font=font(28),fill="#333333")
 d.text((26,62),actual[:66],font=font(18),fill="#5b5b5b")
 for i,z in enumerate(items[:4]):
  col=i%2;row=i//2;x=23+col*523;y=108+row*444
  d.rounded_rectangle((x,y,x+506,y+419),radius=9,fill="white",outline="#cccccc",width=2)
  p=ImageOps.contain(z["img"],(490,340),Image.Resampling.LANCZOS)
  a.paste(p,(x+253-p.width//2,y+10+(340-p.height)//2))
  d.text((x+12,y+362),f"PHOTO {i+1} {z['size'][0]}x{z['size'][1]}",font=font(19),fill="#333333")
  d.text((x+12,y+392),"RIGHTS, KR EDITION & LABEL: HOLD",font=font(15),fill="#9c3333")
 d.text((24,1025),"NO ADVERTISING CLAIMS OR STOCK EDITION AUTOMATICALLY APPROVED",font=font(17),fill="#9c3333")
 return a

OUT.mkdir(parents=True)
cases=[]
for cfg in CASES:
 family=cfg["family"];page=f"https://www.biohealboh.hk/products/{cfg['handle']}"
 endpoint=page+".js"
 errors=[];actual_title=None;urls=[];raw_source_title_match=False;title_mismatch=False
 try:
  res=S.get(endpoint,timeout=16);res.raise_for_status()
  info=res.json()
  actual_title=str(info.get("title","")).strip()
  norm="".join(actual_title.lower().replace("-"," ").replace("_"," ").split())
  raw_source_title_match=all(part in norm for part in cfg["brand_expected"])
  unit_norm=cfg["expected_unit"].replace("ml","")
  if unit_norm not in norm:raise ValueError("brand product volume differs from stock: "+actual_title)
  if not raw_source_title_match:raise ValueError("brand official product type unexpected: "+actual_title)
  title_mismatch=("powercream" in norm and "boostcream" in "".join(cfg["owned_stock_name"].lower().split()))
  for u in info.get("images",[])[:8]:
   url=u.get("src") if isinstance(u,dict) else u
   if isinstance(url,str):urls.append(url if url.startswith("https:") else "https:"+url if url.startswith("//") else url)
 except Exception as e: errors.append("official Shopify product JSON check: "+str(e)[:190])
 already=prior_by[family]["source_photos"]
 former=[dhash(read_existing(z)) for z in already]
 saved=[];hashes=set()
 for url in urls:
  if len(saved)>=4:break
  try:
   parsed=urlparse(url)
   if parsed.scheme!="https" or parsed.hostname not in ALLOWED:continue
   r=S.get(url,timeout=17);r.raise_for_status()
   if urlparse(r.url).hostname not in ALLOWED:raise ValueError("off whitelist redirect")
   data=r.content
   if not 4000<len(data)<12_000_000:raise ValueError("not full product photo size")
   raw=Image.open(BytesIO(data));raw.load()
   if raw.format not in ("JPEG","PNG","WEBP"):raise ValueError("not photo")
   rgb=ImageOps.exif_transpose(raw).convert("RGB")
   size=rgb.size
   if min(size)<900:raise ValueError("native below 900")
   digest=sha256(data).hexdigest()
   if digest in hashes:continue
   hashes.add(digest)
   d=dhash(rgb)
   prior_min=min([ham(d,x) for x in former],default=64)
   new_min=min([ham(d,z["dhash"]) for z in saved],default=64)
   # Archive source even when it is near-duplicate; do NOT inflate slot counts
   idx=len(saved)+1;folder=OUT/family;folder.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[raw.format]
   original=folder/f"{idx:02d}-official-HK-native-original{ext}"
   original.write_bytes(data)
   view=Image.new("RGB",(1080,1080),"white")
   shr=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   view.paste(shr,((1080-shr.width)//2,(1080-shr.height)//2))
   viewpath=folder/f"{idx:02d}-brand-1080-reference-JPG-INTERNAL.jpg"
   view.save(viewpath,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(viewpath) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
   assert viewpath.stat().st_size<2_000_000
   saved.append({"img":rgb,"size":size,"dhash":d,"source_url":url,"raw_original_path":str(original),
    "raw_SHA256":digest,"reference_path":str(viewpath),"reference_SHA256":sha256(viewpath.read_bytes()).hexdigest(),
    "minimum_dhash_distance_to_prior":prior_min,"minimum_dhash_distance_to_other_new":new_min,
    "could_be_prior_duplicate":prior_min<6,"actual_brand_official_title":actual_title,
    "name_mismatch_stock_vs_HK":title_mismatch,"commercial_usage_rights_verified":False,
    "physical_KR_stock_edition_verified":False,"model_claims_reviewed":False,"retail_approved":False})
  except Exception as e:errors.append("photo source: "+str(e)[:150])
 contactpath=None
 if saved:
  contactpath=OUT/(family+"-official-HK-catalog-review-INTERNAL.jpg")
  contact(family,actual_title or cfg["owned_stock_name"],saved).save(contactpath,"JPEG",quality=89,optimize=True,subsampling=0)
  with Image.open(contactpath) as ch:assert ch.size==(1080,1080)
 st=state["families"][family]
 st.update({"last_delta_version":"v2915",
  "release_status":"HK_FIRSTPARTY_REFERENCE_PHOTOS_ARCHIVED_RENAME_AND_RETAIL_RIGHTS_HOLD" if saved else "HK_FIRSTPARTY_NO_VALID_NEW_REFERENCES_NAME_RIGHTS_HOLD",
  "v2915_firstparty_native_photo_count":len(saved),
  "v2915_official_HK_title":actual_title,
  "v2915_name_mismatch_KR_vs_HK":title_mismatch,
  "v2915_brand_photo_contact":str(contactpath) if contactpath else None,
  "latest_photo_QA_checkpoint":f"v2915 HK official product page Shopify product title {actual_title!r}; {len(saved)} native >=900 official source references archived; old product photos and stock title unchanged. Name/stock/rights still HOLD.",
  "sale_approved":False})
 cases.append({"family":family,"product_record_name":cfg["owned_stock_name"],
   "brand_official_page":page,"official_shopify_title":actual_title,"title_matches_product_identity":raw_source_title_match,
   "market_name_conflict_power_vs_boost":title_mismatch,"source_URL_count":len(urls),
   "new_original_images":len(saved),"image_records":[{k:v for k,v in z.items() if k not in ("img","dhash")} for z in saved],
   "contact_image":str(contactpath) if contactpath else None,"errors":errors[:9],
   "next":"Confirm KR inventory physical exact labeling, rights, and possible Power/Boost regional name equivalence; do not rename user SKU automatically"})
report={"version":"v2915","baseline":"v2914","date_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family_count":2,"firstparty_full_resolution_sources":sum(x["new_original_images"] for x in cases),
 "internal_brand_photo_contacts":sum(bool(x["contact_image"]) for x in cases),
 "new_sales_approvals":0,"new_public_image_urls":0,"existing_11_published_families_unchanged":True,
 "existing_55_public_urls_unchanged":True,"prior_QA_paths_modified":0,"final_spreadsheet_shared":False,
 "results":cases}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2915";state["baseline"]="v2914";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2915.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2915","new_manufacturer_original_photos":report["firstparty_full_resolution_sources"],
 "by_family":{x["family"]:x["new_original_images"] for x in cases},
 "brand_KR_name_conflict":{x["family"]:x["market_name_conflict_power_vs_boost"] for x in cases},
 "sale_approvals":0},ensure_ascii=False))
