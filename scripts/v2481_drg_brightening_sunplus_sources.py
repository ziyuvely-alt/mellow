#!/usr/bin/env python3
"""Stage only independently grounded Dr.G Brightening Up Sun+ 50 mL image source files.
No marketing claim copied. Photo usage and exact stock revision QA still required.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from urllib.request import Request,urlopen
import hashlib,io,json
out=Path("v2481-drg-brightening-up-sun-50-source");out.mkdir(exist_ok=True)
sources=[
 {"id":"eland-single-tube","url":"https://item.elandrs.com/upload/prd/orgimg/016/2302843016_0000001.jpg?h=&q=100&w=750","kind":"retailer product-only tube"},
 {"id":"gmarket-pack","url":"https://gdimg.gmarket.co.kr/2282603044/still/400?ver=1636965526","kind":"tube and branded carton"},
 {"id":"drg-global-page","url":"https://www.dr-g.com/our-products/brightening-up-sun","kind":"official product identity (HTML NOT IMAGE)"}
]
found=[];thumbs=[]
for entry in sources:
 if entry["id"]=="drg-global-page":found.append({**entry,"status":"OFFICIAL_PRODUCT_REFERENCE_ONLY"});continue
 r={**entry,"status":"SOURCE_DOWNLOAD_FAIL"}
 try:
  with urlopen(Request(entry["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as resp:raw=resp.read(6_000_001)
  if len(raw)>6_000_000:raise ValueError("too large")
  im=Image.open(io.BytesIO(raw));im.load()
  if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<350:raise ValueError("image unsupported/too small")
  h=hashlib.sha256(raw).hexdigest()
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
  file=f"{entry['id']}.{ext}";(out/file).write_bytes(raw)
  r.update(status="SOURCE_BYTES_QA_PENDING",sha256=h,size=list(im.size),bytes=len(raw),file=file)
  x=ImageOps.contain(im.convert("RGB"),(440,445));can=Image.new("RGB",(470,500),"white")
  can.paste(x,((470-x.width)//2,8));ImageDraw.Draw(can).text((10,465),entry["id"],fill="#222");thumbs.append(can)
 except Exception as e:r["error"]=str(e)[:180]
 found.append(r)
if thumbs:
 contact=Image.new("RGB",(470*len(thumbs),500),"white")
 for i,x in enumerate(thumbs):contact.paste(x,(i*470,0))
 contact.save(out/"contact.jpg",quality=90)
ledger={"date":"2026-11-04","family":"pending-18","product":"Dr.G Brightening Up Sun Plus 50ml","source_bytes_saved":len(thumbs),"sources":found,"official_identity":"https://www.dr-g.com/our-products/brightening-up-sun","photograph_rights_verified":False,"exact_inventory_pack_edition_verified":False,"released":False,"new_verified_url_count":0,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"downloaded":len(thumbs),"statuses":[x["status"] for x in found]}))
