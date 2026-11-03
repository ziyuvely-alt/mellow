#!/usr/bin/env python3
"""3 genuine Pixel Pure toner 200ml photo frames using UNCHANGED official pixels.
Source run v2465 originals only; preserve old two frames; no invented packaging.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json,hashlib
SRC=Path("v2465-pixelpure-toner-official-gallery")
OUT=Path("v2466-pixelpure-toner-three-real-photo-drafts");OUT.mkdir(exist_ok=True)
font=lambda size,bold=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
def render(source,filename,title,detail,top=False):
 img=Image.open(SRC/source).convert("RGB")
 img=img.resize((1080,1080),Image.Resampling.LANCZOS)
 # No square-photo-on-square-background overlay: exact authentic scene is full-bleed.
 # Keep title in a slim unobtrusive translucent band instead of covering packaging.
 lay=Image.new("RGBA",(1080,1080),(0,0,0,0))
 d=ImageDraw.Draw(lay)
 y=36 if top else 904
 d.rounded_rectangle((38,y,1042,y+133),radius=18,fill=(255,255,255,221))
 d.text((64,y+15),"PIXEL PURE",font=font(27,True),fill="#3d5051")
 d.text((64,y+52),title,font=font(37,True),fill="#334e50")
 d.text((64,y+99),detail,font=font(20),fill="#55646b")
 result=Image.alpha_composite(img.convert("RGBA"),lay).convert("RGB")
 f=OUT/filename;result.save(f,"JPEG",quality=92,subsampling=0,optimize=True)
 content=f.read_bytes();assert len(content)<2_000_000 and Image.open(f).size==(1080,1080)
 return {"file":f.name,"source_file":source,"bytes":len(content),"sha256":hashlib.sha256(content).hexdigest(),"dimensions":[1080,1080],"status":"SOURCE_PHOTO_RENDERED_QA_HOLD"}
items=[
 render("original-02.png","03-pouring-liquid-original-photo.jpg","A CLOSER LOOK","Original product texture scene | 200 mL",top=True),
 render("original-03.jpg","04-bottle-angles-original-photo.jpg","BOTTLE DETAILS","Original bottle photography | 200 mL",top=False),
 render("original-05.jpg","05-package-original-photo.jpg","PRODUCT PRESENTATION","Official bottle and package photo | 200 mL",top=True)
]
manifest={"date":"2026-11-04","family":"pending-27","product":"PIXEL PURE Soothing Ampoule Toner 200 mL","existing_2_frames_untouched":True,"new_original_photographic_frames":3,"files":items,"source_run":41682843250,"source_artifact":13254420828,"package_edition_physical_stock_approved":False,"photo_reuse_rights_verified":False,"actual_MK_original_logo_applied":False,"published":False,"new_public_urls":0,"spreadsheet_shared":False,"note":"Source scenes are official product page images, not edited or fabricated product photographs; final visual/logo/rights and overlap QA required."}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"count":len(items),"new_files":[x["file"] for x in items]}))
