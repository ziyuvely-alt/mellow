#!/usr/bin/env python3
"""BBIA 225 inspect actual existing option photography; never edit published assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import argparse,hashlib,json
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    frames=["04.jpg","06.jpg"]
    sheet=Image.new("RGB",(2240,2330),"#f2f2f2")
    d=ImageDraw.Draw(sheet)
    d.text((24,12),"BBIA 206 04 & 06 | published originals | OPTION PROOF QA ONLY",fill="black")
    entries=[]
    for j,f in enumerate(frames):
        p=Path("public/images/206")/f
        data=p.read_bytes()
        im=Image.open(p).convert("RGB")
        y=65+j*1125
        sheet.paste(im,(15,y))
        d.text((25,y+1084),"ORIGINAL "+f,fill="black")
        # 4 nearest-neighbor enlarged crops, preserving text edges for human inspection
        for i,(x0,y0,x1,y1) in enumerate([(0,0,540,540),(540,0,1080,540),(0,540,540,1080),(540,540,1080,1080)]):
            cr=im.crop((x0,y0,x1,y1))
            sheet.paste(cr,(1130+(i%2)*550,y+(i//2)*540))
        entries.append(dict(goodsNo="206",frame=f,dimensions=list(im.size),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),finding="Visual review pending, option-21 label crosscheck required",published_original_modified=False))
    sheet.save(out/"BBIA_v225_206_FRAME_04_06_FULL_AND_QUADRANTS.jpg",quality=93,subsampling=0)
    (out/"QA_MANIFEST_v225.json").write_text(json.dumps(dict(checkpoint="v225",status="INSPECTION_ONLY",images=entries,approved=0,originals_unchanged=True),indent=2))
    print("V225_INSPECTED",json.dumps([{"frame":x["frame"],"size":x["dimensions"],"bytes":x["bytes"]} for x in entries]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
