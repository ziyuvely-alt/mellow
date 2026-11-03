#!/usr/bin/env python3
"""MISSHA PDRN NAD 30ml serum: three independent product-information photo draft JPGs.
Use only the exact product photos 04 and 05, explicitly reject popup, unrelated vitamin-C
bottle, multi-product group, model and unverified claims. QA hold remains.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json
S=Path("v2483-missha-pdrn-two-real-product-galleries/pending-13")
O=Path("v2484-missha-serum-three-new-JPG");O.mkdir(exist_ok=True)
font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def saved(name,image,src,role):
 f=O/name;image.convert("RGB").save(f,"JPEG",quality=93,subsampling=0,optimize=True)
 data=f.read_bytes();assert len(data)<2000000 and Image.open(f).size==(1080,1080)
 return {"file":name,"source":src,"role":role,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"size":[1080,1080],"status":"PHOTO_CANDIDATE_FINAL_QA_HOLD"}
def photo(name,src,head,detail):
 a=Image.open(S/src).convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
 # Original white/near-white official photo already covers the whole square. No
 # separately pasted rectangular image nor synthetic pack/photo.
 d=ImageDraw.Draw(a)
 d.rounded_rectangle((36,906,1044,1054),radius=15,fill="#faf3f4")
 d.text((66,922),"MISSHA  /  PDRN NAD+",font=font(27,True),fill="#641b29")
 d.text((66,959),head,font=font(32,True),fill="#6b1d2d")
 d.text((66,1007),detail,font=font(21),fill="#6b3b46")
 return saved(name,a,src,"AUTHENTIC_SINGLE_PRODUCT_PHOTO")
files=[
 photo("03-real-dropper-serum.jpg","original-04.jpg","DROPPER & SERUM","Single 30 mL genuine product photo."),
 photo("04-real-bottle-capsules.jpg","original-05.jpg","BOTTLE DETAILS","Original red bottle and capsule visual.")
]
c=Image.new("RGB",(1080,1080),"#f9f4f3");d=ImageDraw.Draw(c)
d.text((75,83),"MISSHA",font=font(70,True),fill="#6e1f35")
d.text((75,190),"PDRN NAD+",font=font(64,True),fill="#6e1f35")
d.text((75,274),"FIRMING REPAIR SERUM",font=font(42,True),fill="#6e1f35")
for i,(l,v) in enumerate([("PRODUCT TYPE","Facial serum"),("NET CONTENT","30 mL"),("PACKAGING","Dropper bottle")]):
 y=390+i*167
 d.rounded_rectangle((80,y,1000,y+130),radius=22,fill=["#f1e3e6","#f3e8e9","#f1e3e6"][i])
 d.text((115,y+12),l,font=font(25),fill="#85576a")
 d.text((115,y+59),v,font=font(40,True),fill="#663447")
d.text((80,973),"Check the exact label on your purchased product.",font=font(22),fill="#77545e")
files.append(saved("05-serum-pack-details.jpg",c,"verified 30ml serum packaging details","FACT_ONLY"))
data={"date":"2026-11-04","family_id":"pending-13","product":"MISSHA PDRN NAD Firming Repair Serum 30ml","existing_frames_modified":0,"files":files,"source_run_id":41687211248,"source_artifact_id":13256310428,"source_reject":["original-01.jpg multiproduct","original-02.jpg unrelated app popup","original-03.jpg multiproduct duplicate","original-06.jpg vitamin C unrelated bottle","original-07.jpg model/marketing image","original-08.jpg marketing claims"],"final_QA_pending":["source commercial rights","actual owner MK logo","physical stock edition","different product photo scenes verification"],"new_public_urls":0,"excel_shared":False}
(O/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_jpg":len(files),"source":["original-04.jpg","original-05.jpg"]}))
