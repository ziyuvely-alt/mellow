#!/usr/bin/env python3
"""v2788: make three one-time, new-source GOODAL cream texture crop candidates
and test CLIO 5g native-res exact-product image variants. Never mutate any
previous QA or commercial images. Do not infer commercial rights or item shade.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import requests,json,shutil,hashlib,base64
QA=Path('qa-review')
OUT=QA/'v2788-goodal-new-source-texture-options-clio-mini-native'
A=QA/'v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA'
C=QA/'v2787-goodal-fifth-photo-fix-and-clio-mini-official-source'
assert A.is_dir() and C.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
G=json.loads((A/'manifest.json').read_text())
O=json.loads((C/'manifest.json').read_text())
# Crop ONLY the new jar + surrounding cream swirl from real brand photo01.
# Three variations staged in ONE run for visual choice; not fake independent sources.
SOURCE=A/G['curated_photos'][0]['file']
CROPS={
 'a-top-cream':(160,10,780,420),
 'b-formula-swirl':(215,8,985,515),
 'c-left-cream-jar-detail':(180,55,850,680)
}
good_dir=OUT/'pending-19';good_dir.mkdir()
good=[]
with Image.open(SOURCE) as im:
 im.load();assert im.format=='JPEG' and im.size==(1080,1080)
 picture=im.convert('RGB')
for n,(role,rect) in enumerate(CROPS.items(),1):
 cut=ImageOps.fit(picture.crop(rect),(1080,1080),Image.Resampling.LANCZOS)
 path=good_dir/f'{n:02d}-{role}-real-photo-QA.jpg'
 cut.save(path,'JPEG',quality=92,optimize=True,subsampling=0)
 assert path.stat().st_size<2_000_000
 good.append({'role':role,'file':str(path.relative_to(OUT)),
              'crop':list(rect),'source':str(SOURCE),
              'source_sha256':hashfile(SOURCE),'sha256':hashfile(path),
              'source_pixel_only':True,'visually_reviewed':False})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
canvas=Image.new('RGB',(1400,500),'#f0f0ee')
d=ImageDraw.Draw(canvas)
d.text((15,12),'v2788 GOODAL CREAM 50mL / DIFFERENT AUTHENTIC SOURCE / 3 MACRO TRIALS',font=font,fill='#272727')
for i,x in enumerate(good):
 with Image.open(OUT/x['file']) as im:thumb=im.convert('RGB').resize((420,420),Image.Resampling.LANCZOS)
 xx=15+i*462
 canvas.paste(thumb,(xx,52))
 d.text((xx,475),x['role'],font=font,fill='#333333')
proof=OUT/'goodal-three-real-crop-candidates.jpg'
canvas.save(proof,'JPEG',quality=83,optimize=True)
(OUT/'goodal-contact.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
# CLIO mini model exact same official product media directory.
M=O['clio']
base='https://clubclio.co.kr/data/mall_data/images/product/00/00/00/69/54/'
assert M['official_exact_product_page'].endswith('0000006954')
names=['m.gif','l.gif','b.gif','o.gif','s.gif','m.jpg','l.jpg']
clio_dir=OUT/'pending-04'
clio_dir.mkdir()
checked=[];found=[];hashes=set()
for name in names:
 url=base+name
 item={'url':url,'same_6954_folder':True}
 try:
  r=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Referer':M['official_exact_product_page']},timeout=11)
  item['http_status']=r.status_code
  if r.status_code==200 and len(r.content)<8_000_000:
   pic=Image.open(BytesIO(r.content));pic.load()
   item['native_dimensions']=list(pic.size)
   item['source_sha256']=hashlib.sha256(r.content).hexdigest()
   if min(pic.size)>=450 and item['source_sha256'] not in hashes:
    rgb=ImageOps.exif_transpose(pic).convert('RGB')
    fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
    board=Image.new('RGB',(1080,1080),'white')
    board.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
    save=clio_dir/f"{len(found)+1:02d}-official-mini-{name.replace('.','-')}-QA.jpg"
    board.save(save,'JPEG',quality=92,optimize=True,subsampling=0)
    if save.stat().st_size<2_000_000:
     hashes.add(item['source_sha256'])
     found.append({'file':str(save.relative_to(OUT)),'source_url':url,
        'native_dimensions':list(pic.size),'source_sha256':item['source_sha256'],
        'jpg_sha256':hashfile(save),'retail_approved':False,
        'is_upsampled':max(pic.size)<1080})
 except Exception as e:item['error']=type(e).__name__+':'+str(e)[:120]
 checked.append(item)
if found:
 c=Image.new('RGB',(1410,100+380*((len(found)+3)//4)),'#f0f0ee')
 dc=ImageDraw.Draw(c)
 dc.text((15,12),'v2788 CLIO EXACT 5g PRODUCT ID 6954: VERIFIED SOURCE VARIANTS',font=font,fill='#292929')
 for i,x in enumerate(found):
  with Image.open(OUT/x['file']) as im:tile=im.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
  xx=15+(i%4)*348;yy=50+(i//4)*380
  c.paste(tile,(xx,yy))
  dc.text((xx,yy+327),f"{x['native_dimensions'][0]} x {x['native_dimensions'][1]}",font=font,fill='#333')
 p=OUT/'clio-verified-native-image-proof.jpg'
 c.save(p,'JPEG',quality=84,optimize=True)
 (OUT/'clio-contact.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
report={'version':'v2788','baseline':'v2787',
        'goodal':{'family':'pending-19','alternate_photo_source':str(SOURCE),
                  'three_trial_macro_frames':good,'commercially_approved':False},
        'clio':{'family':'pending-04','product_id':'0000006954',
                'verified_official_product_net_weight':'5g',
                'filename_variants_probed':checked,'distinct_native_photo_sources':found,
                'permission_to_republish':False,'actual_owned_shade_match':False,
                'commercially_approved':False},
        'actual_commercial_sales_approvals':0,
        'existing_11_approved_families_changed':False,
        'existing_55_verified_public_urls_changed':False,
        'previous_v2787_source_files_unchanged':True,
        'final_xlsx_shared':False}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2788','new_goodal_authentic_photo_crop_candidates':len(good),
  'clio_official_file_probes':len(checked),'clio_distinct_native_images':len(found),
  'retail_approved':0}))
