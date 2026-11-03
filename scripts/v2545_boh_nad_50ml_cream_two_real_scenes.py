#!/usr/bin/env python3
"""Replace exactly two 50mL BOH NAD PRIZCELL Glow Boost Cream information photos.
Do NOT use misleading 30ml jar images found in galleries. Use real 50mL printed
closed jar and opened real cream photo, not synthetic color swatches or jars.
All 154 remaining v2544 JPEGs must be identical. Not commercially approved.
"""
from pathlib import Path
from PIL import Image,ImageOps
from urllib.request import urlopen,Request
from io import BytesIO
import hashlib,shutil,json
BASE=Path("v2545-input-156/review-JPG-by-family")
O=Path("v2545-156-boh-nad-cream-two-real-scenes")
D=O/"review-JPG-by-family"
assert BASE.is_dir()
shutil.copytree(BASE,D)
sources=[
 {"slot":2,"url":"https://www.ballagrio.com/cdn/shop/files/bio-heal-boh-nad-prizcell-glow-boost-cream-50ml-01.jpg?v=1770186496",
  "type":"50ml closed glossy red jar with visible 50 mL Net 1.69 fl oz label"},
 {"slot":4,"url":"https://cdn-image.oliveyoung.com/prdtImg/1102/114fd45d-4bd5-4eff-a2c5-bffda0349688.jpg?AR=0&QT=80&RS=1500x1500&SF=webp",
  "type":"original open cream jar and true cream swirl, 50 ml edition"}]
replaced=[]
for item in sources:
 with urlopen(Request(item["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=24) as response:raw=response.read(8_000_001)
 assert len(raw)<8_000_000
 im=Image.open(BytesIO(raw));im.load()
 assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=500
 product_photo=ImageOps.fit(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 old=list((D/"pending-25").glob(f"{item['slot']:02d}_*.jpg"))
 assert len(old)==1,old
 old_sha=hashlib.sha256(old[0].read_bytes()).hexdigest();old[0].unlink()
 p=D/"pending-25"/f"{item['slot']:02d}_v2545-real-BOH-NAD-cream-50ml.jpg"
 product_photo.save(p,"JPEG",quality=91,optimize=True,subsampling=0)
 raw_new=p.read_bytes()
 assert Image.open(p).size==(1080,1080) and len(raw_new)<2_000_000
 replaced.append({"slot":item["slot"],"photo":str(p.relative_to(O)),"source":item["url"],
 "photographic_reason":item["type"],"source_sha256":hashlib.sha256(raw).hexdigest(),
 "old_sha256":old_sha,"new_sha256":hashlib.sha256(raw_new).hexdigest(),"dimensions":list(im.size)})
oldfiles=list(BASE.glob("pending-*/*.jpg"));newfiles=list(D.glob("pending-*/*.jpg"))
assert len(oldfiles)==156 and len(newfiles)==156
same=0
for file in oldfiles:
 if file.parent.name=="pending-25" and file.name[:2] in ("02","04"):continue
 assert file.read_bytes()==(D/file.relative_to(BASE)).read_bytes(),file
 same+=1
assert same==154
for n in range(1,31):
 family=D/f"pending-{n:02d}"
 assert len(list(family.glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for file in newfiles:
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2_000_000
m={"version":"v2545","date":"2026-11-04","family":"pending-25",
 "product":"BIOHEAL BOH NAD Prizcell Glow Boost Cream 50mL",
 "physical_photo_replacements":replaced,"total_review_JPGs":156,
 "old_154_file_bytes_identical":True,"30ml_product_photo_substituted":False,
 "commercial_photo_reuse_rights_verified":False,"physical_owned_stock_50ml_edition_confirmed":False,
 "original_MK_logo_applied":False,"full_sales_QA_approved":False,
 "existing_published_55_URLs_unchanged":True,"new_verified_public_URLs":0,
 "excel_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"retained_original_bytes":154,"true_50ml_photo_upgrades":2,"sale_approved":False}))
