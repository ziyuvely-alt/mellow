#!/usr/bin/env python3
"""v2744: actually extract 30mL MISSHA PDRN NAD+ Firming Repair Serum
from SAVED manufacturer product media #04, NOT prior fact card,
multi-product promotional kit or unrelated vitamin-C bottle.

True alpha segmentation with ISNet and an independent locally seeded GrabCut
mask for QA comparison. Do not synthesize/fabricate pixels or use fake MK logo.
Append-only QA branch, never touch published images or URLs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import cv2,numpy as np,hashlib,json,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2696-missha-serum-official-gallery-proof/source-04-REVIEW-ONLY.jpg"
OUT=ROOT/"v2744-MISSHA-PDRN-30mL-single-official-bottle-two-alpha-qa"
assert SRC.is_file() and not OUT.exists()
OUT.mkdir(parents=True)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(size,bold=False):return ImageFont.truetype(B if bold else F,size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(SRC) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 original=im.convert("RGBA")
# Product-centered region from official single 30mL bottle media.
# Never select full product SET media 01/02 and never 05 vitamin C.
CROP=(235,80,804,990)
roi=original.crop(CROP)
paths=[]
def save_mask_result(name,cut):
 assert cut.mode=="RGBA"
 mask=cut.getchannel("A")
 bbox=mask.getbbox()
 if bbox is None:raise ValueError("No foreground object")
 area=sum(a>=128 for a in mask.getdata())/(cut.width*cut.height)
 bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
 if not (.035<=area<=.79 and bw>=115 and bh>=310):
  raise ValueError(f"Mask geometry rejected: ratio={area:.4f};box={bbox}")
 isolated=cut.crop(bbox)
 group=OUT/name
 group.mkdir()
 png=group/"01-real-serum-bottle-alpha-QA.png"
 isolated.save(png,optimize=True)
 hero=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(hero)
 d.text((80,75),"MISSHA",font=ft(38,True),fill="#4a2c35")
 d.text((80,132),"PDRN NAD+ Firming Repair Serum 30mL",font=ft(24),fill="#7b5962")
 contain=ImageOps.contain(isolated,(830,825),Image.Resampling.LANCZOS)
 hero.paste(contain,((1080-contain.width)//2,180+(830-contain.height)//2),contain)
 jpg=group/"01-real-serum-bottle-1080-white-QA.jpg"
 hero.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2000000
 with Image.open(jpg) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 paths.append({"method":name,"status":"PHYSICAL_ALPHA_PNG_JPG_RENDERED_VISUAL_QA_PENDING",
   "mask_fraction":round(area,4),"bbox":list(bbox),
   "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
   "png_sha256":sha(png),"jpg_sha256":sha(jpg),"jpg_bytes":jpg.stat().st_size,
   "source_pixels_reused_without_synthesis":True})
try:
 rgba=remove(roi,session=new_session("isnet-general-use"),alpha_matting=True,
   alpha_matting_foreground_threshold=229,
   alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
 save_mask_result("isnet_30mL_serum",rgba)
except Exception as e:
 paths.append({"method":"isnet_30mL_serum","status":"HOLD_MASK_FAILED","reason":str(e)[:210]})
# Independent full-volume GrabCut anchored around the single bottle.
# The red decorative circle is farther right and should be background.
arr=np.asarray(roi.convert("RGB"))
h,w=arr.shape[:2]
gc=np.full((h,w),cv2.GC_BGD,np.uint8)
# probable object area, excluding most right-side bubbles
gc[55:h-45,50:min(w-52,445)]=cv2.GC_PR_FGD
# surely object along center red bottle
gc[250:min(h-185,760),190:min(w-135,357)]=cv2.GC_FGD
try:
 bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
 cv2.grabCut(arr[:,:,::-1].copy(),gc,None,bg,fg,4,cv2.GC_INIT_WITH_MASK)
 mask=np.uint8((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD))*255
 n,comp,stats,cent=cv2.connectedComponentsWithStats(mask,connectivity=8)
 candidates=[(int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>2000]
 if not candidates:raise ValueError("No main bottle connected component")
 component=max(candidates)[1]
 alpha=np.where(comp==component,255,0).astype(np.uint8)
 alpha=cv2.GaussianBlur(alpha,(0,0),1.05)
 output=np.dstack([arr,alpha])
 save_mask_result("seeded_grabcut_30mL_serum",Image.fromarray(output,"RGBA"))
except Exception as e:
 paths.append({"method":"seeded_grabcut_30mL_serum","status":"HOLD_MASK_FAILED","reason":str(e)[:210]})
canvas=Image.new("RGB",(1700,615),"#f1f0ef")
d=ImageDraw.Draw(canvas)
d.text((16,15),"v2744 MISSHA REAL OFFICIAL SINGLE 30mL SERUM | ALPHA QUALITY COMPARISON",font=ft(22,True),fill="#2b2929")
with Image.open(SRC) as im:
 canvas.paste(im.convert("RGB").resize((502,502),Image.Resampling.LANCZOS),(13,62))
d.text((18,566),"OFFICIAL REAL BOTTLE SOURCE 04",font=ft(20),fill="#333333")
for i,entry in enumerate(paths[:2]):
 x=552+i*571
 if entry.get("jpg"):
  with Image.open(OUT/entry["jpg"]) as result:
   canvas.paste(result.convert("RGB").resize((502,502),Image.Resampling.LANCZOS),(x,62))
 d.text((x,566),entry["method"]+" / "+("QA" if entry.get("jpg") else "HOLD"),font=ft(20),fill="#333333")
proof=OUT/"v2744-photo-comparison.jpg"
canvas.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2744-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2744","baseline":"v2743",
 "family":"pending-13","product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
 "official_source_gallery":"v2696","photo_source_slot":4,
 "actual_source":str(SRC),"actual_source_sha256":sha(SRC),
 "source_crop_xyxy":list(CROP),
 "new_PNG_JPG_pairs":sum(bool(x.get("jpg")) for x in paths),
 "never_used_wrong_fact_card":True,
 "never_used_wrong_vitamin_C_product":True,
 "never_used_multiple_product_set_pictures":True,
 "commercial_photo_reuse_permission_verified":False,
 "physical_owned_stock_generation_verified":False,
 "original_MK_logo_verified":False,
 "previous_11_approved_product_families_untouched":True,
 "previous_55_public_urls_unchanged":True,
 "all_previous_source_photos_unchanged":True,
 "new_retail_approval":False,"final_xlsx_shared":False,
 "candidates":paths}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2744","saved_photo_alpha_pairs":manifest["new_PNG_JPG_pairs"],
 "statuses":[x["status"] for x in paths],"approved_for_sale":0}))
