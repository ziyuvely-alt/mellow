#!/usr/bin/env python3
"""v2674: one-pass real visual contact proof of 12 yet-unassembled families.
Does not regenerate or rewrite source images; no automatic sale approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,base64,hashlib
ROOT=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2674-unassembled-family-source-contact")
assert not OUT.exists()
OUT.mkdir(parents=True)
ids=[1,3,4,6,9,10,11,12,13,14,15,18]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
manifest=[]
for half in range(2):
 board=Image.new("RGB",(1775,2200),"#eceeeb")
 d=ImageDraw.Draw(board)
 d.text((20,10),f"v2674 ORIGINAL UNASSEMBLED FAMILY JPG PREVIEW / PAGE {half+1} / QA ONLY",font=font,fill="#222")
 for i,idx in enumerate(ids[half*6:(half+1)*6]):
  fam=f"pending-{idx:02d}"
  srcs=sorted((ROOT/fam).glob("*.jpg"))
  assert len(srcs)>=5,(fam,len(srcs))
  frames=[]
  for j,p in enumerate(srcs[:5]):
   with Image.open(p) as im:
    im.load(); assert im.size==(1080,1080)
    tile=im.convert("RGB").resize((322,322),Image.Resampling.LANCZOS)
   x=20+j*350; y=45+i*357
   board.paste(tile,(x,y))
   d.text((x,y+325),f"{fam} / {p.name[:2]}",font=font,fill="#222")
   frames.append({"slot":j+1,"source":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
  manifest.append({"family":fam,"frames":frames})
 photo=OUT/f"v2674-review-page{half+1}.jpg"
 board.save(photo,quality=75,optimize=True)
 (OUT/f"v2674-review-page{half+1}.b64.txt").write_text(base64.b64encode(photo.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps({"version":"v2674","families":manifest,
 "source":"historic v2593 156 JPEGs, current v2647 unverified",
 "retail_approved":0,"source_bytes_unchanged":True,"no_spreadsheet":True},indent=2)+"\n")
print(json.dumps({"reviewed_families":12,"actual_JPG_previews":60,"contact_pages":2,"sale_approved":0}))
