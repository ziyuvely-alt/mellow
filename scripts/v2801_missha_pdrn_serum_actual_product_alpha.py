#!/usr/bin/env python3
"""v2801: repair MISSHA PDRN NAD+ Firming Repair Serum 30mL (pending-13).

Previous v2719 alpha failure used an INFO CARD, which is not a product photograph.
The v2696 AbleShop first-party source-04 is a real *single 30mL bottle*.
Stage a real photo-derived foreground-alpha candidate from that source, plus
one coherent five-frame QA set. Reuse original v2697 four other photo/info frames
byte-for-byte. Do not touch previous approved 11 families and 55 public URLs.
No false official logo, false source quality claims, or retail publication.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import numpy as np,json,hashlib,base64,shutil
R=Path("qa-review")
SRC=R/"v2696-missha-serum-official-gallery-proof"
OLD=R/"v2697-missha-serum-one-product-lifestyle-photo-repair"
OUT=R/"v2801-missha-pdrn-serum-30ml-real-single-bottle-alpha-and-five-frame-QA"
assert SRC.exists() and OLD.exists() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
photo=SRC/"source-04-REVIEW-ONLY.jpg"
assert photo.exists()
with Image.open(photo) as f:
 f.load();assert f.format=="JPEG" and min(f.size)>=400
 original=f.convert("RGBA")
w,h=original.size
# Centered single genuine bottle, not the separate cosmetic gift/group in
# source01 and not the model-holding serum in source06. Top-right promotional
# texture is excluded when possible via ROI; exact alpha gets visual check.
crop=(round(.12*w),round(.06*h),round(.79*w),round(.985*h))
region=original.crop(crop)
result={"family":"pending-13","product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
"firstparty_exact_source":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114237",
"source":str(photo),"source_SHA256":sha(photo),"source_dimensions":[w,h],
"source_crop":list(crop),"model":"isnet-general-use",
"alpha_status":"HOLD_NOT_RENDERED","retail_approved":False}
# Always stage the authentic source photograph, so an uncertain mask doesn't
# cause another loop or artificially recreate a product.
source_preview=OUT/"01-official-single-30mL-serum-source-only-1080-QA.jpg"
white=Image.new("RGB",(1080,1080),"white")
fit=ImageOps.contain(original.convert("RGB"),(1010,1010),Image.Resampling.LANCZOS)
white.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
white.save(source_preview,"JPEG",quality=93,optimize=True)
assert source_preview.stat().st_size<2_000_000
result["source_photo_1080_QA"]=source_preview.name
result["source_photo_scaled_from_original"]=True
try:
 session=new_session("isnet-general-use")
 mask_photo=remove(region,session=session,alpha_matting=True,
  alpha_matting_foreground_threshold=230,
  alpha_matting_background_threshold=18,
  alpha_matting_erode_size=4)
 assert mask_photo.mode=="RGBA"
 alpha=np.asarray(mask_photo.getchannel("A"))
 bbox=mask_photo.getchannel("A").getbbox()
 assert bbox is not None
 ratio=float(np.mean(alpha>=128))
 assert .025<ratio<.83 and bbox[2]-bbox[0]>round(.22*w) and bbox[3]-bbox[1]>round(.35*h),(ratio,bbox)
 item=mask_photo.crop(bbox)
 png=OUT/"01-actual-single-bottle-transparent-foreground-QA.png"
 item.save(png,optimize=True)
 bg=Image.new("RGB",(1080,1080),"white")
 resized=ImageOps.contain(item,(905,905),Image.Resampling.LANCZOS)
 bg.paste(resized,((1080-resized.width)//2,(1080-resized.height)//2),resized)
 jpg=OUT/"01-actual-single-bottle-alpha-hero-1080-QA.jpg"
 bg.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(jpg) as check:check.load();assert check.format=="JPEG" and check.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000
 result.update({"alpha_status":"RENDERED_TRUE_ALPHA_VISUAL_QA_PENDING",
   "alpha_coverage":round(ratio,4),"bbox":list(bbox),
   "transparent_png":png.name,"alpha_1080_jpg":jpg.name,
   "alpha_1080_jpg_sha256":sha(jpg),"alpha_png_sha256":sha(png)})
except Exception as e:
 result.update({"alpha_status":"HOLD_MASK_GEOMETRY_OR_MODEL",
   "alpha_error_type":type(e).__name__,"alpha_error":str(e)[:220]})
# Coherent photo-first 5-frame derivative using four exact old JPG sources.
src_main=OUT/result["alpha_1080_jpg"] if result.get("alpha_1080_jpg") else source_preview
out_main=OUT/"01-final-QA-real-single-serum-photo.jpg"
shutil.copyfile(src_main,out_main)
frames=[{"slot":1,"file":out_main.name,"role":"genuine single 30mL serum main source",
         "sha256":sha(out_main),"mask_source_if_available":bool(result.get("alpha_1080_jpg")),
         "previous_complete_frame_modified":False}]
for slot in (2,3,4,5):
 originals=list(OLD.glob(f"{slot:02d}-*.jpg"))
 assert len(originals)==1,(slot,originals)
 p=originals[0]
 target=OUT/f"{slot:02d}-original-v2697-byte-unchanged-QA.jpg"
 shutil.copyfile(p,target)
 assert sha(target)==sha(p)
 with Image.open(target) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 assert target.stat().st_size<2_000_000
 frames.append({"slot":slot,"file":target.name,"sha256":sha(target),
   "source":str(p),"source_sha256":sha(p),"same_exact_bytes":True})
# Contact: original, actual masked candidate, entire 5-frame set.
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
board=Image.new("RGB",(1820,920),"#f0f0ee")
d=ImageDraw.Draw(board)
d.text((18,15),"v2801 MISSHA PDRN NAD+ Serum 30mL | single bottle actual source vs foreground | QA ONLY",font=font,fill="#303030")
with Image.open(source_preview) as im:
 tile=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
board.paste(tile,(20,56))
with Image.open(out_main) as im:
 tile=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
board.paste(tile,(474,56))
d.text((18,488),"left official standalone photo; right actual foreground if mask valid",font=font,fill="#444")
d.text((18,539),"5-frame set: original slot01 corrected, slots02-05 exact old bytes",font=font,fill="#444")
for i,frame in enumerate(frames):
 with Image.open(OUT/frame["file"]) as im:
  tile=im.convert("RGB").resize((260,260),Image.Resampling.LANCZOS)
 x=16+i*355
 board.paste(tile,(x,586))
 d.text((x,854),f"frame {i+1}",font=font,fill="#252525")
proof=OUT/"v2801-real-bottle-and-five-scenes-proof.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2801-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2801","baseline":"v2800",
 "family":"pending-13","five_real_JPG_QA_frames_saved":5,
 "four_previous_frame_files_preserved_SHA_identical":True,
 "new_exact_firstparty_product_bottle_source_selected":True,
 "prior_info_card_not_reused_as_cutout":True,
 "actual_cutout":result,
 "5_frame_set":frames,
 "stock_generation_confirmed":False,
 "image_commercial_reuse_rights_verified":False,
 "original_round_MK_logo_verified":False,
 "customer_facing_retail_approved":False,
 "old_11_approved_families_untouched":True,
 "old_55_public_URLs_untouched":True,
 "original_v2696_v2697_files_untouched":True,
 "final_XLSX_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2801","source":str(photo),"actual_cutout":result["alpha_status"],
   "five_JPGs":len(frames),"prior_bytes_preserved":4,"retail_approved":False}))
