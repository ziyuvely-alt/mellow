#!/usr/bin/env python3
"""v2436b replace rejected oversized pad texture with unchanged full product-jar photograph."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
B=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions/pending-28"
SRC=B/"INV_03_7280158c0e_EN_V2421C.jpg";OUT=Path("v2436b-output");OUT.mkdir(exist_ok=True)
assert SRC.is_file()
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
prior=h(SRC)
with Image.open(SRC) as base:
 base.load();assert base.size==(1080,1080)
 # Existing whole real jar is approximately x333..751, y284..715.
 photo=base.convert("RGB").crop((295,268,797,730))
 photo=ImageOps.contain(photo,(700,650),Image.Resampling.LANCZOS)
 canvas=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(canvas)
 d.text((70,52),"PIXEL PURE",font=f(38,True),fill=(44,62,54))
 d.text((70,114),"Glow Cleansing Serum Pad",font=f(43,True),fill=(44,62,54))
 d.line((70,190,1010,190),fill=(185,193,186),width=2)
 canvas.paste(photo,((1080-photo.width)//2,242))
 d.line((70,908,1010,908),fill=(185,193,186),width=2)
 d.text((70,940),"210 mL / 70 Pads",font=f(48,True),fill=(44,62,54))
 dst=OUT/"sales-image-drafts/pending-28/PIXELPURE_full_jar_replacement_V2436b.jpg"
 dst.parent.mkdir(parents=True,exist_ok=True)
 canvas.save(dst,"JPEG",quality=94,optimize=True)
 with Image.open(dst) as check:
  check.load();assert check.format=="JPEG" and check.size==(1080,1080) and dst.stat().st_size<2_000_000
assert h(SRC)==prior
cp={"version":"2.4.36b","group":"pending-28","new_actual_revised_JPG":1,
"supersedes":"production-assets-v2436-three-source-photo-drafts/sales-image-drafts/pending-28/pending-28_genuine-photo_no-MK_V2436.jpg",
"reason":"Prior texture-only enlarged draft was not sufficiently product-identifying",
"replacement_source":"INV_03_7280158c0e_EN_V2421C.jpg","source_sha256":prior,
"replacement_file":str(dst.relative_to(OUT)),"replacement_sha256":h(dst),
"source_real_photo_unchanged":True,"MK_badge_excluded_by_crop":True,
"sales_approval":False,"rights_verified":False,"stock_verified":False,
"public_urls_overwritten":0,"next":"Visually inspect exact new image, leave rights and packaging holds"}
(OUT/"v2436b_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps(cp,ensure_ascii=False),flush=True)
