#!/usr/bin/env python3
"""v2671 quick photo-scene chooser for previously untouched Dr.G families.
Read historical original bytes once, render only previews, never edit originals.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,base64
root=Path('source/historical/review-JPG-by-family')
fams=['pending-16','pending-17','pending-18','pending-19','pending-20']
out=Path('qa-review/v2671-drG-unreviewed-source-scenes')
out.mkdir(parents=True,exist_ok=True)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
board=Image.new('RGB',(1775,1820),'#f3f4f2')
d=ImageDraw.Draw(board)
d.text((22,14),'v2671 Dr.G SOURCE PHOTO OPTIONS: 5 NEW FAMILIES, QA REVIEW ONLY',fill='black',font=f)
results=[]
for ri,fam in enumerate(fams):
 paths=sorted((root/fam).glob('*.jpg'))
 assert len(paths)>=5,(fam,len(paths))
 row=[]
 for ci,p in enumerate(paths[:5]):
  with Image.open(p) as im:
   im.load();assert im.size==(1080,1080)
   thumb=im.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
  x=20+ci*350;y=55+ri*355
  board.paste(thumb,(x,y))
  d.text((x,y+323),fam+' / '+p.name[:2],fill='black',font=f)
  row.append({'slot':int(p.name[:2]),'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 results.append({'family':fam,'source_images':row})
p=out/'five-family-source-scenes.jpg'
board.save(p,quality=76,optimize=True)
(out/'five-family-source-scenes.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
(out/'manifest.json').write_text(json.dumps({'version':'v2671','family_count':5,'image_files_inspected':25,
'families':results,'source':'historical v2593, not latest v2647',
'approval_status':'SOURCE_SCENE_REVIEW_ONLY','original_source_bytes_changed':0},indent=2)+'\n')
print(json.dumps({'fams':5,'actual_source_photos':25,'contact_sheet_bytes':p.stat().st_size}))
