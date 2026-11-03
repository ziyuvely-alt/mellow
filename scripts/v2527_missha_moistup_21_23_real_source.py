#!/usr/bin/env python3
"""Stage original MISSHA Magic Cushion Moist Up 21/23 physical shade photo only.
Caution: do not confuse M cushion moisture Japan or Magic Cover Lasting.
Retailer copyrighted photo is strictly a review candidate pending permissions.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageOps
from io import BytesIO
import json,hashlib
O=Path("v2527-missha-moistup-21-23-original-source");O.mkdir(exist_ok=True)
sources=[
 {"id":"sagi-real-two-shades","url":"https://bizweb.dktcdn.net/100/443/867/products/cushion-duong-am-missha-magic-cushion-moist-up-spf50-plus-pa-plus-plus-plus.png?v=1701087892520","source":"Sagi","identity":"Magic Cushion Moist Up, No.21 vs No.23, original smears and natural blend"},
 {"id":"lacosmetique-actual-color","url":"https://lacosmetique.com.au/cdn/shop/files/4_0cc35267-5dcb-4fb7-b152-c99a333a65d3.jpg?v=1756087104&width=1200","source":"La Cosmetique","identity":"Magic Cushion Moist Up 21 23 color guide"}
]
data={"date":"2026-11-04","family":"pending-02","product":"MISSHA Magic Cushion Moist Up 15g","actual_stock_options":["21 Light Beige","23 Natural Beige"],"sources":[],"exact_packaging_generation_confirmed":False,"copyrighted_images_allowed_for_commercial_use":False,"published":False,"excel_shared":False}
tiles=[]
for src in sources:
 item={**src,"status":"FAILED"}
 try:
  with urlopen(Request(src["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=22) as r:raw=r.read(7_000_001)
  if len(raw)>7000000:raise ValueError("oversize")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<450:raise ValueError("small or unsupported")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format];p=O/(src["id"]+"."+ext);p.write_bytes(raw)
  item.update(status="IMAGE_ORIGINAL_BYTES_QA_ONLY",file=p.name,bytes=len(raw),dimensions=list(im.size),sha256=hashlib.sha256(raw).hexdigest())
  ph=ImageOps.contain(im.convert("RGB"),(500,500))
  card=Image.new("RGB",(530,560),"white")
  card.paste(ph,((530-ph.width)//2,5));ImageDraw.Draw(card).text((10,529),src["id"],fill="#242424");tiles.append(card)
 except Exception as e:item["error"]=str(e)[:170]
 data["sources"].append(item)
if tiles:
 sheet=Image.new("RGB",(530*len(tiles),560),"white")
 for i,card in enumerate(tiles):sheet.paste(card,(530*i,0))
 sheet.save(O/"contact.jpg",quality=88)
data["recovered_photo_count"]=len(tiles)
(O/"manifest.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"source_photos":len(tiles),"results":[x["status"] for x in data["sources"]]}))
