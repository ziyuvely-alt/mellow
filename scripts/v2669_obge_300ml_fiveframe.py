#!/usr/bin/env python3
"""v2669: OBgE Max Waterful Sun Cream 300mL five-frame QA draft.
Two distinct original product photos only when official URL succeeds.
No product/brand redesign, no MK badge, no generated fake product.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from urllib.request import Request,urlopen
from io import BytesIO
import json,hashlib,shutil,base64
ROOT=Path('qa-review/v2667-original-photo-picks/original-photo-picks')
OUT=Path('qa-review/v2669-obge-300ml-5frame-qa')
if OUT.exists():raise RuntimeError("v2669 already staged; stop to preserve")
OUT.mkdir(parents=True)
photo=ROOT/'pending-22-source-slot04-QA-ONLY.jpg'
assert photo.is_file()
official_url='https://m.obge.co.kr/web/product/medium/202603/e039688781d45789b70ee436c13cf0f6.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source={"file":photo.name,"sha256":sha(photo)}
try:
    req=Request(official_url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/png,image/*'})
    with urlopen(req,timeout=12) as res: raw=res.read(7_000_001)
    if not 12000<len(raw)<7_000_000: raise ValueError('Official image file unexpected size')
    im=Image.open(BytesIO(raw));im.load()
    if min(im.size)<320:raise ValueError('Official photo too small')
    official=ImageOps.exif_transpose(im).convert('RGB')
except Exception as e:
    hold={'version':'v2669','status':'HOLD_OFFICIAL_SECOND_PHOTO_UNAVAILABLE',
     'error_type':type(e).__name__,'source_300ml_verified':source,
     'new_jpg':0,'new_retail_approvals':0,'existing_files_untouched':True,
     'other_families_must_continue':True}
    (OUT/'hold.json').write_text(json.dumps(hold,indent=2)+'\n')
    print(json.dumps(hold));raise SystemExit(0)
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def ft(sz,b=False):return ImageFont.truetype(B if b else F,sz)
def draw_fit(d,s,x,y,width,size,fill='#343c37'):
    while d.textbbox((0,0),s,font=ft(size,True))[2]>width and size>22:size-=2
    d.text((x,y),s,font=ft(size,True),fill=fill)
rows=[]
dst=OUT/'01-genuine-300ml-bottle-scene-QA.jpg'
shutil.copy2(photo,dst)
rows.append({'frame':1,'file':dst.name,'sha256':sha(dst),'kind':'UNCHANGED_REAL_EXISTING_PHOTO'})
second=Image.new('RGB',(1080,1080),'#fbfbfa')
fitted=ImageOps.contain(official,(960,960),Image.Resampling.LANCZOS)
second.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
dst=OUT/'02-official-product-photo-contained-QA.jpg'
second.save(dst,'JPEG',quality=90,optimize=True)
rows.append({'frame':2,'file':dst.name,'sha256':sha(dst),'kind':'OFFICIAL_RETRIEVED_IMAGE_CONTAINED_NO_CROP',
             'official_source_url':official_url})
for slot,header,lines in [
 (3,'PRODUCT INFORMATION',['MAX WATERFUL','SUN CREAM','300 mL']),
 (4,'NET CONTENT',['300 mL','10.14 fl. oz.']),
 (5,'PRODUCT GUIDE',['FACE + BODY','Use as directed','on product packaging'])
]:
    im=Image.new('RGB',(1080,1080),'#f9faf8')
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,1080,20),fill='#9daaa1')
    draw_fit(d,'OBgE',84,84,900,64,fill='#434f4a')
    d.line((84,188,996,188),fill='#c6d1c8',width=4)
    draw_fit(d,header,84,245,920,43,fill='#62766c')
    y=390
    for i,line in enumerate(lines):
        draw_fit(d,line,84,y,920,72 if (slot==4 and i==0) else 59)
        y+=123
    d.line((84,873,996,873),fill='#d9e2da',width=3)
    d.text((84,926),'KOREAN BEAUTY',font=ft(34),fill='#66756a')
    dst=OUT/f'{slot:02d}-factual-info-qa.jpg'
    im.save(dst,'JPEG',quality=91,optimize=True,subsampling=0)
    rows.append({'frame':slot,'file':dst.name,'sha256':sha(dst),'kind':'FACT_ONLY_INFO_NEW'})
assert len(rows)==5
for r in rows:
    p=OUT/r['file']
    with Image.open(p) as im:
        im.load()
        assert im.format=='JPEG' and im.size==(1080,1080)
    assert p.stat().st_size<2_000_000
    r['bytes']=p.stat().st_size
proof=Image.new('RGB',(1920,2160),'#f0f1ef')
d=ImageDraw.Draw(proof)
d.text((36,20),'OBgE 300 mL | FIVE DISTINCT IMAGE QA DRAFT',font=ft(43,True),fill='#232826')
for k,r in enumerate(rows):
    p=OUT/r['file']
    with Image.open(p) as im:thumb=im.convert('RGB').resize((575,575),Image.Resampling.LANCZOS)
    x=30+(k%3)*630;y=95+(k//3)*1000
    proof.paste(thumb,(x,y))
    d.text((x,y+605),str(r['frame']).zfill(2)+' / '+('PHOTO' if k<2 else 'INFO'),font=ft(28),fill='#222222')
p=OUT/'v2669-5frame-contact.jpg';proof.save(p,quality=82,optimize=True)
(OUT/'v2669-contact.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
manifest={'version':'v2669','family':'pending-22','product':'OBgE Max Waterful Sun Cream 300 mL',
 'status':'FIVE_FRAME_QA_DRAFT_NOT_RETAIL_APPROVED','source_photo_count':2,
 'official_second_photo_size':list(official.size),'photo_usage_rights_confirmed':False,
 'stock_edition_confirmed':False,'latest_v2647_compared':False,
 'frames':rows,'public_55_urls_modified':False,'old_11_approved_modified':False,
 'final_spreadsheet_shared':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'result':'FIVE_FRAME_QA_DRAFT','family':'pending-22','frames':5,
                  'new_info_jpgs':3,'real_source_photos':2,'approved':0}))
