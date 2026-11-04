#!/usr/bin/env python3
"""v2805 GOODAL Cream Alpha: clean two remaining truncated text/brand crops.
Use REAL pixels from previously saved official original photo #2, never
invent or erase product elements. Preserve QA frames 01,03,04 byte-identically.
Append-only isolated QA, no retail use without photo license/owned-stock match.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import hashlib,json,shutil,base64
R=Path("qa-review")
OLD=R/"v2804-goodal-alpha-open-jar-no-clipped-marketing-copy-QA"
SOURCE=R/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"/"02-original-PHOTOGRAPHIC_OPEN_JAR_AND_CREAM-QA.jpg"
OUT=R/"v2805-goodal-alpha-open-jar-cream-texture-clean-crops-QA"
assert SOURCE.exists() and OLD.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(SOURCE) as s:
 s.load()
 assert s.format=="JPEG" and s.size==(1080,1080)
 original=s.convert("RGB")
# Distinct purpose-specific crops of the same real source, no masked/copied claims.
# x>=575 excludes closed jar's small text at left. y<925 avoids bottom tagline.
REGIONS={
  2:{"box":[588,433,1040,913],"description":"Open cream jar and golden encapsulated cream, no clipped promotional headline"},
  5:{"box":[703,426,1037,765],"description":"Real cream and golden bead macro, not an independent fourth/fifth photograph"}
}
records=[]
for slot in range(1,6):
 if slot not in REGIONS:
  source=list(OLD.glob(f"{slot:02d}-*.jpg"))
  assert len(source)==1,(slot,source)
  dest=OUT/source[0].name
  shutil.copy2(source[0],dest)
  assert sha(source[0])==sha(dest)
  records.append({"slot":slot,"filename":dest.name,"origin":str(source[0]),
                  "role":"PRESERVED_UNCHANGED","sha256":sha(dest)})
 else:
  box=REGIONS[slot]["box"]
  item=original.crop(box)
  # Crop is a photographic detail. Do not call it independent item/photo.
  surface=Image.new("RGB",(1080,1080),"white")
  fitted=ImageOps.contain(item,(1020,1015),Image.Resampling.LANCZOS)
  pos=((1080-fitted.width)//2,(1080-fitted.height)//2)
  surface.paste(fitted,pos)
  dest=OUT/(f"{slot:02d}-genuine-source-detail-no-truncated-copy-QA.jpg")
  surface.save(dest,"JPEG",quality=93,optimize=True,subsampling=0)
  records.append({"slot":slot,"filename":dest.name,"origin":str(SOURCE),
                  "source_sha256":sha(SOURCE),"crop_original_xyxy":box,
                  "role":"REVISED_REAL_PHOTO_DETAIL_CROP","description":REGIONS[slot]["description"],
                  "not_independent_scene":True,"sha256":sha(dest)})
for r in records:
 p=OUT/r["filename"]
 with Image.open(p) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080),(p,im.size)
 assert p.stat().st_size<2000000,(p,p.stat().st_size)
 r["bytes"]=p.stat().st_size
assert len({r["sha256"] for r in records})==5
# Always leave all original files and the retail-approved 11 untouched.
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
canvas=Image.new("RGB",(1830,495),"#f2f0ee")
d=ImageDraw.Draw(canvas)
d.text((20,12),"v2805 GOODAL CREAM ALPHA 50mL / REAL SOURCE TEXTURE / QA ONLY",font=font,fill="#242424")
for r in records:
 with Image.open(OUT/r["filename"]) as im:
  pic=im.convert("RGB").resize((336,336),Image.Resampling.LANCZOS)
 x=13+(r["slot"]-1)*365
 canvas.paste(pic,(x,64))
 d.text((x,418),f"FRAME {r['slot']:02d}  "+("RECROP" if r["slot"] in REGIONS else "SHA SAVED"),font=font,fill="#222")
proof=OUT/"v2805-five-JPG-photo-comparison.jpg"
canvas.save(proof,"JPEG",quality=85,optimize=True)
(OUT/"v2805-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2805","baseline":"v2804","family":"pending-19",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "five_1080_JPGs_saved":5,"two_new_actual_source_photo_crops":2,
 "prior_three_JPGs_SHA_preserved_exactly":True,
 "new_original_photographs_added":0,"original_brand_source_photo_reencoded_or_modified":False,
 "no_fake_product_pixels":True,"marketing_claims_not_repeated":True,
 "commercial_image_redistribution_rights_verified":False,"owned_stock_edition_verified":False,
 "approved_MK_logo_verified":False,"new_customer_sale_approved":0,
 "prior_11_approved_product_families_modified":False,
 "prior_55_published_public_URLs_modified":False,
 "final_XLSX_shared":False,"frames":records,
 "human_fullsize_visual_QA_required":True
}
(OUT/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"version":"v2805","frames":5,"real_photo_crops":2,
"sha_preserved":3,"approved":0}))
