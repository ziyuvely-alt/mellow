#!/usr/bin/env python3
"""Three informational ONLY JPGs for pending-15 old Dr.G Green Mild Up Sun Plus 50mL.
Reuse the two existing authentic photos unchanged. No image fabrication, unverified old/new mixing.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
O=Path("v2506-drg-green-mild-2022-three-facts");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def base(title,sub):
 im=Image.new("RGB",(1080,1080),"#f7faf7");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,18),fill="#80b497")
 d.text((69,57),"Dr.G",font=F(48,True),fill="#315b4c")
 d.text((69,126),"GREEN MILD UP SUN PLUS",font=F(32,True),fill="#315b4c")
 d.line((70,191,1010,191),fill="#aecbbb",width=3)
 d.text((70,229),title,font=F(53,True),fill="#2d5246")
 d.text((71,315),sub,font=F(26),fill="#54776a")
 return im,d
def add(name,im,role):
 p=O/name;im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2000000
 return {"file":name,"size":[1080,1080],"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"role":role,"status":"DRAFT_JPG_ORIGINAL_LOGO_AND_STOCK_QA_HOLD"}
a,d=base("MINERAL SUN CARE","Daily sunscreen product information")
for i,(h,val) in enumerate([("TYPE","Mineral sunscreen"),("NET CONTENT","50 mL"),("UV RATING","SPF50+ / PA++++")]):
 y=400+i*175
 d.rounded_rectangle((77,y,1003,y+144),radius=25,fill="#e4eee8" if i!=1 else "#edf1e9")
 d.text((108,y+14),h,font=F(26),fill="#5d7a69")
 d.text((108,y+61),val,font=F(41,True),fill="#345b4b")
d.text((75,969),"Product facts. Confirm the exact stock edition.",font=F(22),fill="#5e7567")
one=add("03-mineral-sun-care-facts.jpg",a,"Exact documented SPF and 50mL format")
b,d=base("ZINC OXIDE","Mineral UV filter")
d.rounded_rectangle((78,425,1002,690),radius=30,fill="#e1eee6")
d.text((118,462),"MINERAL UV FILTER",font=F(30,True),fill="#547763")
d.text((118,548),"ZINC OXIDE",font=F(54,True),fill="#315b4b")
d.text((94,750),"Source: Dr.G Green Mild Up Sun Plus",font=F(28),fill="#4f7060")
d.text((95,797),"ingredient declaration",font=F(28),fill="#4f7060")
d.text((75,967),"Ingredient reference: 2021 product edition.",font=F(22),fill="#5e7567")
two=add("04-zinc-oxide-factual-ingredient.jpg",b,"Documented 2021 zinc oxide presence only, physical 2022 stock check pending")
c,d=base("HOW TO APPLY","Use at the last step of skincare")
for i,(title,detail) in enumerate([("01  TAKE","Take a suitable amount of sunscreen."),("02  SPREAD","Apply evenly to sun-exposed skin."),("03  REAPPLY","Reapply following your package directions.")]):
 y=398+i*177
 d.rounded_rectangle((77,y,1003,y+145),radius=24,fill="#e3eee6" if i%2==0 else "#edf0e8")
 d.text((110,y+15),title,font=F(33,True),fill="#365d4d")
 d.text((110,y+80),detail,font=F(24),fill="#536e60")
d.text((75,971),"Follow the directions on the purchased package.",font=F(21),fill="#5e7567")
three=add("05-sunscreen-usage-guide.jpg",c,"Retailer-listed use instructions; no invented efficacy claims")
m={"date":"2026-11-04","family_id":"pending-15","product":"Dr.G Green Mild Up Sun Plus 50ml (2022-era stock)","existing_photo_JPGs_untouched":2,"new_review_JPGs":[one,two,three],"sources":["https://themonodist.com/dr-g-green-mild-up-sun-spf50-pa/","https://m.funchreward.com/product/zoom.html?product_no=174"],"real_2022_stock_edition_confirmed":False,"original_MellowKR_MK_logo_applied":False,"sales_release_approved":False,"new_public_urls":0,"old_55_public_urls_unchanged":True,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_new_JPGs":len(m["new_review_JPGs"]),"names":[z["file"] for z in m["new_review_JPGs"]]}))
