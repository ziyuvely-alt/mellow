#!/usr/bin/env python3
"""Only two image upgrades: BIOHEAL BOH NAD-PRIZCELL Glow Power Serum 30 mL,
correct metallic-cap red bottle, photos from manufacturer product distributors.
Do not substitute NAD 50ml cream or falsely assume permission to redistribute.
Keep other 154 JPEG files exactly the same as v2543. No workbook or public URLs.
"""
from pathlib import Path
from PIL import Image,ImageOps
from urllib.request import Request,urlopen
from io import BytesIO
import shutil,hashlib,json
BASE=Path("v2544-base-156/review-JPG-by-family")
assert BASE.is_dir()
OUT=Path("v2544-156-boh-prizcell-serum-photo-upgrade")
D=OUT/"review-JPG-by-family"
shutil.copytree(BASE,D)
photos=[
 {"slot":2,"src":"https://cdn-image.oliveyoung.com/prdtImg/1275/5ff8068f-c931-425a-9d1a-caf95b958352.jpg?AR=0&QT=80&RS=1500x1500",
  "role":"actual red 30ml serum bottle with metallic pump and light beam"},
 {"slot":4,"src":"https://kbeautystore.com/cdn/shop/files/9739cac1-9666-4e32-b14f-5c460c77110a_jpg.webp?v=1770815145&width=1200",
  "role":"actual 30ml red serum bottle and dropper photographed under red lighting"}]
new=[]
for entry in photos:
 with urlopen(Request(entry["src"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=23) as r:raw=r.read(8_000_001)
 assert len(raw)<8_000_000
 photo=Image.open(BytesIO(raw));photo.load()
 assert photo.format in ("JPEG","PNG","WEBP") and min(photo.size)>=550
 new_img=ImageOps.fit(photo.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 old=list((D/"pending-24").glob(f"{entry['slot']:02d}_*.jpg"))
 assert len(old)==1,old
 old_hash=hashlib.sha256(old[0].read_bytes()).hexdigest()
 old[0].unlink()
 p=D/"pending-24"/f"{entry['slot']:02d}_v2544-real-NAD-prizcell-serum-30ml.jpg"
 new_img.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes()
 assert len(b)<2_000_000 and Image.open(p).size==(1080,1080)
 new.append({"slot":entry["slot"],"role":entry["role"],"old_sha256":old_hash,
   "new_sha256":hashlib.sha256(b).hexdigest(),"source_url":entry["src"],
   "source_sha256":hashlib.sha256(raw).hexdigest(),"source_size":list(photo.size),
   "path":str(p.relative_to(OUT))})
oldfiles=list(BASE.glob("pending-*/*.jpg"));newfiles=list(D.glob("pending-*/*.jpg"))
assert len(oldfiles)==156 and len(newfiles)==156
kept=0
for p in oldfiles:
 if p.parent.name=="pending-24" and p.name[:2] in ("02","04"):continue
 assert p.read_bytes()==(D/p.relative_to(BASE)).read_bytes(),str(p)
 kept+=1
assert kept==154
for n in range(1,31):
 family=D/f"pending-{n:02d}"
 assert len(list(family.glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for p in newfiles:
 im=Image.open(p);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
m={"version":"v2544","date":"2026-11-04","family":"pending-24",
"product":"BIOHEAL BOH NAD Prizcell Glow Power Serum 30 mL","replacements":new,
"all_actual_qa_jpgs":156,"previous_154_byte_identical":True,
"source_product_volume_match":True,"commercial_photo_rights_checked":False,
"seller_owned_stock_packaging_verified":False,"MK_original_logo_applied":False,
"sales_final_QA_approved":False,"old_verified_55_public_URLs_unchanged":True,
"new_public_URLs":0,"excel_created_or_shared":False}
OUT.mkdir(exist_ok=True)
(OUT/"manifest.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"total":156,"unchanged":154,"new_real_photo_scenes":2,"sale_QA":False}))
