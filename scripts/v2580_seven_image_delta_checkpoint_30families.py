#!/usr/bin/env python3
"""v2580 isolated 7-photo incremental QA checkpoint:
- preserve five earlier corrected customer-ready text proposals unchanged
- add two actual distinct OBgE 50mL source-backed photo scenes in pending23 slots4,5
- preserve remaining 149 JPG sha bytes from v2560
- no publication, no rights/stock/MK claims, no spreadsheets
"""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageOps
from itertools import combinations
BASE=Path("v2580-baseline/review-JPG-by-family")
OLD=Path("v2580-five")
NEW=Path("v2580-two")
OUT=Path("v2580-seven-image-reusable-QA-deltas");OUT.mkdir(exist_ok=True)
old_manifest=json.loads((OLD/"manifest.json").read_text())
new_manifest=json.loads((NEW/"manifest.json").read_text())
assert old_manifest["version"]=="v2576" and new_manifest["version"]=="v2579"
assert len(old_manifest["new_image_deltas"])==5 and len(new_manifest["selected"])==2
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
replacements={}
for r in old_manifest["new_image_deltas"]:
 p=OLD/r["new_file"]
 assert p.is_file() and sha(p)==r["new_sha256"]
 replacements[(r["family"],r["slot"])]=p
for slot,r in zip((4,5),new_manifest["selected"]):
 p=NEW/r["candidate_selected_file"]
 assert p.is_file() and sha(p)==r["candidate_sha256"]
 replacements[("pending-23",slot)]=p
assert len(replacements)==7
assert all(p.exists() for p in replacements.values())
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 n=0
 for y in range(8):
  for x in range(8):n=(n<<1)|(p[y*9+x]>p[y*9+x+1])
 return n
all_old={};all_new={};overlays=[];near=[]
for idx in range(1,31):
 fam=f"pending-{idx:02d}"
 paths=sorted((BASE/fam).glob("*.jpg"))
 assert len(paths)==(6 if idx in (1,2,4,5,6,7) else 5)
 family_photos=[]
 for p in paths:
  slot=int(p.name[:2]);k=(fam,slot)
  oldsha=sha(p)
  all_old[k]=oldsha
  s=replacements.get(k,p)
  newsha=sha(s)
  all_new[k]=newsha
  im=Image.open(s);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and s.stat().st_size<2_000_000
  family_photos.append((slot,newsha,dhash(im)))
  if k in replacements:
   assert oldsha!=newsha
   dest=OUT/f"{fam}-slot{slot:02d}-v2580-review-only.jpg"
   dest.write_bytes(s.read_bytes())
   assert sha(dest)==newsha
   overlays.append({"family":fam,"slot":slot,"previous_sha256":oldsha,
       "candidate_sha256":newsha,"saved_QA_candidate":dest.name,
       "source_provenance":"v2579-two-independent-real-retailer-photos-rights-HOLD" if fam=="pending-23" else "v2576-corrected-copy-photo",
       "sales_approved":False})
 assert len({x[1] for x in family_photos})==len(family_photos)
 for a,b in combinations(family_photos,2):
  dist=(a[2]^b[2]).bit_count()
  if dist<=6:near.append({"family":fam,"slots":[a[0],b[0]],"distance":dist})
assert len(all_old)==len(all_new)==156
assert len(overlays)==7
assert sum(all_old[k]==all_new[k] for k in all_old)==149
assert not near,near
report={"version":"v2580",
 "base_candidate_run":41753618979,"prior_five_fixes_run":41761227478,
 "obge_independent_photo_selection_run":41762139786,
 "family_count":30,"qa_images_verified":156,"actual_candidate_deltas":7,
 "other_unchanged_JPGs_hash_identical":149,
 "new_distinct_original_photos_to_OBGE_pending23":2,
 "previous_five_customer_copy_corrections_preserved":5,
 "duplicates_dhash_threshold_le6":len(near),
 "source_photo_commercial_usage_rights_verified":False,
 "owned_stock_physical_packaging_verified":False,
 "original_mellowkr_MK_logo_applied":False,
 "release_approved":False,"previous_public_55_urls_modified":0,
 "new_public_urls":0,"xlsx_created_or_shared":False,
 "overlays":overlays}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"verified":156,"delta":7,"sha_untouched":149,
"distinct_obge_photos_added_in_QA":2,"near_duplicates":len(near),
"published":False,"xlsx":False}))
