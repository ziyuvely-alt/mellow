#!/usr/bin/env python3
"""v2552 Goodal pending-21 proposed slot-05 distinct actual packaging shot.
QA proposal only: do not overwrite 156 source images; quarantines unknown stock edition.
"""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
B=Path("v2552-baseline/review-JPG-by-family")
S=Path("v2552-goodal-real-source")
O=Path("v2552-goodal-slot05-candidate-review");O.mkdir(exist_ok=True)
assert B.is_dir() and S.is_dir()
old=sorted((B/"pending-21").glob("05_*.jpg"))
assert len(old)==1,old
oldbytes=old[0].read_bytes()
sources=sorted([p for p in S.glob("yellow-box-tube.*") if p.suffix.lower() in (".jpg",".png",".webp")])
result={"version":"v2552","product":"Goodal Green Tangerine Vita C Eye Cream 30ml",
"family":"pending-21","target_slot":5,"source_run":41693239543,"previous_run":41750926355,
"source_156_jpg_untouched":True,"previous_public_55_urls_untouched":True,
"excel_created":False,"revised_image_published":False,"sales_ready":False,
"product_25ad_edition_confirmed":False,"commercial_photo_rights_verified":False}
if not sources:
 result["status"]="SOURCE_UNAVAILABLE_QUARANTINED"
 result["reason"]="Previously staged yellow-box original JPG unavailable; no speculative regeneration"
else:
 assert len(sources)==1
 p=sources[0]
 src=Image.open(p);src.load()
 assert min(src.size)>=420 and src.format in ("JPEG","PNG","WEBP")
 photo=ImageOps.contain(src.convert("RGB"),(960,780),Image.Resampling.LANCZOS)
 canvas=Image.new("RGB",(1080,1080),"#f9faf6")
 x=(1080-photo.width)//2;y=155+(780-photo.height)//2
 canvas.paste(photo,(x,y))
 d=ImageDraw.Draw(canvas)
 F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 d.text((60,44),"goodal",font=F(59,True),fill="#395d36")
 d.text((60,115),"GREEN TANGERINE VITA-C EYE CREAM",font=F(30,True),fill="#405b37")
 d.line((60,967,1020,967),fill="#aec595",width=3)
 d.text((60,982),"Original packaging photograph | 30 mL",font=F(25),fill="#4f6c47")
 path=O/"pending-21-slot05-package-photo-CANDIDATE.jpg"
 canvas.save(path,"JPEG",quality=91,optimize=True)
 raw=path.read_bytes()
 assert Image.open(path).size==(1080,1080) and len(raw)<2_000_000
 # Compare to old slot 05 for evidence of distinct visual scene.
 a=Image.open(old[0]).convert("RGB").resize((256,256))
 b=canvas.resize((256,256))
 px1=list(a.getdata());px2=list(b.getdata())
 mae=sum(abs(v-w) for t,u in zip(px1,px2) for v,w in zip(t,u))/(256*256*3)
 result.update(status="NEW_QA_CANDIDATE_ONLY",source_filename=p.name,
  original_source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
  previous_slot05_sha256=hashlib.sha256(oldbytes).hexdigest(),
  candidate_sha256=hashlib.sha256(raw).hexdigest(),
  source_photo_size=list(src.size),
  candidate_bytes=len(raw),pixel_mae_old05=round(mae,2),
  candidate_jpg=path.name,
  remaining_hold=["Exact 25AD owned packaging edition verification",
   "Commercial rights to external product photography",
   "Original round MK logo source file missing",
   "Human visual review of the genuine product identity"])
(O/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:result.get(k) for k in ("status","candidate_jpg","pixel_mae_old05","source_156_jpg_untouched")}))
