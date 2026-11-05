#!/usr/bin/env python3
"""v2849 CLIO Mesh Blur Cushion 15g+15g exact stock 19C 19N 21N source QA.
Internal reference only. No redistributable sale images, no authenticated MK.
"""
from pathlib import Path
from io import BytesIO
import hashlib, json, requests, re
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path("qa-review")
OUT=R/"v2849-clio-meshblur-15g-refill-three-stock-shades-sourceQA"
assert not OUT.exists()
OUT.mkdir(parents=True)
url="https://lacosmetique.com.au/products/kill-cover-mesh-blur-cushion-refill-set.js"
required={"19C":"Light","19N":"Porcelain","21N":"Linen"}
headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,*/*"}
report={"version":"v2849","family":"pending-07","source":url,
 "product":"CLIO Kill Cover Mesh Blur Cushion Refill Set","stock_required_shades":list(required),
 "expected_stock_contents":"Cushion 15g + refill 15g",
 "no_out_of_stock_extra_shade_usage":True,
 "downloaded_photos_internal_QA_only":True,"actual_owned_stock_version_verified":False,
 "merchant_photo_commercial_redistribution_rights_verified":False,
 "original_MK_logo_authenticated":False,"previous_11_approved_groups_untouched":True,
 "previous_55_URLs_untouched":True,"prior_QA_unchanged":True,
 "new_sales_approved":0,"final_excel_shared":False,"variants":[]}
def hsh(b):return hashlib.sha256(b).hexdigest()
try:
 q=requests.get(url,headers=headers,timeout=23);q.raise_for_status()
 d=q.json()
 title=str(d.get("title",""))
 assert "mesh blur" in title.lower() and ("refill" in title.lower() or "set" in title.lower()),title
 variants=d.get("variants",[])
 assert isinstance(variants,list) and variants
 report.update({"merchant_title":title,"variant_count":len(variants),"shopify_product_id":d.get("id")})
 rows=[]
 for shade,label in required.items():
  matches=[v for v in variants if re.search(r"\\b"+shade+r"\\b",str(v.get("title","")),re.I)]
  row={"shade":shade,"shade_name":label,"matched_variant_count":len(matches),"status":"HOLD"}
  if len(matches)!=1:
   row["reason"]="SHADE_NOT_UNIQUELY_PRESENT";rows.append(row);continue
  variant=matches[0]
  row["variant_id"]=variant.get("id")
  photo=variant.get("featured_image") or {}
  img_url=(photo.get("src") if isinstance(photo,dict) else (photo if isinstance(photo,str) else None))
  if not img_url and isinstance(variant.get("featured_media"),dict):
   img_url=variant["featured_media"].get("preview_image",{}).get("src")
  if not img_url or not img_url.startswith("https://"):
   row["reason"]="NO_EXACT_VARIANT_ASSIGNED_PHOTO";rows.append(row);continue
  row["variant_linked_photo_url"]=img_url
  other=[v for v in variants if v.get("id")!=variant.get("id") and v.get("featured_image")]
  # Even if a source image is shared across several colours it cannot prove exact shade.
  duplicate=[]
  for v in other:
   p=v.get("featured_image")
   src=p.get("src") if isinstance(p,dict) else p if isinstance(p,str) else ""
   if src==img_url:duplicate.append(v.get("title"))
  if duplicate:
   row["status"]="HOLD_SHARED_IMAGE_NOT_SHADE_SPECIFIC"
   row["same_image_other_shades"]=duplicate
   rows.append(row);continue
  try:
   a=requests.get(img_url,timeout=22,headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"})
   a.raise_for_status()
   assert 500<len(a.content)<8000000
   with Image.open(BytesIO(a.content)) as im:
    im.load(); size=list(im.size)
    if min(size)<550:raise ValueError("source too small: "+str(size))
    photo=ImageOps.exif_transpose(im).convert("RGB")
   canvas=Image.new("RGB",(1080,1080),"white")
   fitted=ImageOps.contain(photo,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
   name=f"{shade}-MERCHANT-EXACT-PHOTO-1080-INTERNAL-QA.jpg"
   target=OUT/name;canvas.save(target,"JPEG",quality=92,optimize=True)
   assert target.stat().st_size<2000000
   row.update({"status":"EXACT_VARIANT_PHOTO_SAVED_QA_RETAIL_HOLD",
   "file":name,"source_size":size,"raw_sha256":hsh(a.content),"jpg_sha256":hsh(target.read_bytes()),
   "jpg_bytes":target.stat().st_size})
  except Exception as e:
   row["status"]="HOLD_DOWNLOAD_OR_IMAGE_QA"
   row["reason"]=str(e)[:240]
  rows.append(row)
 report["variants"]=rows
except Exception as e:
 report["source_error"]=str(e)[:400]
 report["variants"]=[{"shade":k,"shade_name":v,"status":"HOLD_SOURCE_UNAVAILABLE"} for k,v in required.items()]
# Records are valuable even when individual photos unavailable.
report["source_photos_saved_count"]=sum("file" in x for x in report["variants"])
report["source_photos_not_saved_count"]=3-report["source_photos_saved_count"]
report["retail_ready_variants_count"]=0
report["release_status"]="HOLD_STOCK_PACKAGING_LICENSE_MK_VISUAL_QA"
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,heavy=False:ImageFont.truetype(bold if heavy else font,n)
contact=Image.new("RGB",(1690,590),"#f2f0ee")
dr=ImageDraw.Draw(contact)
dr.text((25,15),"v2849 CLIO Mesh Blur 15g + 15g refill | stock shades only | INTERNAL QA",font=f(26,True),fill="#35303b")
for i,entry in enumerate(report["variants"]):
 x=25+i*557
 if entry.get("file"):
  with Image.open(OUT/entry["file"]) as im:tile=im.resize((505,505),Image.Resampling.LANCZOS)
  contact.paste(tile,(x,60))
 else:
  dr.rectangle((x,60,x+505,565),outline="#bcb7b9",width=3)
  dr.text((x+20,250),"PHOTO HOLD",font=f(29,True),fill="#796d75")
 dr.text((x+13,532),entry["shade"]+" "+entry["shade_name"]+"  "+entry["status"][:22],font=f(15),fill="#39333b")
contact.save(OUT/"v2849-stock-three-shade-contact-QA.jpg","JPEG",quality=83,optimize=True)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":report["version"],"saved":report["source_photos_saved_count"],"shades":{x["shade"]:x["status"] for x in report["variants"]}},ensure_ascii=False))
