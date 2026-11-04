#!/usr/bin/env python3
"""v2710 fix exactly two incorrect copy labels in v2709 photo-detail QA JPGs:
CLIO lid-and-cushion image is not a clear 'inside' demonstration;
PIXEL PURE brand must be full name, not abbreviated as PIXEL.
Source photographs and 8/10 prior photo JPG bytes remain identical.
No commercial release authorized; no unverified logo adopted.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path('qa-review')
SRC=ROOT/'v2709-clio-mini-and-pixelpure-detail-corrections'
OUT=ROOT/'v2710-two-accurate-copy-corrections-photo-QA'
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
fixes={'pending-04':4,'pending-26':5}
result=[]
for fid,fixslot in fixes.items():
 dst=OUT/fid;dst.mkdir()
 src_files=sorted((SRC/fid).glob('[0-9][0-9]-*.jpg'))
 assert len(src_files)==5
 frames=[]
 for src in src_files:
  slot=int(src.name[:2])
  dest=dst/src.name
  if slot!=fixslot:
   shutil.copy2(src,dest)
   assert sha(dest)==sha(src)
   frames.append({'slot':slot,'file':dest.name,'status':'UNMODIFIED_PRIOR_JPG','sha256':sha(dest)})
   continue
  with Image.open(src) as image:
   image.load();im=image.convert('RGB')
  draw=ImageDraw.Draw(im)
  if fid=='pending-04':
   # Only title and subtitle zone, above original photo.
   draw.rectangle((99,165,987,292),fill='#ffffff')
   draw.text((105,173),'COMPACT DETAILS',font=font(54,True),fill='#3a3337')
   draw.text((105,242),'Closer look at the compact and cushion',font=font(23),fill='#897e82')
   operation='Replace misleading INSIDE THE COMPACT with COMPACT DETAILS'
  else:
   draw.rectangle((99,108,500,161),fill='#ffffff')
   draw.text((105,115),'PIXEL PURE',font=font(31,True),fill='#645961')
   operation='Replace truncated brand PIXEL with PIXEL PURE'
  dest=dst/f'{slot:02d}-copy-accuracy-corrected-product-photo-QA.jpg'
  im.save(dest,'JPEG',quality=94,optimize=True,subsampling=0)
  frames.append({'slot':slot,'file':dest.name,'status':'TEXT_ONLY_CORRECTION_ABOVE_UNCHANGED_PHOTO_REGION',
    'sha256':sha(dest),'prior_sha256':sha(src),'operation':operation})
 for item in frames:
  p=dst/item['file']
  with Image.open(p) as img:
   img.load();assert img.format=='JPEG' and img.size==(1080,1080)
  assert p.stat().st_size<2_000_000
 result.append({'family':fid,'JPG_count':5,'corrected_only_slot':fixslot,
                'four_prior_JPGs_preserved_exact_bytes':True,
                'photo_content_not_redrawn':True,
                'retail_approved':False,'files':frames})
font_small=font(23)
for item in result:
 board=Image.new('RGB',(1850,490),'#f0f0ef')
 d=ImageDraw.Draw(board)
 d.text((15,15),f"v2710 {item['family']} two copy labels corrected / QA NOT RETAIL",font=font(26,True),fill='#252525')
 for f in item['files']:
  with Image.open(OUT/item['family']/f['file']) as img:tile=img.convert('RGB').resize((337,337),Image.Resampling.LANCZOS)
  x=14+(f['slot']-1)*369
  board.paste(tile,(x,65))
  d.text((x,420),f"{f['slot']:02d} "+('COPY FIXED' if f['slot']==item['corrected_only_slot'] else 'UNMODIFIED'),font=font_small,fill='#252525')
 proof=OUT/f"v2710-{item['family']}-contact.jpg"
 board.save(proof,'JPEG',quality=84,optimize=True)
 (OUT/f"v2710-{item['family']}-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={'version':'v2710','base':'v2709',
  'corrected_product_families':2,'changed_text_area_only_JPGs':2,
  'exact_byte_preserved_other_JPGs':8,
  'recovered_source_photographs_recreated':0,
  'new_fabricated_swatches_or_logos':0,'new_retail_approvals':0,
  'retail_release':'HOLD_MK_BADGE_RIGHTS_AND_STOCK_EDITION',
  'old_55_public_URLs_untouched':True,'original_11_approved_families_untouched':True,
  'prior_v2709_photo_JPGs_unchanged':True,'final_spreadsheet_shared':False,
  'families':result}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2710','actual_corrected_JPGs':2,'old_JPGs_sha_identical':8,'sale_approved':0}))
