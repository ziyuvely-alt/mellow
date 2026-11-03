#!/usr/bin/env python3
"""Only TWO genuine Pixelpure Aura Radiance Serum 50ml photographic scenes
replace repetitive seller information cards. Real pump/texture and authentic
dual-bottle pink photography, not generated packaging or color swatches.
All other 154 JPEGs must remain byte-identical. No commercial rights/stock/MK
approval or public URLs, no spreadsheets.
"""
from pathlib import Path
from PIL import Image,ImageOps
from urllib.request import urlopen,Request
from io import BytesIO
import hashlib,json,shutil
BASE=Path("v2548-base-156/review-JPG-by-family");assert BASE.is_dir()
OUT=Path("v2548-pixelpure-aura-serum-2real-scenes")
D=OUT/"review-JPG-by-family";shutil.copytree(BASE,D)
photos=[
 {"slot":2,"url":"https://web.tradekorea.com/product/857/2334857/pixelpure_aura_radiance_serum_%28Skin_Care%29_3.jpg",
 "scene":"authentic 50ml pink pump bottle with dispensed gel and glass drops"},
 {"slot":4,"url":"https://web.tradekorea.com/product/858/2334858/pixelpure_aura_radiance_serum_%28Skin_Care%29_4.jpg",
 "scene":"two real 50ml Aura Radiance Serum pink pump bottles at distinct angles"}]
changes=[]
for s in photos:
 with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=22) as response:raw=response.read(7_000_001)
 assert len(raw)<7_000_000
 src=Image.open(BytesIO(raw));src.load()
 assert src.format in ("JPEG","PNG","WEBP") and min(src.size)>=500
 im=ImageOps.fit(src.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 old=list((D/"pending-30").glob(f"{s['slot']:02d}_*.jpg"))
 assert len(old)==1,old
 oldsha=hashlib.sha256(old[0].read_bytes()).hexdigest()
 old[0].unlink()
 path=D/"pending-30"/f"{s['slot']:02d}_v2548-real-aura-radiance-serum-50ml.jpg"
 im.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
 b=path.read_bytes();assert Image.open(path).size==(1080,1080) and len(b)<2_000_000
 changes.append({"slot":s["slot"],"path":str(path.relative_to(OUT)),"source":s["url"],
                 "scene":s["scene"],"old_sha256":oldsha,"new_sha256":hashlib.sha256(b).hexdigest(),
                 "original_sha256":hashlib.sha256(raw).hexdigest()})
old=list(BASE.glob("pending-*/*.jpg"));new=list(D.glob("pending-*/*.jpg"))
assert len(old)==len(new)==156
unchanged=0
for f in old:
 if f.parent.name=="pending-30" and f.name[:2] in ("02","04"):continue
 assert f.read_bytes()==(D/f.relative_to(BASE)).read_bytes(),str(f)
 unchanged+=1
assert unchanged==154
for n in range(1,31):
 fam=D/f"pending-{n:02d}"
 assert len(list(fam.glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for p in new:
 im=Image.open(p);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
manifest={"version":"v2548","date":"2026-11-04","family":"pending-30",
"product":"PIXELPURE Aura Radiance Serum 50ml","new_original_real_photo_changes":changes,
"total_QA_JPGs":156,"old_other_154_JPGs_byte_identical":True,
"exact_volume_product_source":"https://www.pixelpure.com/product/detail.html?product_no=25",
"photo_merchant_rights_verified":False,"seller_owned_stock_edition_QA":False,
"original_MK_logo_applied":False,"all_sales_QA_passed":False,"previous_55_urls_preserved":True,
"new_public_urls":0,"excel_created_or_shared":False}
OUT.mkdir(exist_ok=True);(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"unchanged":154,"actual_real_photo_upgrades":len(changes)}))
