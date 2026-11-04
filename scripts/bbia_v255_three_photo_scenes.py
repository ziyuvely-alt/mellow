#!/usr/bin/env python3
"""BBIA v255 three new photo detail candidate crops; existing public assets never changed."""
import json,hashlib,io,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont
D=[
 ("228","LIP OIL BALM",0,(0,1750,1000,2800),"JAR PRODUCT DETAIL"),
 ("238","READY TO WEAR EYE SHADOW",0,(0,350,1000,1450),"SINGLE SHADOW DETAIL"),
 ("234","READY TO WEAR EYE PALETTE",2,(0,650,1000,1750),"EYE PALETTE TEXTURE")
]
OUT=Path("/tmp/bbia-v255");OUT.mkdir(parents=True,exist_ok=True)
master={str(x["product_id"]):x for x in json.loads(Path("evidence/bbia-image-review-input.json").read_text())["families"]}
def load(task):
    sku,name,i,rect,role=task;url=master[sku]["detail_references"][i]
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=24) as f:blob=f.read(12_000_000)
    image=Image.open(io.BytesIO(blob)).convert("RGB")
    x0,y0,x1,y1=rect
    return task,url,image.crop((x0,y0,min(image.width,x1),min(image.height,y1))),image.size,hashlib.sha256(blob).hexdigest()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(load,D))
board=Image.new("RGB",(1620,650),"#f4f3f2"); pen=ImageDraw.Draw(board)
pen.text((15,12),"BBIA v255: THREE REAL SOURCE PHOTO SECONDARY SCENE CANDIDATES",fill="#232323")
font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"),n)
rows=[]
for i,(task,url,photo,source_size,sh) in enumerate(results):
    sku,name,source_idx,rect,role=task
    photo.thumbnail((920,780),Image.Resampling.LANCZOS)
    frame=Image.new("RGB",(1080,1080),"#faf9f7");d=ImageDraw.Draw(frame)
    d.text((65,48),"BBIA",font=font(50,True),fill="#302c2c")
    d.text((65,123),name,font=font(30,True),fill="#494343")
    d.line((65,184,1015,184),fill="#d6c9c5",width=2)
    frame.paste(photo,((1080-photo.width)//2,205+(780-photo.height)//2))
    d.text((65,995),role+"  |  PHOTO REFERENCE",font=font(23),fill="#726563")
    nameout="BBIA_"+sku+"_DETAIL_v255_QA_PENDING.jpg";fpath=OUT/nameout
    frame.save(fpath,"JPEG",quality=91,optimize=True,subsampling=0)
    if fpath.stat().st_size>=2000000:raise ValueError("Over 2MB")
    thumb=frame.copy();thumb.thumbnail((525,525))
    board.paste(thumb,(i*540+10,60))
    rows.append({"goodsNo":sku,"file":nameout,"role":role,"source_url":url,"source_crop":list(rect),"source_sha256":sh,
      "source_size":source_size,"dimensions":[1080,1080],"output_bytes":fpath.stat().st_size,
      "sha256":hashlib.sha256(fpath.read_bytes()).hexdigest(),"status":"VISUAL_QA_PENDING"})
board.save(OUT/"BBIA_v255_THREE_DETAIL_CONTACT.jpg",quality=89)
(OUT/"BBIA_v255_MANIFEST.json").write_text(json.dumps({"checkpoint":"v255","parent":"v254","new_jpg":3,"files":rows,
  "existing_images_modified":False,"sales_approved":0,"warning":"Individual photo source image may contain Korean marketing copy. Manually inspect before retaining."},indent=2))
print("V255_RESULT",json.dumps({"created":len(rows),"ids":[x["goodsNo"] for x in rows]}))
