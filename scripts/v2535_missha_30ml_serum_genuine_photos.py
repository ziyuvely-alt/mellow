#!/usr/bin/env python3
"""Recover MISSHA CAMELLIA PDRN+NAD+ Firming Repair Serum actual 30mL photos.
QA candidates only. Never confuse 15ml renewal shot or 70ml repair cream.
"""
import io,json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw
O=Path("v2535-missha-30ml-serum-real-photo-sources");O.mkdir(exist_ok=True)
urls=[
("actual-product-laboratory","https://lacosmetique.com.au/cdn/shop/files/AdelineProductListing_35.png?v=1779428609&width=1500"),
("actual-product-vases","https://lacosmetique.com.au/cdn/shop/files/MISSHAPDRNNADFirmingRepairSerum_500_1.jpg?v=1779774930&width=500"),
("official-japan-bottle-capsules","https://www.misshajp.com/photo/goodsimg/MS104056/ms104056-01.jpg"),
]
result={"date":"2026-11-04","family":"pending-13","product":"MISSHA Camellia PDRN NAD+ Firming Repair Serum 30ml",
"originals":[],"commercial_image_reuse_licensed":False,"physical_stock_edition_match_confirmed":False,"public_release":False,"xlsx_shared":False}
tiles=[]
for name,url in urls:
 row={"name":name,"url":url,"status":"FAILED"}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=24) as r:b=r.read(7500001)
  if len(b)>7500000:raise ValueError("Oversize")
  im=Image.open(io.BytesIO(b));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<450:raise ValueError("Unusable image")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  file=O/(name+"."+ext);file.write_bytes(b)
  row.update(status="REAL_PRODUCT_SOURCE_VISUAL_QA_PENDING",file=file.name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),dimensions=list(im.size))
  tile=Image.new("RGB",(430,460),"white");photo=ImageOps.contain(im.convert("RGB"),(410,415));tile.paste(photo,((430-photo.width)//2,5))
  ImageDraw.Draw(tile).text((14,430),name,fill="#222222");tiles.append(tile)
 except Exception as e:row["error"]=str(e)[:200]
 result["originals"].append(row)
if tiles:
 contact=Image.new("RGB",(430*len(tiles),460),"white")
 for i,tile in enumerate(tiles):contact.paste(tile,(430*i,0))
 contact.save(O/"contact.jpg",quality=87)
result["actual_source_count"]=len(tiles)
(O/"manifest.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"actual_photos":len(tiles),"results":[x["status"] for x in result["originals"]]}))
