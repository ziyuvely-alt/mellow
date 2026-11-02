#!/usr/bin/env python3
"""v2.4.9: reuse previous five JPGs, produce only independently sourced image frames.
No final selling claims, fabricated swatches, repeated crops or public publishing.
"""
import csv, hashlib, io, json, os, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production-v249'
OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
PREV=ROOT/'input-v248-five'
MULTI=ROOT/'input-v249-multiview'
CACHE=ROOT/'input-v249-cache'
# Visual triage 707b0f4; excludes shade charts, unrelated products, marketing models, near-duplicate CLIO packshots.
APPROVED_VISUAL_CANDIDATES={
 'pending-02':['candidate_01.jpg'],
 'pending-05':['candidate_01.jpg'],
 'pending-06':['candidate_01.webp','candidate_03.webp','candidate_04.webp'],
 'pending-07':['candidate_01.jpg'],
 'pending-10':['candidate_01.jpg'],
 'pending-22':['candidate_01.png'],
}
# Existing v248 hero image bytes are reused, never recreated.
PRIOR_IDS={'pending-01','pending-07','pending-08','pending-19','pending-23'}
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(size,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,size)
 except:return ImageFont.load_default()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def is_jpg(p):
 try:
  with Image.open(p) as im:
   return im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
 except:return False
def valid_source(p):
 if not p.is_file() or p.stat().st_size>16_000_000:return False
 try:
  with Image.open(p) as im:
   im.load()
   return im.format in ('JPEG','PNG','WEBP') and min(im.size)>=250
 except:return False
def compose(original,dest,name,frame):
 with Image.open(original) as im: photo=ImageOps.exif_transpose(im).convert('RGBA')
 bg=Image.new('RGB',(1080,1080),[(251,246,238),(245,228,219),(224,235,225),(249,244,237)][(frame-1)%4])
 d=ImageDraw.Draw(bg)
 d.rounded_rectangle((36,36,1044,1044),radius=34,outline=(221,213,201),width=2)
 # Source photo retained as authentic photograph; no false cutout for opaque sources.
 photo.thumbnail((900,805),Image.Resampling.LANCZOS)
 x=(1080-photo.width)//2;y=55+(810-photo.height)//2
 if photo.getextrema()[3]==(255,255): bg.paste(photo,(x,y))
 else:bg.paste(photo,(x,y),photo)
 f=font(34,True);line='';lines=[]
 for c in name:
  if d.textbbox((0,0),line+c,font=f)[2]>930 and line:
   lines.append(line);line=c
  else:line+=c
 if line:lines.append(line)
 for i,s in enumerate(lines[:3]):d.text((72,858+i*46),s,font=f,fill=(50,71,62))
 # No placeholder/source-review labels are printed onto images.
 # Original MK artwork is never recreated. Absence is explicitly retained as QA pending.
 q=90
 while True:
  bg.save(dest,'JPEG',quality=q,optimize=True)
  if dest.stat().st_size<2_000_000 or q<=65:break
  q-=5
 if not is_jpg(dest):raise ValueError('JPG_TECHNICAL_GATE_FAILED')
def copy_from_cache(folder,out):
 if not folder.is_dir():return 0
 count=0
 for source in sorted(folder.glob('*.jpg')):
  dest=out/source.name
  if dest.exists():continue
  if is_jpg(source):
   shutil.copy2(source,dest);count+=1
 return count
rows=[];frames=[];new_count=0; reused=0; skipped={}
for item in QUEUE:
 id=item['id'];name=item['name'];folder=OUT/id;folder.mkdir(exist_ok=True)
 existing=copy_from_cache(CACHE/id,folder)
 if id in PRIOR_IDS:
  old=PREV/id/'01_HERO_CANDIDATE.jpg'
  if not old.is_file():old=PREV/id/'01_HERO_CANDIDATE.JPG'
  if old.is_file() and is_jpg(old):
   dest=folder/'01_HERO_CANDIDATE.jpg'
   if not dest.exists():shutil.copy2(old,dest);existing+=1
 reused+=existing
 sourced=0;fail=[]
 # Multi-source photos are standalone layouts, not fake detail, claims, instructions or shade charts.
 for n,filename in enumerate(APPROVED_VISUAL_CANDIDATES.get(id,[]),1):
  src=MULTI/id/filename
  if not valid_source(src):
   fail.append('UNAVAILABLE_OR_INVALID:'+filename);continue
  ssha=digest(src)
  dest=folder/('SOURCE_%02d_%s.jpg'%(n,ssha[:9]))
  if not dest.exists():
   try:compose(src,dest,name,n);new_count+=1;sourced+=1
   except Exception as exc:fail.append(type(exc).__name__+':'+str(exc)[:80]);continue
  frames.append({'family':id,'filename':dest.name,'source':str(src.relative_to(ROOT)),'source_sha256':ssha,'image_sha256':digest(dest),'bytes':dest.stat().st_size,'type':'SOURCE_PHOTO_FRAME','sale_approved':False})
 for p in sorted(folder.glob('*.jpg')):
  if not any(f['family']==id and f['filename']==p.name for f in frames):
   frames.append({'family':id,'filename':p.name,'source':'REUSED_PREVIOUS_ARTIFACT_OR_CACHE','source_sha256':'','image_sha256':digest(p),'bytes':p.stat().st_size,'type':'REUSED_JPG','sale_approved':False})
 if not list(folder.glob('*.jpg')):
  folder.rmdir()
  reason='NO_VERIFIED_SOURCE_BYTES'
 else:reason='PARTIAL_PHOTO_PRODUCTION_FINAL_QA_DEFERRED'
 if fail:reason+=';'+';'.join(fail)
 rows.append({'id':id,'name':name,'status':'FINAL_QA_PENDING' if reason.startswith('PARTIAL') else 'SOURCE_PENDING','saved_jpg':len(list((OUT/id).glob('*.jpg'))) if (OUT/id).exists() else 0,'new_source_jpg':sourced,'reason':reason})
 print(id,rows[-1]['status'],rows[-1]['saved_jpg'],flush=True)
with (OUT/'family_checkpoint.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with (OUT/'frame_sha256_manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['family','filename','source','source_sha256','image_sha256','bytes','type','sale_approved']);w.writeheader();w.writerows(frames)
summary={'version':'2.4.9','families_total':41,'baseline_public_families':11,'baseline_public_urls':55,'queue_families':30,'reused_jpg_in_this_artifact':reused,'new_jpg':new_count,'jpg_in_artifact':len(frames),'production_families':sum(r['saved_jpg']>0 for r in rows),'source_pending':sum(r['status']=='SOURCE_PENDING' for r in rows),'final_qa_approved':0,'published':0,'notes':'Only independently sourced photos; no invented packaging, claims or swatches. Single photo is not stretched into five different sales frames.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
