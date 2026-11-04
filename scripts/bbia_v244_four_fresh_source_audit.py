#!/usr/bin/env python3
"""v244: 4 fresh families, first two real detail photos each. No past candidate recreation."""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
SKUS=["1000000151","1000000125","207","188"]
def fetch(task):
    sku,idx,url=task; row={"goodsNo":sku,"detail_index":idx,"url":url}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as r: raw=r.read(12_000_000)
        im=Image.open(io.BytesIO(raw));im.load();row.update(status="OK",dimensions=list(im.size),sha256=hashlib.sha256(raw).hexdigest())
        return row,im.convert("RGB")
    except Exception as e:row.update(status="HOLD",error=str(e)[:130]);return row,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    master={str(r["product_id"]):r for r in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
    tasks=[(sku,i,url) for sku in SKUS for i,url in enumerate(master[sku].get("detail_references",[])[:2])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: items=list(pool.map(fetch,tasks))
    board=Image.new("RGB",(1450,2000),"#f8f8f8")
    draw=ImageDraw.Draw(board);draw.text((20,12),"BBIA v244 | NEW FAMILIES DETAIL BAND SOURCE AUDIT | NOT SALE IMAGES",fill="#222222")
    records=[]
    for j,sku in enumerate(SKUS):
        y=45+j*480;draw.text((14,y),sku+" "+master[sku]["family"],fill="#222222")
        for i in range(2):
            row,im=items[j*2+i];records.append(row)
            if im is None:continue
            x=15+i*710; full=im.copy();full.thumbnail((235,350));board.paste(full,(x,y+35))
            # Focus on three consecutive vertically separated source strips.
            height=im.height
            for k in range(3):
                a=round(height*k/3);b=round(height*(k+1)/3)
                crop=im.crop((0,a,im.width,b));crop.thumbnail((135,310))
                board.paste(crop,(x+250+k*150,y+35))
            draw.text((x,y+385),f"DETAIL {i+1}: {im.width} x {im.height}",fill="#333333")
    board.save(out/"BBIA_v244_FOUR_NEW_FAMILY_BANDS.jpg",quality=89)
    report={"checkpoint":"v244","parent":"v243","families":SKUS,"sources_checked":len(items),"downloaded":sum(row["status"]=="OK" for row in records),
       "records":records,"no_old_assets_modified":True,"sale_approved":0}
    (out/"BBIA_v244_SOURCE_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("V244_SOURCES",json.dumps({"requested":len(tasks),"downloaded":report["downloaded"],"families":SKUS}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
