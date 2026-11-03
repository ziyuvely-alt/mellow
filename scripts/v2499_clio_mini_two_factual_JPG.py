#!/usr/bin/env python3
"""Create two *non-swatch* factual customer information JPGs for CLIO mini 5g.
Never synthesize color pixels, swatch photos, packaging or make claims of official shade chart QA.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path("v2499-clio-mesh-glow-mini-fact-frames");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(n,im):
 p=O/n;im.save(p,"JPEG",quality=93,optimize=True,subsampling=0)
 data=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(data)<2_000_000
 return {"filename":n,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"size":[1080,1080],"type":"informational draft only"}
def frame(title,tag):
 im=Image.new("RGB",(1080,1080),"#f8f7f4");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,19),fill="#c3d7cb")
 d.text((68,75),"CLIO",font=F(54,True),fill="#243d36")
 d.text((68,152),"KILL COVER MESH GLOW ESSENTIAL",font=F(31,True),fill="#405850")
 d.text((68,198),"CUSHION MINI · 5 g",font=F(32,True),fill="#405850")
 d.line((68,278,1014,278),fill="#a4b7ab",width=3)
 d.text((68,322),title,font=F(48,True),fill="#30463f")
 d.text((68,971),tag,font=F(22),fill="#566e62")
 return im,d
a,d=frame("CHOOSE YOUR MINI SHADE","Shade names only. Not a photographic color swatch.")
shades=[("21C","LINGERIE","Natural cool skin tone"),("21N","LINEN","Natural neutral skin tone"),("23N","GINGER","Healthy neutral skin tone")]
for i,(id,name,subtitle) in enumerate(shades):
 y=435+i*160
 d.rounded_rectangle((72,y,1008,y+137),radius=22,fill="#e5ede7" if i!=1 else "#edeae3")
 d.text((108,y+25),id,font=F(45,True),fill="#315147")
 d.text((288,y+16),name,font=F(35,True),fill="#315147")
 d.text((288,y+79),subtitle,font=F(23),fill="#5e7269")
x=save("04-mini-3-shade-name-guide.jpg",a)
b,d=frame("APPLY WITH THE PUFF","Check your purchased package for exact use instructions.")
for i,(title,detail) in enumerate([("STEP 1","Pick up a small amount with the included puff."),("STEP 2","Apply evenly to your skin."),("STEP 3","Build coverage gently where needed.")]):
 y=430+i*161
 d.rounded_rectangle((72,y,1008,y+136),radius=20,fill="#e7ede7")
 d.text((105,y+14),title,font=F(33,True),fill="#315147")
 d.text((105,y+76),detail,font=F(23),fill="#536960")
y=save("05-mini-cushion-puff-use-guide.jpg",b)
manifest={"date":"2026-11-04","family":"pending-04","product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g","new_jpg":[x,y],"verified_option_names":["21C Lingerie","21N Linen","23N Ginger"],"option_basis":"https://m.gsshop.com/prd/prd.gs?prdid=1100834213","usage_basis":"https://www.yesstyle.com/en/clio-kill-cover-mesh-glow-essential-cushion-mini-3-colors-21c-lingerie/info.html/pid.1136795277","source_photos_reused":0,"artificial_shade_pixels_created":False,"official_shade_swatch_verified":False,"physical_stock_generation_matched":False,"original_MK_logo_applied":False,"published":False,"workbook_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_customer_review_JPGs":2,"files":[x["filename"],y["filename"]]}))
