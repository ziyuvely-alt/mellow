#!/usr/bin/env python3
"""v2.4.14: preserve v2413 imagery, add only independently informative grounded frames.
Do not pretend five file names yield a complete merchant-ready product set.
"""
import csv,hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'input-v2414'
OUT=ROOT/'production-v2414b'; OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf8'))
N='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
# Each role is tied to the precise listed product, not a generic comparable.
# Tuple: role, headline, line 1, line 2, reference URL
FACT={
 'pending-01':[
  ('SUN','SPF50+ / PA+++','미샤 커버 래스팅','자외선차단 쿠션 15 g','https://www.glowpick.com/products/105231'),
  ('FEATURE','SEMI-MATTE','밀착 커버 · 지속력','보송한 세미매트 피니시','https://www.glowpick.com/products/105231')],
 'pending-02':[
  ('SUN','SPF50+ / PA+++','미샤 매직 쿠션 모이스트 업','자외선 차단 기능','https://www.friensi.com/ko/products/missha-magic-cushion-moist-up-spf50pa-15g'),
  ('HOWTO','PRESS + PAT','퍼프로 적당량을 덜어','두드리듯 펴 바르기','https://www.friensi.com/ko/products/missha-magic-cushion-moist-up-spf50pa-15g')],
 'pending-05':[
  ('HOWTO','LIGHT LAYER','적당량을 취한 후 얇게 펴 바르고','가볍게 두드려 마무리','https://www.ssg.com/item/itemView.ssg?itemId=1000062249759')],
 'pending-08':[
  ('PRODUCT','4 g','페리페라 무드 글로이 틴트','실제 판매 옵션 01~20호 한정','https://clubclio.co.kr/shop/goodsView/0000003551')],
 'pending-19':[
  ('FUNCTION','DUAL FUNCTION','미백 · 주름개선 기능성','50ml 청귤 크림 알파 25AD','https://m.shilladfs.com/estore/kr/ko/p/5770103')],
}

HOLD={'pending-26':'145ml versus 150ml package mismatch; never create'}
def font(n,bold=False):
 try:return ImageFont.truetype(B if bold else N,n)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writejpeg(path,title,info,variant):
 role,head,line1,line2,_=info
 palette=[((249,237,231),(225,235,226)),((232,241,231),(252,247,239)),((249,246,236),(238,221,210))]
 bg1,bg2=palette[variant%3]
 im=Image.new('RGB',(1080,1080),bg1)
 d=ImageDraw.Draw(im);dark=(45,67,57)
 d.text((72,62),'MELLOWKR / PRODUCT DETAILS',font=font(27,True),fill=dark)
 d.line((70,121,1010,121),fill=(154,181,159),width=3)
 d.text((78,166),role,font=font(36,True),fill=dark)
 d.rounded_rectangle((67,279,1012,742),radius=32,fill=bg2)
 # Only official name/pack metadata facts, no invented product visuals or swatches.
 for a,y,sz in [(head,330,59),(line1,510,37),(line2,605,32)]:
  f=font(sz,True if y==330 else False)
  if d.textbbox((0,0),a,font=f)[2]>840:
   raise ValueError('TEXT_TOO_WIDE:'+a)
  d.text((126,y),a,font=f,fill=dark)
 d.line((76,800,1006,800),fill=(153,176,155),width=2)
 d.text((78,845),title,font=font(29,True),fill=dark) if d.textbbox((0,0),title,font=font(29,True))[2]<900 else None
 d.text((78,929),'Verified item information / Final QA pending',font=font(24),fill=(77,96,85))
 im.save(path,'JPEG',quality=91,optimize=True)
 with Image.open(path) as check: assert check.format=='JPEG' and check.size==(1080,1080)
 assert path.stat().st_size<2_000_000
def dhash(p):
 with Image.open(p) as src:
  data=list(ImageOps.grayscale(src).resize((9,8)).getdata())
 return sum(1<<j for j in range(64) if data[(j//8)*9+j%8] > data[(j//8)*9+j%8+1])
frames=[];rows=[];visual=[];new=0;reused=0
for item in QUEUE:
 fid=item['id'];dest=OUT/fid;dest.mkdir(exist_ok=True)
 old=PARENT/fid
 if old.is_dir():
  for p in sorted(old.glob('*.jpg')):
   target=dest/p.name
   if not target.exists():
    shutil.copy2(p,target);reused+=1
 # New independent information roles do not overwrite the source photos.
 for idx,info in enumerate(FACT.get(fid,[]),1):
  role,head,l1,l2,src=info
  path=dest/f'INFO_{role.replace(" ","_")}_{idx:02d}_V2414B.jpg'
  if path.exists():continue
  try:
   writejpeg(path,item['name'],info,idx);new+=1
  except Exception as e:
   if path.exists():path.unlink()
   print('FRAME_HOLD',fid,role,str(e),flush=True)
 files=sorted(dest.glob('*.jpg'))
 if not files: dest.rmdir()
 dh=[]
 for p in files:
  h=dhash(p)
  for oldp,oldh in dh:
   if (h^oldh).bit_count()<=4:
    visual.append({'family':fid,'a':oldp.name,'b':p.name,'dhash_distance':(h^oldh).bit_count()})
  dh.append((p,h))
  with Image.open(p) as im:
   assert im.format=='JPEG' and im.size==(1080,1080) and p.stat().st_size<2_000_000
  frames.append({'family':fid,'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'type':'NEW_INFORMATION' if p.name.endswith('_V2414B.jpg') else 'PRESERVED','source':next((x[4] for x in FACT.get(fid,[]) if p.name.startswith('INFO_'+x[0].replace(' ','_'))),'PRESERVED_V2413')})
 cnt=len(files)
 rows.append({'id':fid,'name':item['name'],'total_jpg':cnt,'new_frames':sum(p.name.endswith('_V2414B.jpg') for p in files),'state':'SOURCE_PENDING' if not cnt else 'FIVE_FRAME_DRAFT' if cnt>=5 else 'PARTIAL_JPG','production_complete':False,'official_swatch_complete':False,'logo_original_applied':False,'reason':HOLD.get(fid,'source photo, pack/option, informational diversity and original logo remain final QA gates')})
 print('FAMILY',fid,cnt,flush=True)
def save_csv(path,records,fields):
 with path.open('w',newline='',encoding='utf-8-sig') as h:
  w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(records)
save_csv(OUT/'family_checkpoint.csv',rows,['id','name','total_jpg','new_frames','state','production_complete','official_swatch_complete','logo_original_applied','reason'])
save_csv(OUT/'frame_sha256_manifest.csv',frames,['family','file','sha256','bytes','type','source'])
save_csv(OUT/'visual_duplicate_candidates.csv',visual,['family','a','b','dhash_distance'])
summary={'version':'2.4.14-b','reused_jpg':reused,'new_jpg':new,'archive_jpg':len(frames),'sha256_unique':len({r['sha256'] for r in frames}),'with_five_or_more':sum(r['total_jpg']>=5 for r in rows),'partial_jpg_families':sum(0<r['total_jpg']<5 for r in rows),'source_pending':sum(r['total_jpg']==0 for r in rows),'duplicate_candidates':len(visual),'production_complete_qa_pending':0,'official_shade_charts_complete':0,'original_logo_applied':0,'public_url_preserved':55}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
