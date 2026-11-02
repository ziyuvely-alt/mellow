#!/usr/bin/env python3
"""Continue v2.4.16 safe source-first production from the last checkpoint.
Preserve 158 source JPG exactly and produce 2 new text-led evidence panels.
Never claim sales QA, MK logo, shades, or fabricated product photographs.
"""
import csv,hashlib,json,shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'input-v2416'
OUT=ROOT/'production-v2416-continuation';OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf8'))
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
OFFICIAL='https://eng.pixelpure.com/product/pixelpure-gentle-gel-to-foam-cleanser-145ml/21/'
def ft(n,b=False):
 try:return ImageFont.truetype(BOLD if b else FONT,n)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def panel(path,number):
 bg=Image.new('RGB',(1080,1080),(249,240,233) if number==2 else (226,238,228))
 d=ImageDraw.Draw(bg)
 dark=(45,65,57)
 d.text((78,78),'PIXELPURE   /   GENTLE CLEANSER',font=ft(31,True),fill=dark)
 d.line((78,141,1005,141),fill=(134,166,144),width=3)
 d.text((80,205),'PRODUCT FACTS' if number==2 else 'DAILY CLEANSING',font=ft(51,True),fill=dark)
 d.rounded_rectangle((70,329,1010,757),radius=42,fill=(255,252,246))
 if number==2:
  d.text((125,406),'145 mL',font=ft(105,True),fill=dark)
  d.text((128,578),'GEL-TO-FOAM',font=ft(50,True),fill=dark)
  d.text((128,650),'공식 제품명 · 용량 기준',font=ft(32),fill=dark)
 else:
  d.text((127,402),'GEL CLEANSER',font=ft(64,True),fill=dark)
  d.text((129,556),'아침 · 저녁 데일리 클렌징',font=ft(39,True),fill=dark)
  d.text((128,646),'사용 경험 요약 기반 · 효능 주장 아님',font=ft(25),fill=dark)
 d.text((77,842),'Pixelpure Gentle Gel-to-Foam Cleanser',font=ft(30,True),fill=dark)
 d.text((77,925),'Official page: 145 mL / Final artwork QA pending',font=ft(24),fill=dark)
 bg.save(path,'JPEG',quality=90,optimize=True)
 with Image.open(path) as i:assert i.format=='JPEG' and i.size==(1080,1080)
 assert path.stat().st_size<2_000_000
rows=[]; frames=[];new=0;old_count=0
for q in QUEUE:
 fid=q['id']; dest=OUT/fid;dest.mkdir(exist_ok=True)
 original=IN/fid
 if original.is_dir():
  for p in sorted(original.glob('*.jpg')):
   shutil.copy2(p,dest/p.name);old_count+=1
 if fid=='pending-26':
  for n in (2,3):
   p=dest/f'PIXELPURE_INFO_{n:02d}_V2416C.jpg'
   panel(p,n);new+=1
 files=list(dest.glob('*.jpg'))
 if not files:dest.rmdir()
 for p in files:
  with Image.open(p) as im:
   assert im.format=='JPEG' and im.size==(1080,1080)
  frames.append({'family':fid,'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'original':'YES' if not p.name.endswith('_V2416C.jpg') else 'NO','source':OFFICIAL if p.name.endswith('_V2416C.jpg') else 'PRESERVED_V2416'})
 rows.append({'family':fid,'jpg':len(files),'new':2 if fid=='pending-26' else 0,'state':'FIVE_FRAME_DRAFT' if len(files)>=5 else 'PARTIAL_JPG' if files else 'SOURCE_PENDING','production_complete_qa_pending':False,'logo_confirmed':False,'shade_chart_approved':False})
 print('family',fid,len(files),flush=True)
def csvout(p,entries,fields):
 with p.open('w',newline='',encoding='utf-8-sig') as h:
  writer=csv.DictWriter(h,fieldnames=fields);writer.writeheader();writer.writerows(entries)
csvout(OUT/'frame_sha256_manifest.csv',frames,['family','file','sha256','bytes','original','source'])
csvout(OUT/'family_checkpoint.csv',rows,['family','jpg','new','state','production_complete_qa_pending','logo_confirmed','shade_chart_approved'])
summary={'version':'2.4.16-continuation','reused_jpg':old_count,'new_jpg':new,'artifact_jpg':len(frames),'unique_sha256':len({r['sha256'] for r in frames}),'five_or_more':sum(r['jpg']>=5 for r in rows),'partial':sum(0<r['jpg']<5 for r in rows),'original_mk_logo_binary':False,'official_swatch_complete':0,'production_complete_qa_pending':0,'public_urls_preserved':55,'note':'New images are evidence-based text panels, not additional independent photos; no seller finalization.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
