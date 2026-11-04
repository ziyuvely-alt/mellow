#!/usr/bin/env python3
"""v254: 4 untouched families / 12 live source photographs, parallel non-destructive QA only."""
import concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
IDS=["238","234","173","228"]
OUT=Path("/tmp/bbia-v254");OUT.mkdir(parents=True,exist_ok=True)
m={str(v["product_id"]):v for v in json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf8"))["families"]}
tasks=[(sku,i,url) for sku in IDS for i,url in enumerate(m[sku]["detail_references"][:3])]
def load(job):
    sku,i,url=job
    result={"goodsNo":sku,"detail_index":i,"source_url":url}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as r: blob=r.read(12000000)
        im=Image.open(io.BytesIO(blob));im.load()
        result.update(status="OK",dimensions=list(im.size),source_sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob))
        return result,im.convert("RGB")
    except Exception as e:
        result.update(status="HOLD",error=f"{type(e).__name__}: {str(e)[:140]}")
        return result,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e: gathered=list(e.map(load,tasks))
board=Image.new("RGB",(1680,1820),"#f8f7f6");draw=ImageDraw.Draw(board)
draw.text((15,12),"BBIA v254 | 4 NEW FAMILIES, 3 DETAIL SOURCES EACH | VIEW ONLY",fill="#1f1f1f")
for ri,sku in enumerate(IDS):
    y=45+ri*430;draw.text((15,y),sku+" "+m[sku]["family"],fill="#222222")
    entries=[(res,im) for res,im in gathered if res["goodsNo"]==sku]
    for ci,(res,im) in enumerate(entries):
        x=10+ci*555
        if im is None:
            draw.text((x,y+50),"SOURCE BLOCKED",fill="#ac2222");continue
        image=im.copy();image.thumbnail((245,310),Image.Resampling.LANCZOS)
        board.paste(image,(x,y+32))
        # 60% through each tall strip shows actual composition without claiming accurate crop.
        a=min(max(0,int(im.height*.4)),max(0,im.height-700))
        crop=im.crop((0,a,im.width,min(im.height,a+700)))
        crop.thumbnail((245,310),Image.Resampling.LANCZOS)
        board.paste(crop,(x+265,y+32))
        draw.text((x,y+358),f"photo {ci+1} {im.width}x{im.height}",fill="#444444")
board.save(OUT/"BBIA_v254_TWELVE_DETAIL_SOURCES_CONTACT.jpg",quality=90)
manifest={"checkpoint":"v254","parent":"v253","families":IDS,"requested":len(tasks),"download_ok":sum(row["status"]=="OK" for row,_ in gathered),
 "records":[row for row,_ in gathered],"new_jpg":0,"public_modified":False,"sales_approved":0,"next":"Select product-only source bands without Korean copy or invented shades"}
(OUT/"BBIA_v254_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("V254_RESULT",json.dumps({"families":len(IDS),"requested":len(tasks),"downloaded":manifest["download_ok"]}))
