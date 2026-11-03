#!/usr/bin/env python3
"""v2532 append precisely ONE authentic photo-based CLIO Founwear 5-shade chart.
Input v2530b 155-JPG corrected corpus. Every prior file must remain byte-identical.
Actual five facial swatch colors (19C,19N,21C,21N,23N) are not generated/recolored.
Rights / stock packaging / original MK logo remain HOLD, no public URLs/XLSX.
"""
from pathlib import Path
from PIL import Image
import shutil,json,hashlib
BASE=Path("v2532-base-155/review-JPG-by-family")
SRC=Path("v2532-clio-original/07-clio-founwear-original-face-5shade.jpg")
assert BASE.is_dir() and SRC.is_file()
im=Image.open(SRC);im.load()
assert im.format=="JPEG" and im.size==(1080,1080)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=="9854f08c15b1a7d9514f1fdf2860277927f578b27510097e44b386c80aee356c"
O=Path("v2532-156-with-clio-founwear-5shade")
DST=O/"review-JPG-by-family"
shutil.copytree(BASE,DST)
target=DST/"pending-05/06-authentic-CLIO-founwear-five-face-swatches.jpg"
shutil.copy2(SRC,target)
old=list(BASE.glob("pending-*/*.jpg"))
new=list(DST.glob("pending-*/*.jpg"))
assert len(old)==155 and len(new)==156,(len(old),len(new))
for f in old:
 copied=DST/f.relative_to(BASE)
 assert copied.read_bytes()==f.read_bytes(),f
family_counts={f.name:len(list(f.glob("*.jpg"))) for f in DST.glob("pending-*")}
assert len(family_counts)==30
six={"pending-01","pending-02","pending-04","pending-05","pending-06","pending-07"}
assert all(family_counts[x]==(6 if x in six else 5) for x in family_counts)
for f in new:
 im=Image.open(f);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2_000_000
for fam in family_counts:
 sha=[hashlib.sha256(f.read_bytes()).hexdigest() for f in (DST/fam).glob("*.jpg")]
 assert len(set(sha))==len(sha)
m={"version":"v2532","date":"2026-11-04","new_image":"review-JPG-by-family/pending-05/06-authentic-CLIO-founwear-five-face-swatches.jpg",
"source_run":41707037373,"source_photo":"https://cdn.shopify.com/s/files/1/0668/0022/2505/files/Photoroom_20250416_121449.png?crop=center&height=1024&v=1744795011&width=960",
"source_SHA256":"8cd6b2e0003d571c5a8a2b0e429bb2e1cdca2d968d8ab38ee688cb6883c0554f",
"JPG_SHA256":hashlib.sha256(target.read_bytes()).hexdigest(),
"real_five_options":["19C Light","19N Porcelain","21C Lingerie","21N Linen","23N Ginger"],
"prior_155_files_byte_identical":True,"total_QA_JPGs":156,"30_families":True,
"photographic_pixels_unmodified":True,"fake_shades_generated":False,
"photo_commercial_rights_approved":False,"inventory_package_generation_verified":False,
"MK_logo_original_applied":False,"public_release_approved":False,"existing_public_URLs_unchanged":55,
"new_public_URLs":0,"xlsx_shared":False}
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total_QA_JPGs":156,"unchanged_originals":155,"new_genuine_five_shade":1}))
