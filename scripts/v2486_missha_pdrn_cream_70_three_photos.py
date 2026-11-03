#!/usr/bin/env python3
"""Create ONLY three pending-14 MISSHA Camellia PDRN NAD+ Firming Repair Cream 70ml
authentic photo JPGs. Do not use serum, popup or Artemisia image from product page.
"""
from pathlib import Path
from PIL import Image, ImageOps
import json,hashlib
S=Path("v2485-missha-pdrn-cream-official-evidence/pending-14")
O=Path("v2486-missha-cream-70-three-JPG");O.mkdir(exist_ok=True)
items=[
 ("original-01.jpg","03-real-cream-pack-and-texture.jpg","GENUINE_CREAM_JAR_LAB_SCENE"),
 ("original-04.jpg","04-open-jar-texture.jpg","GENUINE_OPEN_CREAM_JAR"),
 ("original-05.jpg","05-standalone-jar.jpg","GENUINE_STANDALONE_JAR")
]
records=[]
for source,outfile,role in items:
 im=Image.open(S/source).convert("RGB")
 # Whole-canvas resize of authentic image; preserve product pixels without false cutout.
 im=ImageOps.fit(im,(1080,1080),method=Image.Resampling.LANCZOS)
 p=O/outfile;im.save(p,format="JPEG",quality=94,optimize=True,subsampling=0)
 b=p.read_bytes();assert Image.open(p).size==(1080,1080) and len(b)<2_000_000
 records.append({"file":outfile,"source":source,"role":role,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"dimensions":[1080,1080],"state":"NEW_AUTHENTIC_PHOTO_DRAFT_FINAL_QA_HOLD"})
manifest={"family":"pending-14","date":"2026-11-04","product":"MISSHA PDRN NAD FIRMING REPAIR CREAM 70 mL","source_artifact_id":13255154228,"source_run_id":41687671016,"new_jpg":records,"excluded_images":["original-02.jpg app popup","original-03.jpg repeat of original-01","original-06.jpg other Artemisia line","original-07.jpg other Artemisia line","original-08.jpg model/marketing poster"],"old_images_unchanged":True,"original_owner_MK_logo_present":False,"photo_commercial_rights_verified":False,"inventory_packaging_version_verified":False,"published":False,"verified_new_public_urls":0,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"made":len(records),"filenames":[r["file"] for r in records]},ensure_ascii=False))
