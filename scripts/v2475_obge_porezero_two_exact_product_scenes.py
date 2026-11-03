#!/usr/bin/env python3
"""Recover independent real-product scenes for OBgE Pore Zero Sun Cream 50ml only.
Third-party photos are staged solely for visual/source/rights review, NEVER public deployment.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from urllib.request import Request,urlopen
import io,json,hashlib
O=Path("v2475-obge-porezero-real-views");O.mkdir(exist_ok=True)
sources=[
 {"id":"soonsu-mint-cube","url":"https://soonsubeauty.com/cdn/shop/files/89268559168593820_48441449.jpg?v=1777131105","source":"Soonsu Beauty","scene":"exact PORE ZERO white teal sunscreen tube in mint & ice photo"},
 {"id":"dodoskin-product-texture","url":"https://wholesale.dodoskin.com/cdn/shop/files/OBgEPoreZeroOilControlSunCream50ml-2.jpg?v=1773208375&width=1946","source":"Dodoskin","scene":"exact white teal PORE ZERO sun cream tubes, cream texture"}
]
ledger={"family_id":"pending-23","date":"2026-11-04","seller_product":"OBgE PORE ZERO OIL CONTROL SUN CREAM 50ml","downloaded":0,"candidates":[],"commercial_photo_reuse_rights_verified":False,"published":False,"brand_label_and_tube_generation_verified":False}
tiles=[]
for it in sources:
 item={**it,"status":"FAILED"}
 try:
  with urlopen(Request(it["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"}),timeout=22) as res:b=res.read(8_000_001);item["HTTP"]=res.status
  if len(b)>8_000_000:raise ValueError("too big")
  im=Image.open(io.BytesIO(b));im.load()
  if im.format not in ("JPEG","WEBP","PNG") or min(im.size)<400:raise ValueError("too small / unsupported")
  ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[im.format];f=O/(it["id"]+"."+ext);f.write_bytes(b)
  item.update(status="IMAGE_BYTES_STAGED_VISUAL_QA_PENDING",sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),dimensions=im.size,filename=f.name)
  c=Image.new("RGB",(540,580),"white");im=ImageOps.contain(im.convert("RGB"),(520,515));c.paste(im,((540-im.width)//2,10));ImageDraw.Draw(c).text((8,540),it["id"],fill="#333");tiles.append(c)
 except Exception as e:item["error"]=str(e)[:200]
 ledger["candidates"].append(item)
if tiles:
 out=Image.new("RGB",(540*len(tiles),580),"white")
 for i,t in enumerate(tiles):out.paste(t,(540*i,0))
 out.save(O/"contact.jpg",quality=88)
ledger["downloaded"]=len(tiles)
(O/"manifest.json").write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"downloaded":len(tiles),"status":[x["status"] for x in ledger["candidates"]]}))
