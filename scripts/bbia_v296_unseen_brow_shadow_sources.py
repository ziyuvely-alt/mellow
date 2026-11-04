#!/usr/bin/env python3
"""v296: Inspect truly unused reference indices for two underfilled families.
No JPGs from v277, v255, v294 or other checkpoints are touched.
"""
import concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
TARGET={"1000000108":[0,1,2],"238":[3,4,5,6]}
OUT=Path("/tmp/bbia-v296");OUT.mkdir(parents=True,exist_ok=True)
master={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf8"))["families"]}
jobs=[(sku,i,master[sku]["detail_references"][i]) for sku,indices in TARGET.items() for i in indices]
def run(t):
 sku,i,url=t;r={"goodsNo":sku,"source_index":i,"source_url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as f:data=f.read(11_000_000)
  photo=Image.open(io.BytesIO(data));photo.load()
  name=f"BBIA_{sku}_ORIGINAL_DETAIL_{i}_v296.jpg";(OUT/name).write_bytes(data)
  r.update(status="SAVED_SOURCE",filename=name,dimensions=[photo.width,photo.height],sha256=hashlib.sha256(data).hexdigest())
  return r,photo.convert("RGB")
 except Exception as e:
  r.update(status="HOLD_SOURCE",error=f"{type(e).__name__}: {str(e)[:130]}")
  return r,None
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
 result=list(pool.map(run,jobs))
sheet=Image.new("RGB",(1900,1550),"#f7f6f5")
d=ImageDraw.Draw(sheet)
d.text((15,12),"BBIA v296 | 7 ORIGINAL PHOTOS - PRIORITY UNDERFILLED FAMILIES | NO SALES APPROVAL",fill="#242424")
for row,sku in enumerate(TARGET):
 y=45+row*720;d.text((15,y),sku+" "+master[sku]["family"],fill="#252525")
 for col,(meta,img) in enumerate([v for v in result if v[0]["goodsNo"]==sku]):
  x=col*465+5
  if img is None:
   d.text((x,y+70),"HOLD",fill="#a22");continue
  full=img.copy();full.thumbnail((190,500),Image.Resampling.LANCZOS)
  sheet.paste(full,(x+10,y+40))
  # use separate source full and cropped top quarter to enable human selection
  h=min(img.height,980)
  top=img.crop((0,0,img.width,h));top.thumbnail((230,470),Image.Resampling.LANCZOS)
  sheet.paste(top,(x+205,y+45))
  d.text((x+10,y+568),f"index {meta['source_index']}: {img.width}x{img.height}",fill="#555555")
sheet.save(OUT/"BBIA_v296_SEVEN_UNSEEN_SOURCE_CONTACT.jpg",quality=88)
report={"checkpoint":"v296","parent":"v295","families":list(TARGET),"attempted_sources":len(jobs),"saved_sources":sum(x["status"]=="SAVED_SOURCE" for x,_ in result),"source_rows":[x for x,_ in result],"public_files_modified":False,"new_sale_approved":0,"note":"Do not infer any shade name from color imagery; no new hero JPG before human source crop QA."}
(OUT/"BBIA_v296_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V296_SOURCE_BATCH",json.dumps({"downloaded":report["saved_sources"],"attempted":len(jobs)}))
