#!/usr/bin/env python3
"""v2821: Actual 21N Linen-only CLIO The Original Mini 5g foreground cutout.
Input is already archived variant-linked Lila 21N photo. It has a real compact,
puff AND background swatch. Crop off high background swatch before true alpha
segmentation. Never relabel old #23N packshots as #21N or fabricate shades.
No overwrites of prior 11 approved families, 55 public URLs or prior JPGs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,json,base64,cv2,numpy as np
ROOT=Path("qa-review")
SRC=ROOT/"v2820-clio-mini-5g-Lila-21N-variant-photo-evidence"
SWATCH=ROOT/"v2819-clio-original-mini-5g-21N-exact-variant-photo-evidence"
OUT=ROOT/"v2821-clio-mini-5g-21N-true-compact-alpha-QA"
assert SRC.is_dir() and SWATCH.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
src=SRC/"01-21N-variant-linked-Lila-5g-QA.jpg"
swatch=SWATCH/"01-source-linked-exact-21N-mini5g-QA.jpg"
assert src.is_file() and swatch.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font_regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(font_bold if b else font_regular,n)
result={"version":"v2821","baseline":"v2820","family":"pending-05",
 "product":"CLIO Kill Cover Founwear Cushion The Original Mini 5g",
 "option":"21N Linen","source_21N_photo":str(src),
 "source_sha256":sha(src),"independent_21N_swatch_reference":str(swatch),
 "swatch_sha256":sha(swatch),"do_not_use_23N_photo_as_21N":True,
 "genuine_original_pixel_photo":True,"new_retail_approved":False,
 "exact_owned_stock_edition_verified":False,"photo_commercial_rights_verified":False,
 "original_MK_logo_verified":False,"prior_55_public_urls_unchanged":True,
 "previous_11_approved_product_families_unchanged":True,"previous_v2818_23N_assets_unchanged":True,
 "previous_v2819_and_v2820_21N_assets_unchanged":True,"final_XLSX_shared":False,
 "status":"HOLD_REAL_CUTOUT_VISUAL_OR_SOURCE_QA"}
with Image.open(src) as im:
 im.load()
 assert im.format=="JPEG" and im.size==(1080,1080),(im.format,im.size)
 rgb=im.convert("RGBA")
# Known official variant hero composition: diffuse 21N swatch above and behind,
# real compact and puff below. Crop low enough to minimize the floating swatch
# but not crop the lid. This is photographic source isolation, not a false swatch.
roi_box=(170,365,1075,1063)
roi=rgb.crop(roi_box)
result["original_photo_crop_xyxy"]=list(roi_box)
try:
 rgba=remove(roi,session=new_session("isnet-general-use"),
  alpha_matting=True,alpha_matting_foreground_threshold=225,
  alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
 if rgba.mode!="RGBA":raise ValueError("Segmentation did not return alpha channel")
 alpha=np.asarray(rgba.getchannel("A"),dtype=np.uint8)
 binary=np.uint8(alpha>=96)
 count,labels,stats,_=cv2.connectedComponentsWithStats(binary,connectivity=8)
 components=sorted([(i,int(stats[i,cv2.CC_STAT_AREA])) for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>150],key=lambda z:z[1],reverse=True)
 if not components:raise ValueError("No genuine foreground component")
 # Preserve large foreground pieces (compact and puff can be disconnected)
 maxarea=components[0][1]
 retain={i for i,a in components if a>=maxarea*.12}
 mask=np.uint8(np.isin(labels,list(retain)))*255
 mask=cv2.GaussianBlur(mask,(3,3),0)
 new=np.array(rgba)
 new[:,:,3]=np.minimum(new[:,:,3],mask)
 clean=Image.fromarray(new,"RGBA")
 bbox=clean.getchannel("A").getbbox()
 coverage=float(np.count_nonzero(new[:,:,3]>=128)/new[:,:,3].size)
 if bbox is None or coverage<.06 or coverage>.83 or (bbox[2]-bbox[0])<220 or (bbox[3]-bbox[1])<160:
  raise ValueError(f"Invalid product mask extent: {bbox}, coverage={coverage:.3f}")
 clean=clean.crop(bbox)
 png=OUT/"01-original-21N-mini5g-compact-puff-alpha-QA.png"
 clean.save(png,optimize=True)
 frame=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(frame)
 d.rounded_rectangle((45,44,1035,1035),radius=30,outline="#eee8e5",width=2)
 d.text((91,91),"CLIO",font=ft(44,True),fill="#302d30")
 d.text((91,159),"THE ORIGINAL MINI 5g  |  21N Linen",font=ft(26),fill="#676169")
 fit=ImageOps.contain(clean,(870,792),Image.Resampling.LANCZOS)
 xy=((1080-fit.width)//2,202+(791-fit.height)//2)
 frame.paste(fit,xy,fit)
 d.text((91,994),"EXACT 21N VARIANT SOURCE  |  QA ONLY",font=ft(18),fill="#8c868b")
 jpg=OUT/"01-real-21N-mini5g-1080-hero-QA.jpg"
 frame.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
 with Image.open(jpg) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 assert jpg.stat().st_size<2000000
 result.update({"status":"REAL_21N_ALPHA_RENDERED_VISUAL_QA_PENDING",
  "alpha_coverage":round(coverage,4),"alpha_bbox":list(bbox),
  "main_component_sizes":[a for _,a in components[:8]],
  "main_components_kept":len(retain),
  "alpha_PNG":png.name,"alpha_sha256":sha(png),
  "hero_JPG":jpg.name,"hero_sha256":sha(jpg),"hero_jpg_bytes":jpg.stat().st_size})
except Exception as e:
 result.update({"status":"HOLD_21N_ALPHA_GEOMETRY_FAILED","failure_type":type(e).__name__,"error":str(e)[:240]})
board=Image.new("RGB",(1580,580),"#f2f0ed")
d=ImageDraw.Draw(board)
d.text((20,17),"v2821 21N PHOTO vs ACTUAL SINGLE-SHADE ALPHA vs SAME 21N SWATCH",font=ft(25,True),fill="#292629")
with Image.open(src) as im:
 left=im.convert("RGB").resize((460,460),Image.Resampling.LANCZOS)
board.paste(left,(20,72))
if result.get("hero_JPG"):
 with Image.open(OUT/result["hero_JPG"]) as im:
  center=im.convert("RGB").resize((460,460),Image.Resampling.LANCZOS)
 board.paste(center,(550,72))
with Image.open(swatch) as im:
 right=im.convert("RGB").resize((460,460),Image.Resampling.LANCZOS)
board.paste(right,(1100,72))
d.text((20,538),"21N Lila original",font=ft(19),fill="#3e3a3b")
d.text((550,538),"21N cutout QA or blocked",font=ft(19),fill="#3e3a3b")
d.text((1100,538),"21N DODOSKIN swatch",font=ft(19),fill="#3e3a3b")
proof=OUT/"v2821-21N-original-versus-true-alpha-proof.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2821-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2821","family":"pending-05","option":"21N Linen",
 "status":result["status"],"actual_alpha_saved":bool(result.get("alpha_PNG")),
 "new_sale_approved":False}))
