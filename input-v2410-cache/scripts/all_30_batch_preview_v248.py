#!/usr/bin/env python3
"""Batch review drafts for ALL pending Shopee families, not seller-approved artwork.

Creates five distinct information-layout JPG review frames only where actual source
bytes can be downloaded. Product/source/claims/shades are NOT approved by this script.
Never writes to public/images or changes the existing 55 verified URL mapping.
"""
import csv, hashlib, io, json, re
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
PENDING=json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
OUT=ROOT/'batch-preview-v248'
OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(sz,bold=False):
    p=BOLD if bold else FONT
    try:return ImageFont.truetype(p,sz)
    except:return ImageFont.load_default()
def safe(s):
    return re.sub(r'[^a-zA-Z0-9_-]','_',s)[:72]
def fetch(url):
    p=urlparse(url)
    if p.scheme!='https' or not p.netloc or p.username or p.password:
        raise ValueError('invalid HTTPS source')
    with requests.get(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'},timeout=(10,22),stream=True) as r:
        r.raise_for_status()
        if urlparse(r.url).scheme!='https':raise ValueError('insecure redirect')
        buf=io.BytesIO()
        for x in r.iter_content(65536):
            buf.write(x)
            if buf.tell()>16_000_000:raise ValueError('source too big')
    raw=buf.getvalue()
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if min(im.size)<200:raise ValueError('low-resolution image')
        if im.format not in ['JPEG','PNG','WEBP']:raise ValueError('not an image')
    return raw
def textwrap_pixels(draw,s,f,maxwidth):
    lines=[]
    buf=''
    for c in s:
        candidate=buf+c
        if draw.textbbox((0,0),candidate,font=f)[2]>maxwidth and buf:
            lines.append(buf);buf=c
        else:buf=candidate
    if buf:lines.append(buf)
    return lines
def render(raw,item,folder):
    with Image.open(io.BytesIO(raw)) as im:
        src=im.convert('RGBA')
    peach=(247,226,219); sage=(218,233,224); paper=(251,249,244)
    dark=(48,62,57); muted=(99,109,103)
    descriptions=[
        ('PRODUCT PHOTO','실제 사진 후보 검토'),
        ('PRODUCT DETAILS','제품 외형 및 패키지 확인'),
        ('SKU MATCH','등록 상품명 및 구성 검토'),
        ('SOURCE REVIEW','공식 출처 및 표기 검증 필요'),
        ('QUALITY CHECK','옵션·용량·발색 검증 대기')
    ]
    paths=[]
    for n,(en,ko) in enumerate(descriptions,1):
        bg=([paper,peach,sage, paper,sage][n-1])
        canvas=Image.new('RGB',(1080,1080),bg)
        d=ImageDraw.Draw(canvas)
        d.rounded_rectangle((38,38,1042,1042),radius=24,outline=(204,209,198),width=2)
        d.text((84,83),en,font=font(30,True),fill=dark)
        d.text((84,137),ko,font=font(33),fill=muted)
        # The same authentic source appears only as a crop/scaled view, never fabricated detail.
        if n==1: photo_box=(165,225,915,805)
        elif n==2:photo_box=(100,280,650,875)
        elif n==3:photo_box=(610,295,995,770)
        elif n==4:photo_box=(100,290,555,815)
        else:photo_box=(430,275,985,820)
        x1,y1,x2,y2=photo_box
        target=ImageOps.contain(src,(x2-x1,y2-y1),Image.Resampling.LANCZOS)
        # White matte only for source image without alpha; no fictitious cutouts.
        if target.getbbox():
            dx=x1+((x2-x1)-target.width)//2
            dy=y1+((y2-y1)-target.height)//2
            canvas.paste(target,(dx,dy),target)
        tx= (95 if n in [3,5] else (685 if n in [2,4] else 110))
        ty=(430 if n in [2,3,4,5] else 840)
        fw=325 if n in [2,3,4,5] else 870
        for line in textwrap_pixels(d,item['name'],font(31,True),fw):
            d.text((tx,ty),line,font=font(31,True),fill=dark)
            ty+=47
        d.text((83,982),'SOURCE CANDIDATE  /  NOT APPROVED FOR SALE',font=font(21),fill=(154,79,75))
        dest=folder/f'{n:02d}.jpg'
        quality=90
        while True:
            canvas.save(dest,'JPEG',quality=quality,optimize=True)
            if dest.stat().st_size<2_000_000 or quality<=65:break
            quality-=5
        paths.append(dest)
    return paths
rows=[]
for i,item in enumerate(PENDING,1):
    record={'id':item['id'],'product':item['name'],'source_url':item.get('url',''),'status':'','draft_jpg':0,'sha256_source':'','note':''}
    try:
        if not item.get('url'):raise ValueError('SOURCE_URL_MISSING')
        raw=fetch(item['url'])
        record['sha256_source']=hashlib.sha256(raw).hexdigest()
        family=OUT/safe(item['id']);family.mkdir(exist_ok=True)
        frames=render(raw,item,family)
        record.update(status='DRAFT_QA_HOLD',draft_jpg=len(frames),note='Actual source bytes; product/official source/option/style QA unapproved')
        with (family/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['file','sha256','bytes'])
            for p in frames:w.writerow([p.name,hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_size])
    except Exception as exc:
        record.update(status='SOURCE_HOLD',note=f'{type(exc).__name__}: {str(exc)[:180]}')
    rows.append(record)
    print(f"{i}/{len(PENDING)} {item['name']}: {record['status']}",flush=True)
with (OUT/'ALL_30_BATCH_STATUS.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary={'family_count':len(rows),'draft_families':sum(r['status']=='DRAFT_QA_HOLD' for r in rows),'draft_jpg':sum(r['draft_jpg'] for r in rows),'source_hold':sum(r['status']=='SOURCE_HOLD' for r in rows),'qa_approved':0,'uploaded':0,'public_verified_urls':0}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'README.txt').write_text('Automated batch review ONLY. Source candidate and product correctness unverified. Do NOT publish; no final MellowKR logo, cutout, verified claims or swatch QA. Existing 55 verified URLs untouched.\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
