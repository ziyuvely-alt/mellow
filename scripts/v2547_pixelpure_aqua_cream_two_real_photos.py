#!/usr/bin/env python3
"""Replace only two repetitive Pixelpure Radiance Aqua Soothing Cream 50ml
informational frames with TWO exact manufacturer product photographs:
(1) authentic closed 50ml pink jar on white cream; (2) real opened jar and texture.
Keep 154 other actual v2546 JPEGs byte-identical. No fake packaging or colors.
Commercial rights, real owned stock generation, original MK logo remain QA HOLD.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps
import shutil,json,hashlib
B=Path("v2547-base-156/review-JPG-by-family")
assert B.is_dir()
O=Path("v2547-156-pixelpure-cream-real-scenes")
D=O/"review-JPG-by-family";shutil.copytree(B,D)
sources=[
{"slot":2,"url":"https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/f8d51ba2fbbf7cb558808d00a2f1317a.jpg",
"role":"manufacturer original closed pink 50ml jar over white cream"},
{"slot":4,"url":"https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/5695cce612cdac532a1aedacb62b3581.jpg",
"role":"manufacturer original 50ml pink open jar and genuine cream swirl"}
]
records=[]
for s in sources:
 with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=25) as r:raw=r.read(6_000_001)
 assert len(raw)<6_000_000
 img=Image.open(BytesIO(raw));img.load()
 assert img.format in ("JPEG","PNG","WEBP") and min(img.size)>=500
 out=ImageOps.fit(img.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 previous=list((D/"pending-29").glob(f"{s['slot']:02d}_*.jpg"))
 assert len(previous)==1,previous
 old_sha=hashlib.sha256(previous[0].read_bytes()).hexdigest()
 previous[0].unlink()
 p=D/"pending-29"/f"{s['slot']:02d}_v2547-real-50ml-cream-photo.jpg"
 out.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 records.append({"slot":s["slot"],"old_sha256":old_sha,"new_sha256":hashlib.sha256(b).hexdigest(),
  "source_sha256":hashlib.sha256(raw).hexdigest(),"source":s["url"],"role":s["role"],"new_file":str(p.relative_to(O))})
oldfiles=list(B.glob("pending-*/*.jpg"));newfiles=list(D.glob("pending-*/*.jpg"))
assert len(oldfiles)==len(newfiles)==156
same=0
for p in oldfiles:
 if p.parent.name=="pending-29" and p.name[:2] in ("02","04"):continue
 assert p.read_bytes()==(D/p.relative_to(B)).read_bytes(),str(p)
 same+=1
assert same==154
for n in range(1,31):
 family=D/f"pending-{n:02d}"
 assert len(list(family.glob("*.jpg")))==(6 if n in (1,2,4,5,6,7) else 5)
for p in newfiles:
 im=Image.open(p);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
manifest={"version":"v2547","date":"2026-11-04","family":"pending-29",
"product":"PIXELPURE Radiance Aqua Soothing Cream 50ml",
"exact_real_photo_replacements":records,"actual_JPG_count":156,
"prior_154_source_jpgs_unchanged":True,
"official_product":"https://eng.pixelpure.com/product/detail.html?product_no=26",
"manufacturer_photo_rights_approved_for_commercial_use":False,
"real_owned_stock_package_identical_confirmed":False,"original_MK_logo_applied":False,
"sales_final_QA":False,"prior_verified_55_public_urls_untouched":True,
"new_public_URLs":0,"excel_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"unchanged_originals":154,"genuine_new_50ml_cream_photos":2,"approved":False}))
