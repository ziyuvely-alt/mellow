#!/usr/bin/env python3
"""v2837 correct v2836 false transparent INNER CUSHION using image-mask topology.
Reuse the 1200px-native 21N source, and the v2836 already computed transparency
mask (NO repeat of segmentation model). Fill only enclosed alpha holes in the
largest external product contour, then restore the exact original RGB pixels.
No new commercial approval without photo rights/actual owned SKU confirmation.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import cv2,numpy as np,hashlib,json,base64
R=Path("qa-review")
SOURCE=R/"v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe"/"02-21N-high-native-source-QA.jpg"
PRIOR=R/"v2836-clio-mini5g-21N-1200px-isolated-compact-alpha-QA"
OUT=R/"v2837-21N-mini5g-restore-inner-cushion-source-pixels-QA"
assert SOURCE.is_file() and PRIOR.is_dir() and not OUT.exists()
OUT.mkdir()
prior=json.loads((PRIOR/"manifest.json").read_text())
row=prior["candidate"]
assert row["status"]=="TRUE_ALPHA_AND_1080_JPG_CREATED_VISUAL_QA_PENDING"
assert row["shade"]=="21N Linen"
assert row["new_1080_JPG"]=="01-21N-mini5g-1200native-source-1080hero-QA.jpg"
mask_file=PRIOR/row["transparent_PNG"]
with Image.open(mask_file) as pic:
 pic.load()
 assert pic.mode=="RGBA"
 mask_rgba=np.array(pic)
alpha=mask_rgba[:,:,3]
assert alpha.ndim==2
# Largest existing foreground exterior contour. Filling enclosed holes is
# qualitatively different from rerunning a segmentation model that repeatedly
# misidentifies the peach cushion pan as a transparent area.
binary=np.uint8(alpha>=45)
num,labels,stats,centers=cv2.connectedComponentsWithStats(binary,connectivity=8)
components=sorted([(int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,num)],reverse=True)
assert components and components[0][0]>17000,components[:5]
main=np.uint8(labels==components[0][1])*255
cnts,_=cv2.findContours(main,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnt=max(cnts,key=cv2.contourArea)
hull=np.zeros_like(alpha)
cv2.drawContours(hull,[cnt],-1,255,-1)
# Only interior areas which were erroneous holes are changed; outside shape
# preserve the original soft-edge alpha. Fill 1-pixel voids and pan interior.
recovered=np.maximum(alpha,hull)
restored=int(np.count_nonzero((alpha<=25)&(recovered>=200)))
assert 1800<restored<alpha.size*.50,{"restored_pixels":restored,"alpha_shape":alpha.shape}
box=row["mask_bbox"]
crop=row["extracted_photo_crop"]
with Image.open(SOURCE) as im:
 im.load()
 assert im.format=="JPEG" and im.size==(1080,1080)
 source=im.convert("RGB")
roi=source.crop(tuple(crop))
rgb=roi.crop(tuple(box))
assert rgb.size==(mask_rgba.shape[1],mask_rgba.shape[0])
arr=np.array(rgb)
out=np.dstack([arr,recovered])
corrected=Image.fromarray(out,"RGBA")
transparent=OUT/"01-21N-compact-inner-cushion-restored-TRUE-ALPHA-QA.png"
corrected.save(transparent,optimize=True)
jpeg=OUT/"01-21N-mini5g-1200native-cushion-visible-1080-QA.jpg"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
board=Image.new("RGB",(1080,1080),"white")
d=ImageDraw.Draw(board)
d.rounded_rectangle((48,48,1032,1032),radius=35,outline="#eadfe5",width=2)
d.text((94,97),"CLIO",font=f(42,True),fill="#39353a")
d.text((94,166),"Mesh Glow Essential Cushion Mini 5g",font=f(27),fill="#736b72")
d.text((94,211),"21N Linen | Actual photographed cushion",font=f(20),fill="#897b82")
fitted=ImageOps.contain(corrected,(880,710),Image.Resampling.LANCZOS)
board.paste(fitted,((1080-fitted.width)//2,258+(710-fitted.height)//2),fitted)
d.text((94,995),"INNER CUSHION RESTORED FROM SOURCE PIXELS | QA ONLY",font=f(18),fill="#958c91")
board.save(jpeg,"JPEG",quality=93,optimize=True,subsampling=0)
assert jpeg.stat().st_size<2_000_000
with Image.open(jpeg) as check:
 check.load();assert check.format=="JPEG" and check.size==(1080,1080)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
compare=Image.new("RGB",(1540,610),"#f3f1ef")
draw=ImageDraw.Draw(compare)
draw.text((18,13),"v2837 | 21N 1200px source vs v2836 FAILED EMPTY PAN vs RESTORED REAL PAN",font=f(22,True),fill="#2b292b")
for i,(path,title) in enumerate([(SOURCE,"ORIGINAL 21N SOURCE"),(PRIOR/row["new_1080_JPG"],"REJECTED: CENTER ERASED"),(jpeg,"FIXED: ORIGINAL PAN PIXELS")]):
 with Image.open(path) as im:
  thumbnail=im.convert("RGB").resize((463,463),Image.Resampling.LANCZOS)
 x=20+i*503;compare.paste(thumbnail,(x,55))
 draw.text((x,534),title,font=f(18,True),fill="#373238")
draw.text((20,575),"No new model run. No source photo altered. Not licensed for retail listing.",font=f(18),fill="#625a5e")
proof=OUT/"v2837-source-failed-mask-corrected-compare.jpg"
compare.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2837-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2837","baseline":"v2836","family":"pending-04",
 "item":"CLIO Mesh Glow Essential Cushion Mini 5g","shade":"21N Linen",
 "failure_corrected":"v2836 transparent mask removed the peach cushion pan inside compact",
 "algorithm":"FILL_ENCLOSED_HOLES_OF_LARGEST_PRODUCT_CONTOUR_AND_RESTORE_SOURCE_RGB",
 "neural_segmentation_model_reruns":0,
 "original_source_JPG_sha256_before":row["source_sha256"],
 "original_source_JPG_sha256_after":sha(SOURCE),
 "original_source_untouched":sha(SOURCE)==row["source_sha256"],
 "v2836_rejected_older_transparency_untouched":True,
 "original_product_pixels_restored_count":restored,
 "source_mask_pixels":int(alpha.size),
 "new_true_alpha_PNG":transparent.name,
 "new_1080x1080_JPG":jpeg.name,
 "new_JPG_bytes":jpeg.stat().st_size,
 "new_JPG_sha256":sha(jpeg),
 "new_visual_QA_status":"CORRECTED_PHOTO_CANDIDATE_NEEDS_DIRECT_VISUAL_CONFIRMATION",
 "photo_license_verified":False,
 "actual_owned_stock_exact_21N_shade_verified":False,
 "original_MK_logo_authenticated":False,
 "prior_v2832_five_photo_QA_sets_unchanged":True,
 "prior_11_sales_approved_groups_untouched":True,
 "prior_55_verified_public_urls_untouched":True,
 "new_retail_approvals":0,
 "final_xlsx_shared":False
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2837","restored_original_product_pixels":restored,
"alpha_png_saved":True,"JPG_saved":True,"sales_approved":0}))
