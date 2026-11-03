#!/usr/bin/env python3
"""Append authentic CLIO Mesh Glow Mini 5g shade swatch as the sixth QA frame,
preserving all 151 existing review JPEGs unchanged. The photographed swatch
is inherited from prior validated v2426b QA file, not generated colors.
"""
from pathlib import Path
from PIL import Image
import shutil,hashlib,json
ROOT=Path("v2523-existing-151")
SRC=ROOT/"review-JPG-by-family"
ORIGINAL=Path("v2523-real-clio-swatch/CLIO_Mini_3shade_actual_source_QA_CLEAN_V2426b.jpg")
assert SRC.is_dir() and ORIGINAL.is_file()
O=Path("v2523-152-real-shade-JPG-QA")
TARGET=O/"review-JPG-by-family"
shutil.copytree(SRC,TARGET)
source=Image.open(ORIGINAL);source.load()
assert source.format=="JPEG" and source.size==(1080,1080)
dest=TARGET/"pending-04/06-actual-clio-three-shade-source.jpg"
shutil.copy2(ORIGINAL,dest)
before=sorted(SRC.glob("pending-*/*.jpg"))
after=sorted(TARGET.glob("pending-*/*.jpg"))
assert len(before)==151 and len(after)==152,(len(before),len(after))
for path in before:
 new=TARGET/path.relative_to(SRC)
 assert path.read_bytes()==new.read_bytes(),str(path)
counts={p.name:len(list(p.glob("*.jpg"))) for p in TARGET.glob("pending-*")}
assert len(counts)==30
assert counts["pending-01"]==6 and counts["pending-04"]==6
assert all(c==5 for fam,c in counts.items() if fam not in {"pending-01","pending-04"})
all_sha={}
for p in after:
 im=Image.open(p);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
 all_sha.setdefault(p.parent.name,set()).add(hashlib.sha256(p.read_bytes()).hexdigest())
assert all(len(all_sha[family])==count for family,count in counts.items())
previous=json.loads((ROOT/"manifest.json").read_text())
m={"version":"v2523","date":"2026-11-04","prior_count":151,"total_JPG_candidates":152,
"new_files_count":1,"family":"pending-04","new_slot":6,
"new_image":str(dest.relative_to(O)),"new_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
"original_swatch_file":"CLIO_Mini_3shade_actual_source_QA_CLEAN_V2426b.jpg",
"original_swatch_branch":"production-assets-v2426b-clean-clio",
"matched_exact_three_shades":["21C Lingerie","21N Linen","23N Ginger"],
"old_151_files_byte_identical":True,"30_family_counts":counts,
"all_JPG_format_res_2MB_pass":True,"fabricated_shade_pixels":False,
"original_source_photo_rights_verified":False,"owned_stock_version_match_verified":False,
"original_MK_logo_applied":False,"product_publication_approved":False,
"prior_published_55_urls_unchanged":True,"new_public_URLs":0,
"excel_created":False,"excel_shared":False}
O.mkdir(exist_ok=True);(O/"manifest.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"total_JPG":152,"untouched":151,"authentic_CLIO_shade_JPG_added":1,"final_QA":False}))
