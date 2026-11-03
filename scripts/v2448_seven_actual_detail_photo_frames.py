#!/usr/bin/env python3
"""v2448: create exactly seven new factual detail photo customer drafts.
Do not recreate the eight v2447 main files, do not crop shade guide pending-03.
Every source JPEG SHA-256 verified, source product pixels unchanged other than scaling.
The visually known unlicensed MK graphic lies outside crop and is never copied.
Candidate status does not confer photo reuse authorization or stock verification.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import hashlib,json,zipfile
BASE=Path("prior-v2445b")
OUT=Path("v2448-output"); OUT.mkdir(exist_ok=True)
m=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
jobs={
 "pending-04":("CLIO","Mesh Glow Essential Cushion Mini","Cushion & Puff Detail","5 g",(255,245,865,705),"Edition and shade source pending"),
 "pending-11":("OBgE","All In One Double Essence","Dual Dispenser Detail","50 mL + 50 mL",(278,245,883,707),"Exact photographed package generation pending"),
 "pending-15":("Dr.G","Green Mild Up Sun Plus","Application Texture","50 mL",(264,320,850,704),"Source photo usage permission pending"),
 "pending-25":("BIOHEAL BOH","NAD-PRIZCELL Glow Boost Cream","Jar & Cream Detail","50 mL",(324,268,736,710),"Original MK logo excluded by crop; photo reuse pending"),
 "pending-28":("PIXEL PURE","Glow Cleansing Serum Pad","Jar & Lid Detail","210 mL / 70 Pads",(263,255,809,739),"Photo reuse pending"),
 "pending-29":("PIXEL PURE","Radiance Aqua Soothing Cream","Jar Detail","50 mL",(310,305,810,710),"Photo reuse pending"),
 "pending-30":("PIXEL PURE","Aura Radiance Serum","Serum Texture Detail","50 mL",(263,267,844,677),"Photo reuse pending")
}
results=[]
for gid,(brand,name,header,unit,crop,risk) in jobs.items():
 row=next(x for x in m["asset_rows"] if x["family"]==gid and x["slot"]==2)
 path=BASE/row["file"];assert path.is_file() and sha(path)==row["sha256"]
 with Image.open(path) as img:
  img.load();assert img.format=="JPEG" and img.size==(1080,1080)
  source=img.convert("RGB")
  product=source.crop(crop)
  # Never generate, redraw or inpaint product pixels. Keep entire selected image region.
  scaled=ImageOps.contain(product,(860,618),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),(255,255,255))
  draw=ImageDraw.Draw(canvas)
  ink=(42,66,56)
  draw.text((68,54),brand,font=font(38,True),fill=ink)
  n=44
  while n>=27 and draw.textbbox((0,0),name,font=font(n,True))[2]>942:n-=1
  assert n>=27
  draw.text((68,120),name,font=font(n,True),fill=ink)
  draw.line((68,193,1012,193),fill=(174,189,179),width=2)
  x=(1080-scaled.width)//2
  y=234+(618-scaled.height)//2
  canvas.paste(scaled,(x,y))
  draw.line((68,907,1012,907),fill=(174,189,179),width=2)
  draw.text((68,934),header,font=font(33,True),fill=ink)
  draw.text((68,990),unit,font=font(31),fill=ink)
  dest=OUT/"new-source-backed-detail-JPGs"/gid/(gid+"_genuine-photo-detail-noMK_V2448.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2_000_000
  assert sha(path)==row["sha256"]
  results.append({"group_id":gid,"source":row["file"],"source_sha256":row["sha256"],
    "new_JPG":str(dest.relative_to(OUT)),"new_sha256":sha(dest),
    "crop_xyxy":list(crop),"reuse":"Original photographic pixels are cropped/rescaled, not synthesized",
    "MK_logo_source_region_excluded":True,"post_render_manual_visual_QA":"PENDING",
    "official_source_edition_verified":False,"photo_license_verified":False,
    "physical_stock_verified":False,"sales_approved":False,"remaining":risk})
report={"version":"2.4.48","previous":"production-assets-v2447b-eight-main-image-MK-QA",
 "new_factual_detail_JPG_count":len(results),"groups":len(results),
 "previous_eight_main_JPG_regenerated":0,
 "pending03_MISSHA_unverified_swatch_cropped":False,
 "new_color_swatches":0,"original_531_source_JPGs_modified":0,
 "older_55_public_URLs_modified":0,"FINAL_SALES_APPROVED":0,
 "all_photographic_pixels_from_existing_JPGs":True,
 "new_frame_results":results,
 "next":["Visually open seven new JPGs, reject any accidental crop of wrong edition/photo",
         "Compare every candidate against four exact known MK watermark controls, don't call them approved",
         "Continue another batch only if verified source photo is available; don't duplicate images"]}
(OUT/"v2448_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2448_seven_actual_photo_detail_JPGs.zip","w",zipfile.ZIP_DEFLATED) as z:
 for row in results:z.write(OUT/row["new_JPG"],arcname=row["new_JPG"])
 z.write(OUT/"v2448_checkpoint.json",arcname="v2448_checkpoint.json")
with zipfile.ZipFile(OUT/"v2448_seven_actual_photo_detail_JPGs.zip") as z:assert len(z.namelist())==8 and z.testzip() is None
print(json.dumps({"version":"v2448","new_JPG":len(results),"previous_8_recreated":0,"sale_approved":0}))
