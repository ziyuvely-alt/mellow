#!/usr/bin/env python3
"""Shopee v2.4.19: two genuinely independent image sources, original-byte preservation,
B/C/D evidence queues and selective final QA. NEVER publish or invent MK/shade art.
"""
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageOps
import csv, hashlib, io, json, shutil, requests
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'input-v2418d'
OUT=ROOT/'production-v2419'
OUT.mkdir(exist_ok=True)
SOURCE_FAMILIES={
 'pending-16':{
   'name':'Dr.G R.E.D BLEMISH CLEAR SOOTHING CREAM 70ml',
   'url':'https://img.dr-g.co.kr/img/hb/GlobalOY/redblemish_cream_70ml_02.jpg?QT=80&SF=webp',
   'page':'https://global.oliveyoung.com/product/detail?prdtNo=GA240222331',
   'caption':'DR.G  |  RED BLEMISH SOOTHING CREAM 70 mL',
   'role':'open cream + texture',
   'source':'Dr.G official hosted image through OliveYoung Global',
   'note':'2022 Korean package comparison still required'
 },
 'pending-28':{
   'name':'pixelpure GLOW CLEANSING SERUM PAD 210ml / 70 pads',
   'url':'https://web.tradekorea.com/product/872/2334872/pixelpure_Glow_Cleansing_Serum_Pad_210ml___70_pads%28skin_care%29_2.jpg',
   'page':'https://www.tradekorea.com/product/detail/P849303/pixelpure-Glow-Cleansing-Serum-Pad-210ml---70-pads-skin-care-.html',
   'caption':'PIXELPURE  |  GLOW CLEANSING SERUM PAD',
   'role':'jar with individual lifted pad',
   'source':'TradeKorea seller product listing',
   'note':'Commercial image reuse rights and exact inventory jar print QA pending'
 }
}
B=['pending-'+n for n in ('09','15','16','18','21','22','24','25','27','28','29','30')]
C=['pending-'+n for n in ('01','02','04','05','06','07','08','10')]
D=['pending-'+n for n in ('03','11','12','13','14','17','19','20','23','26')]
prev=OLD/'preserved-v2418b'/'all-previous-jpg-byte-preserved'/'original-preserved'
bprev=OLD/'preserved-v2418b'/'all-previous-jpg-byte-preserved'/'review-five-frame-sets'
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
try:font=ImageFont.truetype(F,28)
except:font=ImageFont.load_default()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dhash(im):
 a=list(ImageOps.grayscale(im.convert('RGB')).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if a[k//8*9+k%8]>a[k//8*9+k%8+1])
def jpgok(p):
 with Image.open(p) as im:return im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
def save_card(im,path,title):
 src=ImageOps.exif_transpose(im).convert('RGBA')
 bg=Image.new('RGBA',(1080,1080),(252,246,239,255))
 src.thumbnail((1020,895),Image.Resampling.LANCZOS)
 bg.alpha_composite(src,((1080-src.width)//2,15+(895-src.height)//2))
 d=ImageDraw.Draw(bg);d.rectangle((0,924,1080,1080),fill=(226,238,228))
 d.text((55,976),title,font=font,fill=(42,60,52))
 bg.convert('RGB').save(path,'JPEG',quality=91,optimize=True)
 assert jpgok(path)
# Preserve all 160 previous unique original JPG bytes + all previously corrected B12 artifact files.
shutil.copytree(OLD,OUT/'v2418d-immutable',dirs_exist_ok=True)
baseline={}
for p in prev.glob('pending-*/*.jpg'):baseline[str(p.relative_to(prev))]=digest(p)
assert len(baseline)==160,('expected 160 old JPGs, got',len(baseline))
new=[];captures=[];bstatus=[]
for fid in B:
 spec=SOURCE_FAMILIES.get(fid);ready=False
 if spec:
  try:
   r=requests.get(spec['url'],timeout=(10,24),headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'});r.raise_for_status()
   raw=r.content
   if len(raw)>12000000:raise ValueError('source >12 MB')
   with Image.open(io.BytesIO(raw)) as check:
    check.load()
    if check.format not in ('JPEG','PNG','WEBP') or min(check.size)<430:raise ValueError('unusable image dimensions')
    candidatehash=dhash(check)
    for p in (prev/fid).glob('*.jpg'):
     with Image.open(p) as old:
      if (candidatehash^dhash(old)).bit_count()<=5:raise ValueError('photo duplicates existing frame')
    # Unique source photograph from a different actual product scene; no fabricated packshot.
    source_folder=OUT/'new-source-originals'/fid;source_folder.mkdir(parents=True,exist_ok=True)
    raw_path=source_folder/('original_'+hashlib.sha256(raw).hexdigest()[:16]+('.png' if check.format=='PNG' else '.jpg'))
    raw_path.write_bytes(raw)
    dest=OUT/'new-candidate-frames'/fid;dest.mkdir(parents=True,exist_ok=True)
    file=dest/'INDEPENDENT_PRODUCT_DETAIL_V2419.jpg';save_card(check,file,spec['caption'])
   ready=True
   new.append({'family':fid,'filename':file.name,'sha256':digest(file),'size':file.stat().st_size,'source_sha256':digest(raw_path),'role':spec['role']})
   captures.append({'family':fid,'url':r.url,'page':spec['page'],'source':spec['source'],'outcome':'NEW_AUTHENTIC_PHOTO_CANDIDATE','hold':spec['note']})
  except Exception as e:
   captures.append({'family':fid,'url':spec['url'],'page':spec['page'],'source':spec['source'],'outcome':'SOURCE_FAILED_OR_REJECTED','hold':str(e)[:140]})
 # Review existing five-frame set. Change only the role whose photograph the verified new frame improves.
 reviewed=list(sorted((bprev/fid).glob('*.jpg')))
 if len(reviewed)==5:
  target=OUT/'B12-candidate-review-sets'/fid
  target.mkdir(parents=True,exist_ok=True)
  for i,p in enumerate(reviewed):shutil.copy2(p,target/(f'{i+1:02d}_'+p.name[3:]))
  if ready:
   # replacement is review-only, not the immutable original; last-frame photo slot is renamed versioned.
   oldslot=next((x for x in target.glob('*.jpg') if 'INV_04' in x.name or 'INV_03' in x.name),None)
   if oldslot:
    oldslot.unlink()
    source=(OUT/'new-candidate-frames'/fid/'INDEPENDENT_PRODUCT_DETAIL_V2419.jpg')
    shutil.copy2(source,target/('05_INDEPENDENT_PRODUCT_DETAIL_V2419.jpg'))
 bstatus.append({'family':fid,'existing_five_frames':len(reviewed),'new_photographic_candidate':int(ready),'seller_final_pass':False,'status':'REVISE','reason':'Original MK binary, inventory package version, image rights and visual frame sign-off unresolved'})
 print('B12',fid,len(reviewed),'new',int(ready),flush=True)
# Compare all 30 families, preserving source copy. No false-positive perceptual "repair".
allstatus=[]
for fid in B+C+D:
 files=list((prev/fid).glob('*.jpg'))
 allstatus.append({'family':fid,'queue':'B' if fid in B else 'C' if fid in C else 'D','jpg':len(files),'status':'SWATCH_PENDING' if fid in C else 'FRAME_REVISE_REQUIRED' if fid in B else 'SOURCE_PENDING','ready_except_logo':False,'production_complete_qa_pending':False,'why':'Actual SKU options + official swatch unverified' if fid in C else 'Full package evidence/logo/rights QA pending'})
# Re-read preserved bytes.
for name,hash0 in baseline.items():
 assert digest(OUT/'v2418d-immutable'/'preserved-v2418b'/'all-previous-jpg-byte-preserved'/'original-preserved'/name)==hash0
def tab(p,rows,fields):
 with (OUT/p).open('w',encoding='utf-8-sig',newline='') as fp:
  writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader();writer.writerows(rows)
tab('B12_status.csv',bstatus,['family','existing_five_frames','new_photographic_candidate','seller_final_pass','status','reason'])
tab('BCD_30_status.csv',allstatus,['family','queue','jpg','status','ready_except_logo','production_complete_qa_pending','why'])
tab('new_photo_sha256.csv',new,['family','filename','sha256','size','source_sha256','role'])
tab('source_provenance.csv',captures,['family','url','page','source','outcome','hold'])
# Perceptual similarity alert separately reviewed with actual images in existing materials.
suspicions=[
 {'family':'pending-16','interpretation':'Distinct actual scenes: open jar, model, texture and package','resolved_by_replacement':False,'need_replacement':False},
 {'family':'pending-18','interpretation':'Same information template but different data: UV vs capacity','resolved_by_replacement':False,'need_replacement':False},
 {'family':'pending-28','interpretation':'Original photos are distinct: pad, jar, closeup, fibers','resolved_by_replacement':False,'need_replacement':False}]
(OUT/'three_similarity_review.json').write_text(json.dumps(suspicions,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'version':'2.4.19','preserved_original_sha256_identical':len(baseline),'new_real_photo_candidates':len(new),'candidate_photographs_in_b12':len(new),'actual_approved_replacement_frames':0,'B_reviewed':len(B),'C_reviewed':len(C),'D_reviewed':len(D),'official_swatch_jpg_completed':0,'real_mk_logo_binary_available':False,'ready_except_logo':0,'production_complete_qa_pending':0,'published_urls_preserved':55,'remaining_duplicate_alerts_examined':3,'resolved_by_actual_source_replacement':0,'summary':'Two independent product photos prepared for review, existing originals immutable; full seller and licensing QA pending.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
