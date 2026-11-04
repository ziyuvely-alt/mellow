#!/usr/bin/env python3
"""v2668 PIXEL PURE Glow Cleansing Serum Pad 210 mL / 70 pads:
Construct 5 distinct QA images from 2 already verified, byte-preserved actual product
photos + 3 original fact-only cards. No invented photo/ingredients/benefits/MK logo.
Never modify released images, and never call a draft sale-approved.
"""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import json,hashlib,shutil,base64,math
ROOT=Path('qa-review/v2667-original-photo-picks/original-photo-picks')
HIST=Path('source/historical/review-JPG-by-family/pending-28')
OUT=Path('qa-review/v2668-pixelpure-5card-actual-draft')
if OUT.exists():raise RuntimeError('QA draft already exists: do not overwrite')
OUT.mkdir(parents=True)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(sz,bold=False):return ImageFont.truetype(B if bold else F,sz)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(draw,text,x,y,max_width,font_size=64,color='#502d39',bold=True):
    size=font_size
    while draw.textbbox((0,0),text,font=ft(size,bold))[2] > max_width and size>=20:
        size-=2
    assert size>=20,(text,max_width)
    draw.text((x,y),text,fill=color,font=ft(size,bold))
    return size
rows=[]
sources={1:ROOT/'pending-28-source-slot02-QA-ONLY.jpg',
         2:next(iter(sorted(HIST.glob('04*.jpg'))))}
for index,src in sources.items():
    assert src.exists(),src
    dest=OUT/f'{index:02d}-actual-product-source-photo-QA.jpg'
    shutil.copy2(src,dest)
    with Image.open(dest) as im:
        im.load()
        assert im.size==(1080,1080) and im.format=="JPEG"
    rows.append({'frame':index,'source_original':str(src),'file':dest.name,
                 'sha256':digest(dest),'bytes':dest.stat().st_size,
                 'kind':'ACTUAL_PRODUCT_PHOTO_UNMODIFIED'})
# Three fact-only frames designed distinct from the two actual photos.
def canvas(top):
    im=Image.new('RGB',(1080,1080),'#fffafa')
    draw=ImageDraw.Draw(im)
    draw.rectangle((0,0,1080,23),fill=top)
    return im,draw
# Frame03: quantity identity
im,d=canvas('#c88f9f')
txt(d,'PIXEL PURE',75,86,930,46)
d.line((75,164,1005,164),fill='#e2c8ce',width=3)
txt(d,'GLOW CLEANSING',75,255,930,66)
txt(d,'SERUM PAD',75,365,930,79)
d.rounded_rectangle((76,580,1004,822),radius=46,fill='#f5e1e7')
txt(d,'210 mL',120,642,370,84)
txt(d,'70 PADS',567,642,390,68)
txt(d,'KOREAN SKINCARE',75,945,900,32,color='#856c73',bold=False)
files={3:im}
# Frame04: package label facts using no fabricated claims
im,d=canvas('#d2a3b1')
txt(d,'PRODUCT INFORMATION',75,95,930,42)
txt(d,'GLOW CLEANSING',75,285,930,61)
txt(d,'SERUM PAD',75,385,930,75)
d.line((75,555,1005,555),fill='#d7aab6',width=4)
txt(d,'NET CONTENT',75,630,930,37,color='#78525d')
txt(d,'210 mL / 70 pads',75,710,930,62)
txt(d,'PIXEL PURE',75,937,930,40,color='#78525d')
files[4]=im
# Frame05: gentle neutral instructions avoiding ingredient/effect claims
im,d=canvas('#caa6af')
txt(d,'PRODUCT GUIDE',80,96,930,48)
txt(d,'GLOW CLEANSING',80,246,910,58)
txt(d,'SERUM PAD',80,340,910,72)
d.rounded_rectangle((77,518,1003,879),radius=48,fill='#f5e3e8')
txt(d,'01  Take one pad',113,574,846,48)
txt(d,'02  Follow label directions',113,690,846,40)
txt(d,'03  Close the lid after use',113,789,846,36)
txt(d,'210 mL  |  70 pads',80,955,900,34,color='#775963')
files[5]=im
for index,im in files.items():
    p=OUT/f'{index:02d}-factual-info-card-QA.jpg'
    im.save(p,format='JPEG',quality=92,optimize=True,subsampling=0)
    rows.append({'frame':index,'file':p.name,'sha256':digest(p),'bytes':p.stat().st_size,
                 'kind':'FACT_ONLY_INFO_CARD_NEW'})
assert len(rows)==5
for r in rows:
    with Image.open(OUT/r['file']) as im:
        im.load()
        assert im.size==(1080,1080) and im.format=='JPEG'
    assert r['bytes']<2_000_000
board=Image.new('RGB',(1920,2250),'#eeedef');d=ImageDraw.Draw(board)
txt(d,'PIXEL PURE / 5 DISTINCT FRAMES / QA ONLY',35,20,1850,42,color='#242424')
for i,r in enumerate(rows):
    with Image.open(OUT/r['file']) as im:
        thumb=im.convert('RGB').resize((565,565),Image.Resampling.LANCZOS)
    x=35+(i%3)*625;y=105+(i//3)*1000
    board.paste(thumb,(x,y))
    txt(d,'FRAME '+str(r['frame']).zfill(2)+' / '+('PHOTO' if r['frame']<=2 else 'INFO'),x,y+595,595,27,color='#333333')
proof=OUT/'v2668-five-frames-visual-proof.jpg'
board.save(proof,quality=80,optimize=True)
(OUT/'v2668-proof.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={'version':'v2668','product':'PIXEL PURE Glow Cleansing Serum Pad 210 mL / 70 Pads',
 'family':'pending-28','five_image_draft_complete':True,'sales_ready':False,
 'actual_source_photo_unmodified':2,'new_distinct_factual_frames':3,
 'unverified_MK_logo_added':False,'status':'QA_ONLY_PENDING_STOCK_IDENTITY_PHOTO_LICENSE_LATEST_V2647_AND_HUMAN_FINAL_QA',
 'frames':rows,'legacy_11_approved_groups_untouched':True,'public_55_urls_unchanged':True,
 'final_xlsx_shared':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'product_family':'pending-28','five_image_draft_complete':True,
                  'actual_existing_source_photos':2,'new_jpg_images':3,
                  'images_tested':5,'sales_approved':0},ensure_ascii=False))
