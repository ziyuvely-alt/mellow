#!/usr/bin/env python3
"""v2765 remove ONLY the narrow erroneous alpha-mask tail from previously
generated pending-21 GOODAL 30mL full-tube PNG, if provably nonproduct.
Reuse previous transparency, never rerun segmentation or fake product pixels.
Original JPGs, PNGs, 11 approved groups and 55 public links remain untouched.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,json,hashlib,base64
ROOT=Path("qa-review")
SOURCE=ROOT/"v2764-two-new-original-source-real-alpha-QA/pending-21/01-true-transparent-original-photo-QA.png"
OUT=ROOT/"v2765-goodal-eye-cream30-remove-narrow-false-tail-QA"
assert SOURCE.is_file() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_sha=sha(SOURCE)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
with Image.open(SOURCE) as image:
 image.load()
 assert image.format=="PNG" and image.mode=="RGBA"
 rgba=image.copy()
w,h=rgba.size
alpha=np.asarray(rgba.getchannel("A"))
counts=np.count_nonzero(alpha>=128,axis=1)
body_w=int(np.median(counts[int(h*.30):int(h*.72)]))
tail_threshold=max(8,int(body_w*.23))
rows_info=[{"row":int(y),"width":int(counts[y])} for y in range(int(h*.65),h,12)]
# Distinguish tail from real silver cap: require a long continuous narrow region
# at bottom. A legitimate product body/cap cannot be auto-removed if ambiguity.
last=int(np.max(np.where(counts>0)[0]))
start=last
while start>=int(h*.57) and int(counts[start])<=tail_threshold:
 start-=1
tail_start=start+1
tail_length=last-tail_start+1
rec={"version":"v2765","family":"pending-21","source_png":str(SOURCE),
 "source_png_sha256":original_sha,"width":w,"height":h,
 "body_median_alpha_width":body_w,"tail_width_threshold":tail_threshold,
 "detected_tail_start":tail_start,"tail_last":last,"detected_tail_length":tail_length,
 "sampled_tail_row_widths":rows_info,"status":"HOLD_UNSAFE_OR_UNDETECTED",
 "retail_approved":False}
try:
 assert body_w>=30,(body_w,w)
 assert tail_length>=22 and tail_start>=int(h*.59),(tail_start,tail_length)
 # Ensure preceding row was broad, not an equally thin genuine cap.
 assert int(counts[tail_start-1])>tail_threshold,(counts[tail_start-1],tail_threshold)
 fixed=rgba.copy()
 mask=np.array(fixed.getchannel("A"))
 mask[tail_start:,:]=0
 fixed.putalpha(Image.fromarray(mask,"L"))
 bbox=fixed.getchannel("A").getbbox()
 assert bbox is not None and bbox[3]<=tail_start
 fixed=fixed.crop(bbox)
 png=OUT/"01-goodal30-full-tube-with-erroneous-mask-tail-removed-QA.png"
 fixed.save(png,optimize=True)
 with Image.open(png) as v:
  assert v.format=="PNG" and v.mode=="RGBA"
 JPG=OUT/"01-goodal30-full-tube-1080-clean-QA.jpg"
 surface=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(surface)
 d.rounded_rectangle((54,54,1026,1026),radius=33,outline="#e9e5e8",width=2)
 d.text((93,102),"GOODAL",font=font(43,True),fill="#373234")
 d.text((93,168),"Green Tangerine Vita C Eye Cream 30mL",font=font(25),fill="#746c75")
 fit=ImageOps.contain(fixed,(850,777),Image.Resampling.LANCZOS)
 surface.paste(fit,((1080-fit.width)//2,210+(777-fit.height)//2),fit)
 d.text((93,996),"EXISTING SOURCE PHOTO MASK REPAIR | QA ONLY",font=font(18),fill="#969096")
 surface.save(JPG,"JPEG",quality=92,optimize=True,subsampling=0)
 with Image.open(JPG) as v:
  v.load();assert v.format=="JPEG" and v.size==(1080,1080)
 assert JPG.stat().st_size<2000000
 rec.update({"status":"NARROW_BOTTOM_ARTIFACT_REMOVED_VISUAL_QA_PENDING",
  "new_png":png.name,"new_jpg":JPG.name,
  "new_png_sha256":sha(png),"new_jpg_sha256":sha(JPG),
  "previous_photo_png_sha_unchanged":sha(SOURCE)==original_sha})
except Exception as e:
 rec.update({"status":"HOLD_UNSAFE_REMOVAL","reason":str(e)[:220]})
canvas=Image.new("RGB",(1720,590),"#efeeed")
d=ImageDraw.Draw(canvas)
d.text((18,14),"v2765 GOODAL EYE CREAM / ALPHA TAIL QA / PREVIOUS vs CORRECTED",font=font(25,True),fill="#282828")
for col,img in enumerate([rgba,fixed if rec.get("new_png") else rgba]):
 bg=Image.new("RGBA",img.size,"white")
 bg.alpha_composite(img)
 large=ImageOps.contain(bg.convert("RGB"),(465,465),Image.Resampling.NEAREST)
 canvas.paste(large,(20+1200*col,65))
 d.text((490,90+col*72),("ORIGINAL" if col==0 else "TAIL CLEANED" if rec.get("new_png") else "NO FIX"),font=font(23,True),fill="#333333")
d.text((490,250),rec["status"],font=font(18),fill="#454545")
proof=OUT/"v2765-tail-comparison.jpg"
canvas.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2765-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2765","baseline":"v2764","cleaned_image_saved":bool(rec.get("new_png")),
 "previous_img_data_unchanged":True,
 "prior_11_retail_approved_groups_modified":False,
 "prior_55_verified_public_URLs_modified":False,
 "photo_rights_verified":False,"actual_stock_generation_verified":False,
 "original_round_MK_logo_verified":False,"new_retail_sale_approved":0,
 "final_excel_shared":False,"case":rec}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":rec["status"],"tail_length":tail_length,"body_w":body_w,
"threshold":tail_threshold,"new_JPG":int(bool(rec.get("new_jpg"))),"retail_approved":0}))
