#!/usr/bin/env python3
"""v2508: 2 missing factual frames only for pending-01 MISSHA Magic Cushion Cover Lasting.
Stock shows 21/23/25/27; no shade swatches are imagined; existing 4 JPG unchanged.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path("v2508-missha-cover-only-two");O.mkdir(exist_ok=True)
def ft(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def base(title,sub):
 im=Image.new("RGB",(1080,1080),"#fcf9f8");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,16),fill="#e2bec9")
 d.text((70,66),"MISSHA",font=ft(55,True),fill="#684554")
 d.text((70,150),"MAGIC CUSHION COVER LASTING",font=ft(31,True),fill="#6b4f5c")
 d.line((70,220,1010,220),fill="#d8b8c3",width=3)
 d.text((70,258),title,font=ft(50,True),fill="#684554")
 d.text((70,333),sub,font=ft(25),fill="#8c6c76")
 return im,d
def save(name,img,role):
 p=O/name;img.save(p,"JPEG",quality=92,subsampling=0,optimize=True)
 raw=p.read_bytes()
 assert len(raw)<2_000_000 and Image.open(p).size==(1080,1080)
 return {"filename":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"size":[1080,1080],"role":role,"sales_approved":False}
im,d=base("FOUR SHADE OPTIONS","Select your exact cushion shade.")
for i,(num,name) in enumerate([("21","LIGHT BEIGE"),("23","NATURAL BEIGE"),("25","WARM BEIGE"),("27","HONEY BEIGE")]):
 y=413+i*129
 d.rounded_rectangle((78,y,1000,y+108),radius=24,fill="#f3e7e9" if i%2==0 else "#ede9e6")
 d.text((113,y+28),"#"+num,font=ft(36,True),fill="#684554")
 d.text((324,y+30),name,font=ft(32,True),fill="#684554")
d.text((78,963),"Choose the shade number listed in your product options.",font=ft(22),fill="#7b6068")
a=save("05-4-shade-name-guide.jpg",im,"Authentic 21/23/25/27 names only; NOT a photographic shade chart")
im,d=base("CUSHION APPLICATION","Use the puff to apply your base makeup.")
for i,(head,body) in enumerate([("01  PICK UP","Take a suitable amount using the puff."),("02  SPREAD","Apply gently along the skin's texture."),("03  PAT","Pat lightly across the face to finish.")]):
 y=406+i*166
 d.rounded_rectangle((78,y,1000,y+143),radius=24,fill="#f2e7e9" if i%2==0 else "#ede9e7")
 d.text((115,y+15),head,font=ft(32,True),fill="#6c4f5c")
 d.text((115,y+79),body,font=ft(24),fill="#765e68")
d.text((79,965),"Follow the directions on the product packaging.",font=ft(22),fill="#7b6068")
b=save("06-puff-application-guide.jpg",im,"Basic use guide from Korean seller product instructions")
m={"date":"2026-11-04","family":"pending-01","product":"MISSHA Magic Cushion Cover Lasting 15g","new_files":[a,b],"previous_product_photo_JPGs_untouched":4,
"shade_options":["21 Light Beige","23 Natural Beige","25 Warm Beige","27 Honey Beige"],
"shade_name_reference":"https://www.watsons.ae/products/missha-magic-cushion-cover-lasting-foundation-15g",
"usage_reference":"https://m.cos-up.com/product/missha-%EB%AF%B8%EC%83%A4-%EB%A7%A4%EC%A7%81-%EC%BF%A0%EC%85%98-%EC%BB%A4%EB%B2%84-%EB%9E%98%EC%8A%A4%ED%8C%85-spf50-pa/1263/",
"fabricated_shade_colors":False,"official_photographic_shade_chart_approved":False,
"actual_owned_stock_edition_confirmed":False,"original_MellowKR_MK_logo_applied":False,
"public_url_new_count":0,"excel_shared":False,"full_sales_QA":"HOLD"}
(O/"manifest.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"new_jpg":len(m["new_files"]),"files":[a["filename"],b["filename"]]}))
