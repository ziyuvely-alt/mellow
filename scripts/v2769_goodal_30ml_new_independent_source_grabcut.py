#!/usr/bin/env python3
"""v2769: New genuine independent single-item GOODAL 30 mL eye-cream source.
Do not re-cut the damaged v2764 product mask or rerun the earlier rembg models.
Use a distinct real retailer photo with intact silver cap; GrabCut foreground
only. All output strictly non-public QA and no MK logo fabrication.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests,numpy as np,cv2,base64,json,hashlib
ROOT=Path("qa-review")
OUT=ROOT/"v2769-goodal-eyecream-clean-independent-source-foreground-QA"
assert not OUT.exists()
OUT.mkdir(parents=True)
SOURCE_URL="https://www.ballagrio.com/cdn/shop/files/A00000022977609ko.webp?v=1769576262"
rec={"version":"v2769","family":"pending-21","product":"GOODAL Green Tangerine Vita C Dark Spot Care Eye Cream 30mL",
"source_url":SOURCE_URL,"source_provider":"Ballagrio retailer photo (third party, use-rights not established)",
"replace_prior_v2764_v2765":False,"old_segmentation_model_retried":False,
"photo_redistribution_rights_verified":False,"exact_owned_stock_25AD_edition_verified":False,
"original_MK_logo_verified":False,"retail_approved":False,"status":"SOURCE_ACQUISITION_PENDING"}
try:
 response=requests.get(SOURCE_URL,timeout=16,headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"})
 response.raise_for_status()
 assert len(response.content)<4_000_000
 with Image.open(BytesIO(response.content)) as orig:
  orig.load()
  photo=ImageOps.exif_transpose(orig).convert("RGB")
 w,h=photo.size
 assert w>=400 and h>=400,(w,h)
 src=OUT/"goodal-eyecream-30ml-single-original-independent-source.png"
 photo.save(src,"PNG",optimize=True)
 rec.update({"source_original_saved":src.name,"source_pixel_dimensions":[w,h],
 "source_sha256":hashlib.sha256(src.read_bytes()).hexdigest()})
 rgb=np.asarray(photo)
 # Exact 1-item white-background photo is mandatory for this segmentation path.
 corners=np.concatenate([rgb[:round(.07*h),:round(.12*w)].reshape(-1,3),
   rgb[:round(.07*h),-round(.12*w):].reshape(-1,3),
   rgb[-round(.06*h):,:round(.12*w)].reshape(-1,3)],axis=0)
 assert np.median(corners)>242,"Non-white source background: do not use white-background GrabCut"
 mask=np.full((h,w),cv2.GC_PR_BGD,dtype=np.uint8)
 mask[:, :round(.29*w)]=cv2.GC_BGD
 mask[:, round(.72*w):]=cv2.GC_BGD
 mask[:round(.04*h),:]=cv2.GC_BGD
 mask[round(.973*h):,:]=cv2.GC_BGD
 mask[round(.32*h):round(.70*h),round(.45*w):round(.54*w)]=cv2.GC_FGD
 mask[round(.83*h):round(.88*h),round(.46*w):round(.53*w)]=cv2.GC_FGD
 mask[round(.07*h):round(.957*h),round(.34*w):round(.68*w)]=cv2.GC_PR_FGD
 # Restore definite foreground where the yellow body / silver cap are.
 mask[round(.32*h):round(.70*h),round(.45*w):round(.54*w)]=cv2.GC_FGD
 mask[round(.83*h):round(.88*h),round(.46*w):round(.53*w)]=cv2.GC_FGD
 cv2.grabCut(rgb[:,:,::-1].copy(),mask,None,np.zeros((1,65),np.float64),
            np.zeros((1,65),np.float64),6,cv2.GC_INIT_WITH_MASK)
 fg=((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD)).astype(np.uint8)
 n,labels,stats,_=cv2.connectedComponentsWithStats(fg,connectivity=8)
 parts=[(i,int(stats[i,cv2.CC_STAT_AREA])) for i in range(1,n)]
 assert parts,"No foreground product selected"
 component=max(parts,key=lambda q:q[1])[0]
 fg=(labels==component).astype(np.uint8)
 fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 alpha=cv2.GaussianBlur(fg*255,(3,3),0.5)
 x,y,bw,bh=cv2.boundingRect(fg)
 ratio=float(np.mean(fg))
 # Reject tiny fragments and crops omitting the lower metallic cap.
 assert .08<ratio<.38 and bw>=round(.15*w) and bh>=round(.72*h),(ratio,(x,y,bw,bh),w,h)
 assert y+bh>=round(.90*h),"Silver lower cap not fully retained"
 assert y<=round(.12*h),"Tube top cropped"
 rgba=np.dstack([rgb,alpha]).astype(np.uint8)
 x0=max(0,x-12);y0=max(0,y-10);x1=min(w,x+bw+12);y1=min(h,y+bh+12)
 product=Image.fromarray(rgba,"RGBA").crop((x0,y0,x1,y1))
 folder=OUT/"pending-21";folder.mkdir(exist_ok=True)
 png=folder/"01-genuine-single-30mL-tube-transparent-QA.png"
 product.save(png,optimize=True)
 cover=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(cover)
 FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 d.rounded_rectangle((46,48,1034,1032),radius=30,outline="#eceae3",width=2)
 d.text((100,93),"GOODAL",font=ImageFont.truetype(BOLD,44),fill="#3c3830")
 d.text((100,162),"Green Tangerine Vita C Eye Cream 30mL",font=ImageFont.truetype(FONT,25),fill="#69665c")
 product=ImageOps.contain(product,(760,777),Image.Resampling.LANCZOS)
 cover.paste(product,((1080-product.width)//2,212+(773-product.height)//2),product)
 d.text((100,995),"SINGLE-ITEM PHOTO SOURCE  |  QA ONLY",font=ImageFont.truetype(FONT,20),fill="#918c82")
 jpg=folder/"01-true-alpha-single-eyecream-1080-QA.jpg"
 cover.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2_000_000
 rec.update({"status":"SINGLE_TUBE_REAL_CUTOUT_RENDERED_VISUAL_QA_REQUIRED",
  "real_alpha_png":str(png.relative_to(OUT)),"shoppe_size_jpg":str(jpg.relative_to(OUT)),
  "source_crop_xyxy":[x0,y0,x1,y1],"mask_bbox":[x,y,bw,bh],
  "mask_coverage":round(ratio,5),
  "png_sha256":hashlib.sha256(png.read_bytes()).hexdigest(),
  "jpg_sha256":hashlib.sha256(jpg.read_bytes()).hexdigest(),
  "png_bytes":png.stat().st_size,"jpg_bytes":jpg.stat().st_size})
except Exception as exc:
 rec.update({"status":"HOLD_NEW_SOURCE_OR_MASK_FAILED","error_type":type(exc).__name__,
 "error":str(exc)[:360]})
# Contact image stores the actual reference alongside the genuine alpha or the blocker.
contact=Image.new("RGB",(1320,600),"#f0efec")
draw=ImageDraw.Draw(contact)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
draw.text((16,16),"v2769 GOODAL EXACT ONE-TUBE SOURCE -> NEW ACTUAL ALPHA | QA ONLY",font=font,fill="#292929")
if rec.get("source_original_saved"):
 im=Image.open(OUT/rec["source_original_saved"]).convert("RGB")
 im=ImageOps.contain(im,(490,490),Image.Resampling.LANCZOS)
 contact.paste(im,(16+(490-im.width)//2,80))
if rec.get("shoppe_size_jpg"):
 im=Image.open(OUT/rec["shoppe_size_jpg"]).convert("RGB")
 im=ImageOps.contain(im,(490,490),Image.Resampling.LANCZOS)
 contact.paste(im,(806+(490-im.width)//2,80))
draw.text((520,124),rec["status"][:24],font=font,fill="#333333")
draw.text((520,175),"No original MK logo / no sale release",font=font,fill="#555555")
proof=OUT/"v2769-single-real-photo-alpha-comparison.jpg"
contact.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2769-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2769","previous_success_checkpoint":"v2768","actual_original_product_photo_fetched":bool(rec.get("source_original_saved")),
"physically_rendered_true_alpha_png_jpg_pairs":int(bool(rec.get("shoppe_size_jpg"))),
"new_sale_retail_approvals":0,"prior_11_approved_families_unchanged":True,
"prior_55_public_verified_urls_unchanged":True,
"previous_QA_files_untouched":True,"original_MK_logo_not_authenticated":True,
"photo_redistribution_rights_not_verified":True,"owned_stock_edition_not_verified":True,
"final_XLSX_shared":False,"item":rec}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2769","photo_fetched":bool(rec.get("source_original_saved")),
"segmented_alpha_png_jpg_pair":int(bool(rec.get("shoppe_size_jpg"))),
"status":rec["status"],"retail_approved":0}))
