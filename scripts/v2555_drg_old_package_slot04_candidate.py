#!/usr/bin/env python3
"""v2555: candidate genuine old-package Dr.G R.E.D cream slot04.
Does not overwrite 156-JPG QA baseline. Does not release images or spreadsheets.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
import json,hashlib
B=Path("v2555-base156/review-JPG-by-family/pending-16")
S=Path("v2555-source-old")
O=Path("v2555-pending16-old-pack-photo-review");O.mkdir(exist_ok=True)
assert B.is_dir() and S.is_dir()
def getslot(n):
 v=list(B.glob(f"{n:02d}_*.jpg"));assert len(v)==1,(n,v);return v[0]
old=getslot(4)
sources=list(S.glob("tenbyten-old-jar-carton.*"))
sources=[p for p in sources if p.suffix.lower() in {".jpg",".png",".webp"}]
res={"version":"v2555","family":"pending-16",
 "product":"Dr.G R.E.D Blemish Clear Soothing Cream 70mL old 2022 edition",
 "target_slot":4,"baseline_run":41715911900,"source_photo_run":41692792277,
 "source_images_unchanged":156,"previous_55_public_urls_preserved":True,
 "new_public_urls":0,"excel_generated":False,"commercial_release_approved":False,
 "product_stock_2022_package_verified":False,"source_photo_usage_rights_verified":False}
if len(sources)!=1:
 res["status"]="QUARANTINE_SOURCE_MISSING_OR_AMBIGUOUS"
 res["matches"]=len(sources)
else:
 p=sources[0];im=Image.open(p);im.load()
 assert min(im.size)>=400 and im.format in ("JPEG","PNG","WEBP")
 photo=ImageOps.contain(im.convert("RGB"),(960,790),Image.Resampling.LANCZOS)
 canvas=Image.new("RGB",(1080,1080),"#f7faf7")
 x=(1080-photo.width)//2;y=155+(790-photo.height)//2
 canvas.paste(photo,(x,y))
 d=ImageDraw.Draw(canvas)
 F=lambda n,b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 d.text((55,43),"Dr.G | R.E.D BLEMISH",fill="#285a45",font=F(41,True))
 d.text((55,103),"CLEAR SOOTHING CREAM | 70 mL",fill="#285a45",font=F(33,True))
 d.line((55,962,1025,962),fill="#b5cbb9",width=2)
 d.text((55,978),"Original jar + carton photograph | old package",fill="#416551",font=F(23))
 target=O/"pending16-04-original-70ml-jar-carton-CANDIDATE.jpg"
 canvas.save(target,"JPEG",quality=92,optimize=True,subsampling=0)
 assert Image.open(target).size==(1080,1080) and target.stat().st_size<2_000_000
 def metrics(a,b):
  a=Image.open(a).convert("RGB").resize((128,128))
  b=b.convert("RGB").resize((128,128))
  diff=ImageStat.Stat(ImageChops.difference(a,b)).mean
  return round(sum(diff)/3,2)
 diffs={str(slot):metrics(getslot(slot),canvas) for slot in range(1,6) if slot!=4}
 # A candidate mirroring an existing scene does not increase useful diversity.
 similar=[x for x,y in diffs.items() if y<8]
 res.update(status="HOLD_FOR_MANUAL_VISUAL_AND_EDITION_QA" if similar else "DISTINCT_CANDIDATE_QA_ONLY",
   original_source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
   existing_slot04_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
   candidate_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
   candidate_image=target.name,candidate_bytes=target.stat().st_size,
   mae_against_other_slots=diffs,similar_existing_slots=similar,
   required_checks=["Product label and 2022 owned-stock edition","Photo reuse rights","Original MK logo","Human visual review"])
(O/"manifest.json").write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:res.get(k) for k in ("status","candidate_image","similar_existing_slots","mae_against_other_slots")},ensure_ascii=False))
