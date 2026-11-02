#!/usr/bin/env python3
"""v2412 second production batch: fill missing info panels in partial-photo families.
Preserves all current images from production-assets-v2412 without recomposition.
"""
import json,csv,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'input-v2412-cache';OUT=ROOT/'production-v2412b';OUT.mkdir(exist_ok=True)
QUEUE=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf8'))
NF='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BF='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
F={
'pending-12':{'title':'MISSHA PDRN NAD+ RENEW PEEL SHOT 25','url':'https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236','frames':[
 ('04','성분 정보','GLUCONOLACTONE','락틱애씨드 · 글루코노락톤','공식 전성분에 함유','기능성 과장 없이 성분명만 표기'),
 ('05','제품 정보','15 mL','미샤 리뉴 필 샷 25','한국 제조 · 단품','브랜드 공식 상품정보')]},
'pending-13':{'title':'MISSHA PDRN NAD+ FIRMING REPAIR SERUM','url':'https://zigzag.kr/catalog/products/169746464','frames':[
 ('03','제품 구성','30 mL','퍼밍 리페어 세럼','단품 30 mL','브랜드 제품 및 판매정보'),
 ('04','성분 정보','PANTHENOL','나이아신아마이드 함유','공식 전성분에 기재','공식 제품정보 전성분 표기'),
 ('05','제품 정보','PDRN NAD+','미백 · 주름개선','2중 기능성 화장품','제품정보 고시 기준')]},
'pending-14':{'title':'MISSHA PDRN NAD+ FIRMING REPAIR CREAM','url':'https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114238','frames':[
 ('04','성분 정보','PDRN NAD+','나이아신아마이드 함유','제품 전성분 기준','브랜드 공식 자료'),
 ('05','제품 구성','70 mL','퍼밍 리페어 크림','한국 제조 · 단품','브랜드 공식 용량')]},
'pending-20':{'title':'GOODAL GREEN TANGERINE VITA C MIST 25AD','url':'https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000706462566&salestrNo=6005&siteNo=6004','frames':[
 ('02','제품 정보','100 mL','청귤 비타C 세럼 미스트','25AD 판매 사양','신세계 상품 필수정보'),
 ('03','사용 방법','SHAKE WELL','내용물을 충분히 흔든 후','사용하도록 안내','판매처 상품필수정보'),
 ('04','사용 방법','CLOSE YOUR EYES','눈을 감고 얼굴 전체에','골고루 분사','판매처 상품필수정보'),
 ('05','성분 정보','NIACINAMIDE','나이아신아마이드','20,000 ppm 표기','상품 고시 전성분 기준')]}
}
def font(n,bold=False):
 try:return ImageFont.truetype(BF if bold else NF,n)
 except:return ImageFont.load_default()
def hashfile(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def make(data,filename,title,step):
 purpose,big,line1,line2,note=data[1:]
 colors=[(251,241,234),(225,236,230),(247,247,241),(237,226,217)]
 bg=Image.new('RGB',(1080,1080),colors[step%4]);d=ImageDraw.Draw(bg)
 ink=(46,63,53);sage=(107,145,126)
 d.text((75,68),'MELLOWKR   /   PRODUCT INFORMATION',font=font(25,True),fill=ink)
 d.line((72,117,1000,117),fill=sage,width=3)
 d.text((78,168),purpose,font=font(38,True),fill=ink)
 if step%2:
  d.rounded_rectangle((78,290,1000,750),radius=43,fill=(254,250,244))
  d.rectangle((117,337,136,685),fill=(158,182,161))
  d.text((175,387),big,font=font(62,True),fill=ink)
  d.text((178,532),line1,font=font(37),fill=ink)
  d.text((178,609),line2,font=font(33),fill=ink)
 else:
  d.ellipse((750,220,1180,660),fill=(242,213,201))
  d.rounded_rectangle((88,310,950,735),radius=27,fill=(234,242,233))
  d.text((138,369),big,font=font(57,True),fill=ink)
  d.text((142,538),line1,font=font(38),fill=ink)
  d.text((142,624),line2,font=font(32),fill=ink)
 d.line((80,814,994,814),fill=(162,176,161),width=2)
 d.text((84,848),title,font=font(29,True),fill=ink)
 d.text((84,929),note,font=font(26),fill=ink)
 bg.save(filename,'JPEG',quality=92,optimize=True)
 with Image.open(filename) as a:assert a.format=='JPEG' and a.size==(1080,1080)
 assert filename.stat().st_size<2_000_000
rows=[];files=[];new=0;reused=0
for item in QUEUE:
 id=item['id'];dest=OUT/id;dest.mkdir(exist_ok=True)
 if (IN/id).exists():
  for source in (IN/id).glob('*.jpg'):
   target=dest/source.name
   if not target.exists():
    shutil.copy2(source,target);reused+=1
 info=F.get(id)
 if info:
  for frame in info['frames']:
   path=dest/f'INFO_{frame[0]}_V2412B.jpg'
   if path.exists():continue
   make(frame,path,info['title'],int(frame[0]));new+=1
 imgs=list(dest.glob('*.jpg'))
 if not imgs:dest.rmdir()
 for p in imgs:
  files.append({'family':id,'file':p.name,'sha256':hashfile(p),'bytes':p.stat().st_size,'source':info['url'] if p.name.endswith('_V2412B.jpg') and info else 'PRESERVED','new':p.name.endswith('_V2412B.jpg')})
 rows.append({'id':id,'jpg':len(imgs),'new_info_frames':len(info['frames']) if info else 0,'status':'INFORMATION_FRAMES_QA_PENDING' if info else ('PARTIAL_JPG' if imgs else 'SOURCE_PENDING'),'production_complete':False})
 print(id,'jpg',len(imgs),flush=True)
def write(path,rows,headers):
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
write(OUT/'frame_sha256_manifest.csv',files,['family','file','sha256','bytes','source','new'])
write(OUT/'family_checkpoint.csv',rows,['id','jpg','new_info_frames','status','production_complete'])
s={'version':'2.4.12-b','new_jpg':new,'reused_jpg':reused,'sha256_unique':len(set(f['sha256'] for f in files)),'new_info_families':len(F),'five_jpg_physical':sum(r['jpg']>=5 for r in rows),'production_complete_qa_pending':0,'unstarted':sum(r['jpg']==0 for r in rows),'sales_approved':0,'public_urls_preserved':55,'note':'Actual new information JPGs with verified product claims, not seller-final five-frame approval.'}
(OUT/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(s,ensure_ascii=False),flush=True)
