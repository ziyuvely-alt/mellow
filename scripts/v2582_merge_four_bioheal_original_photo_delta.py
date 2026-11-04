#!/usr/bin/env python3
"""v2582: QA-only aggregate checkpoint with 7 existing image deltas and 4 NEW
BIOHEAL BOH real product source photographs for slots 03/05 of pending24/25.
Keeps all original 156 JPG unchanged and 145 base slots byte-identical.
Never release without copyright, exact stock and human package checks.
"""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageOps
from itertools import combinations
BASE=Path("v2582-base/review-JPG-by-family")
SEVEN=Path("v2582-seven")
BOH=Path("v2582-boh")
O=Path("v2582-11-change-photo-QA-delta");O.mkdir(exist_ok=True)
a=json.loads((SEVEN/"manifest.json").read_text())
b=json.loads((BOH/"manifest.json").read_text())
assert a["version"]=="v2580" and a["actual_candidate_deltas"]==7
assert b["version"]=="v2581" and b["source_images_saved"]==4 and b["distinct_photo_candidates"]==4
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changes={}
for x in a["overlays"]:
 p=SEVEN/x["saved_QA_candidate"]
 assert p.is_file() and sha(p)==x["candidate_sha256"]
 changes[(x["family"],x["slot"])]=(p,"v2580_preexisting_7_deltas")
for family,prefix in [("pending-24",["01","02"]),("pending-25",["03","04"])]:
 subset=[x for x in b["candidate_results"] if x["family"]==family and x["status"]=="NEW_DISTINCT_CANDIDATE_QA_ONLY"]
 assert len(subset)==2
 for slot,x in zip((3,5),subset):
  p=BOH/x["jpg_file"]
  assert p.is_file() and sha(p)==x["new_JPG_sha256"]
  assert (family,slot) not in changes
  changes[(family,slot)]=(p,"v2581_real_retailer_photo_external_rights_hold")
assert len(changes)==11
def dhash(im):
 q=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 h=0
 for i in range(8):
  for j in range(8):h=(h<<1)|(q[i*9+j]>q[i*9+j+1])
 return h
seen=set();pairs=[];deltas=[];unmodified=0
for n in range(1,31):
 fam=f"pending-{n:02d}"
 old=sorted((BASE/fam).glob("*.jpg"))
 assert len(old)==(6 if n in (1,2,4,5,6,7) else 5)
 photo_hashes=[];photo_dhash=[]
 for p in old:
  slot=int(p.name[:2]);key=(fam,slot)
  assert key not in seen;seen.add(key)
  src,why=changes.get(key,(p,"original"))
  im=Image.open(src);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and src.stat().st_size<2_000_000
  photo_hashes.append(sha(src));photo_dhash.append((slot,dhash(im)))
  if key in changes:
   assert sha(src)!=sha(p)
   dst=O/f"{fam}-slot{slot:02d}-v2582-QA.jpg"
   dst.write_bytes(src.read_bytes())
   assert sha(dst)==sha(src)
   deltas.append({"family":fam,"slot":slot,"old_sha256":sha(p),"new_sha256":sha(dst),
      "qa_file":dst.name,"source":why,"approval":"HOLD_COMMERCIAL_RIGHTS_STOCK_EDITION_MK_AND_VISUAL_QA"})
  else:
   assert sha(src)==sha(p)
   unmodified+=1
 assert len(set(photo_hashes))==len(photo_hashes)
 for x,y in combinations(photo_dhash,2):
  distance=(x[1]^y[1]).bit_count()
  if distance<=6:pairs.append({"family":fam,"slots":[x[0],y[0]],"distance":distance})
assert len(seen)==156 and len(deltas)==11 and unmodified==145
assert not pairs,pairs
report={"version":"v2582","families_checked":30,"QA_JPGs_checked":156,
"modified_only_in_separate_QA_delta":11,"underlying_JPGs_byte_preserved":145,
"prior_7_changes_reused":7,"new_BIOHEAL_24_25_source_photo_overlays":4,
"similarity_alerts_at_dhash_6":len(pairs),
"approved_commercial_use":False,"actual_stock_edition_verified":False,
"original_mellowkr_MK_logo_applied":False,"sales_approved":False,
"existing_public_55_URLs_modified":0,"new_public_urls":0,"xlsx_created_or_shared":False,
"changes":deltas}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"reviewed":156,"changed":11,"untouched":145,
"new_bioheal_qa_scenes":4,"near_dup_alerts":len(pairs),
"published":0,"excel_shared":False}))
