#!/usr/bin/env python3
"""Only missing customer-information JPGs for pending-18 Dr.G Brightening Up Sun Plus 50ml.
Prior 2 photographic files remain unchanged. Avoid mixing Brightening Up Moisture Sun.
Historical Korean catalog and tube labels show SPF50+ PA+++ (THREE plus signs).
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
O=Path("v2514-drg-brightening-sun-plus-three");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def base(title,sub):
 im=Image.new("RGB",(1080,1080),"#faf8f3");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,16),fill="#e9a54f")
 d.text((72,61),"Dr.G",font=F(54,True),fill="#593e2a")
 d.text((72,146),"BRIGHTENING UP SUN+",font=F(37,True),fill="#624633")
 d.line((72,226,1008,226),fill="#ecc99b",width=3)
 d.text((72,267),title,font=F(47,True),fill="#624633")
 d.text((74,346),sub,font=F(26),fill="#806a56")
 return im,d
def write(name,img,kind):
 p=O/name;img.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 return {"file":name,"role":kind,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"size":[1080,1080],"sales_approved":False}
im,d=base("PRODUCT DETAILS","Tone-up sunscreen  |  Net content: 50 mL")
for i,(label,value) in enumerate([("UV PROTECTION","SPF50+ / PA+++"),("PRODUCT TYPE","Brightening Up Sun+"),("NET CONTENT","50 mL")]):
 y=432+165*i
 d.rounded_rectangle((77,y,1003,y+138),radius=23,fill="#f1e6d5" if i!=1 else "#f5eadc")
 d.text((111,y+12),label,font=F(26),fill="#917354")
 d.text((111,y+62),value,font=F(36,True),fill="#624633")
d.text((76,971),"Refer to your purchased product packaging for details.",font=F(22),fill="#806a56")
a=write("03-verified-50ml-spf-pa-facts.jpg",im,"Exact SPF50+ PA+++ and net content; not Moisture Sun")
im,d=base("DAILY APPLICATION","Apply at the final step of your skincare routine.")
for i,(label,text) in enumerate([("01  TAKE","Dispense a suitable amount of sunscreen."),("02  APPLY","Spread evenly over sun-exposed skin."),("03  FOLLOW","Follow the instructions on the package.")]):
 y=418+171*i
 d.rounded_rectangle((78,y,1000,y+143),radius=25,fill="#f2e7d8" if i%2==0 else "#eeeae4")
 d.text((110,y+18),label,font=F(32,True),fill="#644c38")
 d.text((110,y+80),text,font=F(24),fill="#796554")
d.text((76,972),"For external use. Follow label directions.",font=F(22),fill="#806a56")
b=write("04-sunscreen-application-facts.jpg",im,"Verified SSG 50ml usage instructions only")
im,d=base("CHECK YOUR PRODUCT","Exact-product identification")
for i,(label,value) in enumerate([("BRAND","Dr.G"),("PRODUCT","Brightening Up Sun+"),("FORMAT","One 50 mL tube")]):
 y=426+165*i
 d.rounded_rectangle((78,y,1002,y+138),radius=24,fill="#f0e8dc")
 d.text((111,y+11),label,font=F(25),fill="#927353")
 d.text((111,y+63),value,font=F(36,True),fill="#624633")
d.text((77,971),"Brightening Up Sun+ is not Moisture Sun.",font=F(22),fill="#806a56")
c=write("05-single-tube-product-identity.jpg",im,"Single product / pack identity; no gift set assumption")
manifest={"date":"2026-11-04","family_id":"pending-18","product":"Dr.G Brightening Up Sun Plus 50mL",
"existing_two_real_photo_candidates_untouched":True,"new_JPGs":[a,b,c],
"official_retail_source":"https://www.ssg.com/item/itemView.ssg?itemId=1000522807222",
"verified_spf_pa":"SPF50+ PA+++","other_edition_mixed":False,
"physical_stock_generation_match_confirmed":False,"brand_original_MK_logo_applied":False,
"public_sale_approval":False,"new_public_urls":0,"spreadsheet_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"created_jpgs":3,"files":[x["file"] for x in manifest["new_JPGs"]]}))
