#!/usr/bin/env python3
"""v2770: 1:1 color provenance, foreground-alpha + silver-cap edge QA for the
completed v2769 GOODAL 30mL single-tube cutout. NO image regeneration.
Inputs, product pixels, previously approved media, 55 public URLs immutable.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,json,hashlib,base64
R=Path("qa-review")
OLD=R/"v2769-goodal-eyecream-clean-independent-source-foreground-QA"
OUT=R/"v2770-goodal-single-tube-native-source-alpha-validation"
assert OLD.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((OLD/"manifest.json").read_text())["item"]
source=OLD/old["source_original_saved"]
png=OLD/old["real_alpha_png"]
jpg=OLD/old["shoppe_size_jpg"]
original_hashes={p.name:sha(p) for p in [source,png,jpg]}
assert original_hashes[source.name]==old["source_sha256"]
assert original_hashes[png.name]==old["png_sha256"]
assert original_hashes[jpg.name]==old["jpg_sha256"]
with Image.open(source) as im:
 im.load();original=im.convert("RGB").copy()
with Image.open(png) as im:
 im.load();assert im.mode=="RGBA" and im.format=="PNG"
 cut=im.copy()
with Image.open(jpg) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080) and jpg.stat().st_size<2000000
x0,y0,x1,y1=old["source_crop_xyxy"]
assert cut.size==(x1-x0,y1-y0)
src_arr=np.asarray(original.crop((x0,y0,x1,y1)),dtype=np.uint8)
cut_arr=np.asarray(cut,dtype=np.uint8)
mask=cut_arr[:,:,3]
strong=mask>=128
assert strong.sum()>20000
rgb_diff=np.abs(cut_arr[:,:,:3].astype(np.int16)-src_arr.astype(np.int16))
foreground_max_abs_diff=int(rgb_diff[strong].max())
foreground_unchanged_pct=float(np.mean(np.all(rgb_diff[strong]==0,axis=1)))
assert foreground_max_abs_diff==0,(foreground_max_abs_diff,foreground_unchanged_pct)
alpha_bbox=cut.getchannel("A").getbbox()
assert alpha_bbox is not None
# Assess top tube seam and bottom silver cap without cropping/re-creating product pixels.
sections={}
for name,a,b in [
 ("upper_tube",0,int(cut.height*.32)),
 ("middle_tube",int(cut.height*.32),int(cut.height*.70)),
 ("bottom_silver_cap",int(cut.height*.70),cut.height)
]:
 active=int((mask[a:b]>=128).sum())
 strong_rows=int(np.count_nonzero((mask[a:b]>=128).sum(axis=1)>=20))
 sections[name]={"opaque_pixels":active,"rows_with_at_least_20_opaque_pixels":strong_rows}
assert sections["bottom_silver_cap"]["rows_with_at_least_20_opaque_pixels"]>=80
# Prove stored JPG & PNG QA assets are the same untouched files as v2769.
assert all(sha(p)==original_hashes[p.name] for p in (source,png,jpg))
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda size,b=False:ImageFont.truetype(boldfile if b else fontfile,size)
def checker(w,h,step=16):
 bg=Image.new("RGBA",(w,h),"#ffffff");d=ImageDraw.Draw(bg)
 for y in range(0,h,step):
  for x in range(0,w,step):
   if (x//step+y//step)%2==0:d.rectangle((x,y,x+step-1,y+step-1),fill="#d6d6d6")
 return bg
view=Image.new("RGB",(1710,1130),"#f2f1ef")
d=ImageDraw.Draw(view)
d.text((20,14),"v2770 GOODAL Eye Cream 30mL / RAW RGB EXACT SOURCE MATCH / NO REGEN",font=font(27,True),fill="#2b292b")
orig_small=ImageOps.contain(original,(495,990),Image.Resampling.LANCZOS)
view.paste(orig_small,(20+(500-orig_small.width)//2,80))
check=checker(*cut.size)
check.alpha_composite(cut)
fg_small=ImageOps.contain(check.convert("RGB"),(490,990),Image.Resampling.LANCZOS)
view.paste(fg_small,(600+(495-fg_small.width)//2,80))
d.text((580,90),"ALPHA SOURCE PROOF",font=font(22,True),fill="#555")
# True native pixel cap cropped in original pixel scale, not resampled; checkerboard.
bw=270
cap_region=cut.crop((0,max(0,cut.height-285),cut.width,cut.height))
cap_bg=checker(*cap_region.size,step=12)
cap_bg.alpha_composite(cap_region)
view.paste(cap_bg.convert("RGB"),(1210,200))
d.text((1212,125),"SILVER CAP / 1:1 PIXELS",font=font(22,True),fill="#2b292b")
d.text((1212,540),f"RGB Δmax: {foreground_max_abs_diff}",font=font(23,True),fill="#23634f")
d.text((1212,585),f"RGB equal: {foreground_unchanged_pct:.0%}",font=font(23),fill="#333")
d.text((1212,635),"QA ONLY | NOT PUBLISHED",font=font(19),fill="#5a5359")
proof=OUT/"v2770-goodal-original-alpha-and-native-cap.jpg"
view.save(proof,"JPEG",quality=90,optimize=True)
(OUT/"v2770-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2770","previous":"v2769","family":"pending-21",
 "source_photo":str(source),"source_dimensions":list(original.size),
 "transparent_png":str(png),"square_JPG":str(jpg),
 "previous_product_file_sha256_unchanged":True,
 "source_rgb_equals_actual_opaque_cutout_rgb":True,
 "max_RGB_channel_difference_for_foreground":foreground_max_abs_diff,
 "foreground_same_rgb_fraction":foreground_unchanged_pct,
 "alpha_bbox":list(alpha_bbox),"cap_coverage":sections["bottom_silver_cap"],
 "native_1_to_1_cap_proof_saved":True,
 "visually_reviewed_cap_and_full_product":"READY_FOR_FURTHER_QA",
 "release_decision":"HOLD_UNVERIFIED_PHOTO_LICENSE_AND_STOCK_25AD_PACKAGE",
 "commercial_photo_reuse_rights_verified":False,
 "physical_inventory_edition_verified":False,"authenticated_MK_original_logo_found":False,
 "original_11_commercially_approved_product_families_unchanged":True,
 "original_55_verified_public_image_URLs_unchanged":True,
 "prior_QA_asset_JPGs_or_PNGs_changed":0,"new_retail_approvals":0,
 "final_excel_or_spreadsheet_shared":False,
 "source_RGB_provenance_sectors":sections
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2770","source_rgb_max_diff":foreground_max_abs_diff,
 "goodal_bottom_cap_covered_rows":sections["bottom_silver_cap"]["rows_with_at_least_20_opaque_pixels"],
 "old_product_files_unchanged":True,"new_sale_approved":0}))
