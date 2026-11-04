#!/usr/bin/env python3
"""v235 read-only 13-family second creative-role official source triage. Does not recreate any v234 JPG."""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw
SKUS=("1000000056","1000000135","1000000136","1000000178","1000000184",
"1000000216","1000000221","1000000223","1000000227","1000000239",
"1000000244","1000000247","172")
MASTER=Path("evidence/bbia-image-review-input.json")
def fetch(job):
    sku,index,url=job
    d={"goodsNo":sku,"detail_index":index,"url":url,"status":"NOT_CHECKED"}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as r:
            b=r.read(12_000_000)
        im=Image.open(io.BytesIO(b));im.load()
        d.update(status="SOURCE_VERIFIED",dimensions=[im.width,im.height],format=im.format,
                 source_sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
        return d,im.convert("RGB")
    except Exception as e:
        d.update(status="FETCH_HOLD",reason=f"{type(e).__name__}: {str(e)[:130]}")
        return d,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    raw=json.loads(MASTER.read_text(encoding="utf-8"))["families"]
    fam={str(r["product_id"]):r for r in raw}
    jobs=[]
    for sku in SKUS:
        for i,url in enumerate(fam.get(sku,{}).get("detail_references",[])[:2]):
            jobs.append((sku,i,url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
        result=list(e.map(fetch,jobs))
    rows=[d for d,im in result]
    board=Image.new("RGB",(1240,len(SKUS)*214+80),"#f7f7f7")
    draw=ImageDraw.Draw(board)
    draw.text((15,14),"BBIA v235 / 13 FAMILIES x 2 DETAIL REFERENCES / READ-ONLY",fill="#222222")
    for j,sku in enumerate(SKUS):
        y=62+j*214
        draw.text((12,y+4),sku,fill="#222222")
        for i in range(2):
            r=next(((d,im) for d,im in result if d["goodsNo"]==sku and d["detail_index"]==i),None)
            if r is None:continue
            d,im=r
            x=250+i*455
            if im is None:
                draw.text((x,y+35),"SOURCE HOLD",fill="red")
                continue
            img=im.copy()
            # For tall campaign strips, display full source in a constrained panel AND an unaltered top crop.
            img.thumbnail((200,175),Image.Resampling.LANCZOS)
            board.paste(img,(x,y))
            crop=im.crop((0,0,min(im.width,700),min(im.height,700)))
            crop.thumbnail((165,165),Image.Resampling.LANCZOS)
            board.paste(crop,(x+215,y))
            draw.text((x,y+182),f"{d['dimensions'][0]}x{d['dimensions'][1]}  source {i+1}",fill="#333333")
    board.save(out/"BBIA_v235_THIRTEEN_FAMILY_TWO_SOURCE_CONTACT.jpg",quality=88)
    summary={"checkpoint":"v235","previous":"v234","families":len(SKUS),"detail_sources_requested":len(jobs),
       "downloads_ok":sum(x["status"]=="SOURCE_VERIFIED" for x in rows),
       "downloads_hold":sum(x["status"]!="SOURCE_VERIFIED" for x in rows),
       "candidate_identity_hold":"Detail strips are not automatically product-accurate, cannot auto-mint new second-role JPGs",
       "source_rows":rows,"reused_13_v234_jpg":True,"new_sales_jpg":0,"approved":0,
       "current_public_modified":False}
    (out/"BBIA_v235_SECOND_ROLE_SOURCE_AUDIT.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("V235_BATCH",json.dumps({"families":len(SKUS),"sources_requested":len(jobs),"verified":summary["downloads_ok"],
                               "failed":summary["downloads_hold"]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    main(Path(p.parse_args().out))
