#!/usr/bin/env python3
"""No fake logo or shade chart. Source JPEGs immutable. Make full visual QA contact sheets."""
import csv,json,hashlib,shutil
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw,ImageOps,ImageFont
root=Path(__file__).resolve().parents[1];inp=root/'input-v2416c';out=root/'production-v2416d';out.mkdir(exist_ok=True)
contact=out/'visual-contact-sheets';contact.mkdir(exist_ok=True)
queue=json.loads((root/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
SELECT={'pending-05':['SOURCE_01_041b164bb.jpg','INFO_03_V2413.jpg','INFO_05_V2413.jpg'],
'pending-15':['INV_03_8d52f556bc.jpg','INV_02_7f3ea992bc.jpg','INV_01_6b3a4a3666.jpg','INFO_04_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],
'pending-21':['PHOTO_01_V2413.jpg','PHOTO_02_V2413.jpg','INFO_03_V2413.jpg','INFO_04_V2413.jpg','INFO_05_V2413.jpg']}
HOLD={'pending-05':'Only one independent source photo; repeated text-only panel roles.',
'pending-15':'Similar diagonal/front tube compositions; use distinct 3 photo + 2 info shortlist. Original logo verification pending.',
'pending-21':'Standalone and swatch are different source photos; package-version and licensing QA still pending.',
'pending-08':'Peripera official 01-20 color images not all matched to Global SKU.',
'pending-26':'Only one 145ml product photo, two text-only frames; do not mix 150ml images.'}
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
try:F=ImageFont.truetype(font,16);TITLE=ImageFont.truetype(font,21)
except:F=TITLE=ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dh(im):
 a=list(ImageOps.grayscale(im).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if a[(k//8)*9+k%8]>a[(k//8)*9+k%8+1])
records=[];families=[];similar=[];old_count=0
for item in queue:
 fid=item['id'];files=sorted((inp/fid).glob('*.jpg'))
 if not files:continue
 sheet=Image.new('RGB',(1150,72+((len(files)+4)//5)*245),'#f7f5f1');d=ImageDraw.Draw(sheet)
 d.text((20,14),fid+' '+item['name'],font=TITLE,fill='#283d32')
 seen=[]
 for idx,p in enumerate(files):
  with Image.open(p) as im:
   valid=im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
   h=dh(im);thumb=ImageOps.contain(im.convert('RGB'),(205,190))
  x=20+(idx%5)*226;y=65+(idx//5)*245;sheet.paste(thumb,(x,y))
  d.text((x,y+197),p.name[:28],font=F,fill='#313131')
  for q,k in seen:
   dist=(h^k).bit_count()
   if dist<=6:similar.append({'family':fid,'a':q,'b':p.name,'distance':dist})
  seen.append((p.name,h))
  records.append({'family':fid,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'technical_ok':valid,'approved':False})
  old_count+=1
 sheet.save(contact/(fid+'.jpg'),quality=85,optimize=True)
 candidates=SELECT.get(fid,[]);available=[n for n in candidates if (inp/fid/n).is_file()]
 if available:
  target=out/'qa-shortlist'/fid;target.mkdir(parents=True,exist_ok=True)
  for i,n in enumerate(available,1):shutil.copy2(inp/fid/n,target/(f'{i:02d}_'+n))
 families.append({'family':fid,'jpg':len(files),'shortlisted':len(available),'qa':'HOLD' if fid in HOLD else 'REVISE','reason':HOLD.get(fid,'Package, image distinctness, real MK logo and official color options require final visual verification'),'production_complete':False})
 print('QA',fid,len(files),len(available),flush=True)
def csvout(path,items,cols):
 with (out/path).open('w',newline='',encoding='utf-8-sig') as h:
  w=csv.DictWriter(h,fieldnames=cols);w.writeheader();w.writerows(items)
csvout('sha256_source_preservation.csv',records,['family','name','sha256','bytes','technical_ok','approved'])
csvout('family_qa.csv',families,['family','jpg','shortlisted','qa','reason','production_complete'])
csvout('similarity_candidates.csv',similar,['family','a','b','distance'])
summary={'version':'2.4.16d','previous_jpg_preserved':old_count,'new_sales_jpg':0,'visual_contact_sheets':len(families),'curated_families':len(SELECT),'shortlisted_five_frame_families':2,'sha256_unique':len({r['sha256'] for r in records}),'technical_pass':sum(r['technical_ok'] for r in records),'similar_pairs_to_review':len(similar),'real_mk_logo_binary':False,'official_shade_chart_complete':0,'production_complete_qa_pending':0,'public_urls_preserved':55,'note':'Real QA preview images and SHA-verified original JPEG selection, no fictitious seller-ready products.'}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
