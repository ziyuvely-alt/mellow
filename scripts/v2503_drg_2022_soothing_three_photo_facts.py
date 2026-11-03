#!/usr/bin/env python3
"""Produce 3 new 2022-era Dr.G Red Blemish Clear Soothing Cream 70ml draft JPGs.
Do not substitute modern EX formula photos. Preserve 2 existing prior customer JPGs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json
S=Path("v2502-old-source/tenbyten-old-jar-carton.jpg")
assert S.is_file(),"Exact genuine old-package image missing"
O=Path("v2503-drg-old-2022-three-JPG");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def write(name,im,role):
 p=O/name;im.convert("RGB").save(p,"JPEG",quality=91,optimize=True,subsampling=0)
 raw=p.read_bytes();assert len(raw)<2_000_000 and Image.open(p).size==(1080,1080)
 return {"filename":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"dimensions":[1080,1080],"role":role,"status":"CUSTOMER_DRAFT_NOT_PUBLISHED"}
img=Image.open(S).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
# product full-bleed, not artificially cut out; retain genuine jar and carton.
one=write("03-original-old-jar-carton.jpg",img,"Original old packaging photograph")
p=Image.new("RGB",(1080,1080),"#f7f9f6");d=ImageDraw.Draw(p)
d.rectangle((0,0,1080,15),fill="#568172")
d.text((78,70),"Dr.G",font=F(55,True),fill="#234837")
d.text((78,174),"R.E.D BLEMISH",font=F(54,True),fill="#315e44")
d.text((78,241),"CLEAR SOOTHING CREAM",font=F(40,True),fill="#315e44")
d.text((80,329),"PRODUCT FORMAT",font=F(31),fill="#597b62")
for i,(h,v) in enumerate([("TEXTURE","Cream"),("NET CONTENT","70 mL"),("PACKAGE","Jar")]):
 y=408+170*i
 d.rounded_rectangle((78,y,1002,y+138),radius=26,fill="#e2ece3" if i!=1 else "#edf0e7")
 d.text((108,y+17),h,font=F(27),fill="#5c7663")
 d.text((108,y+66),v,font=F(39,True),fill="#2c523c")
d.text((80,961),"Compare your purchased package with the product photo.",font=F(22),fill="#56715e")
two=write("04-product-format-70ml.jpg",p,"Factual net content, jar format; no formula or clinical claims")
q=Image.new("RGB",(1080,1080),"#f8f9f5");d=ImageDraw.Draw(q)
d.text((76,76),"Dr.G  |  RED BLEMISH",font=F(42,True),fill="#305a42")
d.text((76,164),"HOW TO APPLY",font=F(62,True),fill="#315a43")
d.text((76,260),"Clear Soothing Cream",font=F(30),fill="#5d745f")
for i,(h,v) in enumerate([("01  TAKE","Take a suitable amount of cream."),("02  APPLY","Spread evenly across the face."),("03  ABSORB","Let the cream absorb into the skin.")]):
 y=370+i*177
 d.rounded_rectangle((76,y,1003,y+150),radius=24,fill="#e3ede3" if i!=1 else "#eef0e6")
 d.text((108,y+19),h,font=F(34,True),fill="#315a43")
 d.text((108,y+85),v,font=F(25),fill="#577361")
d.text((76,959),"Read the instructions on your original product package.",font=F(22),fill="#56715e")
three=write("05-basic-use-guide.jpg",q,"Use steps grounded in old product retailer directions")
manifest={"date":"2026-11-04","family_id":"pending-16","product":"Dr.G R.E.D Blemish Clear Soothing Cream 70mL 2022-era",
"source_run":41692792277,"source_photo_file":"tenbyten-old-jar-carton.jpg",
"source_reference":"https://www.10x10.co.kr/shopping/category_prd.asp?itemid=4488766",
"directions_reference":"https://www.elandmall.co.kr/i/item?itemNo=2201189584",
"reused_old_preexisting_jpgs":0,"new_JPGs":[one,two,three],
"not_using_modern_EX_images":True,"physically_verified_old_stock_package":False,
"photograph_commercial_rights_verified":False,"original_MK_logo_available":False,
"final_customer_QA_approved":False,"new_public_urls":0,"xls_or_sheets_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"new_actual_jpg_count":3,"new_files":[x["filename"] for x in manifest["new_JPGs"]]}))
