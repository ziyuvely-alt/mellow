#!/usr/bin/env python3
"""v2747 photo-only alternate source salvage: MISSHA Magic Cushion Cover Lasting
shade N23, image 02 from previously saved QA source.
NO fake photos, no upscaling claims, no duplicate shade attribution 21/25/27.
Only source-alpha QA; no retail approval or URL edits.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import cv2,numpy as np,hashlib,json,base64
R=Path('qa-review')
SOURCE=R/'v2675-missha-two-five-frame-photo-sets/pending-01/02-prior-original-byte-identical-QA.jpg'
OUT=R/'v2747-missha-coverlasting-23-source02-round-compact-qa'
assert SOURCE.exists() and not OUT.exists()
OUT.mkdir(parents=True)
with Image.open(SOURCE) as source:
    source.load()
    assert source.format=='JPEG' and source.size==(1080,1080)
    rgb=source.convert('RGB')
arr=np.array(rgb)
grey=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
detected=cv2.HoughCircles(cv2.medianBlur(grey,9),cv2.HOUGH_GRADIENT,
    dp=1.1,minDist=190,param1=115,param2=30,minRadius=155,maxRadius=275)
options=[]
if detected is not None:
    for xx,yy,rr in detected[0]:
        x,y,r=round(float(xx)),round(float(yy)),round(float(rr))
        if 645<=x<=920 and 390<=y<=835 and x-r>10 and x+r<1070 and y-r>10 and y+r<1070:
            # Product circle centered on the right. This is not proof of 23-shade ownership.
            options.append((abs(x-810)/100 + abs(y-635)/130 + abs(r-205)/100,x,y,r))
options.sort()
if options and options[0][0]<=3.3:
    _,cx,cy,r=options[0];mode='opencv_detected_circle_requires_visual_qa'
else:
    cx,cy,r=815,635,205;mode='manual_source02_single_disc_hypothesis'
assert cx+r<1080 and cy+r<1080 and cx-r>=0 and cy-r>=0
mask=Image.new('L',(1080,1080),0)
d=ImageDraw.Draw(mask)
d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(0.7))
bbox=mask.getbbox()
assert bbox
photo=rgb.convert('RGBA')
photo.putalpha(mask)
product=photo.crop(bbox)
png=OUT/'01-original-pink-compact-N23-transparent-QA.png'
product.save(png,optimize=True)
bg=Image.new('RGB',(1080,1080),'white')
fit=ImageOps.contain(product,(885,885),Image.Resampling.LANCZOS)
bg.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit)
jpg=OUT/'01-original-pink-compact-N23-1080-QA.jpg'
bg.save(jpg,'JPEG',quality=91,optimize=True,subsampling=0)
assert jpg.stat().st_size<2_000_000
with Image.open(jpg) as check:
    check.load()
    assert check.format=='JPEG' and check.size==(1080,1080)
# Combined proof: preserve full original, mask overlay, clear product.
outline=rgb.copy();q=ImageDraw.Draw(outline)
q.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#d84231',width=5)
checker=Image.new('RGBA',(1080,1080),'white');dc=ImageDraw.Draw(checker)
for y in range(0,1080,48):
 for x in range(0,1080,48):
  if (x//48+y//48)%2:dc.rectangle((x,y,x+47,y+47),fill='#e5e5e5')
checker.alpha_composite(photo)
contact=Image.new('RGB',(1690,630),'#f0f0ee')
label=ImageDraw.Draw(contact)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(F,22)
label.text((16,14),'v2747 MIS SHA N23 alternate genuine photo02 | actual round-alpha QA only',font=font,fill='#333333')
for i,(name,im) in enumerate([
 ('1 SOURCE / red outline proposal',outline),
 ('2 CUTOUT / checkerboard transparency',checker.convert('RGB')),
 ('3 SOURCE-PIXELS ONLY / 1080 JPG',bg)]):
 x=15+i*562
 tile=im.resize((520,520),Image.Resampling.LANCZOS)
 contact.paste(tile,(x,60))
 label.text((x,589),name,font=font,fill='#2f2e2d')
proof=OUT/'v2747-three-view-source-silhouette.jpg'
contact.save(proof,'JPEG',quality=83,optimize=True)
(OUT/'v2747-proof.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={
 'version':'v2747','baseline':'v2746',
 'family':'pending-01','product':'MISSHA Magic Cushion Cover Lasting',
 'shade':'N23 ONLY','source':str(SOURCE),'source_sha256':sha(SOURCE),
 'source_01_failed_cutout_reused':False,'source_02_unchanged':True,
 'silhouette_method':mode,'circle_xyr':[cx,cy,r],
 'hough_candidates_tested':[[round(z[0],2),*z[1:]] for z in options[:5]],
 'png':png.name,'jpg':jpg.name,'png_sha256':sha(png),'jpg_sha256':sha(jpg),
 'jpg_bytes':jpg.stat().st_size,
 'shades21_25_27_not_generated':True,
 'photo_commercial_rights_verified':False,
 'owned_N23_KR_packaging_match_verified':False,
 'round_original_MK_logo_verified':False,
 'status':'ACTUAL_PHOTO_ALPHA_CREATED_VISUAL_QA_REQUIRED',
 'new_retail_approval':False,
 'approved_old_11_families_unchanged':True,
 'approved_55_public_urls_unchanged':True,
 'final_spreadsheet_shared':False}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2747','source':'N23 frame02','method':mode,'circle':[cx,cy,r], 'saved_png_jpg':True, 'retail_approved':False}))
