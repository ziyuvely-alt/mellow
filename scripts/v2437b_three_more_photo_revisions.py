#!/usr/bin/env python3
"""v2437b: update three visibly inspected real customer frames while avoiding unverifiable 'official' claims.
Photographic regions are copied from actual historical JPGs and unverified MK badge is excluded via crop.
"""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
BASE=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions"
OUT=Path("v2437b-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
items=[
 ("pending-15","INV_03_8d52f556bc_EN_V2421C.jpg",(355,236,720,766),"Dr.G","Green Mild Up Sun Plus","50 mL","Whole photographed tube, no MK mark, stock edition not verified"),
 ("pending-18","INV_04_e3df9b823a_EN_V2421C.jpg",(282,245,803,771),"Dr.G","Brightening Up Sun Plus","50 mL","Remove unverified official model photo claim; existing application photo retained"),
 ("pending-11","INV_04_a0c9d28d19_EN_V2421C.jpg",(270,256,880,746),"OBgE","All In One Double Essence","50 mL + 50 mL","Remove unverified official texture photograph claim; existing texture photograph retained")
]
entries=[]
for gid,name,box,brand,product,amount,reason in items:
 src=BASE/gid/name;assert src.exists()
 origsha=sha(src)
 with Image.open(src) as original:
  original.load();assert original.size==(1080,1080)
  photo=ImageOps.contain(original.convert("RGB").crop(box),(790,645),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(canvas)
  d.text((70,52),brand,font=f(38,True),fill=(45,63,54))
  size=43
  while size>=26 and d.textbbox((0,0),product,font=f(size,True))[2]>938:size-=1
  assert d.textbbox((0,0),product,font=f(size,True))[2]<=938
  d.text((70,113),product,font=f(size,True),fill=(45,63,54))
  d.line((70,192,1010,192),fill=(185,193,187),width=2)
  canvas.paste(photo,((1080-photo.width)//2,234))
  d.line((70,908,1010,908),fill=(185,193,187),width=2)
  d.text((70,944),amount,font=f(48,True),fill=(45,63,54))
  dst=OUT/"sales-image-drafts"/gid/(gid+"_actual_photo_copy_revised_V2437b.jpg")
  dst.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dst,"JPEG",quality=94,optimize=True)
  with Image.open(dst) as check:
   check.load()
   assert check.format=="JPEG" and check.size==(1080,1080) and dst.stat().st_size<2_000_000
  assert sha(src)==origsha
  entries.append({"group_id":gid,"source":str(src.relative_to(BASE)),"source_sha256":origsha,"new_jpg":str(dst.relative_to(OUT)),"new_sha256":sha(dst),"reason":reason,"status":"SALES_IMAGE_DRAFT","commercial_photo_rights":"UNVERIFIED","stock_package":"UNVERIFIED","visual_QA":"PENDING"})
cp={"version":"2.4.37b","created_real_draft_JPG":len(entries),"families":len(entries),
"source_photo_generations":0,"original_photos_changed":0,"public_URL_changes":0,
"official_shade_charts_new":0,"FINAL_QA_APPROVED":0,"outputs":entries,
"next":["Open all three actual JPGs and reject bad crops","Do not claim official source or rights without written proof","Carry latest v2437 and v2437b revisions into consolidated checkpoint"]}
(OUT/"v2437b_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="outputs"},ensure_ascii=False),flush=True)
