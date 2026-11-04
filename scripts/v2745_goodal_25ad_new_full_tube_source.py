#!/usr/bin/env python3
"""v2745: replace FAILED cropped GOODS original 30mL eye-cream source with
full-size SAME-PRODUCT original photo. No repeating failed v2715/v2716 images.

25AD exact 30mL product generation is corroborated by Shilla dutyfree record:
REF.NO 구청귤비타C아이크림 (25AD), SKU.NO 669210000423.
Use first-party distributor CLIO identity check, then retailer's full unit.
All photo rights and exact owned stock still held; QA outputs only.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import requests,hashlib,json,base64
from rembg import remove,new_session
OUT=Path("qa-review/v2745-goodal-eyecream-25ad-full-original-source-QA")
assert not OUT.exists();OUT.mkdir(parents=True)
TARGET="GOODAL Green Tangerine Vita C Dark Spot Care Eye Cream"
SOURCES=[
 ("clio_official_two_tubes_identity_only","https://clubclio.co.kr/data/mall_data/images/product/00/00/00/66/06/basic.gif?v=1773620319",False),
 ("sungsinsa_single_tube_product","https://sungsinsa.com/cdn/shop/files/sgms1j3k.png?v=1776305758&width=1100",True),
 ("hwahae_single_tube_product","https://img.hwahae.co.kr/products/2124760/2124760_20260305113114.jpg",True),
]
report={"version":"v2745","family":"pending-21","product":TARGET,
"verified_reference_25AD_30mL":"https://m.shilladfs.com/estore/kr/ko/p/5754369",
"shilla_reference_number":"구청귤비타C아이크림 (25AD)",
"shilla_SKU":"669210000423",
"official_CLIO_page":"https://clubclio.co.kr/shop/goodsView/0000006606",
"archived_failure_source_images_used":False,
"source_photos":[],"product_cutouts":[],"original_MK_logo_authenticated":False,
"copyright_reuse_rights_verified":False,"user_owned_stock_edition_verified":False,
"new_sale_approved":False,"approved_11_product_families_unchanged":True,
"verified_public_55_image_URLs_unchanged":True,"final_XLSX_shared":False}
H={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,image/gif,*/*"}
session=None
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda size,b=False:ImageFont.truetype(B if b else F,size)
def sha(x):return hashlib.sha256(x).hexdigest()
for source_name,url,single in SOURCES:
 row={"source":source_name,"url":url,"single_product_photo":single}
 try:
  r=requests.get(url,headers=H,timeout=19)
  r.raise_for_status()
  if len(r.content)>6500000:raise ValueError("source >6.5MB")
  with Image.open(BytesIO(r.content)) as im:
   im.load()
   native=im.size
   if min(native)<440:raise ValueError(f"Too small true source {native}")
   rgb=ImageOps.exif_transpose(im).convert("RGB")
  # Render photo reference at 1080x1080, no claims of new source sharpness.
  box=Image.new("RGB",(1080,1080),"white")
  fit=ImageOps.contain(rgb,(1030,1030),Image.Resampling.LANCZOS)
  box.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  p=OUT/(source_name+"-reference-1080-QA.jpg")
  box.save(p,"JPEG",quality=91,optimize=True,subsampling=0)
  if p.stat().st_size>=2000000:raise ValueError("JPG >2MB")
  row.update({"source_native_px":list(native),"file":p.name,
              "native_sha256":sha(r.content),"jpg_sha256":sha(p.read_bytes()),
              "JPG_bytes":p.stat().st_size,"status":"SOURCE_REFERENCE_STAGED"})
  if single and session is None:session=new_session("isnet-general-use")
  if single:
   # Two views tried, one model. Unlike prior closeup 30mL tube, original
   # photos show entire tube including metallic cap.
   try:
    cut=remove(box.convert("RGBA"),session=session,alpha_matting=True,
      alpha_matting_foreground_threshold=235,
      alpha_matting_background_threshold=15,alpha_matting_erode_size=3)
    assert cut.mode=="RGBA"
    channel=cut.getchannel("A");bbox=channel.getbbox()
    if not bbox:raise ValueError("Zero mask")
    area=sum(a>=128 for a in channel.getdata())/(cut.width*cut.height)
    if not(.04<=area<=.67 and bbox[2]-bbox[0]>=130 and bbox[3]-bbox[1]>=500):
     raise ValueError(f"Mask geometry doesn't represent full tube: ratio={area:.3f} bbox={bbox}")
    product=cut.crop(bbox)
    outdir=OUT/source_name;outdir.mkdir()
    png=outdir/"01-true-transparent-eyecream-30mL-QA.png"
    product.save(png,optimize=True)
    white=Image.new("RGB",(1080,1080),"white")
    d=ImageDraw.Draw(white)
    d.text((75,72),"GOODAL",font=ft(37,True),fill="#3f4b37")
    d.text((75,131),"Green Tangerine Vita C Eye Cream 30mL",font=ft(24),fill="#718269")
    photo=ImageOps.contain(product,(825,835),Image.Resampling.LANCZOS)
    white.paste(photo,((1080-photo.width)//2,187+(825-photo.height)//2),photo)
    jpg=outdir/"01-eyecream-full-tube-real-photo-1080-QA.jpg"
    white.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
    if jpg.stat().st_size>=2000000:raise ValueError("JPG >2MB")
    entry={"source":source_name,"original_native_px":list(native),
        "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
        "mask_bbox":list(bbox),"mask_coverage":round(area,4),
        "product_version":"25AD to be compared against user stock in hand",
        "status":"TRUE_SINGLE_TUBE_PHOTO_ALPHA_NEEDS_VISUAL_QA",
        "photo_commercial_rights_verified":False}
    report["product_cutouts"].append(entry)
   except Exception as e:
    row["cutout_failure"]=type(e).__name__+": "+str(e)[:180]
 except Exception as e:
  row["status"]="SOURCE_HOLD";row["error"]=type(e).__name__+": "+str(e)[:180]
 report["source_photos"].append(row)
canvas=Image.new("RGB",(1800,570),"#efefed")
d=ImageDraw.Draw(canvas)
d.text((16,13),"v2745 GOODAL 25AD 30mL / NEW FULL TUBE PHOTO SOURCE VS REAL CUTOUT / QA",font=ft(25,True),fill="#242424")
tiles=[]
for row in report["source_photos"]:
 if row.get("file") and row["single_product_photo"]:
  tiles.append((row["source"],OUT/row["file"]))
for item in report["product_cutouts"]:
 tiles.append((item["source"]+"_MASK",OUT/item["jpg"]))
for idx,(label,path) in enumerate(tiles[:4]):
 with Image.open(path) as im:tile=im.convert("RGB").resize((400,400),Image.Resampling.LANCZOS)
 xx=16+idx*445
 canvas.paste(tile,(xx,60))
 d.text((xx,475),label[:30],font=ft(19),fill="#333333")
proof=OUT/"v2745-full-tube-photo-alpha-contact.jpg"
canvas.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2745-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["physically_rendered_new_alpha_PNG_JPG_pairs"]=len(report["product_cutouts"])
report["status"]="FULL_SOURCE_AND_ALPHA_QA_REVIEW_PENDING" if report["product_cutouts"] else "HOLD_NO_USABLE_NEW_ALPHA"
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2745","photo_source_files":sum("file" in x for x in report["source_photos"]),
  "actual_cutouts":len(report["product_cutouts"]),"status":report["status"],"sale_approved":False}))
