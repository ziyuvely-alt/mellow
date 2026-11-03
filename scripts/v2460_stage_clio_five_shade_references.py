#!/usr/bin/env python3
"""Acquire only independently discovered exact CLIO Essential Cushion 5-shade chart candidates.
Never publish these third-party source images as Shopee/customer content.
"""
import hashlib, json, io, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
OUT=Path("v2460-clio-actual-swatch-evidence"); OUT.mkdir(exist_ok=True)
sources=[
 {"id":"candidate-01","url":"https://cdn.zochil.shop/7566e0e7-0271-48b9-b798-cff4b3db1b01_t1500.jpg","provider":"Klerskin product gallery","kind":"five-shade brand-graphic photo"},
 {"id":"candidate-02","url":"https://cdn11.bigcommerce.com/s-noog3x4u9a/images/stencil/1280x1280/products/9224/27814/Screenshot_2025-12-18_122613__73856.1766060953.jpg?c=2","provider":"Melon and Starfish retailer","kind":"five-shade actual hand/arm swatches"},
 {"id":"candidate-03","url":"https://www.freshmask.ch/cdn/shop/files/clio-kill-cover-mesh-glow-essential-cushion-set-refill-new-8236383_1024x1024%402x.png?v=1774266267","provider":"Fresh Mask retailer","kind":"cushion photo with shades"}
]
required=["19C Light","19N Porcelain","21C Lingerie","21N Linen","23N Ginger"]
ledger={"date":"2026-11-04","family":"pending-06","exact_product":"CLIO Kill Cover Mesh Glow Essential Cushion planned set","seller_options":required,"source_status":"CANDIDATE_BYTES_ONLY_NOT_OFFICIAL_NOT_LICENSED","rights_verified":False,"stock_edition_verified":False,"shade_colors_manually_approved":False,"published":False,"results":[]}
tiles=[]
for it in sources:
 result={"id":it["id"],"url":it["url"],"provider":it["provider"],"scene":it["kind"],"status":"FETCH_FAILED"}
 try:
  req=urllib.request.Request(it["url"],headers={"User-Agent":"Mozilla/5.0 (compatible; legitimate-product-reference-qa/1.0)","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"})
  with urllib.request.urlopen(req,timeout=18) as f:
   b=f.read(10_000_001)
   result["http_status"]=f.status
   result["content_type"]=f.headers.get("Content-Type","")
  if len(b)>10_000_000:raise ValueError("Too large")
  im=Image.open(io.BytesIO(b));im.load()
  if im.format not in ("JPEG","PNG","WEBP"):raise ValueError("unsupported source image format")
  if min(im.size)<450:raise ValueError("image too small to assess real shades")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  file=OUT/(it["id"]+"."+ext);file.write_bytes(b)
  result.update(status="SOURCE_BYTES_STAGED_QA_PENDING",size=im.size,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),file=file.name)
  tile=ImageOps.contain(im.convert("RGB"),(640,610))
  canvas=Image.new("RGB",(680,710),"#ffffff");canvas.paste(tile,((680-tile.width)//2,20));d=ImageDraw.Draw(canvas)
  d.text((20,650),it["id"]+"  "+it["provider"],fill="#111111");tiles.append(canvas)
 except Exception as e: result["failure"]=str(e)[:220]
 ledger["results"].append(result)
ledger["successful_source_files"]=len(tiles)
ledger["note"]="A retailer's shade photo is not automatically the product brand's official image, and no image reuse license is implied. Verify exact stock edition and options before any consumer-facing chart."
(OUT/"QA-ledger.json").write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if tiles:
 sheet=Image.new("RGB",(680*len(tiles),710),"white")
 for i,t in enumerate(tiles):sheet.paste(t,(i*680,0))
 sheet.save(OUT/"candidate-contact.jpg",quality=86)
print(json.dumps({"successful_sources":len(tiles),"checks":ledger["results"]},ensure_ascii=False,indent=2))
