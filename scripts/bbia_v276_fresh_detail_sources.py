#!/usr/bin/env python3
"""v276: verify three missing image roles using UNREVIEWED detail source slots.
Never regenerate earlier v207/v208 brow, v275 lip, or published artwork.
"""
import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
IDS=["1000000108","188","1000000209"]
INDEXES={"1000000108":[3,4,5],"188":[3,4,5],"1000000209":[2,3,4]}
OUT=Path("/tmp/bbia-v276");OUT.mkdir(parents=True,exist_ok=True)
master={str(v["product_id"]):v for v in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
jobs=[(sku,index,master[sku]["detail_references"][index]) for sku in IDS for index in INDEXES[sku]]
def get(job):
 sku,index,url=job
 result={"goodsNo":sku,"index":index,"url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as response:raw=response.read(12000000)
  im=Image.open(io.BytesIO(raw));im.load()
  filename=f"BBIA_{sku}_DETAIL_{index}_ORIGINAL_v276.jpg"
  (OUT/filename).write_bytes(raw)
  result.update(status="SAVED_ORIGINAL",file=filename,dimensions=[im.width,im.height],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  return result,im.convert("RGB")
 except Exception as e:
  result.update(status="HOLD",error=f"{type(e).__name__}: {str(e)[:135]}")
  return result,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(get,jobs))
contact=Image.new("RGB",(1770,1680),"#f7f7f6")
draw=ImageDraw.Draw(contact)
draw.text((12,12),"BBIA v276 | 3 PRODUCTS x 3 UNREVIEWED SOURCE SLOTS | NO AUTOMATIC APPROVAL",fill="#222222")
for row,sku in enumerate(IDS):
 y=42+row*540
 draw.text((15,y),sku+" / "+master[sku]["family"],fill="#222222")
 entries=[(entry,im) for entry,im in results if entry["goodsNo"]==sku]
 for col,(entry,im) in enumerate(entries):
  x=col*590+10
  if im is None:
   draw.text((x+20,y+90),"DOWNLOAD HOLD",fill="#aa2222");continue
  full=im.copy();full.thumbnail((240,400),Image.Resampling.LANCZOS)
  contact.paste(full,(x+8,y+35))
  upper=im.crop((0,0,im.width,min(im.height,900)));upper.thumbnail((300,400),Image.Resampling.LANCZOS)
  contact.paste(upper,(x+260,y+35))
  draw.text((x+12,y+453),f"detail {entry['index']} / {im.width}x{im.height}",fill="#444444")
contact.save(OUT/"BBIA_v276_NINE_UNREVIEWED_DETAIL_CONTACT.jpg",quality=88)
report={"checkpoint":"v276","parent":"v275","families":IDS,"requested":len(jobs),"verified_originals":sum(r["status"]=="SAVED_ORIGINAL" for r,_ in results),"sources":[r for r,_ in results],"original_approved_images_changed":False,"new_sales_approved":0,"next":"Manual select source-only product photo regions and produce candidates only if distinct from prior role"}
(OUT/"BBIA_v276_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V276_SOURCES",json.dumps({"requested":len(jobs),"downloaded":report["verified_originals"]}))
