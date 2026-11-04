#!/usr/bin/env python3
"""BBIA v245: 3 new families in one real-photo batch. Preserve all older artifacts."""
import argparse, concurrent.futures, hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
TARGETS=[
 ("1000000151","LAST EYE PALETTE",1,(0,0,1000,920),"PALETTE DETAIL"),
 ("1000000125","EAU STAY CONCEALER",0,(0,2480,1000,3780),"CONCEALER PACKAGING DETAIL"),
 ("207","NEVER DIE BRUSH EYELINER",0,(0,550,1000,1710),"PEN DETAIL")
]
def font(size,bold=False):
    name="DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+name,size)
def fetch(args):
    sku,title,index,rect,role=args
    master={str(a["product_id"]):a for a in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
    url=master[sku]["detail_references"][index]
    item={"goodsNo":sku,"product":title,"source_url":url,"source_rect":list(rect),"role":role}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as r: data=r.read(12_000_000)
        img=Image.open(io.BytesIO(data)).convert("RGB")
        return item,img,hashlib.sha256(data).hexdigest()
    except Exception as e:
        item["status"]="HOLD_FETCH_FAILED";item["error"]=str(e)[:180];return item,None,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e: results=list(e.map(fetch,TARGETS))
    board=Image.new("RGB",(1620,620),"#f5f5f5");d=ImageDraw.Draw(board)
    d.text((12,10),"BBIA v245 3 DISTINCT SOURCE PHOTO CANDIDATES | QA ONLY",fill="#222222")
    rows=[]
    for i,(r,source,digest) in enumerate(results):
        if source is None:rows.append(r);continue
        x0,y0,x1,y1=r["source_rect"]
        actual=(min(x0,source.width),min(y0,source.height),min(x1,source.width),min(y1,source.height))
        crop=source.crop(actual)
        crop.thumbnail((850,760),Image.Resampling.LANCZOS)
        img=Image.new("RGB",(1080,1080),"#faf9f8");draw=ImageDraw.Draw(img)
        draw.text((65,47),"BBIA",font=font(49,True),fill="#322b2b")
        draw.text((65,120),r["product"],font=font(29,True),fill="#4c4140")
        draw.line((65,180,1015,180),fill="#d8c9c8",width=2)
        img.paste(crop,((1080-crop.width)//2,202+(760-crop.height)//2))
        draw.text((65,995),"OFFICIAL DETAIL PHOTO  |  QA ONLY",font=font(22),fill="#665b58")
        filename=f"BBIA_{r['goodsNo']}_NEW_DETAIL_v245_QA_PENDING.jpg"
        path=out/filename;img.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
        if path.stat().st_size>=2000000: raise ValueError("JPG_LIMIT")
        r.update(status="NEW_DETAIL_PHOTO_QA_PENDING",source_dimensions=list(source.size),source_sha256=digest,
                 new_file=filename,new_bytes=path.stat().st_size,new_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        thumb=img.copy();thumb.thumbnail((510,510),Image.Resampling.LANCZOS);board.paste(thumb,(i*540,70));rows.append(r)
    board.save(out/"BBIA_v245_THREE_PRODUCT_CONTACT.jpg",quality=90)
    manifest={"checkpoint":"v245","parent":"v244","new_jpg_count":sum(r.get("status")=="NEW_DETAIL_PHOTO_QA_PENDING" for r in rows),
              "records":rows,"status":"QA_PENDING_NOT_APPROVED","old_assets_modified":False,"public_55_urls_changed":False}
    (out/"BBIA_v245_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("V245_RESULT",json.dumps({"created":manifest["new_jpg_count"],"items":[[r["goodsNo"],r["status"]] for r in rows]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
