#!/usr/bin/env python3
"""v2850 Mesh Blur refill-set product-common gallery audit.
Skip v2849 shade photos and all explicitly variant-assigned gallery images.
Collect genuine unassigned product scenes for human QA; not sales-ready.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests,json,hashlib
R=Path("qa-review")
ROOT=R/"v2849-clio-meshblur-15g-refill-three-stock-shades-sourceQA"
OUT=R/"v2850-meshblur15g-refill-product-common-scenes-QA"
assert ROOT.is_dir() and not OUT.exists()
OUT.mkdir()
old=json.loads((ROOT/"manifest.json").read_text())
assert old["source_photos_saved_count"]==3
URL=old["source"]
headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,image/jpeg,image/png,image/webp,*/*"}
row={"version":"v2850","baseline":"v2849","family":"pending-07",
"merchant_gallery_json":URL,"inventory_shades":["19C","19N","21N"],
"all_excluded_variant_photo_SHA_sources_preserved":True,
"source_shade_specific_images_v2849_untouched":True,
"all_11_old_approved_groups_untouched":True,"all_55_public_URLs_untouched":True,
"existing_QA_JPGs_modified":0,"new_retail_approved":0,"final_xlsx_shared":False,
"photo_commercial_rights_verified":False,"physical_stock_bundle_edition_verified":False,
"original_MK_logo_authenticated":False,"gallery":[]}
try:
 response=requests.get(URL,timeout=22,headers=headers);response.raise_for_status()
 product=response.json()
 assert "mesh blur" in str(product.get("title","")).lower()
 variants=product.get("variants",[])
 assigned=set()
 for v in variants:
  photo=v.get("featured_image")
  if isinstance(photo,dict) and photo.get("src"):assigned.add(photo["src"].split("?")[0])
  elif isinstance(photo,str):assigned.add(photo.split("?")[0])
 allimg=product.get("images",[])
 urls=[]
 for x in allimg:
  u=x.get("src") if isinstance(x,dict) else x if isinstance(x,str) else None
  if not u or not u.startswith("https://"):continue
  if u.split("?")[0] in assigned:continue
  if u.split("?")[0] not in {s.split("?")[0] for s in urls}:urls.append(u)
 row["merchant_total_gallery_images"]=len(allimg)
 row["merchant_variant_photos_excluded"]=len(assigned)
 row["unassigned_gallery_candidates"]=len(urls)
 for index,u in enumerate(urls[:12],1):
  item={"gallery_idx":index,"src":u,"role":"COMMON_UNASSIGNED_SHADE_REFERENCE",
        "commercial_rights_verified":False,"status":"HOLD_SOURCE_OR_VISUAL"}
  try:
   rr=requests.get(u,headers=headers,timeout=18);rr.raise_for_status()
   assert 500<len(rr.content)<9000000
   with Image.open(BytesIO(rr.content)) as im:
    im.load();size=list(im.size)
    if min(size)<600:raise ValueError(f"too small: {size}")
    im=ImageOps.exif_transpose(im).convert("RGB")
    c=Image.new("RGB",(1080,1080),"white")
    d=ImageOps.contain(im,(1080,1080),Image.Resampling.LANCZOS)
    c.paste(d,((1080-d.width)//2,(1080-d.height)//2))
   name=f"common-{index:02d}-merchant-gallery-NO-SHADE-QA.jpg"
   dest=OUT/name;c.save(dest,"JPEG",quality=92,optimize=True)
   assert dest.stat().st_size<2_000_000
   item.update({"status":"GENUINE_GALLERY_REFERENCE_SAVED_PENDING_HUMAN_QA",
   "file":name,"source_native":size,
   "source_sha256":hashlib.sha256(rr.content).hexdigest(),
   "jpg_sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
  except Exception as e:item["error"]=str(e)[:180]
  row["gallery"].append(item)
except Exception as e:row["gallery_probe_failure"]=str(e)[:280]
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
per_row=4;tile=285
saved=[x for x in row["gallery"] if x.get("file")]
height=95+((max(1,len(saved))+per_row-1)//per_row)*340
board=Image.new("RGB",(1240,height),"#f4f2f0")
dr=ImageDraw.Draw(board)
dr.text((20,20),"v2850 Mesh Blur 15g+refill | common scenes | SHADE UNASSIGNED | QA ONLY",font=f(22,True),fill="#352f39")
for i,item in enumerate(saved):
 x=16+(i%per_row)*304;y=74+(i//per_row)*340
 with Image.open(OUT/item["file"]) as img:thumb=img.resize((285,285),Image.Resampling.LANCZOS)
 board.paste(thumb,(x,y))
 dr.text((x,y+292),f"GALLERY {item['gallery_idx']:02d} / NO SHADE",font=f(15),fill="#5b5259")
board.save(OUT/"v2850-merchant-gallery-visual-QA.jpg","JPEG",quality=83)
row["gallery_photos_saved"]=len(saved)
row["source_photo_rights_not_proven"]=True
row["next"]="Select only exact physical 15g+refill product scenes; shade photo labels remain blocked until stock edition + rights."
(OUT/"manifest.json").write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2850","gallery":row.get("unassigned_gallery_candidates",0),
 "saved":len(saved),"released":0},ensure_ascii=False))
