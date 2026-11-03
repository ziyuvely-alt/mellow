#!/usr/bin/env python3
"""Repair layout overlap in v2431 real 200mL bottle draft, no product alteration."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib
SRC=Path("baseline-v2427b")
OUT=Path("v2431b-output")
OUT.mkdir(exist_ok=True)
p=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"new-independent-photo-candidates"/"pending-27"/"PRODUCT_PHOTO_01_V2424.jpg"
assert p.exists()
def sh(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
with Image.open(p) as source:
 source.load();source=source.convert("RGB")
 # Keep actual 200mL bottle from known authenticated source, leaving all source print pixels unchanged.
 photo=source.crop((91,9,710,912))
 photo=ImageOps.contain(photo,(510,640),Image.Resampling.LANCZOS)
 im=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,195),fill=(246,243,239))
 d.text((72,44),"PIXEL PURE",font=f(32,True),fill=(45,64,54))
 d.text((72,101),"Soothing Ampoule Toner",font=f(43,True),fill=(45,64,54))
 d.line((72,177,1008,177),fill=(181,192,181),width=2)
 x=(1080-photo.width)//2
 im.paste(photo,(x,219))
 d.rectangle((0,878,1080,1080),fill=(245,244,239))
 d.line((72,906,1008,906),fill=(181,192,181),width=2)
 d.text((72,935),"200 mL",font=f(65,True),fill=(45,64,54))
 d.text((72,1027),"Soothing Ampoule Toner",font=f(20),fill=(69,83,73))
 target=OUT/"sales-image-drafts"/"pending-27"/"01_correct_200ml_bottle_layout_fixed_V2431b.jpg"
 target.parent.mkdir(parents=True,exist_ok=True)
 im.save(target,"JPEG",quality=94,optimize=True)
 with Image.open(target) as ck:
  ck.load();assert ck.size==(1080,1080) and ck.format=="JPEG" and target.stat().st_size<2000000
 out={"version":"2.4.31b","corrected_jpg":1,"source_real_200ml_photo_sha256":sh(p),"output_sha256":sh(target),"new_active_photo":str(target.relative_to(OUT)),"old_layout_2431_image_superseded":True,"photo_print_unchanged":True,"white_square":"white studio background blended with white field, no cutout performed","rights_verified":False,"stock_verified":False,"final_qa_approved":False,"public_urls_changed":0}
 (OUT/"v2431b_checkpoint.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
 print(json.dumps(out),flush=True)
