#!/usr/bin/env python3
"""Swap exactly TWO outdated informational cards for photographs of genuine
OBgE Oil Control Finisher 5g. Base v2539 156 QA JPEGs; 154 unchanged.
Photos: actual official opened compact+applicator and distinct suspended compact
composition from authentic Ballagrio product listing. Do not fabricate product.
Rights and actual stock edition remain hold, no public URLs or Excel.
"""
from pathlib import Path
from PIL import Image,ImageOps
from urllib.request import Request,urlopen
from io import BytesIO
import shutil,hashlib,json
BASE=Path("v2541-base-156/review-JPG-by-family")
O=Path("v2541-obge-finisher-2real-photo-QA")
D=O/"review-JPG-by-family"
assert BASE.is_dir()
shutil.copytree(BASE,D)
sources=[
 {"slot":2,"url":"https://obgeglobal.com/cdn/shop/files/83.png?v=1776049524",
  "role":"Genuine 5g open beige finisher compact with OBgE puff","label":"official-open-finisher"},
 {"slot":4,"url":"https://www.ballagrio.com/cdn/shop/files/obge-oil-control-finisher-5g-06.jpg?v=1777873278",
  "role":"Distinct photograph of original 5g separated finisher case and puff","label":"real-product-floating-case"}
]
replacements=[]
for source in sources:
 with urlopen(Request(source["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=24) as response:
  raw=response.read(7_000_001)
 assert len(raw)<7_000_000
 im=Image.open(BytesIO(raw));im.load()
 assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=450
 actual=ImageOps.fit(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 family=D/"pending-09"
 old=list(family.glob(f"{source['slot']:02d}_*.jpg"))
 assert len(old)==1,(source["slot"],old)
 prev_hash=hashlib.sha256(old[0].read_bytes()).hexdigest()
 old[0].unlink()
 p=family/f"{source['slot']:02d}_v2541-{source['label']}.jpg"
 actual.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes()
 assert len(b)<2000000 and Image.open(p).size==(1080,1080)
 replacements.append({"slot":source["slot"],"photo":str(p.relative_to(O)),
   "old_sha256":prev_hash,"new_sha256":hashlib.sha256(b).hexdigest(),
   "src_sha256":hashlib.sha256(raw).hexdigest(),"src_size":list(im.size),"src_url":source["url"],"role":source["role"]})
oldfiles=list(BASE.glob("pending-*/*.jpg"))
newfiles=list(D.glob("pending-*/*.jpg"))
assert len(oldfiles)==156 and len(newfiles)==156
unchanged=0
for f in oldfiles:
 if f.parent.name=="pending-09" and f.name[:2] in ("02","04"):continue
 assert f.read_bytes()==(D/f.relative_to(BASE)).read_bytes(),str(f)
 unchanged+=1
assert unchanged==154
counts={folder.name:len(list(folder.glob("*.jpg"))) for folder in D.glob("pending-*")}
assert len(counts)==30
for n in range(1,31):
 assert counts[f"pending-{n:02d}"]==(6 if n in (1,2,4,5,6,7) else 5)
for file in newfiles:
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2000000
manifest={"version":"v2541","date":"2026-11-04","family":"pending-09","product":"OBgE Oil Control Finisher 5g",
"new_genuine_photo_replacements":replacements,"old_other_154_JPGs_byte_identical":True,
"total_qa_JPGs":156,"all_30_families_retained":True,"no_synthetic_product_or_shade_images":True,
"commercial_photo_rights_approved":False,"actual_owned_stock_edition_confirmed":False,
"original_MK_logo_applied":False,"final_sale_QA":False,
"prior_verified_public_55_urls_preserved":True,"new_public_urls":0,"excel_created_or_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"unchanged":154,"real_photographs_replaced":2,"sales_approved":False}))
