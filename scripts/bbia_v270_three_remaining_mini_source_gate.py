#!/usr/bin/env python3
"""v270: 3 previously untouched MINI families. Batch source identity QA only, no publishing."""
import concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
ids=["1000000187","1000000120","1000000208"]
rows={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
tasks=[(sku,i,url) for sku in ids for i,url in enumerate([rows[sku]["official_photo_url"]]+rows[sku]["detail_references"][:2])]
def get(t):
 sku,i,url=t
 rec={"goodsNo":sku,"slot":i,"source":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as res:data=res.read(12000000)
  img=Image.open(io.BytesIO(data));img.load()
  rec.update(status="DOWNLOADED",size=[img.width,img.height],sha256=hashlib.sha256(data).hexdigest())
  return rec,img.convert("RGB")
 except Exception as e:
  rec.update(status="SOURCE_HOLD",reason=str(e)[:130]);return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e: result=list(e.map(get,tasks))
out=Path("/tmp/bbia-v270");out.mkdir(exist_ok=True,parents=True)
board=Image.new("RGB",(1635,1530),"#f8f8f8");d=ImageDraw.Draw(board)
d.text((10,10),"BBIA v270 | 3 MINI FAMILIES X HERO + 2 DETAIL | UNVERIFIED PACKAGING",fill="#252525")
for r,sku in enumerate(ids):
 y=r*490+40;d.text((10,y),sku+" "+rows[sku]["family"],fill="#222222")
 for n in range(3):
  rec,img=result[r*3+n];x=10+n*545
  if img is None:
   d.text((x,y+100),"SOURCE HOLD",fill="#ae2222");continue
  mini=img.copy();mini.thumbnail((250,370));board.paste(mini,(x,y+35))
  crop=img.crop((0,0,img.width,min(800,img.height)));crop.thumbnail((250,370))
  board.paste(crop,(x+260,y+35))
  d.text((x,y+414),f"source{n} {img.width}x{img.height}",fill="#555555")
board.save(out/"BBIA_v270_THREE_MINI_SOURCE_CONTACT.jpg",quality=88)
manifest={"checkpoint":"v270","parent":"v269","family_goodsNo":ids,"attempted_sources":len(tasks),"success":sum(a["status"]=="DOWNLOADED" for a,b in result),
          "sources":[a for a,b in result],"new_sale_images":0,"published_modified":False,"mini_identity_status":"VISUAL_QA_PENDING"}
(out/"BBIA_v270_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print("V270_RESULT",json.dumps({"families":len(ids),"requested":len(tasks),"downloads":manifest["success"]}))
