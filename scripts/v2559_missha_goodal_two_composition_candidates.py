#!/usr/bin/env python3
"""v2559 continue with pending-02 & pending-19 without modifying 156 QA JPGs.
Generate two genuinely distinct compositional QA candidates using already staged
real product pixels, no fake shade diagrams, no external downloads or URL release.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
import hashlib,json
SRC=Path("v2559-base/review-JPG-by-family")
OUT=Path("v2559-missha-goodal-candidate-QA");OUT.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
cases=[
 {"family":"pending-02","slot":4,"hero":1,"title":"MISSHA | MAGIC CUSHION MOIST UP",
  "subtitle":"APPLICATION GUIDE","footer":"Shades 21 / 23 | Follow the original label directions",
  "lines":[("01","PRESS THE PUFF"),("02","PAT ON SKIN"),("03","BUILD AS NEEDED")],
  "color":"#b87887","paper":"#fbf7f7",
  "caution":"No retailer-watermarked shade photo reused; verify actual owned-stock edition."},
 {"family":"pending-19","slot":5,"hero":1,"title":"GOODAL | VITA-C CREAM ALPHA",
  "subtitle":"DAILY CREAM ROUTINE","footer":"50 mL | Follow the original package directions",
  "lines":[("01","TAKE A SMALL AMOUNT"),("02","APPLY EVENLY"),("03","ALLOW TO ABSORB")],
  "color":"#668c51","paper":"#f8faf4",
  "caution":"Do not add unsupported cosmetic efficacy or 25AD package claims."}
]
results=[]
for case in cases:
 fam=SRC/case["family"];assert fam.is_dir()
 def frame(n):
  f=list(fam.glob(f"{n:02d}*.jpg"));assert len(f)==1,(fam,n,f);return f[0]
 im=Image.open(frame(case["hero"]));im.load()
 assert im.format=="JPEG" and im.size==(1080,1080)
 canvas=Image.new("RGB",(1080,1080),case["paper"])
 d=ImageDraw.Draw(canvas)
 d.rectangle((0,0,1080,18),fill=case["color"])
 d.text((55,44),case["title"],font=F(31,True),fill="#344b3c")
 d.text((55,106),case["subtitle"],font=F(52,True),fill="#344b3c")
 genuine=ImageOps.contain(im.convert("RGB"),(465,695),Image.Resampling.LANCZOS)
 canvas.paste(genuine,((480-genuine.width)//2,207+(695-genuine.height)//2))
 for idx,(number,label) in enumerate(case["lines"]):
  y=250+idx*214
  d.rounded_rectangle((490,y,1025,y+169),radius=23,fill="#e5eae3")
  d.text((515,y+17),number,font=F(39,True),fill="#45644e")
  d.text((515,y+101),label,font=F(21,True),fill="#45644e")
 d.line((55,961,1025,961),fill=case["color"],width=3)
 d.text((56,975),case["footer"],font=F(18),fill="#475c4d")
 output=OUT/(case["family"]+f"-slot{case['slot']:02d}-real-photo-info-QA.jpg")
 canvas.save(output,"JPEG",quality=89,optimize=True)
 raw=output.read_bytes()
 assert Image.open(output).size==(1080,1080) and len(raw)<2000000
 scores={}
 for slot in range(1,7 if case["family"]=="pending-02" else 6):
  ori=Image.open(frame(slot)).convert("RGB").resize((128,128))
  cand=canvas.resize((128,128))
  scores[str(slot)]=round(sum(ImageStat.Stat(ImageChops.difference(ori,cand)).mean)/3,2)
 # Do not falsely label the image as independently licensed product photography.
 results.append({"family":case["family"],"target_slot":case["slot"],"original_source_slot":case["hero"],
 "product_source_sha256":hashlib.sha256(frame(case["hero"]).read_bytes()).hexdigest(),
 "candidate_sha256":hashlib.sha256(raw).hexdigest(),
 "candidate_file":output.name,"candidate_bytes":len(raw),"pixel_mae_vs_existing":scores,
 "near_identical_existing_slots":[k for k,v in scores.items() if v<8],
 "source_reuses_existing_real_photo":True,"new_shades_generated":False,
 "release_state":"QA_HOLD","source_caution":case["caution"]})
assert len(list(SRC.glob("pending-*/*.jpg")))==156
report={"version":"v2559","candidate_count":len(results),"source_original_count":156,
 "original_55_public_urls_changed":0,"old_JPG_replaced":0,"new_public_urls":0,
 "excel_created_or_shared":False,"licensed_photo_rights_verified":False,
 "physical_stock_edition_confirmed":False,"original_round_MK_logo_verified":False,
 "approved_for_sales":False,"entries":results}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"produced":len(results),"families":[x["family"] for x in results],
"near_identical_counts":{x["family"]:len(x["near_identical_existing_slots"]) for x in results},
"baseline_preserved":156,"released":False}))
