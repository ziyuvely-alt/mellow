#!/usr/bin/env python3
"""v2716 source-switch rescue for two unprocessed/unusable real product
cutouts: GOODAL eye cream uses archived alternate detail slot02 (not failed
slot01); OBGE oil finisher uses product-only compact slot05 (not model/gift).
No logos created, previous original JPGs immutable. Try each once and save QA.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,json,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2716-obge-finisher-and-goodal-alternate-real-alpha"
assert not OUT.exists();OUT.mkdir(parents=True)
CASES=[
{"family":"pending-09","base":"v2705-three-recovered-photo-first-family-sets","slot":5,
 "brand":"OBgE","name":"Oil Control Finisher 5g","crop":(150,185,921,933)},
{"family":"pending-21","base":"v2705-three-recovered-photo-first-family-sets","slot":2,
 "brand":"GOODAL","name":"Green Tangerine Vita C Eye Cream 30mL","crop":(180,175,933,943)}
]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session('isnet-general-use')
result=[]
for spec in CASES:
 old=list((ROOT/spec["base"]/spec["family"]).glob(f'{spec["slot"]:02d}-*.jpg'))
 assert len(old)==1,(spec,old)
 src=old[0]
 with Image.open(src) as img:
  img.load()
  assert img.format=='JPEG' and img.size==(1080,1080)
  roi=img.convert('RGBA').crop(spec['crop'])
 row={"family":spec["family"],"source":str(src),"source_sha256":sha(src),
 "source_original_slot":spec["slot"],"original_crop":list(spec['crop']),
 "status":"HOLD_PENDING_VISUAL","retail_approved":False}
 try:
  alpha=remove(roi,session=session,alpha_matting=True,
   alpha_matting_foreground_threshold=230,
   alpha_matting_background_threshold=18,
   alpha_matting_erode_size=4)
  assert alpha.mode=="RGBA"
  a=alpha.getchannel('A')
  pixels=list(a.getdata())
  coverage=sum(v>=128 for v in pixels)/len(pixels)
  bbox=a.getbbox()
  assert bbox is not None
  assert .018<coverage<.83,(spec['family'],coverage)
  assert bbox[2]-bbox[0]>100 and bbox[3]-bbox[1]>170,(spec["family"],bbox)
  product=alpha.crop(bbox)
  folder=OUT/spec['family'];folder.mkdir()
  png=folder/f"{spec['slot']:02d}-actual-transparent-single-product-QA.png"
  product.save(png,optimize=True)
  jpg=folder/f"{spec['slot']:02d}-segmented-product-white-1080-QA.jpg"
  board=Image.new("RGB",(1080,1080),"#ffffff")
  d=ImageDraw.Draw(board)
  d.rounded_rectangle((52,54,1028,1027),radius=36,outline="#ede8e8",width=2)
  d.text((94,97),spec["brand"],font=font(43,True),fill="#373337")
  d.text((94,161),spec["name"],font=font(27),fill="#756a73")
  resized=ImageOps.contain(product,(850,777),Image.Resampling.LANCZOS)
  at=((1080-resized.width)//2,218+(780-resized.height)//2)
  board.paste(resized,at,resized)
  d.text((94,993),"TRUE PRODUCT PHOTO SEGMENTATION  |  QA ONLY",font=font(19),fill="#9c9398")
  board.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as verify:
   verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
  row.update({"status":"ACTUAL_ALPHA_SEGMENTED_VISUAL_QA_PENDING",
   "coverage":round(coverage,4),"bbox":list(bbox),
   "transparent_PNG":str(png.relative_to(OUT)),"JPG":str(jpg.relative_to(OUT)),
   "JPG_sha256":sha(jpg)})
 except Exception as e:
  row.update({"status":"HOLD_ALPHA_CANNOT_ISOLATE_VALID_PRODUCT",
   "error_type":type(e).__name__,"error":str(e)[:220]})
 result.append(row)
board=Image.new("RGB",(1550,1050),"#f0f0ef")
d=ImageDraw.Draw(board)
d.text((16,17),"v2716 ALTERNATE PHYSICAL STOCK PHOTOS / QA CUTOUT REVIEW",font=font(25,True),fill="#292929")
for i,row in enumerate(result):
 y=62+i*487
 with Image.open(row["source"]) as image:
  old=image.convert("RGB").resize((428,428),Image.Resampling.LANCZOS)
 board.paste(old,(18,y))
 d.text((470,y+13),row["family"],font=font(31,True),fill="#323232")
 d.text((470,y+73),row["status"],font=font(18),fill="#606060")
 if row.get("JPG"):
  with Image.open(OUT/row["JPG"]) as image:
   revised=image.convert("RGB").resize((428,428),Image.Resampling.LANCZOS)
  board.paste(revised,(1104,y))
proof=OUT/"v2716-two-alternate-sources-visual-QA.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2716-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2716","baseline":"v2715",
 "attempted_product_families":2,
 "real_new_alpha_PNG_JPG_pairs":sum(bool(x.get("JPG")) for x in result),
 "source_image_JPGs_unchanged":True,"prior_11_sale_approved_families_unchanged":True,
 "prior_55_published_image_URLs_unchanged":True,"new_sales_approved":0,
 "photo_license_verified":False,"physical_stock_generation_verified":False,
 "MK_original_logo_verified":False,"final_XLSX_shared":False,
 "products":result}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2716","families":2,"alpha_rendered":manifest["real_new_alpha_PNG_JPG_pairs"],
 "states":[x["status"] for x in result],"sale_approved":0}))
