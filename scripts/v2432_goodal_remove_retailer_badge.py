#!/usr/bin/env python3
"""v2432 customer image edit: genuine goodal photograph, omit third-party retailer badge by cropping, not inpainting."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
BASE=Path("baseline-v2427b")
OUT=Path("v2432-output");OUT.mkdir(exist_ok=True)
SRC=BASE/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"/"en-photo-captions"/"pending-20"/"SOURCE_8536a4dd0b8b_EN_V2421C.jpg"
assert SRC.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
oldhash=sha(SRC)
with Image.open(SRC) as im:
 im.load();assert im.size==(1080,1080)
 # Source layout: photograph x240:840 y130:730, badge x705:815 y148:270.
 # Crop central x420:665 y175:700 preserves real entire bottle (x~486:601, y~200:667)
 # while provably removing x705+ retailer badge; no synthetic color/product pixels.
 product=im.convert("RGB").crop((420,175,665,700))
 im2=Image.new("RGB",(1080,1080),(246,242,235))
 d=ImageDraw.Draw(im2)
 d.text((72,54),"goodal",font=font(38,True),fill=(45,62,52))
 d.text((72,113),"Green Tangerine Vita C",font=font(40,True),fill=(45,62,52))
 d.text((72,168),"Serum Mist",font=font(37),fill=(45,62,52))
 d.line((72,230,1008,230),fill=(182,191,182),width=2)
 photo=ImageOps.contain(product,(425,655),Image.Resampling.LANCZOS)
 # A contained plain source photo is intentional; original background remains in cropped pixels.
 im2.paste(photo,((1080-photo.width)//2,247))
 d.line((72,927,1008,927),fill=(182,191,182),width=2)
 d.text((72,956),"100 mL",font=font(50,True),fill=(45,62,52))
 target=OUT/"sales-image-drafts"/"pending-20"/"goodal_serum_mist_100ml_no_retailer_badge_V2432.jpg"
 target.parent.mkdir(parents=True,exist_ok=True)
 im2.save(target,"JPEG",quality=93,optimize=True)
 with Image.open(target) as check:
  check.load();assert check.format=="JPEG" and check.size==(1080,1080) and target.stat().st_size<2000000
# Source JPEG source hash unchanged.
assert sha(SRC)==oldhash
result={"version":"2.4.32","group_id":"pending-20","real_JPG_edited":1,"removed_retailer_badge_by_source_crop":True,
"original_brand_photo_pixels_preserved_in_crop":True,"actual_product_packaging_fabricated":False,
"original_source_sha256":oldhash,"output_file":str(target.relative_to(OUT)),"output_sha256":sha(target),
"output_bytes":target.stat().st_size,"output_dimensions":[1080,1080],
"status":"SALES_IMAGE_DRAFT","blockers":["COMMERCIAL_REUSE_PERMISSION_REQUIRED","STOCK_PACKAGING_VERIFICATION_REQUIRED","MK_ORIGINAL_LOGO_REQUIRED"],"final_QA_approved":False,
"public_urls_changed":0,"source_jpg_changed":0,
"verified_brand_listing":"https://clubclio.co.kr/shop/goodsList/121731002000000",
"next":["Review final JPG visually for cropped product / read small text","Check exact current packaging and rights","Continue safe real photo revisions on other product families without invented swatches"]}
(OUT/"v2432_checkpoint.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k not in ["blockers","next"]},ensure_ascii=False),flush=True)
