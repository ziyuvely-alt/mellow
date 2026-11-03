from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
O=Path("v2459-output");O.mkdir(exist_ok=True)
def F(s,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",s)
def T(d,p,t,s,w,b=False,c="#23312e"):
 while d.textbbox((0,0),t,font=F(s,b))[2]>w:s-=1
 d.text(p,t,font=F(s,b),fill=c)
def render(name,product,title,sub,bg,rows,foot):
 a=Image.new("RGB",(1080,1080),bg);d=ImageDraw.Draw(a)
 d.rectangle((80,100,1000,103),fill="#b7c8bd")
 T(d,(82,54),"MELLOWKR  /  PRODUCT GUIDE",24,800,True)
 T(d,(82,139),product.upper(),29,895,True)
 T(d,(82,244),title,68,920,True)
 T(d,(82,338),sub,28,900,False,"#52645c")
 for i,(num,h,detail) in enumerate(rows):
  y=430+158*i
  d.rounded_rectangle((82,y,998,y+135),radius=25,fill="#e7eee8" if bg=="#f6f8f3" else "#f8e9e4")
  d.rounded_rectangle((106,y+24,164,y+82),radius=19,fill="#cfded2" if bg=="#f6f8f3" else "#f0cdbf")
  T(d,(122,y+30),num,30,52,True)
  T(d,(187,y+24),h,34,760,True)
  T(d,(187,y+72),detail,25,750,False,"#52645c")
 d.line((82,934,998,934),fill="#bccac1",width=3)
 T(d,(82,960),foot,22,910,False,"#52645c")
 path=O/name;a.save(path,"JPEG",quality=92,subsampling=0,optimize=True)
 b=path.read_bytes();im=Image.open(path);assert im.size==(1080,1080) and im.format=="JPEG" and len(b)<2000000
 return dict(filename=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),size=[1080,1080],status="FINAL_QA_HOLD_STOCK_AND_ORIGINAL_MK",public=False)
x=render("pending-08-shade-option-check-corrected.jpg","Peripera Mood Glowy Tint","CHECK YOUR SHADE","Confirm your selected option before checkout.","#f9f4f1",[("01","SHADE NUMBER","Use the number shown in the listing option."),("02","SHADE NAME","Check the full option name, not just the number."),("03","PRODUCT EDITION","Match the option to the product photo.")],"Selection guide only. Not an official shade chart.")
y=render("pending-19-package-check-corrected.jpg","Goodal Green Tangerine Vita C Cream Alpha","PACKAGE DETAILS","Product identification guide.","#f6f8f3",[("01","PRODUCT NAME","Green Tangerine Vita C Cream Alpha"),("02","NET CONTENT","50 mL cream. Single product."),("03","PACKAGE CHECK","Match the purchased product edition.")],"No unverified treatment or regulatory claims.")
(O/"manifest.json").write_text(json.dumps({"source_run":41676483713,"changes":[x,y],"previous_jpg_overwritten":0,"prior_public_55_untouched":True,"new_url_verified":0,"excel_shared":False},indent=2))
