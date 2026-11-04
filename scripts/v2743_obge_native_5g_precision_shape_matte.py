#!/usr/bin/env python3
"""v2743 apply only a physically traced compact silhouette to genuine v2741
OBgE Oil Control Finisher 5g 997px firstparty source photo. Product color/pixels
unaltered; reject surrounding white cosmetic swatch. No previous image
re-render, no URL change or commercial use permission assumption.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
import json,base64,hashlib,math
ROOT=Path("qa-review")
SRC=ROOT/"v2741-obge-finisher-5g-firstparty-original-resolution-QA/01-MANUFACTURER-real-source-1080-QA.jpg"
OUT=ROOT/"v2743-obge-finisher-official-5g-only-precision-contour-matte"
assert SRC.is_file() and not OUT.exists()
OUT.mkdir(parents=True)
with Image.open(SRC) as origin:
 origin.load();assert origin.format=="JPEG" and origin.size==(1080,1080)
 original=origin.convert("RGB")
# These contour anchors encircle the single beige 5g compact only, not the
# white smears behind its left and right sides. Coordinates on v2741 1080.
# Closed clockwise, with rounded corners restored by interpolated spline.
anchors=[
 (404,204),(478,191),(585,191),(661,194),
 (711,208),(742,235),(762,276),(771,328),
 (760,370),(747,391),(746,445),
 (747,602),(750,742),(746,795),
 (728,825),(692,844),(635,854),(475,854),
 (397,850),(360,831),(345,799),(341,738),
 (340,581),(338,440),(333,391),
 (316,363),(313,317),(321,272),(336,238),(360,215)
]
def catmull(points, subdiv=8):
 n=len(points);vertices=[]
 for i in range(n):
  a=points[(i-1)%n];b=points[i];c=points[(i+1)%n];d=points[(i+2)%n]
  for k in range(subdiv):
   t=k/subdiv;t2=t*t;t3=t2*t
   xy=[]
   for q in (0,1):
    val=.5*((2*b[q])+(-a[q]+c[q])*t+
       (2*a[q]-5*b[q]+4*c[q]-d[q])*t2+
       (-a[q]+3*b[q]-3*c[q]+d[q])*t3)
    xy.append(int(round(val)))
   vertices.append(tuple(xy))
 return vertices
vertices=catmull(anchors)
maskhi=Image.new("L",(2160,2160),0)
draw=ImageDraw.Draw(maskhi)
draw.polygon([(2*x,2*y) for x,y in vertices],fill=255)
mask=maskhi.resize((1080,1080),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.65))
bbox=mask.getbbox()
assert bbox is not None
x0,y0,x1,y1=bbox
bw,bh=x1-x0,y1-y0
assert 370<bw<620 and 490<bh<800,(bbox,bw,bh)
rgba=original.convert("RGBA")
rgba.putalpha(mask)
product=rgba.crop(bbox)
src_sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
png=OUT/"01-official-product-5g-precision-transparent-QA.png"
product.save(png,optimize=True)
# User-required Shopee JPG asset with no low-quality square photo frame.
white=Image.new("RGB",(1080,1080),"#ffffff")
fitted=ImageOps.contain(product,(900,900),Image.Resampling.LANCZOS)
position=((1080-fitted.width)//2,(1080-fitted.height)//2)
white.paste(fitted,position,fitted)
jpg=OUT/"01-official-product-5g-white-1080-JPG-QA.jpg"
white.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
with Image.open(jpg) as verify:
 verify.load();assert verify.size==(1080,1080) and verify.format=="JPEG"
assert jpg.stat().st_size<2_000_000
# Matte on checkerboard: critical to see if bleed/white cream remains.
checker=Image.new("RGBA",(1080,1080),(255,255,255,255))
d=ImageDraw.Draw(checker)
for yy in range(0,1080,40):
 for xx in range(0,1080,40):
  if (xx//40+yy//40)%2: d.rectangle((xx,yy,xx+39,yy+39),fill=(225,225,227,255))
checker.alpha_composite(rgba)
contact=Image.new("RGB",(1670,630),"#efefee")
d=ImageDraw.Draw(contact)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(F,22)
d.text((15,11),"v2743 EXACT PRODUCT SILHOUETTE, 997px manufacturer stock source / QA ONLY",font=font,fill="#333333")
for i,item in enumerate([original,checker.convert("RGB"),white]):
 scaled=item.resize((500,500),Image.Resampling.LANCZOS)
 contact.paste(scaled,(15+i*550,58))
 d.text((15+i*550,563),["Unchanged source / white cosmetic smear","True alpha on checkerboard","JPG with white matte"][i],font=font,fill="#333333")
contact_file=OUT/"v2743-source-alpha-white-contact.jpg"
contact.save(contact_file,"JPEG",quality=84,optimize=True)
(OUT/"v2743-proof.b64.txt").write_text(base64.b64encode(contact_file.read_bytes()).decode())
manifest={
 "version":"v2743","baseline":"v2742","family":"pending-09",
 "product":"OBgE Oil Control Finisher 5g","method":"single-compact-manual-source-contour",
 "manufacturer_photo_source":"https://obgeglobal.com/cdn/shop/files/83.png?v=1776049524",
 "official_original_native_px":[997,997],
 "qa_input_source":str(SRC),"qa_input_sha256":src_sha,
 "no_original_product_photo_pixel_reconstruction":True,
 "old_v2742_two_failed_mask_JPGs_untouched":True,
 "source_actual_product_mask_bbox":[x0,y0,x1,y1],
 "original_product_pixel_area_estimate":[round(bw*997/1080),round(bh*997/1080)],
 "genuine_alpha_PNG":png.name,"1080_JPG":jpg.name,
 "png_sha256":hashlib.sha256(png.read_bytes()).hexdigest(),
 "jpg_sha256":hashlib.sha256(jpg.read_bytes()).hexdigest(),
 "JPG_bytes":jpg.stat().st_size,
 "technical_image_check":"PASS",
 "human_visual_product_border_check":"NOT_YET",
 "commercial_photo_reuse_rights_verified":False,
 "actual_owned_stock_EAN_and_5g_packaging_verified":False,
 "original_round_MK_logo_verified":False,
 "new_retail_sale_approval":False,
 "old_11_retail_approved_groups_unchanged":True,
 "old_55_published_URLs_unchanged":True,
 "final_XLSX_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2743","real_1080_cutout":True,
 "native_source_px":997,"product_bbox":[x0,y0,x1,y1],
 "JPG_bytes":jpg.stat().st_size,"sale_approved":False}))
