#!/usr/bin/env python3
"""Exact Shopify OBgE HK Double Essence media recovery. No related-product image scraping."""
import json,hashlib,io
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
out=Path("v2492-obge-double-essence-exact-gallery");out.mkdir(exist_ok=True)
prod_url="https://obge.hk/products/all-in-one-double-essence.js"
data={"date":"2026-11-04","family":"pending-11","product":"OBgE All In One Double Essence 50ml + 50ml","source":prod_url,"status":"PENDING","images":[],"variants":[],"rights_verified":False,"stock_edition_matched":False,"published":False}
try:
 with urlopen(Request(prod_url,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=25) as r:
  body=r.read(5000000)
 product=json.loads(body)
 title=product.get("title","")
 if "Double Essence" not in title:raise ValueError("exact product title mismatch: "+title)
 data["title"]=title
 data["variants"]=[{"id":v.get("id"),"title":v.get("title"),"available":v.get("available")} for v in product.get("variants",[])]
 urls=[]
 for im in product.get("images",[]):
  url=im.get("src") if isinstance(im,dict) else im
  if url and url not in urls:urls.append(url)
 seen=set();tiles=[]
 for i,url in enumerate(urls[:20]):
  url="https:"+url if url.startswith("//") else url
  row={"src":url,"status":"FETCH_ERROR"}
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as r: raw=r.read(8000001)
   if len(raw)>8000000:raise ValueError("too large")
   im=Image.open(io.BytesIO(raw));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<400:raise ValueError("image unsuitable")
   sha=hashlib.sha256(raw).hexdigest()
   if sha in seen:continue
   seen.add(sha)
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   f=out/f"exact-gallery-{len(seen):02d}.{ext}";f.write_bytes(raw)
   row.update({"status":"SOURCE_BYTES_STAGED_EXACT_SKU_VISUAL_QA_PENDING","filename":f.name,"sha256":sha,"bytes":len(raw),"dimensions":im.size})
   thumb=ImageOps.contain(im.convert("RGB"),(350,350))
   card=Image.new("RGB",(370,400),"white");card.paste(thumb,((370-thumb.width)//2,5));ImageDraw.Draw(card).text((12,364),f.name,fill="#222222");tiles.append(card)
  except Exception as e:row["error"]=str(e)[:170]
  data["images"].append(row)
 if tiles:
  sheet=Image.new("RGB",(370*min(4,len(tiles)),400*((len(tiles)+3)//4)),"white")
  for i,c in enumerate(tiles):sheet.paste(c,((i%4)*370,(i//4)*400))
  sheet.save(out/"contact.jpg",quality=88)
 data["status"]="GALLERY_CAPTURED_REVIEW_PENDING"
except Exception as e:data["status"]="PRODUCT_JSON_UNAVAILABLE";data["error"]=str(e)[:300]
(out/"manifest.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":data["status"],"images_saved":sum(x["status"].startswith("SOURCE_BYTES") for x in data["images"]),"variants":data["variants"]},ensure_ascii=False))
