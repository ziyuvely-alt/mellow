#!/usr/bin/env python3
"""v2434c corrected Peripera informational JPEG: replace failing ornament entirely
with coherent rounded panel; preserve trustworthy text content, no product photos.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
P=Path("baseline-v2434")/"sales-image-drafts"/"pending-08"/"INFO_FORMULA_01_V2414_EN_V2421_V2434.jpg"
OUT=Path("v2434c-output");OUT.mkdir(exist_ok=True)
assert P.exists()
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(P) as opened:
 im=opened.convert("RGB");d=ImageDraw.Draw(im)
 # Entire pale panel, no graphics extending off its bounds. Avoid covering customer heading.
 panel=im.getpixel((400,338))
 bg=im.getpixel((25,320))
 d.rectangle((60,296,1040,777),fill=bg)
 d.rounded_rectangle((72,303,1008,763),radius=39,fill=panel)
 for t,y,size,bold in [
  ("MOOD GLOWY TINT",387,54,True),
  ("Lip tint  |  4 g",565,39,False),
  ("Choose a shade from the listing",646,30,False)
 ]:
  font=f(size,bold);bb=d.textbbox((0,0),t,font=font);width=bb[2]-bb[0]
  assert width<=840
  d.text((540-width//2,y),t,font=font,fill=(44,64,53))
 dst=OUT/"sales-image-drafts/pending-08/INFO_FORMULA_01_clean_panel_V2434c.jpg"
 dst.parent.mkdir(parents=True,exist_ok=True)
 im.save(dst,"JPEG",quality=95,optimize=True)
 with Image.open(dst) as test:
  test.load(); assert test.size==(1080,1080) and test.format=="JPEG" and dst.stat().st_size<2000000
report={"version":"2.4.34c","superseded":["v2434 INFO_FORMULA","v2434b ornament revision"],"new_customer_copy_revision":1,"output":str(dst.relative_to(OUT)),"sha256":sha(dst),"size":dst.stat().st_size,"style":"plain rounded panel; no circle or background rectangle artifacts","source_images_modified":0,"final_approval":False,"public_URLs_changed":0}
(OUT/"v2434c_checkpoint.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
