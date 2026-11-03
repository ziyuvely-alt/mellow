#!/usr/bin/env python3
"""v2441b two additional distinct JPG corrections, not previous outputs.
Goodal 25AD false generation claim removed in a separate function card.
MISSHA serum Net Content ornamental circle removed. Both only copy-region modifications.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
SRC=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-customer-drafts"
OUT=Path("v2441b-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
jobs=[
 ("pending-13","INFO_03_V2412B_EN_V2421.jpg",["30 mL","Firming Repair Serum","Single product"],"Existing ornamental arc intersects net content card"),
 ("pending-19","INFO_FUNCTION_01_V2414B_EN_V2421.jpg",["DUAL FUNCTION","Brightening + wrinkle care","Goodal Vita C Cream Alpha"],"Existing unsupported 25AD generation label removed; retained pre-existing product function claim")
]
results=[]
for gid,filename,lines,reason in jobs:
 src=SRC/gid/filename;assert src.exists()
 prev=sha(src)
 with Image.open(src) as im0:
  im0.load();assert im0.size==(1080,1080) and im0.format=="JPEG"
  im=im0.convert("RGB")
  d=ImageDraw.Draw(im)
  bg=im.getpixel((35,540));panel=im.getpixel((540,323))
  d.rectangle((66,296,1048,775),fill=bg)
  d.rounded_rectangle((72,303,1008,763),radius=39,fill=panel)
  for label,y,n,b in [(lines[0],378,65,True),(lines[1],565,39,False),(lines[2],652,34,False)]:
   while n>22 and d.textbbox((0,0),label,font=font(n,b))[2]>838:n-=1
   assert n>=22
   ff=font(n,b);width=d.textbbox((0,0),label,font=ff)[2]
   d.text((540-width//2,y),label,font=ff,fill=(43,63,54))
  output=OUT/"sales-image-drafts"/gid/(gid+"_second_frame_fact_repair_V2441b.jpg")
  output.parent.mkdir(parents=True,exist_ok=True)
  im.save(output,"JPEG",quality=94,optimize=True)
  with Image.open(output) as x:
   x.load();assert x.format=="JPEG" and x.size==(1080,1080) and output.stat().st_size<2000000
  assert sha(src)==prev
  results.append({"group_id":gid,"source":str(src.relative_to(SRC)),"source_sha":prev,"file":str(output.relative_to(OUT)),"sha256":sha(output),"reason":reason,"state":"SALES_IMAGE_DRAFT","rights_hold":True,"stock_version_hold":True})
report={"version":"2.4.41b","new_customer_jpg":len(results),"groups":len(results),"earlier_success_recreated":0,"original_source_changed":0,"public_url_changed":0,"final_approved":0,"results":results,"remaining":["Official SKU and photograph proof required before publication","Continue other unreviewed groups","Check output visual quality and preserve rejected versions separately"]}
(OUT/"v2441b_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("results","remaining")}),flush=True)
