#!/usr/bin/env python3
"""Create only the missing informational frames for pending-28; never overwrite prior 2 original photo frames."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
out=Path("v2462-pending28-new-three");out.mkdir(exist_ok=True)
def font(size,bold=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
def centered(d,text,y,size,bold=False,color="#30443e"):
 ft=font(size,bold);w=d.textbbox((0,0),text,font=ft)[2];d.text(((1080-w)//2,y),text,font=ft,fill=color)
def make(key,title,subtitle,bullets,kind):
 im=Image.new("RGB",(1080,1080),"#f8f6f3");d=ImageDraw.Draw(im)
 d.rectangle((0,0,1080,22),fill="#7d9b8f")
 d.text((72,74),"PIXEL PURE",font=font(38,True),fill="#425e59")
 d.text((72,124),"Glow Cleansing Serum Pad",font=font(25),fill="#637b76")
 d.line((72,187,1008,187),fill="#bbc9c2",width=3)
 centered(d,title,244,52,True)
 centered(d,subtitle,320,24)
 if kind=="steps":
  for i,(h,v) in enumerate(bullets):
   y=423+i*166
   d.rounded_rectangle((84,y,996,y+135),radius=22,fill=["#e1ece5","#f2e2df","#e7e9ef"][i])
   d.rounded_rectangle((106,y+28,167,y+90),radius=20,fill="#fffdfb")
   d.text((125,y+40),str(i+1),font=font(31,True),fill="#50635b")
   d.text((196,y+26),h,font=font(32,True),fill="#30443e")
   d.text((196,y+77),v,font=font(22),fill="#566f66")
 elif kind=="facts":
  for i,(h,v) in enumerate(bullets):
   x=84+i*313
   d.rounded_rectangle((x,444,x+289,721),radius=28,fill=["#e1ece5","#f2e2df","#e7e9ef"][i])
   d.text((x+25,480),h,font=font(27,True),fill="#425e59")
   d.text((x+25,550),v,font=font(36,True),fill="#30443e")
 elif kind=="verify":
  for i,(h,v) in enumerate(bullets):
   y=420+159*i
   d.rounded_rectangle((84,y,996,y+133),radius=22,outline="#b6cabe",width=4)
   d.ellipse((110,y+36,154,y+80),fill="#a7c2b5")
   d.text((188,y+21),h,font=font(32,True),fill="#30443e")
   d.text((188,y+72),v,font=font(23),fill="#60756a")
 d.line((74,943,1006,943),fill="#bcc9be",width=2)
 centered(d,"Korean stock listing information | Verify package details",964,20)
 p=out/key;im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 raw=p.read_bytes();assert len(raw)<2_000_000 and Image.open(p).size==(1080,1080)
 return {"file":key,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"format":"JPEG","size":"1080x1080","status":"NEW_JPG_PREPARED_FINAL_VISUAL_QA_HOLD"}
cards=[
 make("03-how-to-check-instructions.jpg","CLEANSING PAD ROUTINE","Follow the directions printed on your purchased product.",[("PREPARE","Open the jar and take out one pad."),("CLEANSE","Use the pad as described on the package."),("FINISH","Follow the package's rinse guidance.")],"steps"),
 make("04-product-format.jpg","CLEANSING SERUM PAD","Pre-soaked pad format in a jar.",[("FORMAT","Serum pad"),("COUNT","70 pads"),("VOLUME","210 mL")],"facts"),
 make("05-pack-check.jpg","CHECK YOUR PACKAGE","Verify the exact product you receive.",[("PRODUCT NAME","Glow Cleansing Serum Pad"),("PACKAGE CONTENT","70 pre-soaked pads"),("NET CONTENT","210 mL on the existing stock listing")],"verify")
]
manifest={"date":"2026-11-04","family_id":"pending-28","existing_photo_frames_preserved":2,"new_info_jpg_count":3,"new_image_files":cards,"reference_product_page":"https://pixelpure.com/product/detail.html?product_no=23","net_content_basis":"Seller stock record for 210mL; brand official listing confirms 70 pads","commercial_photo_rights_pending":True,"original_MK_logo_binary_pending":True,"published_new_url":0,"full_family_qa_approved":False,"do_not_merge_excel":True}
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"files":[x["file"] for x in cards],"count":len(cards)}))
