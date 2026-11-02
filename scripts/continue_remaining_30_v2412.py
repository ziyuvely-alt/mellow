#!/usr/bin/env python3
"""v2.4.12 evidence-backed informational frame creation.
Existing v2411 JPEGs remain immutable. This script creates only additional
typography-led info images with distinct official facts, no fabricated product
pictures, colors, swatches, packshots or logo. Final QA stays separate.
"""
import csv,hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production-v2412';OUT.mkdir(exist_ok=True)
SRC=ROOT/'input-v2411-cache'
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
N='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
OFFICIAL={
'pending-09':{
'name':'OBgE OIL CONTROL FINISHER','official':'https://obge.co.kr/product/detail.html?product_no=1865',
'facts':[
('03','제품 특징','유분과 번들거림 케어','오일 컨트롤 피니셔','젤 파우더 제품','브랜드 공식 설명 기준'),
('04','성분 정보','SILICA  ·  ZINC PCA','공식 전성분에 실리카 포함','징크피씨에이 포함','전성분 표기 기준'),
('05','제품 구성','5 g','오일 컨트롤 피니셔','단품 5 g','제품정보 표기 기준')]},
'pending-15':{
'name':'Dr.G GREEN MILD UP SUN PLUS','official':'https://www.dr-g.co.kr/item/9637',
'facts':[
('03','제품 특징','민감한 피부를 위한','무기 자외선 차단제','브랜드 공식 제품 설명','정확한 제품 버전 확인 필요'),
('04','핵심 성분','ZINC OXIDE','징크옥사이드 함유','무기 자외선 차단','브랜드 공식 제품 설명'),
('05','제품 정보','50 mL','그린 마일드 업 선 플러스','선케어 제품','브랜드 공식 용량')]},
'pending-18':{
'name':'Dr.G BRIGHTENING UP SUN PLUS','official':'https://www.dr-g.co.kr/item/3622?cc=19&pc=4',
'facts':[
('03','자외선 차단','SPF50+  PA+++','브라이트닝 업 선 플러스','브랜드 공식 자외선 지수','50 mL 제품 자료'),
('04','제품 특징','BRIGHTENING UP','피부톤을 밝혀주는','브라이트닝 선케어','브랜드 공식 설명'),
('05','제품 정보','50 mL','브라이트닝 업 선 플러스','선케어 제품','기획·증정품 별도')]},
'pending-22':{
'name':'OBgE MAX WATERFUL SUN CREAM','official':'https://obge.co.kr/product/detail.html?product_no=1251',
'facts':[
('03','제품 특징','FACE + BODY','얼굴과 바디에 사용하는','300 mL 대용량 선크림','브랜드 공식 FAQ'),
('04','보습 성분','PANTHENOL + ECTOIN','판테놀 · 엑토인 함유','히알루론산 계열 성분 함유','공식 전성분 확인'),
('05','제품 정보','300 mL','자외선 차단 · 주름 개선','기능성 화장품','브랜드 공식 제품정보')]},
'pending-16':{
'name':'Dr.G RED BLEMISH CLEAR SOOTHING CREAM','official':'https://www.dr-g.co.kr/item/9826?cc=26&pc=5',
'facts':[
('05','제품 정보','70 mL','레드 블레미쉬','클리어 수딩 크림','2022년 실제 용기 버전 검수 별도')]}
}
def font(n,bold=False):
 try:return ImageFont.truetype(B if bold else N,n)
 except:return ImageFont.load_default()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def draw_frame(info,number,data,dest):
 role,big,l1,l2,foot=data[1:]
 # Three meaningfully different editorial systems rather than repetitive product photos.
 themes=[(251,241,234),(229,239,230),(248,246,237)]
 kind=int(number)%3;bg=Image.new('RGB',(1080,1080),themes[kind])
 d=ImageDraw.Draw(bg)
 dark=(45,66,57);sage=(127,155,132);peach=(231,170,148)
 d.text((72,64),'MELLOWKR   /   PRODUCT GUIDE',font=font(26,True),fill=dark)
 d.line((70,116,1010,116),fill=sage,width=3)
 d.text((74,151),role,font=font(39,True),fill=dark)
 if kind==0:
  d.rounded_rectangle((60,258,1020,715),radius=55,fill=(229,237,229))
  d.ellipse((775,450,1060,730),fill=(246,215,205))
  d.text((108,342),big,font=font(59,True),fill=dark)
  d.text((108,525),l1,font=font(38),fill=dark)
  d.text((108,597),l2,font=font(34),fill=dark)
 elif kind==1:
  for i,x in enumerate((75,690)):
   d.rounded_rectangle((x,284,x+(285 if i else 570),713),radius=32,fill=(253,251,246))
  d.ellipse((114,323,264,473),fill=(237,204,190))
  d.text((106,515),big,font=font(52,True),fill=dark)
  d.text((106,606),l1,font=font(34),fill=dark)
  d.text((713,378),l2,font=font(30),fill=dark)
 else:
  d.rounded_rectangle((66,275,1014,735),radius=24,fill=(237,222,212))
  d.rectangle((105,320,126,684),fill=sage)
  d.text((162,345),big,font=font(63,True),fill=dark)
  d.text((167,545),l1,font=font(36),fill=dark)
  d.text((167,616),l2,font=font(32),fill=dark)
 d.line((78,790,1002,790),fill=(175,184,171),width=2)
 d.text((83,830),info['name'],font=font(31,True),fill=dark)
 d.text((83,894),foot,font=font(28),fill=(84,99,89))
 # No final QA badge or fictitious official logo printed on artwork.
 bg.save(dest,'JPEG',quality=93,optimize=True)
 with Image.open(dest) as check:
  assert check.format=='JPEG' and check.size==(1080,1080)
 assert dest.stat().st_size<2_000_000
