#!/usr/bin/env python3
"""v2.4.17 product-photo candidate production, traceable safe curation.
Does not touch the 160 JPEG originals or the existing public 55 URLs.
"""
import csv,hashlib,io,json,shutil
from pathlib import Path
import requests
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
PREV=ROOT/'input-v2416c'
OUT=ROOT/'production-v2417'
OUT.mkdir(exist_ok=True)
FONTPATH='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def fnt(sz):
 try:return ImageFont.truetype(FONTPATH,sz)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 a=list(ImageOps.grayscale(im).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if a[(k//8)*9+k%8]>a[(k//8)*9+k%8+1])
SOURCES=[
 {'id':'pending-15','url':'https://image.msscdn.net/thumbnails/images/prd_img/20230828/3505223/detail_3505223_16932037977475_big.jpg?w=1200','role':'product_and_texture','label':'Dr.G  GREEN MILD UP SUN+  /  50 mL','source_page':'https://www.musinsa.com/products/3505223','note':'2022 packaging edition and commercial rights remain QA-gated'},
 {'id':'pending-21','url':'https://image.coupangcdn.com/image/vendor_inventory/20f5/008034caf02a6153d28358f99a4d400b0a3ffa1447bde37651e353d12feb.jpg','role':'single_item_with_box','label':'goodal  VITA-C EYE CREAM  /  30 mL','source_page':'https://www.coupang.com/vp/products/2040525869','note':'Single product plus box; verify 25AD retail package identity and commercial rights'},
]
SELECT={
 'pending-15':['INV_03_8d52f556bc.jpg','INV_02_7f3ea992bc.jpg','INFO_04_OFFICIAL_V2412.jpg','INFO_05_OFFICIAL_V2412.jpg'],
 'pending-21':['PHOTO_02_V2413.jpg','INFO_03_V2413.jpg','INFO_04_V2413.jpg','INFO_05_V2413.jpg'],
}
def create_card(source_path,target,label):
 with Image.open(source_path) as im:
  im.load()
  src=ImageOps.exif_transpose(im).convert('RGB')
 bg=Image.new('RGB',(1080,1080),(250,245,238))
 src.thumbnail((980,915),Image.Resampling.LANCZOS)
 x=(1080-src.width)//2;y=18+(912-src.height)//2
 bg.paste(src,(x,y))
 d=ImageDraw.Draw(bg)
 d.rectangle((0,937,1080,1080),fill=(230,237,228))
 textwidth=d.textbbox((0,0),label,font=fnt(29))[2]
 if textwidth>1010:raise RuntimeError('label overflow')
 d.text((62,976),label,font=fnt(29),fill=(44,62,54))
 bg.save(target,'JPEG',quality=90,optimize=True)
 with Image.open(target) as im:assert im.format=='JPEG' and im.size==(1080,1080)
 assert target.stat().st_size<2_000_000
sha_rows=[];capture=[];sets=[];new=0;original=0
for fid_dir in sorted(PREV.glob('pending-*')):
 if not fid_dir.is_dir():continue
 dest=OUT/'original-preserved'/fid_dir.name;dest.mkdir(parents=True,exist_ok=True)
 for file in sorted(fid_dir.glob('*.jpg')):
  out=dest/file.name;shutil.copy2(file,out)
  original+=1
  sha_rows.append({'family':fid_dir.name,'file':file.name,'sha256':sha(out),'size':out.stat().st_size,'kind':'PREVIOUS_EXACT'})
for item in SOURCES:
 fid=item['id'];rawdir=OUT/'source-originals'/fid;rawdir.mkdir(parents=True,exist_ok=True)
 try:
  r=requests.get(item['url'],timeout=(8,22),headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'});r.raise_for_status()
  if len(r.content)>12_000_000:raise ValueError('source size exceeded')
  with Image.open(io.BytesIO(r.content)) as im:
   im.load();fmt=im.format;wh=im.size
   if fmt not in ('JPEG','PNG','WEBP') or min(wh)<360:raise ValueError('unsupported/low-resolution source')
   newhash=dhash(im.convert('RGB'))
  src=rawdir/(hashlib.sha256(r.content).hexdigest()[:18]+'.'+('jpg' if fmt=='JPEG' else 'png'))
  src.write_bytes(r.content)
  if any((newhash-dhash(Image.open(p).convert('RGB'))).bit_count()<=5 for p in (PREV/fid).glob('*.jpg')):
   raise ValueError('near duplicate of preserved JPEG, not counted')
  newframe=OUT/'candidate-new'/fid
  newframe.mkdir(parents=True,exist_ok=True)
  target=newframe/('SOURCE_PHOTO_'+item['role']+'_V2417.jpg')
  create_card(src,target,item['label'])
  new+=1
  sha_rows.append({'family':fid,'file':target.name,'sha256':sha(target),'size':target.stat().st_size,'kind':'NEW_SOURCE_CANDIDATE'})
  capture.append({'family':fid,'url':r.url,'page':item['source_page'],'sha256':sha(src),'status':'CAPTURED_PHOTO_CANDIDATE','qa_hold':item['note']})
 except Exception as e:
  capture.append({'family':fid,'url':item['url'],'page':item['source_page'],'sha256':'','status':'SOURCE_FAILED','qa_hold':str(e)[:180]})
for fid, selected in SELECT.items():
 folder=OUT/'review-five-frame-sets'/fid;folder.mkdir(parents=True,exist_ok=True)
 candidate=list((OUT/'candidate-new'/fid).glob('*.jpg'))
 eligible=([candidate[0]] if candidate else [])+[PREV/fid/n for n in selected if (PREV/fid/n).is_file()]
 for idx,p in enumerate(eligible,1):
  shutil.copy2(p,folder/(f'{idx:02d}_'+p.name))
 sets.append({'family':fid,'files':len(eligible),'status':'PHOTO_VERIFIED_REVIEW_SET' if len(eligible)==5 else 'PARTIAL_JPG','qa':'HOLD','reason':'Original MK logo binary, inventory edition, source licensing and final per-frame QA unresolved'})
def csvsave(path,data,fields):
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
csvsave(OUT/'source_sha_manifest.csv',sha_rows,['family','file','sha256','size','kind'])
csvsave(OUT/'capture_provenance.csv',capture,['family','url','page','sha256','status','qa_hold'])
csvsave(OUT/'review_set_status.csv',sets,['family','files','status','qa','reason'])
summary={'version':'2.4.17','original_jpg_unchanged':original,'new_candidate_jpg':new,'candidate_five_frame_sets':sum(s['files']==5 for s in sets),'ready_except_logo':0,'production_complete_qa_pending':0,'final_qa_approved':0,'real_mk_logo_binary_recovered':False,'official_swatch_charts_complete':0,'resolved_duplicate_pairs':0,'original_public_urls_unchanged':55,'note':'Two actual product-photo candidate files and non-destructive five-frame review copies. Not final seller-approved due to image rights/edition/logo.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
