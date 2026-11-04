#!/usr/bin/env python3
"""v220 source-vs-published BBIA audit. Read-only, no publication or swatch invention."""
import argparse, hashlib, io, json
from pathlib import Path
from urllib.request import urlopen, Request
from PIL import Image, ImageDraw, ImageFont
PRODUCTS = [
    ("200", "LAST POWDER LIPSTICK", "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/19/03/13/200/200_magnify_095.jpg"),
    ("206", "LAST AUTO GEL EYELINER", "https://cdn-pro-web-250-115.cdn-nhncommerce.com/sky007com_godomall_com/data/goods/19/03/13/206/206_magnify_078.jpg"),
]
def get(url):
    with urlopen(Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=20) as resp:
        return resp.read(7000000)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def main(root,out):
    out.mkdir(parents=True,exist_ok=True)
    manifest={"checkpoint":"v220","parent":"v219","mode":"READ_ONLY_PHOTO_IDENTITY_COMPARISON","families":[],"new_sales_images":0,"sales_approved":0,"published_assets_changed":False}
    sheet=Image.new("RGB",(1260,1460),"#f5f4f2")
    draw=ImageDraw.Draw(sheet)
    draw.text((25,20),"BBIA v220  |  OFFICIAL VS HISTORIC PUBLIC IMAGES (QA ONLY)",fill="#292929")
    for row,(goods,name,url) in enumerate(PRODUCTS):
        y=65+row*690
        entry={"goodsNo":goods,"product":name,"official_image_url":url,"official_product_page":"https://www.bbia.co.kr/goods/goods_view.php?goodsNo="+goods,"published":[],"hold_reasons":[]}
        draw.text((24,y),goods+" "+name,fill="#222222")
        try:
            data=get(url)
            photo=Image.open(io.BytesIO(data));photo.load();entry["official_download"]="PASS"
            entry["official_dimensions"]=[photo.width,photo.height]
            entry["official_sha256"]=sha(data)
            rgb=photo.convert("RGB");rgb.thumbnail((310,340))
            sheet.paste(rgb,(24,y+34))
            draw.text((24,y+390),"OFFICIAL GENERIC HERO",fill="#333333")
        except Exception as exc:
            entry["official_download"]="HOLD"
            entry["official_error"]=str(exc)[:160]
        files=sorted((root/"public"/"images"/goods).glob("*.jpg"))
        for i,p in enumerate(files[:6]):
            blob=p.read_bytes()
            im=Image.open(io.BytesIO(blob));im.load()
            record={"name":p.name,"bytes":len(blob),"dimensions":[im.width,im.height],"sha256":sha(blob)}
            entry["published"].append(record)
            if i < 6:
                small=im.convert("RGB");small.thumbnail((260,275))
                x=355+(i%3)*295
                yy=y+35+(i//3)*315
                sheet.paste(small,(x,yy))
                draw.text((x,yy+278),p.name,fill="#444444")
        entry["published_count"]=len(files)
        if goods=="200":
            entry["hold_reasons"].append("No released product image; v213 candidates only. Official hero cannot verify individual shades.")
        if goods=="206":
            entry["hold_reasons"].append("Generic official hero does not resolve 21 shade naming collision; published images retained unchanged.")
        entry["release_gate"]="QA_PENDING_OPTION_SPECIFIC_PROOF"
        manifest["families"].append(entry)
    sheet.save(out/"BBIA_v220_OFFICIAL_VS_PUBLIC_CONTACT.jpg",quality=90)
    (out/"BBIA_v220_SOURCE_PUBLISHED_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V220_COMPLETE",json.dumps([{"goodsNo":x["goodsNo"],"official":x.get("official_download"),"size":x.get("official_dimensions"),"published":x["published_count"]} for x in manifest["families"]]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--out",default="/tmp/bbia-v220")
    x=p.parse_args();main(Path(x.root),Path(x.out))
