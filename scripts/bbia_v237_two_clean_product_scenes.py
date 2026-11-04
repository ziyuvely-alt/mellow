#!/usr/bin/env python3
"""v237: two targeted product-photo-only candidates, discard testimonial; never touch originals."""
import argparse,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
def font(s,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,s)
def main(src,out):
    out.mkdir(parents=True,exist_ok=True)
    master={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
    targets=[
      ("1000000227","NUDY LIP PENCIL",1,(0,1030,1000,2300)),
      ("1000000247","EYE & CHEEK PRIMER BALM",1,(0,960,1000,2170))
    ]
    contact=Image.new("RGB",(2160,1150),"#f4f4f4")
    report={"checkpoint":"v237","parent":"v236","inherited":"v234 13 existing hero candidates immutable",
       "previous_v236":{"mascara_172":"RETAIN_SECOND_ROLE_PENDING_SALE_QA",
                        "1000000221_blush":"HOLD_TESTIMONIAL_COPY_NOT_PRODUCT_PHOTOGRAPH",
                        "1000000227":"KOREAN_EMBEDDED_HOLD_REPLACED_BY_CLEAN_CROP_CANDIDATE",
                        "1000000247":"KOREAN_EMBEDDED_HOLD_REPLACED_BY_CLEAN_CROP_CANDIDATE"},
       "files":[],"approved":0,"published_changed":False}
    for i,(sku,title,index,rect) in enumerate(targets):
        url=master[sku]["detail_references"][index]
        item={"goodsNo":sku,"source_url":url,"source_crop":list(rect)}
        try:
            with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as resp:
                data=resp.read(12000000)
            original=Image.open(io.BytesIO(data)).convert("RGB")
            actual=(0,min(rect[1],original.height),original.width,min(rect[3],original.height))
            crop=original.crop(actual)
            if crop.width<450 or crop.height<500: raise ValueError("too small crop")
            # Preserve authentic pixels in product photo area, avoid top Korean source headlines.
            crop.thumbnail((870,770),Image.Resampling.LANCZOS)
            canvas=Image.new("RGB",(1080,1080),"#faf9f8")
            draw=ImageDraw.Draw(canvas)
            draw.text((70,53),"BBIA",font=font(51,True),fill="#2a2526")
            draw.text((70,129),title,font=font(28,True),fill="#4c4040")
            draw.line((70,187,1010,187),fill="#d8cbc9",width=2)
            canvas.paste(crop,((1080-crop.width)//2,205+(770-crop.height)//2))
            draw.text((70,1007),"PRODUCT PHOTO DETAIL  |  SHADE MAY VARY",font=font(22),fill="#665957")
            name=f"BBIA_{sku}_PHOTO_ONLY_DETAIL_v237_QA_PENDING.jpg"
            path=out/name
            canvas.save(path,"JPEG",quality=92,optimize=True,subsampling=0)
            if path.stat().st_size>=2_000_000:raise ValueError("oversize JPEG")
            item.update(status="CREATED_PENDING_VISUAL_KOREAN_PHOTO_CHECK",file=name,
                        size=[1080,1080],bytes=path.stat().st_size,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        source_sha256=hashlib.sha256(data).hexdigest(),source_dimensions=list(original.size))
            contact.paste(canvas,(1080*i,60))
            ImageDraw.Draw(contact).text((30+i*1080,20),sku+" source crop visual QA",fill="#222222")
        except Exception as e:item.update(status="HOLD",error=f"{type(e).__name__}: {e}")
        report["files"].append(item)
    contact.save(out/"BBIA_v237_TWO_PHOTO_ONLY_CONTACT.jpg",quality=89)
    (out/"BBIA_v237_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("V237_RESULT",json.dumps([{"sku":x["goodsNo"],"status":x["status"]} for x in report["files"]]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--src",required=True);p.add_argument("--out",required=True)
    z=p.parse_args();main(Path(z.src),Path(z.out))
