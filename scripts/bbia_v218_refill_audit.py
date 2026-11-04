#!/usr/bin/env python3
"""v218: inspect existing v217 JPG; no edit to candidate or approved public images."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps

def luminance(rgb):
    return sum(rgb[:3])/3

def block_stats(im, box):
    patch=im.crop(box).convert("RGB")
    pixels=list(patch.getdata())
    avg=[round(sum(c[i] for c in pixels)/len(pixels),2) for i in range(3)]
    return {"box":list(box),"rgb_mean":avg}

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    source=Path(a.input);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    files=list(source.rglob("*.jpg"))
    report={"checkpoint":"v218","upstream":"v217 run 41824071042, artifact 13318516246","mode":"READ_ONLY_INSPECT_AND_QA_PREVIEW","jpg_count":len(files),"sales_approved":False,"source_assets_modified":False,"checks":[]}
    for f in files:
        im=Image.open(f);im.load();im=im.convert("RGB")
        width,height=im.size;size=f.stat().st_size
        chunks={
            "top_brand":(75,70,480,155),
            "product_heading":(75,145,1020,290),
            "photo_center":(290,345,790,865),
            "photo_outer_left":(250,420,345,760),
            "photo_outer_right":(735,420,830,760),
            "bottom_caption":(75,930,1025,1015),
            "paper_background":(12,340,110,850),
        }
        stats={key:block_stats(im,box) for key,box in chunks.items()}
        # Border probe: large abrupt difference between image edge and paper is possible square-frame artifact.
        scan_y=[460,580,720]; scan_x=[285,320,345,735,760,795]
        probes=[{"x":x,"y":y,"rgb":list(im.getpixel((x,y)))} for y in scan_y for x in scan_x]
        report["checks"].append({"file":f.name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"size":[width,height],"bytes":size,"technical_pass":(width,height)==(1080,1080) and size<2000000,"stats":stats,"boundary_color_samples":probes,"finding":"Pixel sample diagnostics only; human design approval remains pending. No declaration of cutout transparency."})
        # 2x zoom-free overview and region crops to facilitate human visual QA
        canvas=Image.new("RGB",(1620,1260),"#eeeeee")
        thumb=im.copy();thumb.thumbnail((1030,1030))
        canvas.paste(thumb,(20,20))
        detail=im.crop((260,330,830,895)).resize((520,520))
        canvas.paste(detail,(1080,20))
        d=ImageDraw.Draw(canvas)
        d.text((20,1090),"v218 DIAGNOSTIC: left = exact v217 JPG; right = photo center crop",fill="black")
        d.text((20,1135),"QA_PENDING. No sales/publishing approval; not a newly generated selling image.",fill="black")
        canvas.save(out/"BBIA_v218_REFILL_VISUAL_QA_CONTACT.jpg",quality=88)
    (out/"BBIA_v218_VISUAL_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V218_AUDIT",json.dumps({"jpg_count":len(files),"files":[x["file"] for x in report["checks"]],"technical_pass":all(x["technical_pass"] for x in report["checks"])}))
    if not files:raise SystemExit("NO_PREVIOUS_JPG_IN_ARCHIVE")

if __name__=="__main__":main()
