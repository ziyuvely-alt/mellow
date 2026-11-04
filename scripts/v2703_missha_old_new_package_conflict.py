#!/usr/bin/env python3
"""v2703 create exact image proof of NEW vs OLD MISSHA M Perfect Cover BB Cream.
Never present redesigned US bottle as existing old Korean stock photo.
Reuse existing source file SHA and preserve approved public assets.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json,base64
QA=Path("qa-review")
OLD=QA/"v2682-seven-remaining-five-JPG-reviews"/"pending-03"
NEW=QA/"v2702-missha-M-perfect-cover-BB-official-photo-proof"
OUT=QA/"v2703-MISSHA-BB-old-vs-new-package-identity-hold"
assert OLD.is_dir() and NEW.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=list(OLD.glob("01-*.jpg"))
assert len(prior)==1
sources=[
  (prior[0],"01-HISTORICAL-old-gold-pump-KR-QA.jpg"),
  (NEW/"02-MISSHA-US-actual-source-reference.jpg","02-BRAND-UPDATE-NOTICE-REFERENCE-DO-NOT-UPLOAD.jpg"),
  (NEW/"01-MISSHA-US-actual-source-reference.jpg","03-NEW-US-pink-red-tube-REFERENCE-DO-NOT-UPLOAD.jpg")
]
manifest={"version":"v2703","family":"pending-03",
"product":"MISSHA M Perfect Cover BB Cream 50mL",
"current_old_inventory_image_source":"v2682 pending-03 old gold-pump tube",
"verified_official_US_current_design_changed":True,
"new_current_US_box_should_replace_old_stock_gallery":False,
"shades_US_21_23_25_numbered_present":True,
"identity_status":"HOLD_OLD_VS_NEW_PACKAGE_GENERATION_NOT_PHOTO_MATCHED",
"retail_approved":False,"copy_unchanged_SHA":[],
"public_55_urls_modified":False,"approved_11_product_families_unchanged":True,
"final_spreadsheet_shared":False}
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(fontfile,24)
board=Image.new("RGB",(1515,650),"#f2f0ef")
d=ImageDraw.Draw(board)
d.text((18,14),"v2703 OLD-KOREAN STOCK vs NEW-US BRAND PACKAGING / HOLD",font=font,fill="#292929")
labels=["HISTORICAL OLD TUBE","OFFICIAL REDESIGN NOTICE","CURRENT US NEW DESIGN"]
for n,(source,name) in enumerate(sources):
 assert source.exists(),source
 target=OUT/name
 shutil.copy2(source,target)
 assert sha(target)==sha(source)
 with Image.open(target) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  thumb=im.convert("RGB").resize((445,445),Image.Resampling.LANCZOS)
 x=20+n*500
 board.paste(thumb,(x,63))
 d.text((x,520),labels[n],font=font,fill="#292929")
 manifest["copy_unchanged_SHA"].append({"file":target.name,"sha256":sha(target),"source":str(source)})
proof=OUT/"v2703-design-conflict-proof.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2703-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"different_packaging_confirmed":True,"reference_JPGs":3,
 "new_sale_ready":0,"old_photos_sha_preserved":True}))
