#!/usr/bin/env python3
"""v2670 selective OBgE frame02 repair: replace near-identical scene with
the official 300mL beige-background packshot; copy remaining four bytes unchanged.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from urllib.request import urlopen,Request
from io import BytesIO
import json,hashlib,shutil,base64
SRC=Path('qa-review/v2669-obge-300ml-5frame-qa')
OUT=Path('qa-review/v2670-obge-300ml-distinct-official-photo-qa')
assert SRC.exists() and not OUT.exists()
OUT.mkdir(parents=True)
manifest=json.loads((SRC/'manifest.json').read_text())
assert manifest['version']=='v2669' and len(manifest['frames'])==5
new_url='https://m.obge.co.kr/web/product/big/202512/a539d1b39803753e1b2da68db3f586d2.jpg'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dhash(im):
 pix=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if pix[y*9+x]>pix[y*9+x+1])
with urlopen(Request(new_url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/*'}),timeout=12) as resp:raw=resp.read(7_000_001)
assert 12000<len(raw)<7_000_000
source=Image.open(BytesIO(raw));source.load()
assert source.format in ('JPEG','PNG','WEBP') and min(source.size)>=320
new_src=ImageOps.exif_transpose(source).convert('RGB')
new=Image.new('RGB',(1080,1080),'#f7f4ec')
fitted=ImageOps.contain(new_src,(1040,1040),Image.Resampling.LANCZOS)
new.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
with Image.open(SRC/manifest['frames'][0]['file']) as first:
 first.load();distance=(dhash(first.convert('RGB'))^dhash(new)).bit_count()
assert distance>=10, f'New official frame is still too similar to 01: {distance}'
newfile='02-official-beige-packshot-distinct-QA.jpg'
new.save(OUT/newfile,format='JPEG',quality=93,optimize=True,subsampling=0)
rows=[]
for r in manifest['frames']:
    rr=dict(r)
    if r['frame']==2:
        rr.update({'file':newfile,'sha256':digest(OUT/newfile),
          'kind':'OFFICIAL_300ML_BEIGE_PACKSHOT_DISTINCT_NO_CROP',
          'official_source_url':new_url,'source_image_px':list(source.size)})
    else:
        old=SRC/r['file'];target=OUT/r['file']
        assert digest(old)==r['sha256']
        shutil.copy2(old,target)
        assert digest(target)==r['sha256']
    rows.append(rr)
assert len(rows)==5 and all((OUT/r['file']).is_file() for r in rows)
for r in rows:
 with Image.open(OUT/r['file']) as im:
  im.load();assert im.format=='JPEG' and im.size==(1080,1080)
 assert (OUT/r['file']).stat().st_size<2_000_000
proof=Image.new('RGB',(1920,2150),'#e9eae7')
d=ImageDraw.Draw(proof)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',39)
d.text((30,20),'v2670 OBgE 300mL 5 DISTINCT JPG QA FRAMES',fill='#222222',font=font)
for k,r in enumerate(rows):
    with Image.open(OUT/r['file']) as im:
        thumb=im.convert('RGB').resize((575,575),Image.Resampling.LANCZOS)
    x=30+(k%3)*625;y=105+(k//3)*995
    proof.paste(thumb,(x,y))
    d.text((x,y+603),('FRAME '+str(r['frame']).zfill(2)),fill='#222222',font=font)
p=OUT/'v2670-proof.jpg';proof.save(p,quality=83,optimize=True)
(OUT/'v2670-proof.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
newmanifest={'version':'v2670','baseline':'v2669','family':'pending-22',
'product':'OBgE Max Waterful Sun Cream 300 mL',
'new_source_url':new_url,'different_image_first_vs_second_dhash_distance':distance,
'newly_replaced_image_slots':[2],'prior_frame_sha256_byte_unchanged':[1,3,4,5],
'sale_approved':False,'commercial_photo_rights_verified':False,
'exact_owned_stock_matched':False,'latest_v2647_compared':False,
'original_55_public_urls_unchanged':True,'old_11_approved_unchanged':True,
'no_excel':True,'frames':rows}
(OUT/'manifest.json').write_text(json.dumps(newmanifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2670','changed':1,'unchanged':4,
  'dhash_first_vs_second':distance,'photo_distinct_pass':True,'sales_approved':0}))
