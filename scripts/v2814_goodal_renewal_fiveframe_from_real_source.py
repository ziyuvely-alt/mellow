#!/usr/bin/env python3
"""v2814: Assemble five truthful GOODAL 2026 renewal eye-cream QA JPGs from
already-stored SINGLE TUBE photographs; NO new product generation, NO
unauthenticated MK mark, NO promotional gift image, NO old pump reference.
A close-up is explicitly a crop of an existing source, not a third photo shoot.
Source 25AD identity, rights and user's actual stock remain HOLD.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2813-goodal-renewal-25AD-tube-genuine-source-alpha"
OUT=ROOT/"v2814-goodal-25ad-renewal-tube-five-photo-first-JPG-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
sources={
 "hero":SRC/"01-real-2026-renewal-yellow-tube-alpha-hero-1080-QA.jpg",
 "photo":SRC/"01-2026-renewal-single-tube-1080-QA.jpg",
 "texture":SRC/"02-2026-hikoco-tube-photo-1080-QA.jpg",
 "alpha":SRC/"01-real-2026-renewal-yellow-tube-transparent-QA.png",
}
for path in sources.values():assert path.is_file(),path
with Image.open(sources["texture"]) as img:
 img.load();assert img.format=="JPEG" and img.size==(1080,1080)
 texture=img.convert("RGB")
rows=[]
def checked(path,slot,role,src,kind,description):
 with Image.open(path) as img:
  img.load();assert img.format=="JPEG" and img.size==(1080,1080)
 assert path.stat().st_size<2_000_000
 rows.append({"slot":slot,"file":path.name,"role":role,
              "source":str(src),"source_sha256":sha(src),
              "jpg_sha256":sha(path),"jpg_bytes":path.stat().st_size,
              "composition_kind":kind,"source_description":description,
              "rights_verified":False,"stock_edition_verified":False})
for slot,name,key,role,description in [
 (1,"01-existing-true-alpha-2026-tube-hero-QA.jpg","hero","SINGLE_TUBE_REAL_ALPHA","Existing cutout saved in v2813, NOT newly generated"),
 (2,"02-original-2026-single-yellow-tube-full-QA.jpg","photo","SINGLE_TUBE_SOURCE_PHOTO","2026 tube original product-only reference (480px intrinsic)"),
 (3,"03-original-2026-yellow-tube-cream-swatch-QA.jpg","texture","ACTUAL_CREAM_SMEAR_PRODUCT_SCENE","Original 1500px source showing tube with cream texture")
]:
 dst=OUT/name
 shutil.copy2(sources[key],dst)
 assert sha(dst)==sha(sources[key])
 checked(dst,slot,role,sources[key],"BYTE_IDENTICAL_TO_PREVIOUS_QA",description)
# Two distinct, crop-only photographic detail frames from the existing source.
# Natural pixels remain unaltered, not a fake independent photoshoot.
def detail(slot,name,box,label):
 assert 0<=box[0]<box[2]<=1080 and 0<=box[1]<box[3]<=1080
 crop=texture.crop(box)
 canvas=Image.new("RGB",(1080,1080),"#ffffff")
 # Preserve original aspect/scale; slight clean whitespace instead of upscale
 # to an extreme 1:1 crop, and no overlaid claims.
 cropped=ImageOps.contain(crop,(1010,1010),Image.Resampling.LANCZOS)
 canvas.paste(cropped,((1080-cropped.width)//2,(1080-cropped.height)//2))
 path=OUT/name
 canvas.save(path,"JPEG",quality=93,optimize=True,subsampling=0)
 checked(path,slot,label,sources["texture"],"REAL_PHOTO_CROPPED_DETAIL_NOT_NEW_SHOOT",
         "Crop only of the existing tube-and-cream source photo, no invented product pixels")
 return path
detail(4,"04-real-tube-label-and-silver-cap-detail-QA.jpg",(365,90,735,790),
       "2026_TUBE_LABEL_CAP_CLOSEUP")
detail(5,"05-real-cream-texture-macro-no-extra-gifts-QA.jpg",(60,285,540,850),
       "CREAM_SMEAR_PHOTOGRAPHIC_MACRO")
assert len(rows)==5
assert len({r["jpg_sha256"] for r in rows})==5,"Not five byte-distinct JPGs"
# Save unchanged transparent PNG so downstream source is not lost.
alpha=OUT/"01-existing-single-tube-true-alpha-unchanged-QA.png"
shutil.copy2(sources["alpha"],alpha)
assert sha(alpha)==sha(sources["alpha"])
# Proof contact JPEG. Real sources only; never use gifting advertisement in listing.
proof=Image.new("RGB",(1840,965),"#f0f0ed")
d=ImageDraw.Draw(proof)
d.text((16,14),"v2814 / GOODAL 2026 YELLOW TUBE / REAL PHOTO FIRST / QA ONLY",font=font,fill="#282828")
for row in rows:
 i=row["slot"]-1
 with Image.open(OUT/row["file"]) as im:
  tile=im.convert("RGB").resize((345,345),Image.Resampling.LANCZOS)
 x=17+(i%5)*364
 proof.paste(tile,(x,70))
 d.text((x,426),f"{row['slot']:02d} {row['role'][:19]}",font=font,fill="#303030")
 d.text((x,465),"Original" if row["slot"]<=3 else "Real-source crop",font=font,fill="#777777")
d.text((19,545),"Five photo-first JPGs are composed from only TWO independent photographic scenes.",font=font,fill="#404040")
d.text((19,590),"01 is the existing true-alpha cutout; 04 and 05 are crops from photo 03, NOT separate shoots.",font=font,fill="#404040")
d.text((19,635),"No old pump / bonus products / fake MK logo. Commercial photo rights and 25AD stock match are NOT verified.",font=font,fill="#404040")
outproof=OUT/"v2814-fiveframe-visual-proof.jpg"
proof.save(outproof,"JPEG",quality=83,optimize=True)
(OUT/"v2814-fiveframe-proof.b64.txt").write_text(base64.b64encode(outproof.read_bytes()).decode("ascii"))
manifest={
 "version":"v2814","baseline":"v2813","family":"pending-21",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Eye Cream 30mL (2026 renewal tube)",
 "five_actual_1080_JPGs_saved":len(rows),"transparent_PNG_preserved":True,
 "photo_independent_original_scenes":2,"genuine_crop_only_frames":2,
 "previous_jpg_bytes_copied_unchanged":3,
 "marketing_swatch_fabricated":False,"promotional_gift_photo_used":False,
 "old_pump_edition_photo_used":False,"verified_2026_stock_25AD_equivalence":False,
 "photo_commercial_rights_verified":False,"original_round_MK_logo_verified":False,
 "full_res_human_visual_QA":"NEEDS_DIRECT_REVIEW",
 "retail_sales_approved":False,
 "old_11_sales_approved_families_unchanged":True,
 "old_55_public_URLs_unchanged":True,
 "prior_v2813_images_unchanged":True,
 "final_excel_spreadsheet_shared":False,
 "frames":rows,
 "next":"Inspect actual photographic crop framing, ensure four/five offer genuine distinct value; exact user-owned tube/25AD edition and license remain sale gates."
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2814","JPGs":5,"preserved_unchanged":3,
                  "actual_photo_detail_crops":2,
                  "photo_source_scenes":2,
                  "new_sales_approved":0}))
