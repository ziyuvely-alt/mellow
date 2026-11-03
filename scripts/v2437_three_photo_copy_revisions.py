#!/usr/bin/env python3
"""v2437: three real customer JPEG revisions based on visually opened existing product images.
- Replace incorrect DrG 'cream' claim with texture-only truthful copy and original photograph.
- OBgE Oil Control Finisher: crop exact real 5g compact image, omit unverified MK mark.
- OBgE Double Essence: crop exact real photographed bottle, omit unverified MK.
No generated product photography, no licensing approval, no overwriting published URLs.
"""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
SRC=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions"
OUT=Path("v2437-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(sz,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
items=[
{"gid":"pending-09","src":"INV_03_1859a75292_EN_V2421C.jpg","crop":(288,254,789,696),"brand":"OBgE","title":"Oil Control Finisher","size":"5 g","change":"Real compact case and puff, removes existing unauthenticated MK illustration"},
{"gid":"pending-11","src":"INV_03_8a47d85c96_EN_V2421C.jpg","crop":(446,242,632,735),"brand":"OBgE","title":"All In One Double Essence","size":"50 mL + 50 mL","change":"Real double-chamber bottle, removes existing unauthenticated MK illustration"},
{"gid":"pending-18","src":"INV_02_66493f8937_EN_V2421C.jpg","crop":(296,280,783,743),"brand":"Dr.G","title":"Brightening Up Sun Plus","size":"50 mL","change":"Removes misleading 'Official cream texture photo'; only describes real product texture photo"}
]
outputs=[]
for j in items:
 source=SRC/j["gid"]/j["src"];assert source.exists(),source
 previous=sha(source)
 with Image.open(source) as original:
  original.load();assert original.size==(1080,1080)
  photograph=original.convert("RGB").crop(j["crop"])
  photograph=ImageOps.contain(photograph,(730,630),Image.Resampling.LANCZOS)
  bg=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(bg)
  d.text((73,51),j["brand"],font=ft(38,True),fill=(43,61,53))
  size=44
  while size>=26 and d.textbbox((0,0),j["title"],font=ft(size,True))[2]>925:size-=1
  assert d.textbbox((0,0),j["title"],font=ft(size,True))[2]<=925
  d.text((73,115),j["title"],font=ft(size,True),fill=(43,61,53))
  d.line((73,191,1007,191),fill=(182,191,185),width=2)
  bg.paste(photograph,((1080-photograph.width)//2,237))
  d.line((73,906,1007,906),fill=(182,191,185),width=2)
  d.text((73,936),j["size"],font=ft(53,True),fill=(43,61,53))
  filename=f"{j['gid']}_real_photo_copy_revision_V2437.jpg"
  dest=OUT/"sales-image-drafts"/j["gid"]/filename
  dest.parent.mkdir(parents=True,exist_ok=True)
  bg.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as test:
   test.load();assert test.size==(1080,1080) and test.format=="JPEG" and dest.stat().st_size<2_000_000
  assert sha(source)==previous
  outputs.append({"group_id":j["gid"],"source":str(source),"source_sha256":previous,"output":str(dest.relative_to(OUT)),"new_sha256":sha(dest),"reason":j["change"],"state":"SALES_IMAGE_DRAFT","visual_qa_after_export":"PENDING","photo_rights":"UNVERIFIED","stock_package":"UNVERIFIED"})
checkpoint={"version":"2.4.37","actual_customer_JPG_created":3,"groups_revised":3,"original_photographs_modified":0,"synthetic_shade_or_product_pixels":0,"published_URL_mutations":0,"verified_licensing":0,"final_QA_approved":0,"latest_drafts":outputs,
"next":["Open and visually verify all three new JPGs; reject clipping and poor presentation","Continue exact-source photos across other pending product groups","Check photo commercial reuse and physical stock packaging before approval"]}
(OUT/"v2437_checkpoint.json").write_text(json.dumps(checkpoint,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in checkpoint.items() if k!="latest_drafts"},ensure_ascii=False),flush=True)
