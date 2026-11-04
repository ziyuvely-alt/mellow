#!/usr/bin/env python3
"""v236 source-photo detail-role QA scenes, NOT final sale images. Preserve v234 assets."""
import argparse,hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
SOURCE=[
 ("172","Never Die Mascara",0,0,800),
 ("1000000227","Nudy Lip Pencil",1,0,850),
 ("1000000221","Soft Blush",1,0,850),
 ("1000000247","Eye and Cheek Primer",1,0,850),
]
def font(n,bold=False):
    f="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(f,n)
def fetch(url):
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as r:
        return r.read(12_000_000)
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    fam={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
    board=Image.new("RGB",(1480,1220),"#f3f3f3")
    d=ImageDraw.Draw(board)
    d.text((15,12),"BBIA v236  |  FOUR DISTINCT DETAIL SCENES  |  VISUAL QA ONLY",fill="#222222",font=font(20,True))
    results=[]
    for i,(sku,label,source_index,y0,y1) in enumerate(SOURCE):
        url=fam[sku]["detail_references"][source_index]
        row={"goodsNo":sku,"product_label":label,"source":url,"source_index":source_index,"crop_y":[y0,y1]}
        try:
            data=fetch(url)
            photo=Image.open(io.BytesIO(data)).convert("RGB")
            row.update(source_sha256=hashlib.sha256(data).hexdigest(),source_size=list(photo.size))
            # Preserve exact source's original proportions within a quiet, neutral photo canvas.
            crop=photo.crop((0,y0,photo.width,min(y1,photo.height)))
            crop.thumbnail((880,745),Image.Resampling.LANCZOS)
            canvas=Image.new("RGB",(1080,1080),"#faf9f7")
            drawer=ImageDraw.Draw(canvas)
            drawer.text((65,55),"BBIA",font=font(47,True),fill="#282727")
            drawer.text((65,123),label.upper(),font=font(31,True),fill="#433a39")
            drawer.line((65,190,1015,190),fill="#ddd3cf",width=2)
            x=(1080-crop.width)//2
            y=205+(755-crop.height)//2
            canvas.paste(crop,(x,y))
            drawer.text((65,999),"OFFICIAL DETAIL PHOTO  |  QA REFERENCE",font=font(24),fill="#625856")
            file=f"BBIA_{sku}_DETAIL_ROLE_v236_QA_PENDING.jpg"
            canvas.save(out/file,"JPEG",quality=90,optimize=True,subsampling=0)
            assert (out/file).stat().st_size < 2_000_000
            row.update(status="NEW_SECONDARY_ROLE_JPG_QA_PENDING",output=file,
                       output_sha256=hashlib.sha256((out/file).read_bytes()).hexdigest(),
                       output_bytes=(out/file).stat().st_size)
            preview=canvas.copy();preview.thumbnail((705,520),Image.Resampling.LANCZOS)
            bx=15+(i%2)*740;by=65+(i//2)*575
            board.paste(preview,(bx,by))
            d.text((bx,by+520),f"{sku} - source height {photo.height}px",fill="#262626")
        except Exception as e:
            row.update(status="SOURCE_OR_CANDIDATE_HOLD",error=f"{type(e).__name__}: {str(e)[:150]}")
        results.append(row)
    board.save(out/"BBIA_v236_FOUR_DETAIL_CONTACT.jpg",quality=88)
    report={"checkpoint":"v236","parent":"v235","source_count":4,"new_jpg":sum(x["status"]=="NEW_SECONDARY_ROLE_JPG_QA_PENDING" for x in results),
            "records":results,"status":"VISUAL_QA_PENDING_NOT_SALES_APPROVED",
            "limits":["Could contain Korean copy embedded in detail originals","Variant-specific images not verified","No existing public or v234 images changed"],
            "existing_assets_modified":False,"sales_approved":0}
    (out/"BBIA_v236_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("V236_CREATED",json.dumps({"new_jpg":report["new_jpg"],"statuses":[[x["goodsNo"],x["status"]] for x in results]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
