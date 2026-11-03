#!/usr/bin/env python3
"""v2453: recover two previously blocked CLIO product photo details using DIFFERENT
existing photo for pending-06 and correct whole-object crop for pending-07.
No old successful JPG regenerated. Also record visually identified wrong-category
OBgE 300mL source photo as permanent reject (cushion ≠ sunscreen bottle).
"""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json,zipfile
SRC=Path("prior-v2427b")
OUT=Path("v2453-output");OUT.mkdir(exist_ok=True)
ROOT=SRC/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions"
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(sz,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
jobs=[
 {"g":"pending-06","file":"SOURCE_02_8efe54403_EN_V2421C.jpg",
 "crop":(197,78,856,829),"title":"Kill Cover Mesh Glow Essential","detail":"Cushion Compact in Original Photo","hold":"Exact special-set package and shade generation unverified"},
 {"g":"pending-07","file":"SOURCE_01_3c2612d6d_EN_V2421C.jpg",
 "crop":(170,266,641,750),"title":"Kill Cover Mesh Blur Cushion",
 "detail":"Compact & Puff from Original Photo","hold":"Special bundle contents and all shade versions unverified"}
]
items=[]
for j in jobs:
 source=ROOT/j["g"]/j["file"]
 assert source.exists(),source
 sh=h(source)
 with Image.open(source) as im:
  im.load();assert im.size==(1080,1080) and im.format=="JPEG"
  product=im.convert("RGB").crop(j["crop"])
  product=ImageOps.contain(product,(810,645),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(canvas)
  ink=(44,64,56)
  d.text((68,52),"CLIO",font=ft(38,True),fill=ink)
  n=43
  while n>=26 and d.textbbox((0,0),j["title"],font=ft(n,True))[2]>945:n-=1
  assert n>=26
  d.text((68,118),j["title"],font=ft(n,True),fill=ink)
  d.line((68,191,1012,191),fill=(178,191,182),width=2)
  canvas.paste(product,((1080-product.width)//2,224+(645-product.height)//2))
  d.line((68,910,1012,910),fill=(178,191,182),width=2)
  ds=32
  while ds>=24 and d.textbbox((0,0),j["detail"],font=ft(ds,True))[2]>945:ds-=1
  d.text((68,941),j["detail"],font=ft(ds,True),fill=ink)
  d.text((68,991),"Cushion",font=ft(29),fill=ink)
  path=OUT/"new-CLIO-real-product-photo-JPGs"/j["g"]/(j["g"]+"_genuine_photo_quality_replacement_V2453.jpg")
  path.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(path,"JPEG",quality=94,optimize=True)
  with Image.open(path) as test:
   test.load()
   assert test.format=="JPEG" and test.size==(1080,1080) and path.stat().st_size<2000000
  assert h(source)==sh
  items.append({"group_id":j["g"],"actual_JPG":str(path.relative_to(OUT)),
   "SHA256":h(path),"photo_source":str(source),"source_SHA256":sh,"source_crop_xyxy":j["crop"],
   "artificial_product_pixels":False,"source_rights_verified":False,
   "stock_shade_generation_verified":False,"visual_QA":"PENDING_DIRECT_IMAGE_INSPECTION",
   "final_sale_approved":False,"hold":j["hold"]})
assert len(items)==2
# Directly inspected in source: p22 Product Photo 02 shows a square cushion case,
# completely different from sunscreen 300mL pump packaging. Never re-use as photo.
bad=SRC/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/new-independent-photo-candidates/pending-22/PRODUCT_PHOTO_02_V2424.jpg"
assert bad.exists()
with Image.open(bad) as verify:verify.load();assert verify.size==(1080,1080)
report={"version":"2.4.53","prior_checkpoint":"production-assets-v2452-32-source-JPGs-five-groups-hold",
"replaced_only_two_previously_rejected_CLIO_detail_JPG":2,
"previous_32_reviewable_JPGs_regenerated":0,
"original_531_JPGs_modified":0,"prior_published_55_URLs_modified":0,
"new_swatch_charts_generated":0,"commercial_image_permissions_verified":0,
"FINAL_SALES_APPROVED":0,"NO_SPREADSHEETS_SHARED":True,
"new_photo_crops":items,
"wrong_product_photo_quarantine":{"group_id":"pending-22","source":str(bad),
"SHA256":h(bad),"visually_observed":"Source shows OBgE square beige cushion case, not MAX Waterful Sun Cream 300mL pump bottle",
"reason":"Wrong product category; do not label this a sunscreen photograph",
"status":"PERMANENT_REJECT_WRONG_PRODUCT"},
"other_pending22_candidate_photo_01":"HOLD_SRC_PROVENANCE_NOT_VERIFIED",
"next":"Visually inspect both new CLIO crops; use exact image bytes if acceptable; preserve source and rights holds"}
(OUT/"v2453_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2453_two_new_CLIO_photo_JPGs.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
 for item in items:z.write(OUT/item["actual_JPG"],arcname=item["actual_JPG"])
 z.write(OUT/"v2453_checkpoint.json",arcname="v2453_checkpoint.json")
with zipfile.ZipFile(OUT/"v2453_two_new_CLIO_photo_JPGs.zip") as z:
 assert z.testzip() is None and len(z.namelist())==3
print(json.dumps({"version":report["version"],"new_real_CLIO_JPGs":2,"wrong_category_OBgE_photo_permanently_rejected":1,"spreadsheets_shared":0}),flush=True)
