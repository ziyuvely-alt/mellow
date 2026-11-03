#!/usr/bin/env python3
"""Recover real 15g MISSHA Magic Cushion Cover Lasting pink compact package photos.
Do not confuse Moist Up, Velvet Finish, newer PRO Cushion, or a generated package.
Stage for QA-only, commercial/photo rights and exact owned-stock edition unverified.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw
import json,hashlib
OUT=Path("v2529-missha-cover-physical-source");OUT.mkdir(exist_ok=True)
sources=[
 {"name":"N21-pink-box-and-compact","uri":"https://cdn.makeupshop.ro/imagini-makeup/produse/original/3-profil-magic-cushion-cover-lasting-6zs20t2z.jpg","seller":"MakeupShop Romania","expected":"pastel pink N21 full carton and closed compact"},
 {"name":"N23-pink-box-and-compact","uri":"https://kbeautymx.com/cdn/shop/files/IMG-2981.jpg?v=1733271488&width=1445","seller":"KBeauty MX","expected":"pastel pink N23 carton and closed compact"},
 {"name":"N21-N23-open-puffs-packages","uri":"https://down-vn.img.susercontent.com/file/sg-11134201-22110-cbwkev75wejv4b","seller":"Shopee Vietnam","expected":"two pastel pink boxes labeled N21 & N23 plus an open authentic compact"}
]
report={"date":"2026-11-04","family":"pending-01","target":"MISSHA Magic Cushion Cover Lasting 15g actual product photo",
"source_captures":[],"existing_6_JPGs_unmodified":True,"photo_use_permission":False,"owned_stock_pack_edition_verification":False,
"no_public_publish":True,"excel_shared":False}
cards=[]
for q in sources:
 d={**q,"status":"FAILED"}
 try:
  with urlopen(Request(q["uri"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"}),timeout=22) as r:
   raw=r.read(7500001)
  if len(raw)>7500000:raise ValueError("file too large")
  im=Image.open(BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<420:raise ValueError("not usable source photo")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  filename=q["name"]+"."+ext;(OUT/filename).write_bytes(raw)
  d.update(status="GENUINE_SOURCE_CANDIDATE_VISUAL_QA_PENDING",file=filename,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),dimensions=list(im.size))
  sample=ImageOps.contain(im.convert("RGB"),(510,510))
  tile=Image.new("RGB",(530,560),"white");tile.paste(sample,((530-sample.width)//2,5));ImageDraw.Draw(tile).text((14,527),q["name"],fill="#202020")
  cards.append(tile)
 except Exception as e:d["error"]=str(e)[:220]
 report["source_captures"].append(d)
if cards:
 sheet=Image.new("RGB",(530*len(cards),560),"white")
 for i,t in enumerate(cards):sheet.paste(t,(530*i,0))
 sheet.save(OUT/"contact.jpg",quality=88)
report["photos_recovered"]=len(cards)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_source_photos":len(cards),"sources":[x["status"] for x in report["source_captures"]]}))
