#!/usr/bin/env python3
"""v2507: Only unfilled review items: 2 targeted customer-text corrections
for Dr.G Green Mild Up Sun Plus 2022, and 1 CLIO Founwear set shade/name
information frame. No invented swatches, shades or product packshots.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
ROOT=Path("v2507-corrected-info-only")
ROOT.mkdir(exist_ok=True)
def ft(sz,b=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
def save(family,name,im,role):
 dst=ROOT/family;dst.mkdir(parents=True,exist_ok=True)
 p=dst/name;im.convert("RGB").save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes()
 assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 return dict(family=family,file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),pixels=[1080,1080],role=role,public=False)
def base(brand,product,title,description,bg="#f7faf7"):
 im=Image.new("RGB",(1080,1080),bg);d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,18),fill="#80b497")
 d.text((68,56),brand,font=ft(48,True),fill="#315b4c")
 d.text((68,128),product,font=ft(31,True),fill="#315b4c")
 d.line((70,195,1010,195),fill="#aecbbb",width=3)
 d.text((70,235),title,font=ft(52,True),fill="#2d5246")
 d.text((70,323),description,font=ft(25),fill="#54776a")
 return im,d
im,d=base("Dr.G","GREEN MILD UP SUN PLUS","MINERAL SUN CARE","Product details  |  50 mL")
for i,(label,val) in enumerate([("TYPE","Mineral sunscreen"),("NET CONTENT","50 mL"),("UV RATING","SPF50+ / PA++++")]):
 y=412+i*175
 d.rounded_rectangle((77,y,1003,y+144),radius=24,fill="#e4eee8" if i!=1 else "#edf1e9")
 d.text((108,y+14),label,font=ft(26),fill="#5d7a69")
 d.text((108,y+61),val,font=ft(40,True),fill="#345b4b")
d.text((75,977),"Follow the information on the product packaging.",font=ft(23),fill="#5e7567")
a=save("pending-15","03-mineral-facts-clean.jpg",im,"Factual SPF and 50mL information; only footer corrected")
im,d=base("Dr.G","GREEN MILD UP SUN PLUS","HOW TO APPLY","Daily sunscreen application guide")
for i,(head,body) in enumerate([("01  TAKE","Take a suitable amount of sunscreen."),("02  SPREAD","Apply evenly to sun-exposed skin."),("03  REAPPLY","Reapply as instructed on the package.")]):
 y=403+i*176
 d.rounded_rectangle((77,y,1003,y+145),radius=24,fill="#e3eee6" if i!=1 else "#edf0e8")
 d.text((110,y+14),head,font=ft(33,True),fill="#365d4d")
 d.text((110,y+80),body,font=ft(24),fill="#536e60")
d.text((75,977),"Use according to the directions on the package.",font=ft(22),fill="#5e7567")
b=save("pending-15","05-usage-clean.jpg",im,"Customer-oriented factual application card, no internal QA footer")
# CLIO official seller's five shades match exact inventory; no invented shade colors.
im,d=base("CLIO","KILL COVER FOUNWEAR CUSHION","5 SHADES","Cushion foundation  |  Original + refill","#f8f7f5")
shades=[("19C","LIGHT"),("19N","PORCELAIN"),("21C","LINGERIE"),("21N","LINEN"),("23N","GINGER")]
for i,(code,name) in enumerate(shades):
 y=396+i*104
 d.rounded_rectangle((78,y,1000,y+90),radius=22,fill="#e7e8e4" if i%2 else "#e0e9e3")
 d.text((115,y+22),code,font=ft(32,True),fill="#294738")
 d.text((320,y+23),name,font=ft(29,True),fill="#294738")
d.text((80,964),"Choose the exact shade number and name in the listing.",font=ft(22),fill="#587265")
c=save("pending-05","06-verified-five-shade-name-guide.jpg",im,"Text-only authentic five option name guide, not an official swatch image")
manifest={"created_utc":"2026-11-04","purpose":"Targeted corrections and one missing option-name frame","source":{"drg":"previous v2506 accepted technical JPG, exclusion of unverified 2021 zinc ingredient", "clio":"Official CLIO-managed SSG Founwear 2x15g listing and GS shop 5 shades"},
 "new_files":[a,b,c],"not_recreated":["pending-15 original 2 real product photos","pending-15 04-zinc-oxide card remains QA hold","pending-05 prior 5 JPGs"],
 "no_fabricated_shade_swatches":True,"official_licensed_photo_missing":True,"original_MK_logo_missing":True,"physical_inventory_edition_verified":False,"sales_ready":False,"public_55_urls_unchanged":True,"spreadsheet_shared":False}
(ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"actual_jpg":3,"names":[x["file"] for x in manifest["new_files"]]}))
