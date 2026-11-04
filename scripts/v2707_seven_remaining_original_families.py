#!/usr/bin/env python3
"""v2707 last seven original preserved photo family media sets in one copy-only
QA recovery. All physical images remain original SHA bytes. No invented logo,
color swatch, approval, use-rights or package edition claims.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,base64,shutil,re
ARCH=Path('old_assets/public/owned86/20261029')
OUT=Path('qa-review/v2707-seven-remaining-archival-real-photo-family-sets')
assert ARCH.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
SPEC=[
 ('pending-16','drg-red-blemish-clear-soothing-cream-70ml','Dr.G R.E.D Blemish Clear Soothing Cream 70mL'),
 ('pending-22','obge-max300ml','OBgE Max Waterful Sun Cream 300mL'),
 ('pending-24','bioheal-boh-nad-glow-power-serum-30ml','BIOHEAL BOH NAD Glow Power Serum 30mL'),
 ('pending-25','bioheal-boh-nad-glow-boost-cream-50ml','BIOHEAL BOH NAD Glow Boost Cream 50mL'),
 ('pending-27','pixelpure-toner200ml','PIXEL PURE Soothing Ampoule Toner 200mL'),
 ('pending-28','pixelpure-pad210ml','PIXEL PURE Glow Cleansing Serum Pads 70ea/210mL'),
 ('pending-30','pixelpure-serum50ml','PIXEL PURE Aura Radiance Serum 50mL'),
]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for family,slug,title in SPEC:
 source=ARCH/slug
 fs=sorted(source.glob('*.jpg'),key=lambda p:int(re.search(r'_(\d+)\.jpg$',p.name).group(1)))
 assert len(fs)>=5,(family,len(fs))
 dest=OUT/family;dest.mkdir()
 files=[]
 for n,p in enumerate(fs[:5],1):
  target=dest/f'{n:02d}-authentic-old-product-image-unchanged-QA.jpg'
  shutil.copy2(p,target)
  assert sha(target)==sha(p)
  with Image.open(target) as im:
   im.load();assert im.size==(1080,1080) and im.format=='JPEG'
  assert target.stat().st_size<2000000
  files.append({'frame':n,'sha256':sha(target),'filename':target.name,'source_path':str(p),
                'bytes_identical_to_archive':True})
 rows.append({'family':family,'product':title,'photo_JPGs':5,
              'unverified_MK_badge_in_older_art':'POSSIBLE_HOLD',
              'commercial_release':'HOLD_PENDING_STOCK_EDITION_LICENSE_LOGO',
              'frames':files})
for page in range(3):
 subset=rows[page*3:(page+1)*3]
 if not subset:break
 canvas=Image.new('RGB',(1820,60+len(subset)*402),'#f1f2f0')
 d=ImageDraw.Draw(canvas)
 d.text((15,13),f'v2707 ORIGINAL 5-JPG FAMILY PHOTOS / PAGE {page+1} / QA ONLY',font=font,fill='#292929')
 for ri,x in enumerate(subset):
  for fr in x['frames']:
   with Image.open(OUT/x['family']/fr['filename']) as img:
    thumb=img.convert('RGB').resize((324,324),Image.Resampling.LANCZOS)
   xx=15+(fr['frame']-1)*361; yy=54+ri*402
   canvas.paste(thumb,(xx,yy))
   d.text((xx,yy+331),x['family']+' / '+str(fr['frame']),font=font,fill='#292929')
 proof=OUT/f'v2707-reviewed-page-{page+1}.jpg'
 canvas.save(proof,'JPEG',quality=81,optimize=True)
 (OUT/f'v2707-reviewed-page-{page+1}.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 'version':'v2707','baseline':'v2706',
 'source_archive_commit':'b2b883b86f3e80b7723ccf39b3766dfe6f483da9',
 'new_distinct_historical_product_families_staged':len(rows),
 'exact_original_JPG_assets_staged':len(rows)*5,
 'original_JPG_bytes_reencoded':0,
 'existing_11_sale_approved_untouched':True,
 'existing_55_verified_public_urls_untouched':True,
 'existing_QA_drafts_all_unchanged':True,
 'new_sales_approved':0,
 'source_photo_commercial_rights_verified':False,
 'owned_stock_exact_generation_verified':False,
 'original_round_MK_logo_verified':False,
 'final_xlsx_shared':False,
 'families':rows}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'new_product_families_with_5photo_reference':len(rows),
'exact_original_photo_JPGs':len(rows)*5,'retail_approved':0}))
