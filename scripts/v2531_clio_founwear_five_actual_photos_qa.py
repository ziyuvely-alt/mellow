#!/usr/bin/env python3
"""Recover physical 5-tone CLIO Founwear Cushion The Original swatch photograph.
Old planning stock only uses 19C 19N 21C 21N 23N. Do not mix newer
seven shade product-generation or source image that depicts other cushion.
The arm source is used unmodified except scaling, staged as QA-only.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from urllib.request import Request,urlopen
from io import BytesIO
import hashlib,json
O=Path("v2531-clio-founwear-five-shade-actual")
O.mkdir(exist_ok=True)
sources=[
 {"url":"https://www.ballagrio.com/cdn/shop/files/9_c8783bdb-d8c6-43ae-8a60-6da9c472d41a.jpg?v=1749660283&width=720","id":"original-arm-5shade","kind":"actual arm swatches 19C,19N,21C,21N,23N"},
 {"url":"https://cdn.shopify.com/s/files/1/0668/0022/2505/files/Photoroom_20250416_121449.png?crop=center&height=1024&v=1744795011&width=960","id":"original-face-5shade","kind":"actual cheek swatches 19C,19N,21C,21N,23N"}
]
report={"version":"v2531","date":"2026-11-04","family":"pending-05","product":"CLIO Kill Cover Founwear Cushion The Original (15g + 15g refill), 5 stock shades","source_photos":[],"new_JPGs":[],"known_stock_shades":["19C Light","19N Porcelain","21C Lingerie","21N Linen","23N Ginger"],"new_7shade_edition_not_automatically_substituted":True,
"original_source_photo_licensing_not_verified":True,"actual_stock_package_generation_unverified":True,
"MK_original_logo_unavailable":True,"not_published":True,"xlsx_created_or_shared":False}
for s in sources:
 r={**s,"status":"FAILED"}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=24) as resp:raw=resp.read(7000001)
  if len(raw)>7000000:raise ValueError("Oversized source")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<450:raise ValueError("Unusable source format/resolution")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  source_name=s["id"]+"."+ext
  (O/source_name).write_bytes(raw)
  r.update(status="GENUINE_PHOTOGRAPHIC_SOURCE_QA_HOLD",file=source_name,sha256=hashlib.sha256(raw).hexdigest(),size=list(im.size))
  # Keep source swatch pixels intact. Do not crop or paint shade information.
  canvas=im.convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
  filename=("06" if s["id"]=="original-arm-5shade" else "07")+f"-clio-founwear-{s['id']}.jpg"
  p=O/filename;canvas.save(p,"JPEG",quality=93,optimize=True,subsampling=0)
  b=p.read_bytes();assert len(b)<2000000 and Image.open(p).size==(1080,1080)
  report["new_JPGs"].append({"filename":filename,"source":source_name,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)})
 except Exception as e:r["error"]=str(e)[:200]
 report["source_photos"].append(r)
(O/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
assert report["new_JPGs"],"No valid real shade photos, fail instead of inventing colors"
print(json.dumps({"real_photo_jpg":len(report["new_JPGs"]),"sources":[x["status"] for x in report["source_photos"]]}))
