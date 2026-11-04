#!/usr/bin/env python3
"""v2666 PHOTO TRIAGE ONLY: show original, non-cropped five rejected families
in a compact contact sheet. Preserve every byte, no sale claims."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,base64
SRC=Path("source/older/review-JPG-by-family")
OUT=Path("v2666-five-photo-scene-visual-QA");OUT.mkdir(exist_ok=True)
fams=["pending-05","pending-07","pending-15","pending-22","pending-28"]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
data=[]
for fam in fams:
 p=sorted((SRC/fam).glob("*.jpg"))
 assert len(p)==6 if fam in ("pending-05","pending-07") else len(p)==5
 entries=[]
 for item in p:
  with Image.open(item) as im:
   im.load()
   assert im.size==(1080,1080)
  entries.append({"slot":int(item.name[:2]),"sha256":hashlib.sha256(item.read_bytes()).hexdigest(),
       "filename":item.name})
 data.append({"family":fam,"images":entries})
board=Image.new("RGB",(1500,1810),"#f5f5f6");d=ImageDraw.Draw(board)
d.text((25,12),"v2666 Historical REAL JPEG gallery | 5 families | QA ONLY",font=font,fill="#151515")
for ri,row in enumerate(data):
 for ci,entry in enumerate(row["images"]):
  p=SRC/row["family"]/entry["filename"]
  im=Image.open(p).convert("RGB").resize((226,226),Image.Resampling.LANCZOS)
  x=20+ci*245;y=48+ri*347
  board.paste(im,(x,y))
  d.text((x,y+229),row["family"]+" / "+str(entry["slot"]).zfill(2),font=font,fill="#111111")
d.text((20,1790),"Historical v2593 input, NOT v2647 latest; review packaging, captions, photo rights",font=font,fill="#111111")
photo=OUT/"five-family-original-scene-contact.jpg"
board.save(photo,quality=70,optimize=True)
(OUT/"five-family-original-scene-contact.b64.txt").write_text(base64.b64encode(photo.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps({"version":"v2666","origin":"v2593 historical source images",
"no_current_v2647_claim":True,"actual_families":data,
"retail_approved":False,"images_reencoded_for_retail":0,
"existing_55_urls_unchanged":True,"original_14_candidate_files_unchanged":True,"xlsx":False},indent=2)+"\n")
print(json.dumps({"families":5,"input_files":sum(len(x['images']) for x in data),
 "preview_bytes":photo.stat().st_size,"sales_approved":0}))
