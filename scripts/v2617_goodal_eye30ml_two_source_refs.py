#!/usr/bin/env python3
"""v2617 exact-product Goodal 30mL Dark Spot Care Eye Cream tube-and-texture
photo reference. Does NOT alter prior 156 JPGs or imply commercial license.
Failed sources are recorded, not retried in an infinite loop.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from io import BytesIO
from PIL import Image,ImageOps
import hashlib,json
O=Path("v2617-goodal-30ml-texture-real-photo-reference");O.mkdir(exist_ok=True)
sources=[
 {"name":"tube-dispensing-cream","page":"https://kbeautyarabia.com/products/green-tangerine-dark-circle-eye-cream-30-ml",
 "url":"https://kbeautyarabia.com/cdn/shop/files/greentangerinevitacdarkspotcareeyecreamnew2.png?v=1772199028&width=1080"},
 {"name":"tube-white-background","page":"https://bellubeauty.co.uk/products/goodal-green-tangerine-vita-c-dark-circle-eye-cream-30ml",
 "url":"https://bellubeauty.co.uk/cdn/shop/files/GOODAL-Green-Tangerine-Vita-C-Dark-Spot-Care-Eye-Cream-30ml-BelluBeauty-73210661306694.jpg?v=1777846139"}
]
res=[]
for s in sources:
 row={"name":s["name"],"page":s["page"],"status":"SOURCE_HOLD"}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/*"}),timeout=18) as r:data=r.read(8000000)
  assert 16000<len(data)<8000000
  im=Image.open(BytesIO(data));im.load()
  assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=400
  canvas=Image.new("RGB",(1080,1080),"#fafbf9")
  photo=ImageOps.contain(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  canvas.paste(photo,((1080-photo.width)//2,(1080-photo.height)//2))
  path=O/(s["name"]+"-QA-ONLY.jpg")
  canvas.save(path,"JPEG",quality=92,subsampling=0,optimize=True)
  assert path.stat().st_size<2000000
  row.update(status="SOURCE_IMAGE_ACQUIRED_REVIEW_ONLY",file=path.name,
    source_url=s["url"],source_pixel_size=list(im.size),
    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 except Exception as exc:
  row["error_type"]=type(exc).__name__
 row["product_edition_photo_checked"]=False
 row["commercial_rights_cleared"]=False
 res.append(row)
manifest={"version":"v2617","family":"pending-21",
 "product":"Goodal Green Tangerine Vita C Dark Spot Care Eye Cream 30mL",
 "downloaded_count":sum(x["status"]=="SOURCE_IMAGE_ACQUIRED_REVIEW_ONLY" for x in res),
 "attempted_count":len(sources),"image_assets_changed_in_prior_v2616":0,
 "source_rights_verified":False,"original_MK_logo_verified":False,
 "sales_release_allowed":False,"existing_55_public_URLs_unchanged":True,
 "xlsx_created_or_shared":False,"sources":res}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"downloaded":manifest["downloaded_count"],"attempted":2,"released":False,"xlsx":False}))
