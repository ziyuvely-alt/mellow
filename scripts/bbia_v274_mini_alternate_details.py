#!/usr/bin/env python3
"""v274: Only second manufacturer detail source for three already-reviewed mini families.
Read-only original image proof, do not recreate accepted v273 JPGs.
"""
import json,io,hashlib,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
IDS=["1000000187","1000000120","1000000208"]
OUT=Path("/tmp/bbia-v274");OUT.mkdir(parents=True,exist_ok=True)
master={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
def retrieve(sku):
    url=master[sku]["detail_references"][1]
    rec={"goodsNo":sku,"url":url,"detail_index":1}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as resp: body=resp.read(12_000_000)
        im=Image.open(io.BytesIO(body));im.load()
        path=OUT/f"BBIA_{sku}_DETAIL_SOURCE_2_v274.jpg";path.write_bytes(body)
        rec.update(status="SOURCE_SAVED",file=path.name,dimensions=[im.width,im.height],bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        return rec,im.convert("RGB")
    except Exception as exc:
        rec.update(status="HOLD_DOWNLOAD",reason=f"{type(exc).__name__}: {str(exc)[:130]}")
        return rec,None
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:received=list(pool.map(retrieve,IDS))
board=Image.new("RGB",(1650,1530),"#f7f6f5")
d=ImageDraw.Draw(board);d.text((16,10),"BBIA v274 | ALTERNATE MINI PRODUCT DETAIL SOURCES, NO SALES EDIT",fill="#222222")
for n,(rec,im) in enumerate(received):
    x=n*550
    d.text((x+10,45),rec["goodsNo"]+" "+rec["status"],fill="#222222")
    if im is None:continue
    photo=im.copy();photo.thumbnail((510,540));board.paste(photo,(x+(550-photo.width)//2,80))
    for k in range(3):
        a=round(im.height*k/3);b=round(im.height*(k+1)/3)
        c=im.crop((0,a,im.width,b));c.thumbnail((510,280))
        board.paste(c,(x+(550-c.width)//2,655+k*280))
board.save(OUT/"BBIA_v274_ALTERNATE_THREE_MINI_CONTACT.jpg",quality=89)
(OUT/"BBIA_v274_MANIFEST.json").write_text(json.dumps({"checkpoint":"v274","parent":"v273","source_attempts":3,"sources_recovered":sum(r["status"]=="SOURCE_SAVED" for r,_ in received),"rows":[r for r,_ in received],"new_sales_jpg":0,"existing_approved_untouched":True},ensure_ascii=False,indent=2))
print("V274_ALTERNATE_SOURCES",json.dumps({"recovered":sum(r["status"]=="SOURCE_SAVED" for r,_ in received)}))
