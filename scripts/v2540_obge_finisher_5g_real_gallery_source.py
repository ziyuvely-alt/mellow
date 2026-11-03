#!/usr/bin/env python3
"""Retrieve ORIGINAL OBgE Oil Control Finisher 5g gallery photographs from official Shopify.
For QA only, do not publish source images without commercial reuse clearance.
No invented product rendering, no substitution of OBgE Perfect Cushion/other skin products.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import json,hashlib
out=Path("v2540-obge-finisher-real-official-photos")
out.mkdir(exist_ok=True)
endpoint="https://obgeglobal.com/products/oil-control-finisher.js"
report={"date":"2026-11-04","version":"v2540","family":"pending-09","product":"OBgE Oil Control Finisher 5g",
"official_catalog":"https://obge.co.kr/product/detail.html?product_no=1865",
"global_shopify_api":endpoint,"gallery":[],"success":False,"published":False,
"licensed_photo_use":False,"physical_stock_edition_match":False,"spreadsheet_shared":False}
try:
 with urlopen(Request(endpoint,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=25) as r:
  obj=json.loads(r.read(3_000_000))
 title=obj.get("title","")
 if "Oil Control Finisher" not in title:raise ValueError("Wrong product title "+title)
 report["api_title"]=title
 report["variant_titles"]=[x.get("title") for x in obj.get("variants",[])]
 uris=obj.get("images",[])
 report["gallery_urls_found"]=len(uris)
 hashes=set();thumbs=[]
 for u in uris[:24]:
  if isinstance(u,dict):u=u.get("src","")
  if u.startswith("//"):u="https:"+u
  if not u.startswith("https://"):continue
  try:
   with urlopen(Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=18) as rr:b=rr.read(7_000_001)
   if len(b)>7_000_000:continue
   im=Image.open(BytesIO(b));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<550:continue
   sha=hashlib.sha256(b).hexdigest()
   if sha in hashes:continue
   hashes.add(sha)
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   name=f"original-{len(report['gallery'])+1:02d}.{ext}"
   (out/name).write_bytes(b)
   report["gallery"].append({"file":name,"sha256":sha,"source_url":u,
      "dimensions":list(im.size),"bytes":len(b),"product_label_match_QA":"PENDING","rights":"HOLD"})
   tile=Image.new("RGB",(350,390),"white")
   p=ImageOps.contain(im.convert("RGB"),(325,335));tile.paste(p,((350-p.width)//2,7))
   ImageDraw.Draw(tile).text((12,349),name,fill="#222222");thumbs.append(tile)
  except Exception as e:report.setdefault("download_failures",[]).append(str(e)[:130])
 if thumbs:
  canvas=Image.new("RGB",(350*min(5,len(thumbs)),390*((len(thumbs)+4)//5)),"white")
  for i,t in enumerate(thumbs):canvas.paste(t,((i%5)*350,(i//5)*390))
  canvas.save(out/"contact.jpg",quality=85)
 report["success"]=bool(report["gallery"])
except Exception as e:report["error"]=str(e)[:300]
(out/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"gallery_count":len(report["gallery"]),"official_product":report.get("api_title"),"error":report.get("error")}))
