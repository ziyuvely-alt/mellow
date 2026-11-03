#!/usr/bin/env python3
"""Targeted visual repair of v2464 3 QA-failed OBgE 5g frames.
Original photos remain unaltered except whole-canvas scale; NO boxy paste.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
SRC=Path("v2463-obge-oil-control-real-photo")
OUT=Path("v2467-obge-finisher-photo-layout-repair");OUT.mkdir(exist_ok=True)
font=lambda s,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",s)
def persist(name,im,source):
 f=OUT/name; im.convert("RGB").save(f,"JPEG",quality=92,subsampling=0,optimize=True)
 b=f.read_bytes(); assert len(b)<2_000_000 and Image.open(f).size==(1080,1080)
 return {"file":name,"source":source,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"status":"FULL_BLEED_PHOTO_REPAIR_REVIEW_REQUIRED"}
# Actual official-source photo, continuous white image, no superimposed photo rectangle.
a=Image.open(SRC/"brand-global-open-compact.png").convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
d=ImageDraw.Draw(a)
d.text((50,40),"OBgE  /  OIL CONTROL FINISHER",font=font(34,True),fill="#35473d")
d.text((50,90),"Original compact view  |  5 g",font=font(25),fill="#5f665c")
f1=persist("03-open-compact-fullbleed-repair.jpg",a,"brand-global-open-compact.png")
# Different real scene from retailer: no artificial white-photo box.
b=Image.open(SRC/"retailer-dual-angle.jpg").convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
lay=Image.new("RGBA",(1080,1080),(0,0,0,0));dd=ImageDraw.Draw(lay)
dd.rounded_rectangle((32,883,1048,1045),radius=18,fill=(255,250,243,218))
dd.text((66,908),"MULTI-ANGLE PHOTO",font=font(39,True),fill="#4d3b2c")
dd.text((66,964),"Original OBgE compact and applicator views",font=font(25),fill="#5f4834")
b=Image.alpha_composite(b.convert("RGBA"),lay).convert("RGB")
f2=persist("04-multi-angle-fullbleed-repair.jpg",b,"retailer-dual-angle.jpg")
# Factual info only: separate, not a fabricated packaging photograph.
c=Image.new("RGB",(1080,1080),"#f6f4ef");d=ImageDraw.Draw(c)
d.text((68,85),"OBgE",font=font(55,True),fill="#31493a")
d.text((68,164),"OIL CONTROL FINISHER",font=font(39,True),fill="#31493a")
d.text((68,256),"PRODUCT FACTS",font=font(49,True),fill="#536658")
for i,(l,v) in enumerate([("PRODUCT","Oil Control Finisher"),("SIZE","5 g"),("SHOP","Korean stock product")]):
 y=385+i*157;d.rounded_rectangle((70,y,1010,y+122),radius=30,fill=["#e4e9de","#e9e0d5","#e4e9de"][i]);d.text((109,y+15),l,font=font(25),fill="#637568");d.text((109,y+53),v,font=font(34,True),fill="#304739")
f3=persist("05-product-facts-clean-repair.jpg",c,"seller stock record")
manifest={"date":"2026-11-04","family":"pending-09","previous_v2464_repaired_not_overwritten":True,"new_replacement_files":[f1,f2,f3],"source_artifact_run":41682388609,"photo_pixels_real":True,"product_geometry_unchanged":True,"official_MK_logo_missing":True,"license_and_inventory_final_QA_pending":True,"published":False,"excel_unchanged":True}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"real_repaired_JPGs":3,"bytes":[x["bytes"] for x in [f1,f2,f3]]}))
