#!/usr/bin/env python3
"""Stage authentic shade reference candidates, NEVER produce commercial images."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import urllib.request,io,hashlib,json
out=Path("v2461-real-option-evidence");out.mkdir(exist_ok=True)
items=[
 {"family":"pending-07","id":"clio-mesh-blur-5-shades","url":"https://i.ebayimg.com/images/g/q38AAOSwLBFoPFbw/s-l1200.jpg","identity":"CLIO Kill Cover Mesh Blur Cushion 15g","seller_options":["19C Light","19N Porcelain","21N Linen"],"expected":"Different from Mesh Glow Essential; only selected 3 of an image that may depict 5"},
 {"family":"pending-10","id":"obge-homme-3shades-old-candidate","url":"https://baseec-img-mng.akamaized.net/images/item/origin/1c8934ffbb8f36ddc491f541817199bb.jpg?imformat=generic","identity":"OBgE Perfect Homme Cushion prior generation","seller_options":["1 Ivory","2 Beige","3 Sand"],"expected":"Retailer describes 13g SPF50+ PA+++ whereas held stock is listed 15g; NEVER approve as same edition"}
]
results=[];thumbs=[]
for it in items:
 x=dict(it,status="FAILED_OR_UNVERIFIED",commercial_reuse_rights=False,stock_edition_verified=False)
 try:
  req=urllib.request.Request(it["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"})
  with urllib.request.urlopen(req,timeout=20) as f:raw=f.read(8_000_001);x["http_status"]=f.status
  if len(raw)>8_000_000:raise ValueError("too large")
  img=Image.open(io.BytesIO(raw));img.load()
  if img.format not in ("JPEG","WEBP","PNG") or min(img.size)<400:raise ValueError("unsupported format/resolution")
  ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[img.format];path=out/(it["id"]+"."+ext);path.write_bytes(raw)
  x.update(status="SOURCE_BYTES_STAGED_QA_PENDING",filename=path.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),dimensions=img.size)
  if it["family"]=="pending-10":x["qa_flag"]="POSSIBLE_WRONG_EDITION_13G_VS_STOCK_15G"
  im=ImageOps.contain(img.convert("RGB"),(600,600));b=Image.new("RGB",(650,680),"white");b.paste(im,((650-im.width)//2,8));d=ImageDraw.Draw(b);d.text((18,635),it["family"]+" "+it["id"],fill="#111111");thumbs.append(b)
 except Exception as e:x["error"]=str(e)[:250]
 results.append(x)
if thumbs:
 sheet=Image.new("RGB",(650*len(thumbs),680),"white")
 for i,im in enumerate(thumbs):sheet.paste(im,(650*i,0))
 sheet.save(out/"review-only-contact.jpg",quality=90)
ledger={"date":"2026-11-04","source_asset_status":"UNLICENSED_QA_ONLY","source_photos_downloaded":sum(x["status"]=="SOURCE_BYTES_STAGED_QA_PENDING" for x in results),"results":results,"publication_approved":False,"new_public_urls":0}
(out/"qa-ledger.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"source_photos_downloaded":ledger["source_photos_downloaded"],"results":[{"id":x["id"],"status":x["status"],"qa_flag":x.get("qa_flag"),"error":x.get("error")} for x in results]},ensure_ascii=False))
