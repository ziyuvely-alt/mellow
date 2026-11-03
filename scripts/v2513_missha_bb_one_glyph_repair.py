#!/usr/bin/env python3
"""Repair ONLY v2512 MISSHA BB three-shade card whose Hangul glyphs rendered as tofu.
No photo replacement, no new colors, no modification to second already-good JPG.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
source=Path("source-v2512/04-stock-3-shade-name-guide.jpg")
assert source.is_file()
out=Path("v2513-missha-bb-one-glyph-correction");out.mkdir(exist_ok=True)
im=Image.open(source).convert("RGB");d=ImageDraw.Draw(im)
ft=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
# Redraw only interiors of three existing shade rows, retaining overall art and layout.
for i,(code,name) in enumerate([("21","LIGHT BEIGE"),("23","NATURAL BEIGE"),("25","WARM BEIGE")]):
 y=424+i*164
 color="#f0e3e8" if i!=1 else "#f1eae8"
 d.rounded_rectangle((76,y,1003,y+143),radius=25,fill=color)
 d.text((110,y+45),"#"+code,font=ft(43,True),fill="#69464d")
 d.text((284,y+51),name,font=ft(34,True),fill="#69464d")
path=out/"04-stock-shade-names-legible.jpg";im.save(path,"JPEG",quality=92,subsampling=0,optimize=True)
raw=path.read_bytes()
assert Image.open(path).size==(1080,1080) and len(raw)<2_000_000
manifest={"date":"2026-11-04","family":"pending-03","reason":"DejaVu Sans lacks Korean glyphs; first v2512 card rendered tofu rectangles",
 "repaired_file":path.name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
 "previous_photo_JPGs_untouched":True,"v2512_second_info_card_untouched":True,
 "colors_fabricated":False,"stock_edition_photo_confirmed":False,
 "MK_original_logo_present":False,"final_sales_QA":"HOLD","public_URLs_added":0,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"fixed_JPG":path.name,"sha256":manifest["sha256"]}))
