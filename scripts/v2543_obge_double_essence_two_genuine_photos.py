#!/usr/bin/env python3
"""Replace ONLY two info-card scenes in 156 QA images of OBgE Double Essence 100mL.
Two real photos: (1) true exposed twin pump + package from Soonsu, (2) genuine texture photo from Joom.
All other 154 original JPEG bytes preserved. No invented products, AI mockups or copied fake swatches.
Source licensing and exact user owned-stock packaging remain HOLD. No public URLs or Excel.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps
import shutil,hashlib,json
ROOT=Path("v2543-base-156/review-JPG-by-family")
assert ROOT.is_dir()
O=Path("v2543-156-obge-double-essence-real-photo-QA")
T=O/"review-JPG-by-family"
shutil.copytree(ROOT,T)
sources=[
 {"slot":2,"url":"https://soonsubeauty.com/cdn/shop/files/11314019277828210_1462891387.jpg?v=1777131344","role":"genuine white bottle with open dual nozzle, original carton and angled second bottle"},
 {"slot":4,"url":"https://img.joomcdn.net/6b3923d63b2395e63e15fb485f5cf2c3b3094cb1_original.jpeg","role":"genuine bottle with two distinct cream textures photographed behind bottle"}
]
replace=[]
for x in sources:
 with urlopen(Request(x["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=22) as r:raw=r.read(7_000_001)
 assert len(raw)<7_000_000
 im=Image.open(BytesIO(raw));im.load()
 assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=450, (x["url"],im.size)
 assert im.size[0]>0
 actual=ImageOps.fit(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 old=list((T/"pending-11").glob(f"{x['slot']:02d}_*.jpg"))
 assert len(old)==1,old
 prev=hashlib.sha256(old[0].read_bytes()).hexdigest()
 old[0].unlink()
 p=T/"pending-11"/f"{x['slot']:02d}_v2543-genuine-double-essence-photo.jpg"
 actual.save(p,"JPEG",quality=91,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 replace.append({"slot":x["slot"],"original_source":x["url"],"original_source_sha256":hashlib.sha256(raw).hexdigest(),"photo_sha256":hashlib.sha256(b).hexdigest(),"photo":str(p.relative_to(O)),"role":x["role"],"old_card_sha256":prev})
old=list(ROOT.glob("pending-*/*.jpg"));new=list(T.glob("pending-*/*.jpg"))
assert len(old)==156 and len(new)==156
same=0
for p in old:
 if p.parent.name=="pending-11" and p.name[:2] in ("02","04"):continue
 assert p.read_bytes()==(T/p.relative_to(ROOT)).read_bytes(),str(p)
 same+=1
assert same==154
for n in range(1,31):
 family=f"pending-{n:02d}"
 assert len(list((T/family).glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for p in new:
 im=Image.open(p);im.load();assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
m={"version":"v2543","date":"2026-11-04","family":"pending-11",
 "product":"OBgE All In One Double Essence 100 mL = Step 1 50 mL + Step 2 50 mL",
 "verified_unit_source":"https://www.ssg.com/item/itemView.ssg?itemId=1000464955759",
 "replaced_JPGs":replace,"total_JPGs":156,"prior_154_files_byte_identical":True,
 "full_30_family_5_or_6_JPG_count_valid":True,
 "MK_brand_logo_original_present":False,"merchant_source_photo_rights_verified":False,
 "physical_stock_package_version_verified":False,"commercial_sales_QA_approved":False,
 "old_55_public_urls_untouched":True,"new_public_urls":0,"excel_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total_qa_images":156,"unchanged":154,"two_physical_photo_replacements":len(replace)}))
