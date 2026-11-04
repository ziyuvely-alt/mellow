#!/usr/bin/env python3
"""v2721 actual alpha product-only segmentation on two never-segmented archive
families, independent of former kit/group failures. Source JPG unchanged.
Reject wrong packaging or photo permissions at sales gate.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,base64,json
ROOT=Path("qa-review")
OUT=ROOT/"v2721-three-drg-goodal-alpha-photo-QA"
assert not OUT.exists();OUT.mkdir(parents=True)
SPECS=[
 {"fid":"pending-17","folder":"v2672-two-five-JPG-real-scene-sets",
  "brand":"Dr.G","name":"Brightening Up Moisture Sun 50mL","size":"Exact formula / package generation HOLD",
  "source_slot":3,"crop":(145,112,954,968)},
 {"fid":"pending-20","folder":"v2672-two-five-JPG-real-scene-sets",
  "brand":"GOODAL","name":"Green Tangerine Vita C Serum Mist 100mL","size":"Exact stock 100mL HOLD",
  "source_slot":2,"crop":(132,98,953,965)},
 {"fid":"pending-19","folder":"v2673-two-new-product-five-JPG-sets",
  "brand":"GOODAL","name":"Green Tangerine Vita C Cream Alpha 50mL","size":"Actual 50mL alpha cream and packaging HOLD",
  "source_slot":1,"crop":(105,112,973,963)}
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
result=[]
for q in SPECS:
  folder=ROOT/q["folder"]
  sources=list((folder/q["fid"]).glob(f"{q['source_slot']:02d}-*.jpg")) if (folder/q["fid"]).is_dir() else list(folder.glob("01-*.jpg"))
  assert len(sources)==1,(q["fid"],[str(x) for x in sources])
  src=sources[0]
  with Image.open(src) as photo:
    photo.load();assert photo.format=="JPEG" and photo.size==(1080,1080)
    clipped=photo.convert("RGBA").crop(q["crop"])
  x={"family":q["fid"],"product":q["name"],"original_source":str(src),
     "original_sha256":sha(src),"cropped_region":list(q["crop"]),
     "product_edition_hold":q["size"],"retail_approved":False,
     "status":"REQUIRES_VISUAL_FOREGROUND_QA"}
  try:
    alpha=remove(clipped,session=session,alpha_matting=True,
      alpha_matting_foreground_threshold=230,
      alpha_matting_background_threshold=18,
      alpha_matting_erode_size=4)
    assert alpha.mode=="RGBA"
    a=alpha.getchannel("A");bbox=a.getbbox()
    assert bbox
    fraction=sum(y>=128 for y in a.getdata())/(alpha.width*alpha.height)
    assert .03<fraction<.80 and bbox[2]-bbox[0]>120 and bbox[3]-bbox[1]>170,(fraction,bbox)
    item=alpha.crop(bbox)
    dest=OUT/q["fid"];dest.mkdir()
    png=dest/"01-real-transparent-product-QA.png"
    item.save(png,optimize=True)
    jpg=dest/"01-real-product-hero-1080-QA.jpg"
    board=Image.new("RGB",(1080,1080),"white")
    d=ImageDraw.Draw(board)
    d.rounded_rectangle((54,54,1026,1026),radius=32,outline="#ebe5e6",width=2)
    d.text((95,101),q["brand"],font=ft(40,True),fill="#343038")
    font_size=29
    while d.textbbox((0,0),q["name"],font=ft(font_size))[2]>886 and font_size>18:font_size-=1
    d.text((95,165),q["name"],font=ft(font_size),fill="#756d74")
    contain=ImageOps.contain(item,(855,770),Image.Resampling.LANCZOS)
    location=((1080-contain.width)//2,218+(780-contain.height)//2)
    board.paste(contain,location,contain)
    d.text((95,990),"ACTUAL PHOTOGRAPHIC PRODUCT CUTOUT  |  QA ONLY",font=ft(18),fill="#948e92")
    board.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
    with Image.open(jpg) as check:
      check.load();assert check.format=="JPEG" and check.size==(1080,1080)
    assert jpg.stat().st_size<2_000_000
    x.update({"status":"REAL_ALPHA_PNG_JPG_RENDERED_NEEDS_VISUAL_QA",
      "alpha_coverage":round(fraction,4),"bbox":list(bbox),
      "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
      "jpg_sha256":sha(jpg)})
  except Exception as e:
    x.update({"status":"HOLD_ALPHA_FAILED","error_type":type(e).__name__,"error":str(e)[:200]})
  result.append(x)
board=Image.new("RGB",(1560,1545),"#f0f0ef")
d=ImageDraw.Draw(board)
d.text((16,15),"v2721 THREE NEW EXACT-ITEM REAL SOURCE CUTOUTS / QA ONLY",font=ft(25,True),fill="#292929")
for ix,row in enumerate(result):
  yy=60+ix*487
  with Image.open(row["original_source"]) as p:
    old=p.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
  board.paste(old,(16,yy))
  d.text((468,yy+16),row["family"],font=ft(30,True),fill="#282828")
  d.text((468,yy+74),row["status"],font=ft(17),fill="#666")
  if row.get("jpg"):
    with Image.open(OUT/row["jpg"]) as p:
      new=p.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
    board.paste(new,(1115,yy))
proof=OUT/"v2721-original-vs-real-cutout.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2721-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2721","baseline":"v2719",
"new_product_families_attempted":3,
"real_alpha_png_jpg_pairs_saved":sum(bool(x.get("jpg")) for x in result),
"new_retail_approvals":0,
"commercial_photo_rights_verified":False,"physical_stock_edition_verified":False,
"approved_MK_logo_verified":False,"original_photos_modified":False,
"prior_11_approved_groups_modified":False,"prior_55_public_urls_modified":False,
"final_xlsx_shared":False,"products":result}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"family_count":3,"actual_JPG_PNG_pairs":manifest["real_alpha_png_jpg_pairs_saved"],
 "statuses":[x["status"] for x in result],"retail_approved":0}))
