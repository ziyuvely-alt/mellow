#!/usr/bin/env python3
"""Use the v222 JPG as source. Remove entire embedded Korean caption below photo, no source re-render."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
def main(srcdir,out):
    out.mkdir(parents=True,exist_ok=True)
    target=next(srcdir.rglob("BBIA_206_03_EN_CAPTION_FIX_v222_QA_PENDING.jpg"))
    original=Image.open(target).convert("RGB")
    assert original.size==(1080,1080)
    im=original.copy()
    # The Korean text is at y~861-895; frame's pink backdrop x340..740.
    # Preserve actual pencil and shade photography above y=805.
    left,top,right,bottom=340,808,740,924
    for y in range(top,bottom):
        # Pale pink backdrop is near-flat. Sample the source's nearby clear strip to maintain tint.
        sample=original.getpixel((720,800))
        for x in range(left,right):
            im.putpixel((x,y),sample)
    # Reinsert only simple, already verified English identifying caption.
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f=ImageFont.truetype(font,20) if Path(font).exists() else ImageFont.load_default()
    label="PENCIL DETAIL  |  SHADE MAY VARY"
    d=ImageDraw.Draw(im)
    bounds=d.textbbox((0,0),label,font=f)
    x=(left+right-(bounds[2]-bounds[0]))//2
    d.text((x,857),label,font=f,fill=(110,93,93))
    dst=out/"BBIA_206_03_EN_NO_KOREAN_v223_QA_PENDING.jpg"
    im.save(dst,"JPEG",quality=94,optimize=True,subsampling=0)
    with Image.open(dst) as test:
        test.verify()
    board=Image.new("RGB",(2160,1170),"#eeeeee")
    board.paste(original,(0,70))
    board.paste(im,(1080,70))
    draw=ImageDraw.Draw(board)
    draw.text((25,22),"v222 residual Korean caption",fill=(20,20,20))
    draw.text((1100,22),"v223 complete lower-caption cleanup",fill=(20,20,20))
    board.save(out/"BBIA_v223_BEFORE_AFTER_CONTACT.jpg",quality=91)
    report={"checkpoint":"v223","parent":"v222","goodsNo":"206","frame":"03","source_artifact_run":41827460390,
      "source_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
      "output_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
      "output_bytes":dst.stat().st_size,"size":[1080,1080],
      "edited_region":[left,top,right,bottom],
      "source_product_photo_above_808_untouched_before_jpeg_encoding":True,
      "preexisting_public_files_changed":False,"shade_21_conflict_unresolved":True,
      "sales_approved":False,"qa_status":"VISUAL_QA_PENDING"}
    (out/"QA_MANIFEST_v223.json").write_text(json.dumps(report,indent=2))
    print("V223_EDITED",json.dumps({"bytes":report["output_bytes"],"source_sha256":report["source_sha256"],"output_sha256":report["output_sha256"]}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--src",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();main(Path(a.src),Path(a.out))
