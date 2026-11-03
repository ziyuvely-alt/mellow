from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import shutil,json,hashlib
S=Path('v2427-source');O=Path('v2427b-output')
shutil.copytree(S,O,dirs_exist_ok=True)
source=Image.open(S/'obge-three-shades-authentic-source.jpg').convert('RGB')
w,h=source.size
bg=Image.new('RGB',(1080,1080),(249,246,242))
d=ImageDraw.Draw(bg)
reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,b=False: ImageFont.truetype(bold if b else reg,n)
d.text((56,64),'OBgE PERFECT COVER CUSHION',font=F(43,True),fill=(45,54,48))
d.text((56,132),'3 SHADES  |  15 g',font=F(29),fill=(80,80,73))
d.line((56,195,1020,195),fill=(172,166,146),width=3)
for i,(no,name,rect) in enumerate([('1','Ivory',(7,105,166,219)),('2','Beige',(177,105,336,219)),('3','Sand',(346,105,505,219))]):
 box=tuple(int(z*w/512) if k%2==0 else int(z*h/512) for k,z in enumerate(rect))
 crop=ImageOps.contain(source.crop(box),(306,302),Image.Resampling.LANCZOS)
 x=56+i*341
 bg.paste(crop,(x+(307-crop.width)//2,281+(300-crop.height)//2))
 d.rounded_rectangle((x,655,x+308,792),radius=20,fill=(236,226,215))
 d.text((x+18,681),'No. '+no,font=F(35,True),fill=(49,51,47))
 d.text((x+18,736),name,font=F(28),fill=(49,51,47))
d.line((56,860,1020,860),fill=(178,168,152),width=2)
d.text((56,898),'1 Ivory   /   2 Beige   /   3 Sand',font=F(29),fill=(69,69,63))
p=O/'OBGE_3shade_clean_QA_V2427b.jpg'
bg.save(p,'JPEG',quality=91,optimize=True)
assert Image.open(p).size==(1080,1080) and p.stat().st_size<2000000
first=S/'OBGE_Perfect_Cover_Cushion_3shade_actual_photo_QA_V2427.jpg'
assert hashlib.sha256(first.read_bytes()).digest()!=hashlib.sha256(p.read_bytes()).digest()
proof=json.loads((S/'summary.json').read_text())
proof.update({'version':'2.4.27b','extra_corrected_real_photo_chart_JPG':1,'source_three_swatches_photo_sha256':hashlib.sha256((S/'obge-three-shades-authentic-source.jpg').read_bytes()).hexdigest(),'clean_chart_JPG_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'initial_EN_four_jpg_unchanged':4,'commercial_license_verified':False,'official_renewed_package_edition_verified':False,'shade_chart_sales_approved':0,'existing_public_urls_changed':0})
(O/'summary.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False))
print('SUMMARY',json.dumps(proof,ensure_ascii=False),flush=True)
