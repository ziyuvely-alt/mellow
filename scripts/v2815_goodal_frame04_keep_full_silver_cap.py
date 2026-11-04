#!/usr/bin/env python3
"""v2815: change ONLY misleading/detail-clipped 04 JPG from v2814.
Frame 04 now includes the actual 2026 tube's front text AND whole silver cap.
All other four frame bytes and alpha PNG are preserved identically.
The real source image is not redrawn. Consumer-facing publication remains HOLD.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import shutil,hashlib,json,base64
ROOT=Path("qa-review")
PREV=ROOT/"v2814-goodal-25ad-renewal-tube-five-photo-first-JPG-QA"
SRC=ROOT/"v2813-goodal-renewal-25AD-tube-genuine-source-alpha"
OUT=ROOT/"v2815-goodal-25ad-five-photo-set-silver-cap-crop-fixed"
assert PREV.is_dir() and SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((PREV/"manifest.json").read_text())
rows=[]
for item in j["frames"]:
 item=dict(item);slot=item["slot"]
 if slot!=4:
  old=PREV/item["file"]
  target=OUT/old.name
  shutil.copy2(old,target)
  assert sha(target)==sha(old)
  item.update({"copied_prior_sha_identical":True,"prior_frame_source":str(old)})
 else:
  source=SRC/"02-2026-hikoco-tube-photo-1080-QA.jpg"
  assert source.is_file()
  with Image.open(source) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   rgb=im.convert("RGB")
  # The full metallic cap reaches the photo's lower edge: don't cut at y790.
  # This crop keeps cap, top seal, product label; shows honest detail from same image.
  region=[355,70,730,1050]
  crop=rgb.crop(tuple(region))
  canvas=Image.new("RGB",(1080,1080),"white")
  fit=ImageOps.contain(crop,(1010,1025),Image.Resampling.LANCZOS)
  canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  target=OUT/"04-real-tube-front-and-silver-cap-full-detail-QA.jpg"
  canvas.save(target,"JPEG",quality=94,optimize=True,subsampling=0)
  item.update({"file":target.name,"role":"2026_TUBE_FRONT_LABEL_AND_SILVER_CAP_DETAIL",
   "source":str(source),"source_sha256":sha(source),
   "composition_kind":"REAL_PHOTOGRAPH_CROP_NO_NEW_PRODUCT_PIXELS",
   "crop_xyxy_source_1080":region,"description":"Genuine 2026 renewal tube front with silver cap visibly retained; same source photo as frame03.",
   "prior_frame_replaced":True,"prior_bad_frame":"04-real-tube-label-and-silver-cap-detail-QA.jpg"})
 with Image.open(target) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert target.stat().st_size<2_000_000
 item["jpg_sha256"]=sha(target);item["jpg_bytes"]=target.stat().st_size
 rows.append(item)
assert len(rows)==5 and len({x["jpg_sha256"] for x in rows})==5
for alpha in PREV.glob("*.png"):
 out=OUT/alpha.name
 shutil.copy2(alpha,out)
 assert sha(out)==sha(alpha)
# Actual photograph contact sheet to verify the metallic bottom is preserved.
board=Image.new("RGB",(1840,680),"#f1f0ef")
d=ImageDraw.Draw(board)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
d.text((16,10),"v2815 FIVE REAL PHOTO-BASED JPGs / EXACTLY FRAME04 CHANGED / QA HOLD",font=font,fill="#303030")
for i,item in enumerate(rows):
 with Image.open(OUT/item["file"]) as img:
  thumb=img.convert("RGB").resize((345,345),Image.Resampling.LANCZOS)
 x=16+i*364
 board.paste(thumb,(x,51))
 d.text((x,410),f"{item['slot']:02d} "+("CAP FULLY INCLUDED" if item["slot"]==4 else "SAME SOURCE BYTES"),font=font,fill="#303030")
d.text((16,506),"Only v2814 frame 04 source crop corrected to show the genuine 2026 yellow tube and entire silver cap.",font=font,fill="#404040")
d.text((16,552),"No 25AD stock edition, license, or authorized MK mark verified. No sales approval or URL changes.",font=font,fill="#404040")
proof=OUT/"v2815-fiveframe-full-cap-visual-QA.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2815-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode("ascii"))
m={
 "version":"v2815","baseline":"v2814","family":"pending-21",
 "frames_actual_JPGs":len(rows),"corrected_frame_04_only":True,
 "unchanged_previous_frames_sha_identical":[1,2,3,5],
 "original_transparent_png_sha_identical":True,
 "source_reused":"qa-review/v2813-goodal-renewal-25AD-tube-genuine-source-alpha/02-2026-hikoco-tube-photo-1080-QA.jpg",
 "photo_source_count_independent":2,"not_four_five_new_shoots":True,
 "actual_stock_generation_unverified":True,"commercial_photo_use_permission_unverified":True,
 "original_MK_logo_unverified":True,
 "sale_approved":False,"approved_previous_11_groups_unchanged":True,
 "public_previous_55_URLs_unchanged":True,"prior_v2814_files_unchanged":True,
 "final_excel_shared":False,"frames":rows}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2815","total_JPGs":5,"newly_corrected":1,
 "prior_JPGs_byte_identical":4,"retail_approval":0}))
