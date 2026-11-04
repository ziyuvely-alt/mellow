#!/usr/bin/env python3
"""Shopee v2742: TWO one-time exact-real-photo cutout candidates from v2741
manufacturer OBgE Oil Control Finisher 5g photo #01 ONLY. Reject all other
v2741 recommendation/promo files. No image synthesis or fake product pixels.
No retouch of any prior 11 approved items, public 55 URLs or source JPG.
"""
from pathlib import Path
import hashlib,json,base64
import cv2,numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path("qa-review")
src=R/"v2741-obge-finisher-5g-firstparty-original-resolution-QA/01-MANUFACTURER-real-source-1080-QA.jpg"
out=R/"v2742-obge-5g-source997-compact-alpha-extraction"
assert src.exists() and not out.exists()
out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(src) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 rgb=np.array(im.convert("RGB"))
h,w=rgb.shape[:2]
red,green,blue=rgb[:,:,0].astype(np.int16),rgb[:,:,1].astype(np.int16),rgb[:,:,2].astype(np.int16)
luma=(77*red+150*green+29*blue)//256
xx=np.arange(w)[None,:];yy=np.arange(h)[:,None]
# Restrict to the single genuine compact area. Cream swatch appears on right.
roi=(xx>=220)&(xx<=820)&(yy>=110)&(yy<=970)
# Brown/beige lid + dark purple strip pixels are warm or dark; near-white
# cosmetic cream behind is neutral and therefore excluded.
warm=((red-green>=6)&(red-blue>=12)&(luma<244))
dark=(luma<156)&((red-blue>=-2)|(red-green>=0))
candidate=np.uint8((warm|dark)&roi)*255
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
candidate=cv2.morphologyEx(candidate,cv2.MORPH_CLOSE,k,iterations=2)
candidate=cv2.morphologyEx(candidate,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
cnts,_=cv2.findContours(candidate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
valid=[]
for c in cnts:
 x,y,bw,bh=cv2.boundingRect(c)
 if bw>=170 and bh>=230 and cv2.contourArea(c)>=11000 and x<740:
  valid.append((cv2.contourArea(c),c))
assert valid,"No plausible source-product core; do not fabricate cutout"
valid.sort(key=lambda x:x[0],reverse=True)
core=np.zeros((h,w),np.uint8)
cv2.drawContours(core,[valid[0][1]],-1,255,thickness=-1)
# Expand only slightly to retain genuine object edges; do not include white
# cosmetic swatch behind it. Blur alpha fringe without changing photo pixels.
expanded=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)),iterations=1)
models=[("chromatic_contour",expanded)]
# GrabCut seeded with the product core. A separate method, not a repeat of
# failed neural foreground masks from previous archived tiny composite.
gc=np.full((h,w),cv2.GC_BGD,np.uint8)
prob=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(29,29)),iterations=1)
gc[prob>0]=cv2.GC_PR_FGD
strong=cv2.erode(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)),iterations=1)
gc[strong>0]=cv2.GC_FGD
# Cream/high-light neutral image is not a product silhouette.
neutral_white=(luma>235)&(np.abs(red-green)<8)&(np.abs(green-blue)<9)
gc[neutral_white&(core==0)]=cv2.GC_BGD
try:
 bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
 cv2.grabCut(rgb[:,:,::-1].copy(),gc,None,bg,fg,5,cv2.GC_INIT_WITH_MASK)
 fgmask=np.uint8((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD))*255
 # Keep large component anchored on the product; no floating cream fragments.
 contours,_=cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 if contours:
  largest=max(contours,key=cv2.contourArea)
  clean=np.zeros_like(fgmask)
  cv2.drawContours(clean,[largest],-1,255,thickness=-1)
  if cv2.contourArea(largest)>=18000:
   models.append(("grabcut_seeded",clean))
