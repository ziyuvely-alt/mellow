#!/usr/bin/env python3
"""2022-era Dr.G R.E.D Blemish Clear Soothing Cream 70mL exact packaging photo.
Do not substitute 2025/26 Clear Soothing Cream EX; do not publish retailer photos.
"""
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
from io import BytesIO
import hashlib,json
O=Path("v2502-drg-2022-soothing-cream-qa");O.mkdir(exist_ok=True)
S=[{"id":"tenbyten-old-jar-carton","url":"https://webimage.10x10.co.kr/image/basic1000/448/B004488766.jpg","product":"old jar with white-green carton, 5-CICA complex / clear soothing cream"}]
res={"date":"2026-11-04","family":"pending-16","target":"Dr.G R.E.D Blemish Clear Soothing Cream 70ml (2022-era old stock)","comparative_new_product":"R.E.D Blemish Clear Soothing Cream EX (modern 10-Cica Exosome)","status":"SOURCING_ONLY","sources":[],"source_photo_reuse_rights":False,"physical_owned_stock_edition_match":False,"new_public_urls":0,"excel_shared":False}
cards=[]
for s in S:
 t={**s,"status":"DOWNLOAD_FAILED"}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=23) as r:raw=r.read(5000001)
  if len(raw)>5000000:raise ValueError("oversized")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<400:raise ValueError("unusable image")
  name=s["id"]+"."+{"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  (O/name).write_bytes(raw)
  t.update(status="REAL_2022_PRODUCT_IMAGE_QA_HOLD",file=name,source_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),dimensions=im.size)
  c=Image.new("RGB",(550,615),"white");pic=ImageOps.contain(im.convert("RGB"),(520,540));c.paste(pic,((550-pic.width)//2,10));ImageDraw.Draw(c).text((16,563),s["id"],fill="#333333");cards.append(c)
 except Exception as e:t["error"]=str(e)[:220]
 res["sources"].append(t)
if cards:
 cards[0].save(O/"contact.jpg",quality=89)
res["actual_source_count"]=len(cards)
(O/"manifest.json").write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"actual_source_count":len(cards),"status":[x["status"] for x in res["sources"]]}))
