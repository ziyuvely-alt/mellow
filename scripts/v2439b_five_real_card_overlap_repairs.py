#!/usr/bin/env python3
"""v2.4.39b repair five confirmed ornamental overlays in existing source JPGs.
Keep MellowKR outer artwork, reuse only verified existing in-frame text.
No new product photos, color swatches or reuse-rights claims.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
BASE=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-customer-drafts"
OUT=Path("v2439b-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(sz,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
plans=[
 ("pending-01","INFO_PACKAGE_02_V2414_EN_V2421.jpg",["MAGIC CUSHION","Cover Lasting formula","Magic Cushion compact"]),
 ("pending-06","INFO_03_V2413_EN_V2421.jpg",["MESH GLOW","Kill Cover Mesh Glow","Cushion compact"]),
 ("pending-09","INFO_05_OFFICIAL_V2412_EN_V2421.jpg",["5 g","Oil Control Finisher","Single product"]),
 ("pending-14","INFO_05_V2412B_EN_V2421.jpg",["70 mL","Firming Repair Cream","Single product"]),
 ("pending-23","INFO_IDENTITY_01_V2414_EN_V2421.jpg",["PORE ZERO","Oil Control Sunscreen","50 mL single product"])
]
results=[]
for gid,name,lines in plans:
 p=BASE/gid/name
 assert p.is_file(),p
 original_sha=sha(p)
 with Image.open(p) as x:
  x.load();assert x.size==(1080,1080) and x.format=="JPEG"
  im=x.convert("RGB")
  d=ImageDraw.Draw(im)
  bg=im.getpixel((30,550))
  panel=im.getpixel((550,320))
  # Original circular motif extends to x1027. Replace whole card and ring bounds.
  d.rectangle((67,296,1048,773),fill=bg)
  d.rounded_rectangle((72,303,1008,763),radius=40,fill=panel)
  for label,y,size,bold in [(lines[0],377,65,True),(lines[1],566,39,False),(lines[2],650,36,False)]:
   while size>=22 and d.textbbox((0,0),label,font=ft(size,bold))[2]>835:size-=1
   assert size>=22,(gid,label)
   font=ft(size,bold)
   bb=d.textbbox((0,0),label,font=font)
   d.text((540-(bb[2]-bb[0])//2,y),label,font=font,fill=(43,62,53))
  target=OUT/"sales-image-drafts"/gid/(gid+"_original_text_clean_card_V2439b.jpg")
  target.parent.mkdir(parents=True,exist_ok=True)
  im.save(target,"JPEG",quality=94,optimize=True)
  with Image.open(target) as qa:
   qa.load();assert qa.format=="JPEG" and qa.size==(1080,1080) and target.stat().st_size<2_000_000
  assert sha(p)==original_sha
  results.append({"group_id":gid,"source":str(p.relative_to(BASE)),
     "original_sha256":original_sha,"output":str(target.relative_to(OUT)),"new_sha256":sha(target),
     "revision":"Removed visible circle overlap from information card, retained factual original text",
     "status":"SALES_IMAGE_DRAFT","sales_release_allowed":False,
     "external_commercial_rights_verified":False,"physical_stock_version_verified":False})
report={"version":"2.4.39b","new_actual_JPG_edits":len(results),"groups_modified":len(results),
 "prior_customer_images_changed":0,"new_color_swatches":0,"public_55_urls_changed":0,
 "photo_rights_verified":0,"FINAL_QA_APPROVED":0,"results":results,
 "next":["Open each new JPG directly; reject any residual ring or text crop","Keep 30 family queue and full real image SHA from v2439",
 "Resolve 8-group exact edition swatches and commercial reuse rights before final approval"]}
(OUT/"v2439b_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k!="results"},ensure_ascii=False),flush=True)
