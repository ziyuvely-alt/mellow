#!/usr/bin/env python3
"""Shopee Thumbnail Creator PRO v2.4.10; production first, final QA separate.
Reuses existing v249 cache and inventory-owned source images without overwriting
approved public URLs. Never fabricates packages, colors, swatches, claims or logos.
"""
import csv,hashlib,io,json,os,re,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production-v2410';OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf8'))
CACHE=ROOT/'input-v249-cache'
SRCROOT=ROOT/'public/owned86/20261029'
# Each mapping is explicitly inventory matched, not a fuzzy product-name match.
MAP={
'pending-03':'missha-m-perfect-cover-bb-cream',
'pending-04':'clio-mesh-glow-essential-cushion-mini',
'pending-09':'obge-oil-control-finisher-5g',
'pending-11':'obge-double-essence50x2',
'pending-15':'drg-green-mild-up-sun-plus-50ml',
'pending-16':'drg-red-blemish-clear-soothing-cream-70ml',
'pending-18':'drg-brightening-up-sun-plus-50ml',
'pending-22':'obge-max300ml',
'pending-24':'bioheal-boh-nad-glow-power-serum-30ml',
'pending-25':'bioheal-boh-nad-glow-boost-cream-50ml',
'pending-26':'pixelpure-gentle-gel-to-foam-cleanser-145ml',
'pending-27':'pixelpure-toner200ml',
'pending-28':'pixelpure-pad210ml',
'pending-29':'pixelpure-radiance-aqua-soothing-cream-50ml',
'pending-30':'pixelpure-serum50ml'}
# 26 is intentionally held until 145/150ml package conflict is resolved.
BLOCK={'pending-26':'145ML_150ML_LABEL_MISMATCH'}
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,n)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readimg(p):
 with Image.open(p) as im:
  im.load();return ImageOps.exif_transpose(im).convert('RGBA')
