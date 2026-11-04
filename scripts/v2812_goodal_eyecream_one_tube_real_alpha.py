#!/usr/bin/env python3
"""v2812. Actual true-alpha product-only cutout from NEW standalone 30mL product
photo v2811 frame03. Never retry old clipped tube from v2715/v2716. This
candidate is NOT proof of owned 25AD stock edition or retail photo license.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,json,base64,numpy as np,cv2
ROOT=Path("qa-review")
SRC=ROOT/"v2811-goodal-25AD-single-30mL-three-real-source-photos"
OUT=ROOT/"v2812-goodal-standalone-eyecream-single-tube-true-alpha"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
p=SRC/"03-30mL-single-listing-scene-REVIEW-ONLY.jpg"
assert p.is_file()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
with Image.open(p) as src:
 src.load()
 assert src.format=="JPEG" and src.size==(1080,1080)
 raw=src.convert("RGBA")
# Bright uniform source, full original frame has no old logo; do not clip cap/base.
source=raw.crop((85,20,995,1065))
cut=remove(source,session=new_session("isnet-general-use"),alpha_matting=True,
  alpha_matting_foreground_threshold=230,
  alpha_matting_background_threshold=18,
  alpha_matting_erode_size=4)
assert cut.mode=="RGBA"
alpha=cut.getchannel("A");bbox=alpha.getbbox()
assert bbox is not None
a=np.array(alpha)
pixel_area=np.count_nonzero(a>=128)/a.size
labels,regions,stats,centers=cv2.connectedComponentsWithStats((a>=128).astype("uint8"),connectivity=8)
parts=sorted((int(stats[i,cv2.CC_STAT_AREA]) for i in range(1,labels) if stats[i,cv2.CC_STAT_AREA]>25),reverse=True)
assert len(parts)>0
largest_ratio=parts[0]/max(1,sum(parts))
valid=(.018<pixel_area<.62 and bbox[2]-bbox[0]>125
       and bbox[3]-bbox[1]>570 and largest_ratio>.91)
artifact={"version":"v2812","family":"pending-21",
 "product":"GOODAL Green Tangerine Vita C Dark Circle Eye Cream 30mL",
 "source":"qa-review/v2811-goodal-25AD-single-30mL-three-real-source-photos/03-30mL-single-listing-scene-REVIEW-ONLY.jpg",
 "source_sha256":sha(p),"source_crop":[85,20,995,1065],
 "model":"isnet-general-use","alpha_matting":True,
 "coverage":round(pixel_area,4),"bbox":list(bbox),
 "foreground_main_component_ratio":round(largest_ratio,4),
 "geometry_gate_pass":valid,"status":"HOLD_MASK_NOT_PHYSICALLY_SAFE",
 "source_is_photograph_of_one_real_product":True,
 "stock_25AD_package_generation_verified":False,
 "source_photo_selling_rights_verified":False,
 "real_retail_approval":False}
if valid:
 isolated=cut.crop(bbox)
 png=OUT/"01-real-transparent-single-30mL-bottle-QA.png"
 isolated.save(png,optimize=True)
 board=Image.new("RGB",(1080,1080),"#ffffff")
 d=ImageDraw.Draw(board)
 d.rounded_rectangle((50,50,1030,1030),radius=38,outline="#eae5e5",width=2)
 d.text((93,97),"GOODAL",font=font(43,True),fill="#4f513e")
 d.text((93,161),"Green Tangerine Vita C Eye Cream 30mL",font=font(25),fill="#7b806c")
 scaled=ImageOps.contain(isolated,(860,760),Image.Resampling.LANCZOS)
 xy=((1080-scaled.width)//2,214+(777-scaled.height)//2)
 board.paste(scaled,xy,scaled)
 d.text((93,988),"GENUINE SINGLE-PRODUCT SOURCE | QA, NOT FOR SALE",font=font(18),fill="#9f9f91")
 jpg=OUT/"01-real-single-30mL-hero-1080-QA.jpg"
 board.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(jpg) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000
 artifact.update({"status":"TRUE_ALPHA_PHYSICALLY_SAVED_VISUAL_QA_PENDING",
  "png_file":png.name,"jpg_file":jpg.name,
  "png_sha256":sha(png),"jpg_sha256":sha(jpg),
  "jpg_bytes":jpg.stat().st_size})
# Side by side: original full source and derived masked image when available.
contact=Image.new("RGB",(1250,630),"#efefec")
dr=ImageDraw.Draw(contact)
dr.text((19,12),"v2812 ORIGINAL SINGLE 30mL / TRUE ALPHA MASK  |  QA ONLY",font=font(24,True),fill="#262626")
with Image.open(p) as src:
 contact.paste(src.convert("RGB").resize((515,515),Image.Resampling.LANCZOS),(20,68))
if artifact.get("jpg_file"):
 with Image.open(OUT/artifact["jpg_file"]) as img:
  contact.paste(img.convert("RGB").resize((515,515),Image.Resampling.LANCZOS),(680,68))
dr.text((540,210),f"Mask valid: {valid}",font=font(19),fill="#363636")
dr.text((540,250),f"Main region: {largest_ratio:.3f}",font=font(18),fill="#363636")
dr.text((540,285),f"Coverage: {pixel_area:.3f}",font=font(18),fill="#363636")
proof=OUT/"v2812-goodal-single-30mL-before-after.jpg"
contact.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2812-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode("ascii"))
manifest={**artifact,"previous_30mlx2_official_bundle_not_reused":True,
 "old_bad_clipped_photo_reused":False,"previous_v2811_source_preserved_sha":True,
 "existing_11_sale_approved_families_untouched":True,
 "published_55_verified_URLs_untouched":True,
 "no_fake_MK_logo_generated":True,
 "final_excel_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2812","mask_valid":valid,"saved_PNG_JPG_pair":bool(artifact.get("jpg_file")),"retail_approved":False}))
