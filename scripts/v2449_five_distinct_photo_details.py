#!/usr/bin/env python3
"""v2449: Five source-backed customer-photo detail drafts, zero repeated prior outputs.
Historical originals are immutable. No commercial rights or stock approval.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,zipfile
BASE=Path("prior-v2445b")
OUT=Path("v2449-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
jobs=[
 ("pending-09","OBgE","Oil Control Finisher","Compact In Use","5 g",(212,299,638,627),"Model-image commercial permission unverified"),
 ("pending-16","Dr.G","R.E.D Blemish Clear Soothing Cream","Jar In Hand","70 mL",(339,290,731,667),"Model-image commercial permission unverified"),
 ("pending-18","Dr.G","Brightening Up Sun Plus","Tube Back Detail","50 mL",(275,290,807,695),"Exact original package generation unverified"),
 ("pending-24","BIOHEAL BOH","NAD-PRIZCELL Glow Power Serum","Original Serum Bottle","30 mL",(374,278,707,712),"Real source package photo permission unverified"),
 ("pending-27","PIXEL PURE","Soothing Ampoule Toner","Fluid Texture Detail","200 mL",(224,276,875,715),"Volume and formula of exact photographed edition unverified")
]
out=[]
for gid,brand,name,caption,vol,crop,risk in jobs:
 old=next(r for r in manifest["asset_rows"] if r["family"]==gid and r["slot"]==2)
 src=BASE/old["file"];assert src.is_file() and sha(src)==old["sha256"]
 with Image.open(src) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  photo=ImageOps.contain(im.convert("RGB").crop(crop),(820,626),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(canvas);ink=(43,64,56)
  d.text((66,52),brand,font=ft(38,True),fill=ink)
  n=43
  while n>=26 and d.textbbox((0,0),name,font=ft(n,True))[2]>946:n-=1
  assert n>=26
  d.text((66,118),name,font=ft(n,True),fill=ink)
  d.line((66,191,1014,191),fill=(179,189,183),width=2)
  canvas.paste(photo,((1080-photo.width)//2,234+(626-photo.height)//2))
  d.line((66,907,1014,907),fill=(179,189,183),width=2)
  d.text((66,938),caption,font=ft(35,True),fill=ink)
  d.text((66,989),vol,font=ft(30),fill=ink)
  dest=OUT/"new-photo-detail-JPGs"/gid/f"{gid}_original-photo-detail_V2449.jpg"
  dest.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2_000_000
  assert sha(src)==old["sha256"]
  out.append({"group_id":gid,"source_file":old["file"],"source_sha256":old["sha256"],
   "output":str(dest.relative_to(OUT)),"output_sha256":sha(dest),"crop_xyxy":list(crop),
   "risk":risk,"new_fake_product_pixels":False,"status":"SALES_IMAGE_DRAFT",
   "commercial_photo_rights_verified":False,"stock_package_verified":False,"visual_QA":"PENDING"})
assert len(out)==5
manifest={"version":"2.4.49","previous_checkpoint":"production-assets-v2448b-15-photo-candidate-checkpoint",
 "new_real_photo_detail_JPG":5,"new_groups":5,"prior_15_JPGs_unchanged":True,
 "pending22_blurry_photo":"HELD_NO_RETOUCH","old_531_JPGs_overwritten":0,
 "published_55_URLs_modified":0,"official_shade_charts_approved":0,
 "FINAL_SALES_APPROVED":0,"files":out,
 "next":"Directly inspect five rendered JPGs and exclude any unsuitable crop; further product-shade and commercial rights QA"}
(OUT/"v2449_checkpoint.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2449_5_actual_photo_detail_candidates.zip","w",zipfile.ZIP_DEFLATED) as z:
 for x in out:z.write(OUT/x["output"],arcname=x["output"])
 z.write(OUT/"v2449_checkpoint.json",arcname="v2449_checkpoint.json")
with zipfile.ZipFile(OUT/"v2449_5_actual_photo_detail_candidates.zip") as z:
 assert len(z.namelist())==6 and z.testzip() is None
print(json.dumps({"version":"2.4.49","images":5,"approved":0,"no_spreadsheet":True}),flush=True)
