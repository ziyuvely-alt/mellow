#!/usr/bin/env python3
"""Safe partial production for OBgE Double Essence 50ml+50ml.
Reuses exact-image-only original-01 from successful v2490, excludes seven wrong SKUs.
Produces 1 authentic hero and 2 fact cards pending original MK logo/stock version/licensing.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
src=Path("v2490-original/pending-11/original-01.png")
assert src.is_file(), "Missing original official exact product photo"
out=Path("v2493-obge-double-essence-three-partial");out.mkdir(exist_ok=True)
ft=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def file(name,im,status):
 f=out/name;im.convert("RGB").save(f,"JPEG",quality=92,optimize=True,subsampling=0)
 raw=f.read_bytes();assert Image.open(f).size==(1080,1080) and len(raw)<2_000_000
 return {"file":name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"status":status}
# Genuine photographic source. Do not alter packaging proportions or text.
im=Image.open(src).convert("RGB")
hero=Image.new("RGB",(1080,1080),"#f5f5f3");im=ImageOps.contain(im,(875,865))
hero.paste(im,((1080-im.width)//2,140))
d=ImageDraw.Draw(hero)
d.text((65,48),"OBgE  ALL-IN-ONE DOUBLE ESSENCE",font=ft(36,True),fill="#334437")
d.text((65,1010),"Original official product photo | Stock edition pending confirmation",font=ft(18),fill="#516351")
a=file("03-official-single-product-photo.jpg",hero,"AUTHENTIC_PRODUCT_PHOTO_QA_HOLD")
# Evidence for quantity 1st-phase 50ml + 2nd-phase 50ml: SSG official page; do not assert 2 retail bottles.
x=Image.new("RGB",(1080,1080),"#f6f5f0");d=ImageDraw.Draw(x)
d.text((76,73),"OBgE  /  DOUBLE ESSENCE",font=ft(41,True),fill="#30483d")
d.text((76,184),"DUAL FORMULA",font=ft(63,True),fill="#30483d")
d.text((76,265),"Two phases inside one product",font=ft(30),fill="#5b7164")
for i,(label,val) in enumerate([("PHASE 01","50 mL"),("PHASE 02","50 mL")]):
 yy=403+i*212
 d.rounded_rectangle((80,yy,1000,yy+185),radius=30,fill="#e1eae0" if i==0 else "#eae3da")
 d.text((112,yy+26),label,font=ft(31),fill="#5a7163")
 d.text((112,yy+79),val,font=ft(56,True),fill="#30483d")
d.text((79,971),"Total net volume: 100 mL  |  Packaging version requires stock QA",font=ft(22),fill="#5b6b60")
b=file("04-two-phase-net-content.jpg",x,"FACT_SOURCE_VERIFIED_PACKAGING_QA_HOLD")
y=Image.new("RGB",(1080,1080),"#f5f7f5");d=ImageDraw.Draw(y)
d.text((78,73),"OBgE  /  DOUBLE ESSENCE",font=ft(41,True),fill="#30483d")
d.text((78,181),"HOW TO USE",font=ft(64,True),fill="#30483d")
for i,(title,desc) in enumerate([("STEP 01","Dispense a suitable amount into your hand."),("STEP 02","Gently smooth over facial skin."),("STEP 03","Pat lightly until absorbed.")]):
 yy=325+i*190
 d.rounded_rectangle((76,yy,1005,yy+162),radius=23,fill="#e4ece4" if i%2==0 else "#e8e5dd")
 d.text((108,yy+18),title,font=ft(34,True),fill="#3b5848")
 d.text((108,yy+85),desc,font=ft(24),fill="#566c5f")
d.text((77,970),"Follow the directions printed on your purchased package.",font=ft(22),fill="#556a60")
c=file("05-seller-usage-information.jpg",y,"OFFICIAL_RETAILER_USAGE_FACT_QA_HOLD")
m={"date":"2026-11-04","family":"pending-11","source_run_id":41688655026,"source_artifact_id":13256606734,"source_correct_photo":"pending-11/original-01.png","wrong_product_photo_files_excluded":7,"new_JPG_files":[a,b,c],"prior_two_candidate_images_untouched":True,"new_photo_scenes":1,"new_factual_information_cards":2,"final_five_frame_sales_QA":False,"reason_for_hold":["Real MK logo bytes not available","Official photograph commercial use rights not verified","User-owned inventory physical package and 1+1 presentation not crosschecked","2 information frames and 1 source photo do not yet establish distinct full family scene diversity"],"published_url_added":0,"workbook_shared":False}
(out/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_JPG_files":3,"shas":[z["sha256"] for z in (a,b,c)]}))
