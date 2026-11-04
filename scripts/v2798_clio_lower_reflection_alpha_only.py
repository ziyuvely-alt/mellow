#!/usr/bin/env python3
"""v2798: correction to lower floor-reflection alpha only, using v2797 cutout.
Original 5 official scene JPGs and original 1200 px sources remain byte identical.
Separate QA candidate; not commercially released.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,base64,hashlib,json
ROOT=Path("qa-review")
PREV=ROOT/"v2797-clio-meshglow-five-distinct-official-photo-scenes-and-alpha-qa"
OUT=ROOT/"v2798-clio-meshglow-alpha-floor-reflection-precision-correction"
assert PREV.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
prior=json.loads((PREV/"manifest.json").read_text())
src=PREV/prior["real_alpha_cutout_candidate"]["png_file"]
with Image.open(src) as im:
 im.load();assert im.format=="PNG" and im.mode=="RGBA"
 original=im.copy()
raw=np.asarray(original).copy()
height,width=raw.shape[:2]
start,end=int(height*.845),int(height*.935)
assert 0<start<end<height
a=raw[:,:,3].copy()
for y in range(start,end):
 raw[y,:,3]=np.uint8(np.rint(a[y,:]*(end-y)/(end-start)))
raw[end:,:,3]=0
assert np.array_equal(raw[:start],np.asarray(original)[:start])
changed=int(np.count_nonzero(a!=raw[:,:,3]))
assert changed>100
out_image=Image.fromarray(raw,"RGBA")
bbox=out_image.getchannel("A").getbbox()
assert bbox
out_image=out_image.crop(bbox)
png=OUT/"01-reflection-alpha-refined-real-source-cutout-QA.png"
out_image.save(png,optimize=True)
fit=ImageOps.contain(out_image,(930,930),Image.Resampling.LANCZOS)
square=Image.new("RGB",(1080,1080),"white")
square.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit)
jpg=OUT/"01-reflection-cleaned-product-1080-QA.jpg"
square.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
with Image.open(jpg) as test:assert test.format=="JPEG" and test.size==(1080,1080)
assert jpg.stat().st_size<2000000
before=PREV/"01-alternate-real-segmented-object-1080-QA.jpg"
with Image.open(before) as im:left=im.convert("RGB").resize((520,520),Image.Resampling.LANCZOS)
with Image.open(jpg) as im:right=im.convert("RGB").resize((520,520),Image.Resampling.LANCZOS)
canvas=Image.new("RGB",(1110,610),"#f1f0ee")
d=ImageDraw.Draw(canvas)
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
d.text((18,12),"v2798 | Same original product cutout | Reflection alpha change only | QA",font=f,fill="#252525")
canvas.paste(left,(18,55));canvas.paste(right,(567,55))
d.text((18,579),"v2797 original untouched",font=f,fill="#333")
d.text((567,579),"v2798 lower reflection faded",font=f,fill="#333")
contact=OUT/"v2798-reflection-before-after.jpg"
canvas.save(contact,"JPEG",quality=85,optimize=True)
(OUT/"v2798-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={"version":"v2798","baseline":"v2797","family":"pending-06",
"real_alpha_edit_saved":True,"edited_alpha_pixels":changed,
"alpha_fade_from_y":start,"alpha_fade_until_y":end,
"all_product_and_alpha_pixels_above_y_unchanged":start,
"source_png_sha256":sha(src),"source_preview_sha256":sha(before),
"new_png":png.name,"new_jpg":jpg.name,
"new_png_sha256":sha(png),"new_jpg_sha256":sha(jpg),
"five_existing_distinct_official_photos_unchanged":True,
"1200px_firstparty_source_originals_unchanged":True,
"stock_variant_and_sale_unit_verified":False,
"photo_reuse_license_verified":False,
"original_MK_logo_verified":False,
"retail_approved":False,
"existing_11_approved_families_unchanged":True,
"existing_55_public_urls_unchanged":True,
"final_excel_shared":False,
"human_visual_qa":"PENDING"}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2798","alpha_pixels_changed":changed,
"new_png":png.name,"new_jpg":jpg.name,"retail_approved":False}))
