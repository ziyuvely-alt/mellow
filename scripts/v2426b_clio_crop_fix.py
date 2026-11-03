from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import shutil,hashlib,json
s=Path('v2426-input');o=Path('v2426b-output');shutil.copytree(s,o,dirs_exist_ok=True)
a=Image.open(s/'source-evidence-clio-library.jpg').convert('RGB');W,H=a.size
p=Image.new('RGB',(1080,1080),(249,246,242));d=ImageDraw.Draw(p)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,bold=False:ImageFont.truetype(b if bold else f,n)
d.text((60,59),'CLIO KILL COVER',font=F(47,True),fill=(52,53,49));d.text((60,124),'Mesh Glow Essential Cushion Mini | 5 g',font=F(27),fill=(70,71,66))
d.line((60,190,1014,190),fill=(209,179,172),width=3);d.text((60,218),'SHADE GUIDE / 3 OFFICIAL OPTIONS',font=F(27,True),fill=(100,76,82))
for i,(num,name,box) in enumerate([('21C','Lingerie',(160,294,305,378)),('21N','Linen',(385,294,532,378)),('23N','Ginger',(380,420,532,509))]):
 x=58+i*339;region=a.crop((int(box[0]*W/600),int(box[1]*H/600),int(box[2]*W/600),int(box[3]*H/600)));region=ImageOps.contain(region,(290,210))
 p.paste(region,(x+(305-region.width)//2,340+(210-region.height)//2));d.rounded_rectangle((x,582,x+305,730),radius=20,fill=(238,232,226));d.text((x+18,606),num,font=F(39,True),fill=(49,50,46));d.text((x+18,669),name,font=F(30),fill=(49,50,46))
d.line((60,802,1015,802),fill=(201,190,179),width=2);d.text((60,836),'Select one shade per cushion.',font=F(31),fill=(78,75,70));d.text((60,895),'21C Lingerie / 21N Linen / 23N Ginger',font=F(25),fill=(78,75,70))
t=o/'CLIO_Mini_3shade_actual_source_QA_CLEAN_V2426b.jpg';p.save(t,'JPEG',quality=92,optimize=True)
assert Image.open(t).size==(1080,1080) and t.stat().st_size<2000000
j=json.loads((o/'summary.json').read_text());j['v2426b_visual_crop_fix_JPG']=1;j['actual_source_license_approved']=False;j['official_shade_chart_sales_approved']=0;(o/'summary.json').write_text(json.dumps(j,indent=2))
print('REVISED',t)
