#!/usr/bin/env python3
"""v239 inspect exactly five unused detail source strips, preview vertical bands. No sale image creation."""
import argparse,concurrent.futures,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
IDS=("1000000056","1000000178","1000000184","1000000223","1000000239")
def load(item):
    id,ref=item
    data=urlopen(Request(ref,headers={"User-Agent":"Mozilla/5.0"}),timeout=22).read(12000000)
    im=Image.open(io.BytesIO(data)).convert("RGB")
    return id,im,hashlib.sha256(data).hexdigest()
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    data=json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]
    f={str(x["product_id"]):x for x in data}
    req=[(id,f[id]["detail_references"][0]) for id in IDS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e: results=list(e.map(load,req))
    tilew=280;tileh=235
    board=Image.new("RGB",(5*tilew,6*tileh+95),"#f5f5f5")
    d=ImageDraw.Draw(board)
    d.text((15,12),"BBIA v239 | SOURCE BAND INSPECTION, NO FINAL JPGS",fill="#222222")
    records=[]
    for c,(id,im,hash) in enumerate(results):
        d.text((c*tilew+12,44),id,fill="#222222")
        segment_h=im.height/6
        for i in range(6):
            y0=round(i*segment_h); y1=round((i+1)*segment_h)
            seg=im.crop((0,y0,im.width,y1))
            seg.thumbnail((260,190),Image.Resampling.LANCZOS)
            x=c*tilew+(tilew-seg.width)//2
            y=90+i*tileh
            board.paste(seg,(x,y))
            d.text((c*tilew+12,y+192),f"band {i+1}: y{y0}-{y1}",fill="#555555")
        records.append({"goodsNo":id,"url":f[id]["detail_references"][0],"source_dimensions":list(im.size),"source_sha256":hash,
                        "bands":[[round(i*segment_h),round((i+1)*segment_h)] for i in range(6)]})
    board.save(out/"BBIA_v239_FIVE_FAMILY_SIX_BANDS.jpg",quality=90)
    (out/"BBIA_v239_SOURCE_BANDS.json").write_text(json.dumps({"checkpoint":"v239","records":records,"new_sale_jpg":0,"old_images_changed":False},indent=2))
    print("V239_FIVE_SOURCES",json.dumps([{"goodsNo":x["goodsNo"],"dimensions":x["source_dimensions"]} for x in records]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
