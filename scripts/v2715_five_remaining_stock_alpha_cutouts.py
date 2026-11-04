#!/usr/bin/env python3
"""v2715 genuine alpha-masked product hero QA, remaining 5 never-segmented product
families. Sources: existing archived authentic 1080 JPGs. No fictional pixels,
original logos, false shade swatches, or approved product overwrites.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import base64,hashlib,json
ROOT=Path("qa-review")
OUT=ROOT/"v2715-five-more-original-product-real-alpha-hero-tests"
assert not OUT.exists();OUT.mkdir(parents=True)
SPECS=[
 ("pending-03","v2705-three-recovered-photo-first-family-sets","MISSHA","M Perfect Cover BB Cream 50mL | 23 Natural Beige",(235,190,873,965)),
 ("pending-11","v2706-six-archival-five-real-source-families","OBgE","All In One Double Essence | Dual-Chamber Bottle",(235,180,857,971)),
 ("pending-15","v2706-six-archival-five-real-source-families","Dr.G","Green Mild Up Sun Plus 50mL",(215,190,867,957)),
 ("pending-18","v2706-six-archival-five-real-source-families","Dr.G","Brightening Up Sun Plus 50mL",(210,190,873,965)),
 ("pending-21","v2705-three-recovered-photo-first-family-sets","GOODAL","Green Tangerine Vita C Eye Cream 30mL",(230,185,867,970)),
]
FREG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FBOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(size,bold=False):return ImageFont.truetype(FBOLD if bold else FREG,size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
rows=[]
for fid,folder,brand,desc,xyxy in SPECS:
 old=list((ROOT/folder/fid).glob('01-*.jpg'))
 assert len(old)==1,(fid,old)
 path=old[0]
 with Image.open(path) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  crop=im.convert("RGBA").crop(xyxy)
 info={"family":fid,"source":str(path),"source_sha256":sha(path),
   "used_original_crop":list(xyxy),"model":"isnet-general-use",
   "status":"HOLD_ORIGINAL_PHOTO_CANDIDATE","retail_approved":False}
 try:
  cut=remove(crop,session=session,alpha_matting=True,
     alpha_matting_foreground_threshold=230,alpha_matting_background_threshold=18,
     alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  mask=cut.getchannel("A")
  bbox=mask.getbbox()
  assert bbox is not None
  coverage=sum(v>=128 for v in mask.getdata())/(cut.width*cut.height)
  assert .025<=coverage<=.82,(fid,coverage,bbox)
  assert bbox[2]-bbox[0]>=130 and bbox[3]-bbox[1]>=220,(fid,bbox)
  pure=cut.crop(bbox)
  destdir=OUT/fid;destdir.mkdir()
  outpng=destdir/"01-real-alpha-product-only-QA.png"
  pure.save(outpng,optimize=True)
  board=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(board)
  d.rounded_rectangle((55,54,1025,1027),radius=36,outline="#e9e4e5",width=2)
  d.text((97,93),brand,font=ft(41,True),fill="#333136")
  size=27
  while d.textbbox((0,0),desc,font=ft(size))[2]>887 and size>16:size-=1
  d.text((97,161),desc,font=ft(size),fill="#777077")
  im=ImageOps.contain(pure,(850,775),Image.Resampling.LANCZOS)
  where=((1080-im.width)//2,219+(772-im.height)//2)
  board.paste(im,where,im)
  d.text((97,989),"ACTUAL PHOTOGRAPHIC CUTOUT  |  QA ONLY",font=ft(19),fill="#978d90")
  outjpg=destdir/"01-real-cutout-white-hero-1080-QA.jpg"
  board.save(outjpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert outjpg.stat().st_size<2000000
  with Image.open(outjpg) as check:assert check.format=="JPEG" and check.size==(1080,1080)
  info.update({"status":"REAL_ALPHA_CUTOUT_RENDERED_NEEDS_VISUAL_REVIEW",
       "alpha_coverage":round(coverage,4),"bbox":list(bbox),
       "alpha_png":str(outpng.relative_to(OUT)),"square_jpg":str(outjpg.relative_to(OUT)),
       "square_jpg_sha256":sha(outjpg)})
 except Exception as e:
  info.update({"status":"HOLD_MASK_REJECTED","exception_type":type(e).__name__,"error":str(e)[:220]})
 rows.append(info)
for pg in range(2):
 sub=rows[pg*3:(pg+1)*3]
 if not sub:continue
 board=Image.new("RGB",(1520,60+480*len(sub)),"#f0f0ee")
 draw=ImageDraw.Draw(board)
 draw.text((18,12),f"v2715 ORIGINAL -> REAL SEGMENTED CUTOUT / PAGE {pg+1} / QA ONLY",font=ft(26,True),fill="#282828")
 for i,item in enumerate(sub):
  y=60+i*480
  with Image.open(item["source"]) as im:
   original=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
  board.paste(original,(20,y))
  draw.text((454,y+15),item["family"],font=ft(31,True),fill="#2d2d2d")
  draw.text((454,y+75),item["status"],font=ft(17),fill="#686868")
  if item.get("square_jpg"):
   with Image.open(OUT/item["square_jpg"]) as im:
    new=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
   board.paste(new,(1080,y))
 dest=OUT/f"v2715-contact-page-{pg+1}.jpg"
 board.save(dest,"JPEG",quality=83,optimize=True)
 (OUT/f"v2715-contact-page-{pg+1}.b64.txt").write_text(base64.b64encode(dest.read_bytes()).decode())
summary={"version":"v2715","baseline":"v2714","attempted_new_families":len(rows),
 "successful_true_alpha_png_JPG_pairs":sum(bool(x.get("square_jpg")) for x in rows),
 "original_JPGs_modified":0,"published_11_product_families_modified":0,
 "verified_public_55_urls_modified":0,"retail_approved":0,
 "stock_item_generation_verification":False,"photo_use_rights_verified":False,
 "original_MK_badge_verified":False,"final_excel_shared":False,
 "products":rows}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"tested":len(rows),"real_alpha_cutouts":summary["successful_true_alpha_png_JPG_pairs"],
"retail_approved":0,"status":[x["status"] for x in rows]}))
