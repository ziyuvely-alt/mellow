#!/usr/bin/env python3
"""Replace exactly TWO repetitive PIXELPURE 210ml / 70-pad information cards
with genuine original photos of correct stock jar and pads.
Preserve previous 154 JPEGs byte-identically; no 145/150 cleanser confusion.
No rights, MK-logo or physical-stock approval. Never publish or share Excel.
"""
from pathlib import Path
from PIL import Image,ImageOps
from urllib.request import urlopen,Request
from io import BytesIO
import json,hashlib,shutil
B=Path("v2546-input-156/review-JPG-by-family")
assert B.is_dir()
O=Path("v2546-156-pixelpure-pads-actual-real-scenes")
D=O/"review-JPG-by-family";shutil.copytree(B,D)
srcs=[
 {"slot":2,"url":"https://web.tradekorea.com/product/872/2334872/pixelpure_Glow_Cleansing_Serum_Pad_210ml___70_pads%28skin_care%29_2.jpg",
  "scene":"correct 210ml 70pads open pink jar with real tweezers lifting one pad"},
 {"slot":4,"url":"https://web.tradekorea.com/product/874/2334874/pixelpure_Glow_Cleansing_Serum_Pad_210ml___70_pads%28skin_care%29_4.jpg",
  "scene":"correct 210ml 70pads pink tub with lid open and real cream-colored pads"}
]
replaced=[]
for x in srcs:
 with urlopen(Request(x["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=22) as resp:raw=resp.read(6_000_001)
 assert len(raw)<6_000_000
 photo=Image.open(BytesIO(raw));photo.load()
 assert photo.format in ("JPEG","PNG","WEBP") and min(photo.size)>=500
 pic=ImageOps.fit(photo.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 existing=list((D/"pending-28").glob(f"{x['slot']:02d}_*.jpg"))
 assert len(existing)==1,existing
 prev_sha=hashlib.sha256(existing[0].read_bytes()).hexdigest();existing[0].unlink()
 dst=D/"pending-28"/f"{x['slot']:02d}_v2546-real-210ml-pads-photo.jpg"
 pic.save(dst,"JPEG",quality=91,optimize=True,subsampling=0)
 assert Image.open(dst).size==(1080,1080) and dst.stat().st_size<2_000_000
 replaced.append({"slot":x["slot"],"path":str(dst.relative_to(O)),"source":x["url"],"scene":x["scene"],
 "original_sha256":hashlib.sha256(raw).hexdigest(),"new_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"prior_sha256":prev_sha})
old=list(B.glob("pending-*/*.jpg"));now=list(D.glob("pending-*/*.jpg"))
assert len(old)==len(now)==156
unchanged=0
for f in old:
 if f.parent.name=="pending-28" and f.name[:2] in ("02","04"):continue
 assert f.read_bytes()==(D/f.relative_to(B)).read_bytes(),str(f)
 unchanged+=1
assert unchanged==154
for n in range(1,31):
 family=D/f"pending-{n:02d}"
 assert len(list(family.glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for file in now:
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2_000_000
m={"version":"v2546","date":"2026-11-04","family":"pending-28",
"product":"PIXELPURE Glow Cleansing Serum Pad 210mL / 70 pads",
"replaced_JPGs":replaced,"qa_JPG_count":156,"other_154_original_files_byte_identical":True,
"size_and_pad_count_on_source_photos":"210 mL / 70 pads",
"official_product_confirmation":"https://pixelpure.com/product/detail.html?product_no=23",
"source_photo_commercial_reuse_permission":False,
"actual_owned_stock_packaging_match":False,"original_MK_logo_applied":False,
"retail_sales_final_QA_approved":False,"previous_55_public_URLs_untouched":True,
"new_public_URLs":0,"xlsx_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"untouched":154,"real_pad_photos":2,"final_approved":False}))
