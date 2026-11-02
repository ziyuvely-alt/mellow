#!/usr/bin/env python3
"""v2.4.15: scoped partial-frame creation from verifiable seller photo and documented content.
No synthetic product silhouettes, invented swatches, unverified MK logos, or public release.
"""
import csv,hashlib,io,json,shutil
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'input-v2414b';OUT=ROOT/'production-v2415';OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SOURCES={
 'pending-23':[
 'https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023044705ko.jpg?l=ko',
 'https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023044706ko.jpg?l=ko',
 'https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023044702ko.jpg?l=ko',
 ],
}
PAGES={'pending-23':'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000230447'}
def font(n,bold=False):
 try:return ImageFont.truetype(BOLD if bold else FONT,n)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 a=list(ImageOps.grayscale(im).resize((9,8)).getdata())
 return sum(1<<k for k in range(64) if a[(k//8)*9+(k%8)] > a[(k//8)*9+(k%8)+1])
def keep_previous(family,dir):
 target=OUT/family;target.mkdir(exist_ok=True)
 previous=CACHE/family
 count=0
 if previous.is_dir():
  for file in previous.glob('*.jpg'):
   shutil.copy2(file,target/file.name);count+=1
 return target,count
def jpeg_ok(path):
 try:
  with Image.open(path) as im:
   return im.format=='JPEG' and im.size==(1080,1080) and path.stat().st_size<2_000_000
 except:return False
def info_tint(path):
 # Documented scope only. No fictitious shade samples, unofficial color names or reused photo.
 bg=Image.new('RGB',(1080,1080),(251,242,234));d=ImageDraw.Draw(bg)
 dark=(46,68,59);sage=(220,234,220)
 d.text((76,65),'PERIPERA   /   MOOD GLOWY TINT',font=font(30,True),fill=dark)
 d.line((75,131,1004,131),fill=(143,166,146),width=3)
 d.rounded_rectangle((70,233,1012,769),radius=45,fill=sage)
 d.text((133,310),'4 g',font=font(113,True),fill=dark)
 d.text((140,527),'무드 글로이 틴트',font=font(51,True),fill=dark)
 d.text((140,621),'판매 옵션: 01 ~ 20호',font=font(36),fill=dark)
 d.text((83,848),'실제 발색표는 브랜드 공식 자료 확인 후 별도 제작',font=font(27),fill=dark)
 d.text((83,918),'제품정보 프레임 / 공식 색상표 미확인',font=font(25),fill=(90,98,91))
 bg.save(path,'JPEG',quality=92,optimize=True)
 assert jpeg_ok(path)
def photo_card(original,path):
 with Image.open(original) as im:
  pic=ImageOps.exif_transpose(im).convert('RGBA');pic.load()
 bg=Image.new('RGB',(1080,1080),(246,235,229))
 pic.thumbnail((965,840),Image.Resampling.LANCZOS)
 x=(1080-pic.width)//2;y=42+(840-pic.height)//2
 bg.paste(pic,(x,y),pic)
 d=ImageDraw.Draw(bg)
 d.rectangle((0,897,1080,1080),fill=(229,238,225))
 d.text((76,938),'OBgE  /  PORE ZERO OIL CONTROL SUN',font=font(29,True),fill=(42,64,55))
 d.text((76,1002),'50 mL  ·  Actual retailer product image',font=font(24),fill=(49,70,60))
 bg.save(path,'JPEG',quality=88,optimize=True)
 assert jpeg_ok(path)
frame_rows=[];family_rows=[];sources=[];new=0;reused=0
for q in QUEUE:
 fid=q['id'];folder,n=keep_previous(fid,ROOT);reused+=n
 if fid=='pending-08':
  target=folder/'INFO_SCOPE_05_V2415.jpg'
  if not target.exists():info_tint(target);new+=1
 if fid=='pending-23':
  original_dir=OUT/'source-evidence'/fid;original_dir.mkdir(parents=True,exist_ok=True)
  seen=[]
  for existing in folder.glob('*.jpg'):
   with Image.open(existing) as im:seen.append(dhash(im.convert('RGB')))
  for ix,url in enumerate(SOURCES[fid]):
   try:
    if urlparse(url).scheme!='https':raise ValueError('url must be https')
    response=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'},timeout=(9,18));response.raise_for_status()
    if len(response.content)>12_000_000:raise ValueError('source too large')
    buf=io.BytesIO(response.content)
    with Image.open(buf) as im:
     im.load()
     if im.format not in ('PNG','JPEG','WEBP') or min(im.size)<300:raise ValueError('bad image')
     ph=dhash(im.convert('RGB'))
    raw_sha=hashlib.sha256(response.content).hexdigest()
    orig=original_dir/('source_'+raw_sha[:12]+'.'+('png' if im.format=='PNG' else 'jpg'))
    orig.write_bytes(response.content)
    if any((ph-h).bit_count()<=5 for h in seen):
     sources.append({'family':fid,'url':url,'sha256':raw_sha,'status':'VISUAL_DUPLICATE_SOURCE_HOLD'});continue
    target=folder/'PHOTO_RETAILER_05_V2415.jpg'
    if not target.exists():
     photo_card(orig,target);new+=1
    seen.append(ph)
    sources.append({'family':fid,'url':url,'sha256':raw_sha,'status':'PHOTO_CANDIDATE_CREATED'})
    break
   except Exception as e:sources.append({'family':fid,'url':url,'sha256':'','status':'SOURCE_FAILED:'+str(e)[:70]})
 if fid=='pending-26':
  sources.append({'family':fid,'url':'https://pixelpure.com/product/detail.html?product_no=21','sha256':'','status':'145ML_150ML_PACKAGE_MISMATCH_HOLD'})
 files=sorted(folder.glob('*.jpg'))
 if not files:folder.rmdir()
 for p in files:
  assert jpeg_ok(p)
  frame_rows.append({'id':fid,'filename':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'status':'NEW_QA_PENDING' if p.name.endswith('_V2415.jpg') else 'PRESERVED'})
 family_rows.append({'id':fid,'name':q['name'],'jpg':len(files),'new':sum(p.name.endswith('_V2415.jpg') for p in files),'state':'SOURCE_PENDING' if not files else 'FIVE_FRAME_DRAFT' if len(files)>=5 else 'PARTIAL_JPG','production_complete':False,'original_mk_applied':False,'official_shade_chart':False})
 print('FAMILY',fid,len(files),flush=True)
def save_csv(p,rows,fields):
 with p.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
save_csv(OUT/'frame_sha256_manifest.csv',frame_rows,['id','filename','sha256','bytes','status'])
save_csv(OUT/'family_checkpoint.csv',family_rows,['id','name','jpg','new','state','production_complete','original_mk_applied','official_shade_chart'])
save_csv(OUT/'source_provenance.csv',sources,['family','url','sha256','status'])
summary={'version':'2.4.15','reused_jpg':reused,'new_jpg':new,'unique_file_sha256':len({x['sha256'] for x in frame_rows}),'artifact_jpg':len(frame_rows),'families_with_5plus_jpg':sum(r['jpg']>=5 for r in family_rows),'partial_families':sum(0<r['jpg']<5 for r in family_rows),'missing_families':sum(r['jpg']==0 for r in family_rows),'production_complete_qa_pending':0,'original_logo_binary_recovered':False,'original_logo_applied_families':0,'official_shade_complete':0,'duplicate_pairs_replaced':0,'new_public_urls':0,'existing_public_urls_preserved':55,'note':'Neither repeated photography nor unverified product matches are considered final merchant artwork'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
