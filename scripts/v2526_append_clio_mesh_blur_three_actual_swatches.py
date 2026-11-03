#!/usr/bin/env python3
"""v2526 Append REAL 3-shade CLIO Mesh Blur (19C,19N,21N) JPEG from original photo pixels.
Exact image source f26b5535... (900x1006) and fixed measured crop bounds.
The previous 153 actual QA JPG bytes must be preserved byte-for-byte.
Do not confuse Mesh Blur with Mesh Glow, no synthetic swatches or public URLs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,shutil,json
BASE=Path("v2526-base-153");SRC=BASE/"review-JPG-by-family"
PHOTO=Path("v2526-original-photo/five-real-arm-swatches.jpg")
assert PHOTO.is_file() and SRC.is_dir()
assert hashlib.sha256(PHOTO.read_bytes()).hexdigest()=="f26b55356ce2443bdf4f48139160445b0c7706fe4abe65a97f46ed54041bee92"
im=Image.open(PHOTO).convert("RGB")
assert im.size==(900,1006)
O=Path("v2526-154-clio-mesh-blur-real-three-shades")
dest=O/"review-JPG-by-family"
shutil.copytree(SRC,dest)
card=Image.new("RGB",(1080,1080),"#f9f7fb")
d=ImageDraw.Draw(card)
F=lambda size:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",size)
d.text((53,64),"CLIO  |  KILL COVER MESH BLUR",font=F(36),fill="#493a62")
d.text((54,138),"REAL SHADE PHOTOS",font=F(54),fill="#43345d")
crop_bounds=[("19C",74,228),("19N",235,391),("21N",538,696)]
for i,(shade,left,right) in enumerate(crop_bounds):
 crop=im.crop((left,158,right,559)).resize((290,615),Image.Resampling.LANCZOS)
 x=49+i*345
 card.paste(crop,(x,259))
 d.text((x+70,910),shade,font=F(34),fill="#43345d")
final=dest/"pending-07/06-original-CLIO-mesh-blur-three-stock-shades.jpg"
card.save(final,"JPEG",quality=92,optimize=True,subsampling=0)
assert Image.open(final).size==(1080,1080) and final.stat().st_size<2000000
old_files=sorted(SRC.glob("pending-*/*.jpg"));new_files=sorted(dest.glob("pending-*/*.jpg"))
assert len(old_files)==153 and len(new_files)==154
for prior in old_files:
 assert prior.read_bytes()==(dest/prior.relative_to(SRC)).read_bytes()
counts={p.name:len(list(p.glob("*.jpg"))) for p in dest.glob("pending-*")}
assert len(counts)==30 and counts["pending-07"]==6
assert all(v==6 for k,v in counts.items() if k in {"pending-01","pending-04","pending-06","pending-07"})
assert all(v==5 for k,v in counts.items() if k not in {"pending-01","pending-04","pending-06","pending-07"})
for p in new_files:
 image=Image.open(p)
 assert image.format=="JPEG" and image.size==(1080,1080) and p.stat().st_size<2000000
m={"version":"v2526","date":"2026-11-04","previous_153_JPG_byte_identical":True,"new_source_file_sha256":"f26b55356ce2443bdf4f48139160445b0c7706fe4abe65a97f46ed54041bee92",
"new_JPG":str(final.relative_to(O)),"new_JPG_sha256":hashlib.sha256(final.read_bytes()).hexdigest(),
"new_JPG_bytes":final.stat().st_size,"total_QA_jpg":154,"families":30,"shade_option_names":["19C Light","19N Porcelain","21N Linen"],
"photo_source":"https://www.shegoestoseoul.com/image/catalog/PRODUCT/2025/clio/killcover-mesh-blur-cushion/clio-kill-cover-mesh-blur-cushion-23.jpg",
"crop_bounds":[{"shade":s,"box":[l,158,r,559]} for s,l,r in crop_bounds],
"no_artificial_shade_or_packaging_pixels":True,"old_55_published_URLs_unchanged":True,
"commercial_photo_rights_verified":False,"physical_owned_stock_packaging_matched":False,
"MK_logo_applied":False,"final_sales_approval":False,"new_public_URLs":0,
"excel_created_or_shared":False}
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"QA_JPG":154,"original_153_unchanged":True,"new_real_CLIO_Mesh_Blur_shades":1}))
