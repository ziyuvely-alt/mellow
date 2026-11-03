#!/usr/bin/env python3
"""Create only pending-18 additional frames 03-05. No existing JPG regenerated.
Preserve genuine product image exact; final licensed/masked/MK-logo QAs are held.
"""
from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import hashlib,json
src=Path("v2481-drg-brightening-up-sun-50-source")
out=Path("v2482-drg-brightening-sun-three-JPG");out.mkdir(exist_ok=True)
font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(name,im,scene):
 p=out/name;im.convert("RGB").save(p,"JPEG",quality=92,subsampling=0,optimize=True);raw=p.read_bytes()
 assert len(raw)<2000000 and Image.open(p).size==(1080,1080)
 return {"filename":name,"source":scene,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"size":[1080,1080],"status":"JPG_CREATED_FINAL_STOCK_AND_RIGHTS_QA_HOLD"}
def composite(source,name,subtitle,kind):
 im=Image.open(src/source).convert("RGB")
 # No artificial cutout; original product image placed against color-matched white to avoid a visible rectangle.
 # ImageOps.contain preserves full label and carton.
 background=Image.new("RGB",(1080,1080),"white")
 cap=ImageOps.contain(im,(970,830),method=Image.Resampling.LANCZOS)
 background.paste(cap,((1080-cap.width)//2,135))
 d=ImageDraw.Draw(background)
 d.text((68,36),"Dr.G",font=font(49,True),fill="#513626")
 d.text((68,88),"BRIGHTENING UP SUN+",font=font(30,True),fill="#513626")
 d.line((68,996,1012,996),fill="#c1baa9",width=2)
 d.text((68,1010),subtitle,font=font(21),fill="#56483c")
 return save(name,background,kind)
files=[]
files.append(composite("eland-single-tube.jpg","03-exact-single-tube-photo.jpg","True original 50 mL product photo | seller stock edition check pending","single tube 750px source"))
files.append(composite("gmarket-pack.jpg","04-bottle-and-box-source.jpg","Actual tube and retail box | low-source-resolution QA HOLD","tube+box 400px source"))
im=Image.new("RGB",(1080,1080),"#f6f5f1");d=ImageDraw.Draw(im)
d.text((70,80),"Dr.G",font=font(64,True),fill="#4a3b31")
d.text((70,183),"BRIGHTENING UP SUN+",font=font(53,True),fill="#4a3b31")
d.text((70,262),"PRODUCT INFORMATION",font=font(36),fill="#716254")
for i,(label,value) in enumerate([("PRODUCT","Brightening Up Sun Plus"),("NET CONTENT","50 mL"),("FORMAT","Facial sunscreen")]):
 y=380+170*i
 d.rounded_rectangle((78,y,1002,y+132),radius=25,fill=["#eee7df","#ebece7","#eee7df"][i])
 d.text((108,y+17),label,font=font(25),fill="#7a6b5c")
 d.text((108,y+59),value,font=font(36,True),fill="#4b4237")
d.text((80,960),"Check the packaging and ingredient label on your purchased item.",font=font(20),fill="#6b635b")
files.append(save("05-no-claims-product-information.jpg",im,"official Dr.G product name and net content"))
(out/"manifest.json").write_text(json.dumps({"date":"2026-11-04","family_id":"pending-18","existing_old_frames_recreated":0,"new_jpg":files,"source_run_id":41686720559,"source_artifact_id":13254249352,"needs_higher_resolution_package_photo":True,"commercial_rights_verified":False,"actual_MK_logo_applied":False,"actual_stock_edition_matched":False,"published":False,"new_public_urls":0,"excel_shared":False},indent=2)+"\n")
print(json.dumps({"files":len(files),"lowres_hold":"04-bottle-and-box-source.jpg"}))
