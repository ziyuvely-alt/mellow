#!/usr/bin/env python3
"""Replace ONLY redundant frame 05 from Dr.G Brightening Up Sun+ candidate pack.
Brand-confirmed message: daily tone-up, sebum control, lightweight finish.
No unverified 24h/clinical, no fake product photo or package.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
O=Path("v2515-drg-brightening-one-distinct-repair");O.mkdir(exist_ok=True)
F=lambda s,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",s)
im=Image.new("RGB",(1080,1080),"#faf8f3");d=ImageDraw.Draw(im)
d.rectangle((0,0,1080,16),fill="#e9a54f")
d.text((72,60),"Dr.G",font=F(54,True),fill="#593e2a")
d.text((72,145),"BRIGHTENING UP SUN+",font=F(37,True),fill="#624633")
d.line((72,226,1008,226),fill="#ecc99b",width=3)
d.text((72,266),"LIGHTWEIGHT FINISH",font=F(45,True),fill="#624633")
d.text((74,340),"Daily tone-up sun care",font=F(27),fill="#806a56")
for i,(h,v) in enumerate([("TONE-UP","Helps brighten the look of skin."),("SEBUM CARE","Designed for shine control."),("TEXTURE","Lightweight, comfortable finish.")]):
 y=426+166*i
 d.rounded_rectangle((78,y,1003,y+140),radius=24,fill="#f1e6d5" if i!=1 else "#eeeae4")
 d.text((108,y+14),h,font=F(29,True),fill="#6a4f39")
 d.text((108,y+75),v,font=F(24),fill="#806a56")
d.text((77,973),"Use as instructed on the original product packaging.",font=F(22),fill="#806a56")
p=O/"05-tone-up-sebum-finish.jpg";im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
m={"date":"2026-11-04","family":"pending-18","product":"Dr.G Brightening Up Sun Plus 50ml","source_v2514_artifact":13262705215,"replaced_only":"05-single-tube-product-identity.jpg","reason":"05 duplicated the same net-content and product-identity facts as 03","new_jpg":p.name,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"factual_brand_source":"https://www.dr-g.com/our-products/brightening-up-sun","unchanged_03_04":True,"previous_product_photographs_unchanged":True,"no_unverified_clinical_metrics":True,"original_MK_logo_missing":True,"rights_and_stock_edition_pending":True,"public_urls_added":0,"excel_shared":False,"sales_final_qa":False}
(O/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
print(json.dumps({"corrected":p.name,"sha256":m["sha256"]}))
