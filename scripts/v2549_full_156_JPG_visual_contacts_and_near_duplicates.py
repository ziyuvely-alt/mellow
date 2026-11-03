#!/usr/bin/env python3
"""v2549 full QA of all 156 physical JPEGs in latest Shopee 30-family review corpus.
Generate contact sheets grouped by five families (NOT public sales images), quantify
EXACT hash duplicate and strict near-duplicate perceptual dHash <=6, and record
explicit release blockers (photo rights, MK original, physical package, color swatches).
Never delete files, never publish URLs, never create Excel.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from itertools import combinations
import hashlib,json,shutil
B=Path("v2549-input-156/review-JPG-by-family")
assert B.is_dir()
O=Path("v2549-30family-all156-visual-review");O.mkdir(exist_ok=True)
f=lambda n:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
def dhash(im):
 pixels=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 result=0
 for y in range(8):
  for x in range(8):
   result=(result<<1)|(pixels[y*9+x]>pixels[y*9+x+1])
 return result
family_data={}
all_records=[]
similar=[]
for n in range(1,31):
 fam=f"pending-{n:02d}"
 paths=sorted((B/fam).glob("*.jpg"))
 assert len(paths)==(6 if n in (1,2,4,5,6,7) else 5),(fam,len(paths))
 images=[]
 for p in paths:
  img=Image.open(p);img.load()
  size=p.stat().st_size
  assert img.format=="JPEG" and img.size==(1080,1080) and size<2_000_000,(p,img.size,size)
  rec={"family":fam,"filename":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
    "size_bytes":size,"slot":int(p.name[:2]),"dhash":dhash(img)}
  all_records.append(rec);images.append((p,img,rec))
 assert len({x[2]["slot"] for x in images})==len(images)
 for a,b in combinations(images,2):
  distance=(a[2]["dhash"]^b[2]["dhash"]).bit_count()
  if distance<=6:
   similar.append({"family":fam,"file_a":a[0].name,"file_b":b[0].name,"dhash_distance":distance,
     "exact_hash_identical":a[2]["sha256"]==b[2]["sha256"],
     "status":"MANUAL_SCENE_REVIEW_REQUIRED_NOT_AUTO_DELETE"})
 family_data[fam]={"count":len(paths),"files":[x[2]["filename"] for x in images]}
# Six contact sheets of five product groups: images are thumbnail previews for manual inspection only.
for first in range(1,31,5):
 sheet=Image.new("RGB",(1760,6*390),"#ececeb")
 d=ImageDraw.Draw(sheet)
 for row,n in enumerate(range(first,min(first+5,31))):
  fam=f"pending-{n:02d}"
  imgs=sorted((B/fam).glob("*.jpg"))
  for col,path in enumerate(imgs):
   pic=Image.open(path).convert("RGB")
   thumbnail=ImageOps.contain(pic,(282,322),Image.Resampling.LANCZOS)
   x=col*290+(290-thumbnail.width)//2
   y=row*390+18+(330-thumbnail.height)//2
   sheet.paste(thumbnail,(x,y))
   d.text((col*290+10,row*390+349),f"{fam} / {path.name[:2]}",font=f(20),fill="#232323")
 p=O/f"contact-families-{first:02d}-{first+4:02d}.jpg"
 sheet.save(p,"JPEG",quality=83,optimize=True)
# Preserve only a manifest, not user Excel.
report={"version":"v2549","date":"2026-11-04","source_latest_run":41715911900,
"total_physical_JPEGs":len(all_records),"total_families":len(family_data),
"all_files_1080_1080_JPG_below_2mb":True,
"total_expected_single_or_option_image_frames":156,"exact_sha_duplicates":[],
"perceptual_dhash_0_to_6_candidates":similar,
"near_duplicate_candidate_count":len(similar),
"families":family_data,"file_records":all_records,
"workbook_created":False,"workbook_shared":False,
"original_55_verified_public_urls_preserved":True,"new_public_urls":0,
"sales_release_approved":False,
"remaining_blockers":["Original round MellowKR MK logo image still inaccessible","Source commercial reuse rights require confirmation",
  "Exact owned stock product generation photos not all confirmed, notably Pixelpure cleanser 145ml",
  "Peripera 26AD 01-20 true official swatch chart and some other optioned products still QA-hold",
  "Per-family full visual/claims review requires human or visual confirmation, not only dHash or size"],
"note":"JPG counts and dHash are technical checks, not commercial product-final approval. Never modify user's completed 11 families or 55 verified URLs."}
assert len(all_records)==156,len(all_records)
assert not any(a["sha256"]==b["sha256"] for a,b in combinations(all_records,2) if a["family"]==b["family"])
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"image_count":len(all_records),"families":len(family_data),
"perceptual_near_pairs":len(similar),"contact_sheets":6,"sales_ready":False}))
