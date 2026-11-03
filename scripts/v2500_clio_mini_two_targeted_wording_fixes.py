#!/usr/bin/env python3
"""v2500 targeted corrections ONLY to two preexisting v2499 CLIO mini informational JPGs.
No re-creation of photographs or color swatches.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
SRC=Path("v2499-source")
OUT=Path("v2500-clio-mini-targeted-corrections");OUT.mkdir(exist_ok=True)
font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(im,name):
 p=OUT/name;im.save(p,"JPEG",quality=92,subsampling=0,optimize=True)
 b=p.read_bytes()
 assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 return {"file":name,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def copy_bg(im, area, xy):
 # Sample clean background colors directly from prior cards, no fabricated product photo.
 d=ImageDraw.Draw(im)
 d.rectangle(area,fill=im.getpixel(xy))
src=Image.open(SRC/"04-mini-3-shade-name-guide.jpg").convert("RGB")
d=ImageDraw.Draw(src)
# Verified option name, not inferred undertone: cover only secondary descriptive lines.
for y in (580,739,899):
 copy_bg(src,(282,y-8,948,y+52),(810,y-30))
# Cover meta verification disclaimer in bottom margin, leaving the actual product option titles.
copy_bg(src,(55,949,1032,1033),(1017,945))
d=ImageDraw.Draw(src)
d.text((72,962),"Select the exact shade name in the product options.",font=font(24),fill="#4b6558")
first=save(src,"04-mini-3-shade-names-corrected.jpg")
# Same workflow does not modify previously finished product photo frames.
puff=Image.open(SRC/"05-mini-cushion-puff-use-guide.jpg").convert("RGB")
copy_bg(puff,(55,948,1035,1035),(1017,942))
d=ImageDraw.Draw(puff)
d.text((72,962),"See the product packaging for full directions.",font=font(24),fill="#4b6558")
second=save(puff,"05-mini-puff-directions-footer-corrected.jpg")
m={"date":"2026-11-04","family_id":"pending-04","source_run":41691203770,
   "source_JPGs_untouched":True,"exact_fixes":["Removed inferred warm/cool/neutral skin-tone marketing descriptions","Replaced internal evidence disclaimer with customer shade-selection instruction","Replaced internal QA footer on puff card"],"new_replacement_jpgs":[first,second],
   "fabricated_swatch_pixels":False,"official_photo_shade_chart_verified":False,"original_MK_logo_applied":False,"stock_generation_verified":False,"public_URLs_added":0,"xlsx_shared":False,"sales_final_QA":"HOLD"}
(OUT/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
print(json.dumps({"targeted_repair_JPGs":2,"new_hashes":[first["sha256"],second["sha256"]]}))
