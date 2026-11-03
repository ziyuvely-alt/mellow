#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json
base=Path("v2538-base/review-JPG-by-family")
out=Path("v2538-156-missha-peelshot-washoff-corrected")
dst=out/"review-JPG-by-family"
assert base.is_dir()
shutil.copytree(base,dst)
ff=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
im=Image.new("RGB",(1080,1080),"#faf6f4");d=ImageDraw.Draw(im)
d.rectangle((0,0,1080,16),fill="#a65059")
d.text((66,54),"MISSHA  |  PDRN NAD+",font=ff(39,True),fill="#5a3038")
d.text((66,116),"RENEW PEEL SHOT 25",font=ff(42,True),fill="#5a3038")
d.text((66,185),"15 mL  /  WASH-OFF TREATMENT",font=ff(26),fill="#76545a")
d.line((66,245,1014,245),fill="#dcb7bb",width=3)
d.text((66,276),"HOW TO USE",font=ff(57,True),fill="#60343e")
steps=[("01","1-2 TIMES A WEEK","Use once or twice weekly."),
       ("02","AVOID EYES & LIPS","Apply evenly, away from eyes and lips."),
       ("03","WAIT ABOUT 5 MIN","Leave on for approximately 5 minutes."),
       ("04","RINSE OFF","Rinse thoroughly with water or lukewarm water.")]
for i,(n,head,body) in enumerate(steps):
 y=371+i*143
 d.rounded_rectangle((66,y,1015,y+124),radius=22,fill="#f0e1e1" if i%2==0 else "#f5ebe8")
 d.text((89,y+31),n,font=ff(39,True),fill="#a4505b")
 d.text((174,y+12),head,font=ff(27,True),fill="#69434b")
 d.text((174,y+66),body,font=ff(21),fill="#765960")
d.text((66,974),"Follow the instructions on the purchased package.",font=ff(22),fill="#785a61")
old=list((dst/"pending-12").glob("05_*.jpg"))
assert len(old)==1,old
prior=hashlib.sha256(old[0].read_bytes()).hexdigest();old[0].unlink()
p=dst/"pending-12/05-v2538-official-washoff-usage.jpg"
im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
b=p.read_bytes()
assert Image.open(p).size==(1080,1080) and len(b)<2000000
previous=sorted(base.glob("pending-*/*.jpg"));current=sorted(dst.glob("pending-*/*.jpg"))
assert len(previous)==156 and len(current)==156
unchanged=0
for f in previous:
 if f.parent.name=="pending-12" and f.name.startswith("05_"):continue
 assert f.read_bytes()==(dst/f.relative_to(base)).read_bytes(),str(f)
 unchanged+=1
assert unchanged==155
counts={folder.name:len(list(folder.glob("*.jpg"))) for folder in dst.glob("pending-*")}
assert len(counts)==30
assert all(counts[f"pending-{i:02d}"]==(6 if i in (1,2,4,5,6,7) else 5) for i in range(1,31))
for f in current:
 image=Image.open(f);image.load()
 assert image.format=="JPEG" and image.size==(1080,1080) and f.stat().st_size<2000000
manifest={"version":"v2538","date":"2026-11-04","family":"pending-12",
"product":"MISSHA PDRN NAD+ Renew Peel Shot 25 15 mL","replaced_slot":5,"prior_sha256":prior,
"new_file":str(p.relative_to(out)),"new_sha256":hashlib.sha256(b).hexdigest(),
"official_ingredients":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236",
"washoff_directions":"https://www.misshajp.com/shop/g/gMS104057/",
"weekly_application_source":"https://www.cosme.net/variations/1259156/",
"original_155_JPGs_byte_identical":True,"actual_review_JPG_count":156,
"source_photo_recreated":False,"MK_original_logo_applied":False,
"commercial_photo_rights_checked":False,"actual_inventory_package_QA":False,
"final_sales_release":False,"prior_55_verified_urls_unchanged":True,
"new_public_urls":0,"excel_created_or_shared":False}
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"JPG":156,"unchanged":155,"replaced_single_usage_card":str(p)}))
