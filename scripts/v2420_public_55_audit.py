#!/usr/bin/env python3
"""v2.4.20 public first: inspect candidate 11 already-published 5-frame sets.
Never modify public/images, deploy, or assert guessed URLs are previously verified.
Archive raw actual HTTP bytes and source GitHub originals, compare SHA and visual layouts.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageDraw,ImageFont,ImageOps
from urllib.parse import quote
from io import BytesIO
import requests,hashlib,csv,json,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production-v2420-public-audit';OUT.mkdir(exist_ok=True)
BASE='https://mellow-bbia-images.onrender.com/'
REGULAR=[
'bioheal-boh-collagen-remodeling-eye-patch-60-v242-20261101',
'bioheal-boh-probioderm-3d-lifting-cream-50ml-realphoto-v230-20261031',
'clio-kill-cover-founwear-cushion-original-mini-sourcephoto-v245b-cutout-20261101',
'goodal-serum-alpha-40ml-qa-20261031',
'lamelin-miracle-nmn-pdrn-biotox-cream-50ml-sourcephoto-v243-20261101',
'lamelin-miracle-nmn-pdrn-biotox-mask-pack-v244-20261101',
'lamelin-miracle-nmn-pdrn-needle-shot-hair-serum-22-v244-20261101',
'missha-glow-bb-boomer-40ml-realphoto-20261031',
'missha-time-revolution-first-essence-lotion-5x-130ml-v242-20261101',
'obge-pore-zero-fresh-all-in-one-150ml-v241-recovered-5jpg-20261031'
]
items=[]
for name in REGULAR:
 for i in range(1,6):items.append({'family':name,'slot':i,'rel':f'images/{name}/{i:02d}.jpg'})
name='obge-natural-cover-lotion-50g-10ml'
for i in range(1,6):
 suffix='v241-localqa' if i<3 else 'v242-20261101'
 items.append({'family':name,'slot':i,'rel':f'images/{name}-{suffix}/{i:02d}.jpg'})
assert len(items)==55
# Load source-published path exact copies from GitHub checkout.
for d in items:
 p=ROOT/'public'/d['rel']
 d['local_exists']=p.is_file()
 if d['local_exists']:
  dest=OUT/'immutable-repo-public'/d['rel'];dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(p,dest);d['repo_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 else:d['repo_sha256']=''
def fetch(d):
 url=BASE+d['rel']
 try:
  r=requests.get(url,timeout=(10,30),headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/*'});r.raise_for_status()
  if len(r.content)>5_000_000:raise ValueError('large response')
  with Image.open(BytesIO(r.content)) as im:
   im.load();format=im.format;size=im.size
  if format!='JPEG':raise ValueError('not JPEG')
  target=OUT/'immutable-http-public'/d['rel'];target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(r.content)
  return {**d,'url':r.url,'http_status':r.status_code,'http_sha256':hashlib.sha256(r.content).hexdigest(),'same_as_repo':d['repo_sha256']==hashlib.sha256(r.content).hexdigest(),'width':size[0],'height':size[1],'status':'PUBLIC_ACCESSIBLE_QA_PENDING' if size==(1080,1080) else 'PUBLIC_VISUAL_REVISION','reason':'Downloaded, not equivalent to language/brand QA'}
 except Exception as e:
  return {**d,'url':url,'http_status':0,'http_sha256':'','same_as_repo':False,'width':0,'height':0,'status':'PUBLIC_SOURCE_UNVERIFIED','reason':str(e)[:150]}
rows=[]
with ThreadPoolExecutor(max_workers=8) as pool:
 for f in as_completed([pool.submit(fetch,d) for d in items]):rows.append(f.result())
rows.sort(key=lambda x:(x['family'],x['slot']))
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
try:font=ImageFont.truetype(F,17)
except:font=ImageFont.load_default()
for family in sorted(set(d['family'] for d in rows)):
 members=sorted([d for d in rows if d['family']==family],key=lambda x:x['slot'])
 sheet=Image.new('RGB',(1130,305),(249,247,241));dr=ImageDraw.Draw(sheet)
 dr.text((25,12),family,font=font,fill=(24,50,40))
 for i,d in enumerate(members):
  p=OUT/'immutable-http-public'/d['rel']
  if not p.is_file():p=ROOT/'public'/d['rel']
  if p.is_file():
   with Image.open(p) as im:img=ImageOps.contain(im.convert('RGB'),(210,210))
   sheet.paste(img,(10+224*i,37))
  dr.text((10+i*224,255),f'{d["slot"]:02d} {d["status"][:20]}',font=font,fill=(34,55,44))
 out=OUT/'public-contact-sheets'/f'{family}.jpg';out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out,'JPEG',quality=88,optimize=True)
with (OUT/'public_55_candidate_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
 cols=['family','slot','rel','url','http_status','local_exists','repo_sha256','http_sha256','same_as_repo','width','height','status','reason']
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
summary={'version':'2.4.20','candidate_public_paths':len(rows),'candidate_families':11,'http_downloaded':sum(x['http_status']==200 for x in rows),'sha_matches_live_repo':sum(x['same_as_repo'] for x in rows),'missing_http':sum(x['http_status']!=200 for x in rows),'language_qa_pass':0,'language_qa_pending':55,'new_en_public_jpg':0,'originals_modified':0,'note':'55 paths are a candidate mapping reconstructed from 11 preexisting public five-frame families. Exact historical 55 URL list remains unproven; downloadable does not mean QA passed.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
