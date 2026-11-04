#!/usr/bin/env python3
"""v2557 exact verified 145ml Pixelpure source-only candidate.
Never use 150ml detail gallery despite official page title. No public image overwrite.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageStat,ImageChops
import json,hashlib
S=Path("v2557-source-145")
B=Path("v2557-base156/review-JPG-by-family/pending-26")
O=Path("v2557-pixelpure-exact145-candidate-QA");O.mkdir(exist_ok=True)
EXPECTED="6bcb50db894591dd724125629308de7907b427021fef2edcc67f8debecc505cd"
F=S/"official-product-image-01.jpg"
assert B.is_dir() and F.is_file()
assert hashlib.sha256(F.read_bytes()).hexdigest()==EXPECTED,"Official verified 145ml original mismatch; quarantine"
src=Image.open(F);src.load()
assert src.format=="JPEG" and min(src.size)>=350
canvas=Image.new("RGB",(1080,1080),"#faf9f7")
d=ImageDraw.Draw(canvas)
font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
d.text((52,44),"PIXEL PURE",fill="#404a43",font=font(54,True))
d.text((52,115),"GENTLE GEL TO FOAM CLEANSER",fill="#404a43",font=font(29,True))
original=ImageOps.contain(src.convert("RGB"),(470,750),Image.Resampling.LANCZOS)
canvas.paste(original,((505-original.width)//2,202+(750-original.height)//2))
for i,(label,desc) in enumerate([("145 mL","EXACT 145 mL BOTTLE"),("GEL TO FOAM","DAILY CLEANSING FORMAT"),("USE","FOLLOW PACKAGE DIRECTIONS")]):
 y=286+206*i
 d.rounded_rectangle((513,y,1026,y+170),radius=21,fill="#e8eee8" if i!=1 else "#f0f1eb")
 d.text((536,y+20),label,font=font(39,True),fill="#425d4b")
 d.text((536,y+110),desc,font=font(19),fill="#637469")
d.line((52,957,1028,957),fill="#c9d3c8",width=3)
d.text((52,975),"Brand official original / printed 145 ml label QA",font=font(22),fill="#4c6755")
out=O/"pending26-05-verified-original-145ml-CANDIDATE.jpg"
canvas.save(out,"JPEG",quality=91,optimize=True)
assert Image.open(out).size==(1080,1080) and out.stat().st_size<2_000_000
scores={};baselines={}
for i in range(1,6):
 files=list(B.glob(f"{i:02d}_*.jpg"));assert len(files)==1
 old=Image.open(files[0]).convert("RGB").resize((128,128))
 a=canvas.resize((128,128))
 scores[str(i)]=round(sum(ImageStat.Stat(ImageChops.difference(old,a)).mean)/3,2)
 baselines[str(i)]=hashlib.sha256(files[0].read_bytes()).hexdigest()
similar=[k for k,v in scores.items() if v<8]
report={"version":"v2557","family":"pending-26","product":"Pixelpure Gentle Gel To Foam Cleanser 145mL",
"source_type":"OFFICIAL_PRODUCT_IMAGE_VISUAL_145ML_LABEL_VERIFIED_IN_V2533B",
"source_run":41710591522,"source_image_sha256":EXPECTED,
"excluded_150_ml_images":["official-product-image-02.jpg","official-product-image-03.jpg","official-product-image-04.jpg"],
"excluded_accessory":["official-product-image-05.jpg"],
"candidate_image":out.name,"candidate_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
"pixel_mae_vs_existing_slots":scores,"near_same_scene_existing_slots":similar,
"source_156_jpg_untouched":True,"old_55_urls_unchanged":True,"xlsx_generated":False,
"new_public_urls":0,"manual_source_photo_rights_confirmed":False,
"physical_owned_stock_pack_verified":False,"original_mk_logo_applied":False,
"sales_approval":False,"status":"QA_CANDIDATE_145ML_RIGHTS_HOLD" if not similar else "QA_HOLD_POSSIBLE_DUPLICATE_WITH_EXISTING",
"note":"Published official product web page title 145mL does not validate all images; source SHA strict; 150mL files never used."}
(O/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":report["status"],"candidate":out.name,"near_existing":similar,"MAE":scores}))
