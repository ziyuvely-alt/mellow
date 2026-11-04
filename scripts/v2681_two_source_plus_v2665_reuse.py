#!/usr/bin/env python3
"""v2681: complete 5 physical JPEG QA frames for Goodal Eye Cream and
Pixel Pure 145mL Gel-to-Foam cleanser, reusing exactly previously produced v2665
text-repaired JPEG rather than regenerating and two existing product photos per SKU.
Remaining cards factual and source edition unverified => no retail approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,base64,shutil
SRC=Path("historical/review-JPG-by-family")
PREV=Path("qa-review/v2665-4-clean-copy-cards")
OUT=Path("qa-review/v2681-two-eyecleanser-five-frame-qa")
assert PREV.exists() and not OUT.exists()
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda sz,b=True:ImageFont.truetype(B if b else F,sz)
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
specs=[
 dict(fam="pending-21",brand="GOODAL",name=["GREEN TANGERINE","VITA C EYE CREAM"],volume="30 mL",
      source=[4,5],prior="pending-21-slot03-copy-repaired-QA-ONLY.jpg",accent="#f0e9c9",
      hold="PHOTO_RIGHTS_STOCK_EDITION_AND_EYE_CREAM_LABEL"),
 dict(fam="pending-26",brand="PIXEL PURE",name=["GENTLE GEL TO FOAM","CLEANSER"],volume="145 mL",
      source=[3,5],prior="pending-26-slot04-copy-repaired-QA-ONLY.jpg",accent="#d7e9e1",
      hold="PHOTO_145ML_INVENTORY_CONFIRMATION_NOT_150ML_AND_RIGHTS")
]
rows=[]
preview=Image.new("RGB",(1840,1490),"#eff0ed");pd=ImageDraw.Draw(preview)
pd.text((25,16),"v2681 GOODAL + PIXELPURE: TWO REPAIRED 5-JPG QA FAMILIES",font=ft(35),fill="#222222")
for ix,s in enumerate(specs):
 folder=OUT/s["fam"];folder.mkdir()
 frames=[]
 for frame,slot in enumerate(s["source"],1):
  original=list((SRC/s["fam"]).glob(f"{slot:02d}*.jpg"))
  assert len(original)==1,(s["fam"],slot,len(original))
  original=original[0]
  dst=folder/f"{frame:02d}-unmodified-real-source-slot{slot:02d}-QA.jpg"
  shutil.copy2(original,dst)
  assert sh(original)==sh(dst)
  frames.append(dict(frame=frame,type="EXACT_SOURCE_PHOTO",file=dst.name,sha256=sh(dst),source_slot=slot))
 former=PREV/s["prior"]
 assert former.exists()
 third=folder/"03-v2665-text-repair-reused-byte-identical-QA.jpg"
 shutil.copy2(former,third);assert sh(former)==sh(third)
 frames.append(dict(frame=3,type="EXACT_V2665_APPROVED_TEXT_REPAIR_REUSED",file=third.name,sha256=sh(third)))
 for k,heading,lines in [(4,"NET CONTENT",[s["volume"],"SINGLE PRODUCT"]),
                         (5,"PRODUCT INFORMATION",s["name"])]:
  im=Image.new("RGB",(1080,1080),"#fcfcfa");d=ImageDraw.Draw(im)
  d.rounded_rectangle((64,58,1016,1019),radius=35,fill="#ffffff",outline="#d9dcd8",width=3)
  d.rounded_rectangle((90,88,990,270),radius=28,fill=s["accent"])
  d.text((120,143),s["brand"],font=ft(57),fill="#3a4942")
  d.text((120,355),heading,font=ft(40),fill="#54655c")
  y=515
  for line in lines:
   size=66
   while d.textbbox((0,0),line,font=ft(size))[2]>836 and size>24:size-=2
   assert size>24
   d.text((120,y),line,font=ft(size),fill="#303b35");y+=121
  d.line((120,880,960,880),fill="#d7dcd8",width=3)
  d.text((120,926),"KOREAN BEAUTY",font=ft(30,False),fill="#68776e")
  dest=folder/f"{k:02d}-{heading.lower().replace(' ','-')}-factual-QA.jpg"
  im.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
  frames.append(dict(frame=k,type="NEW_FACTUAL_INFO",file=dest.name,sha256=sh(dest)))
 assert len(frames)==5
 for frame in frames:
  p=folder/frame["file"]
  with Image.open(p) as image:
   image.load();assert image.format=="JPEG" and image.size==(1080,1080)
   thumb=image.convert("RGB").resize((343,343),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  x=18+(frame["frame"]-1)*363;y=60+ix*705
  preview.paste(thumb,(x,y))
  pd.text((x,y+350),s["fam"]+" / "+str(frame["frame"]).zfill(2),font=ft(23),fill="#292929")
  frame["bytes"]=p.stat().st_size
 rows.append(dict(family=s["fam"],jpg_count=5,real_source_count=2,v2665_reused_text_count=1,
                  factual_info_new=2,approval="HOLD_"+s["hold"],frames=frames))
pr=OUT/"v2681-two-family-proof.jpg";preview.save(pr,quality=84,optimize=True)
(OUT/"v2681-two-family-proof.b64.txt").write_text(base64.b64encode(pr.read_bytes()).decode())
summary=dict(version="v2681",baseline="v2680",new_fiveframe_QA_sets=2,
             existing_historical_source_jpg_byte_preserved=4,
             existing_v2665_text_repair_jpg_byte_preserved=2,
             newly_generated_factual_info_JPGs=4,total_physical_JPGs=10,
             sales_approved=0,legacy_11_approved_untouched=True,public_55_URLs_untouched=True,
             exact_stock_edition_verified=False,commercial_rights_confirmed=False,
             latest_v2647_compared=False,final_spreadsheet_shared=False,
             families=rows)
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_QA_families":2,"total_physical_JPG":10,
                  "old_source_preserved":4,"previous_v2665_card_reused":2,
                  "new_info_images":4,"retail_approved":0}))
