#!/usr/bin/env python3
"""Stage two *actual* CLIO Mesh Blur cushion (not Mesh Glow) five-shade source photos.
Target inventory three shades: 19C Light, 19N Porcelain, 21N Linen.
No shades invented. No cropped/commercial customer jpg until visual source QA.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw
import hashlib,json
OUT=Path("v2525-clio-mesh-blur-source-evidence");OUT.mkdir(exist_ok=True)
sources=[
{"id":"five-real-arm-swatches","url":"https://www.shegoestoseoul.com/image/catalog/PRODUCT/2025/clio/killcover-mesh-blur-cushion/clio-kill-cover-mesh-blur-cushion-23.jpg","source":"She Goes To Seoul","expect":"Five physically applied CLIO Mesh Blur swatches 19C 19N 21C 21N 23N"},
{"id":"five-face-cheek-swatches","url":"https://bizweb.dktcdn.net/100/516/042/products/36788621-7383127004751046208-n-f6789b828be44fda88ee7e68bf1602de-master-0c7289222c0c4d588b88fc2e5c17899b-1766991062125.jpg?v=1767149294700","source":"Money's Beauty","expect":"Actual five cheek swatches with distinct 19C 19N 21N labels"}
]
report={"date":"2026-11-04","family":"pending-07","target":"CLIO Kill Cover Mesh Blur Cushion 15g+15g refill","stock_shades":["19C Light","19N Porcelain","21N Linen"],"source_photos":[],"source_photo_rights_verified":False,"photo_edition_verified_against_stock":False,"approved_swatch_image":False,"published":False,"excel_shared":False}
thumb=[]
for x in sources:
 entry={**x,"status":"FAILED"}
 try:
  with urlopen(Request(x["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as response:raw=response.read(8000001)
  if len(raw)>8000000:raise ValueError("Too large")
  img=Image.open(BytesIO(raw));img.load()
  if img.format not in ("JPEG","PNG","WEBP") or min(img.size)<450:raise ValueError("Bad format or resolution")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[img.format]
  name=x["id"]+"."+ext;(OUT/name).write_bytes(raw)
  entry.update(status="PHOTO_BYTES_RECOVERED_VISUAL_QA_PENDING",name=name,sha256=hashlib.sha256(raw).hexdigest(),dimensions=list(img.size),bytes=len(raw))
  pic=ImageOps.contain(img.convert("RGB"),(510,510));t=Image.new("RGB",(540,560),"white");t.paste(pic,((540-pic.width)//2,5));ImageDraw.Draw(t).text((12,524),x["id"],fill="#252525");thumb.append(t)
 except Exception as e:entry["error"]=str(e)[:200]
 report["source_photos"].append(entry)
if thumb:
 sheet=Image.new("RGB",(540*len(thumb),560),"white")
 for i,t in enumerate(thumb):sheet.paste(t,(i*540,0))
 sheet.save(OUT/"contact.jpg",quality=88)
report["downloaded_exact_product_images"]=len(thumb)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photos":len(thumb),"results":[x["status"] for x in report["source_photos"]]}))
