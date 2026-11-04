#!/usr/bin/env python3
"""Read-only enlarge and inspect the existing exact published 206/03.jpg."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    src=Path("public/images/206/03.jpg")
    im=Image.open(src).convert("RGB")
    w,h=im.size
    canvas=Image.new("RGB",(2220,1630),"#eeeeee")
    canvas.paste(im,(25,60))
    crops=[
        (0,0,540,540),
        (540,0,1080,540),
        (0,540,540,1080),
        (540,540,1080,1080),
    ]
    for i,b in enumerate(crops):
        section=im.crop(b).resize((540,540),Image.Resampling.NEAREST)
        x=1130+(i%2)*540;y=60+(i//2)*590
        canvas.paste(section,(x,y))
        ImageDraw.Draw(canvas).text((x,y+543),f"QUADRANT {i+1}: {b}",fill="#222222")
    d=ImageDraw.Draw(canvas)
    d.text((25,25),"206/03.jpg PUBLIC ORIGINAL | unmodified",fill="#222222")
    canvas.save(out/"BBIA_v221_206_03_ORIGINAL_CROP_INSPECTION.jpg",quality=94,subsampling=0)
    result={"checkpoint":"v221","goodsNo":"206","frame":"03.jpg","original_path":str(src),"dimensions":[w,h],"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"diagnostic":"BBIA_v221_206_03_ORIGINAL_CROP_INSPECTION.jpg","preexisting_jpg_edited":False,"sales_approved":False,"next":"Inspect actual quadrant text region and build one targeted new English version if possible, not a duplicate hero"}
    (out/"QA_MANIFEST_v221.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print("V221_READ_ONLY_206_03",json.dumps({"size":[w,h],"bytes":src.stat().st_size,"sha256":result["source_sha256"]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    main(Path(p.parse_args().out))
