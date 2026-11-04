#!/usr/bin/env python3
"""v2665: four original non-cropped factual QA frames replacing clearly cropped text,
without inventing product photographs, swatches, gifts, MK logos or permissions.
The existing 14 candidates and published images are read-only.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json,math
OUT=Path("v2665-four-clean-copy-qa-only")
OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(s,bold=False):
 f=FONT.replace("DejaVuSans.ttf","DejaVuSans-Bold.ttf") if bold else FONT
 return ImageFont.truetype(f,s)
# Copy limited to known product names and catalog sizes; no benefit or stock-edition assertions.
records=[
 {"family":"pending-02","original_slot":5,"brand":"MISSHA","lines":["MAGIC CUSHION","MOIST UP"],"detail":"Cushion compact","note":"Exact owned-stock edition confirmation pending","accent":"#d3dfd5"},
 {"family":"pending-08","original_slot":3,"brand":"PERIPERA","lines":["MOOD GLOWY TINT"],"detail":"4 g","note":"Shade 001-020 | 26AD edition verification pending","accent":"#f1dfdb"},
 {"family":"pending-21","original_slot":3,"brand":"GOODAL","lines":["GREEN TANGERINE","VITA C EYE CREAM"],"detail":"30 mL","note":"Actual owned-stock bottle and photo rights pending","accent":"#f1e3c6"},
 {"family":"pending-26","original_slot":4,"brand":"PIXEL PURE","lines":["GENTLE GEL TO FOAM","CLEANSER"],"detail":"145 mL","note":"Do not substitute a 150 mL product photo","accent":"#d9e8dc"}
]
def rgb(hex):
 return tuple(int(hex[i:i+2],16) for i in (1,3,5))
def fitted(draw,text,max_px,weight):
 for size in range(76,25,-2):
  ft=font(size,weight)
  if draw.textbbox((0,0),text,font=ft)[2]<=max_px:return ft
 raise ValueError("Cannot fit "+text)
for r in records:
 im=Image.new("RGB",(1080,1080),"#f8f8f5");d=ImageDraw.Draw(im)
 d.rounded_rectangle((62,56,1018,1024),radius=28,fill="#ffffff",outline="#d4d9d3",width=3)
 d.rounded_rectangle((84,78,996,252),radius=24,fill=r["accent"])
 d.text((118,128),r["brand"],font=font(42,True),fill="#222f2b")
 d.text((120,298),"PRODUCT DETAILS",font=font(31,True),fill="#455b52")
 y=390
 for line in r["lines"]:
  ft=fitted(d,line,840,True)
  d.text((120,y),line,font=ft,fill="#1c3028")
  y+=d.textbbox((0,0),line,font=ft)[3]+35
 d.line((120,675,960,675),fill="#c8d6cd",width=3)
 d.text((120,723),r["detail"],font=font(64,True),fill="#1e332a")
 d.line((120,835,960,835),fill="#dce1dc",width=2)
 # fine print QA notes intentionally NOT on sale image: no English/stock claim contamination.
 d.text((120,914),"KOREAN BEAUTY",font=font(31),fill="#61736d")
 p=OUT/f'{r["family"]}-slot{r["original_slot"]:02d}-copy-repaired-QA-ONLY.jpg'
 im.save(p,quality=92,optimize=True,subsampling=0)
 assert p.stat().st_size<2_000_000
 assert Image.open(p).size==(1080,1080)
 r["path"]=p.name;r["bytes"]=p.stat().st_size;r["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
 r["status"]="TYPOGRAPHY_REPAIRED_QA_ONLY"
 r["stock_verified"]=False;r["photo_rights_verified"]=False;r["latest_v2647_compared"]=False
 r["retail_approved"]=False
# proof sheet for actual eyes-on review, source cards are not resized/cropped
proof=Image.new("RGB",(2100,2180),"#eff0ef");d=ImageDraw.Draw(proof)
d.text((38,12),"v2665 FOUR DISTINCT COPY REPAIRS / QA ONLY / NOT RETAIL",font=font(37,True),fill="#161616")
for idx,r in enumerate(records):
 im=Image.open(OUT/r["path"])
 thumb=im.resize((1000,1000),Image.Resampling.LANCZOS)
 x=35+(idx%2)*1040;y=76+(idx//2)*1050
 proof.paste(thumb,(x,y))
 d.text((x,y+1005),r["family"]+" "+r["path"][:46],font=font(23),fill="#222222")
proof.save(OUT/"v2665-four-cards-visual-contact.jpg",quality=85,optimize=True)
report={"version":"v2665","source":"v2664 rejected visual cards, facts from earlier existing evidence",
 "created_jpg":4,"technical_pass":4,"files":records,"sales_approved":0,
 "skipped_due_to_rights_or_generation":["pending-05","pending-07","pending-15","pending-22","pending-28"],
 "original_14_QA_assets_unchanged":True,"published_55_urls_unchanged":True,"approved_11_families_unchanged":True,
 "final_xlsx_shared":False,"next":"Inspect contact sheet and reject any inaccurate product copy; only after exact-stock/photo rights and v2647 proof can any candidate go to retail."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"generated":4,"family":[r["family"] for r in records],"sale_approved":0,"file_sizes":[r["bytes"] for r in records]}))
