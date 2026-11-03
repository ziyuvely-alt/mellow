#!/usr/bin/env python3
"""Source exact Goodal 25AD eye cream 30ml, no gift bundles or wrong cream jar.
All external images are QA-only pending edition and rights verification.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageDraw,ImageOps
import json,hashlib
O=Path("v2504-goodal-25ad-eye-cream-sources");O.mkdir(exist_ok=True)
sources=[
 {"key":"single-yellow-tube","url":"https://bellubeauty.co.uk/cdn/shop/files/GOODAL-Green-Tangerine-Vita-C-Dark-Spot-Care-Eye-Cream-30ml-BelluBeauty-73210661306694.jpg?v=1777846139","reason":"Exact 30ml yellow eye cream tube, standalone"},
 {"key":"cream-texture-tube","url":"https://hikoco.co.nz/cdn/shop/files/hikoco_Goodal_GreenTangerineVitaCDarkCircleEyeCream26_01.jpg?v=1772406150","reason":"Exact product tube and texture"},
 {"key":"yellow-box-tube","url":"https://thumbnail.coupangcdn.com/thumbnails/remote/492x492ex/image/vendor_inventory/20f5/008034caf02a6153d28358f99a4d400b0a3ffa1447bde37651e353d12feb.jpg","reason":"Exact yellow carton and tube in one photo"}
]
ledger={"date":"2026-11-04","family":"pending-21","product":"Goodal Vita C Dark Spot Care Eye Cream 30ml 25AD stock","listed_25AD_SKU":"669210000423","sku_evidence_url":"https://m.shilladfs.com/estore/kr/ko/p/5754369","sources":[],"commercial_rights_verified":False,"physical_25AD_stock_verified":False,"published":False,"excel_shared":False}
cards=[]
for x in sources:
 v={**x,"status":"FETCH_FAILED"}
 try:
  with urlopen(Request(x["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as r:b=r.read(6_000_001)
  if len(b)>6000000:raise ValueError("too big")
  im=Image.open(BytesIO(b));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<420:raise ValueError("low quality")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format];fn=x["key"]+"."+ext
  (O/fn).write_bytes(b)
  v.update(status="REAL_SOURCE_BYTES_PRODUCT_MATCH_PENDING",file=fn,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),size=list(im.size))
  t=ImageOps.contain(im.convert("RGB"),(350,360));canvas=Image.new("RGB",(380,410),"white");canvas.paste(t,((380-t.width)//2,6));ImageDraw.Draw(canvas).text((12,376),x["key"],fill="#222");cards.append(canvas)
 except Exception as e:v["error"]=str(e)[:180]
 ledger["sources"].append(v)
if cards:
 sheet=Image.new("RGB",(380*len(cards),410),"white")
 for i,x in enumerate(cards):sheet.paste(x,(380*i,0))
 sheet.save(O/"contact.jpg",quality=88)
ledger["staged_actual_source_count"]=len(cards)
(O/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_staged":len(cards),"status":[x["status"] for x in ledger["sources"]]}))
