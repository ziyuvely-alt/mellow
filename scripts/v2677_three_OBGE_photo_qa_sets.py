#!/usr/bin/env python3
"""v2677 OBgE 3 distinct item five-frame QA batches, using selected historical
real product photos and no inferences about options/gifts. Preserve source bytes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import Counter
import hashlib,json,shutil,base64
ROOT=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2677-three-obge-five-JPG-source-led-QA-sets")
assert not OUT.exists()
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(v,bold=False):return ImageFont.truetype(B if bold else F,v)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(d,t,x,y,w,size,color):
 while size>26 and d.textbbox((0,0),t,font=font(size,True))[2]>w:size-=2
 assert d.textbbox((0,0),t,font=font(size,True))[2]<=w,(t,size)
 d.text((x,y),t,font=font(size,True),fill=color)
SPECS=[
 {"family":"pending-09","name":"OBgE Oil Control Finisher","lines":["OIL CONTROL","FINISHER"],"src":[2,4],
  "info":[("PRODUCT DETAILS",["OIL CONTROL","FINISHER"]),("NET CONTENT",["5 g","SINGLE PRODUCT"]),("PRODUCT GUIDE",["CHECK ORIGINAL","PACKAGE DIRECTIONS"])],
  "color":"#e9dcc4","block":"STOCK_VARIANT_AND_PHOTO_RIGHTS"},
 {"family":"pending-10","name":"OBgE Perfect Homme Cushion","lines":["PERFECT HOMME","CUSHION"],"src":[1,2,3],
  "info":[("PRODUCT INFORMATION",["PERFECT HOMME","CUSHION"]),("SELECT SHADE",["MATCH ORIGINAL","STOCK LABEL"])],
  "color":"#dfd4c9","block":"13G_VS_15G_REAL_STOCK_AND_SHADE_VERSION"},
 {"family":"pending-11","name":"OBgE All In One Double Essence","lines":["ALL IN ONE","DOUBLE ESSENCE"],"src":[2,4],
  "info":[("PRODUCT DETAILS",["ALL IN ONE","DOUBLE ESSENCE"]),("FORMULA INFORMATION",["50 mL + 50 mL","DUAL FORMULA"]),("PRODUCT GUIDE",["FOLLOW ORIGINAL","PACKAGE DIRECTIONS"])],
  "color":"#e2dbd2","block":"ONE_BOTTLE_VS_TWO_UNIT_SET_AND_PHOTO_RIGHTS"},
]
proof=Image.new("RGB",(1835,2100),"#eeeeed")
d=ImageDraw.Draw(proof)
d.text((20,13),"v2677 3 OBgE PRODUCT FAMILIES / 15 DISTINCT QA JPGS / NOT RETAIL",font=font(32,True),fill="#252525")
results=[]
for ri,s in enumerate(SPECS):
 fam=s["family"]; dest=OUT/fam;dest.mkdir()
 frames=[]
 for ix,slot in enumerate(s["src"],1):
  ps=list((ROOT/fam).glob(f"{slot:02d}*.jpg"))
  assert len(ps)==1,(fam,slot,ps)
  src=ps[0];target=dest/f"{ix:02d}-original-slot{slot:02d}-byte-preserved-QA.jpg"
  shutil.copy2(src,target)
  assert sha(src)==sha(target)
  frames.append({"frame":ix,"source_slot":slot,"type":"EXACT_PRIOR_REAL_PHOTO",
                 "file":target.name,"sha256":sha(target)})
 for j,(label,lines) in enumerate(s["info"],len(s["src"])+1):
  im=Image.new("RGB",(1080,1080),"#fffefb")
  dr=ImageDraw.Draw(im)
  dr.rounded_rectangle((64,55,1016,1025),radius=34,fill="#ffffff",outline="#e3ddd7",width=3)
  dr.rounded_rectangle((80,78,1000,275),radius=27,fill=s["color"])
  write(dr,"OBgE",120,140,820,57,"#3c3531")
  write(dr,label,120,364,820,42,"#64594d")
  y=510
  for ln in lines:
   write(dr,ln,120,y,820,66,"#302923");y+=125
  dr.line((120,880,960,880),fill="#d1cbc5",width=3)
  dr.text((120,920),"KOREAN BEAUTY",font=font(29),fill="#897c75")
  target=dest/f"{j:02d}-{label.lower().replace(' ','-')}-QA.jpg"
  im.save(target,format="JPEG",quality=92,optimize=True,subsampling=0)
  frames.append({"frame":j,"type":"FACT_ONLY_CUSTOM_QA_FRAME","file":target.name,
                 "sha256":sha(target)})
 assert len(frames)==5
 for f in frames:
  p=dest/f["file"]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   thumb=im.convert("RGB").resize((342,342),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  x=20+(f["frame"]-1)*363;y=70+ri*671
  proof.paste(thumb,(x,y))
  d.text((x,y+346),f'{fam} / {f["frame"]:02d}',font=font(22),fill="#252525")
  f["bytes"]=p.stat().st_size
 results.append({"family":fam,"product":s["name"],"total_files":len(frames),
                 "prior_real_photos_preserved":len(s["src"]),
                 "original_info_frames_created":len(s["info"]),
                 "release_status":"HOLD_"+s["block"],
                 "frames":frames})
p=OUT/"v2677-three-family-actual-preview.jpg"
proof.save(p,quality=80,optimize=True)
(OUT/"v2677-preview.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
manifest={"version":"v2677","baseline":"v2676","families":results,
 "total_5JPG_QA_families":3,"physical_JPGs":15,
 "prior_real_photos_preserved":sum(x["prior_real_photos_preserved"] for x in results),
 "new_factual_JPGs":sum(x["original_info_frames_created"] for x in results),
 "retail_approved":0,
 "latest_v2647_actual_photo_archive_verified":False,
 "source_photo_commercial_rights_confirmed":False,
 "stock_generation_and_exact_box_content_verified":False,
 "old_55_public_urls_mutated":False,"old_11_approved_families_mutated":False,
 "final_spreadsheet_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"actual_new_5frame_QA_families":3,"files":15,
                  "original_source_photos":manifest["prior_real_photos_preserved"],
                  "new_info_JPGs":manifest["new_factual_JPGs"],"retail_approved":0}))
