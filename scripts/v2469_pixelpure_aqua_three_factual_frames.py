#!/usr/bin/env python3
"""Create only the 3 missing Pixelpure Aqua Soothing Cream 50ml JPGs, preserving previous 2.
Authentic brand photo pixels are preserved by full-canvas photo; no synthetic packaging/claims.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
SRC=Path("v2468-pixelpure-cream-50ml-gallery")
OUT=Path("v2469-pixelpure-cream-three-new-JPG");OUT.mkdir(exist_ok=True)
ft=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(name,im,source):
 path=OUT/name; im.convert("RGB").save(path,"JPEG",quality=90,subsampling=0,optimize=True)
 b=path.read_bytes()
 assert len(b)<2_000_000 and Image.open(path).size==(1080,1080)
 return {"file":name,"origin":source,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"status":"LOCAL_JPG_READY_FINAL_QA_HOLD"}
def photo(src,name,heading,subtitle,band="bottom"):
 raw=Image.open(SRC/src).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
 # Exact product pixels remain unchanged; header text only in peripheral white/lower scene.
 overlay=Image.new("RGBA",(1080,1080),(0,0,0,0));d=ImageDraw.Draw(overlay)
 y=905 if band=="bottom" else 22
 d.rounded_rectangle((30,y,1050,y+145),radius=16,fill=(255,255,255,218))
 d.text((52,y+11),"PIXEL PURE",font=ft(27,True),fill="#344447")
 d.text((52,y+49),heading,font=ft(39,True),fill="#344447")
 d.text((52,y+102),subtitle,font=ft(22),fill="#526064")
 return save(name,Image.alpha_composite(raw.convert("RGBA"),overlay).convert("RGB"),src)
a=photo("original-02.jpg","03-real-cream-jar-photo.jpg","RADIANCE AQUA SOOTHING CREAM","Authentic closed-jar product photo | 50 mL")
b=photo("original-04.jpg","04-real-open-jar-photo.jpg","PRODUCT TEXTURE VIEW","Authentic open-jar photograph | 50 mL")
c=Image.new("RGB",(1080,1080),"#f7f4f4");d=ImageDraw.Draw(c)
d.text((82,73),"PIXEL PURE",font=ft(49,True),fill="#3d4d53")
d.text((82,158),"RADIANCE AQUA",font=ft(53,True),fill="#33474c")
d.text((82,218),"SOOTHING CREAM",font=ft(53,True),fill="#33474c")
d.line((80,310,995,310),fill="#c9c3c8",width=3)
for i,(name,value) in enumerate([("PRODUCT TYPE","Moisturizing face cream"),("NET CONTENT","50 mL"),("PACKAGE","Jar format")]):
 y=365+170*i
 d.rounded_rectangle((80,y,1000,y+144),radius=24,fill=["#eadfe4","#e7ede9","#eadfe4"][i])
 d.text((112,y+14),name,font=ft(25),fill="#607279")
 d.text((112,y+65),value,font=ft(39,True),fill="#394e52")
d.text((81,963),"Product details only. Check the original packaging before use.",font=ft(21),fill="#66747a")
third=save("05-product-format-50ml.jpg",c,"Official 50ml jar product page factual description")
manifest={"date":"2026-11-04","family_id":"pending-29","prior_jpg_reused_untouched":2,"new_jpg":[a,b,third],"official_page":"https://www.pixelpure.com/product/detail.html?product_no=26","official_source_artifact":13253792183,"no_unverified_ingredients_or_clinical_claims":True,"actual_original_MK_logo":False,"commercial_photo_reuse_rights_checked":False,"stock_edition_QA_passed":False,"published_new_urls":0,"excel_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_files":3,"bytes":[x["bytes"] for x in [a,b,third]]}))
