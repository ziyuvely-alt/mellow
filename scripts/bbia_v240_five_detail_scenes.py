#!/usr/bin/env python3
"""v240 5 distinct authentic product-photo detail candidates, all isolated, non-published.
Use source strip bands manually inspected at v239; do not use unrelated testimonial/model/shade photos.
"""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
TARGETS=[
("1000000056","NEVER DIE MASCARA SLIM",(0,815,1000,1550),"APPLICATOR DETAIL"),
("1000000178","EAU MATTE CUSHION",(0,1580,1000,2180),"COMPACT DETAIL"),
("1000000184","EAU POWDER PACT",(0,2690,1000,3715),"COMPACT & POWDER"),
("1000000223","LIP OIL ESSENCE",(0,2280,1000,3040),"PRODUCT LINEUP"),
("1000000239","LUCKY SHINE TINT",(0,2290,1000,2855),"BOTTLE DETAIL")
]
def font(n,bold=False):
    name="DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+name,n)
def download(t):
    sku,label,rect,role=t
    with urlopen(Request(masters[sku]["detail_references"][0],headers={"User-Agent":"Mozilla/5.0"}),timeout=24) as res:
        blob=res.read(12000000)
    im=Image.open(io.BytesIO(blob));im.load()
    return t,im.convert("RGB"),hashlib.sha256(blob).hexdigest()
masters={}
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    global masters
    masters={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
        results=list(e.map(download,TARGETS))
    board=Image.new("RGB",(1800,1200),"#f5f5f5")
    d=ImageDraw.Draw(board)
    d.text((10,15),"BBIA v240 - FIVE DISTINCT PHOTO DETAIL QA CANDIDATES",fill="#222222")
    manifest=[]
    for i,(task,source,sh) in enumerate(results):
        sku,label,rect,role=task
        x0,y0,x1,y1=rect
        crop=source.crop((x0,min(source.height,y0),min(source.width,x1),min(source.height,y1)))
        if crop.width<400 or crop.height<350:raise RuntimeError("SOURCE_CROP_TOO_SMALL "+sku)
        crop.thumbnail((925,765),Image.Resampling.LANCZOS)
        output=Image.new("RGB",(1080,1080),(250,249,247))
        draw=ImageDraw.Draw(output)
        draw.text((67,49),"BBIA",font=font(49,True),fill=(38,31,33))
        draw.text((67,121),label,font=font(31,True),fill=(53,44,46))
        draw.line((68,185,1010,185),fill=(211,199,194),width=2)
        output.paste(crop,((1080-crop.width)//2,211+(765-crop.height)//2))
        draw.text((67,993),role+"  |  PHOTO REFERENCE",font=font(25),fill=(91,77,75))
        fn=f"BBIA_{sku}_DETAIL_v240_QA_PENDING.jpg"
        path=out/fn
        output.save(path,"JPEG",quality=90,optimize=True,subsampling=0)
        size=path.stat().st_size
        if size>=2000000:raise RuntimeError("JPG_LIMIT "+sku)
        manifest.append({"goodsNo":sku,"label":label,"role":role,"source_url":masters[sku]["detail_references"][0],
             "source_sha256":sh,"source_dimensions":list(source.size),"source_crop":list(rect),
             "file":fn,"file_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
             "bytes":size,"dimensions":[1080,1080],"status":"QA_PENDING_VISUAL_PHOTO_IDENTITY_AND_TEXT"})
        thumb=output.copy();thumb.thumbnail((575,540),Image.Resampling.LANCZOS)
        bx=(i%3)*600+15;by=(i//3)*590+45
        board.paste(thumb,(bx,by))
        d.text((bx,by+544),sku,fill="#333333")
    board.save(out/"BBIA_v240_FIVE_DETAIL_CONTACT.jpg",quality=90)
    (out/"BBIA_v240_MANIFEST.json").write_text(json.dumps({"checkpoint":"v240","parent":"v239",
         "new_jpg_count":len(manifest),"new_sales_approved":0,"previous_assets_modified":False,
         "evidence":manifest},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V240_CREATED",json.dumps({"count":len(manifest),"files":[x["file"] for x in manifest]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
