#!/usr/bin/env python3
"""v2537: targeted one-photo correction for MISSHA 70ml Firming Repair Cream.
Original 156 review JPGs preserved except pending-14 slot 01 (net-content info
replaced by authentic new camera scene of exact 70ml jar and ceramic vases).
Never mix serum/shot, invent packaging, remove product marks, or publish a
third-party photo before rights and stock-edition checks.
"""
from pathlib import Path
from PIL import Image,ImageOps
from io import BytesIO
from urllib.request import Request,urlopen
import hashlib,json,shutil
BASE=Path("v2537-input-156/review-JPG-by-family")
assert BASE.is_dir()
O=Path("v2537-156-missha-cream-photo-correction")
DEST=O/"review-JPG-by-family"
shutil.copytree(BASE,DEST)
url="https://lacosmetique.com.au/cdn/shop/files/pdrn-nad-firming-repair-cream-70ml-1187963.jpg?v=1782718570&width=1000"
with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=25) as r:raw=r.read(6_000_001)
assert len(raw)<6_000_000
original=Image.open(BytesIO(raw));original.load()
assert original.format in ("JPEG","PNG","WEBP") and min(original.size)>=450
# Preserve photographic integrity: no AI-generated packaging or additive product imagery.
shot=ImageOps.fit(original.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
old=list((DEST/"pending-14").glob("01_*.jpg"))
assert len(old)==1,old
old_hash=hashlib.sha256(old[0].read_bytes()).hexdigest()
old[0].unlink()
p=DEST/"pending-14/01-v2537-actual-MISSHA-firming-repair-cream-vases.jpg"
shot.save(p,"JPEG",quality=91,optimize=True,subsampling=0)
assert Image.open(p).size==(1080,1080) and p.stat().st_size<2_000_000
previous=list(BASE.glob("pending-*/*.jpg"))
now=list(DEST.glob("pending-*/*.jpg"))
assert len(previous)==156 and len(now)==156
unchanged=0
for f in previous:
 if f.parent.name=="pending-14" and f.name.startswith("01_"):continue
 assert (DEST/f.relative_to(BASE)).read_bytes()==f.read_bytes(),str(f)
 unchanged+=1
assert unchanged==155
counts={folder.name:len(list(folder.glob("*.jpg"))) for folder in DEST.glob("pending-*")}
assert len(counts)==30
for n in range(1,31):
 family=f"pending-{n:02d}"
 assert counts[family]==(6 if n in (1,2,4,5,6,7) else 5),(family,counts[family])
for file in now:
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2_000_000
info={"version":"v2537","date":"2026-11-04","family":"pending-14",
"product":"MISSHA Camellia PDRN NAD+ Firming Repair Cream 70 mL",
"replaced_slot":1,"prior_info_sha256":old_hash,
"photo":str(p.relative_to(O)),"photo_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
"original_photo_url":url,"source_file_sha256":hashlib.sha256(raw).hexdigest(),
"source_photo_dimensions":list(original.size),"previous_files_unchanged":155,
"total_actual_JPGs":156,"families":30,"photo_visual_licensing_unverified":True,
"physical_owned_stock_package_unverified":True,"MK_logo_original_missing":True,
"retail_sales_QA":False,"existing_public_55_urls_untouched":True,
"new_public_urls":0,"excel_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(info,indent=2)+"\n")
print(json.dumps({"total":156,"retained_byte_identical":155,"true_photo_replacements":1,"original_photo_size":original.size}))
