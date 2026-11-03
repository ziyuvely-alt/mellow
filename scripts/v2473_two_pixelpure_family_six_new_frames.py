#!/usr/bin/env python3
"""Make only new image drafts for pending-26 cleanser 145ml and pending-30 serum 50ml.
Old customer JPG candidates remain untouched. Source image pixels are real and not fabricated.
Never publish without rights, exact stock-package and original shop logo checks.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
ROOT=Path("v2473-pixelpure-two-family-new-six")
F=lambda n,b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(dest,im,source,role):
 dest.parent.mkdir(parents=True,exist_ok=True)
 im.convert("RGB").save(dest,"JPEG",quality=92,subsampling=0,optimize=True)
 data=dest.read_bytes()
 assert len(data)<2000000 and Image.open(dest).size==(1080,1080)
 return {"path":str(dest.relative_to(ROOT)),"source":source,"role":role,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"size":[1080,1080],"status":"REVIEW_ONLY_ORIGINAL_LOGO_AND_RIGHTS_HOLD"}
def photo(family,source,id,title,subtitle,placement):
 path=Path("inputs")/family/source
 photo=Image.open(path).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
 # Entire canvas is a genuine photograph (not rectangle pasted on white).
 band=Image.new("RGBA",(1080,1080),(0,0,0,0));d=ImageDraw.Draw(band)
 yy=30 if placement=="top" else 915
 d.rounded_rectangle((26,yy,1054,yy+136),radius=18,fill=(255,255,255,220))
 d.text((52,yy+12),"PIXEL PURE",font=F(26,True),fill="#343f44")
 d.text((52,yy+47),title,font=F(36,True),fill="#3c4c50")
 d.text((52,yy+94),subtitle,font=F(22),fill="#55666b")
 im=Image.alpha_composite(photo.convert("RGBA"),band).convert("RGB")
 return save(ROOT/family/id,im,source,"GENUINE_PHOTO")
def facts(family,id,title,details):
 im=Image.new("RGB",(1080,1080),"#f7f6f4");d=ImageDraw.Draw(im)
 d.text((78,68),"PIXEL PURE",font=F(51,True),fill="#43595c")
 d.text((78,162),title,font=F(49,True),fill="#374c4d")
 d.line((78,265,1002,265),fill="#bdcece",width=3)
 for i,(label,value) in enumerate(details):
  y=323+i*174
  d.rounded_rectangle((76,y,1002,y+137),radius=26,fill=["#e1eae7","#f1e4e6","#e5e9ef"][i])
  d.text((108,y+18),label,font=F(27),fill="#5e7475")
  d.text((108,y+65),value,font=F(36,True),fill="#354d50")
 d.text((78,974),"Check the exact label on your purchased product.",font=F(23),fill="#596b6d")
 return save(ROOT/family/id,im,"verified stock product name / volume only","FACTS_ONLY")
r=[]
r.append(photo("pending-26","original-02.jpg","03-product-texture-photo.jpg","GEL-TO-FOAM CLEANSER","Original genuine brand scene | 145 mL","bottom"))
r.append(photo("pending-26","original-03.jpg","04-bottle-and-carton-photo.jpg","BOTTLE + CARTON","Original package photo | 145 mL","bottom"))
r.append(photo("pending-26","original-04.jpg","05-bottle-angle-photo.jpg","PRODUCT ANGLES","Original genuine product scene | 145 mL","bottom"))
r.append(photo("pending-30","original-01.jpg","03-serum-bottle-photo.jpg","AURA RADIANCE SERUM","Original bottle photo | 50 mL","bottom"))
r.append(photo("pending-30","original-02.jpg","04-serum-group-photo.jpg","MULTI-ANGLE VIEW","Authentic serum bottle photography | 50 mL","bottom"))
r.append(facts("pending-30","05-product-facts-50ml.jpg","AURA RADIANCE SERUM",[("BRAND","PIXEL PURE"),("PRODUCT TYPE","Facial serum"),("NET CONTENT","50 mL")]))
manifest={"date":"2026-11-04","families":["pending-26","pending-30"],"old_existing_jpg_recreated":0,"new_files":r,"source_artifacts":[13255125987,13253692437],"original_shop_MK_logo_applied":False,"marketing_photo_rights_verified":False,"actual_inventory_package_edition_verified":False,"published_URLs_added":0,"final_QA_approved":False,"excel_shared":False}
(ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"files_created":len(r),"families":["pending-26","pending-30"]}))