def dhash(im):
 v=ImageOps.grayscale(im).resize((9,8))
 a=list(v.getdata())
 return sum((1<<i) for i in range(64) if a[(i//8)*9+(i%8)] > a[(i//8)*9+(i%8)+1])
def unique_candidate(img, seen, limit=7):
 h=dhash(img)
 if any((h^o).bit_count()<=limit for o in seen):return False
 seen.add(h);return True
def render(photo,title,out,kind):
 # Never pretend a white rectangular photograph has transparent edges.
 bg=Image.new('RGB',(1080,1080),[(251,246,239),(244,232,224),(225,237,229),(250,243,235),(228,237,229)][(kind-1)%5])
 draw=ImageDraw.Draw(bg)
 draw.rounded_rectangle((34,34,1046,1046),radius=26,outline=(220,219,212),width=2)
 pic=photo.copy()
 pic.thumbnail((918,803),Image.Resampling.LANCZOS)
 x=(1080-pic.width)//2;y=48+(795-pic.height)//2
 if pic.getextrema()[3]==(255,255):bg.paste(pic,(x,y))
 else:bg.paste(pic,(x,y),pic)
 f=font(33,True);line='';lines=[]
 for ch in title:
  if line and draw.textbbox((0,0),line+ch,font=f)[2]>920:
   lines.append(line);line=ch
  else:line+=ch
 if line:lines.append(line)
 for ix,s in enumerate(lines[:3]):
  draw.text((70,862+ix*47),s,font=f,fill=(49,68,59))
 quality=91
 while True:
  bg.save(out,'JPEG',quality=quality,optimize=True)
  if out.stat().st_size<2_000_000 or quality<=65:break
  quality-=5
 with Image.open(out) as test:
  assert test.format=='JPEG' and test.size==(1080,1080)
 assert out.stat().st_size<2_000_000
def safe_copy(src,dst):
 if dst.exists():return False
 with Image.open(src) as im:
  if im.format!='JPEG' or im.size!=(1080,1080) or src.stat().st_size>=2_000_000:return False
 shutil.copy2(src,dst);return True
rows=[];files=[];added=0;reused=0;source_reused=0
for item in QUEUE:
 fid=item['id']; name=item['name']; dest=OUT/fid
 dest.mkdir(exist_ok=True)
 prev=CACHE/fid
 existing_paths=[]
 if prev.is_dir():
  for f in sorted(prev.glob('*.jpg')):
   output=dest/f.name
   if safe_copy(f,output):reused+=1
 seen={dhash(readimg(p)) for p in dest.glob('*.jpg')}
 sources=[];notes=[]
 if fid in BLOCK: notes.append(BLOCK[fid])
 else:
  group=MAP.get(fid)
  if group and (SRCROOT/group).is_dir():
   for p in sorted((SRCROOT/group).glob('*.jpg')):
    try:
     im=readimg(p)
     if min(im.size)<250:notes.append('LOW_RES:'+p.name);continue
     source_reused+=1
     if not unique_candidate(im,seen):
      notes.append('NEAR_DUPLICATE:'+p.name);continue
     sources.append((p,im))
    except Exception as e:notes.append('BAD_SOURCE:'+p.name+':'+str(e)[:50])
  elif group:notes.append('INVENTORY_SOURCE_NOT_FOUND')
 existing=len(list(dest.glob('*.jpg')))
 # Max 5 distinct photo-led frames; do not fill a frame with another crop of the same shot.
 for original,im in sources:
  if len(list(dest.glob('*.jpg')))>=5:break
  n=len(list(dest.glob('*.jpg')))+1
  target=dest/('INV_%02d_%s.jpg'%(n,sha(original)[:10]))
  if target.exists():continue
  render(im,name,target,n)
  added+=1
  files.append({'family':fid,'file':target.name,'sha256':sha(target),'size':target.stat().st_size,'origin':str(original.relative_to(ROOT)),'source_sha256':sha(original),'kind':'NEW_COMPOSITION_UNREVIEWED'})
 for p in sorted(dest.glob('*.jpg')):
  if not any(z['family']==fid and z['file']==p.name for z in files):
   files.append({'family':fid,'file':p.name,'sha256':sha(p),'size':p.stat().st_size,'origin':'production-assets-v249','source_sha256':'','kind':'REUSED'})
 count=len(list(dest.glob('*.jpg')))
 if count==0:
  dest.rmdir()
  state='SOURCE_PENDING'
 elif count>=5:state='FIVE_PHOTO_FRAMES_FINAL_QA_PENDING'
 else:state='PARTIAL_FRAMES_FINAL_QA_PENDING'
 if fid in BLOCK:state='SOURCE_MISMATCH_HOLD'
 rows.append({'id':fid,'name':name,'state':state,'file_count':count,'originals_referenced':len(sources),'notes':';'.join(notes) or ('NO_ADDITIONAL_SOURCE' if count<5 else 'PACKAGE_AND_RIGHTS_QA_DEFERRED')})
 print(fid,state,count,flush=True)
with (OUT/'family_checkpoint.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with (OUT/'frame_manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['family','file','sha256','size','origin','source_sha256','kind']);w.writeheader();w.writerows(files)
summary={'version':'2.4.10','queue':30,'new_jpg':added,'reused_jpg':reused,'inventory_source_files_examined':source_reused,'unique_jpg_in_artifact':len({a['sha256'] for a in files}),'newly_started_families':sum(r['file_count']>0 and r['id'] not in ['pending-01','pending-02','pending-05','pending-06','pending-07','pending-08','pending-10','pending-19','pending-22','pending-23'] for r in rows),'five_frame_candidate_families':sum(r['state']=='FIVE_PHOTO_FRAMES_FINAL_QA_PENDING' for r in rows),'final_qa_pending_families':sum(r['file_count']>0 for r in rows),'source_pending_families':sum(r['file_count']==0 for r in rows),'published':0,'baseline_public_url':55,'note':'Inventory originals may themselves be composites; multi-frame composition is NOT final merchant approval; official package, source license, claims, options and brand MK logo still require final review.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
