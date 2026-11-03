#!/usr/bin/env python3
"""v2432b: 3 real MISSHA source photo layouts from existing JPGs.
Do not invent packaging, touch product pixels, perform unsafe alpha cutout, or claim sales approval.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
BASE=Path("baseline-v2427b")/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"/"en-photo-captions"
OUT=Path("v2432b-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
items=[
 ("pending-12","SOURCE_4166c45da556_EN_V2421C.jpg","PDRN NAD+ Renew Peel Shot 25","15 mL"),
 ("pending-13","SOURCE_4d228780ef6c_EN_V2421C.jpg","PDRN NAD+ Firming Repair Serum","30 mL"),
 ("pending-14","SOURCE_5c660ccf24ce_EN_V2421C.jpg","PDRN NAD+ Firming Repair Cream","70 mL")
]
outputs=[]
for gid,filename,title,volume in items:
 src=BASE/gid/filename
 assert src.exists()
 with Image.open(src) as original:
  original.load();assert original.size==(1080,1080)
  # Exact observed photo field is x290:790, y180:680; use without erasing any
  # printed product text, preserving entire actual 500x500 image unchanged.
  field=original.convert("RGB").crop((290,180,790,680))
  # White studio field is preserved; white outer canvas removes the contrasting beige inset.
  canvas=Image.new("RGB",(1080,1080),(255,255,255));draw=ImageDraw.Draw(canvas)
  draw.text((72,61),"MISSHA",font=font(43,True),fill=(44,58,51))
  fontsize=38
  while fontsize>26 and draw.textbbox((0,0),title,font=font(fontsize,True))[2]>930:
   fontsize-=1
  draw.text((72,128),title,font=font(fontsize,True),fill=(44,58,51))
  draw.line((72,202,1008,202),fill=(181,190,182),width=2)
  # Place source field 500x500 as-is; no product resizing, stretching or AI inpainting.
  canvas.paste(field,(290,240))
  draw.line((72,861,1008,861),fill=(181,190,182),width=2)
  draw.text((72,896),volume,font=font(59,True),fill=(44,58,51))
  dest=OUT/"sales-image-drafts"/gid/(gid+"_source_photo_white_field_V2432b.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dest,"JPEG",quality=95,optimize=True)
  with Image.open(dest) as chk:
   chk.load();assert chk.size==(1080,1080) and chk.format=="JPEG" and dest.stat().st_size<2_000_000
  outputs.append({"group_id":gid,"original_sha256":sha(src),"draft_sha256":sha(dest),
                  "original":str(src),"output":str(dest.relative_to(OUT)),"size_bytes":dest.stat().st_size,
                  "exact_photo_pixels_copied":True,"cutout_performed":False,"new_status":"SALES_IMAGE_DRAFT",
                  "blocks":["COMMERCIAL_REUSE_PERMISSION_REQUIRED","STOCK_PACKAGE_VERSION_UNVERIFIED","MK_LOGO_ORIGINAL_REQUIRED"]})
cp={"version":"2.4.32b","actual_customer_JPG_drafts":len(outputs),"product_photo_replacement":0,"background_revision_by_white_field":len(outputs),
    "alpha_cutout":0,"photo_fabrication":0,"published_URL_mutations":0,"FINAL_QA_APPROVED":0,"output":outputs,
    "next":"QA visual check all 3 latest JPGs, verify stock+photo permissions; continue other families"}
(OUT/"v2432b_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="output"},ensure_ascii=False),flush=True)
