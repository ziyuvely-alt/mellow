#!/usr/bin/env python3
"""v249: create 3 genuinely new photo-role JPG drafts for goodsNos outside v247 current candidate set.
Uses native verified v248 manufacturer detail links, never changes published imagery.
"""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
TASKS=[
("1000000057","LAST CONTOUR PEN EYELINER",1,(0,0,1000,1000),"EYE APPLICATION"),
("1000000074","READY TO WEAR WATER LIPSTICK",1,(0,0,1000,1100),"ORIGINAL PRODUCT LINEUP"),
("1000000113","L'EAU TINT",1,(0,0,1000,1100),"ORIGINAL PRODUCT LINEUP")
]
def font(size,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),size)
def fetch(job,master):
    sku,name,idx,rect,role=job
    url=master[sku]["detail_references"][idx]
    info={"goodsNo":sku,"label":name,"detail_index":idx,"source_url":url,"role":role,"cropped_region":list(rect)}
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as r:data=r.read(12000000)
        photo=Image.open(io.BytesIO(data)).convert("RGB")
        info.update(status="SOURCE_OK",source_dimensions=list(photo.size),source_sha256=hashlib.sha256(data).hexdigest())
        return info,photo.crop((rect[0],rect[1],min(rect[2],photo.width),min(rect[3],photo.height)))
    except Exception as e:
        info.update(status="SOURCE_HOLD",error=str(e)[:150]);return info,None
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    master={str(r["product_id"]):r for r in json.loads(Path("evidence/bbia-image-review-input.json").read_text(encoding="utf-8"))["families"]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:
        results=list(p.map(lambda x:fetch(x,master),TASKS))
    board=Image.new("RGB",(1620,630),"#f5f4f3")
    bd=ImageDraw.Draw(board)
    bd.text((12,12),"BBIA v249 | 3 NEW SOURCE-FAITHFUL DETAIL DRAFTS | NOT SALES APPROVED",fill="#222222")
    records=[]
    for idx,(info,crop) in enumerate(results):
        if crop is None:records.append(info);continue
        crop.thumbnail((910,780),Image.Resampling.LANCZOS)
        frame=Image.new("RGB",(1080,1080),(250,249,248))
        d=ImageDraw.Draw(frame)
        d.text((66,50),"BBIA",font=font(49,True),fill=(40,34,37))
        d.text((66,125),info["label"],font=font(29,True),fill=(59,50,51))
        d.line((66,183,1015,183),fill=(210,201,196),width=2)
        frame.paste(crop,((1080-crop.width)//2,200+(785-crop.height)//2))
        d.text((66,1000),info["role"]+"  |  SHADE MAY VARY",font=font(23),fill=(98,88,84))
        name="BBIA_"+info["goodsNo"]+"_SOURCE_DETAIL_v249_QA_PENDING.jpg"
        path=out/name
        frame.save(path,"JPEG",quality=92,optimize=True,subsampling=0)
        with Image.open(path) as check:check.verify()
        assert path.stat().st_size<2_000_000
        info.update(status="CANDIDATE_CREATED_VISUAL_QA_PENDING",output_file=name,output_bytes=path.stat().st_size,
                    output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=[1080,1080])
        thumb=frame.copy();thumb.thumbnail((515,520),Image.Resampling.LANCZOS)
        board.paste(thumb,(idx*540+10,56))
        records.append(info)
    board.save(out/"BBIA_v249_THREE_NEW_FAMILIES_CONTACT.jpg",quality=88)
    result={"checkpoint":"v249","parent":"v248","new_jpg":sum(r["status"]=="CANDIDATE_CREATED_VISUAL_QA_PENDING" for r in records),
      "records":records,"approved_sales_jpg":0,"verified_55_urls_modified":False,"existing_jpg_modified":False,
      "warning":"Manufacturer strip crop may contain original promo language or shade names; final photo and variant QA needed"}
    (out/"BBIA_v249_MANIFEST.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("V249_CREATED",json.dumps({"new_jpg":result["new_jpg"],"ids":[x["goodsNo"] for x in records]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
