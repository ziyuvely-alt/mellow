#!/usr/bin/env python3
"""Make NON-APPROVED visual QA previews using original BBIA source photos.

No synthetic shade swatches or modified products. Only downloaded official actual
image pixels are shown on an editorial background. These files are NOT valid as
final Shopee artwork until real image/procurement/color/weight QA passes.
"""
import concurrent.futures
from collections import Counter
import hashlib
import io
import json
import math
import re
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence'/'bbia-image-review-input.json'
OUT=ROOT/'bbia-image-review-previews'
OUTPUT_SIZE=1080
MAX_BYTES=1_999_999
CREAM='#FCFBF8'; GREEN='#C6D5CB'; PEACH='#F1D0C6'; BROWN='#3D3A38'; MUTED='#74746C'

ENGLISH={
'누디 립 펜슬':'Nudi Lip Pencil','누디 슬림 아이라이너':'Nudi Slim Eyeliner',
'럭키 샤인 틴트':'Lucky Shine Tint','아이&치크 프라이머 밤':'Eye & Cheek Primer Balm',
'애교살 펜슬':'Aegyosal Pencil','오 파우더 팩트':'Oh Powder Pact',
'찰떡 블러쉬':'Chaltteok Blush','라스트 벨벳 틴트':'Last Velvet Tint',
'라스트 오토 젤 아이라이너':'Last Auto Gel Eyeliner',
'라스트 오토 젤 아이라이너 슬림':'Last Auto Gel Eyeliner Slim',
'라스트 윤곽 스틱':'Last Contour Stick','레디 투 웨어 다우니 치크':'Ready to Wear Downy Cheek',
'립 오일 에센스':'Lip Oil Essence','오 글로우 쿠션 본품':'Oh Glow Cushion',
'오 매트 쿠션 리필':'Oh Matte Cushion Refill','오 매트 쿠션 본품':'Oh Matte Cushion',
'오 스테이 컨실러':'Oh Stay Concealer','오버 글레이즈':'Over Glaze',
'오버 글레이즈 스틱':'Over Glaze Stick','글로우 틴트':'Glow Tint',
'네버 다이 마스카라':'Never Die Mascara','네버 다이 마스카라 슬림':'Never Die Mascara Slim',
'네버 다이 아이라이너':'Never Die Eyeliner','라스트 블러쉬':'Last Blush',
'라스트 아이 팔레트':'Last Eye Palette','라스트 아이 프라이머':'Last Eye Primer',
'라스트 오토 아이브로우 펜슬':'Last Auto Eyebrow Pencil',
'라스트 컨투어 펜 아이라이너':'Last Contour Pen Eyeliner',
'라스트 파우더 립스틱':'Last Powder Lipstick',
'라스트 펜 아이라이너':'Last Pen Eyeliner',
'레디 투 웨어 아이 섀도우':'Ready to Wear Eye Shadow',
'레디 투 웨어 아이 팔레트':'Ready to Wear Eye Palette',
'레디 투 웨어 워터 립스틱':'Ready to Wear Water Lipstick',
'로 틴트':'Raw Tint','립 오일 밤':'Lip Oil Balm',
'에센셜 아이 팔레트':'Essential Eye Palette',
'오 글로우 쿠션 리필':'Oh Glow Cushion Refill',
'오 매트 쿠션 퍼프 2P':'Oh Matte Cushion Puff 2P',
'오 쿠션 퍼프 2P':'Oh Cushion Puff 2P',
'오 파우더 팩트 퍼프 2P':'Oh Powder Pact Puff 2P',
'오 퍼펙트 브러쉬':'Oh Perfect Brush',
'오 핑거 퍼프 2P':'Oh Finger Puff 2P',
'찰떡 루비셀 퍼프 1P':'Chaltteok Rubycell Puff 1P'
}

def font_paths():
 import subprocess
 output=subprocess.run(['fc-list',':','family','file'],capture_output=True,text=True).stdout.splitlines()
 fonts=[p.split(':')[0] for p in output if 'NotoSansCJK' in p or 'Noto Sans CJK' in p]
 return fonts[0] if fonts else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT=None

def F(size): return ImageFont.truetype(FONT,size)