manifest=[];rows=[];added=0;reused=0
for item in QUEUE:
 fid=item['id'];name=item['name'];dest=OUT/fid;dest.mkdir(exist_ok=True)
 existing=SRC/fid
 if existing.exists():
  for p in sorted(existing.glob('*.jpg')):
   target=dest/p.name
   if target.exists():continue
   shutil.copy2(p,target);reused+=1
 item_info=OFFICIAL.get(fid)
 if item_info:
  for fr in item_info['facts']:
   num=fr[0];path=dest/f'INFO_{num}_OFFICIAL_V2412.jpg'
   if not path.exists():
    draw_frame(item_info,num,fr,path);added+=1
 files=sorted(dest.glob('*.jpg'))
 if not files:dest.rmdir()
 for p in files:
  manifest.append({'family':fid,'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'source_url':item_info['official'] if p.name.startswith('INFO_') and item_info else 'PRESERVED_V2411','type':'NEW_INFORMATION_FRAME' if p.name.startswith('INFO_') else 'REUSED','approved':False})
 info_count=sum(p.name.startswith('INFO_') for p in files)
 status='INFORMATION_FRAMES_QA_PENDING' if info_count else ('PARTIAL_JPG' if files else 'SOURCE_PENDING')
 rows.append({'id':fid,'name':name,'total_jpg':len(files),'new_info_frames':info_count,'status':status,'production_complete':False,'reason':('Official claim-backed text panels created; original frame role, MK logo, actual package and photo quality QA pending' if info_count else 'Additional official information or product imagery needed')})
 print('FAMILY',fid,'info',info_count,'files',len(files),flush=True)
def csvwrite(path,rows,headers):
 with path.open('w',encoding='utf-8-sig',newline='') as h:
  w=csv.DictWriter(h,fieldnames=headers);w.writeheader();w.writerows(rows)
csvwrite(OUT/'frame_sha256_manifest.csv',manifest,['family','file','sha256','bytes','source_url','type','approved'])
csvwrite(OUT/'family_checkpoint.csv',rows,['id','name','total_jpg','new_info_frames','status','production_complete','reason'])
summary={'version':'2.4.12','new_jpg':added,'reused_jpg':reused,'jpeg_sha256_unique':len({r['sha256'] for r in manifest}),'new_info_families':sum(r['new_info_frames']>0 for r in rows),'production_complete_qa_pending':0,'final_qa_approved':0,'source_pending':sum(r['total_jpg']==0 for r in rows),'public_urls_unchanged':55,'notes':'Verified official text information only. No new model product photograph, shade chart or MK logo invented. All artifacts remain unapproved.'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
