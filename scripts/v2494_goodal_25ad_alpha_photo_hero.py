#!/usr/bin/env python3
"""Pending-19 Goodal 25AD Cream Alpha 50ml single authentic product-photo hero.
Brand product image exact ALPHA; 25AD stock edition not assumed from listing.
No duplication of v2459 corrected information card.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont,ImageOps
from io import BytesIO
import hashlib,json
out=Path("v2494-goodal-cream-alpha-photo");out.mkdir(exist_ok=True)
url="https://use-image.oliveyoung.com/images/prd/8800290367942/thumbnail/6035c2d6-31dd-47b1-92cb-4c0c2b24bc6b.jpg?AR=0&QT=85&RS=1000X1000&SF=webp"
ledger={"date":"2026-11-04","family":"pending-19","exact_product":"Goodal Green Tangerine Vita-C Dark Spot Care Cream Alpha 50ml","stock_edition":"25AD (not visually proven)","product_source":"Olive Young US","source_url":url,"source_status":"PENDING","new_jpg":0,"final_license_verified":False,"source_stock_version_verified":False,"public_urls_added":0,"prior_v2459_info_card_preserved":True}
try:
 with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=25) as r:b=r.read(6000001)
 if len(b)>6000000:raise ValueError("oversize")
 im=Image.open(BytesIO(b));im.load()
 if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<500:raise ValueError("not photo")
 (out/"source-alpha-original."+{"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]).write_bytes(b)
 ledger["source_sha256"]=hashlib.sha256(b).hexdigest()
 canvas=Image.new("RGB",(1080,1080),"#f6f7ee")
 # Genuine product shot preserved, no invented labels, make clean retail layout.
 photo=ImageOps.contain(im.convert("RGB"),(950,875))
 canvas.paste(photo,((1080-photo.width)//2,115))
 d=ImageDraw.Draw(canvas);font=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 d.text((55,34),"GOODAL  /  VITA-C CREAM ALPHA",font=font(38,True),fill="#315646")
 d.text((55,1013),"50 mL  |  Original product photo  |  Stock edition QA pending",font=font(19),fill="#5a725e")
 f=out/"03-real-alpha-jar-hero.jpg";canvas.save(f,"JPEG",quality=90,subsampling=0,optimize=True)
 raw=f.read_bytes();assert len(raw)<2000000 and Image.open(f).size==(1080,1080)
 ledger.update(source_status="ACTUAL_ORIGINAL_PHOTO_AND_JPG_BYTES_STAGED_QA_HOLD",new_jpg=1,output_filename=f.name,output_sha256=hashlib.sha256(raw).hexdigest(),output_bytes=len(raw),source_dimensions=im.size)
except Exception as e:ledger["error"]=str(e)[:240]
(out/"manifest.json").write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"status":ledger["source_status"],"new_jpg":ledger["new_jpg"]}))
