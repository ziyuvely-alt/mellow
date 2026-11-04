#!/usr/bin/env python3
"""v2676 MISSHA Firming Repair Serum 30mL: preserve 4 historical JPGs
and replace unverified ingredient-claim card05 with neutral factual net content.
QA-only, no product-photo fabrication or public overwrite.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import shutil,hashlib,json,base64
src=Path('historical/review-JPG-by-family/pending-13')
out=Path('qa-review/v2676-missha-pdrn-serum-fiveframe-qa')
assert not out.exists()
out.mkdir(parents=True)
files=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for slot in (1,2,3,4):
 match=list(src.glob(f'{slot:02d}*.jpg'))
 assert len(match)==1,(slot,match)
 p=match[0];q=out/f'{slot:02d}-original-byte-preserved-QA.jpg'
 shutil.copy2(p,q)
 assert sha(p)==sha(q)
 files.append({'slot':slot,'file':q.name,'sha256':sha(q),'kind':'EXACT_OLD_PHOTO_PRESERVED'})
im=Image.new('RGB',(1080,1080),'#fffafa')
d=ImageDraw.Draw(im)
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(size,b=False):return ImageFont.truetype(bold if b else font,size)
def tx(s,x,y,size):
 while d.textbbox((0,0),s,font=f(size,True))[2]>880 and size>24:size-=2
 d.text((x,y),s,font=f(size,True),fill='#473034')
d.rounded_rectangle((62,62,1018,1018),radius=31,fill='#ffffff',outline='#dbcfd1',width=3)
d.rounded_rectangle((86,90,994,280),radius=25,fill='#f0dbde')
tx('MISSHA',118,146,58)
tx('PRODUCT INFORMATION',118,370,42)
tx('PDRN NAD+',118,493,68)
tx('FIRMING REPAIR SERUM',118,603,67)
d.line((120,786,960,786),fill='#dcc5c9',width=3)
tx('30 mL',118,826,70)
d.text((118,954),'KOREAN BEAUTY',font=f(29),fill='#897579')
new=out/'05-net-content-factual-only-QA.jpg';im.save(new,quality=92,optimize=True,subsampling=0)
files.append({'slot':5,'file':new.name,'sha256':sha(new),'kind':'NEW_NO_UNVERIFIED_INGREDIENT_CLAIMS'})
proof=Image.new('RGB',(1835,700),'#eef0ed');d=ImageDraw.Draw(proof)
d.text((20,16),'v2676 MISSHA PDRN SERUM: 5 UNIQUE JPEG QA FRAMES',fill='#252525',font=f(34,True))
for i,r in enumerate(files):
 p=out/r['file']
 with Image.open(p) as frame:
  frame.load();assert frame.format=='JPEG' and frame.size==(1080,1080)
  tile=frame.convert('RGB').resize((338,338),Image.Resampling.LANCZOS)
 assert p.stat().st_size<2_000_000
 x=20+i*362;proof.paste(tile,(x,72))
 d.text((x,420),f'FRAME {i+1:02d}',fill='#252525',font=f(25,True))
preview=out/'v2676-visual-sheet.jpg';proof.save(preview,quality=83,optimize=True)
(out/'v2676-sheet.b64.txt').write_text(base64.b64encode(preview.read_bytes()).decode())
(out/'manifest.json').write_text(json.dumps({'version':'v2676','family':'pending-13',
 'product':'MISSHA PDRN NAD+ Firming Repair Serum 30 mL',
 'old_real_JPGs_preserved':4,'new_safe_fact_JPGs':1,'total_JPGs':5,
 'release_status':'HOLD_PHOTO_RIGHTS_STOCK_EDITION_LATEST_V2647',
 'approved_11_products_untouched':True,'existing_55_URLs_untouched':True,
 'final_spreadsheet_shared':False,'frames':files},indent=2)+'\n')
print(json.dumps({'family':'pending-13','actual_5_JPGs':5,'preserved_JPGs':4,'new_fact_JPGs':1,'retail_approvals':0}))
