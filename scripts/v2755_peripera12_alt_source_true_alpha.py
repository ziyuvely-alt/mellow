#!/usr/bin/env python3
"""v2755 rescue ONLY old PERIPERA #12 Peritage Warm-gorithm via a
DIFFERENT confirmed 12-specific source (first source v2754 returned HTTP404).
Leave v2753 17 shades and v2754 #13/#14 byte-for-byte unchanged.
Commercial use not approved without user stock match and photo rights.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
from rembg import remove,new_session
import json,requests,hashlib,base64
OUT=Path("qa-review/v2755-only-peripera-12-legacy-alternate-bottle-photo")
assert not OUT.exists()
OUT.mkdir(parents=True)
SOURCES=[
 {"label":"Ktown4u original #12", "page":"https://www.ktown4u.com/iteminfo?eve_no=10399856&goods_no=96117&grp_no=10399985",
  "image":"https://www.ktown4u.com/goods_files/SH0164/goods_images/000097/GD00096117.default.6.png",
  "crop_frac":[0.19,0.08,0.71,0.87]},
 {"label":"Kiokii #12 Peritage","page":"https://kiokii.com/products/peripera-ink-mood-glowy-tint-12",
  "image":"https://kiokii.com/cdn/shop/products/peripera-ink-mood-glowy-tintperipera-524554.webp?v=1705599723",
  "crop_frac":[0.00,0.06,0.51,0.93]},
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fbold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda x,b=False:ImageFont.truetype(fbold if b else freg,x)
r={"version":"v2755","family":"pending-08","target_legacy_shade":"12",
 "legacy_exact_name":"Warm-gorithm","existing_v2753_17_alpha_pairs_unchanged":True,
 "existing_v2754_13_14_sources_and_alpha_unchanged":True,
 "first_404_source_not_retried":True,
 "output":"HOLD_NO_NEW_SOURCE","retail_approved":False,"attempts":[]}
for c in SOURCES:
 a={"label":c["label"],"source_page":c["page"],"source_url":c["image"]}
 try:
  rsp=requests.get(c["image"],timeout=17,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/webp,image/jpeg,*/*"})
  rsp.raise_for_status()
  if len(rsp.content)>7_000_000:raise ValueError("Source photo too large")
  original=Image.open(BytesIO(rsp.content));original.load()
  if min(original.size)<400:raise ValueError("Source photo too low resolution")
  rgb=ImageOps.exif_transpose(original).convert("RGB")
  raw=OUT/("12-source-"+c["label"].split()[0].lower()+".jpg")
  rgb.save(raw,"JPEG",quality=91,optimize=True)
  a.update({"downloaded":True,"dimensions":list(rgb.size),"source_sha256":hashlib.sha256(rsp.content).hexdigest(),"QA_copy":raw.name})
  # Crop only known bottle region, never mouth/lip promo panel.
  x0,y0,x1,y1=c["crop_frac"]
  crop=rgb.crop((round(x0*rgb.width),round(y0*rgb.height),round(x1*rgb.width),round(y1*rgb.height)))
  cut=remove(crop.convert("RGBA"),session=new_session("isnet-general-use"),alpha_matting=True,
             alpha_matting_foreground_threshold=230,alpha_matting_background_threshold=18,
             alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  alpha=cut.getchannel("A");bbox=alpha.getbbox()
  if bbox is None:raise ValueError("No product foreground mask")
  coverage=sum(x>=128 for x in alpha.getdata())/(alpha.width*alpha.height)
  if not(.02<coverage<.82 and bbox[2]-bbox[0]>100 and bbox[3]-bbox[1]>190):
   raise ValueError("Mask geometry failed: "+str((coverage,bbox)))
  product=cut.crop(bbox)
  png=OUT/"12-Warm-gorithm-real-old-product-alpha-QA.png"
  product.save(png,optimize=True)
  card=Image.new("RGB",(1080,1080),"white")
  draw=ImageDraw.Draw(card)
  draw.rounded_rectangle((52,53,1028,1027),radius=35,outline="#eae3e6",width=2)
  draw.text((91,95),"PERIPERA",font=ft(41,True),fill="#3b3237")
  draw.text((91,156),"Old Ink Mood Glowy Tint #12 Warm-gorithm",font=ft(25),fill="#766d72")
  large=ImageOps.contain(product,(855,773),Image.Resampling.LANCZOS)
  card.paste(large,((1080-large.width)//2,216+(774-large.height)//2),large)
  draw.text((91,990),"REAL PHOTO ALPHA  |  QA ONLY",font=ft(18),fill="#999096")
  jpg=OUT/"12-Warm-gorithm-true-alpha-1080-JPG-QA.jpg"
  card.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as im:
   im.load();assert im.size==(1080,1080) and im.format=="JPEG"
  a.update({"alpha_rendered":True,"mask_coverage":round(coverage,4),"alpha_png":png.name,
            "1080_jpg":jpg.name,"1080_jpg_sha256":sha(jpg)})
  r.update({"output":"ONE_NEW_AUTHENTIC_12_ALPHA_QA_PENDING_VISUAL",
    "source_used":c["label"],"alpha_png":png.name,"1080_jpg":jpg.name})
  r["attempts"].append(a)
  break
 except Exception as e:
  a.update({"alpha_rendered":False,"issue":str(e)[:200]})
  r["attempts"].append(a)
board=Image.new("RGB",(1350,500),"#f1f1ef")
d=ImageDraw.Draw(board)
d.text((20,17),"v2755 PERIPERA #12 ONLY: NEW REAL PHOTO vs ALPHA  |  QA NOT RETAIL",font=ft(23,True),fill="#272727")
used=next((x for x in r["attempts"] if x.get("alpha_rendered")),None)
if used:
 for f,x in [(used["QA_copy"],15),(used["1080_jpg"],910)]:
  with Image.open(OUT/f) as im:thumb=im.convert("RGB").resize((400,400),Image.Resampling.LANCZOS)
  board.paste(thumb,(x,70))
proof=OUT/"v2755-number-12-alternate-source-proof.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2755-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
r.update({"old_11_published_families_untouched":True,"verified_55_public_URLs_untouched":True,
 "no_original_source_image_mutation":True,"new_retail_approved":0,
 "commercial_redistribution_rights_verified":False,"owned_stock_packaging_verified":False,
 "no_final_XLSX_shared":True})
(OUT/"manifest.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2755","status":r["output"],
"attempted_sources":len(r["attempts"]),"source_used":r.get("source_used"),
"photo_new_cutout":bool(r.get("alpha_png")),"retail_approved":0}))