def load(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; BBIA-Visual-QA/1.0)','Accept':'image/avif,image/webp,image/jpeg,image/png,image/*'})
 with urllib.request.urlopen(req,timeout=25) as r:
  b=r.read(8_500_000)
  if r.status!=200 or not b.startswith((bytes.fromhex('ffd8ff'),bytes.fromhex('89504e470d0a1a0a'),b'RIFF')):raise ValueError('Not a source photo')
 img=Image.open(io.BytesIO(b));img.seek(0)
 img.load()
 if img.width<180 or img.height<180:raise ValueError('Image too small to faithfully present')
 return img.convert('RGB'),hashlib.sha256(b).hexdigest()

def safe_name(n):return re.sub(r'[^a-zA-Z0-9_-]','_',str(n))

def crop_contain(image, box, inset=12):
 x0,y0,x1,y1=box;w=max(1,x1-x0-2*inset);h=max(1,y1-y0-2*inset)
 im=ImageOps.contain(image,(w,h),Image.Resampling.LANCZOS)
 return im,(x0+(x1-x0-im.width)//2,y0+(y1-y0-im.height)//2)

def lines(draw,text,maxwidth,font):
 out=[];cur=''
 for word in text.split():
  trial=(cur+' '+word).strip()
  if draw.textbbox((0,0),trial,font=font)[2]>maxwidth and cur:out.append(cur);cur=word
  else:cur=trial
 if cur:out.append(cur)
 return out

def bg():
 im=Image.new('RGB',(1080,1080),CREAM);d=ImageDraw.Draw(im)
 d.ellipse((-180,-520,350,790),outline=GREEN,width=12)
 d.ellipse((-260,-380,285,720),outline='#DFE8DC',width=17)
 d.ellipse((-500,660,1400,1340),outline=PEACH,width=56)
 d.ellipse((-330,780,1300,1490),outline='#F6E3DB',width=40)
 d.rounded_rectangle((34,32,1046,1048),radius=20,outline='#E8E9E3',width=2)
 return im

def label(d,text,y,size=46,color=BROWN,maxwidth=910):
 font=F(size); ls=lines(d,text,maxwidth,font)
 for idx,t in enumerate(ls[:3]): d.text((87,y+idx*(size+11)),t,fill=color,font=font)
 return y+min(len(ls),3)*(size+11)

def add_header(im,eng,title,idx,total):
 d=ImageDraw.Draw(im)
 d.text((87,67),'BBIA  /  MELLO W KR PRODUCT VIEW',font=F(20),fill=MUTED)
 y=label(d,title,122,50)
 d.text((87,1037),'SOURCE-PHOTO REVIEW  •  NOT APPROVED FOR SHOPEE UPLOAD',font=F(16),fill='#9B817D')
 d.text((880,1037),f'{idx:02d} / {total:02d}',font=F(16),fill=MUTED)
 return y

def panel_photo(im,img,rect,frame=True):
 d=ImageDraw.Draw(im)
 if frame:d.rounded_rectangle(rect,fill='#FFFFFF',outline='#E8E1DF',width=2,radius=20)
 rendered,pos=crop_contain(img,rect,16)
 im.paste(rendered,pos)

def compose(f,base,details,num,total):
 name=f['family'];short=name.replace('[정규 미니 여부 검증 필요] ','');english=ENGLISH.get(short,short)
 im=bg();d=ImageDraw.Draw(im)
 if num==1:
  y=add_header(im,english,english,1,total)
  d.text((89,min(283,y+10)),short,font=F(27),fill=MUTED)
  panel_photo(im,base,(160,312,914,945)); d.text((90,977),'Choose one verified variant at checkout',font=F(23),fill=BROWN)
 elif num==2:
  add_header(im,english,'In focus',2,total)
  panel_photo(im,details[0] if details else base,(115,255,962,860))
  d.text((88,912),english,font=F(35),fill=BROWN)
  d.text((88,962),'Original product photography from the brand catalog',font=F(20),fill=MUTED)
 elif num==3:
  add_header(im,english,'A closer look',3,total)
  photo=details[1] if len(details)>1 else details[0] if details else base
  panel_photo(im,photo,(100,265,980,920))
  d.text((90,954),'Appearance may vary by selected shade or size',font=F(22),fill=MUTED)
 elif num==4:
  add_header(im,english,'Explore the lineup',4,total)
  panel_photo(im,base,(128,254,650,920))
  d.rounded_rectangle((682,255,988,920),radius=18,fill='#F8F6F3')
  d.text((707,285),'BBIA',font=F(34),fill=BROWN)
  opts=f['options'];d.text((707,353),f'{len(opts)} candidate option(s)',font=F(23),fill=MUTED)
  if len(opts)>1:
   for i,opt in enumerate(opts[:12]):
    xx=f"{opt['number']}  {opt['name_ko']}"; ff=F(20)
    if d.textbbox((0,0),xx,font=ff)[2]>270:ff=F(17)
    d.text((707,415+i*38),xx,font=ff,fill=BROWN)
   if len(opts)>12:d.text((707,878),f'+ {len(opts)-12} more in shade list',font=F(18),fill=MUTED)
  else:d.text((707,415),'Single product family',font=F(22),fill=BROWN)
 elif num==5:
  add_header(im,english,'Select your product',5,total)
  panel_photo(im,details[2] if len(details)>2 else base,(95,270,978,812))
  d.rounded_rectangle((95,843,979,980),radius=20,fill='#FFFFFF',outline='#E7DFDB',width=2)
  d.text((125,872),'Product',font=F(23),fill=MUTED)
  d.text((125,911),english[:38],font=F(27),fill=BROWN)
 elif num==6:
  add_header(im,english,'Shade name index',6,total)
  d.text((88,230),'Based on current sourcing candidates • shade swatches not simulated',font=F(22),fill=MUTED)
  opts=f['options']; count=len(opts); ncols=2 if count<=22 else 3
  cellwidth=(910-16*(ncols-1))//ncols
  nr=math.ceil(count/ncols); step=min(70,650/max(1,nr)); base_y=330
  for i,opt in enumerate(opts):
   col=i//nr;row=i%nr;x=88+col*(cellwidth+16);y=base_y+int(row*step)
   s=f"{opt['number']}  {opt['name_ko']}";fontsize=24 if count<15 else 21 if count<23 else 18
   ff=F(fontsize)
   while fontsize>=15 and d.textbbox((0,0),s,font=ff)[2]>cellwidth-4:
    fontsize-=1;ff=F(fontsize)
   d.text((x,y),s,font=ff,fill=BROWN)
  d.text((88,965),'Verify exact current colors against the manufacturer before listing.',font=F(18),fill=MUTED)
 return im

def make_one(f):
 pid=f['product_id'];url=f['official_photo_url']
 if not url:return {'product_id':pid,'name':f['family'],'status':'NO_HERO_SOURCE','image_count':0}
 try: base,sha=load(url)
 except Exception as e:return {'product_id':pid,'name':f['family'],'status':'SOURCE_FAILED','error':str(e),'image_count':0}
 details=[];used=[]
 for u in f.get('detail_references',[])[:5]:
  if len(details)>=3:break
  try:
   img,hashval=load(u)
   if img.height>6000 or img.width>6000:continue
   details.append(img);used.append({'url':u,'sha256':hashval})
  except Exception:pass
 total=5 if len(f['options'])==1 else 6
 o=OUT/pid;o.mkdir(parents=True,exist_ok=True)
 produced=[]
 for i in range(1,total+1):
  im=compose(f,base,details,i,total)
  p=o/f'{i:02d}.jpg'
  for quality in (91,87,82,76,69):
   im.save(p,'JPEG',quality=quality,optimize=True,subsampling=0)
   if p.stat().st_size<MAX_BYTES:break
  if p.stat().st_size>=MAX_BYTES:raise ValueError('Too large despite compression')
  produced.append({'file':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[im.width,im.height],'status':'VISUAL_REVIEW_REQUIRED'})
 return {'product_id':pid,'name':f['family'],'status':'DRAFT_CREATED_NOT_APPROVED','image_count':len(produced),'official_image_source':url,'official_source_sha256':sha,'used_detail_sources':used,'files':produced}

def main():
 global FONT
 FONT=font_paths()
 print('Using font',FONT,flush=True)
 data=json.loads(SOURCE.read_text(encoding='utf-8'))
 families=data['families'];OUT.mkdir(exist_ok=True)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for res in ex.map(make_one,families):
   results.append(res);print('BUILD',res['product_id'],res['status'],res.get('image_count',0),flush=True)
 out={'kind':'NON_APPROVED_SOURCE_PHOTO_BASED_DRAFTS','family_count':len(families),'family_with_sources':sum(bool(f['official_photo_url']) for f in families),'created_families':sum(x['status']=='DRAFT_CREATED_NOT_APPROVED' for x in results),'created_images':sum(x['image_count'] for x in results),'releases_approved':0,'results':results}
 (OUT/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('DRAFT_IMAGES',out['created_images'],'FAMILIES',out['created_families'],flush=True)
 if out['created_families']<35:raise SystemExit('Too many failed images: review source files')

if __name__=='__main__':main()