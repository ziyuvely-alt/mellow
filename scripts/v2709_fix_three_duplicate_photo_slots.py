#!/usr/bin/env python3
"""v2709 targeted visual diversity repair of duplicate-heavy CLIO mini and
PIXELPURE 145 mL cleanser, by reusing authentic source photograph pixels only.

No image generation. No fabricated swatch, product, brand logo, or fake cutout.
The 3 replacement frames are zoomed photo details, not claims of new scenes.
Original 80 JPGs, published 11 families, and 55 approved public URLs immutable.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
from collections import defaultdict
import hashlib,json,shutil,base64
ROOT=Path('qa-review')
SRC=ROOT/'v2706-six-archival-five-real-source-families'
OUT=ROOT/'v2709-clio-mini-and-pixelpure-detail-corrections'
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(sz,bold=False):return ImageFont.truetype(BOLD if bold else FONT,sz)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
TARGETS={
 'pending-04':{
   'name':'CLIO Mesh Glow Essential Mini Cushion 5g',
   'crop_by_slot':{
    3:((295,324,875,855),'PUFF & COMPACT','Detail from an existing product photo'),
    4:((280,307,865,840),'INSIDE THE COMPACT','Product photo detail, not a shade chart')
   },
   'hold':['Only genuine mini 5g artwork is allowed, not the 15g set','Shade 21C/21N/23N label and stock edition need confirmation']
 },
 'pending-26':{
   'name':'PIXEL PURE Gentle Gel-to-Foam Cleanser 145mL',
   'crop_by_slot':{
     5:((315,223,815,854),'BOTTLE CLOSE-UP','145mL package detail from original source')
   },
   'hold':['Do not substitute a 150mL package image','Genuine product packaging and photo redistribution rights not verified']
 }
}
records=[]
for fid,cfg in TARGETS.items():
  dirname=OUT/fid;dirname.mkdir()
  old=SRC/fid
  originals=sorted(old.glob('[0-9][0-9]-*.jpg'))
  assert len(originals)==5,(fid,len(originals))
  entries=[]
  for original in originals:
    slot=int(original.name[:2])
    with Image.open(original) as pic:
      pic.load();assert pic.format=='JPEG' and pic.size==(1080,1080)
      original_rgb=pic.convert('RGB')
    if slot not in cfg['crop_by_slot']:
      dst=dirname/original.name
      shutil.copy2(original,dst)
      assert sha(dst)==sha(original)
      entries.append({'slot':slot,'file':dst.name,'role':'PRESERVED_OLD_REAL_SCENE','source':str(original),'sha256':sha(dst),'source_sha256':sha(original),'pixel_origin':'UNCHANGED_SOURCE_BYTES'})
      continue
    (x0,y0,x1,y1),title,subtitle=cfg['crop_by_slot'][slot]
    assert 0<=x0<x1<=880 and 0<=y0<y1<=875, 'Do not include unverified corner MK mark'
    crop=original_rgb.crop((x0,y0,x1,y1))
    canvas=Image.new('RGB',(1080,1080),'#fffdfb')
    draw=ImageDraw.Draw(canvas)
    draw.rounded_rectangle((65,63,1015,1018),radius=38,fill='#ffffff',outline='#eee6e3',width=2)
    draw.text((105,115),cfg['name'].split(' ')[0].upper(),font=f(31,True),fill='#645961')
    draw.text((105,173),title,font=f(54,True),fill='#3a3337')
    draw.text((105,242),subtitle,font=f(23),fill='#897e82')
    # Soft organic vignette is an honest detail crop, not background removal.
    fitted=ImageOps.contain(crop,(845,670),Image.Resampling.LANCZOS)
    mask=Image.new('L',fitted.size,0)
    md=ImageDraw.Draw(mask)
    md.ellipse((4,4,fitted.width-5,fitted.height-5),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(17))
    at=((1080-fitted.width)//2,322+(675-fitted.height)//2)
    canvas.paste(fitted,at,mask)
    draw.text((105,951),'SOURCE PHOTO DETAIL  |  QA ONLY',font=f(22),fill='#8d7e82')
    dst=dirname/f'{slot:02d}-real-source-detail-no-unverified-logo-QA.jpg'
    canvas.save(dst,'JPEG',quality=94,optimize=True,subsampling=0)
    entries.append({'slot':slot,'file':dst.name,'role':'NEW_DETAIL_CROP_FROM_EXISTING_REAL_PHOTO',
       'source':str(original),'sha256':sha(dst),'source_sha256':sha(original),
       'crop_source_xyxy':[x0,y0,x1,y1],'exact_product_photo_pixels_used':True,
       'source_badge_area_excluded':True,'not_true_background_removal':True})
  assert [x['slot'] for x in entries]==[1,2,3,4,5]
  for x in entries:
    path=dirname/x['file']
    with Image.open(path) as image:
      image.load();assert image.format=='JPEG' and image.size==(1080,1080)
    assert path.stat().st_size<2_000_000
    x['bytes']=path.stat().st_size
  records.append({'family':fid,'product':cfg['name'],'JPG_count':len(entries),
    'preserved_exact':5-len(cfg['crop_by_slot']),'new_real_photo_detail_crops':len(cfg['crop_by_slot']),
    'hold_reasons':cfg['hold']+['Original source corner MK art not authenticated','Commercial source photo reuse permission not verified'],
    'status':'DRAFT_VISUAL_QA_NOT_RETAIL_APPROVED','files':entries})
for p,rec in enumerate(records):
 board=Image.new('RGB',(1855,490),'#f0f0ee')
 d=ImageDraw.Draw(board)
 d.text((20,17),'v2709 PHOTO DETAIL REPAIR / '+rec['family']+' / QA ONLY',font=f(26,True),fill='#282628')
 for x in rec['files']:
    with Image.open(OUT/rec['family']/x['file']) as im:
      tile=im.convert('RGB').resize((335,335),Image.Resampling.LANCZOS)
    xx=16+(x['slot']-1)*369
    board.paste(tile,(xx,70))
    d.text((xx,421),f"FRAME {x['slot']:02d}  "+('DETAIL' if x['role'].startswith('NEW') else 'PRESERVED'),font=f(21),fill='#353034')
 proof=OUT/f'v2709-{rec["family"]}-review.jpg'
 board.save(proof,'JPEG',quality=85,optimize=True)
 (OUT/f'v2709-{rec["family"]}-review.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={'version':'v2709','baseline':'v2708',
  'product_families_updated':len(records),'new_detail_photograph_frames':3,
  'existing_QA_photos_SHA_preserved':7,'source_photos_reencoded_or_mutated':0,
  'new_generated_product_objects':0,'new_generated_brand_logos':0,
  'source_corner_logo_region_excluded_from_derived_crops':True,
  'commercial_approved':0,'photo_rights_verified':False,'owned_stock_generation_verified':False,
  'prior_11_sale_approved_families_unchanged':True,'prior_55_public_URLs_unchanged':True,
  'previous_v2706_asset_sets_untouched':True,'final_XLSX_shared':False,
  'families':records}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'families':2,'new_real_photo_detail_JPGs':3,'old_sha_identical_JPGs':7,'new_retail_approved':0}))
