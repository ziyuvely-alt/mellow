#!/usr/bin/env python3
"""v2679 one-pass visual inventory of all remaining 16 historical pending-family JPGs,
showing original source bytes without changing or republishing anything."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,base64
ROOT=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2679-sixteen-pending-family-source-previews")
OUT.mkdir(parents=True,exist_ok=True)
ids=[2,3,4,5,7,8,15,18,21,23,24,25,26,27,29,30]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
rows=[]
for page in range(4):
 canvas=Image.new("RGB",(1770,1470),"#eeeef0");d=ImageDraw.Draw(canvas)
 d.text((12,8),f"v2679 16 FAMILIES UNSTAGED / page {page+1}/4 / HISTORICAL QA PHOTOS",fill="black",font=font)
 for ri,num in enumerate(ids[page*4:(page+1)*4]):
  fam=f'pending-{num:02d}'
  files=sorted((ROOT/fam).glob("*.jpg"))
  assert len(files)>=5,(fam,len(files))
  names=[]
  for ci,p in enumerate(files[:5]):
   with Image.open(p) as im:
    im.load()
    assert im.size==(1080,1080) and im.format=="JPEG"
    thumb=im.convert("RGB").resize((321,321),Image.Resampling.LANCZOS)
   x=12+ci*351;y=45+ri*354
   canvas.paste(thumb,(x,y))
   d.text((x,y+324),fam+" / "+p.name[:2],fill="#111",font=font)
   names.append(p.name)
  rows.append({"family":fam,"historic_source_filenames":names})
 jpg=OUT/f'v2679-sixteen-families-page-{page+1}.jpg'
 canvas.save(jpg,quality=77,optimize=True)
 (OUT/f'v2679-sixteen-families-page-{page+1}.b64.txt').write_text(base64.b64encode(jpg.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps({"version":"v2679","source":"historical v2593","families":rows,"preview_pages":4,
 "original_images_mutated":0,"sale_approved":0,"final_xlsx_not_shared":True},indent=2)+"\n")
print(json.dumps({"families":len(rows),"historic_JPGs_previewed":80,"contact_sheets":4}))
