#!/usr/bin/env python3
"""v2.4.31c: two actual goodal customer info JPEG copy corrections, no product pixels changed."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
SRC=Path("baseline-v2427b")
OUT=Path("v2431c-output");OUT.mkdir(exist_ok=True)
BASE=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"/"en-customer-drafts"/"pending-20"
def font(n,b=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def hash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for name,revision,line1,line2 in [
 ("INFO_02_V2412B_EN_V2421.jpg","unverified_25AD_removed","Green Tangerine Vita C","Serum Mist"),
 ("INFO_03_V2412B_EN_V2421.jpg","repetitive_howto_fixed","Shake well before use","Spray evenly onto skin")
]:
 src=BASE/name
 assert src.is_file()
 with Image.open(src) as image:
  img=image.convert("RGB"); d=ImageDraw.Draw(img)
  # Edit only text rows inside flat information inset, preserving surrounding header and product photographs.
  sample=img.getpixel((540,733))
  d.rectangle((230,547,870,703),fill=sample)
  for text,y,sz in [(line1,569,39),(line2,646,35)]:
   f=font(sz)
   bb=d.textbbox((0,0),text,font=f)
   assert bb[2]<=740
   d.text((540-bb[2]//2,y),text,font=f,fill=(48,67,57))
  dest=OUT/"sales-image-drafts"/"pending-20"/(name.replace(".jpg","")+"_V2431c.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  img.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load()
   assert ck.size==(1080,1080) and ck.format=="JPEG" and dest.stat().st_size<2000000
  assert hash(src)!=hash(dest)
  results.append({"source":str(src.relative_to(SRC)),"source_sha256":hash(src),"output":str(dest.relative_to(OUT)),"sha256":hash(dest),"revision":revision,"stage":"SALES_IMAGE_DRAFT","rights_verified":False,"visual_qa":"PENDING"})
report={"version":"2.4.31c","customer_info_jpg_modified":2,"product_photo_replaced":0,
"candidate_official_swatches":0,"sale_approved":0,"published_urls_changed":0,
"original_unchanged":True,"evidence":[
"https://www.hwahae.com/en/products/goodal-Green-Tangerine-Vita-C-Serum-Mist/2013152",
"https://lewkin.com/ko-kr/products/green-tangerine-vita-c-serum-mist-100ml"],"edits":results,
"next":"Get exact current retail packaging and rights; do not promote QA draft without evidence"}
(OUT/"v2431c_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k!="edits"}),flush=True)
