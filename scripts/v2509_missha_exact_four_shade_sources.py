#!/usr/bin/env python3
"""Source two independent REAL four-shade chart references for MISSHA Cover Lasting.
Never generate/artificially recolor shade pixels. Never publish third-party images
or assume stock edition compatibility. Contact previews are evidence only.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw
import hashlib,json
O=Path("v2509-missha-four-shade-source-review");O.mkdir(exist_ok=True)
sources=[
 {"name":"cosmic-four-shades","url":"https://cosmic.net.ua/image/cache/catalog/0011/000000000051-800x800.jpg","provider":"Cosmic Ukraine","expected":"#21 #23 #25 #27 and compact in one chart"},
 {"name":"watsons-four-shades","url":"https://www.watsons.ae/cdn/shop/files/ASW200010095_106.jpg?v=1707986940&width=1445","provider":"Watsons UAE","expected":"#21 #23 #25 #27 real cream swatches and cushion"}
]
rows=[];tiles=[]
for q in sources:
 rec={**q,"status":"FETCH_FAILED"}
 try:
  with urlopen(Request(q["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=18) as f:raw=f.read(6_500_001)
  if len(raw)>6500000:raise ValueError("oversize")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","WEBP","PNG") or min(im.size)<500:raise ValueError("unusable format/size")
  ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[im.format]
  fn=q["name"]+"."+ext;(O/fn).write_bytes(raw)
  rec.update(status="PHOTO_BYTES_CAPTURED_QA_ONLY",file=fn,sha256=hashlib.sha256(raw).hexdigest(),dimensions=list(im.size),bytes=len(raw))
  thumbnail=ImageOps.contain(im.convert("RGB"),(520,540))
  tile=Image.new("RGB",(560,600),"white")
  tile.paste(thumbnail,((560-thumbnail.width)//2,12))
  ImageDraw.Draw(tile).text((20,570),q["name"],fill="#222");tiles.append(tile)
 except Exception as e:rec["error"]=str(e)[:220]
 rows.append(rec)
if tiles:
 contact=Image.new("RGB",(560*len(tiles),600),"white")
 for i,t in enumerate(tiles):contact.paste(t,(560*i,0))
 contact.save(O/"reference-contact.jpg",quality=88)
m={"date":"2026-11-04","family_id":"pending-01","product":"MISSHA Magic Cushion Cover Lasting 15g","options":["#21","#23","#25","#27"],"source_results":rows,"exact_physical_stock_edition_verified":False,"photo_commercial_reuse_rights_verified":False,"official_original_shade_chart_approved":False,"artificial_color_swatches":False,"public_URLs_added":0,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_source_files":len(tiles),"statuses":[x["status"] for x in rows]}))
