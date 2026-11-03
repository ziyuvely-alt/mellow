#!/usr/bin/env python3
"""Stage verified identity OBgE Oil Control Finisher 5g additional product scene candidates.
Commercial rights and final frame approval intentionally withheld.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from urllib.request import Request,urlopen
import io,hashlib,json
o=Path("v2463-obge-oil-control-real-photo");o.mkdir(exist_ok=True)
src=[
 {"id":"brand-global-open-compact","url":"https://obgeglobal.com/cdn/shop/files/83.png?v=1776049524","provider":"OBgE global official product page","role":"Open compact, applicator and product texture"},
 {"id":"retailer-dual-angle","url":"https://www.ballagrio.com/cdn/shop/files/obge-oil-control-finisher-5g-06.jpg?v=1777873278","provider":"Ballagrio retailer","role":"Two compacts from different perspectives"},
 {"id":"brand-korea-product-tiny","url":"https://cafe24img.poxo.com/obge/web/product/tiny/202509/6085fe68572f4d2e2f60cfd051e6e77e.jpg","provider":"OBgE official Korea","role":"Exact official product standalone"}
]
records=[];tiles=[]
for x in src:
 row=dict(x,status="FAILED",final_photo_rights_approved=False)
 try:
  with urlopen(Request(x["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=22) as r: b=r.read(10_000_001)
  if len(b)>10_000_000:raise ValueError("large image rejected")
  im=Image.open(io.BytesIO(b));im.load()
  if im.format not in ("PNG","JPEG","WEBP"):raise ValueError("bad format")
  if min(im.size)<300:raise ValueError("low resolution source")
  ext={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[im.format]
  f=o/(x["id"]+"."+ext);f.write_bytes(b)
  row.update(status="SOURCE_BYTES_STAGED_QA_PENDING",sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),dimensions=im.size,file=f.name)
  bgr=Image.new("RGB",(530,570),"white");im=ImageOps.contain(im.convert("RGB"),(510,500));bgr.paste(im,((530-im.width)//2,10));ImageDraw.Draw(bgr).text((8,530),x["id"],fill="#242424");tiles.append(bgr)
 except Exception as e:row["error"]=str(e)[:180]
 records.append(row)
if tiles:
 sheet=Image.new("RGB",(530*len(tiles),570),"white")
 for i,t in enumerate(tiles):sheet.paste(t,(530*i,0))
 sheet.save(o/"review-contact.jpg",quality=85)
data={"date":"2026-11-04","family":"pending-09","product":"OBgE Oil Control Finisher 5g","previous_existing_images":2,"new_source_bytes":sum(x["status"]=="SOURCE_BYTES_STAGED_QA_PENDING" for x in records),"sources":records,"commercial_reuse_permission_verified":False,"published":False,"original_MK_logo_present":False,"status":"VISUAL_AND_LICENSE_QA_PENDING"}
(o/"source-ledger.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"downloaded":data["new_source_bytes"],"ids":[r["id"] for r in records]},ensure_ascii=False))
