#!/usr/bin/env python3
"""v248 bulk candidate discovery only for untouched next eight product families.
Sources are real master detail references; never mutate original photos or public images.
"""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
IDS=("205","1000000057","173","238","234","1000000074","1000000113","228")
def load(job):
    sku,i,url=job
    entry={"goodsNo":sku,"index":i,"url":url}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as f:raw=f.read(12000000)
        p=Image.open(io.BytesIO(raw));p.load()
        entry.update(status="OK",source_px=[p.width,p.height],bytes=len(raw),source_sha256=hashlib.sha256(raw).hexdigest())
        return entry,p.convert("RGB")
    except Exception as e:
        entry.update(status="HOLD",error=f"{type(e).__name__}: {str(e)[:120]}")
        return entry,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    d=json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf-8"))
    master={str(p["product_id"]):p for p in d["families"]}
    tasks=[(sku,i,u) for sku in IDS for i,u in enumerate(master[sku].get("detail_references",[])[:2])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(load,tasks))
    board=Image.new("RGB",(1520,2010),"#f6f6f6")
    draw=ImageDraw.Draw(board)
    draw.text((12,12),"BBIA v248 | EIGHT UNTOUCHED FAMILY SOURCE PREVIEWS | SOURCE ONLY",fill="#222222")
    for row,sku in enumerate(IDS):
        y=row*245+47
        draw.text((10,y),f"{sku}: {master[sku]['family']}",fill="#222222")
        for i in range(2):
            r,img=results[row*2+i]
            x=i*760+15
            if img is None:
                draw.text((x,y+40),"SOURCE HOLD",fill="#991111");continue
            full=img.copy();full.thumbnail((190,190))
            board.paste(full,(x,y+30))
            # Top and central regions are separate reference views, never modified to imply a different SKU.
            for j,(start,end) in enumerate([(0,min(700,img.height)),(int(img.height*.35),min(img.height,int(img.height*.35)+700))]):
                crop=img.crop((0,start,img.width,end));crop.thumbnail((235,190))
                board.paste(crop,(x+205+j*250,y+30))
            draw.text((x,y+220),f"detail{i+1} {img.width}x{img.height}",fill="#555555")
    board.save(out/"BBIA_v248_EIGHT_FAMILY_SOURCE_CONTACT.jpg",quality=88)
    manifest={"checkpoint":"v248","parent":"v247","reviewed_family_ids":list(IDS),
      "fetched_sources":sum(r["status"]=="OK" for r,img in results),
      "failed_sources":sum(r["status"]!="OK" for r,img in results),
      "sources":[r for r,img in results],
      "new_sales_images":0,"previous_jpg_modified":False,"published_changed":False,
      "decision_gate":"Manual select non-promotional photo details before making new QA JPG."}
    (out/"BBIA_v248_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("V248_BATCH",json.dumps({"families":len(IDS),"sources_ok":manifest["fetched_sources"],"failed":manifest["failed_sources"]}))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",required=True);main(Path(a.parse_args().out))
