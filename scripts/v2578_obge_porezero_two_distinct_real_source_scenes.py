#!/usr/bin/env python3
"""v2578: acquire two genuinely different photographs of exact OBgE Pore-Zero
Oil Control Sun Cream 50mL. Product photos are REVIEW ONLY and not commercially
licensed by the original owners. All 156 previous customer QA JPG untouched.
Source quality validation, image details, and same-family duplicate checks.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageStat,ImageChops
from itertools import combinations
import hashlib,json
OUT=Path("v2578-two-real-obge-porezero-source-scenes");OUT.mkdir(exist_ok=True)
B=Path("v2578-previous/review-JPG-by-family/pending-23")
assert B.is_dir() and len(list(B.glob("*.jpg")))==5
sources=[
  {"tag":"real-tube-cream-texture","url":"https://www.daeskin.com.au/cdn/shop/files/product_images_1762936952.10262771840178682_19674406691769131379.jpg?v=1769136067",
   "page":"https://www.daeskin.com.au/products/obge-pore-zero-oil-control-sun-cream-spf50-50ml",
   "identity":"OBgE PORE-ZERO OIL CONTROL SUN CREAM, white-turquoise 50mL tube with white cream smear"},
  {"tag":"real-dual-tube-distinct-angle","url":"https://www.dodoskin.com/cdn/shop/files/OBgEPoreZeroOilControlSunCream50ml-2.jpg?v=1761115221&width=3000",
   "page":"https://www.dodoskin.com/products/obge-pore-zero-oil-control-sun-cream-50ml",
   "identity":"OBgE PORE-ZERO OIL CONTROL SUN CREAM, two actual white-turquoise tubes, cream texture"}
]
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 result=0
 for row in range(8):
  for col in range(8):result=(result<<1)|(p[row*9+col]>p[row*9+col+1])
 return result
def mae(a,b):
 aa=a.convert("RGB").resize((128,128));bb=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(aa,bb)).mean)/3,2)
old=[]
for f in B.glob("*.jpg"):
 im=Image.open(f);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080)
 old.append((f,im.copy()))
rows=[];new=[]
for s in sources:
 try:
  req=Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/jpeg,image/*"})
  with urlopen(req,timeout=20) as res:raw=res.read(8_000_001)
  assert len(raw)<8_000_000 and len(raw)>10_000
  original=Image.open(BytesIO(raw));original.load()
  assert original.format in ("JPEG","PNG","WEBP") and min(original.size)>=400
  # Avoid cutout or AI alteration: preserve every photograph pixel within its full
  # rectangular frame; a neutral background appears only when aspect ratios differ.
  resized=ImageOps.contain(original.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  image=Image.new("RGB",(1080,1080),"#f7f9f8")
  image.paste(resized,((1080-resized.width)//2,(1080-resized.height)//2))
  path=OUT/(s["tag"]+"-CANDIDATE.jpg")
  image.save(path,"JPEG",quality=90,optimize=True,subsampling=0)
  assert Image.open(path).size==(1080,1080) and path.stat().st_size<2_000_000
  comparisons=[{"existing_slot":int(f.name[:2]),"mae":mae(image,im),
     "dhash_distance":(dhash(image)^dhash(im)).bit_count()} for f,im in old]
  near=[x for x in comparisons if x["dhash_distance"]<=6 or x["mae"]<8]
  rows.append({"tag":s["tag"],"candidate_jpg":path.name,"source_page":s["page"],
    "raw_download_url":s["url"],"source_image_sha256":hashlib.sha256(raw).hexdigest(),
    "source_pixels":list(original.size),"QA_jpg_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "candidate_size_bytes":path.stat().st_size,
    "visual_product_description_in_source":s["identity"],
    "candidate_distinctness_checks":comparisons,
    "potential_same_family_near_repeats":near,
    "photo_source_rights_verified":False,
    "exact_stock_package_verified":False,"sales_approved":False,
    "status":"PHOTO_QA_CANDIDATE_ONLY" if not near else "HOLD_POSSIBLE_SIMILARITY"})
  new.append((path,image))
 except Exception as e:
  rows.append({"tag":s["tag"],"source_page":s["page"],"status":"SOURCE_FETCH_HOLD",
   "error_class":type(e).__name__,"sales_approved":False})
assert len(rows)==2
if len(new)==2:
 mutual={"mae":mae(new[0][1],new[1][1]),"dhash_distance":(dhash(new[0][1])^dhash(new[1][1])).bit_count()}
else:mutual=None
report={"version":"v2578","family":"pending-23",
"product":"OBgE Pore-Zero Oil Control Sun Cream 50mL",
"independent_real_photographs_downloaded":len(new),
"product_family_existing_photo_count":len(old),
"source_items_attempted":len(sources),
"two_new_photo_mutual_comparison":mutual,
"previous_156_JPG_modified":0,"existing_55_public_URLs_modified":0,
"new_public_URLs":0,"xlsx_created_or_shared":False,
"commercial_photo_rights_verified":False,
"actual_50mL_edition_confirmed_for_stock":False,
"final_approved":False,"source_photographs":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photo_download_success":len(new),"independent_source_scenes":len(sources),
"near_dup_existing":sum(len(x.get("potential_same_family_near_repeats",[])) for x in rows),
"source_fails":len(sources)-len(new),"commercial_release":False,"xlsx_shared":False}))
