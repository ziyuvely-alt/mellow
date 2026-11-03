#!/usr/bin/env python3
"""v2511 exact 15g OBgE Perfect Homme Cushion corrections.
Do not preserve the old beige round Perfect Cover Cushion as valid imagery.
Do not create swatch pixels, deform product art or publish third-party originals.
All five outputs are provisional candidate JPEGs only.
"""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
src=Path("v2510-sources")
out=Path("v2511-obge-homme-15g-corrected-five");out.mkdir(exist_ok=True)
ft=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
items=[]
def save(name,im,source,role):
 p=out/name;im.convert("RGB").save(p,"JPEG",quality=91,optimize=True,subsampling=0)
 b=p.read_bytes()
 assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 items.append({"filename":name,"source":source,"role":role,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"pixels":[1080,1080]})
def photo(fname,name,role,caption):
 im=Image.open(src/fname).convert("RGB")
 # preserve entire original photo, with no cutout, generated package, or fake swatch.
 canvas=Image.new("RGB",(1080,1080),"#f6f3ee")
 fit=ImageOps.contain(im,(1040,960),Image.Resampling.LANCZOS)
 canvas.paste(fit,((1080-fit.width)//2,(970-fit.height)//2+10))
 d=ImageDraw.Draw(canvas)
 d.rectangle((0,0,1080,57),fill="#eee6dd")
 d.text((38,10),"OBgE  |  PERFECT HOMME CUSHION",font=ft(27,True),fill="#453c38")
 d.rectangle((0,1016,1080,1080),fill="#eee6dd")
 d.text((40,1033),caption,font=ft(22),fill="#51443b")
 save(name,canvas,fname,role)
photo("15g-source-01.jpg","01-original-open-compact.jpg","Authentic 15g rectangular case with puff","Original 15 g product view")
photo("15g-source-03.jpg","02-original-product-and-texture.jpg","Authentic original compact with foundation texture","Real compact and foundation texture")
photo("15g-source-02.jpg","03-original-model-with-cushion.jpg","Authentic actual-model product photography, commercial rights pending","Product in use  |  15 g")
photo("15g-source-05.jpg","04-original-3shade-chart.jpg","Unmodified retailer photographed 3-shade chart; rights/edition hold","#1 Ivory  |  #2 Beige  |  #3 Sand")
im=Image.new("RGB",(1080,1080),"#f8f6f2");d=ImageDraw.Draw(im)
d.text((70,75),"OBgE",font=ft(56,True),fill="#423731")
d.text((70,173),"PERFECT HOMME CUSHION",font=ft(37,True),fill="#423731")
d.line((70,250,1010,250),fill="#c8bcb0",width=3)
for i,(head,val) in enumerate([("NET WEIGHT","15 g"),("SHADES","#1 Ivory  /  #2 Beige  /  #3 Sand"),("SUN RATING","SPF50+  PA+++")]):
 y=320+i*205
 d.rounded_rectangle((70,y,1010,y+171),radius=25,fill="#ebe4dc" if i%2==0 else "#e6ece7")
 d.text((105,y+27),head,font=ft(29),fill="#675c53")
 size=34 if i==1 else 46
 d.text((105,y+90),val,font=ft(size,True),fill="#433a34")
d.text((70,978),"Confirm the edition and shade on the purchased package.",font=ft(22),fill="#77695b")
save("05-15g-verified-product-facts.jpg",im,"verified retailer 15g specifications","15g and PA+++ not old erroneous PA++++")
m={"date":"2026-11-04","family":"pending-10","target":"OBgE Perfect Homme Cushion 15g","source_artifact":13261430991,"source_run":41696226787,
"new_jpgs":items,"old_5_jpgs":"QUARANTINE WRONG_BEIGE_ROUND_PERFECT_COVER_CUSHION","old_55_public_urls_unchanged":True,"shades":["#1 Ivory","#2 Beige","#3 Sand"],
"edition_evidence":"https://cn.hd-dfs.com/shop/gd/dtl/goos.do?onlnGoosCd=56716260000401",
"rights_verified":False,"physical_stock_packaging_verified":False,"original_MK_logo_applied":False,"sales_approved":False,"public_url_added":0,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"new_jpg_count":len(items),"files":[i["filename"] for i in items]}))
