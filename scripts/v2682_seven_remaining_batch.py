#!/usr/bin/env python3
"""v2682: One-shot build of 7 pending five-frame QA family sets.
Preserve all real prior photo pixels/bytes, reuse v2665 repairs where available.
Hold peripera pending-08 because the 26AD source swatch/edition is conflicting.
Never mark a layout-only/fact-only image as a final sale-quality photo.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,shutil,json,base64
SRC=Path("historical/review-JPG-by-family")
REPAIR=Path("qa-review/v2665-4-clean-copy-cards")
OUT=Path("qa-review/v2682-seven-remaining-five-JPG-reviews")
assert not OUT.exists()
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def f(n,bold=True):return ImageFont.truetype(B if bold else R,n)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(d,s,x,y,maxw,n,c):
 while n>=23 and d.textbbox((0,0),s,font=f(n))[2]>maxw:n-=2
 assert n>=23,(s,n)
 d.text((x,y),s,font=f(n),fill=c)
def infocard(spec,index,frame):
 im=Image.new("RGB",(1080,1080),"#fffdfb")
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((56,55,1024,1020),radius=34,fill="#ffffff",outline="#e1dadd",width=3)
 d.rounded_rectangle((82,82,998,267),radius=26,fill=spec["accent"])
 text(d,spec["brand"],115,136,853,57,"#443840")
 kinds=[
  ("PRODUCT INFORMATION",spec["lines"]),
  ("PRODUCT DETAILS",spec["lines"][-2:]),
  ("NET CONTENT",spec["volume"] and [spec["volume"]] or ["CHECK STOCK LABEL"]),
  ("PRODUCT GUIDE",["FOLLOW ORIGINAL","PACKAGE DIRECTIONS"])
 ]
 head,lines=kinds[index%len(kinds)]
 text(d,head,115,361,860,43,"#6c5661")
 y=506
 for item in lines:
  text(d,item,115,y,850,64,"#3b3038");y+=126
 d.line((115,881,962,881),fill="#ded3d8",width=3)
 d.text((115,930),"KOREAN BEAUTY",font=f(30,False),fill="#83747c")
 return im,head
SPECS=[
 {"id":2,"brand":"MISSHA","lines":["MAGIC CUSHION","MOIST UP"],"volume":None,
  "source":[2],"reuse":"pending-02-slot05-copy-repaired-QA-ONLY.jpg","accent":"#e9e5dd",
  "hold":"OWNED_CUSHION_SHADE_AND_PACKAGING_EDITION"},
 {"id":3,"brand":"MISSHA","lines":["M PERFECT COVER","BB CREAM"],"volume":None,
  "source":[3],"reuse":None,"accent":"#e9d6d3",
  "hold":"SHADE_21_23_25_VS_OLD_23_25_AND_MK_ISSUE"},
 {"id":4,"brand":"CLIO","lines":["MESH GLOW","MINI CUSHION"],"volume":"5 g",
  "source":[1,2,3],"reuse":None,"accent":"#eadce9",
  "hold":"MINI_21C_21N_23N_SHADE_CHART_PROOF_MK_LOGO"},
 {"id":5,"brand":"CLIO","lines":["KILL COVER","FOUNWEAR CUSHION"],"volume":None,
  "source":[3],"reuse":None,"accent":"#e3e4e0",
  "hold":"EXACT_KIT_EDITION_MAIN_REFILL_AND_COMPOSITION"},
 {"id":7,"brand":"CLIO","lines":["KILL COVER","MESH BLUR CUSHION"],"volume":None,
  "source":[2],"reuse":None,"accent":"#e0deef",
  "hold":"EXACT_PACKAGE_CONTENTS_VS_PROMOTIONAL_GIFTS"},
 {"id":15,"brand":"Dr.G","lines":["GREEN MILD UP","SUN PLUS"],"volume":"50 mL",
  "source":[3,5],"reuse":None,"accent":"#dbece4",
  "hold":"UNVERIFIED_VISIBLE_MK_MARK_AND_EXACT_STOCK_GENERATION"},
 {"id":18,"brand":"Dr.G","lines":["BRIGHTENING UP","SUN PLUS"],"volume":"50 mL",
  "source":[2,4],"reuse":None,"accent":"#f1e6d5",
  "hold":"UNVERIFIED_VISIBLE_MK_MARK_AND_EXACT_STOCK_GENERATION"}
]
rows=[]
for spec in SPECS:
 fam=f"pending-{spec['id']:02d}"
 dst=OUT/fam;dst.mkdir()
 frames=[]
 for oldslot in spec["source"]:
  ps=list((SRC/fam).glob(f"{oldslot:02d}*.jpg"))
  assert len(ps)==1,(fam,oldslot)
  original=ps[0]
  slot=len(frames)+1
  dest=dst/f"{slot:02d}-existing-actual-frame{oldslot:02d}-UNMODIFIED-QA.jpg"
  shutil.copy2(original,dest)
  assert hashfile(original)==hashfile(dest)
  frames.append({"frame":slot,"original_slot":oldslot,"file":dest.name,"sha256":hashfile(dest),
                 "kind":"HISTORICAL_ACTUAL_SOURCE_UNCHANGED"})
 if spec.get("reuse"):
  src=REPAIR/spec["reuse"];assert src.exists(),src
  ix=len(frames)+1;dest=dst/f"{ix:02d}-previous-v2665-text-repair-UNMODIFIED-QA.jpg"
  shutil.copy2(src,dest);assert hashfile(src)==hashfile(dest)
  frames.append({"frame":ix,"file":dest.name,"sha256":hashfile(dest),"kind":"PRIOR_V2665_COPY_REPAIR_UNCHANGED"})
 index=0
 while len(frames)<5:
  k=len(frames)+1;im,heading=infocard(spec,index,k)
  dest=dst/f"{k:02d}-new-{heading.lower().replace(' ','-')}-QA.jpg"
  im.save(dest,"JPEG",quality=90,optimize=True,subsampling=0)
  frames.append({"frame":k,"file":dest.name,"sha256":hashfile(dest),"kind":"NEW_FACT_ONLY_INFORMATION_CARD"})
  index+=1
 for r in frames:
  p=dst/r["file"]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  assert p.stat().st_size<2_000_000
  r["bytes"]=p.stat().st_size
 rows.append({"family":fam,"status":"FIVE_JPG_QA_DRAFT_ONLY",
  "release_hold":spec["hold"],"real_photo_count":len(spec["source"]),
  "legacy_text_repair_reused":bool(spec.get("reuse")),
  "original_kit_color_source_claims_approved":False,
  "frames":frames})
# Small multi-page sheets so actual content can be seen and inspected.
for page in range(2):
 picks=rows[page*4:(page+1)*4]
 board=Image.new("RGB",(1780,1510),"#eeefed")
 draw=ImageDraw.Draw(board)
 draw.text((17,12),f"v2682 PENDING QA REAL JPGS PAGE {page+1} / NOT RETAIL APPROVED",font=f(34),fill="#242424")
 for ri,row in enumerate(picks):
  for ci,r in enumerate(row["frames"]):
   with Image.open(OUT/row["family"]/r["file"]) as im:
    tile=im.convert("RGB").resize((323,323),Image.Resampling.LANCZOS)
   x=15+ci*351;y=59+ri*355
   board.paste(tile,(x,y))
   draw.text((x,y+324),row["family"]+" "+str(ci+1),font=f(21,False),fill="#222")
 p=OUT/f"v2682-contact-{page+1}.jpg"
 board.save(p,quality=77,optimize=True)
 (OUT/f"v2682-contact-{page+1}.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
m={"version":"v2682","base_checkpoint":"v2681",
   "new_5_JPG_QA_sets":len(rows),"physical_JPGs":len(rows)*5,
   "source_images_byte_preserved":sum(x["real_photo_count"] for x in rows),
   "v2665_existing_card_reused":1,
   "new_fact_only_frames":sum(sum(r["kind"]=="NEW_FACT_ONLY_INFORMATION_CARD" for r in x["frames"]) for x in rows),
   "not_staged":{"family":"pending-08","reason":"26AD generation and option 004 official shade naming conflict; no exact verifiable product photograph"},
   "retail_approved":0,"commercial_photo_licenses_verified":False,
   "latest_v2647_binary_compared":False,"physical_stock_options_verified":False,
   "old_11_approved_groups_changed":False,"old_55_public_urls_changed":False,
   "final_xlsx_shared":False,"rows":rows}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"QA_families":len(rows),"files":len(rows)*5,"originals":m["source_images_byte_preserved"],
"new_information":m["new_fact_only_frames"],"hold":["pending-08"],"sale_approved":0}))
