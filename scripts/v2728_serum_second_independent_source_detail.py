#!/usr/bin/env python3
"""v2728 Make independently photographed MISSHA PDRN NAD+ serum DETAIL frame #02,
from verified media03 (open 30mL bottle + pipette), not derivative of source04.

Preserve 11 live approved families + 55 published URLs; append QA only.
No synthetic product, color swatch, logo or unsupported skincare claims.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import json,hashlib,base64
root=Path("qa-review")
src=root/"v2696-missha-serum-official-gallery-proof/source-03-REVIEW-ONLY.jpg"
out=root/"v2728-serum-independent-pipette-product-detail-QA"
assert src.is_file() and not out.exists()
out.mkdir(parents=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(bold if b else regular,n)
rec={"version":"v2728","baseline":"v2727","family":"pending-13","role":"02_OPEN_BOTTLE_AND_PIPETTE_PRODUCT_DETAIL",
     "source_image":str(src),"source_image_sha256":digest(src),
     "source_is_independent_of_hero_source04":True,
     "retail_approved":False,
     "photo_redistribution_permission_proven":False,
     "exact_30ml_owned_stock_version_proven":False,
     "original_MK_logo_physically_available_to_renderer":False,
     "existing_11_approved_families_modified":False,
     "existing_55_public_urls_modified":False,
     "source_product_photo_original_mutated":False,
     "final_excel_shared":False,
     "status":"HOLD_TECHNICAL_OR_VISUAL_REVIEW"}
try:
 with Image.open(src) as photo:
  photo.load()
  assert photo.format=="JPEG" and photo.size==(1080,1080)
  full=photo.convert("RGBA")
 # The independent photograph contains a pipette at upper left and unsealed
 # product bottle at right; use almost full canvas, not old cropped media04.
 crop=(20,20,1050,1070)
 piece=full.crop(crop)
 rgba=remove(piece,session=new_session("isnet-general-use"),
             alpha_matting=True,
             alpha_matting_foreground_threshold=230,
             alpha_matting_background_threshold=18,
             alpha_matting_erode_size=4)
 assert rgba.mode=="RGBA"
 a=rgba.getchannel("A")
 box=a.getbbox()
 assert box is not None
 cov=sum(v>=128 for v in a.getdata())/(rgba.width*rgba.height)
 if not (.04<cov<.78 and box[2]-box[0]>=370 and box[3]-box[1]>=520):
  raise ValueError(f"not plausible product + pipette alpha: coverage={cov:.4f}; box={box}")
 h,w=rgba.height,rgba.width
 edge_fraction={
  "left":sum(a.getpixel((0,y))>=90 for y in range(h))/h,
  "right":sum(a.getpixel((w-1,y))>=90 for y in range(h))/h,
  "top":sum(a.getpixel((x,0))>=90 for x in range(w))/w,
  "bottom":sum(a.getpixel((x,h-1))>=90 for x in range(w))/w
 }
 if max(edge_fraction.values())>=.10:
  raise ValueError("photo cutout clipped source boundary: "+str(edge_fraction))
 isolated=rgba.crop(box)
 png=out/"02-real-open-bottle-and-pipette-transparent-QA.png"
 isolated.save(png,optimize=True)
 square=Image.new("RGB",(1080,1080),"#ffffff")
 d=ImageDraw.Draw(square)
 d.rounded_rectangle((51,51,1028,1030),radius=33,outline="#eee3e8",width=2)
 d.text((100,102),"MISSHA  |  PRODUCT DETAIL",font=ft(34,True),fill="#393139")
 d.text((100,162),"PDRN NAD+ Firming Repair Serum 30mL",font=ft(25),fill="#70636b")
 img=ImageOps.contain(isolated,(904,777),Image.Resampling.LANCZOS)
 square.paste(img,((1080-img.width)//2,216+(772-img.height)//2),img)
 d.text((101,985),"ORIGINAL OPEN BOTTLE & DROPPER PHOTO  |  QA ONLY",font=ft(17),fill="#9a8891")
 jpg=out/"02-real-dropper-bottle-source-photo-detail-1080-QA.jpg"
 square.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
 with Image.open(jpg) as x:
  x.load();assert x.format=="JPEG" and x.size==(1080,1080)
 assert jpg.stat().st_size<2000000
 rec.update({"status":"REAL_ALPHA_PNG_JPG_RENDERED_VISUAL_QA_PENDING",
             "alpha_png":png.name,"1080_jpg":jpg.name,
             "png_sha256":digest(png),"jpg_sha256":digest(jpg),
             "jpg_bytes":jpg.stat().st_size,
             "mask_bbox":list(box),"alpha_coverage":round(cov,4),
             "mask_edge_contact_fraction":edge_fraction})
 p=Image.new("RGB",(1160,620),"#f1eeee")
 q=ImageDraw.Draw(p)
 q.text((20,16),"v2728 DISTINCT PHOTO SCENE | REAL OPEN BOTTLE + PIPETTE",font=ft(22,True),fill="#302a30")
 with Image.open(src) as before:
  left=before.convert("RGB").resize((525,525),Image.Resampling.LANCZOS)
 with Image.open(jpg) as after:
  right=after.convert("RGB").resize((525,525),Image.Resampling.LANCZOS)
 p.paste(left,(22,55));p.paste(right,(604,55))
 q.text((22,587),"OFFICIAL ORIGINAL SOURCE 03",font=ft(17),fill="#605263")
 q.text((604,587),"NEW QA FRAME 02 | NOT RETAIL APPROVED",font=ft(16),fill="#963449")
 proof=out/"v2728-before-after-independent-frame.jpg"
 p.save(proof,"JPEG",quality=84,optimize=True)
 (out/"v2728-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
except Exception as e:
 rec.update({"status":"HOLD_ALPHA_INDEPENDENT_SOURCE_FAILED","error":str(e)[:230],
             "exception_type":type(e).__name__})
(out/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":rec["version"],"status":rec["status"],
                  "new_frame_created":int(bool(rec.get("1080_jpg"))),
                  "new_retail_approvals":0}))
