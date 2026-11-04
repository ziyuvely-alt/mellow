#!/usr/bin/env python3
"""v2727: EXACT original-source alpha-mask cleanup, not a new product rendering.

The v2726 genuine 30ml MISSHA serum cutout has a few remnant floating red decorative
bubbles to the upper right of the dropper. Remove ONLY pixels beyond a conservative
photographically verified neck-to-bottle right boundary, never recolor genuine
package pixels. Preserve v2726 and original unchanged; fail closed if clipped.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,hashlib,json,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2726-missha-serum-30ml-true-single-bottle-cutout-QA"
OUT=ROOT/"v2727-missha-serum-only-bubble-alpha-cleanup-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
png=SRC/"01-real-transparent-serum-30ml-QA.png"
assert png.exists()
with Image.open(png) as im:
 im.load();assert im.mode=="RGBA" and im.format=="PNG"
 ar=np.array(im)
h,w=ar.shape[:2]
assert h>=380 and w>=150,(w,h)
a=ar[:,:,3]
mask=a>=110
# full-height bottle body occupies 48%-83% of object; find median left and right
# bounds from robust central rows only. Prevent decorative bubbles affecting bounds.
bound=[]
for y in range(round(h*.52),round(h*.82),max(1,h//90)):
 cols=np.where(mask[y])[0]
 if cols.size>max(14,w//8):
  bound.append((float(np.quantile(cols,.04)),float(np.quantile(cols,.96))))
assert len(bound)>=12,(len(bound),h)
body_left=float(np.median([q[0] for q in bound]))
body_right=float(np.median([q[1] for q in bound]))
body_width=body_right-body_left
assert body_width>.38*w,(body_left,body_right,w)
body_center=(body_left+body_right)/2
# Neck is deliberately narrower than main bottle, the true top droplet is
# in central columns. The decorative disc behind it is outside this boundary.
cap_limit=body_center+.33*body_width
bottom_limit=body_right+min(8,w*.018)
# Restrict ONLY the upper right of the mask, leaving original body/label area.
before_count=int(np.sum(a>=110))
deleted_pix=0
for y in range(h):
 progress=y/h
 if progress<=.18:limit=cap_limit
 elif progress<=.38:
  t=(progress-.18)/.20
  limit=cap_limit+(bottom_limit-cap_limit)*t
 else:limit=bottom_limit
 xcut=min(w,max(0,int(round(limit))+1))
 if xcut<w:
  deleted_pix+=int(np.sum(a[y,xcut:]>=110))
  ar[y,xcut:,3]=0
after=ar[:,:,3]
remaining=int(np.sum(after>=110))
removed_fraction=deleted_pix/max(1,before_count)
assert .0005<removed_fraction<.18,(deleted_pix,before_count,removed_fraction)
# Entire lower 55% (true red bottle body, logo/label and volume) must stay intact.
x_margin=round(bottom_limit)+1
assert np.array_equal(a[round(h*.52):,:max(0,x_margin)],after[round(h*.52):,:max(0,x_margin)])
assert remaining>=before_count*.82
# Object should retain a long vertical red bottle silhouette.
ys,xs=np.where(after>=110)
assert ys.size>10000 and (ys.max()-ys.min())>=h*.89
clean=Image.fromarray(ar,"RGBA")
bbox=clean.getchannel("A").getbbox()
assert bbox
clean=clean.crop(bbox)
dest_png=OUT/"01-real-alpha-serum-no-floating-bubbles-QA.png"
clean.save(dest_png,optimize=True)
with Image.open(dest_png) as verify:
 verify.load();assert verify.mode=="RGBA"
reg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda z,b=False:ImageFont.truetype(bold if b else reg,z)
sheet=Image.new("RGB",(1080,1080),"white")
d=ImageDraw.Draw(sheet)
d.rounded_rectangle((52,51,1028,1030),radius=34,outline="#efe7e8",width=2)
d.text((98,99),"MISSHA",font=f(44,True),fill="#373038")
d.text((98,160),"PDRN NAD+ Firming Repair Serum 30mL",font=f(26),fill="#655a65")
fitted=ImageOps.contain(clean,(850,760),Image.Resampling.LANCZOS)
sheet.paste(fitted,((1080-fitted.width)//2,216+(775-fitted.height)//2),fitted)
d.text((98,987),"AUTHENTIC PRODUCT PHOTO  |  QA ONLY",font=f(18),fill="#999093")
dest_jpg=OUT/"01-real-serum-1080-QA-bubbles-removed.jpg"
sheet.save(dest_jpg,"JPEG",quality=92,optimize=True,subsampling=0)
with Image.open(dest_jpg) as verify:
 verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
assert dest_jpg.stat().st_size<2000000
proof=Image.new("RGB",(1150,630),"#f2f0f1")
pd=ImageDraw.Draw(proof)
pd.text((13,12),"v2727 BEFORE / AFTER  |  REAL SOURCE ALPHA RETOUCHED  |  QA ONLY",font=f(23,True),fill="#363039")
with Image.open(SRC/"01-real-1080-single-serum-hero-QA.jpg") as prev:
 before=prev.convert("RGB").resize((525,525),Image.Resampling.LANCZOS)
with Image.open(dest_jpg) as now:
 afterpic=now.convert("RGB").resize((525,525),Image.Resampling.LANCZOS)
proof.paste(before,(25,65));proof.paste(afterpic,(600,65))
pd.text((25,596),"BEFORE: RED BUBBLE FRAGMENTS",font=f(17),fill="#792b4d")
pd.text((600,596),"AFTER: SAME BOTTLE, CLEANER ALPHA",font=f(17),fill="#34715d")
pp=OUT/"v2727-before-after-visual-proof.jpg"
proof.save(pp,"JPEG",quality=84,optimize=True)
(OUT/"v2727-proof.b64.txt").write_text(base64.b64encode(pp.read_bytes()).decode())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={
 "version":"v2727","baseline":"v2726","family":"pending-13",
 "status":"ALPHA_MASK_REMNANTS_CLEANED_VISUAL_QA_PENDING",
 "source_original_photo_sha256":"703c7d4e3d883364813e09087dfbf9ad08f5c4a422dd8b86b17036be6abf03ff",
 "source_cutout_sha256":sha(png),"source_cutout_unchanged":True,
 "actual_new_transparent_PNG":dest_png.name,"actual_new_1080_JPG":dest_jpg.name,
 "output_png_sha256":sha(dest_png),"output_jpg_sha256":sha(dest_jpg),
 "output_jpg_size_bytes":dest_jpg.stat().st_size,
 "visible_alpha_pixels_removed_fraction":round(removed_fraction,5),
 "photographic_product_package_RGB_recolored":False,
 "original_photo_and_prior_QA_art_untouched":True,
 "already_published_11_groups_unchanged":True,
 "verified_public_55_URLs_untouched":True,
 "brand_original_MK_asset_presence":"VERIFIED_IN_OWNED_PLUGIN_ARCHIVE_BUT_NOT_YET_EXTRACTED_HERE",
 "commercial_photo_reuse_license_confirmed":False,
 "exact_owned_stock_edition_verified":False,
 "new_retail_sale_approvals":0,"final_xlsx_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2727","actual_new_JPG":1,"real_alpha_deleted_fraction":round(removed_fraction,5),"new_retail_approved":0}))
