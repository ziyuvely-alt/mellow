#!/usr/bin/env python3
"""Selective correction of only two Dr.G v2482 jpg frames.
Remove leaked internal QA/status copy from lower strip without changing original
tube/carton photographs. Do not touch frame05 or any previous published asset.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
src=Path("v2482-drg-brightening-sun-three-JPG")
out=Path("v2489-drg-two-footer-repairs");out.mkdir(exist_ok=True)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
result=[]
for n in ["03-exact-single-tube-photo.jpg","04-bottle-and-box-source.jpg"]:
 im=Image.open(src/n).convert("RGB");assert im.size==(1080,1080)
 d=ImageDraw.Draw(im)
 d.rectangle((0,984,1079,1079),fill="white")
 d.line((68,996,1012,996),fill="#d6cfc5",width=2)
 d.text((70,1012),"Dr.G  |  Brightening Up Sun+  |  50 mL",font=font,fill="#56483c")
 p=out/n;im.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
 b=p.read_bytes();assert len(b)<2000000
 result.append({"file":n,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"fixed":"Removed internal QA/status footer only","status":"VISUAL_QA_PENDING"})
data={"date":"2026-11-04","family_id":"pending-18","source_run_id":41687077182,"modified_only_two_existing_draft_frames":True,"prior_original_files_unchanged":True,"files":result,"other_drafts_unchanged":True,"original_MK_logo_missing":True,"commercial_rights_and_stock_QA_pending":True,"new_public_URLs":0,"excel_shared":False}
(out/"manifest.json").write_text(json.dumps(data,indent=2)+"\n")
print(json.dumps({"targeted_repairs":len(result)}))
