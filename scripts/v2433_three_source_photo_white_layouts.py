#!/usr/bin/env python3
"""v2.4.33 genuine product photograph white-field partial edit, preserving source product pixels.
No inpainting, generative product, fake alpha, rights claims, or public URL mutation.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
BASE=Path("baseline-v2427b")/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"
OUT=Path("v2433-output"); OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(sz,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",sz)
jobs=[
 {"id":"pending-17","path":"en-photo-captions/pending-17/SOURCE_1354c0fcba9a_EN_V2421C.jpg","crop":[132,22,947,837],"brand":"Dr.G","title":"Brightening Up Moisture Sun","volume":"50 mL","risk":"STOCK_GENERATION_AND_RIGHTS"},
 {"id":"pending-19","path":"en-hero-fixed/pending-19/01_HERO_EN_V2422.jpg","crop":[180,125,900,845],"brand":"goodal","title":"Green Tangerine Vita C Cream Alpha","volume":"50 mL","risk":"STOCK_GENERATION_AND_RIGHTS"},
 {"id":"pending-23","path":"en-hero-fixed/pending-23/01_HERO_EN_V2422.jpg","crop":[145,90,935,880],"brand":"OBgE","title":"Pore Zero Oil Control Sun Cream","volume":"50 mL","risk":"STOCK_GENERATION_AND_RIGHTS"}
]
outputs=[]
for j in jobs:
 src=BASE/j["path"];assert src.exists()
 before=sha(src)
 with Image.open(src) as orig:
  orig.load();assert orig.size==(1080,1080)
  photo=orig.convert("RGB").crop(tuple(j["crop"]))
  # Retain actual source photo content and its white studio background.
  photo=ImageOps.contain(photo,(670,635),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),(255,255,255))
  d=ImageDraw.Draw(canvas)
  d.text((72,49),j["brand"],font=font(44,True),fill=(45,62,53))
  fs=41
  while fs>=27 and d.textbbox((0,0),j["title"],font=font(fs,True))[2]>940:fs-=1
  assert d.textbbox((0,0),j["title"],font=font(fs,True))[2]<=940
  d.text((72,117),j["title"],font=font(fs,True),fill=(45,62,53))
  d.line((72,190,1008,190),fill=(181,191,183),width=2)
  canvas.paste(photo,((1080-photo.width)//2,218))
  d.line((72,901,1008,901),fill=(181,191,183),width=2)
  d.text((72,934),j["volume"],font=font(62,True),fill=(45,62,53))
  dst=OUT/"sales-image-drafts"/j["id"]/(j["id"]+"_real_product_photo_white_layout_V2433.jpg")
  dst.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dst,"JPEG",quality=94,optimize=True)
  with Image.open(dst) as ck:
   ck.load();assert ck.size==(1080,1080) and ck.format=="JPEG" and dst.stat().st_size<2_000_000
  assert sha(src)==before
  outputs.append({"group_id":j["id"],"original":j["path"],"original_SHA256":before,"new_image":str(dst.relative_to(OUT)),"output_SHA256":sha(dst),"bytes":dst.stat().st_size,"status":"SALES_IMAGE_DRAFT","pixel_source":"actual photographed existing JPG crop only","alpha_cutout":False,"rights_verified":False,"stock_package_verified":False,"layout_QA_pending":True})
cp={"version":"2.4.33","actual_new_modified_product_JPGs":len(outputs),"groups_modified":len(outputs),"source_pixels_generated":False,"original_image_changed":0,"published_URL_changed":0,"rights_verified":0,"FINAL_QA_APPROVED":0,"results":outputs,"next_restart":["visually inspect each of the 3 exported JPGs before promotion","if any product crop broken, reject only that draft and preserve original","continue white-inset source fix on next families","source and commercial-rights checks separate from draft creation"]}
(OUT/"v2433_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="results"},ensure_ascii=False),flush=True)
