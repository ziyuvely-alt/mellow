#!/usr/bin/env python3
"""v2672, real 2-family 10 JPG production-set curation, no recreation of existing imagery.
Preserve genuine existing 5 photo-based frames per family, verify 1080 JPG <2MB,
avoid final publication if stock edition/right proof missing.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil,base64,itertools
root=Path('source/historical/review-JPG-by-family')
out=Path('qa-review/v2672-two-five-JPG-real-scene-sets')
assert not out.exists()
out.mkdir(parents=True)
fams={"pending-17":{"product":"Dr.G Brightening Up Moisture Sun 50mL"},
      "pending-20":{"product":"GOODAL Green Tangerine Vita C Serum Mist 100mL"}}
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
rows=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
proof=Image.new('RGB',(1800,920),'#ecefed');d=ImageDraw.Draw(proof)
d.text((22,10),'v2672 TWO FIVE-FRAME PHOTO-LED QA SETS | NO PRODUCT ALTERATION',font=font,fill='#151515')
for i,(fam,info) in enumerate(fams.items()):
 srcs=sorted((root/fam).glob('*.jpg'))
 assert len(srcs)>=5
 dest=out/fam;dest.mkdir()
 hashes=[]
 for idx,p in enumerate(srcs[:5],1):
  target=dest/f'{idx:02d}-original-QA.jpg'
  shutil.copy2(p,target)
  assert hashfile(target)==hashfile(p)
  with Image.open(target) as im:
   im.load();assert im.format=='JPEG' and im.size==(1080,1080)
   dh=dhash(im.convert('RGB'))
   thumbnail=im.convert('RGB').resize((332,332),Image.Resampling.LANCZOS)
  assert target.stat().st_size < 2_000_000
  hashes.append(dh)
  x=25+(idx-1)*352;y=52+i*430
  proof.paste(thumbnail,(x,y))
  d.text((x,y+336),f'{fam} / frame {idx:02d}',font=font,fill='#111111')
 minimum=min((a^b).bit_count() for a,b in itertools.combinations(hashes,2))
 rows.append({'family':fam,'product':info['product'],'actual_existing_jpg_frames':5,
              'shas':[hashfile(p) for p in sorted(dest.glob('*.jpg'))],
              'minimal_internal_dhash_distance':minimum,'packaging_match_verified':False,
              'sale_release':'HOLD_PHOTO_LICENSE_STOCK_V2647_AND_FINAL_HUMAN_QA'})
p=out/'v2672-two-family-preview.jpg';proof.save(p,quality=82,optimize=True)
(out/'v2672-preview.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
manifest={'version':'v2672','baseline':'v2671','new_family_5JPG_QA_sets':2,
          'physical_existing_JPG_preserved_without_reencoding':10,
          'source':'v2593 historical; currently accessible latest v2647 absent',
          'rows':rows,'new_sale_approved_families':0,
          'prior_11_approved_unchanged':True,'old_55_public_urls_unchanged':True,
          'no_final_excel':True}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'five_JPG_family_sets':2,'files':10,'minimum_dhash':[x['minimal_internal_dhash_distance'] for x in rows],
                  'new_sales_approved':0}))
