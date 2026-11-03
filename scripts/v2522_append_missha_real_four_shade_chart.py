#!/usr/bin/env python3
"""Add one verified photographed MISSHA Magic Cushion Cover Lasting shade reference,
21/23/25/27, to 150 QA-only JPEGs; don't fabricate swatches, alter 150, or publish.
"""
from pathlib import Path
from PIL import Image
import io,shutil,json,hashlib
BASE=Path("v2522-inputs")
SRC=BASE/"review-JPG-by-family"
OUT=Path("v2522-151-physical-JPG-review")
TARGET=OUT/"review-JPG-by-family"
assert SRC.is_dir()
shutil.copytree(SRC,TARGET)
orig=BASE/"real-source/cosmic-four-shades.jpg"
assert orig.exists()
im=Image.open(orig).convert("RGB")
assert im.size==(800,800),im.size
dst=TARGET/"pending-01/06-real-source-21-23-25-27-shades.jpg"
im.resize((1080,1080),Image.Resampling.LANCZOS).save(dst,"JPEG",quality=93,optimize=True,subsampling=0)
b=dst.read_bytes()
assert len(b)<2_000_000 and Image.open(dst).size==(1080,1080)
old_manifest=json.loads((BASE/"manifest.json").read_text())
c=0
for f in SRC.glob("pending-*/*.jpg"):
 copy=TARGET/f.parent.name/f.name
 assert copy.read_bytes()==f.read_bytes(),str(f)
 c+=1
assert c==150
counts={family.name:len(list(family.glob("*.jpg"))) for family in TARGET.glob("pending-*")}
assert len(counts)==30
assert counts["pending-01"]==6 and all(n==5 for k,n in counts.items() if k!="pending-01")
manifest={"date":"2026-11-04","version":"v2522","retained_150_original_files_byte_identical":True,
"new_JPGs_created":1,"total_JPG_candidates":151,
"added_family":"pending-01","added_slot":6,"new_file":str(dst.relative_to(OUT)),
"new_SHA256":hashlib.sha256(b).hexdigest(),"original_source_SHA256":hashlib.sha256(orig.read_bytes()).hexdigest(),
"shade_options":["21","23","25","27"],"shade_original":"https://cosmic.net.ua/image/cache/catalog/0011/000000000051-800x800.jpg",
"color_generation_or_artificial_swatch_pixels":False,"official_brand_approval":False,
"stock_edition_matched":False,"commercial_photo_rights_verified":False,"MK_original_logo_present":False,
"sale_approval":False,"verified_55_URLs_unchanged":True,"new_public_URLs":0,"excel_created_or_shared":False,
"critical_note":"Photographic shade chart staged solely for QA. Do not publish before source license and stock edition crosscheck."}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"total":151,"untouched":150,"added_real_color_reference":1,"sale_approved":False}))
