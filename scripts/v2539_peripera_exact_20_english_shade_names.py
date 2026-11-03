#!/usr/bin/env python3
"""v2539: replace only repetitive Peripera pending-08 frame 05 with exact 01-20 English option names.
Names sourced from Peripera-sponsored Minsco 2026-01-22 review and 26AD retailer listing.
Do NOT generate colors or shades, include later 21-30, or imply swatch verification.
155 source JPEGs remain byte-identical. Source packaging edition still needs final QA.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import shutil,hashlib,json
B=Path("v2539-input-156/review-JPG-by-family")
assert B.is_dir()
O=Path("v2539-156-peripera-20shade-names-QA");D=O/"review-JPG-by-family"
shutil.copytree(B,D)
f=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
shades=["Tiny Strawberry","Coral Chemistry","Juicy Peach","Anyway Peach","Baby Fairy","Pink Youth","Plum Fizz","Joking Pink","Rose In Mind","Bare Pink","Visual Pink","Campus Queen","Mood Queen","Rosy Wish","My Pick Rose","Rose-Pick","Blush Fig","Coral Influencer","Cherry So What","Brown Yakgwa"]
im=Image.new("RGB",(1080,1080),"#faf8fa");d=ImageDraw.Draw(im)
d.rectangle((0,0,1080,13),fill="#e596ad")
d.text((58,49),"peripera",font=f(47,True),fill="#803d56")
d.text((58,113),"MOOD GLOWY TINT  /  4g",font=f(29,True),fill="#654452")
d.text((58,174),"YOUR 20 SHADES",font=f(54,True),fill="#843c5c")
d.line((58,256,1023,256),fill="#e5b9c6",width=3)
for i,name in enumerate(shades):
 col=i//10;row=i%10
 x=55+col*510;y=284+row*66
 d.rounded_rectangle((x,y,x+478,y+58),radius=13,fill="#f1e3e8" if row%2==0 else "#f7edf0")
 d.text((x+15,y+12),f"{i+1:02d}",font=f(28,True),fill="#974d68")
 d.text((x+81,y+15),name,font=f(23,True),fill="#5a3b4a")
d.text((60,975),"Shade names only  |  Refer to actual product photos for color.",font=f(20),fill="#806170")
old=list((D/"pending-08").glob("05_*.jpg"));assert len(old)==1,old
old_sha=hashlib.sha256(old[0].read_bytes()).hexdigest();old[0].unlink()
p=D/"pending-08/05-v2539-20-English-shade-names.jpg"
im.save(p,"JPEG",quality=91,optimize=True,subsampling=0)
assert Image.open(p).size==(1080,1080) and p.stat().st_size<2000000
prior=list(B.glob("pending-*/*.jpg"));new=list(D.glob("pending-*/*.jpg"))
assert len(prior)==156 and len(new)==156
same=0
for q in prior:
 if q.parent.name=="pending-08" and q.name.startswith("05_"):continue
 assert q.read_bytes()==(D/q.relative_to(B)).read_bytes(),str(q)
 same+=1
assert same==155
counts={x.name:len(list(x.glob("*.jpg"))) for x in D.glob("pending-*")}
assert len(counts)==30
assert all(counts[f"pending-{i:02d}"]==(6 if i in (1,2,4,5,6,7) else 5) for i in range(1,31))
for q in new:
 a=Image.open(q);a.load()
 assert a.format=="JPEG" and a.size==(1080,1080) and q.stat().st_size<2000000
m={"version":"v2539","date":"2026-11-04","family":"pending-08","product":"Peripera Mood Glowy Tint 26AD selected 01-20 / 4g",
"new_image":str(p.relative_to(O)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"superseded_05_sha256":old_sha,
"shades":[{"number":f"{i+1:02d}","english_name":n} for i,n in enumerate(shades)],
"naming_source":"https://www.youtube.com/watch?v=2M3eJESkSac",
"crosscheck_source":"https://m.gsshop.com/prd/prd.gs?prdid=1106843033",
"verified_reconciliations":{"04":"Anyway Peach","06":"Pink Youth","07":"Plum Fizz","14":"Rosy Wish"},
"official_brand_photo_colors_verified":False,"shade_colors_generated":False,
"extra_21_to_30_shades_included":False,"seller_stock_26AD_packaging_edition_final_QA":False,
"original_photo_recreated":False,"other_155_JPGs_byte_identical":True,
"total_QA_JPG":156,"MK_logo_applied":False,"commercial_rights_verified":False,
"sale_ready":False,"public_55_URLs_unchanged":True,"new_public_urls":0,"excel_created_or_shared":False}
(O/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"unchanged":155,"replaced_factual_option_card":1,"shade_option_count":len(shades)}))
