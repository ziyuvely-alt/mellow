#!/usr/bin/env python3
"""v2500b: Repair the single failed CLIO mini 3-shade label card only.
Preserve all v2499/v2500 photos, cards and previous output immutably.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
S=Path("v2499-source")/"04-mini-3-shade-name-guide.jpg"
assert S.exists()
im=Image.open(S).convert("RGB")
d=ImageDraw.Draw(im)
F=lambda size,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",size)
card_color=(232,234,230)
for number,name,y in [("21C","LINGERIE",435),("21N","LINEN",595),("23N","GINGER",755)]:
 d.rounded_rectangle((70,y,1010,y+136),radius=25,fill=card_color)
 d.text((105,y+34),number,font=F(43,True),fill="#30483e")
 d.text((293,y+35),name,font=F(40,True),fill="#30483e")
d.rectangle((55,942,1045,1038),fill=im.getpixel((1030,925)))
d.text((70,963),"Please select the exact shade listed in your options.",font=F(23),fill="#4b6558")
out=Path("v2500b-clio-single-shade-correction");out.mkdir(exist_ok=True)
p=out/"04-mini-shades-factual-corrected.jpg"
im.save(p,"JPEG",quality=92,optimize=True)
b=p.read_bytes()
assert Image.open(p).size==(1080,1080) and len(b)<2000000
m={"date":"2026-11-04","family":"pending-04","source_original_run":41691203770,"prior_v2500_attempt":"REJECTED_VISUAL_QA_PATCH_INTERSECTS_SHADE_LABELS","corrected_single_JPG":p.name,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"other_completed_jpgs_recreated":0,"actual_color_swatches_synthesized":False,"mk_logo_missing":True,"original_shade_photo_missing":True,"published":False,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
print(json.dumps({"created_JPG":p.name,"sha256":m["sha256"],"size_bytes":m["bytes"]}))
