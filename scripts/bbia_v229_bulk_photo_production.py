#!/usr/bin/env python3
"""BBIA v229: non-destructive bulk recovery and source-faithful hero candidates.
No invented shades, no text/photo changes to existing production images.
"""
import argparse, concurrent.futures, hashlib, io, json, re
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO=Path(".")
MASTER=REPO/"evidence/bbia-image-review-input.json"
PUBLIC=REPO/"public/images"
MAX_WORKERS=8
MAX_SOURCE_BYTES=9_000_000
MIN_NATIVE=800
MAX_CANDIDATES=12

def font(size,bold=False):
    path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path,size)

def inspect(rec):
    url=rec.get("official_photo_url")
    item={"goodsNo":str(rec.get("product_id")),"family":rec.get("family"),"source_url":url,
          "official_page":rec.get("official_page"),"status":"NOT_ATTEMPTED"}
    if not url or not url.startswith("https://"):
        item.update(status="NO_OFFICIAL_SOURCE_URL")
        return item,None
    try:
        req=Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urlopen(req,timeout=20) as res:
            data=res.read(MAX_SOURCE_BYTES+1)
        if len(data)>MAX_SOURCE_BYTES:raise ValueError("SOURCE_TOO_LARGE")
        im=Image.open(io.BytesIO(data)); im.load()
        if im.format not in ("JPEG","PNG","WEBP"):raise ValueError("UNKNOWN_IMAGE_FORMAT")
        item.update(status="PHOTO_DOWNLOADED",source_dimensions=[im.width,im.height],source_format=im.format,source_bytes=len(data),source_sha256=hashlib.sha256(data).hexdigest())
        return item,im.convert("RGB")
    except Exception as e:
        item.update(status="FETCH_FAILED_HOLD",error=f"{type(e).__name__}: {str(e)[:180]}")
        return item,None

def produce(out,entry,photo):
    key=entry["goodsNo"]
    canvas=Image.new("RGB",(1080,1080),(250,249,247))
    draw=ImageDraw.Draw(canvas)
    # Product photograph preserved at native resolution, not hallucinated or upsampled.
    photo=photo.copy()
    photo.thumbnail((890,800),Image.Resampling.LANCZOS)
    x=(1080-photo.width)//2
    y=155+(800-photo.height)//2
    canvas.paste(photo,(x,y))
    draw.text((65,37),"BBIA",font=font(49,True),fill=(38,34,36))
    draw.line((65,112,1015,112),fill=(211,199,195),width=2)
    # No misleading SKU shade name. The product name is the page-provided family name, may be Korean:
    # use neutral English "ORIGINAL PRODUCT PHOTOGRAPH" until exact official English family name verified.
    draw.text((65,982),"GENUINE PRODUCT PHOTO  |  SHADE MAY VARY",font=font(26),fill=(61,52,52))
    name=f"BBIA_{key}_OFFICIAL_PHOTO_EN_v229_QA_PENDING.jpg"
    path=out/name
    canvas.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
    with Image.open(path) as check:check.verify()
    entry.update(new_jpg=name,output_bytes=path.stat().st_size,output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 output_dimensions=[1080,1080],status="NEW_QA_CANDIDATE_CREATED",sales_approved=False,
                 limits="Product generic photo only; not shade-specific; visual QA pending")
    if entry["output_bytes"] >=2_000_000:
        path.unlink()
        entry.update(status="OUTPUT_OVER_2MB_HOLD",new_jpg=None)
    return entry

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    raw=json.loads(MASTER.read_text(encoding="utf-8"))["families"]
    published={p.name for p in PUBLIC.iterdir() if p.is_dir()}
    excluded={"200","206","1000000124","1000000122"} # known holds / separate tracks
    eligible=[r for r in raw if str(r["product_id"]) not in published and str(r["product_id"]) not in excluded]
    records=[]
    items=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for r in pool.map(inspect,eligible):
            items.append(r)
    # Differentiate "source secured" from "image generation": only sufficient native resolutions.
    seen_hash=set()
    created=0
    contact=[]
    for entry,im in items:
        if im is None:
            records.append(entry);continue
        if min(im.size)<MIN_NATIVE:
            entry.update(status="LOW_NATIVE_RES_HOLD",minimum_native_px=MIN_NATIVE)
        elif entry["source_sha256"] in seen_hash:
            entry.update(status="IDENTICAL_SOURCE_HOLD")
        elif created>=MAX_CANDIDATES:
            entry.update(status="SOURCE_READY_QUEUE_NEXT_BATCH")
        else:
            entry=produce(out,entry,im)
            if entry["status"]=="NEW_QA_CANDIDATE_CREATED":
                created+=1
                thumb=Image.open(out/entry["new_jpg"]).convert("RGB")
                thumb.thumbnail((340,340))
                contact.append((entry["goodsNo"],thumb))
        seen_hash.add(entry["source_sha256"])
        records.append(entry)
    if contact:
        board=Image.new("RGB",(1080,((len(contact)+2)//3)*385+55),"#f4f4f4")
        d=ImageDraw.Draw(board)
        d.text((15,12),"BBIA v229 NEW CANDIDATES | photo-source QA pending",fill="black")
        for idx,(key,img) in enumerate(contact):
            x=10+(idx%3)*360;y=50+(idx//3)*385
            board.paste(img,(x,y))
            d.text((x,y+345),key,fill="black")
        board.save(out/"BBIA_v229_BATCH_CONTACT.jpg",quality=88)
    summary={
        "checkpoint":"v229","master_families":len(raw),"preexisting_published_families":len(published),
        "eligible_unpublished_master_families":len(eligible),"source_success":sum("source_dimensions" in x for x in records),
        "new_en_photo_candidate_jpg":created,
        "source_low_resolution_holds":sum(x["status"]=="LOW_NATIVE_RES_HOLD" for x in records),
        "source_fetch_errors":sum(x["status"]=="FETCH_FAILED_HOLD" for x in records),
        "new_sales_approved":0,"existing_published_changed":False,"verified_55_urls_changed":False,
        "records":records
    }
    (out/"BBIA_v229_BATCH_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V229_BATCH_RESULT",json.dumps({k:v for k,v in summary.items() if k!="records"},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    main(Path(p.parse_args().out))
