#!/usr/bin/env python3
"""v2748 independent N21 carton/compact photo cutout from existing PHOTO01.

DO NOT rework v2747 N23 or invent N25/N27 colors. N21 SKU eligibility has
historical option-list conflict and stays QA-HOLD even if photo circle good.
Original image pixels are unmodified; transparent round silhouette only.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageOps,ImageFont
import numpy as np,cv2,hashlib,json,base64
R=Path('qa-review')
src=R/'v2675-missha-two-five-frame-photo-sets/pending-01/01-prior-original-byte-identical-QA.jpg'
out=R/'v2748-missha-coverlasting-21-source01-round-compact-only'
assert src.is_file() and not out.exists()
out.mkdir(parents=True)
with Image.open(src) as im:
 im.load();assert im.format=='JPEG' and im.size==(1080,1080)
 rgb=im.convert('RGB')
arr=np.array(rgb)
g=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
hough=cv2.HoughCircles(cv2.medianBlur(g,9),cv2.HOUGH_GRADIENT,
 dp=1.15,minDist=180,param1=116,param2=29,minRadius=165,maxRadius=310)
candidates=[]
if hough is not None:
 for xx,yy,rr in hough[0]:
  x,y,rad=round(float(xx)),round(float(yy)),round(float(rr))
  # Circle on right of box, in this independent N21 source photo
  if 570<=x<=925 and 235<=y<=870 and x-r>=12 and x+rad<=1068 and y-r>=12 and y+rad<=1068:
   score=abs(x-800)/95+abs(y-560)/125+abs(rad-245)/100
   candidates.append((round(score,3),x,y,rad))
candidates.sort()
if candidates and candidates[0][0]<3.5:
 _,cx,cy,r=candidates[0];method='hough_circle_on_actual_source'
else:
 cx,cy,r=805,575,246;method='conservative_manual_circle_needs_visual_QA'
assert cx-r>=0 and cy-r>=0 and cx+r<=1080 and cy+r<=1080
mask=Image.new('L',(1080,1080),0)
md=ImageDraw.Draw(mask)
md.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(.7))
bbox=mask.getbbox()
cut=rgb.convert('RGBA')
cut.putalpha(mask)
cut=cut.crop(bbox)
png=out/'01-missha-N21-actual-compact-transparent-QA.png'
cut.save(png,optimize=True)
white=Image.new('RGB',(1080,1080),'white')
fit=ImageOps.contain(cut,(880,880),Image.Resampling.LANCZOS)
white.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit)
jpg=out/'01-missha-N21-real-compact-1080-QA.jpg'
white.save(jpg,'JPEG',quality=92,optimize=True,subsampling=0)
with Image.open(jpg) as verify:
 verify.load();assert verify.format=='JPEG' and verify.size==(1080,1080)
assert jpg.stat().st_size<2000000
# Picture for manual human quality adjudication and N21 source carton
outlined=rgb.copy()
od=ImageDraw.Draw(outlined)
od.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#d63f35',width=5)
check=Image.new('RGBA',(1080,1080),'white');cd=ImageDraw.Draw(check)
for y in range(0,1080,48):
 for x in range(0,1080,48):
  if (x//48+y//48)%2: cd.rectangle((x,y,x+47,y+47),fill='#e5e5e5')
full=rgb.convert('RGBA');full.putalpha(mask)
check.alpha_composite(full)
canvas=Image.new('RGB',(1690,650),'#f1f0ef')
d=ImageDraw.Draw(canvas)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
d.text((16,15),'v2748 Original photo01 N21 - real compact-only alpha  |  SHADE OPTION HOLD',font=f,fill='#303030')
for i,(im,label) in enumerate([(outlined,'01 genuine N21 carton+compact'),(check.convert('RGB'),'02 transparent against checker'),(white,'03 original compact pixels only')]):
 x=15+560*i
 canvas.paste(im.resize((515,515),Image.Resampling.LANCZOS),(x,70))
 d.text((x,607),label,font=f,fill='#333333')
proof=out/'v2748-N21-photo-alpha-comparison.jpg'
canvas.save(proof,'JPEG',quality=83,optimize=True)
(out/'v2748-proof.b64.txt').write_text(base64.b64encode(proof.read_bytes()).decode())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest={
 'version':'v2748','baseline':'v2747',
 'family':'pending-01','product':'MISSHA Magic Cushion Cover Lasting',
 'photo_label':'N21 carton in original photographic artwork',
 'source_path':str(src),'source_sha256':sha(src),
 'actual_photo_N23_from_v2747_reused':False,
 'selected_circle':[cx,cy,r], 'method':method,
 'hough_candidates':[list(x) for x in candidates[:5]],
 'source_alpha_png':png.name,'1080_jpg':jpg.name,
 'png_sha256':sha(png),'jpg_sha256':sha(jpg),'jpg_bytes':jpg.stat().st_size,
 'N21_exact_user_stock_option_eligible':'UNVERIFIED_HISTORICAL_OPTION_CONFLICT',
 'use_for_shade23_25_27':False,'display_product_swatch_simulation':False,
 'photo_redistribution_rights_verified':False,
 'actual_original_MK_logo_verified':False,
 'new_retail_approvals':0,
 'published_55_urls_untouched':True,'eleven_approved_product_families_unchanged':True,
 'final_xlsx_shared':False,
 'visual_QA':'NOT_YET_REVIEWED'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':'v2748','real_N21_png_jpg_saved':True,'mode':method,'circle':[cx,cy,r],'retail_approved':False}))
