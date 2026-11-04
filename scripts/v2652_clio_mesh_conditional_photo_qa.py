#!/usr/bin/env python3
"""v2652: conditional batch for CLIO Mesh Glow/Blur historical duplicate frames.
No previous work regenerated, no modification of anything under public/images.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter,ImageStat,ImageDraw
import json,hashlib
ROOT=Path("source/photos/review-JPG-by-family")
OUT=Path("v2652-clio-other-two-diagnostic");OUT.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(img):
 p=list(ImageOps.grayscale(img).resize((9,8)).getdata())
 return sum(1 << (y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
def delta(a,b):return (dhash(a)^dhash(b)).bit_count()
cases=[("pending-06","CLIO Mesh Glow",1,5),("pending-07","CLIO Mesh Blur",1,4)]
results=[]
for fam,title,one,two in cases:
 files={int(p.name[:2]):p for p in sorted((ROOT/fam).glob("*.jpg"))}
 assert len(files)==6 and one in files and two in files
 with Image.open(files[one]) as im:hero=ImageOps.exif_transpose(im).convert("RGB")
 with Image.open(files[two]) as im:detail=ImageOps.exif_transpose(im).convert("RGB")
 dist=delta(hero,detail)
 result={"family":fam,"product":title,"pair":[one,two],
         "source_sha256":[digest(files[one]),digest(files[two])],
         "historical_dhash_distance":dist,"is_high_similarity_candidate":dist<=12,
         "historical_not_latest_v2647":True,
         "stock_edition_verified":False,"photo_rights_verified":False}
 images=[(hero,"Existing hero"),(detail,"Existing detail")]
 if dist<=12:
  candidates=[]
  for scale in (0.68,0.76):
   side=int(1080*scale)
   for anchor,cx,cy in [("left-top",side//2,side//2),
                        ("right-top",1080-side//2,side//2),
                        ("left-bottom",side//2,1080-side//2),
                        ("right-bottom",1080-side//2,1080-side//2),
                        ("center",540,540)]:
    crop=detail.crop((cx-side//2,cy-side//2,cx-side//2+side,cy-side//2+side))
    crop=crop.resize((1080,1080),Image.Resampling.LANCZOS)
    edge=ImageStat.Stat(crop.filter(ImageFilter.FIND_EDGES).convert("L")).stddev[0]
    d=delta(hero,crop)
    candidates.append((d+min(edge/6,4),d,scale,anchor,crop))
  best=max(candidates,key=lambda t:(t[0],t[1]))
  cand=OUT/f"{fam}-slot{two:02d}-original-photo-crop-QA-ONLY.jpg"
  best[-1].save(cand,quality=91,optimize=True,subsampling=0)
  assert cand.stat().st_size<2_000_000
  result.update({"candidate_created":True,"candidate_file":cand.name,
                 "candidate_sha256":digest(cand),"crop_anchor":best[3],
                 "crop_fraction":best[2],"candidate_distance":best[1],
                 "technical_separation_pass":best[1]>=12})
  images.append((best[-1],"New QA-only crop"))
 else:
  result.update({"candidate_created":False,"reason":"Historical distance above threshold, no duplicate-specific image needed"})
 sheet=Image.new("RGB",(780*len(images)+20,965),"#eef0f3")
 dr=ImageDraw.Draw(sheet);dr.text((20,8),f"{fam}: {title} | Historical not current sales approved",fill="#000000")
 for i,(im,label) in enumerate(images):
  x=15+i*780
  sheet.paste(im.resize((760,760),Image.Resampling.LANCZOS),(x,60))
  dr.text((x,835),label,fill="#000000")
 dr.text((15,930),"QA ONLY | Existing JPG originals unchanged | Exact stock edition & reuse rights HOLD",fill="#000000")
 sheet.save(OUT/f"{fam}-comparison.jpg",quality=85,optimize=True)
 results.append(result)
summary={"version":"v2652","baseline":"v2651","historical_archive":"v2593",
 "scope":cases,"results":results,
 "excluded":["pending-05 slot05 already addressed in v2651","pending-07 slot03 updated in v2647"],
 "previously_approved_11_families_untouched":True,"public_urls_55_untouched":True,
 "no_new_retail_approval":True,"no_spreadsheet":True,
 "next":"Only select candidates after current v2647 comparison and real stock edition/rights check"}
(OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps([{"family":r["family"],"historical_distance":r["historical_dhash_distance"],
                   "candidate_created":r["candidate_created"],"candidate_distance":r.get("candidate_distance")}
                  for r in results]))
