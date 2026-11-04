#!/usr/bin/env python3
"""v2827 FIX ONLY left peach background halo in v2825 21N real-alpha.
No re-segmentation and no change to the authentic 21N product pixels.
Preserve 21C approved QA hero, 23N five-scene QA, original photos, public URLs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,cv2,json,hashlib,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2825-clio-mini-5g-21C-21N-uncropped-top-edge-repair"/"21N"
OUT=ROOT/"v2827-clio-mini5g-21N-remaining-peach-halo-mask-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
png=SRC/"01-full-lid-real-compact-alpha-QA.png"
oldjpg=SRC/"01-corrected-full-lid-1080-JPG-QA.jpg"
assert png.is_file() and oldjpg.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(png) as im:rgba=im.convert("RGBA")
arr=np.array(rgba)
height,width=arr.shape[:2]
hsv=cv2.cvtColor(arr[:,:,:3],cv2.COLOR_RGB2HSV)
yy,xx=np.indices((height,width))
# Restrict to left exterior away from silver frame and puff.
# Saturated peach faint background source tint is not part of this white/silver compact.
peach=((hsv[:,:,0]>=3)&(hsv[:,:,0]<=25)&(hsv[:,:,1]>=28)
        &(hsv[:,:,2]>=115)&(xx<min(210,int(width*.23)))&(yy<height*.85))
near_left=(xx<min(65,int(width*.07)))
removed=np.logical_or(peach,near_left)&(arr[:,:,3]>0)
prev_alpha=int(np.count_nonzero(arr[:,:,3]>20))
arr[:,:,3][removed]=0
removed_count=int(np.count_nonzero(removed))
removed_fraction=removed_count/max(1,prev_alpha)
assert removed_fraction<.075,(removed_fraction,removed_count)
img=Image.fromarray(arr,"RGBA")
bbox=img.getchannel("A").getbbox()
assert bbox is not None and (bbox[2]-bbox[0])>=700
# Keep unchanged image size where possible to avoid moving the product.
repaired=OUT/"01-full-lid-21N-ghost-removed-transparent-QA.png"
img.save(repaired,optimize=True)
freg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fbold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(fbold if b else freg,n)
surface=Image.new("RGB",(1080,1080),"white")
d=ImageDraw.Draw(surface)
d.rounded_rectangle((52,50,1028,1028),radius=32,outline="#eee8e7",width=2)
d.text((96,99),"CLIO",font=ft(43,True),fill="#333032")
d.text((96,163),"THE ORIGINAL MINI 5g  |  21N Linen",font=ft(26),fill="#676166")
fitted=ImageOps.contain(img,(870,778),Image.Resampling.LANCZOS)
surface.paste(fitted,((1080-fitted.width)//2,210+(778-fitted.height)//2),fitted)
d.text((95,992),"EXACT 21N PRODUCT PHOTO  |  QA ONLY",font=ft(18),fill="#93888d")
newjpg=OUT/"01-21N-real-photo-full-lid-no-peach-halo-1080-QA.jpg"
surface.save(newjpg,"JPEG",quality=93,optimize=True,subsampling=0)
assert newjpg.stat().st_size<2000000
board=Image.new("RGB",(1120,635),"#f3f0ec")
bd=ImageDraw.Draw(board)
bd.text((18,13),"v2827 21N 5g only: OLD residual peach vs SPATIAL HUE CLEANUP",font=ft(24,True),fill="#332c32")
for index,source in enumerate((oldjpg,newjpg)):
 with Image.open(source) as im:
  tile=im.convert("RGB").resize((520,520),Image.Resampling.LANCZOS)
 board.paste(tile,(18+index*557,62))
bd.text((18,586),"v2825 older left halo | source untouched",font=ft(19),fill="#292629")
bd.text((576,586),"v2827 region-limited photo alpha fix",font=ft(19),fill="#292629")
proof=OUT/"v2827-21N-residual-peach-before-after-QA.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2827-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2827","baseline":"v2826",
 "family":"pending-05","variant":"21N Linen","product":"CLIO Founwear The Original Mini 5g",
 "action":"REGION_LIMITED_ALPHA_HALO_CLEANUP_NOT_NEW_SOURCE_SEGMENTATION",
 "source_cutout_png":str(png),"source_png_sha256":sha(png),
 "prior_JPG":str(oldjpg),"prior_JPG_sha256":sha(oldjpg),
 "new_alpha_png":repaired.name,"new_jpg":newjpg.name,
 "new_png_sha256":sha(repaired),"new_jpg_sha256":sha(newjpg),
 "changed_alpha_pixels":removed_count,"removed_fraction":round(removed_fraction,5),
 "upper_lid_full_source_geometry_preserved":True,
 "new_sale_approval":False,"photo_reuse_rights_verified":False,
 "exact_owned_stock_variant_verified":False,"MK_original_logo_verified":False,
 "existing_21C_23N_and_21N_sources_unchanged":True,
 "approved_11_families_untouched":True,"approved_55_urls_untouched":True,
 "final_excel_shared":False,
 "status":"HALO_CLEANUP_RENDERED_VISUAL_REVIEW_REQUIRED"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2827","new_21N_png_and_jpg":True,
 "alpha_pixels_removed":removed_count,"fraction":round(removed_fraction,5),
 "new_sale_approved":False}))
