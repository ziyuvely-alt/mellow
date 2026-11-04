#!/usr/bin/env python3
"""v2705: Recover fifteen real, historically preserved JPG photo/art assets
from the archive commit, without rerender or rewriting. This is a new,
isolated QA comparison candidate (NOT storefront approval).
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,shutil,base64,re
ARCH=Path('old_assets/public/owned86/20261029')
OUT=Path('qa-review/v2705-three-recovered-photo-first-family-sets')
assert ARCH.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
FAMILIES=[
 ('pending-03','missha-m-perfect-cover-bb-cream','MISSHA M Perfect Cover BB Cream | gold pump old generation'),
 ('pending-09','obge-oil-control-finisher-5g','OBgE Oil Control Finisher 5g'),
 ('pending-21','goodal-green-tangerine-eye-cream-30ml','GOODAL Green Tangerine Vita C Eye Cream 30ml')
]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
board=Image.new('RGB',(1820,1460),'#eeeeec')
d=ImageDraw.Draw(board)
d.text((16,15),'v2705 REAL ARCHIVED ASSETS / THREE PRODUCT FAMILIES / QA-ONLY',font=font,fill='#222222')
rows=[]
for i,(family,slug,title) in enumerate(FAMILIES):
 path=ARCH/slug
 srcs=sorted(path.glob('*.jpg'),key=lambda p:int(re.search(r'_(\d+)\.jpg$',p.name).group(1)))
 assert len(srcs)>=5,(family,len(srcs))
 dst=OUT/family;dst.mkdir()
 frames=[]
 for num,src in enumerate(srcs[:5],1):
  target=dst/f'{num:02d}-original-source-sha-unchanged-QA.jpg'
  shutil.copy2(src,target)
  sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
  assert sha(src)==sha(target)
  with Image.open(target) as im:
   im.load()
   assert im.format=='JPEG' and im.size==(1080,1080),(target,im.size)
   thumb=im.convert('RGB').resize((325,325),Image.Resampling.LANCZOS)
  assert target.stat().st_size<2_000_000
  x=16+(num-1)*359;y=55+i*451
  board.paste(thumb,(x,y))
  d.text((x,y+335),family+' / '+str(num),font=font,fill='#222222')
  frames.append(dict(frame=num,source=str(src),file=target.name,
                     source_sha256=sha(src),saved_sha256=sha(target),size_bytes=target.stat().st_size))
 rows.append(dict(family=family,product=title,actual_JPGs=len(frames),
                  all_original_source_bytes_preserved=True,retail_approval='HOLD_PHOTO_LICENSE_STOCK_GEN_MK_QA',
                  frames=frames))
proof=OUT/'v2705-archival-product-photos-review.jpg'
board.save(proof,quality=82,optimize=True)
(OUT/'v2705-contact.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
manifest=dict(version='v2705',baseline='v2704',source_archive_commit='b2b883b86f3e80b7723ccf39b3766dfe6f483da9',
               families=rows,archived_JPGs_recovered=15,legacy_JPGs_reencoded=0,
               old_QA_sets_preserved=True,existing_11_approved_unchanged=True,
               existing_55_public_URLs_unchanged=True,commercial_photo_rights_proven=False,
               exact_owned_stock_version_proven=False,
               original_round_MK_logo_validated=False,
               new_retail_approved=0,final_XLSX_shared=False)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2705','photo_JPG_assets_recovered':15,
                  'families':[x['family'] for x in rows],'sales_approved':0}))
