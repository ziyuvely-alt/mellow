#!/usr/bin/env python3
"""v2764: new-source real alpha isolation for TWO previously rejected families.
No old photo, approved listing, original logo, URL, or prior QA output changed.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import new_session,remove
import hashlib,json,base64
R=Path("qa-review")
OUT=R/"v2764-two-new-original-source-real-alpha-QA"
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 {"family":"pending-01","brand":"MISSHA","label":"Magic Cushion Cover Lasting #23",
  "source":R/"v2675-missha-two-five-frame-photo-sets/pending-01/02-prior-original-byte-identical-QA.jpg",
  "crop":(25,32,1050,1000),"source_change":"Use existing #23 box+closed compact scene; old frame01 clipped the compact",
  "hold":"Only #23; shades 21/25/27 and stock generation must be independently confirmed"},
 {"family":"pending-21","brand":"GOODAL","label":"Green Tangerine Vita C Eye Cream 30mL",
  "source":R/"v2705-three-recovered-photo-first-family-sets/pending-21/01-original-source-sha-unchanged-QA.jpg",
  "crop":(560,225,944,925),"source_change":"Crop actual full yellow tube from original frame01, not failed truncated slot02",
  "hold":"25AD tube packaging and volume must match owned stock, not a gift or different edition"},
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
rows=[]
for case in CASES:
 src=case["source"];assert src.is_file(),src
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
  roi=im.convert("RGBA").crop(case["crop"])
 rec={"family":case["family"],"source":str(src),
      "source_sha256":sha(src),"source_crop_xyxy":list(case["crop"]),
      "previous_failure_avoided":case["source_change"],
      "remainder_hold":case["hold"],"status":"HOLD_NO_VALID_ALPHA",
      "retail_approved":False}
 try:
  cut=remove(roi,session=model,alpha_matting=True,
       alpha_matting_foreground_threshold=230,
       alpha_matting_background_threshold=18,
       alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  alpha=cut.getchannel("A");bbox=alpha.getbbox()
  assert bbox is not None
  fraction=sum(p>=128 for p in alpha.getdata())/(cut.width*cut.height)
  minW,minH=(280,180) if case["family"]=="pending-01" else (50,180)
  assert .015<fraction<.88 and bbox[2]-bbox[0]>=minW and bbox[3]-bbox[1]>=minH,(fraction,bbox)
  item=cut.crop(bbox)
  folder=OUT/case["family"];folder.mkdir()
  png=folder/"01-true-transparent-original-photo-QA.png"
  item.save(png,optimize=True)
  square=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(square)
  d.rounded_rectangle((52,53,1028,1027),radius=34,outline="#ede5e8",width=2)
  d.text((90,96),case["brand"],font=ft(40,True),fill="#352f34")
  size=28
  while d.textbbox((0,0),case["label"],font=ft(size))[2]>892 and size>17:size-=1
  d.text((90,162),case["label"],font=ft(size),fill="#756c72")
  resized=ImageOps.contain(item,(860,777),Image.Resampling.LANCZOS)
  pos=((1080-resized.width)//2,208+(780-resized.height)//2)
  square.paste(resized,pos,resized)
  d.text((90,996),"REAL PHOTO FOREGROUND | QA ONLY",font=ft(19),fill="#979096")
  jpg=folder/"01-clean-real-object-1080-JPG-QA.jpg"
  square.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as test:
   test.load();assert test.format=="JPEG" and test.size==(1080,1080)
  with Image.open(png) as test:
   test.load();assert test.format=="PNG" and test.mode=="RGBA"
  rec.update({"status":"ALPHA_CANDIDATE_RENDERED_REQUIRES_VISUAL_QA",
   "mask_coverage":round(fraction,4),"bbox":list(bbox),
   "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
   "jpg_sha256":sha(jpg),"source_unchanged":sha(src)==rec["source_sha256"]})
 except Exception as e:
  rec.update({"status":"HOLD_SEGMENTATION_INVALID","error":str(e)[:250],"exception":type(e).__name__})
 rows.append(rec)
board=Image.new("RGB",(1490,1000),"#efeeee")
d=ImageDraw.Draw(board)
d.text((16,15),"v2764 TWO ALTERNATE ACTUAL SOURCE PHOTOS / NO RETAIL APPROVAL",font=ft(26,True),fill="#292729")
for i,rec in enumerate(rows):
 y=60+i*460
 with Image.open(rec["source"]) as im:tile=im.convert("RGB").resize((410,410),Image.Resampling.LANCZOS)
 board.paste(tile,(16,y))
 d.text((445,y+16),rec["family"],font=ft(29,True),fill="#333333")
 d.text((445,y+74),rec["status"],font=ft(17),fill="#666666")
 if rec.get("jpg"):
  with Image.open(OUT/rec["jpg"]) as im:tile=im.convert("RGB").resize((410,410),Image.Resampling.LANCZOS)
  board.paste(tile,(1068,y))
proof=OUT/"v2764-source-vs-real-mask.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2764-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2764","baseline":"v2763",
 "new_unapproved_families_attempted":2,
 "actual_alpha_PNG_JPG_pairs_saved":sum(bool(x.get("jpg")) for x in rows),
 "old_source_photos_reencoded":0,"prior_QA_media_modified":False,
 "original_11_approved_retail_families_unchanged":True,
 "original_55_published_URLs_unchanged":True,
 "no_new_product_pixels_or_logo_generated":True,
 "commercial_rights_confirmed":False,"actual_stock_generation_confirmed":False,
 "authentic_round_MK_logo_found":False,"retail_approved":0,
 "final_XLSX_shared":False,"attempts":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2764","attempts":2,
 "real_png_jpg_pairs":manifest["actual_alpha_PNG_JPG_pairs_saved"],
 "statuses":[x["status"] for x in rows],"retail_approved":0}))
