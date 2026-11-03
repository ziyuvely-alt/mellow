#!/usr/bin/env python3
"""Stage exact OBgE 100 mL All In One Double Essence ORIGINAL brand-store imagery.
Product consists of two 50 mL chambers. Never use 100 mL standalone sunscreen.
No new merchant JPG or Excel until source/stock package and rights checked.
"""
import json,io,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageOps
O=Path("v2542-obge-double-essence-brand-source-QA");O.mkdir(exist_ok=True)
api="https://obge.hk/products/all-in-one-double-essence.js"
out={"version":"v2542","date":"2026-11-04","family":"pending-11","target":"OBgE All In One Double Essence 100 mL total, 50 mL + 50 mL","source_api":api,"photos":[],"brand_source_verified":False,
"owned_stock_package_verified":False,"photo_rights_verified":False,"sale_approved":False,"xls_shared":False,"public_urls_added":0}
try:
 with urlopen(Request(api,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=23) as r:
  product=json.loads(r.read(3_000_000))
 name=product.get("title","")
 if "Double Essence" not in name:raise ValueError("Not exact product "+name)
 out["source_title"]=name;out["brand_source_verified"]=True
 photos=product.get("images",[])
 out["photo_urls_count"]=len(photos)
 images=[];seen=set()
 for raw_src in photos[:16]:
  if isinstance(raw_src,dict):raw_src=raw_src.get("src","")
  if raw_src.startswith("//"):raw_src="https:"+raw_src
  if not raw_src.startswith("https://"):continue
  try:
   with urlopen(Request(raw_src,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=18) as f:raw=f.read(7_000_001)
   if len(raw)>7_000_000:continue
   im=Image.open(io.BytesIO(raw));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<480:continue
   sha=hashlib.sha256(raw).hexdigest()
   if sha in seen:continue
   seen.add(sha)
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   filename=f"exact-double-essence-{len(images)+1:02d}.{ext}"
   (O/filename).write_bytes(raw)
   out["photos"].append({"filename":filename,"original_url":raw_src,"sha256":sha,"bytes":len(raw),"size":list(im.size),"content_visual_QA":"PENDING"})
   q=ImageOps.contain(im.convert("RGB"),(295,320));card=Image.new("RGB",(320,360),"white");card.paste(q,((320-q.width)//2,8));ImageDraw.Draw(card).text((13,332),filename,fill="#222")
   images.append(card)
  except Exception as e:out.setdefault("failed_image_urls",[]).append({"url":raw_src,"error":str(e)[:140]})
 if images:
  sheet=Image.new("RGB",(320*min(5,len(images)),360*((len(images)+4)//5)),"white")
  for i,c in enumerate(images):sheet.paste(c,((i%5)*320,(i//5)*360))
  sheet.save(O/"contact.jpg",quality=84)
except Exception as e:out["error"]=str(e)[:250]
out["actual_usable_source_images"]=len(out["photos"])
(O/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photos":len(out["photos"]),"title":out.get("source_title"),"error":out.get("error")}))
