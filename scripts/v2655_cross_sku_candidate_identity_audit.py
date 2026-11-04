#!/usr/bin/env python3
"""v2655 cross-product contamination audit for all 14 existing QA candidate jpgs.
Only reads already-made images, no repeated generation or sales publication.
Compare candidate perceptual hashes with the entire historic 156-JPG corpus.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageStat
from collections import defaultdict
from itertools import combinations
import hashlib,json,csv
ROOT=Path("source")
OUT=Path("v2655-cross-sku-photo-identity-audit");OUT.mkdir(exist_ok=True)
def dhash(image):
    p=list(ImageOps.grayscale(image).resize((9,8)).getdata())
    return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
def phash(path):
    with Image.open(path) as image:
        image.load()
        assert image.format=="JPEG" and image.size==(1080,1080)
        return dhash(image)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def hamming(a,b):return (a^b).bit_count()
base=ROOT/"historical/review-JPG-by-family"
hist=[]
for p in sorted(base.glob("pending-*/*.jpg")):
    hist.append({"family":p.parent.name,"slot":int(p.name[:2]),"sha256":sha(p),"dhash":phash(p),"source":"historical"})
assert len(hist)==156
artifacts=[
  ("v2651",ROOT/"v2651","pending-05"),
  ("v2652",ROOT/"v2652","pending-07"),
  ("v2653",ROOT/"v2653",None)]
candidates=[]
for version,root,forced in artifacts:
    found=list(root.glob("*-QA-ONLY.jpg"))
    if version!="v2653":
        assert len(found)==1,(version,found)
    else:assert len(found)==12,len(found)
    for p in found:
        fam=forced or p.name[:10]
        assert fam.startswith("pending-")
        candidates.append({"family":fam,"file":p.name,"version":version,"dhash":phash(p),
                           "sha256":sha(p),"bytes":p.stat().st_size})
assert len(candidates)==14,len(candidates)
pairs=[]
for cand in candidates:
    nearest=sorted([{"family":ref["family"],"slot":ref["slot"],"distance":hamming(cand["dhash"],ref["dhash"]),
                      "same_family":cand["family"]==ref["family"],
                      "same_sha":cand["sha256"]==ref["sha256"]}
                    for ref in hist],key=lambda r:r["distance"])
    cand["nearest_historical"]=nearest[:5]
    cand["cross_family_exact_matches"]=[x for x in nearest if x["distance"]==0 and not x["same_family"]]
    cand["cross_family_strong_near_matches"]=[x for x in nearest if x["distance"]<=5 and not x["same_family"]]
    cand["review_flag"]=("HOLD_CROSS_FAMILY_PHOTO_IDENTITY"
                         if cand["cross_family_strong_near_matches"]
                         else "NO_HIGH_SIMILARITY_CROSS_FAMILY_MATCH_IN_HISTORICAL_SET")
    for x in cand["cross_family_strong_near_matches"]:
        pairs.append({"candidate":cand["family"],"file":cand["file"],"historical_family":x["family"],
                      "historical_slot":x["slot"],"distance":x["distance"]})
between=[]
for a,b in combinations(candidates,2):
    if a["family"]!=b["family"] and hamming(a["dhash"],b["dhash"])<=5:
        between.append({"a":a["file"],"b":b["file"],"family_a":a["family"],"family_b":b["family"],
                        "distance":hamming(a["dhash"],b["dhash"])})
assert len({x["file"] for x in candidates})==14
for c in candidates:
    del c["dhash"]
summary={
 "version":"v2655","baseline":"v2654","candidate_files":14,"historical_reference_images":156,
 "cross_family_strong_matches":pairs,"candidate_to_candidate_cross_family_near_matches":between,
 "flagged_candidate_count":len({p["file"] for p in pairs}|{p["a"] for p in between}|{p["b"] for p in between}),
 "candidates":candidates,
 "limitations":["dHash is perceptual screening, not actual product identity proof",
                "Historical v2593 corpus is not latest v2647",
                "Current stock packaging and commercial photo rights still not verified"],
 "retail_approved_new_images":0,
 "approved_11_product_families_mutated":False,
 "existing_public_55_urls_mutated":False,
 "final_spreadsheet_shared":False
}
(OUT/"v2655-cross-sku-evidence.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
with (OUT/"cross-sku-collision-pairs.csv").open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["candidate","file","historical_family","historical_slot","distance"])
    w.writeheader();w.writerows(pairs)
print(json.dumps({"candidate_files":len(candidates),"historical_refs":len(hist),
   "flagged_candidates":summary["flagged_candidate_count"],
   "cross_family_historical_pairs":len(pairs),
   "candidate_pair_collisions":len(between),
   "flagged_details":pairs[:30]},ensure_ascii=False))
