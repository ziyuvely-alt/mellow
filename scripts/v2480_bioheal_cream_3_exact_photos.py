#!/usr/bin/env python3
"""Pending-25 BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50ml.
Make only frames 03-05 from exact real retailer pixels. No typography overlay,
invented pack, pseudo-cutout, shade graphic or stock/license assertion.
"""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json
src=Path("v2479-bioheal-nad-cream-source")
out=Path("v2480-bioheal-nad-cream-three-photos")
out.mkdir(exist_ok=True)
items=[
("original-04.jpg","03-original-open-jar-texture.jpg","REAL_OPEN_JAR_TEXTURE"),
("original-05.jpg","04-original-closeup-jar.jpg","REAL_JAR_CLOSEUP"),
("original-06.jpg","05-original-single-product.jpg","REAL_STANDALONE_JAR")
]
files=[]
for source,name,role in items:
 im=Image.open(src/source).convert("RGB")
 # Center-cover crop only; original product pixels and product labels never generated/painted.
 im=ImageOps.fit(im,(1080,1080),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
 p=out/name;im.save(p,"JPEG",quality=93,subsampling=0,optimize=True)
 raw=p.read_bytes()
 assert len(raw)<2000000 and Image.open(p).size==(1080,1080)
 files.append({"filename":name,"source":source,"role":role,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"jpg_1080_square":True,"status":"EXACT_PHOTO_QA_HOLD"})
manifest={"date":"2026-11-04","family_id":"pending-25","name":"BIOHEAL BOH NAD PRIZCELL Glow Boost Cream 50ml","new_jpg":files,"source_run_id":41686243752,"source_artifact_id":13254318742,"existing_older_frames_modified":0,"marketing_banners_excluded":["original-01.jpg","original-02.jpg"],"model_photo_excluded":["original-03.jpg"],"photo_rights_approved":False,"original_MK_logo_applied":False,"stock_edition_verified":False,"released":False,"new_verified_public_url":0,"excel_created_or_shared":False}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"new_jpg_count":len(files),"sizes":[x["bytes"] for x in files],"status":"QA_HOLD"}))
