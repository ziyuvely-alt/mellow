#!/usr/bin/env python3
"""v2718 new foreground segmentation batch, ONLY four families not processed
in v2711-17. Retain source pixels only; reject kits and stock variants in manual QA.
Commercial rights remain unverified and never auto-release.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import json,base64,hashlib
ROOT=Path("qa-review")
OUT=ROOT/"v2718-four-unprocessed-clio-missha-real-photo-cutouts"
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 {"family":"pending-05","folder":"v2682-seven-remaining-five-JPG-reviews",
  "brand":"CLIO","name":"Kill Cover Founwear Cushion Mini",
  "crop":(142,159,938,963),
  "hold":"Confirm exactly mini SKU; do not include refill or gift from kit"},
 {"family":"pending-07","folder":"v2682-seven-remaining-five-JPG-reviews",
  "brand":"CLIO","name":"Kill Cover Mesh Blur Cushion",
  "crop":(154,159,936,966),
  "hold":"Full-size vs promotional gift / shade and edition unverified"},
 {"family":"pending-12","folder":"v2678-missha-clio-two-five-JPG-sets",
  "brand":"MISSHA","name":"PDRN NAD+ Renew Peel Shot 25",
  "crop":(156,160,929,959),
  "hold":"Actual photographed 15mL vs inventory historical 15g mismatch, never publish without resolution"},
 {"family":"pending-13","folder":"v2676-missha-pdrn-serum-fiveframe-qa",
  "brand":"MISSHA","name":"PDRN Firming Repair Serum 30mL",
  "crop":(178,146,926,963),
  "hold":"Exact stock generation and same 30mL single item must be proven"}
]
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session('isnet-general-use')
results=[]
for c in CASES:
 srcs=list((ROOT/c["folder"]/c["family"]).glob('01-*.jpg'))
 assert len(srcs)==1,(c["family"],srcs)
 src=srcs[0]
 with Image.open(src) as im:
  im.load();assert im.format=='JPEG' and im.size==(1080,1080)
  roi=im.convert('RGBA').crop(c["crop"])
 row={'family':c['family'],'product':c['name'],'source':str(src),
      'source_sha256':sha(src),'crop':list(c['crop']),'stock_hold':c['hold'],
      'status':'HOLD_TECHNICAL_OR_VISUAL','retail_approved':False}
 try:
  product=remove(roi,session=session,alpha_matting=True,
     alpha_matting_foreground_threshold=230,
     alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
  assert product.mode=='RGBA'
  channel=product.getchannel('A')
  bbox=channel.getbbox()
  assert bbox
  cov=sum(x>=128 for x in channel.getdata())/(product.width*product.height)
  if not(.025<cov<.82 and bbox[2]-bbox[0]>100 and bbox[3]-bbox[1]>190):
   raise ValueError(f'Not plausible product mask: cover={cov:.4f}, box={bbox}')
  cut=product.crop(bbox)
  folder=OUT/c['family'];folder.mkdir()
  png=folder/'01-actual-transparent-product-foreground-QA.png'
  cut.save(png,optimize=True)
  jpg=folder/'01-actual-product-cutout-square-1080-QA.jpg'
  white=Image.new('RGB',(1080,1080),'white')
  d=ImageDraw.Draw(white)
  d.rounded_rectangle((55,53,1025,1027),radius=34,outline='#ece6e9',width=2)
  d.text((92,97),c['brand'],font=ft(43,True),fill='#353136')
  n=30
  while d.textbbox((0,0),c['name'],font=ft(n))[2]>885 and n>17:n-=1
  d.text((92,165),c['name'],font=ft(n),fill='#766d73')
  fit=ImageOps.contain(cut,(857,774),Image.Resampling.LANCZOS)
  xy=((1080-fit.width)//2,218+(776-fit.height)//2)
  white.paste(fit,xy,fit)
  d.text((92,994),'REAL SOURCE PHOTO SEGMENTATION | QA ONLY',font=ft(18),fill='#979095')
  white.save(jpg,'JPEG',quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as test:
   test.load();assert test.format=='JPEG' and test.size==(1080,1080)
  row.update({'status':'FOREGROUND_JPG_PNG_RENDERED_VISUAL_REVIEW_REQUIRED',
              'alpha_coverage':round(cov,4),'bbox':list(bbox),
              'transparent_png':str(png.relative_to(OUT)),
              'jpg':str(jpg.relative_to(OUT)),'jpg_sha256':sha(jpg)})
 except Exception as e:
  row.update({'status':'HOLD_BAD_SEGMENTATION','error_type':type(e).__name__,
              'error':str(e)[:200]})
 results.append(row)
for page in range(2):
 canvas=Image.new('RGB',(1530,1030),'#f0f0ef')
 d=ImageDraw.Draw(canvas)
 d.text((14,16),f'v2718 FOUR UNSEGMENTED FAMILIES | PAGE {page+1} | QA ONLY',font=ft(25,True),fill='#282828')
 for i,row in enumerate(results[page*2:(page+1)*2]):
  y=58+i*477
  with Image.open(row['source']) as im:
   old=im.convert('RGB').resize((420,420),Image.Resampling.LANCZOS)
  canvas.paste(old,(16,y))
  d.text((456,y+17),row['family'],font=ft(32,True),fill='#333')
  d.text((456,y+72),row['status'],font=ft(18),fill='#666')
  if row.get('jpg'):
   with Image.open(OUT/row['jpg']) as im:
    new=im.convert('RGB').resize((420,420),Image.Resampling.LANCZOS)
   canvas.paste(new,(1090,y))
 p=OUT/f'v2718-photo-visual-page-{page+1}.jpg'
 canvas.save(p,'JPEG',quality=82,optimize=True)
 (OUT/f'v2718-visual-page-{page+1}.b64.txt').write_text(base64.b64encode(p.read_bytes()).decode())
report={'version':'v2718','baseline':'v2717','new_families_attempted':len(results),
        'actual_photo_alpha_PNG_JPG_pairs_saved':sum(bool(x.get('jpg')) for x in results),
        'new_retail_approvals':0,'photo_redistribution_permission_proven':False,
        'owned_stock_variants_verified':False,'original_approved_MK_logo_verified':False,
        'prior_11_approved_families_modified':False,
        'prior_55_published_URLs_changed':False,
        'prior_saved_original_photo_JPGs_mutated':0,
        'no_final_excel_shared':True,'products':results}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'families':4,'saved_pairs':report['actual_photo_alpha_PNG_JPG_pairs_saved'],
  'statuses':[x['status'] for x in results],'approved_for_sale':0}))
