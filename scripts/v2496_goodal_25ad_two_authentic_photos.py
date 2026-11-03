#!/usr/bin/env python3
"""Download genuine Goodal Vita C Serum Mist 25AD 100mL distinct image scenes.
Never substitute newer E-TXA mist, old formula or 2-pack bundles.
Images are sourcing evidence only until physical 25AD edition and reuse rights verified.
"""
import io,json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageOps
O=Path("v2496-goodal-mist-25ad-source-photos");O.mkdir(exist_ok=True)
sources=[
 {"id":"25ad-straight-product","url":"https://sv3-cdn.stylevana.com/media/catalog/product/g/o/goodal-green-tangerine-vita-c-serum-mist-niacinamide-hyaluronic-acid-25ad-100ml-108.jpg","seller":"Stylevana","edition_label":"25AD verified by merchant title","role":"straight full-bottle photo"},
 {"id":"25ad-angled-product","url":"https://puremarket.rs/cdn/shop/files/XXL_p0181288333_grande.webp?v=1770548956","seller":"Pure Market","edition_label":"physical image matches 25AD label; exact merchant edition not stated","role":"tilted bottle angle"}
]
ledger={"date":"2026-11-04","family":"pending-20","target":"Goodal Green Tangerine Vita C Serum Mist (25AD) 100 mL","photos":[],"commercial_reuse_rights_verified":False,"final_stock_package_match":False,"pub_urls_added":0}
cards=[]
for s in sources:
 x={**s,"status":"FAILED"}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=22) as r:raw=r.read(8000001)
  if len(raw)>8000000:raise ValueError("too large")
  im=Image.open(io.BytesIO(raw));im.load()
  if im.format not in ("PNG","JPEG","WEBP") or min(im.size)<400:raise ValueError("unusable")
  h=hashlib.sha256(raw).hexdigest()
  ext={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[im.format]
  f=O/(s["id"]+"."+ext);f.write_bytes(raw)
  x.update(status="REAL_SOURCE_PHOTO_QA_PENDING",file=f.name,sha256=h,bytes=len(raw),dimensions=im.size)
  tile=Image.new("RGB",(540,570),"white");picture=ImageOps.contain(im.convert("RGB"),(510,510))
  tile.paste(picture,((540-picture.width)//2,8))
  ImageDraw.Draw(tile).text((15,530),s["id"],fill="#333");cards.append(tile)
 except Exception as e:x["error"]=str(e)[:200]
 ledger["photos"].append(x)
if cards:
 sheet=Image.new("RGB",(540*len(cards),570),"white")
 for i,t in enumerate(cards):sheet.paste(t,(i*540,0))
 sheet.save(O/"contact.jpg",quality=90)
ledger["source_photo_count"]=len(cards)
(O/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photo_count":len(cards),"photo_statuses":[x["status"] for x in ledger["photos"]]}))
