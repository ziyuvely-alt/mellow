#!/usr/bin/env python3
"""v2435b replace cropped Pixelpure Aura Radiance Serum hero from preserved whole-bottle source.
Exclude MK badge through central product crop. No fabricated product pixels or official-image claims.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
SRCROOT=Path("v2427b-source")
BASE=SRCROOT/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions/pending-30"
SRC=BASE/"INV_03_a2a1622ea7_EN_V2421C.jpg"
OLD=BASE/"INV_01_449aa19f31_EN_V2421C.jpg"
O=Path("v2435b-output");O.mkdir(exist_ok=True)
assert SRC.exists() and OLD.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
before={str(p):sha(p) for p in (SRC,OLD)}
with Image.open(SRC) as opened:
 opened.load()
 assert opened.size==(1080,1080)
 # Complete original 50mL serum bottle x445..610, y263..750; crop x350..700 avoids MK logo (x828+).
 photo=opened.convert("RGB").crop((350,240,700,766))
 photo=ImageOps.contain(photo,(510,640),Image.Resampling.LANCZOS)
 im=Image.new("RGB",(1080,1080),(255,255,255))
 d=ImageDraw.Draw(im)
 d.text((72,50),"PIXEL PURE",font=ff(40,True),fill=(45,63,56))
 d.text((72,119),"Aura Radiance Serum",font=ff(43,True),fill=(45,63,56))
 d.line((72,187,1008,187),fill=(184,192,185),width=2)
 im.paste(photo,((1080-photo.width)//2,224))
 d.line((72,925,1008,925),fill=(184,192,185),width=2)
 d.text((72,956),"50 mL",font=ff(55,True),fill=(45,63,56))
 out=O/"sales-image-drafts/pending-30/PIXELPURE_Aura_Radiance_50ml_full_bottle_V2435b.jpg"
 out.parent.mkdir(parents=True,exist_ok=True)
 im.save(out,"JPEG",quality=94,optimize=True)
 with Image.open(out) as check:
  check.load()
  assert check.size==(1080,1080) and check.format=="JPEG" and out.stat().st_size<2_000_000
assert before=={str(p):sha(p) for p in (SRC,OLD)}
report={"version":"2.4.35b","group":"pending-30","actual_product_photo_frame_modified":1,
"source":"INV_03_a2a1622ea7_EN_V2421C.jpg","source_sha256":sha(SRC),"superseded_frame":"INV_01_449aa19f31_EN_V2421C.jpg","new_file":str(out.relative_to(O)),"new_sha256":sha(out),
"product_pictured":"PIXELPURE Aura Radiance Serum 50mL, original photographed packaging",
"photo_source_pixels_generated":False,"MK_badge_omitted_by_cropping":True,"brand_photo_rights_verified":False,
"stock_package_verified":False,"visual_QA_after_edit":"PENDING","FINAL_QA_APPROVED":False,
"public_URL_changed":0,"original_photos_overwritten":0}
(O/"v2435b_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False),flush=True)
