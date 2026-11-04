#!/usr/bin/env python3
"""v2653: next unfinished families, detect within-product visual repeats and stage
isolated original-photo detail alternatives only when a clear historical duplication
is actually detected. Never touch public assets, v2647, or any final spreadsheet.
Historical v2593 photo corpus is not the latest sales asset.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter,ImageStat,ImageDraw
from itertools import combinations
from collections import defaultdict
import json,hashlib
SRC=Path("source/photos/review-JPG-by-family")
OUT=Path("v2653-pending08-30-visual-triage");OUT.mkdir(exist_ok=True)
SKIP={"pending-05","pending-06","pending-07"}
LATER_REPLACED={
 ("pending-07",3),("pending-09",2),("pending-27",5),("pending-28",2),
 ("pending-29",1),("pending-30",1),("pending-26",1)}
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
def dist(a,b):return (a^b).bit_count()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
families=sorted(p for p in SRC.glob("pending-*") if p.is_dir() and p.name not in SKIP)
assert len(families)==27, len(families)
results=[];generated=[]
for folder in families:
 imgs={}
 for p in sorted(folder.glob("*.jpg")):
  slot=int(p.name[:2])
  with Image.open(p) as im:
   im.load()
   image=ImageOps.exif_transpose(im).convert("RGB")
   assert image.size==(1080,1080)
   imgs[slot]={"file":p,"img":image,"hash":dhash(image),"sha256":sha(p)}
 assert len(imgs)==(6 if folder.name in ("pending-01","pending-02","pending-04") else 5)
 pairs=[]
 for a,b in combinations(imgs,2):
  dd=dist(imgs[a]["hash"],imgs[b]["hash"])
  if dd<=12:
   pairs.append({"slots":[a,b],"distance":dd,
                 "source_sha256":[imgs[a]["sha256"],imgs[b]["sha256"]],
                 "contains_known_revised_frame":(folder.name,a) in LATER_REPLACED or (folder.name,b) in LATER_REPLACED})
 pairs.sort(key=lambda p:p["distance"])
 result={"family":folder.name,"jpg_count":len(imgs),"historical_candidate_pairs":pairs,
         "no_candidate_because_distinct":not pairs}
 if pairs:
  p=next((p for p in pairs if not p["contains_known_revised_frame"]),None)
  # Stage one candidate per family at most. No edits if only near pair was already addressed.
  if p:
   a,b=p["slots"];hero=imgs[a]["img"];detail=imgs[b]["img"]
   selections=[]
   for ratio in (0.70,0.78):
    side=int(1080*ratio)
    for anchor,cx,cy in [
       ("top-left",side//2,side//2),("top-right",1080-side//2,side//2),
       ("bottom-left",side//2,1080-side//2),("bottom-right",1080-side//2,1080-side//2),
       ("center",540,540)]:
     crop=detail.crop((cx-side//2,cy-side//2,cx-side//2+side,cy-side//2+side)).resize((1080,1080),Image.Resampling.LANCZOS)
     separation=dist(dhash(hero),dhash(crop))
     edge=ImageStat.Stat(crop.filter(ImageFilter.FIND_EDGES).convert("L")).stddev[0]
     selections.append((separation+min(edge/6,4),separation,anchor,ratio,crop))
   best=max(selections,key=lambda z:(z[0],z[1]))
   # Prevent gratuitous crops and low-information edits; separation only a triage criterion.
   if best[1]>=16:
    candidate=OUT/f"{folder.name}-slot{b:02d}-original-photo-crop-QA-ONLY.jpg"
    best[-1].save(candidate,quality=91,optimize=True,subsampling=0)
    assert candidate.stat().st_size<2000000
    result["staged_candidate"]={"slots":[a,b],"file":candidate.name,"sha256":sha(candidate),
            "crop_anchor":best[2],"crop_fraction":best[3],"dhash_distance":best[1],
            "size_bytes":candidate.stat().st_size,"status":"QA_ONLY_NO_RETAIL_APPROVAL"}
    board=Image.new("RGB",(2280,860),"#e9ebed");dr=ImageDraw.Draw(board)
    for i,(image,label) in enumerate([(hero,"SOURCE A"),(detail,"SOURCE B"),(best[-1],"QA CROP CANDIDATE")]):
     board.paste(image.resize((740,740),Image.Resampling.LANCZOS),(10+i*760,60))
     dr.text((10+i*760,25),label,fill="#111111")
    dr.text((10,825),folder.name+" | Historical source only | Verify edition, license and current v2647 first",fill="#111111")
    board.save(OUT/f"{folder.name}-comparison-QA.jpg",quality=83,optimize=True)
    generated.append(folder.name)
   else: result["no_candidate_reason"]="No acceptable composition with sufficient perceptual separation"
  else: result["no_candidate_reason"]="Only pairs known revised in later v2647 checkpoint"
 results.append(result)
report={"version":"v2653","base_image_artifact_run":41764831639,
 "archive_version":"v2593 historical, not v2647", "families_analyzed":len(families),
 "finished_prior_families_excluded":sorted(SKIP),
 "known_later_replaced_slots_excluded":sorted([{"family":f,"slot":s} for f,s in LATER_REPLACED],key=lambda x:(x["family"],x["slot"])),
 "families_with_historical_near_pairs":sum(bool(x["historical_candidate_pairs"]) for x in results),
 "new_QA_candidate_files":len(generated),"candidate_families":generated,
 "results":results,
 "retail_approval":False,"original_public_55_urls_untouched":True,
 "approved_11_families_untouched":True,"xlsx_not_shared":True,
 "next":"Review contact sheets for product-specific detail meaning; compare latest v2647 before any production merge"}
(OUT/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"families":len(families),"families_with_near_pairs":report["families_with_historical_near_pairs"],
 "staged_candidates":len(generated),"families_staged":generated,
 "approved_retail_images":0,"published_urls_changed":0},ensure_ascii=False))
