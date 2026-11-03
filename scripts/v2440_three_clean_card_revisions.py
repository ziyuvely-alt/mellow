#!/usr/bin/env python3
"""v2440: three real visually-observed customer info card repairs, non-destructive.
The untouched historical original image and source products are never modified.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
SRC=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-customer-drafts"
OUT=Path("v2440-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
items=[
("pending-02","INFO_SUN_01_V2414B_EN_V2421.jpg",["SPF50+ / PA+++","Magic Cushion Moist Up","UV protection compact"],"ornamental circle intersects PA+++ headline"),
("pending-05","INFO_PACKAGE_01_V2414_EN_V2421.jpg",["FOUNWEAR CUSHION","Kill Cover Founwear Cushion","Cushion compact"],"ornamental circle intersects long Founwear headline; lower copy too generic"),
("pending-10","INFO_05_V2413_EN_V2421.jpg",["15 g","Perfect Cover Cushion","Select your cushion shade"],"ornament intersects information panel; retain correct product caption")
]
out=[]
for gid,name,lines,issue in items:
 p=SRC/gid/name;assert p.exists()
 old=sha(p)
 with Image.open(p) as loaded:
  loaded.load();assert loaded.format=="JPEG" and loaded.size==(1080,1080)
  im=loaded.convert("RGB")
  d=ImageDraw.Draw(im)
  bg=im.getpixel((30,530));panel=im.getpixel((540,320))
  d.rectangle((67,296,1048,774),fill=bg)
  d.rounded_rectangle((72,303,1008,763),radius=40,fill=panel)
  for txt,y,size,bold in [(lines[0],377,62,True),(lines[1],565,39,False),(lines[2],650,35,False)]:
   while size>=22 and d.textbbox((0,0),txt,font=ft(size,bold))[2]>832:size-=1
   assert size>=22
   w=d.textbbox((0,0),txt,font=ft(size,bold))[2]
   d.text((540-w//2,y),txt,font=ft(size,bold),fill=(43,62,53))
  dst=OUT/"sales-image-drafts"/gid/f"{gid}_observed_card_collision_repair_V2440.jpg"
  dst.parent.mkdir(parents=True,exist_ok=True)
  im.save(dst,"JPEG",quality=94,optimize=True)
  with Image.open(dst) as ck:
   ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and dst.stat().st_size<2_000_000
  assert sha(p)==old
  out.append({"group":gid,"original":str(p.relative_to(SRC)),"original_sha256":old,"updated":str(dst.relative_to(OUT)),"updated_sha256":sha(dst),"issue":issue,"status":"SALES_IMAGE_DRAFT","visual_review":"PENDING","rights":"HOLD","physical_stock":"HOLD"})
ck={"version":"2.4.40","edited_jpg":len(out),"edited_groups":len(out),"source_jpg_overwrites":0,"published_image_url_changes":0,"new_official_swatch_charts":0,"sales_approved":0,"edits":out,
"next":["Manually visually inspect all 3 new JPG for border/text defects","Verify exact stock package and commercial rights","Continue preserving pending-12 INCI unverified instead of rewriting ingredient claim"]}
(OUT/"v2440_checkpoint.json").write_text(json.dumps(ck,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in ck.items() if k!="edits"}))
