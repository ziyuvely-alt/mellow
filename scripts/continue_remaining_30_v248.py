#!/usr/bin/env python3
"""Continue the pending roster without recreating previously produced frames.

This stage uses actual downloadable candidate bytes only. A single independently
sourced hero draft is produced per candidate; no repeated crop masquerades as
five distinct frames. All outputs stay in an Actions artifact, not public/images.
"""
import csv, hashlib, io, json, re
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
QUEUE = json.loads((ROOT/'evidence/pending-30-v247.json').read_text(encoding='utf-8'))
OUT = ROOT/'production-continuation-v248'
OUT.mkdir(exist_ok=True)
ALREADY = {'pending-02','pending-05','pending-06','pending-10','pending-22'}
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONTB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n, bold=False):
    try: return ImageFont.truetype(FONTB if bold else FONT,n)
    except: return ImageFont.load_default()
def fetch(url):
    p=urlparse(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password:
        raise ValueError('UNSAFE_SOURCE_URL')
    resp=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'},timeout=(10,22),stream=True)
    resp.raise_for_status()
    if urlparse(resp.url).scheme != 'https': raise ValueError('INSECURE_REDIRECT')
    raw=io.BytesIO()
    for b in resp.iter_content(65536):
        raw.write(b)
        if raw.tell()>16000000: raise ValueError('SOURCE_TOO_LARGE')
    blob=raw.getvalue()
    with Image.open(io.BytesIO(blob)) as test:
        test.load()
        if min(test.size)<250 or test.format not in ('JPEG','PNG','WEBP'):raise ValueError('BAD_SOURCE_IMAGE')
    return blob
def make_hero(blob, name, target):
    with Image.open(io.BytesIO(blob)) as im:
        pic=ImageOps.exif_transpose(im).convert('RGBA')
    im=Image.new('RGB',(1080,1080),(250,244,238))
    d=ImageDraw.Draw(im)
    d.ellipse((-280,480,460,1220),fill=(220,232,220))
    d.ellipse((820,-280,1350,250),fill=(249,223,214))
    # Do not invent cutout boundaries for JPEG photos; transparent PNG retains real alpha.
    size=(860,790)
    pic.thumbnail(size, Image.Resampling.LANCZOS)
    x=(1080-pic.width)//2; y=90+(790-pic.height)//2
    if pic.getextrema()[3] == (255,255):
        # Opaque source is retained without background replacement or fake cutout.
        im.paste(pic,(x,y))
    else: im.paste(pic,(x,y),pic)
    # Only product name from the inventory queue, no unverified claims or shades.
    f=font(34,True)
    text=name
    chunks=[]; line=''
    for c in text:
        if d.textbbox((0,0),line+c,font=f)[2]>935 and line:
            chunks.append(line);line=c
        else:line+=c
    if line:chunks.append(line)
    yy=880
    for s in chunks[:3]:
        d.text((70,yy),s,font=f,fill=(49,67,58)); yy+=46
    im.save(target,'JPEG',quality=89,optimize=True)
    if target.stat().st_size>=2_000_000:
        im.save(target,'JPEG',quality=78,optimize=True)
    assert target.stat().st_size<2_000_000
    return hashlib.sha256(target.read_bytes()).hexdigest()
records=[]
for item in QUEUE:
    id=item['id']
    row={'id':id,'name':item['name'],'status':'','new_jpg':0,'sha256':'','reason':''}
    if id in ALREADY:
        row.update(status='EXISTING_PRODUCTION_PRESERVED',reason='Do not recreate prior production drafts')
    elif not item.get('url'):
        row.update(status='SOURCE_PENDING',reason='No source candidate')
    else:
        try:
            blob=fetch(item['url'])
            folder=OUT/id;folder.mkdir(exist_ok=True)
            file=folder/'01_HERO_CANDIDATE.jpg'
            h=make_hero(blob,item['name'],file)
            row.update(status='JPG_PRODUCTION',new_jpg=1,sha256=h,reason='Candidate photo exact SKU and commercial rights require later final QA; original MK logo not accessible in repository')
        except Exception as e:
            row.update(status='SOURCE_PENDING',reason=f'{type(e).__name__}: {str(e)[:160]}')
    records.append(row)
    print(id,row['status'],flush=True)
with (OUT/'production_manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
summary={'roster':len(records),'preserved_existing':len(ALREADY),'new_jpg':sum(x['new_jpg'] for x in records),'jpg_production_families':sum(x['new_jpg']>0 for x in records),'sales_qa_approved':0,'published':0,'note':'Production only; final QA deferred; no product public deployment'}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False),flush=True)
