#!/usr/bin/env python3
"""BBIA v217: one refill-only editorial candidate from actual official image, no publishing."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageFilter

URL = "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/24/02/06/1000000124/1000000124_magnify_061.jpg"
GOODS = "1000000124"

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def run(folder):
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version":"v217", "goodsNo": GOODS, "name":"BBIA Eau Glow Cushion Refill",
        "source_url": URL, "official_listing":"https://www.bbia.co.kr/goods/goods_view.php?goodsNo=1000000124",
        "source_kind":"CURRENT_OFFICIAL_GENERIC_PRIMARY_IMAGE",
        "status":"QA_PENDING_NOT_SALES_APPROVED", "existing_images_modified":False,
        "verified_55_urls_modified":False, "claims":"Refill Only; No Compact Case Included",
        "notes":["Single frame only; no invented swatch or 5-role count","Authenticity established by official listing URL; current source photo does not authenticate each shade","Uses only original photographic pixels without generative replacement"]
    }
    try:
        req=Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; ProductQA/1.0)"})
        with urlopen(req,timeout=25) as resp:
            data=resp.read(8_000_000)
            manifest["source_http_status"]=resp.status
        photo=Image.open(io.BytesIO(data)).convert("RGB")
        manifest["source_size"]=list(photo.size)
        manifest["source_sha256"]=hashlib.sha256(data).hexdigest()
        if min(photo.size)<400:
            raise ValueError("SOURCE_TOO_SMALL_FOR_NONUPSCALED_EDITORIAL")
        # Use photo at native resolution: do not upscale a 500px source and invent detail.
        canvas=Image.new("RGB",(1080,1080),(250,249,249))
        draw=ImageDraw.Draw(canvas)
        draw.text((88,88),"BBIA",font=font(46,True),fill=(40,40,43))
        draw.text((88,164),"EAU GLOW CUSHION",font=font(49,True),fill=(40,40,43))
        draw.text((88,229),"REFILL ONLY",font=font(45,True),fill=(124,86,74))
        draw.line((88,300,992,300),fill=(207,195,194),width=3)
        # Feather only the rectangular boundary to avoid a visible square picture frame.
        # Do not remove or retouch any pixels inside the official product photo.
        shown=photo.copy()
        shown.thumbnail((620,620),Image.Resampling.LANCZOS)
        x=(1080-shown.width)//2
        y=340
        mask=Image.new("L",shown.size,0)
        edge=45
        m=ImageDraw.Draw(mask)
        m.rounded_rectangle((edge,edge,shown.width-edge,shown.height-edge),radius=48,fill=255)
        mask=mask.filter(ImageFilter.GaussianBlur(20))
        canvas.paste(shown,(x,y),mask)
        draw=ImageDraw.Draw(canvas)
        draw.line((88,918,992,918),fill=(207,195,194),width=2)
        draw.text((88,948),"REFILL INSERT  |  COMPACT CASE NOT INCLUDED",font=font(26),fill=(75,68,67))
        out=folder/"BBIA_1000000124_REFILL_ONLY_EN_v217_QA_PENDING.jpg"
        canvas.save(out,"JPEG",quality=91,optimize=True,subsampling=0)
        with Image.open(out) as check:
            check.verify()
        manifest["output"]=out.name
        manifest["output_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
        manifest["output_size"]=[1080,1080]
        manifest["output_bytes"]=out.stat().st_size
        manifest["technical_pass"]=out.stat().st_size<2_000_000
        if not manifest["technical_pass"]:
            raise ValueError("OUTPUT_TOO_LARGE")
        print("CREATED",out.name,"bytes",out.stat().st_size,"source",photo.size)
    except Exception as e:
        manifest["status"]="SOURCE_BLOCKED_OR_IMAGE_REJECTED"
        manifest["error"]=f"{type(e).__name__}: {e}"
        print("HOLD",manifest["error"])
    finally:
        (folder/"QA_MANIFEST_v217.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="/tmp/bbia-v217")
    a=p.parse_args()
    run(Path(a.out))
