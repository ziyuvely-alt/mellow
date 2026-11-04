#!/usr/bin/env python3
"""Replace only bottom Korean caption in existing 206/03; keep source image immutable."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC=Path("public/images/206/03.jpg")
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    source=Image.open(SRC).convert("RGB")
    if source.size!=(1080,1080): raise RuntimeError("Original unexpected dimensions")
    im=source.copy()
    # Original inset photograph x≈339..739, Korean caption near y≈811..870.
    # Correct caption by local background-matching: do not alter pencil/texture upper region.
    region=(337,815,741,896)
    x0,y0,x1,y1=region
    # The photo's lower area is pale pink. Estimate from nearby upper area and
    # smoothly feather the patch edge to prevent a hard rectangular replacement.
    bg=Image.new("RGB",(x1-x0,y1-y0))
    d=ImageDraw.Draw(bg)
    for y in range(y1-y0):
        sample=source.getpixel((365,min(792,775+y//6)))
        d.line((0,y,x1-x0,y),fill=sample)
    mask=Image.new("L",bg.size,0)
    m=ImageDraw.Draw(mask)
    m.rounded_rectangle((8,2,bg.width-8,bg.height-2),radius=20,fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(14))
    im.paste(bg,(x0,y0),mask)
    # Do not insert claims about precise shades: factual generic English caption only.
    fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font=ImageFont.truetype(fontpath,18) if Path(fontpath).exists() else ImageFont.load_default()
    d=ImageDraw.Draw(im)
    label="PENCIL DETAIL  |  SHADE MAY VARY"
    bb=d.textbbox((0,0),label,font=font)
    x=(337+741-(bb[2]-bb[0]))//2
    d.text((x,836),label,fill=(117,100,99),font=font)
    path=out/"BBIA_206_03_EN_CAPTION_FIX_v222_QA_PENDING.jpg"
    im.save(path,"JPEG",quality=94,subsampling=0,optimize=True)
    with Image.open(path) as verified: verified.verify()
    contact=Image.new("RGB",(2160,1140),"#eeeeee")
    contact.paste(source,(0,60));contact.paste(im,(1080,60))
    c=ImageDraw.Draw(contact);c.text((30,20),"ORIGINAL 03: Korean embedded caption",fill="#222222")
    c.text((1110,20),"v222 QA candidate: selective English caption only",fill="#222222")
    contact.save(out/"BBIA_v222_ORIGINAL_VS_EN_QA_CONTACT.jpg",quality=92)
    manifest={
      "checkpoint":"v222","product":"BBIA Last Auto Gel Eyeliner",
      "goodsNo":"206","source":str(SRC),
      "source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
      "output":path.name,"output_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "output_bytes":path.stat().st_size,
      "output_size":[1080,1080],
      "caption_repair_region":list(region),
      "qa_status":"QA_PENDING",
      "original_published_image_unchanged":True,
      "no_shade_mapping_claim":True,
      "no_sales_approval":True
    }
    (out/"QA_MANIFEST_v222.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print("V222_CREATED",json.dumps({"bytes":manifest["output_bytes"],"sha256":manifest["output_sha256"],"original_unchanged":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    main(Path(p.parse_args().out))
