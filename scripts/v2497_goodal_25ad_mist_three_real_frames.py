#!/usr/bin/env python3
"""Produce only missing distinct 25AD mist draft visuals from genuine 600px photos.
Stock edition and licensed photo reuse are NOT approved.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
S=Path("v2496-goodal-mist-25ad-source-photos")
O=Path("v2497-goodal-25ad-mist-three-JPGs");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(name,im,src):
 p=O/name;im.convert("RGB").save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2000000
 return {"filename":name,"source":src,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"size":[1080,1080],"status":"Genuine-photo-draft / commercial rights & seller stock pending"}
def pic(source,name,title,top):
 im=Image.open(S/source).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
 # Text is confined to unoccupied edge; all product pixels from actual retailer photo.
 layer=Image.new("RGBA",(1080,1080),(0,0,0,0))
 d=ImageDraw.Draw(layer)
 y=16 if top else 936
 d.rounded_rectangle((32,y,1048,y+121),radius=13,fill=(255,255,255,220))
 d.text((62,y+13),"goodal  |  VITA-C SERUM MIST",font=F(33,True),fill="#345f4b")
 d.text((62,y+65),title,font=F(24),fill="#54745e")
 return save(name,Image.alpha_composite(im.convert("RGBA"),layer).convert("RGB"),source)
a=pic("25ad-straight-product.jpg","03-25ad-front-bottle.jpg","100 mL  |  Niacinamide + Hyaluronic Acid",True)
b=pic("25ad-angled-product.jpg","04-25ad-bottle-angle.jpg","Actual product view  |  25AD reference",False)
im=Image.new("RGB",(1080,1080),"#f8f8f0");d=ImageDraw.Draw(im)
d.text((72,76),"goodal",font=F(48,True),fill="#365c4a")
d.text((72,167),"GREEN TANGERINE",font=F(48,True),fill="#345c48")
d.text((72,228),"VITA-C SERUM MIST",font=F(49,True),fill="#345c48")
d.text((72,306),"100 mL  |  HOW TO USE",font=F(30),fill="#63775d")
for i,(head,body) in enumerate([("01  SHAKE","Shake thoroughly to mix before use."),("02  CLOSE EYES","Keep your eyes closed while spraying."),("03  MIST EVENLY","Spray evenly across the face.")]):
 y=406+i*168
 d.rounded_rectangle((68,y,1012,y+141),radius=22,fill="#e7edda" if i!=1 else "#f1ebdd")
 d.text((101,y+15),head,font=F(31,True),fill="#345c48")
 d.text((101,y+75),body,font=F(25),fill="#60705a")
d.text((70,960),"Refer to the instructions on the purchased packaging.",font=F(22),fill="#637765")
c=save("05-verified-usage-instructions.jpg",im,"Clio direct SSG seller listing 25AD use directions")
manifest={"date":"2026-11-04","family":"pending-20","source_run":41690163576,"source_artifact":13255563047,"previous_JPG_recreated":0,"new_JPG_files":[a,b,c],"exact_25AD_image_label_checked":True,"physical_owned_stock_package_checked":False,"licensed_image_use_verified":False,"MK_original_logo_applied":False,"final_sales_QA":False,"new_public_URLs":0,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"created_JPGs":len(manifest["new_JPG_files"]),"names":[a["filename"],b["filename"],c["filename"]]}))
