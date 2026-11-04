#!/usr/bin/env python3
"""v298: inspect five never-used source slots for separate cushion / powder pact roles."""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
import io,json,hashlib,concurrent.futures
TARGET={"1000000178":[2,3,4],"1000000184":[1,2]}
master={str(r["product_id"]):r for r in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
out=Path("/tmp/bbia-v298");out.mkdir(exist_ok=True,parents=True)
jobs=[(sku,i,master[sku]["detail_references"][i]) for sku,indices in TARGET.items() for i in indices]
def fetch(t):
 sku,i,url=t;rec=dict(goodsNo=sku,source_index=i,url=url)
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as r: data=r.read(12_000_000)
  im=Image.open(io.BytesIO(data));im.load()
  fn=f"BBIA_{sku}_SOURCE_{i}_v298.jpg";(out/fn).write_bytes(data)
  rec.update(status="SOURCE_SAVED",file=fn,dimensions=[im.width,im.height],sha256=hashlib.sha256(data).hexdigest())
  return rec,im.convert("RGB")
 except Exception as e:rec.update(status="HOLD_SOURCE",error=str(e)[:160]);return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as p:result=list(p.map(fetch,jobs))
board=Image.new("RGB",(1800,1080),"#f7f6f4");d=ImageDraw.Draw(board)
d.text((15,10),"BBIA v298 FIVE PREVIOUSLY UNREVIEWED CUSHION/PACT DETAILS",fill="#222222")
for row,sku in enumerate(TARGET):
 y=45+row*510;d.text((12,y),sku+" "+master[sku]["family"],fill="#222222")
 for col,(rec,img) in enumerate([v for v in result if v[0]["goodsNo"]==sku]):
  x=col*595
  if img is None:d.text((x+5,y+45),"HOLD",fill="red");continue
  full=img.copy();full.thumbnail((200,400));board.paste(full,(x+5,y+28))
  c=img.crop((0,0,img.width,min(img.height,1050)));c.thumbnail((335,400))
  board.paste(c,(x+230,y+28))
  d.text((x+5,y+439),f"INDEX {rec['source_index']}: {img.width}x{img.height}",fill="#444444")
board.save(out/"BBIA_v298_FIVE_UNUSED_SOURCES_CONTACT.jpg",quality=89)
manifest={"checkpoint":"v298","parent":"v297","sources_requested":len(jobs),"sources_saved":sum(a["status"]=="SOURCE_SAVED" for a,_ in result),"records":[a for a,_ in result],"new_sales_approved":0,"published_unchanged":True}
(out/"BBIA_v298_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print("V298_RESULT",json.dumps({"sources_saved":manifest["sources_saved"]}))
