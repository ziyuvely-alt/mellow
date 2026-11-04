#!/usr/bin/env python3
"""v2576: promote ONLY five customer-copy-corrected JPGs to isolated latest QA
delta. All 156 existing source candidates kept unchanged, and 55 published URLs
untouched. A single full-frame pass proves integrity and similarity.
No content license or physical product claims and NO public deployment.
"""
from pathlib import Path
from PIL import Image, ImageOps
from itertools import combinations
import hashlib,json
BASE=Path("v2576-prior/review-JPG-by-family")
FIX=Path("v2576-fixed")
OUT=Path("v2576-incremental-five-photo-corrections")
OUT.mkdir(exist_ok=True)
source=json.loads((FIX/"manifest.json").read_text())
assert source["version"]=="v2574" and len(source["candidate_corrections"])==5
S={(x["family"],x["slot"]):x for x in source["candidate_corrections"]}
assert set(S)=={("pending-21",5),("pending-16",4),("pending-26",5),("pending-01",5),("pending-06",5)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 pix=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 n=0
 for row in range(8):
  for col in range(8):n=(n<<1)|(pix[row*9+col]>pix[row*9+col+1])
 return n
manifest=[]
all_hashes={}
flags=[]
for i in range(1,31):
 fam=f"pending-{i:02d}"
 source_images=sorted((BASE/fam).glob("*.jpg"))
 expected=6 if i in (1,2,4,5,6,7) else 5
 assert len(source_images)==expected,(fam,len(source_images),expected)
 image_hashes=[];identities=[]
 for p in source_images:
  slot=int(p.name[:2]);key=(fam,slot)
  assert key not in all_hashes,key
  chosen=p
  if key in S:
   c=S[key]
   chosen=FIX/c["correction_file"]
   assert chosen.is_file(),chosen
   assert sha(chosen)==c["correction_sha256"]
   assert sha(chosen)!=sha(p),"Correction identical to earlier retained candidate"
   dst=OUT/f"{fam}-slot{slot:02d}-customer-copy-QA.jpg"
   dst.write_bytes(chosen.read_bytes())
   assert sha(dst)==sha(chosen)
   manifest.append({"family":fam,"slot":slot,"old_sha256":sha(p),"new_sha256":sha(dst),
      "new_file":dst.name,"customer_copy_fixed":True,"published":False})
  im=Image.open(chosen);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and chosen.stat().st_size<2000000
  h=sha(chosen)
  image_hashes.append(h)
  identities.append((slot,dhash(im)))
  all_hashes[key]=h
 assert len(set(image_hashes))==expected
 for (n,a),(m,b) in combinations(identities,2):
  if (a^b).bit_count()<=6:flags.append({"family":fam,"slots":[n,m],"dhash_distance":(a^b).bit_count()})
assert len(all_hashes)==156 and len(manifest)==5
assert len(list(OUT.glob("*.jpg")))==5
# Prevent premature release even if full technical QA passes.
m={"version":"v2576","source_run":41753618979,"corrections_run":41760689379,
 "validated_images":156,"families":30,"image_delta_count":5,
 "other_images_fully_preserved":151,
 "previous_six_corrections_reused":True,
 "no_original_jpg_recreated_or_overwritten":True,
 "previous_55_public_urls_changed":0,"published_urls_new":0,
 "unchanged_source_families":25,"xlsx_generated_or_shared":False,
 "technical_similarity_review_candidates":flags,"source_hash_map":{f"{k[0]}:{k[1]}":v for k,v in all_hashes.items()},
 "new_image_deltas":manifest,"commercial_photo_rights_verified":False,
 "stock_generation_verified":False,"MK_original_logo_included":False,
 "final_sale_approved":False,
 "next_step":"Review image claims and verify owned stock/license/logo; then decide sale approval per family, no automatic publishing."}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"families":30,"checked":156,"new_delta_jpg":5,"unchanged_sha_count":151,
"near_duplicate_alerts":len(flags),"published":0,"XLSX":False}))
