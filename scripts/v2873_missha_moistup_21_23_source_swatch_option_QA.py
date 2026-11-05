#!/usr/bin/env python3
"""v2873: source-pixel-preserving SHA-locked MISSHA Magic Cushion Moist Up 21/23 QA.
Reuses a pre-existing 5-scene regional PHOTO set (v2701) and one genuine
Sagi-watermarked actual #21 vs #23 application source (v2528). Preserve the
complete original alongside a focus crop; do NOT hide its watermark in a
standalone presentation or recolor any shade. Production/stock edition
is NOT authenticated, nor are retailer-photo usage rights.
No brand logo invention, old asset updates, public URL writes or Excel output.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json

R=Path("qa-review")
OLD=R/"v2701-missha-moistup-five-actual-product-photo-QA"
EXT=Path("/tmp/v2873swatch/review-JPG-by-family/pending-02")
EXT_MANIFEST=Path("/tmp/v2873swatch/manifest.json")
OUT=R/"v2873-missha-moistup-two-shade-source-photo-swatch-QA"
assert OLD.is_dir() and EXT.is_dir() and EXT_MANIFEST.is_file()
assert not OUT.exists(), "Do not overwrite previously processed v2873 output."
sha=lambda p:sha256(p.read_bytes()).hexdigest()
pm=json.loads((OLD/"manifest.json").read_text())
sm=json.loads(EXT_MANIFEST.read_text())
assert pm["version"]=="v2701" and pm["family"]=="pending-02"
assert sm["version"]=="v2528" and sm["source_image_shades"]==["#21","#23"]
assert sm["original_154_images_byte_identical"]
product_row=next(x for x in pm["frames"] if x["slot"]==2)
prod=OLD/product_row["file"]
swatch=EXT/"06-original-21-23-shades-watermarked-QA.jpg"
assert prod.is_file() and swatch.is_file()
assert sha(prod)==product_row["sha256"]
assert sha(swatch)==sm["new_sha256"]
with Image.open(prod) as photo:
 photo.load(); assert photo.format=="JPEG" and min(photo.size)>=700
 product=photo.convert("RGB")
with Image.open(swatch) as photo:
 photo.load(); assert photo.format=="JPEG" and photo.size==(1080,1080)
 actual=photo.convert("RGB")
# Preserve existing source bytes and every watermark. Crop ONLY to zoom
# into the real target swatch, always with complete watermarked photo above.
names={"21":("LIGHT BEIGE",(24,70,529,531)),
       "23":("NATURAL BEIGE",(550,70,1060,531))}
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
cards=[]
for shade,(desc,crop) in names.items():
 body=Image.new("RGB",(1080,1080),"#FCFAFD")
 d=ImageDraw.Draw(body)
 d.rounded_rectangle((36,36,1044,1044),radius=25,outline="#E0D7E5",width=2)
 d.text((70,64),"MISSHA",font=ft(56,True),fill="#443C50")
 d.text((70,140),"MAGIC CUSHION MOIST UP",font=ft(26),fill="#655B68")
 d.rounded_rectangle((780,78,1005,162),radius=12,fill="#F0E8F1")
 d.text((799,94),"NO."+shade,font=ft(31,True),fill="#665267")
 d.text((799,130),desc,font=ft(15,True),fill="#665267")
 d.line((65,187,1015,187),fill="#D7C8D9",width=3)
 # Exact photo is shared across the regional catalog: no option-specific
 # color/material/puff claim is inferred from product body.
 shared=ImageOps.contain(product,(465,497),Image.Resampling.LANCZOS)
 body.paste(shared,(68+(465-shared.width)//2,236+(497-shared.height)//2))
 d.text((83,731),"SHARED PRODUCT PHOTO",font=ft(18,True),fill="#5D5362")
 d.text((83,759),"Regional edition not stock-verified",font=ft(15),fill="#857985")
 # The entire Sagi-sourced image is visibly retained in the retail QA
 # panel, including the original Sagi watermark in its upper-right corner.
 full=ImageOps.contain(actual,(450,450),Image.Resampling.LANCZOS)
 body.paste(full,(563+(450-full.width)//2,225+(450-full.height)//2))
 d.text((575,683),"SAGI SOURCE · BOTH SHADES",font=ft(16,True),fill="#5D5362")
 d.text((575,709),"Watermark preserved / not licensed",font=ft(14),fill="#857985")
 # Shade-specific zoom is sourced from exact pixels without recoloring.
 zoom=actual.crop(crop)
 z=ImageOps.contain(zoom,(890,128),Image.Resampling.LANCZOS)
 # Narrow zoom band (with #21 / #23 label), not a fabricated color chip.
 d.rounded_rectangle((73,806,1007,969),radius=16,fill="#FFFFFF",outline="#E4D8E7",width=2)
 body.paste(z,(93+(890-z.width)//2,821+(128-z.height)//2))
 d.text((80,978),"SOURCE SWATCH ONLY · QA NOT SALES · NO COLOR EDIT",font=ft(17,True),fill="#7A6A79")
 file=OUT/f"MISSHA-MoistUp-No{shade}-real-shade-source-1080-QA.jpg"
 body.save(file,"JPEG",quality=94,optimize=True,subsampling=0)
 with Image.open(file) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080)
 assert file.stat().st_size<2_000_000
 assert sha(prod)==product_row["sha256"] and sha(swatch)==sm["new_sha256"]
 cards.append({"shade":shade,"shade_name":desc,"status":"NEW_QA_REFERENCE_HOLD_SALES",
   "image_JPG_1080":str(file),"sha256":sha(file),"bytes":file.stat().st_size,
   "regional_product_photo_src":str(prod),
   "regional_photo_sha256":product_row["sha256"],
   "Sagi_watermarked_swatches_src":str(swatch),
   "Sagi_image_SHA256":sm["new_sha256"],
   "swatch_zoom_source_crop_px":list(crop),
   "original_watermark_retained_in_full_photo":True,
   "swatch_pixels_recolored":False,
   "stock_Korean_edition_verified":False,
   "source_commercial_usage_allowed":False,
   "retail_approved":False})
assert len(cards)==2 and len({c["sha256"] for c in cards})==2
board=Image.new("RGB",(2240,1190),"#F0EDF1")
d=ImageDraw.Draw(board)
d.text((20,14),"v2873 | MISSHA MOIST UP NO21 + NO23 ORIGINAL PRODUCT & SAGE WATERMARK SOURCE | INTERNAL QA",
       font=ft(23,True),fill="#4B4250")
for i,x in enumerate(cards):
 with Image.open(x["image_JPG_1080"]) as im:
  board.paste(im.convert("RGB"),(15+1110*i,70))
 d.text((22+1110*i,1160),"NO."+x["shade"]+" | LICENSE & PHYSICAL EDITION HOLD",font=ft(19,True),fill="#57495A")
contact=OUT/"v2873-missha-moistup-two-actual-shade-swatch-comparison-QA.jpg"
board.save(contact,"JPEG",quality=88,optimize=True)
report={
 "version":"v2873","baseline":"v2872","family":"pending-02",
 "product":"MISSHA Magic Cushion Moist Up No.21 / No.23",
 "new_1080_shade_QA_JPGs":2,"new_product_photo_downloads":0,
 "input_photo_sources_archived_versions":["v2701","v2528"],
 "source_files_changed":0,"new_shade_pixels_synthesized":0,
 "watermark_removed_or_faked":False,
 "prior_11_completed_groups_preserved":True,
 "prior_55_public_URLs_preserved":True,
 "commercial_photo_rights_verified":False,
 "owned_Korean_stock_same_regional_edition_verified":False,
 "authenticated_original_MK_logo_applied":False,
 "sale_approvals":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,
 "cards":cards,"contact":str(contact),"contact_sha256":sha(contact),
 "next":"Review v2873 for correct 21 vs 23 group-swatch positioning and original watermark; exact KR stock packaging and reuse license are required before publication. Next SKU should progress without re-cutting v2873 photos."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2873","new_1080_QA_images":2,
                  "sha_unique":True,"old_files_modified":0,"retail_approved":0}))
