#!/usr/bin/env python3
"""v2702 evidence-only MISSHA M Perfect Cover BB cream, exact 50ml and shade
21/23/25 from verified MISSHA US product catalog. Avoid confusing with new
SERUM BB Cream or Japan M PRO-COVER. No approved art is overwritten.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,hashlib,base64,re
OUT=Path("qa-review/v2702-missha-M-perfect-cover-BB-official-photo-proof")
assert not OUT.exists();OUT.mkdir(parents=True)
PAGE="https://misshaus.com/products/m-perfect-cover-bb-cream-spf-42-pa-50ml-new"
HEAD={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/html,image/avif,image/jpeg,image/png,*/*"}
report={"version":"v2702","family":"pending-03","page":PAGE,"product":"MISSHA M Perfect Cover BB Cream SPF42 PA+++ 50ml",
"source_image_candidates":[],"real_photo_files":[],"retail_approved":False,
"old_11_approved_untouched":True,"old_55_public_urls_untouched":True,
"prior_pending03_QA_set_untouched":True,"final_xlsx_shared":False}
try:
 response=requests.get(PAGE+".js",headers=HEAD,timeout=19);response.raise_for_status()
 product=response.json()
 title=product.get("title","")
 if not all(s in title.lower() for s in ["perfect","cover","bb cream"]):
  raise ValueError("Not an exact product catalog match")
 if "serum" in title.lower() or "pro-cover" in title.lower():
  raise ValueError("Wrong MISSHA packaging/series")
 report["product_title"]=title
 variants=product.get("variants",[])
 report["variants"]=[{"name":v.get("title"),"sku":v.get("sku"),"id":v.get("id")} for v in variants[:24]]
 report["source_shades_21_23_25_mentioned"]=all(any(re.search(r"\b"+s+r"\b",str(v.get("title",""))) for v in variants) for s in ["21","23","25"])
 urls=[]
 for pic in product.get("images",[]):
  if isinstance(pic,str):urls.append(pic)
  elif isinstance(pic,dict):urls.append(pic.get("src") or "")
 seen=set();urls=[urljoin(PAGE,u) for u in urls if u]
 urls=[u for u in urls if not(u in seen or seen.add(u))]
 report["source_image_candidates"]=urls[:30]
 for u in urls[:16]:
  try:
   res=requests.get(u,headers=HEAD,timeout=14);res.raise_for_status()
   if len(res.content)>8500000:continue
   orig=Image.open(BytesIO(res.content));orig.load()
   if min(orig.size)<370:continue
   rgb=ImageOps.exif_transpose(orig).convert("RGB")
   square=Image.new("RGB",(1080,1080),"white")
   image=ImageOps.contain(rgb,(1040,1040),Image.Resampling.LANCZOS)
   square.paste(image,((1080-image.width)//2,(1080-image.height)//2))
   dest=OUT/f"{len(report['real_photo_files'])+1:02d}-MISSHA-US-actual-source-reference.jpg"
   square.save(dest,"JPEG",quality=91,optimize=True,subsampling=0)
   if dest.stat().st_size>=2_000_000:dest.unlink();continue
   report["real_photo_files"].append({"file":dest.name,"url":u,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"source_px":list(orig.size)})
   if len(report["real_photo_files"])>=10:break
  except (requests.RequestException,OSError,ValueError):continue
 report["status"]="SOURCE_REFERENCES_NEED_PHYSICAL_EDITION_AND_SHADE_VISUAL_QA" if report["real_photo_files"] else "HOLD_NO_PRODUCT_JPGS"
except Exception as exc:
 report["status"]="HOLD_SOURCE_CATALOG_ACCESS"
 report["error_type"]=type(exc).__name__;report["error"]=str(exc)[:230]
if report["real_photo_files"]:
 n=len(report["real_photo_files"]);rows=(n+3)//4
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
 board=Image.new("RGB",(1820,rows*430+90),"#f0f0ef");d=ImageDraw.Draw(board)
 d.text((16,17),"v2702 M PERFECT COVER BB CREAM | OFFICIAL VARIANT PHOTO QA ONLY",font=font,fill="#222222")
 for i,f in enumerate(report["real_photo_files"]):
  with Image.open(OUT/f["file"]) as img:
   thumb=img.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
  x=15+(i%4)*452;y=70+(i//4)*430
  board.paste(thumb,(x,y));d.text((x,y+350),f"REFERENCE {i+1:02d}",font=font,fill="#242424")
 proof=OUT/"v2702-photo-gallery-proof.jpg";board.save(proof,"JPEG",quality=83,optimize=True)
 (OUT/"v2702-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_official_source_JPGs":len(report["real_photo_files"]),
"variant_21_23_25_numbers":report.get("source_shades_21_23_25_mentioned"),
"state":report["status"],"sale_approved":0}))
