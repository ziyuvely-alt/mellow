#!/usr/bin/env python3
"""Only new pending-25 BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50ml sources.
Downloaded photos are QA evidence, not licensed commercial images.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import urllib.request,io,hashlib,json
out=Path("v2479-bioheal-nad-cream-source");out.mkdir(exist_ok=True)
root="https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/"
sources=[("10","jpg"),("11","jpg"),("05","jpg"),("04","jpg"),("06","jpg"),("09","jpeg")]
items=[];tiles=[];hashes=set()
for suffix,ext in sources:
 url=f"{root}A000000246299{suffix}ko.{ext}?l=ko"
 item={"url":url,"status":"SOURCE_UNAVAILABLE"}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as response: raw=response.read(8000001)
  if len(raw)>8000000:raise ValueError("oversize")
  im=Image.open(io.BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<320:raise ValueError("not usable full-size source")
  sha=hashlib.sha256(raw).hexdigest()
  if sha in hashes: item.update(status="IDENTICAL_DUPLICATE",sha256=sha);items.append(item);continue
  hashes.add(sha)
  filename=f"original-{len(tiles)+1:02d}.jpg"
  im.convert("RGB").save(out/filename,"JPEG",quality=94,optimize=True)
  item.update(status="ORIGINAL_PIXELS_DOWNLOADED_VISUAL_QA_PENDING",filename=filename,sha256=sha,dimensions=list(im.size),bytes=len(raw))
  canvas=Image.new("RGB",(370,405),"white");thumb=ImageOps.contain(im.convert("RGB"),(350,350));canvas.paste(thumb,((370-thumb.width)//2,5))
  ImageDraw.Draw(canvas).text((12,368),filename,fill="#111111");tiles.append(canvas)
 except Exception as e:item["error"]=str(e)[:180]
 items.append(item)
if tiles:
 contact=Image.new("RGB",(370*min(3,len(tiles)),405*((len(tiles)+2)//3)),"white")
 for i,t in enumerate(tiles):contact.paste(t,(370*(i%3),405*(i//3)))
 contact.save(out/"source-contact.jpg",quality=90)
report={"family":"pending-25","date":"2026-11-04","product":"BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50ml","verified_product_page":"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246299","downloaded_count":len(tiles),"items":items,"retailer_image_rights_verified":False,"stock_photo_edition_verified":False,"published":False,"new_public_urls":0,"old_jpgs_recreated":0,"spreadsheet_shared":False}
(out/"source-ledger.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"downloaded":len(tiles),"expected":len(sources),"item_statuses":[x["status"] for x in items]}))
