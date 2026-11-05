#!/usr/bin/env python3
"""v2852 CLIO Founwear The Original 15g + refill 15g, 5 stock shades.
Alternative supplier exact-variant photo lookup, no old v2851 rerun.
Avoid 5g mini, N-suffixed alternate editions, generic/unassigned photos.
Internal QA only. User-owned inventory edition and photo rights still HOLD.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,re,hashlib

R=Path("qa-review")
OLD=R/"v2851-clio-giftset-five-option-variant-photo-QA"/"manifest.json"
OUT=R/"v2852-founwear-original-five-variant-alternative-merchant-QA"
assert OLD.exists() and not OUT.exists()
old=json.loads(OLD.read_text())
assert old["version"]=="v2851" and old["families"][0]["id"]=="pending-05"
assert old["families"][0]["photos_saved"]==0
OUT.mkdir(parents=True)
shades={"19C":"Light","19N":"Porcelain","21C":"Lingerie","21N":"Linen","23N":"Ginger"}
merchants=[
 {"name":"W Cosmetics AU","url":"https://wcosmetics.com.au/products/clio-kill-cover-founwear-cushion-the-original.js","size":700},
 {"name":"Holiholic KR","url":"https://holiholic.com/products/clio-kill-cover-founwear-cushion-the-original-refill.js","size":600},
 {"name":"Dodoskin","url":"https://www.dodoskin.com/products/clio-kill-cover-founwear-cushion-the-original-15g-x-2ea-original-refill.js","size":600},
 {"name":"Moona Store","url":"https://www.moona.store/products/kill-cover-founwear-cushion-the-original.js","size":600}
]
headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,image/png,image/jpeg,image/webp,*/*"}
sha=lambda b:hashlib.sha256(b).hexdigest()
def absolute(url):
 if isinstance(url,str) and url.startswith("//"): return "https:"+url
 if isinstance(url,str) and url.startswith("https://"):return url
 return None
def name(v):return re.sub(r"^#+","",re.sub(r"\s+"," ",str(v).strip())).strip()
report={"version":"v2852","baseline":"v2851","inventory_family":"pending-05",
 "product":"CLIO Kill Cover Founwear Cushion The Original",
 "expected_set":"15g compact + 15g refill",
 "stock_shades":list(shades.keys()),
 "excluded_nonstock_shades":True,
 "prior_v2851_and_all_other_QA_assets_unchanged":True,
 "original_published_11_families_untouched":True,
 "original_published_55_urls_untouched":True,
 "true_owned_stock_set_edition_verified":False,
 "photo_redistribution_rights_verified":False,
 "authentic_original_MK_logo_verified":False,
 "new_public_image_urls":0,"new_retail_approvals":0,
 "final_XLSX_shared":False,"merchants":[],"variants":[]}
saved={}
for merchant in merchants:
 audit={"name":merchant["name"],"source":merchant["url"],"status":"HOLD",
 "set_description_verified":False,"shade_photo_candidates":{}}
 try:
  res=requests.get(merchant["url"],headers=headers,timeout=20);res.raise_for_status()
  product=res.json()
  title=str(product.get("title","")).lower()
  if not all(w in title for w in ("founwear","original")) or any(x in title for x in ("mini","5g","royal","new founwear")):
   raise ValueError("wrong edition title: "+title[:160])
  raw=re.sub(r"<[^>]*>"," ",str(product.get("description","")))
  desc=re.sub(r"\s+"," ",raw).lower()
  audit["merchant_title"]=product.get("title")
  audit["set_description_verified"]=("refill" in title or "refill" in desc or "15g x 2" in desc or "15g*2" in desc or "15g+15g" in desc)
  audit["status"]="MERCHANT_PRODUCT_LOOKUP_OK"
  variants=product.get("variants",[])
  audit["merchant_variants"]=len(variants)
  for shade,label in shades.items():
   if shade in saved:
    audit["shade_photo_candidates"][shade]="ALREADY_STAGED_FROM_EARLIER_MERCHANT"
    continue
   expected=shade+" "+label
   # exact option name, not 21N Linen N or other edition suffix.
   match=[v for v in variants if name(v.get("title","")).lower()==expected.lower()]
   if shade=="21C":
    match=[v for v in variants if name(v.get("title","")).lower() in ("21c lingerie","21c langerie")]
   if len(match)!=1:
    audit["shade_photo_candidates"][shade]="EXACT_VARIANT_NOT_UNIQUE"
    continue
   v=match[0]
   rawimg=v.get("featured_image")
   if isinstance(rawimg,dict):link=rawimg.get("src")
   elif isinstance(rawimg,str):link=rawimg
   else:link=v.get("featured_media",{}).get("preview_image",{}).get("src") if isinstance(v.get("featured_media"),dict) else None
   link=absolute(link)
   if not link:
    audit["shade_photo_candidates"][shade]="NO_VARIANT_ASSIGNED_PHOTO"
    continue
   duplicate=False
   for other in variants:
    if other.get("id")==v.get("id"):continue
    img=other.get("featured_image")
    otheruri=absolute(img.get("src") if isinstance(img,dict) else img if isinstance(img,str) else None)
    if otheruri and otheruri.split("?")[0]==link.split("?")[0]:
     duplicate=True;break
   if duplicate:
    audit["shade_photo_candidates"][shade]="PHOTO_SHARED_ACROSS_VARIANTS"
    continue
   try:
    image_response=requests.get(link,headers=headers,timeout=22)
    image_response.raise_for_status()
    data=image_response.content
    if not 600<len(data)<8000000:raise ValueError("invalid photo data size")
    with Image.open(BytesIO(data)) as im:
     im.load();native=list(im.size)
     if min(native)<merchant["size"]:raise ValueError("native source below threshold "+str(native))
     photo=ImageOps.exif_transpose(im).convert("RGB")
    canvas=Image.new("RGB",(1080,1080),"white")
    fit=ImageOps.contain(photo,(1080,1080),Image.Resampling.LANCZOS)
    canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
    path=OUT/(shade+"-"+merchant["name"].split(" ")[0]+"-exact-product-1080-QA.jpg")
    canvas.save(path,"JPEG",quality=92,optimize=True)
    if path.stat().st_size>2000000:raise ValueError("JPEG >2MB")
    saved[shade]={"shade":shade,"shade_label":label,"merchant":merchant["name"],"merchant_product":audit["merchant_title"],
      "merchant_variant_id":v.get("id"),"merchant_variant_label":v.get("title"),
      "merchant_product_set_claim":audit["set_description_verified"],
      "source_url":link,"native_pixels":native,"source_sha256":sha(data),
      "rendered_file":path.name,"rendered_JPG_sha256":sha(path.read_bytes()),
      "rendered_JPG_bytes":path.stat().st_size,"status":"SHADE_ASSIGNED_PHOTO_SAVED_QA_ONLY_RETAIL_HOLD"}
    audit["shade_photo_candidates"][shade]="SAVED_INTERNAL_QA"
   except Exception as e:
    audit["shade_photo_candidates"][shade]="HOLD_FETCH_OR_IMAGE_QA:"+str(e)[:100]
 except Exception as exc:
  audit["status"]="HOLD_MERCHANT_ACCESS_OR_PRODUCT_IDENTITY"
  audit["error"]=str(exc)[:200]
 report["merchants"].append(audit)
 if len(saved)==len(shades):break
for shade,label in shades.items():
 report["variants"].append(saved.get(shade,{"shade":shade,"shade_label":label,"status":"HOLD_NO_EXACT_MERCHANT_SHADE_PHOTO"}))
report["shade_specific_QA_JPG_saved"]=len(saved)
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
contact=Image.new("RGB",(1670,840),"#f3f1ef")
d=ImageDraw.Draw(contact)
d.text((18,14),"v2852 Founwear Original 15g + refill | Five stock shades | Internal QA only",font=f(23,True),fill="#362f38")
for i,row in enumerate(report["variants"]):
 x=18+(i%3)*548;y=61+(i//3)*385
 if row.get("rendered_file"):
  with Image.open(OUT/row["rendered_file"]) as im:contact.paste(im.resize((330,330),Image.Resampling.LANCZOS),(x,y))
 else:
  d.rectangle((x,y,x+330,y+330),outline="#b3abb1",width=3)
  d.text((x+25,y+145),"HOLD SOURCE",font=f(23,True),fill="#8b7a82")
 d.text((x,y+334),shade if False else (row["shade"]+" "+row["shade_label"]),font=f(18,True),fill="#4b3f48")
contact.save(OUT/"v2852-five-stock-shade-contact-QA.jpg","JPEG",quality=82,optimize=True)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2852","saved":len(saved),"shades":{x["shade"]:x["status"] for x in report["variants"]},
 "source_merchants":len(report["merchants"]),"retail_approved":0},ensure_ascii=False))
