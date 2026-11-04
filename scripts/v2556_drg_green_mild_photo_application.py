#!/usr/bin/env python3
"""v2556 distinct application + authentic existing photo candidate for pending15
Avoid fake sunscreen packaging / claims; immutable baseline and zero publication.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageStat,ImageChops
import json,hashlib
B=Path("v2556-base/review-JPG-by-family/pending-15")
O=Path("v2556-drg-green-mild-app-photo-candidate");O.mkdir(exist_ok=True)
assert B.is_dir()
def find(n):
 paths=list(B.glob(f"{n:02d}_*.jpg"));assert len(paths)==1,(n,paths)
 return paths[0]
hero=find(1)
im=Image.open(hero);im.load()
assert im.size==(1080,1080) and im.format=="JPEG"
canvas=Image.new("RGB",(1080,1080),"#f7faf8")
d=ImageDraw.Draw(canvas)
F=lambda size,bold=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
d.rectangle((0,0,1080,20),fill="#82af96")
d.text((57,50),"Dr.G | GREEN MILD UP SUN PLUS",font=F(37,True),fill="#285d48")
d.text((58,126),"HOW TO APPLY",font=F(55,True),fill="#275743")
photo=ImageOps.contain(im.convert("RGB"),(430,560),Image.Resampling.LANCZOS)
canvas.paste(photo,((500-photo.width)//2,235+(560-photo.height)//2))
for i,(title,detail) in enumerate([
 ("01  TAKE","Use an appropriate amount."),
 ("02  APPLY","Spread across sun-exposed skin."),
 ("03  REAPPLY","Follow the original label directions.")]):
 y=295+i*194
 d.rounded_rectangle((505,y,1040,y+153),radius=18,fill="#e1eee5" if i%2==0 else "#edf1eb")
 d.text((528,y+14),title,font=F(31,True),fill="#2e624d")
 d.text((528,y+83),detail,font=F(18),fill="#466555")
d.line((60,957,1020,957),fill="#bad0c4",width=3)
d.text((58,974),"Mineral sunscreen | 50 mL | Follow product directions",font=F(22),fill="#4c6d5b")
out=O/"pending15-05-photo-plus-how-to-apply-CANDIDATE.jpg"
canvas.save(out,"JPEG",quality=90,optimize=True,subsampling=0)
assert Image.open(out).size==(1080,1080) and out.stat().st_size<2000000
def mae(p):
 source=Image.open(p).convert("RGB").resize((128,128))
 target=canvas.resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(source,target)).mean)/3,2)
diff={str(n):mae(find(n)) for n in range(1,6)}
low=[k for k,v in diff.items() if v<8]
ledger={"version":"v2556","family":"pending-15","product":"Dr.G Green Mild Up Sun Plus 50 mL old stock",
"candidate_image":out.name,"candidate_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
"source_hero_sha256":hashlib.sha256(hero.read_bytes()).hexdigest(),
"pixel_difference_vs_existing":diff,"low_diversity_slots":low,
"status":"QA_CANDIDATE_HOLD" if not low else "QUARANTINE_LOW_DIVERSITY",
"technical_source_156_unmodified":True,"original_55_urls_unchanged":True,
"new_public_urls":0,"xlsx_created":False,"commercial_release_approved":False,
"stock_2022_version_verified":False,"external_source_rights_verified":False,
"logo_original_applied":False,"photo_content_note":"Reuses genuine stored hero pixels, no new product pack generated",
"remaining_gates":["Check owned stock's product edition","Check original hero photo reuse rights","Verify source vs exact sunscreen packaging","Visual check and original MK logo"]}
(O/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":ledger["status"],"candidate":out.name,"differences":diff,"low_diversity":low}))
