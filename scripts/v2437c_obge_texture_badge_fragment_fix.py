#!/usr/bin/env python3
"""v2437c remove residual unverified MK seal fragment from real OBgE texture draft.
Crop from original photo excluding MK seal coordinates entirely, preserve real texture pixels.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
BASE=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions/pending-11/INV_04_a0c9d28d19_EN_V2421C.jpg"
OUT=Path("v2437c-output");OUT.mkdir(exist_ok=True)
assert BASE.exists()
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
old=sh(BASE)
with Image.open(BASE) as x:
 x.load()
 # seal is x828+ y729+, so source region ends at x805 and y710.
 crop=x.convert("RGB").crop((270,253,805,710))
 photo=ImageOps.contain(crop,(760,635),Image.Resampling.LANCZOS)
 img=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(img)
 d.text((70,54),"OBgE",font=ff(38,True),fill=(45,63,54))
 d.text((70,121),"All In One Double Essence",font=ff(43,True),fill=(45,63,54))
 d.line((70,192,1010,192),fill=(185,192,186),width=2)
 img.paste(photo,((1080-photo.width)//2,246))
 d.line((70,907,1010,907),fill=(185,192,186),width=2)
 d.text((70,939),"50 mL + 50 mL",font=ff(51,True),fill=(45,63,54))
 target=OUT/"sales-image-drafts/pending-11/OBGE_texture_no_logo_fragment_V2437c.jpg"
 target.parent.mkdir(parents=True,exist_ok=True)
 img.save(target,"JPEG",quality=94,optimize=True)
 with Image.open(target) as t:
  t.load();assert t.format=="JPEG" and t.size==(1080,1080) and target.stat().st_size<2_000_000
assert old==sh(BASE)
cp={"version":"2.4.37c","new_actual_modified_jpg":1,"previous_rejected":"production-assets-v2437b-three-more-photo-revisions/sales-image-drafts/pending-11/pending-11_actual_photo_copy_revised_V2437b.jpg","reason":"Visible MK fragment remains at bottom right of rejected image","new_file":str(target.relative_to(OUT)),"source_sha256":old,"output_sha256":sh(target),"source_photo_unchanged":True,"retail_status":"SALES_IMAGE_DRAFT","commercial_reuse_rights_verified":False,"FINAL_QA_APPROVED":0,"published_URLs_changed":0}
(OUT/"v2437c_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps(cp,ensure_ascii=False),flush=True)
