#!/usr/bin/env python3
"""Correct ONLY pending-20 Goodal 25AD 100ml serum mist how-to-use JPG.
Prior two photographic JPGs untouched. Correction supported by YesStyle 1136600635.
No original logo, no public release, no workbook changes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path("v2501-goodal-mist-single-factual-fix")
O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
im=Image.new("RGB",(1080,1080),"#f8f8f0");d=ImageDraw.Draw(im)
d.text((72,76),"goodal",font=F(48,True),fill="#365c4a")
d.text((72,167),"GREEN TANGERINE",font=F(48,True),fill="#345c48")
d.text((72,228),"VITA-C SERUM MIST",font=F(49,True),fill="#345c48")
d.text((72,306),"100 mL  |  HOW TO USE",font=F(30),fill="#63775d")
for i,(head,body) in enumerate([
 ("01  SHAKE","Shake gently to mix the oil and serum layers."),
 ("02  SPRAY","Spray an adequate amount across the face."),
 ("03  PAT","Pat gently to support absorption.")]):
 y=406+i*168
 d.rounded_rectangle((68,y,1012,y+141),radius=22,fill="#e7edda" if i!=1 else "#f1ebdd")
 d.text((101,y+15),head,font=F(31,True),fill="#345c48")
 d.text((101,y+75),body,font=F(24),fill="#60705a")
d.text((70,960),"Refer to the directions on your purchased package.",font=F(22),fill="#637765")
f=O/"05-usage-verified-source-corrected.jpg";im.save(f,"JPEG",quality=92,subsampling=0,optimize=True)
raw=f.read_bytes()
assert Image.open(f).size==(1080,1080) and len(raw)<2000000
manifest={"date":"2026-11-04","family":"pending-20","previous_source_run":41690495044,
"revision_reason":"Correct misattributed source and remove unsupported extra instruction",
"verified_retailer_source":"https://www.yesstyle.com/en/goodal-green-tangerine-vita-c-serum-mist-100ml/info.html/pid.1136600635",
"new_single_JPG":f.name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
"prior_product_photo_JPGs_overwritten":0,"stock_25AD_packaging_verified":False,"MK_original_logo_applied":False,
"sales_final_QA_approved":False,"new_public_URLs":0,"xlsx_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"created_JPG":f.name,"sha256":manifest["sha256"]}))
