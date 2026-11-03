#!/usr/bin/env python3
"""v2451: seven NEW actual-source product detail draft JPEGs for seven previously
uncovered families. Never rerender the 25 already completed JPEGs.
All product pixels come from historical actual source photographs; cropping/layout
only, no shade/packaging fabrication or logo recreation.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import hashlib, json, zipfile
BASE=Path("prior-v2445b")
OUT=Path("v2451-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((BASE/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
# Crop only pixels of the visually opened actual photography; promo badges excluded where possible.
# The source edition, model rights and gift set content stay on HOLD until evidence confirmed.
jobs=[
 dict(group="pending-02",slot=2,brand="MISSHA",name="Magic Cushion Moist Up",detail="Compact & Box",size="Cushion",crop=(146,70,932,831),hold="Exact shade stock and package generation unverified"),
 dict(group="pending-05",slot=3,brand="CLIO",name="Kill Cover Founwear Cushion",detail="Original Cushion Detail",size="Cushion",crop=(152,91,907,832),hold="Special set contents and exact shade edition unverified"),
 dict(group="pending-06",slot=2,brand="CLIO",name="Kill Cover Mesh Glow Essential",detail="Compact & Puff Detail",size="Cushion",crop=(457,242,743,745),hold="Special bundle GIFT claims excluded; shade/edition and reseller photo rights unverified"),
 dict(group="pending-07",slot=2,brand="CLIO",name="Kill Cover Mesh Blur Cushion",detail="Compact & Puff Detail",size="Cushion",crop=(185,438,648,760),hold="Gift package/edition not confirmed; only product section cropped"),
 dict(group="pending-10",slot=2,brand="OBgE",name="Perfect Cover Cushion",detail="Cushion & Puff Detail",size="15 g",crop=(300,258,758,662),hold="Real package source may be older generation; official shades 1/2/3 unverified"),
 dict(group="pending-21",slot=4,brand="goodal",name="Green Tangerine Vita C Eye Cream",detail="Eye Cream Tube Detail",size="30 mL",crop=(390,67,698,816),hold="Exact eye cream generation and 25AD correspondence unverified"),
 dict(group="pending-23",slot=5,brand="OBgE",name="Pore Zero Oil Control Sun Cream",detail="Original Tube Detail",size="50 mL",crop=(346,158,720,817),hold="Tube package generation and commercial source photo rights unverified")
]
results=[]
for j in jobs:
 row=next(x for x in manifest["asset_rows"] if x["family"]==j["group"] and x["slot"]==j["slot"])
 source=BASE/row["file"];assert source.is_file() and sha(source)==row["sha256"]
 with Image.open(source) as incoming:
  incoming.load();assert incoming.format=="JPEG" and incoming.size==(1080,1080)
  photo=ImageOps.contain(incoming.convert("RGB").crop(j["crop"]),(800,635),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(canvas);ink=(47,64,55);line=(178,192,182)
  d.text((68,52),j["brand"],font=font(37,True),fill=ink)
  text=j["name"];n=45
  while n>=25 and d.textbbox((0,0),text,font=font(n,True))[2]>940:n-=1
  assert n>=25
  d.text((68,117),text,font=font(n,True),fill=ink)
  d.line((68,189,1012,189),fill=line,width=2)
  canvas.paste(photo,((1080-photo.width)//2,224+(635-photo.height)//2))
  d.line((68,909,1012,909),fill=line,width=2)
  d.text((68,939),j["detail"],font=font(34,True),fill=ink)
  d.text((68,992),j["size"],font=font(29),fill=ink)
  dest=OUT/"new-real-photo-detail-JPGs"/j["group"]/(j["group"]+"_actual-photograph-detail_V2451.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2_000_000
  assert sha(source)==row["sha256"]
  results.append({"group_id":j["group"],"input_image":row["file"],"input_SHA256":row["sha256"],
  "photo_crop":list(j["crop"]),"output":str(dest.relative_to(OUT)),"output_SHA256":sha(dest),
  "photos_synthetically_generated":False,"post_render_visual_QA":"PENDING","product_generation":"PENDING",
  "photo_commercial_reuse_rights":"PENDING","MK_authentic_logo":"NOT_APPLIED","sale_approved":False,
  "hold_reason":j["hold"]})
assert len(results)==7
report={"version":"2.4.51","prior_verified_25_images":"production-assets-v2450b-25-image-candidate-checkpoint",
"actual_new_customer_detail_JPGs":7,"newly_covered_families":7,"previous_25_JPGs_regenerated":0,
"previously_untouched_source_JPGs_modified":0,"previous_public_55_URL_paths_modified":0,
"model_lookalikes_generated":0,"color_swatches_generated":0,"new_final_sale_approved_sets":0,
"no_spreadsheets_shared":True,"results":results,
"next":["Open all seven actual JPGs directly; reject blurred, mismatched or distorted crops",
      "Check logo against known MK controls, do not infer commercial rights",
      "Maintain 25 prior successful images byte-identically and handle remaining absent families",
      "Verify official exact product-generation shade charts before publishing"]}
(OUT/"v2451_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2451_seven_new_real_photo_detail_JPGs.zip","w",zipfile.ZIP_DEFLATED) as z:
 for x in results:z.write(OUT/x["output"],arcname=x["output"])
 z.write(OUT/"v2451_checkpoint.json",arcname="v2451_checkpoint.json")
with zipfile.ZipFile(OUT/"v2451_seven_new_real_photo_detail_JPGs.zip") as z:assert len(z.namelist())==8 and z.testzip() is None
print(json.dumps({"version":"v2451","new_real_photo_JPGs":len(results),"prior_25_untouched":True,"approved":0,"no_spreadsheets":True}),flush=True)
