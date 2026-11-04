#!/usr/bin/env python3
"""Fix only four wrong English shade names in BBIA 206 JPGs; preserve public originals."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

# Carefully crop text-only rows, never product application photography or MK logo.
REPAIRS={
 "04.jpg":[((94,801,318,833),"20 Mauve Burn",(99,802),24),((564,801,811,833),"27 Mocha Burn",(571,802),24)],
 "06.jpg":[((247,426,394,454),"07 Rose Burn",(251,428),16),((441,688,595,715),"19 Ginger Burn",(445,691),16),
           ((633,688,794,715),"20 Mauve Burn",(640,691),16),((54,951,225,978),"27 Mocha Burn",(60,953),16)]
}
def sha(x):return hashlib.sha256(x).hexdigest()
def repair(im,rect):
    # Linearly reconstruct the background from native pixels immediately above/below
    # the short text row. This leaves all source photo pixels OUTSIDE text untouched.
    x0,y0,x1,y1=rect
    top_y=y0-5; bottom_y=y1+5
    source=im.copy()
    for x in range(x0,x1):
        top=source.getpixel((x,top_y))
        bot=source.getpixel((x,bottom_y))
        for y in range(y0,y1):
            t=(y-top_y)/(bottom_y-top_y)
            fill=tuple(round(top[ch]*(1-t)+bot[ch]*t) for ch in range(3))
            im.putpixel((x,y),fill)

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest={"checkpoint":"v226","goodsNo":"206","parent":"v225","source":["public/images/206/04.jpg","public/images/206/06.jpg"],
              "source_option_names_verified_with":[
                 "https://global.oliveyoung.com/product/detail?prdtNo=GA220213716",
                 "https://www.bbia.vn/san-pham/bbia-last-auto-gel-eyeliner/",
                 "https://item.gmarket.co.kr/Item?goodsCode=4715662901"],
              "new_jpg":[], "sale_approved":False,"other_26_shade_photos_authenticated":False,
              "public_files_modified":False,"existing_55_public_urls_changed":False}
    fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    board=Image.new("RGB",(2160,2300),"#eeeeee")
    d=ImageDraw.Draw(board)
    for idx,(filename,rows) in enumerate(REPAIRS.items()):
        path=Path("public/images/206")/filename
        old=Image.open(path).convert("RGB")
        assert old.size==(1080,1080)
        new=old.copy()
        for rect,label,pos,size in rows:
            repair(new,rect)
            font=ImageFont.truetype(fontpath,size)
            ImageDraw.Draw(new).text(pos,label,font=font,fill=(49,48,48))
        name="BBIA_206_"+filename[:2]+"_SHADE_LABELS_v226_QA_PENDING.jpg"
        dest=out/name
        new.save(dest,"JPEG",quality=94,subsampling=0,optimize=True)
        with Image.open(dest) as check:
            check.verify()
        board.paste(old,(0,55+idx*1120))
        board.paste(new,(1080,55+idx*1120))
        d.text((10,14+idx*1120),"ORIGINAL "+filename,fill="#222222")
        d.text((1100,14+idx*1120),"v226 corrected English label candidate",fill="#222222")
        manifest["new_jpg"].append({"name":name,"source":str(path),"original_sha256":sha(path.read_bytes()),
            "output_sha256":sha(dest.read_bytes()),"bytes":dest.stat().st_size,"dimensions":[1080,1080],
            "corrected_labels":[r[1] for r in rows]})
    board.save(out/"BBIA_v226_BEFORE_AFTER_04_06.jpg",quality=89,subsampling=0)
    (out/"QA_MANIFEST_v226.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print("V226_CORRECTED",json.dumps([{"name":x["name"],"bytes":x["bytes"],"labels":x["corrected_labels"]} for x in manifest["new_jpg"]]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);main(Path(p.parse_args().out))
