#!/usr/bin/env python3
"""Fallback photo sources with exact DrG Brightening Up MOISTURE Sun 50ml SKU identity.
Never confuse with BRIGHTENING UP SUN PLUS. Source photo only, no published asset.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw
from io import BytesIO
import hashlib,json
O=Path("v2488-drg-moisture-exact-photos");O.mkdir(exist_ok=True)
base="https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0018/A000000180138"
sources=[
 *[{"id":f"oliveyoung-{suffix}","url":base+suffix+"?l=ko","origin":"Olive Young exact goods A000000180138"} for suffix in ("06ko.jpg","08ko.jpg","07ko.jpg","09ko.jpg")],
 {"id":"hwahae-2023-single","url":"https://img.hwahae.co.kr/products/2023450/2023450_20230215101949.jpg","origin":"Hwahae original 2023 product catalog"},
 {"id":"dodoskin-forearm","url":"https://www.dodoskin.com/cdn/shop/files/Dr.GBrighteningUpMoistureSunSPF50_PA_50ml-4.jpg?v=1746425335&width=1200","origin":"Dodoskin actual in-use scene"}
]
ledger={"date":"2026-11-04","family_id":"pending-17","target":"Dr.G Brightening Up Moisture Sun 50ml","edition":"2023 stock, unconfirmed physical package","results":[],"approved_commercial_photo_rights":False,"new_public_urls":0}
seen=set();tiles=[]
for s in sources:
 row={**s,"status":"FETCH_HOLD"}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as f:raw=f.read(6_500_001)
  if len(raw)>6500000:raise ValueError("too large")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<300:raise ValueError("unusable format or small")
  sha=hashlib.sha256(raw).hexdigest()
  if sha in seen: row["status"]="DUPLICATE";ledger["results"].append(row);continue
  seen.add(sha);ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format];name=s["id"]+"."+ext
  (O/name).write_bytes(raw)
  row.update(status="IMAGE_BYTES_STAGED_STOCK_MATCH_QA_PENDING",file=name,dimensions=list(im.size),sha256=sha,bytes=len(raw))
  pic=ImageOps.contain(im.convert("RGB"),(340,330));card=Image.new("RGB",(360,380),"white")
  card.paste(pic,((360-pic.width)//2,7));ImageDraw.Draw(card).text((10,350),s["id"],fill="#222");tiles.append(card)
 except Exception as e:row["error"]=str(e)[:180]
 ledger["results"].append(row)
if tiles:
 sheet=Image.new("RGB",(360*min(3,len(tiles)),380*((len(tiles)+2)//3)),"white")
 for i,x in enumerate(tiles):sheet.paste(x,((i%3)*360,(i//3)*380))
 sheet.save(O/"contact.jpg",quality=88)
ledger["new_sources_downloaded"]=len(tiles)
(O/"manifest.json").write_text(json.dumps(ledger,indent=2)+"\n")
print(json.dumps({"downloaded":len(tiles),"sources":[x["id"]+":"+x["status"] for x in ledger["results"]]}))
