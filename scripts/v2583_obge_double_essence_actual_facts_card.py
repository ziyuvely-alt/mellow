#!/usr/bin/env python3
"""v2583: one evidence-backed OBgE Double Essence 50mL+50mL customer copy card.
Reuses actual correct-product physical source pixels already stored in base slot02;
never fetch recommended cross-SKU images. QA only, no rights or final approval.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageChops,ImageStat
import hashlib,json
B=Path("v2583-original/review-JPG-by-family/pending-11")
O=Path("v2583-obge-double-essence-source-reuse-factual-card");O.mkdir(exist_ok=True)
assert len(list(B.glob("*.jpg")))==5
def image_slot(n):
 paths=list(B.glob(f"{n:02d}*.jpg"));assert len(paths)==1
 return paths[0]
photo=image_slot(2)
photoim=Image.open(photo).convert("RGB")
canvas=Image.new("RGB",(1080,1080),"#f6f8f6")
d=ImageDraw.Draw(canvas)
f=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
d.rounded_rectangle((33,33,1047,1046),radius=36,fill="#fffefd")
d.text((67,65),"OBgE",font=f(64,True),fill="#324f47")
d.text((67,150),"ALL-IN-ONE DOUBLE ESSENCE",font=f(35,True),fill="#3c5b4d")
d.line((67,212,1012,212),fill="#bacdc1",width=3)
# This is an authentic existing product photo, not a generated physical bottle.
pic=ImageOps.contain(photoim,(445,580),Image.Resampling.LANCZOS)
canvas.paste(pic,(52+(445-pic.width)//2,252+(580-pic.height)//2))
d.text((530,285),"TWO FORMULAS",font=f(37,True),fill="#344d42")
for idx,(label,descr) in enumerate([
 ("STEP 1","50 mL ESSENCE"),("STEP 2","50 mL ESSENCE")]):
 y=375+idx*213
 d.rounded_rectangle((520,y,1003,y+176),radius=20,fill="#e4eee8")
 d.text((547,y+25),label,font=f(35,True),fill="#305746")
 d.text((547,y+98),descr,font=f(28),fill="#47745a")
d.line((70,910,1010,910),fill="#bed0c2",width=2)
d.text((70,935),"TOTAL 100 mL  |  50 mL + 50 mL",font=f(27,True),fill="#335847")
d.text((70,990),"Apply as directed on the product label.",font=f(19),fill="#52725f")
target=O/"pending-11-slot05-double-essence-50plus50-factual-QA.jpg"
canvas.save(target,"JPEG",quality=90,optimize=True,subsampling=0)
assert Image.open(target).size==(1080,1080) and target.stat().st_size<2_000_000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=image_slot(5)
def mae(a,b):
 ia=Image.open(a).convert("RGB").resize((128,128))
 ib=Image.open(b).convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(ia,ib)).mean)/3,2)
distances={str(i):mae(image_slot(i),target) for i in range(1,6)}
assert min(distances.values())>8,distances
report={"version":"v2583","family":"pending-11",
"exact_product":"OBgE All In One Double Essence",
"confirmed_contents":"100 mL total, step 1 50 mL + step 2 50 mL",
"catalog_evidence":"https://www.ssg.com/item/itemView.ssg?itemId=1000464955759",
"actual_source_photo_existing_slot":2,"source_photo_sha256":sha(photo),
"old_slot05_sha256":sha(old),"QA_candidate_sha256":sha(target),
"new_qa_image_file":target.name,"dissimilarity_MAE":distances,
"official_instructions_exact_stock_edition_verified":False,
"source_photo_commercial_reuse_permission_verified":False,
"original_round_MK_logo_inserted":False,"published":False,
"old_156_JPG_files_changed":0,"previous_55_public_URLs_changed":0,
"xlsx_created_or_shared":False}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"factual_customer_card_created":1,"new_image_SHA":sha(target),"closest_to_existing_MAE":min(distances.values()),"public":False,"xls":False}))
