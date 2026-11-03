#!/usr/bin/env python3
"""Goodal 25AD eye cream: 3 NEW verified-photo/factual JPG candidates only.
No prior customer images overwritten, no made-up package, claims, or original MK logo.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json
SOURCE=Path("v2504-goodal-eye-originals")
OUT=Path("v2505-goodal-eye-three-JPG-review");OUT.mkdir(exist_ok=True)
def font(n,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
def save(name,im,role):
 path=OUT/name;im.convert("RGB").save(path,"JPEG",quality=91,optimize=True,subsampling=0)
 content=path.read_bytes()
 assert Image.open(path).size==(1080,1080) and len(content)<2000000
 return {"file":name,"bytes":len(content),"sha256":hashlib.sha256(content).hexdigest(),"resolution":[1080,1080],"role":role,"status":"REVIEW_ONLY_FINAL_STOCK_AND_PHOTO_RIGHTS_QA_HOLD"}
def scene(filename,outname,title,description):
 image=Image.open(SOURCE/filename).convert("RGB")
 # Exact genuine photo with original objects/pixels and no generated color swatches.
 canvas=Image.new("RGB",(1080,1080),"#ffffff")
 photo=ImageOps.contain(image,(1020,810),Image.Resampling.LANCZOS)
 canvas.paste(photo,((1080-photo.width)//2,145+(810-photo.height)//2))
 d=ImageDraw.Draw(canvas)
 d.text((54,31),"goodal",font=font(45,True),fill="#376d3f")
 d.text((54,87),"VITA-C DARK SPOT CARE EYE CREAM",font=font(29,True),fill="#425d45")
 d.line((48,972,1032,972),fill="#b6c9a7",width=2)
 d.text((53,989),description,font=font(22),fill="#637763")
 return save(outname,canvas,title)
one=scene("single-yellow-tube.jpg","03-real-30ml-eye-cream-front.jpg","Real front-facing tube photograph","Eye cream  |  30 mL")
two=scene("cream-texture-tube.jpg","04-real-tube-and-texture.jpg","Real source photo with cream texture","Genuine product view  |  30 mL")
im=Image.new("RGB",(1080,1080),"#f7f8f0");d=ImageDraw.Draw(im)
d.rectangle((0,0,1080,18),fill="#a8c77b")
d.text((74,63),"goodal",font=font(49,True),fill="#3c654a")
d.text((74,163),"GREEN TANGERINE",font=font(49,True),fill="#3c654a")
d.text((74,220),"VITA-C EYE CREAM",font=font(47,True),fill="#3c654a")
d.text((74,306),"PRODUCT IDENTIFICATION",font=font(29),fill="#657969")
for i,(label,value) in enumerate([("PRODUCT TYPE","Eye cream"),("NET CONTENT","30 mL"),("PACKAGE TYPE","Tube")]):
 y=394+i*175
 d.rounded_rectangle((78,y,1002,y+144),radius=22,fill="#e3ecda" if i!=1 else "#eff1e6")
 d.text((112,y+17),label,font=font(27),fill="#617b64")
 d.text((112,y+66),value,font=font(40,True),fill="#375f43")
d.text((72,969),"Check your actual stock packaging for edition and instructions.",font=font(22),fill="#6b7e65")
three=save("05-30ml-product-facts.jpg",im,"Factual tube/30ml format")
manifest={
 "date":"2026-11-04","family_id":"pending-21",
 "product":"Goodal Green Tangerine Vita C Dark Spot Care Eye Cream 30mL",
 "source_run":41693239543,"source_artifact_id":13257049730,
 "original_photo_files":["single-yellow-tube.jpg","cream-texture-tube.jpg"],
 "previous_customer_JPGs_recreated":0,
 "new_JPGs":[one,two,three],
 "exact_25AD_stock_packaging_confirmed":False,
 "external_photo_commercial_rights_verified":False,
 "original_MellowKR_MK_logo_applied":False,
 "shade_fabrication":False,
 "sales_QA_approved":False,
 "new_public_urls":0,
 "excel_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"files_created":len(manifest["new_JPGs"]),"filenames":[x["file"] for x in manifest["new_JPGs"]]}))
