#!/usr/bin/env python3
"""Append a single genuine MISSHA Magic Cushion Moist Up #21/#23 source swatch as QA ONLY.
Keep Sagi source watermark intact, do not alter original swatch colors. Its
commercial reuse permission and user's specific package edition remain unverified.
Original 154 files are byte-identical. Never publish or create Excel.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,shutil
src=Path("v2528-original-missha/sagi-real-two-shades.webp")
base=Path("v2528-baseline-154/review-JPG-by-family")
assert src.is_file() and base.is_dir()
assert hashlib.sha256(src.read_bytes()).hexdigest()=="b02107a23bccf3e1b3130ace63f3640da43ece586633b71160e3a6540ef6da2f"
photo=Image.open(src);photo.load()
assert photo.size==(600,600) and photo.format=="WEBP"
out=Path("v2528-155-real-missha-moistup-QA")
dst=out/"review-JPG-by-family";shutil.copytree(base,dst)
image=photo.convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
p=dst/"pending-02/06-original-21-23-shades-watermarked-QA.jpg"
image.save(p,"JPEG",quality=94,optimize=True,subsampling=0)
assert Image.open(p).size==(1080,1080) and p.stat().st_size<2000000
prior=list(base.glob("pending-*/*.jpg"));now=list(dst.glob("pending-*/*.jpg"))
assert len(prior)==154 and len(now)==155,(len(prior),len(now))
for f in prior:assert f.read_bytes()==(dst/f.relative_to(base)).read_bytes(),str(f)
families={f.name:len(list(f.glob("*.jpg"))) for f in dst.glob("pending-*")}
assert len(families)==30
assert all(n==6 for f,n in families.items() if f in {"pending-01","pending-02","pending-04","pending-06","pending-07"})
assert all(n==5 for f,n in families.items() if f not in {"pending-01","pending-02","pending-04","pending-06","pending-07"})
for f in now:
 im=Image.open(f);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2000000
assert all(len({hashlib.sha256(f.read_bytes()).hexdigest() for f in (dst/fam).glob("*.jpg")})==n for fam,n in families.items())
m={"version":"v2528","date":"2026-11-04","total_review_JPGs":155,"original_154_images_byte_identical":True,
"new_image":str(p.relative_to(out)),"new_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
"source_photo":"https://bizweb.dktcdn.net/100/443/867/products/cushion-duong-am-missha-magic-cushion-moist-up-spf50-plus-pa-plus-plus-plus.png?v=1701087892520",
"source_sha256":"b02107a23bccf3e1b3130ace63f3640da43ece586633b71160e3a6540ef6da2f",
"photo_source_watermark_preserved":True,"source_image_shades":["#21","#23"],
"exact_stock_package_edition_verified":False,"commercial_photo_usage_rights_verified":False,
"product_original_MK_logo_applied":False,"sales_ready":False,
"previous_55_verified_public_URLs_unchanged":True,"new_public_URLs":0,"spreadsheet_created_or_shared":False,
"reason_for_hold":"Sagi-watermarked retailer photo is an authentic QA reference, not licensed merchant artwork."}
out.mkdir(exist_ok=True)
(out/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
print(json.dumps({"QA_images":155,"untouched":154,"new_real_swatches":1,"sales_ready":False}))
