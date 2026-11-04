#!/usr/bin/env python3
"""v2584 manifest-only incremental checkpoint: preserve v2582's eleven unchanged
JPG bytes and add only the one verified OBgE double essence 50mL+50mL info
card from v2583. Do NOT re-evaluate all 156 or reupload existing 11 JPGs.
No public images or sales acceptance. Future reconstruct via manifest provenance.
"""
from pathlib import Path
from PIL import Image,ImageOps
from itertools import combinations
import hashlib,json
OLD=Path("v2584-prev")
NEW=Path("v2584-obge")
BASE=Path("v2584-base/review-JPG-by-family/pending-11")
OUT=Path("v2584-twelve-photo-incremental-manifest-only");OUT.mkdir(exist_ok=True)
p=json.loads((OLD/"manifest.json").read_text())
n=json.loads((NEW/"manifest.json").read_text())
assert p["version"]=="v2582" and p["modified_only_in_separate_QA_delta"]==11
assert n["version"]=="v2583" and n["family"]=="pending-11"
candidate=NEW/n["new_qa_image_file"]
assert candidate.is_file()
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(candidate)==n["QA_candidate_sha256"]
files=sorted(BASE.glob("*.jpg"))
assert len(files)==5
oldslot=[x for x in files if x.name.startswith("05")]
assert len(oldslot)==1 and sha(oldslot[0])==n["old_slot05_sha256"]
assert not any(x["family"]=="pending-11" and x["slot"]==5 for x in p["changes"])
img=Image.open(candidate);img.load()
assert img.format=="JPEG" and img.size==(1080,1080) and candidate.stat().st_size<2_000_000
dst=OUT/"pending-11-slot05-factual-50plus50-QA.jpg"
dst.write_bytes(candidate.read_bytes())
assert sha(dst)==sha(candidate)
def dhash(im):
 pixels=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 h=0
 for y in range(8):
  for x in range(8):h=(h<<1)|(pixels[y*9+x]>pixels[y*9+x+1])
 return h
newhash=dhash(img)
distances={}
for x in files:
 if x==oldslot[0]:continue
 s=int(x.name[:2])
 dist=(newhash^dhash(Image.open(x))).bit_count()
 distances[str(s)]=dist
assert all(d>6 for d in distances.values()),distances
preserved=[{"family":x["family"],"slot":x["slot"],"new_sha256":x["new_sha256"],"source_checkpoint":"v2582"} for x in p["changes"]]
append={"family":"pending-11","slot":5,"previous_sha256":n["old_slot05_sha256"],
 "new_sha256":sha(dst),"qa_file":dst.name,"source_checkpoint":"v2583",
 "scene_source":"saved original exact product photo slot02, customer factual 50mL+50mL"}
report={"version":"v2584","base_156_run":41753618979,
 "previous_eleven_run":41762644574,
 "new_product_card_run":41762824246,
 "previous_eleven_photo_hashes_preserved_from_manifest":True,
 "new_jpg_created_in_this_run":0,"new_card_copied_from_v2583":1,
 "total_approved_for_QA_overlay":12,"other_144_original_frame_sha_untouched_by_virtual_overlay":True,
 "new_card_dhash_against_unchanged_pending11_slots":distances,
 "source_photo_rights_verified":False,"actual_owned_stock_edition_verified":False,
 "logo_original_verified":False,"sales_release_approved":False,
 "public_55_URLs_changed":0,"xlsx_created_or_shared":False,
 "previous_eleven":preserved,"new_delta":append}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"older_eleven_deltas_reused":11,"one_new_QA_card":1,
"latest_12_delta_checkpoint":True,"full_156_rerun":False,
"public_URLs_changed":0,"xlsx_shared":False}))
