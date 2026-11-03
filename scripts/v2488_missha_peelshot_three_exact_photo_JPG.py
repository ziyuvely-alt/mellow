#!/usr/bin/env python3
"""Only 3 NEW genuine photo JPGs for MISSHA PDRN NAD Renew Peel Shot 25 15ml.
Never use popup, unrelated marketing poster, serum/cream, guessed shade, or fake pack.
"""
from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib
S=Path("v2487-missha-pdrn-peelshot-15-official-evidence/pending-12")
O=Path("v2488-missha-peelshot-15-three-JPG");O.mkdir(exist_ok=True)
images=[
 ("original-01.jpg","03-real-liquid-dropper-scene.jpg","GENUINE_15ML_PRODUCT_LIQUID_SCENE"),
 ("original-04.jpg","04-real-product-around-droppers.jpg","GENUINE_15ML_PRODUCT_WITH_DROPPERS"),
 ("original-05.jpg","05-real-standalone-15ml-shot.jpg","GENUINE_15ML_STANDALONE_PRODUCT")
]
result=[]
for original,name,role in images:
 im=Image.open(S/original).convert("RGB")
 im=ImageOps.fit(im,(1080,1080),method=Image.Resampling.LANCZOS)
 p=O/name;im.save(p,"JPEG",quality=93,subsampling=0,optimize=True)
 b=p.read_bytes();assert len(b)<2_000_000 and Image.open(p).size==(1080,1080)
 result.append({"file":name,"original_source":original,"role":role,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"format":"JPEG","dimensions":[1080,1080],"status":"PHOTO_BYTES_READY_FINAL_QA_HOLD"})
manifest={"date":"2026-11-04","family_id":"pending-12","product":"MISSHA PDRN NAD Renew Peel Shot 25 15mL","three_new_JPG_files":result,"source_run_id":41688077234,"source_artifact_id":13256570685,"rejected_originals":["original-02.jpg popup","original-03.jpg duplicate of 01","original-06.jpg model/advertising","original-07.jpg Korean claim-based infographic","original-08.jpg Korean marketing detail"],"existing_customer_JPGs_untouched":True,"final_stock_edition_checked":False,"commercial_rights_verified":False,"original_MK_logo_applied":False,"new_public_URLs":0,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_files":len(result),"sha256":[x["sha256"] for x in result]}))
