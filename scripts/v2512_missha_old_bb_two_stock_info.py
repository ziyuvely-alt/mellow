#!/usr/bin/env python3
"""Create only two factual MISSHA M Perfect Cover BB Cream stock-option cards.
Do NOT use or fabricate old-vs-PRO product photos or artificial color swatches.
The exact owned edition of the user's stock remains unverified.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
out=Path("v2512-missha-m-perfect-bb-two-factual");out.mkdir(exist_ok=True)
font=lambda size,bold=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
def base(title,sub):
 im=Image.new("RGB",(1080,1080),"#fbf6f7");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,17),fill="#cd9ea9")
 d.text((74,59),"MISSHA",font=font(56,True),fill="#69464d")
 d.text((74,141),"M PERFECT COVER BB CREAM",font=font(34,True),fill="#69464d")
 d.line((75,219,1004,219),fill="#d5b3b9",width=3)
 d.text((74,261),title,font=font(50,True),fill="#69464d")
 d.text((74,333),sub,font=font(26),fill="#85666e")
 return im,d
def save(name,im,kind):
 p=out/name;im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 raw=p.read_bytes()
 assert Image.open(p).size==(1080,1080) and len(raw)<2_000_000
 return {"filename":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"size":[1080,1080],"content_kind":kind}
# Original inventory has exactly these three 21/23/25 options; shade-chart colors are unknown.
im,d=base("YOUR SHADE OPTIONS","Select the matching option before checkout.")
for i,(shade,ko,en) in enumerate([
 ("21","화사한 베이지","LIGHT BEIGE"),
 ("23","자연스러운 베이지","NATURAL BEIGE"),
 ("25","웜 베이지","WARM BEIGE")]):
 y=424+i*164
 d.rounded_rectangle((76,y,1003,y+143),radius=25,fill="#f0e3e8" if i!=1 else "#f1eae8")
 d.text((109,y+44),"#"+shade,font=font(44,True),fill="#69464d")
 d.text((285,y+22),ko,font=font(29,True),fill="#69464d")
 d.text((285,y+81),en,font=font(26),fill="#7e6169")
d.text((78,970),"Shade names only. Check the actual product listing.",font=font(22),fill="#896f75")
a=save("04-stock-3-shade-name-guide.jpg",im,"Verified 3 selected inventory options, no color swatches")
im,d=base("PRODUCT CHECK","Match the item you receive to your order.")
for i,(head,val) in enumerate([
 ("CHECK 01","M Perfect Cover BB Cream"),
 ("CHECK 02","Confirm your shade: 21 / 23 / 25"),
 ("CHECK 03","Check the packaging and product version")]):
 y=423+i*168
 d.rounded_rectangle((78,y,1000,y+146),radius=27,fill="#f1e4e7" if i%2==0 else "#f1eae8")
 d.text((110,y+18),head,font=font(31,True),fill="#69464d")
 d.text((110,y+80),val,font=font(24),fill="#7a5f68")
d.text((78,969),"Product version and package design may vary.",font=font(22),fill="#896f75")
b=save("05-legacy-stock-package-check.jpg",im,"Customer product/edition identification information, not packaging photo")
m={"date":"2026-11-04","family":"pending-03","product":"MISSHA M Perfect Cover BB Cream",
 "stock_options_verified":[{"shade":"21","kr":"화사한베이지"},{"shade":"23","kr":"자연스러운베이지"},{"shade":"25","kr":"웜베이지"}],
 "basis":"evidence/inventory-30-family-crosswalk-20261104.json, stock rows 8, 9, 10",
 "new_jpgs":[a,b],"old_product_JPGs_recreated":0,
 "no_fabricated_shade_pixels":True,"old_stock_edition_photo_verified":False,
 "2026_PRO_product_photo_substituted":False,"original_MK_logo_applied":False,
 "final_sales_QA":"HOLD","new_public_urls":0,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_new_jpg":len(m["new_jpgs"]),"files":[x["filename"] for x in m["new_jpgs"]]}))
