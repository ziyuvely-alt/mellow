#!/usr/bin/env python3
"""v2435: patch provably misleading caption on actual Peripera hero.
Reposition existing exact photographic shade collage without editing any swatch pixels.
This is an unapproved product-image DRAFT until shade generation/source/rights proven.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json
SRCROOT=Path("v2427b-source")
SRC=SRCROOT/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-hero-fixed/pending-08/01_HERO_EN_V2422.jpg"
OUT=Path("v2435-output");OUT.mkdir(exist_ok=True)
assert SRC.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
old=sha(SRC)
with Image.open(SRC) as input:
 input.load();assert input.size==(1080,1080)
 # Existing shade collage x145..935, y90..880. Do not alter original color/shade pixels.
 collage=input.convert("RGB").crop((145,90,935,880))
 canvas=Image.new("RGB",(1080,1080),(255,255,255))
 d=ImageDraw.Draw(canvas)
 d.text((58,36),"peripera",font=f(40,True),fill=(46,65,56))
 d.text((58,96),"Mood Glowy Tint",font=f(44,True),fill=(46,65,56))
 d.line((58,167,1022,167),fill=(185,192,184),width=2)
 resized=ImageOps.contain(collage,(760,760),Image.Resampling.LANCZOS)
 canvas.paste(resized,((1080-resized.width)//2,188))
 d.line((58,973,1022,973),fill=(185,192,184),width=2)
 d.text((59,991),"4 g",font=f(30,True),fill=(46,65,56))
 dest=OUT/"sales-image-drafts/pending-08/01_peripera_selected_shades_no_20claim_V2435.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 canvas.save(dest,"JPEG",quality=93,optimize=True)
 with Image.open(dest) as ck:
  ck.load()
  assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2_000_000
assert sha(SRC)==old
status={
 "version":"2.4.35","image_group":"pending-08","new_actual_revised_JPG":1,
 "source_sha256":old,"output_sha256":sha(dest),"file":str(dest.relative_to(OUT)),
 "change":"Removed misleading Shades 01-20 caption from actual 8/20 sampled shade collage; original shade photographs preserved, resized uniformly",
 "status":"SALES_IMAGE_DRAFT","final_qa_approved":False,
 "original_photo_pixels_fabricated":False,"source_provenance_verified":False,
 "retail_shade_generation_verified":False,"commercial_rights_verified":False,
 "prior_image_files_modified":0,"public_urls_overwritten":0,
 "web_evidence":[
  {"url":"https://www.gsshop.com/prd/prd.gs?prdid=1106843033","observation":"26AD currently lists shade 012 개강여신; 004 006 007 not listed; do not presume discontinued"},
  {"url":"https://www.obge.co.kr/product/detail.html?product_no=10","observation":"OBgE product confirms 15g; no confirmation existing file matches renewed packaging"}
 ],
 "do_not_claim":"This is NOT a 20-color official swatch chart, NOR an approved commercial image",
 "next_restart":["Compare 12 shade names between exact old 4g generation and 26AD","Find official full 01-20 reference for precise SKU mapping","Continue nonblocking 30-group image and packaging verification"]
}
(OUT/"v2435_checkpoint.json").write_text(json.dumps(status,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in status.items() if k not in ("web_evidence","next_restart")},ensure_ascii=False),flush=True)
