#!/usr/bin/env python3
"""BBIA v227: refine only frame04 caption backgrounds from v226 artifact; keep originals."""
from pathlib import Path
import argparse, hashlib, json
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

def main(src,out):
    out.mkdir(parents=True,exist_ok=True)
    old=next(src.rglob("BBIA_206_04_SHADE_LABELS_v226_QA_PENDING.jpg"))
    image=cv2.imread(str(old))
    mask=np.zeros(image.shape[:2],dtype=np.uint8)
    coords=[(91,794,321,840),(558,794,823,843)]
    for x0,y0,x1,y1 in coords: cv2.rectangle(mask,(x0,y0),(x1,y1),255,-1)
    repaired=cv2.inpaint(image,mask,20,cv2.INPAINT_TELEA)
    im=Image.fromarray(cv2.cvtColor(repaired,cv2.COLOR_BGR2RGB))
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
    draw.text((99,803),"20 Mauve Burn",font=font,fill=(56,51,50))
    draw.text((571,803),"27 Mocha Burn",font=font,fill=(56,51,50))
    output=out/"BBIA_206_04_SHADE_LABELS_v227_QA_PENDING.jpg"
    im.save(output,"JPEG",quality=94,subsampling=0,optimize=True)
    with Image.open(output) as verify: verify.verify()
    if output.stat().st_size>=2_000_000:raise ValueError("JPG_LIMIT")
    contact=Image.new("RGB",(2160,1145),"#f0f0f0")
    contact.paste(Image.open(old).convert("RGB"),(0,50))
    contact.paste(im,(1080,50))
    labels=ImageDraw.Draw(contact)
    labels.text((18,14),"v226 original candidate",fill="#222222")
    labels.text((1100,14),"v227 two-region texture reconstruction",fill="#222222")
    contact.save(out/"BBIA_v227_BEFORE_AFTER.jpg",quality=90)
    manifest={
        "checkpoint":"v227","goodsNo":"206","frame":"04","parent":"v226",
        "source_artifact_id":13321142179,"input_sha256":hashlib.sha256(old.read_bytes()).hexdigest(),
        "output_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "output_bytes":output.stat().st_size,"dimensions":[1080,1080],
        "modified_regions":coords,
        "corrected_options":{"20":"Mauve Burn","27":"Mocha Burn"},
        "source_photographs_not_intentionally_modified":True,
        "existing_public_assets_modified":False,
        "frame06_v226_reused_not_recreated":True,
        "sales_approved":False,
        "status":"QA_PENDING_FINAL_VISUAL"
    }
    (out/"QA_MANIFEST_v227.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print("V227_CREATED",json.dumps({"size":output.stat().st_size,"sha":manifest["output_sha256"]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--src",required=True);p.add_argument("--out",required=True)
    v=p.parse_args();main(Path(v.src),Path(v.out))
