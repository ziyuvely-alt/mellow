#!/usr/bin/env python3
"""v2615: obtain two genuine single-product BIOHEAL BOH NAD-PRIZCELL
Glow Power Serum 30mL photographs. In particular excludes current serum+mask+
cream promotional bundle in v2614 pending-24 slot03.
Separate QA-only photo sources, not sales rights or new live image URLs.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps
import hashlib,json
O=Path("v2615-boh-30ml-solo-product-sources-QA"); O.mkdir(exist_ok=True)
C=[
 {"id":"single-bottle-with-dropper","page":"https://lacosmetique.com.au/products/nad-prizcell-glow-power-serum-30ml",
  "urls":[
    "https://lacosmetique.com.au/cdn/shop/files/nad-prizcell-glow-power-serum-30ml-2634145.png?v=1779943270&width=1200",
    "https://www.ballagrio.com/cdn/shop/files/biohealboh-nad-prizcell-glow-power-serum-30ml-01_1200x1200.jpg?v=1758606854"]},
 {"id":"single-bottle-water-droplets","page":"https://k-touch.us/products/bio-heal-boh-nad-prizcell-glow-power-serum-30ml",
  "urls":[
    "https://k-touch.us/cdn/shop/files/B2ADA058-C68E-4D0A-8D27-479EA966D5DC.png?v=1781042499",
    "https://kbeautystore.com/cdn/shop/files/9739cac1-9666-4e32-b14f-5c460c77110a_jpg.webp?v=1770815145&width=1200"]}
]
results=[]
for case in C:
 entry={"scene":case["id"],"source_page":case["page"],"status":"SOURCE_ACCESS_HOLD"}
 for trial,url in enumerate(case["urls"],1):
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/png,image/jpeg,image/*"}),timeout=20) as r:
    raw=r.read(9000000)
   assert 15000<len(raw)<9000000
   orig=Image.open(BytesIO(raw));orig.load()
   assert orig.format in ("JPEG","PNG","WEBP") and min(orig.size)>=500
   photo=ImageOps.contain(orig.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
   canvas=Image.new("RGB",(1080,1080),"#fcfbfa")
   canvas.paste(photo,((1080-photo.width)//2,(1080-photo.height)//2))
   path=O/(case["id"]+"-SOURCE-QA.jpg")
   canvas.save(path,"JPEG",quality=93,subsampling=0,optimize=True)
   assert path.stat().st_size<2000000
   entry.update(status="PHOTO_ACQUIRED_NOT_LICENSED",file=path.name,
    chosen_url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    original_pixel_size=list(orig.size),retailer_photo_source_verified=False,
    seller_commercial_reuse_rights_verified=False,physical_stock_package_identical=False)
   break
  except Exception as e:
   entry[f"source_attempt_{trial}_reason"]=type(e).__name__
 results.append(entry)
manifest={"version":"v2615","family":"pending-24",
 "inventory":"BIOHEAL BOH NAD PRIZCELL Glow Power Serum 30 mL single retail SKU",
 "wrong_earlier_scene":"v2614 slot03 photograph advertises a serum + extra film mask + 20 mL cream promotional set",
 "attempted_distinct_solo_scenes":2,
 "downloaded_solo_photos":sum("file" in x for x in results),
 "old_156_source_images_untouched":True,"previous_public_55_urls_changed":0,
 "xlsx_created_or_shared":False,
 "photo_authorization_verified":False,"commercial_publication_approved":False,
 "photos":results}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"acquired":manifest["downloaded_solo_photos"],"holds":2-manifest["downloaded_solo_photos"],
 "old_photos_modified":0,"xlsx_shared":False}))
