#!/usr/bin/env python3
"""Compose 3 *new* distinct Dr.G Moisture Sun 50ml candidate JPGs.
Do not touch previous family candidates or approved public 55. Keep sale QA blocked.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
SRC=Path("v2488-drg-moisture-exact-photos")
OUT=Path("v2489-drg-moisture-three-new-JPG");OUT.mkdir(exist_ok=True)
def font(s,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",s)
def save(name,img,source):
 p=OUT/name;img.convert("RGB").save(p,"JPEG",quality=90,subsampling=0,optimize=True)
 b=p.read_bytes(); assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 return {"file":name,"source":source,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"resolution":[1080,1080],"status":"DRAFT_JPG_EXACT_PRODUCT_PHOTO_RIGHTS_LOGO_QA_PENDING"}
def real(name,source,heading,detail,y):
 img=Image.open(SRC/source).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
 layer=Image.new("RGBA",img.size,(0,0,0,0));d=ImageDraw.Draw(layer)
 d.rounded_rectangle((24,y,1056,y+135),radius=20,fill=(255,255,255,216))
 d.text((54,y+12),"Dr.G  |  BRIGHTENING UP MOISTURE SUN",font=font(27,True),fill="#51483c")
 d.text((54,y+50),heading,font=font(41,True),fill="#51483c")
 d.text((54,y+103),detail,font=font(21),fill="#70665d")
 return save(name,Image.alpha_composite(img.convert("RGBA"),layer).convert("RGB"),source)
r=[]
r.append(real("03-texture-genuine-scene.jpg","oliveyoung-08ko.jpg.jpg","MOISTURE SUN TEXTURE","Real product tube and texture photograph | 50 mL",915))
r.append(real("04-hand-use-genuine-scene.jpg","dodoskin-forearm.jpg","A CLOSER LOOK","Real product photograph | 50 mL",26))
img=Image.new("RGB",(1080,1080),"#fbf7f1");d=ImageDraw.Draw(img)
d.rectangle((0,0,1080,18),fill="#e6b084")
d.text((80,74),"Dr.G",font=font(55,True),fill="#534439")
d.text((80,171),"BRIGHTENING UP",font=font(51,True),fill="#57483c")
d.text((80,230),"MOISTURE SUN",font=font(51,True),fill="#57483c")
d.line((80,323,999,323),fill="#ddbe9f",width=3)
items=[("TYPE","Sunscreen / tone-up"),("SIZE","50 mL"),("PRODUCT","Brightening Up Moisture Sun")]
for i,(label,value) in enumerate(items):
 y=378+i*168
 d.rounded_rectangle((80,y,1000,y+141),radius=29,fill=("#f5e8da" if i%2==0 else "#f2eeea"))
 d.text((112,y+16),label,font=font(27),fill="#7b685a")
 d.text((112,y+62),value,font=font(37,True),fill="#574639")
d.text((82,966),"Always follow the directions on the original package.",font=font(23),fill="#6a6056")
r.append(save("05-factual-single-product.jpg",img,"Official Dr.G / Olive Young 50 mL product identity"))
manifest={"date":"2026-11-04","family_id":"pending-17","existing_JPG_overwritten":0,"new_JPG_files":r,"original_2023_stock_package_match_confirmed":False,"exact_original_MK_logo_applied":False,"third_party_photo_rights_verified":False,"public_url_added":0,"release_QA":"HOLD","no_workbook_share":True,"notes":"Exact product source visuals only. Older two frames remain untouched. Full five-frame visual QA still required."}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"created":len(r),"files":[x["file"] for x in r]}))
