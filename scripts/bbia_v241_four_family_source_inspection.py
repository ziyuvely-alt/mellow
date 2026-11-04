#!/usr/bin/env python3
"""BBIA v241: inspect unused official detail photos in a batch. No image publishing or re-render of completed sets."""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
SKUS=["1000000135","1000000136","1000000216","1000000244"]
def get(task):
    sku,idx,url=task
    r={"sku":sku,"detail_index":idx,"source_url":url}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as resp: blob=resp.read(12000000)
        im=Image.open(io.BytesIO(blob));im.load()
        r.update(status="OK",size=[im.width,im.height],bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
        return r,im.convert("RGB")
    except Exception as ex:
        r.update(status="HOLD_FETCH",error=str(ex)[:130]);return r,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    data=json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf-8"))["families"]
    families={str(x["product_id"]):x for x in data}
    tasks=[(sku,i,url) for sku in SKUS for i,url in enumerate(families[sku]["detail_references"][:3])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: fetched=list(pool.map(get,tasks))
    board=Image.new("RGB",(1740,4*470+70),"#f7f7f7")
    d=ImageDraw.Draw(board)
    d.text((18,14),"BBIA v241 | FOUR FAMILY x THREE SOURCE DETAILS | NO SALE APPROVAL",fill="#222222")
    rows=[]
    for row,sku in enumerate(SKUS):
        d.text((18,52+row*470),sku+"  "+families[sku]["family"],fill="#232323")
        for col in range(3):
            x=15+col*580;y=83+row*470
            r,im=fetched[row*3+col];rows.append(r)
            if im is None:
                d.text((x,y),"SOURCE HOLD",fill="red");continue
            full=im.copy();full.thumbnail((255,320))
            board.paste(full,(x,y))
            # Show unmodified top 650px of source separately for informed, faithful crop choices
            crop=im.crop((0,0,im.width,min(650,im.height)))
            crop.thumbnail((290,315))
            board.paste(crop,(x+275,y))
            d.text((x,y+332),f"detail {col+1}: {im.width}x{im.height}",fill="#555555")
    board.save(out/"BBIA_v241_FOUR_FAMILY_12_SOURCES_CONTACT.jpg",quality=88)
    summary={"checkpoint":"v241","parent":"v240","families":4,"source_requested":len(tasks),
      "downloaded":sum(r["status"]=="OK" for r in rows),"holds":sum(r["status"]!="OK" for r in rows),
      "records":rows,"new_jpg_created":0,"old_assets_modified":False,"sale_approved":0,
      "note":"Wide preview is a crop selection aid only; images may contain Korean or swatches without independent option verification."}
    (out/"BBIA_v241_SOURCE_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V241_RESULT",json.dumps({"source_count":len(tasks),"downloaded":summary["downloaded"],"holds":summary["holds"],"families":4}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
