#!/usr/bin/env python3
"""Compose exactly 3 NEW image drafts for pending-09 from recovered previous action artifact.
Do not recreate old two, do not alter product pixels, avoid false cutout and claim fabrication.
"""
import json,hashlib,io
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path("v2464-pending09-three-real-photo-frames"); ROOT.mkdir(exist_ok=True)
SRC=Path("v2463-obge-oil-control-real-photo")
def ft(s,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",s)
def fit(d,txt,max_width,size,b=False):
 while d.textbbox((0,0),txt,font=ft(size,b))[2]>max_width: size-=1
 return ft(size,b)
def hdr(d,tag):
 d.text((70,62),"OBgE",font=ft(52,True),fill="#293d37")
 d.text((71,129),"OIL CONTROL FINISHER  |  5 g",font=ft(27,True),fill="#4b5f55")
 d.line((70,192,1010,192),fill="#b9c9bb",width=3)
 d.text((70,974),tag,font=fit(d,tag,900,23),fill="#425850")
def compose(name,source,heading,descriptor,layout="central",bg="#f7f8f3"):
 im=Image.new("RGB",(1080,1080),bg);d=ImageDraw.Draw(im);hdr(d,"Product photo reference | Pending brand image use verification")
 d.text((72,225),heading,font=fit(d,heading,930,53,True),fill="#284038")
 d.text((72,306),descriptor,font=fit(d,descriptor,940,25),fill="#567166")
 pic=Image.open(SRC/source).convert("RGB")
 # Preserve the real photo pixels in a clean crop with no invented packaging or artificial shadow.
 if layout=="central":
  pic=ImageOps.contain(pic,(865,560))
  x=(1080-pic.width)//2;y=391
 else:
  pic=ImageOps.contain(pic,(940,565))
  x=(1080-pic.width)//2;y=385
 im.paste(pic,(x,y))
 f=ROOT/name;im.save(f,format="JPEG",quality=92,subsampling=0,optimize=True)
 raw=f.read_bytes();assert Image.open(f).size==(1080,1080) and len(raw)<2_000_000
 return {"file":name,"size":[1080,1080],"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"status":"PHOTO_BACKED_DRAFT_QA_HOLD"}
frames=[
 compose("03-actual-open-compact.jpg","brand-global-open-compact.png","OPEN COMPACT VIEW","Original OBgE product photo, with puff and product detail.","central"),
 compose("04-actual-dual-angle.jpg","retailer-dual-angle.jpg","MULTI-ANGLE VIEW","Two authentic views of the compact and applicator.","wide")
]
canvas=Image.new("RGB",(1080,1080),"#f5f1eb");d=ImageDraw.Draw(canvas);hdr(d,"Exact seller stock: 5 g | Final image QA and shop MK logo pending")
d.text((72,240),"PRODUCT INFORMATION",font=ft(49,True),fill="#294038")
d.text((72,325),"Check the packaging of your received item.",font=ft(26),fill="#5a6f65")
for i,(label,val) in enumerate([("BRAND","OBgE"),("PRODUCT","Oil Control Finisher"),("NET WEIGHT","5 g")]):
 y=440+150*i
 d.rounded_rectangle((74,y,1006,y+125),radius=24,fill="#e3e9df")
 d.text((106,y+17),label,font=ft(23),fill="#5c7167")
 d.text((106,y+54),val,font=ft(34,True),fill="#30453e")
f=ROOT/"05-stock-identification.jpg";canvas.save(f,"JPEG",quality=92,optimize=True)
raw=f.read_bytes();frames.append({"file":f.name,"size":[1080,1080],"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"status":"INFO_ONLY_DRAFT_QA_HOLD"})
manifest={"date":"2026-11-04","family_id":"pending-09","product":"OBgE Oil Control Finisher 5g","source_run_id":41682388609,"prior_photos_preserved":2,"new_files":frames,"final_product_edition_match_approved":False,"source_photo_commercial_rights_approved":False,"original_MK_logo_present":False,"public_url_verified_added":0,"workbook_untouched":True,"note":"Exact genuine images embedded unchanged, but final MK logo, photo rights and duplication review required."}
(ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"new_files":len(frames),"names":[x["file"] for x in frames]}))
