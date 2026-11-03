#!/usr/bin/env python3
"""Append actual photographic five-shade CLIO Mesh Glow Essential Cushion set (pending-06).
Conservative source-first approach; never manufacture shade/texture swatch pixels.
All 152 old QA JPEGs retained byte-identically, no sales/public URLs/Excel.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image
import hashlib,shutil,json
ROOT=Path("v2524-base-152")
SRC=ROOT/"review-JPG-by-family"
OUT=Path("v2524-153-actual-CLIO-five-shade-QA")
TARGET=OUT/"review-JPG-by-family"
assert SRC.is_dir()
shutil.copytree(SRC,TARGET)
urls=[
"https://www.ballagrio.com/cdn/shop/files/12_8892f631-07c7-469c-900d-bee9719219e1.png?v=1749669982&width=1200",
"https://cdn11.bigcommerce.com/s-noog3x4u9a/images/stencil/1280x1280/products/9224/27814/Screenshot_2025-12-18_122613__73856.1766060953.jpg?c=2"
]
source=None;origin=None;original_size=None
for url in urls:
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/jpeg,image/webp,*/*"}),timeout=20) as response: raw=response.read(6_000_001)
  assert len(raw)<6_000_000
  img=Image.open(BytesIO(raw));img.load()
  assert img.format in ("PNG","JPEG","WEBP") and min(img.size)>=450
  source=img.convert("RGB");origin=url;original_size=img.size
  break
 except Exception as e:
  print("source blocked:",url,str(e)[:120])
assert source is not None,"No valid genuine 5 shade source: hold this family, don't synthesize shades"
# Respect entire original image and accurate photo shade labels; never invent/re-color.
dst=TARGET/"pending-06/06-clio-mesh-glow-5-real-swatches.jpg"
source.resize((1080,1080),Image.Resampling.LANCZOS).save(dst,"JPEG",quality=94,subsampling=0,optimize=True)
assert Image.open(dst).size==(1080,1080) and dst.stat().st_size<2_000_000
old=list(SRC.glob("pending-*/*.jpg"))
new=list(TARGET.glob("pending-*/*.jpg"))
assert len(old)==152 and len(new)==153
for f in old:
 assert f.read_bytes()==(TARGET/f.relative_to(SRC)).read_bytes(),str(f)
counts={p.name:len(list(p.glob("*.jpg"))) for p in TARGET.glob("pending-*")}
assert len(counts)==30
assert counts["pending-06"]==6 and counts["pending-01"]==6 and counts["pending-04"]==6
assert all(v==5 for k,v in counts.items() if k not in {"pending-01","pending-04","pending-06"})
for family,items in counts.items():
 files=list((TARGET/family).glob("*.jpg"))
 assert len({hashlib.sha256(f.read_bytes()).hexdigest() for f in files})==items
 for f in files:
  im=Image.open(f); im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2_000_000
manifest={"version":"v2524","date":"2026-11-04","family":"pending-06","product":"CLIO Kill Cover Mesh Glow Essential Cushion Set 15g + refill 15g",
"new_file":str(dst.relative_to(OUT)),"source_original_url":origin,"source_dimensions":original_size,
"sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
"exact_real_shades":["19C Light","19N Porcelain","21C Lingerie","21N Linen","23N Ginger"],
"source_sale_url":"https://www.ballagrio.com/products/clio-kill-cover-mesh-glow-essential-cushion-with-refill-5-colors-15g-2ea",
"official_option_identity":"https://clubclio.shop/products/clio-kill-cover-mesh-glow-cushion-set-refill",
"old_152_JPGs_byte_identical":True,"total_JPG_QA":153,"added_only":1,"all_30_families_have_five_or_six":True,
"photos_real_no_synthetic_shade_pixels":True,"source_license_verified":False,"physical_stock_edition_QA_verified":False,
"original_MK_logo_applied":False,"public_sale_ready":False,"previous_published_55_urls_untouched":True,
"new_public_url_count":0,"Excel_created_or_shared":False}
OUT.mkdir(exist_ok=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"total":153,"retained_unchanged":152,"new_real_shade_photo_count":1,"released":False}))