except cv2.error as e:
 print("GrabCut unavailable: "+str(e)[:160])
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT=ImageFont.truetype(F,24)
BOLD=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",32)
rows=[]
for name,rawmask in models:
 alpha=cv2.GaussianBlur(rawmask,(0,0),1.35)
 contours,_=cv2.findContours(np.uint8(alpha>=128)*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 if not contours:continue
 largest=max(contours,key=cv2.contourArea)
 x,y,bw,bh=cv2.boundingRect(largest)
 # Enforce significant improvement over old real 274x269 object pixels.
 good_geometry=(bw>=310 and bh>=370 and cv2.contourArea(largest)>=20000)
 # White cosmetic swatch to the right should not be retained.
 # Right bound remains central, not full width.
 good_geometry=good_geometry and (x+bw<=905)
 entry={"method":name,"source_photo":str(src),"source_sha256":sha(src),
  "native_manufacturer_photo_px":[997,997],
  "source_bbox_original1080":[x,y,bw,bh],
  "actual_product_crop_source_px_approx":[round(bw*997/1080),round(bh*997/1080)],
  "mask_area":int(cv2.countNonZero(np.uint8(alpha>=128))),
  "mask_geometry_pass":bool(good_geometry),
  "retail_approved":False}
 if not good_geometry:
  entry["status"]="HOLD_MASK_SHAPE_TOO_SMALL_OR_OFF_CENTER"
  rows.append(entry);continue
 bgra=np.dstack([rgb[:,:,::-1],alpha])
 # PIL source channels RGBA, never synthetic object pixels.
 img=Image.fromarray(np.dstack([rgb,alpha]),"RGBA").crop((x,y,x+bw,y+bh))
 folder=out/name;folder.mkdir()
 png=folder/"01-real-native-source-compact-transparent-QA.png"
 img.save(png,optimize=True)
 white=Image.new("RGB",(1080,1080),"#ffffff")
 draw=ImageDraw.Draw(white)
 draw.text((88,67),"OBgE",font=BOLD,fill="#352d30")
 draw.text((88,121),"Oil Control Finisher | 5g",font=FONT,fill="#6c6065")
 fit=ImageOps.contain(img,(910,825),Image.Resampling.LANCZOS)
 white.paste(fit,((1080-fit.width)//2,174+(825-fit.height)//2),fit)
 draw.text((88,1026),"OFFICIAL REAL-PHOTO CUTOUT QA ONLY",font=FONT,fill="#948b8d")
 jpg=folder/"01-manufacturer-compact-only-1080-QA.jpg"
 white.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2000000
 entry.update({"status":"ACTUAL_ALPHA_SOURCE_PHOTO_CANDIDATE_REQUIRES_VISUAL_QA",
  "png":str(png.relative_to(out)),"jpg":str(jpg.relative_to(out)),
  "jpg_sha256":sha(jpg),"png_sha256":sha(png),"JPG_bytes":jpg.stat().st_size})
 rows.append(entry)
canvas=Image.new("RGB",(1700,610),"#f0f0ef")
d=ImageDraw.Draw(canvas)
d.text((22,15),"v2742 997px MANUFACTURER SOURCE vs COLOR/GRABCUT PRODUCT ONLY",font=FONT,fill="#262626")
with Image.open(src) as original:
 thumb=original.convert("RGB").resize((485,485),Image.Resampling.LANCZOS)
 canvas.paste(thumb,(18,68))
d.text((24,560),"SOURCE PHOTO",font=FONT,fill="#333333")
for i,entry in enumerate(rows[:2]):
 pos=550+i*575
 if entry.get("jpg"):
  with Image.open(out/entry["jpg"]) as test:
   im=test.convert("RGB").resize((485,485),Image.Resampling.LANCZOS)
  canvas.paste(im,(pos,68))
 d.text((pos,560),entry["method"]+" / "+entry["status"][:18],font=FONT,fill="#333333")
proof=out/"v2742-real-photo-alpha-comparison.jpg"
canvas.save(proof,"JPEG",quality=83,optimize=True)
(out/"v2742-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2742","baseline":"v2741","family":"pending-09",
 "actual_real_photo_cutouts_saved":sum(bool(x.get("jpg")) for x in rows),
 "original_source_JPG_unchanged":True,"other_v2741_recommendation_images_used":False,
 "approved_product_images_modified":0,"public_55_urls_modified":0,
 "photo_redistribution_permission_verified":False,"actual_owned_stock_EAN_verified":False,
 "original_MK_logo_authenticated":False,"new_retail_approved":0,
 "final_excel_shared":False,"candidates":rows}
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2742","attempts":len(rows),
"physical_cutouts":manifest["actual_real_photo_cutouts_saved"],
"statuses":[x["status"] for x in rows],"sale_approved":0}))
