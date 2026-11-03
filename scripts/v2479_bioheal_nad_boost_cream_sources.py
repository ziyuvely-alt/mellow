#!/usr/bin/env python3
"""Source-first stock-safe BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50 mL photo capture.
Only candidate source bytes; do not produce final sales JPGs until exact edition/rights checked.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from urllib.request import Request,urlopen
from io import BytesIO
import hashlib,json
p=Path("v2479-bioheal-boost-cream-sources");p.mkdir(exist_ok=True)
prefix="https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A000000246299"
shots=["10ko.jpg","11ko.jpg","05ko.jpg","04ko.jpg","06ko.jpg","09ko.jpeg"]
ledger={"date":"2026-11-04","family_id":"pending-25","target":"BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50ml","exact_retailer_goods_no":"A000000246299","sources":[],"verified_sale_ready":False,"seller_original_MK_logo_available":False,"reused_completed_images":False,"public_url_added":0}
cards=[]
for i,suffix in enumerate(shots,1):
 url=prefix+suffix+"?l=ko"
 item={"image_source_url":url,"status":"FETCH_HOLD"}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as resp:
   raw=resp.read(8000001)
  if len(raw)>8000000:raise ValueError("Large image")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<300:raise ValueError("Insufficient resolution/format")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  name=f"source-{i:02d}.{ext}";(p/name).write_bytes(raw)
  item.update(status="SOURCE_BYTES_STAGED_VISUAL_QA_PENDING",filename=name,dimensions=im.size,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  thumb=ImageOps.contain(im.convert("RGB"),(330,340))
  c=Image.new("RGB",(360,398),"white");c.paste(thumb,((360-thumb.width)//2,5));ImageDraw.Draw(c).text((15,358),name,fill="#222222")
  cards.append(c)
 except Exception as e:item["error"]=str(e)[:180]
 ledger["sources"].append(item)
ledger["downloaded_photo_candidates"]=len(cards)
if cards:
 w=360*min(len(cards),3);h=398*((len(cards)+2)//3);sheet=Image.new("RGB",(w,h),"white")
 for idx,t in enumerate(cards):sheet.paste(t,((idx%3)*360,(idx//3)*398))
 sheet.save(p/"source-contact.jpg",quality=88)
(p/"source-manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"source_files":len(cards),"statuses":[x["status"] for x in ledger["sources"]]}))
