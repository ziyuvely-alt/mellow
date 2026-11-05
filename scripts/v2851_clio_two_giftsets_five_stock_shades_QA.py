#!/usr/bin/env python3
"""v2851 two CLIO cushion GIFT SET family stock-variant photo QA.
Only photos explicitly assigned to desired shade on merchandise listing.
Do not mistake 5g mini, 15g single, refill or sales gift for stock gift set.
Reuse v2797 5-scene source manifest, no photo resourcing for that gallery.
Not retail approval. No source or published image overwritten.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,hashlib,re

R=Path("qa-review")
OUT=R/"v2851-clio-giftset-five-option-variant-photo-QA"
assert not OUT.exists()
OUT.mkdir()
stock={
 "pending-05":{"title":"CLIO Kill Cover Founwear Cushion The Original (main + refill)","url":"https://lacosmetique.com.au/products/kill-cover-founwear-cushion-the-original.js",
  "shades":["19C","19N","21C","21N","23N"],"required":["founwear","original"],
  "reject":["mini","5g","royal edition"],"stock_packaging":"physical Korean stock gift set exact edition unverified"},
 "pending-06":{"title":"CLIO Kill Cover Mesh Glow Essential Cushion Gift Set","url":"https://clubclio.shop/products/clio-kill-cover-mesh-glow-cushion-set-refill.js",
  "shades":["19C","19N","21C","21N","23N"],"required":["mesh","glow"],
  "reject":["mini","5g"],"stock_packaging":"physical Korean stock essential edition and gift set contents unverified"},
}
orig=R/"v2797-clio-meshglow-five-distinct-official-photo-scenes-and-alpha-qa"/"manifest.json"
assert orig.is_file()
prior=json.loads(orig.read_text())
assert prior["five_distinct_1080_JPGs_saved"]==5 and prior["family"]=="pending-06"
sha=lambda b:hashlib.sha256(b).hexdigest()
header={"User-Agent":"Mozilla/5.0","Accept":"application/json,image/jpeg,image/png,image/webp,*/*"}
summary={
 "version":"v2851","baseline":"v2850",
 "inventory_families":["pending-05","pending-06"],
 "reused_without_copying":{"source":"v2797","pending_06_common_scenes_sha_preserved":True,"count":5},
 "prior_11_approved_groups_unchanged":True,"prior_55_public_URLs_unchanged":True,
 "new_approved_sales_groups":0,"original_MK_logo_authenticated":False,
 "source_photo_redistribution_rights_verified":False,"exact_owned_stock_edition_verified":False,
 "final_excel_shared":False,"source_images_modified":0,"families":[]}
for fid,req in stock.items():
 p=OUT/fid;p.mkdir()
 family={"id":fid,"intended_stock_family":req["title"],"intended_stock_options":req["shades"],
 "seller_product_json":req["url"],"source_product_status":"NOT_CHECKED",
 "stock_bundle_contents_independently_confirmed":False,
 "source_listing_is_identical_to_user_owned_stock":False,
 "variants":[]}
 try:
  r=requests.get(req["url"],timeout=22,headers=header);r.raise_for_status()
  data=r.json()
  title=str(data.get("title",""))
  norm=re.sub(r"\s+"," ",title.strip().lower())
  family["merchant_title"]=title
  if not all(word in norm for word in req["required"]) or any(x in norm for x in req["reject"]):
   raise ValueError("wrong product identity or mini edition: "+title[:150])
  raw_desc=re.sub(r"<[^>]*>"," ",str(data.get("description","")))
  desc=re.sub(r"\s+"," ",raw_desc).lower()
  family["merchant_product_id"]=data.get("id")
  family["merchant_title_identity_pass"]=True
  family["merchant_explicit_set_or_refill"]=("refill" in norm or "refill" in desc or "리필" in desc)
  if not family["merchant_explicit_set_or_refill"]:
   family["source_product_status"]="HOLD_NO_SET_OR_REFILL_INDICATION"
  else:
   family["source_product_status"]="POTENTIAL_SET_LISTING_REQUIRES_STOCK_EDITION_QA"
  variants=data.get("variants",[])
  family["merchant_variant_count"]=len(variants)
  if not isinstance(variants,list) or not variants:raise ValueError("no merchant variants")
  for shade in req["shades"]:
   matches=[v for v in variants if re.search(r"\b"+shade+r"\b",str(v.get("title","")),re.I)]
   row={"shade":shade,"match_count":len(matches),"status":"HOLD"}
   if len(matches)!=1:
    row["reason"]="SHADE_MISSING_OR_AMBIGUOUS";family["variants"].append(row);continue
   option=matches[0];row["merchant_variant_id"]=option.get("id")
   photo=option.get("featured_image")
   uri=photo.get("src") if isinstance(photo,dict) else photo if isinstance(photo,str) else None
   if not uri and isinstance(option.get("featured_media"),dict):
    uri=option["featured_media"].get("preview_image",{}).get("src")
   if not uri or not uri.startswith("https://"):
    row["reason"]="NO_MERCHANT_EXACT_SHADE_ASSIGNED_IMAGE";family["variants"].append(row);continue
   others=[]
   for v in variants:
    if v is option:continue
    other=v.get("featured_image")
    other_uri=other.get("src") if isinstance(other,dict) else other if isinstance(other,str) else None
    if other_uri and other_uri.split("?")[0]==uri.split("?")[0]:others.append(v.get("title"))
   if others:
    row.update({"status":"HOLD_SHARED_IMAGE_NOT_SHADE_SPECIFIC","other_shades":others})
    family["variants"].append(row);continue
   row["variant_image_url"]=uri
   try:
    rr=requests.get(uri,timeout=22,headers=header);rr.raise_for_status()
    if not (500<len(rr.content)<8_000_000):raise ValueError("invalid image bytes")
    with Image.open(BytesIO(rr.content)) as im:
     im.load();source_size=list(im.size)
     if min(source_size)<650:raise ValueError("small native photo "+str(source_size))
     original=ImageOps.exif_transpose(im).convert("RGB")
    canvas=Image.new("RGB",(1080,1080),"white")
    crop=ImageOps.contain(original,(1080,1080),Image.Resampling.LANCZOS)
    canvas.paste(crop,((1080-crop.width)//2,(1080-crop.height)//2))
    outname=f"{shade}-merch-exact-shade-JPG1080-QA.jpg"
    dest=p/outname
    canvas.save(dest,"JPEG",quality=93,optimize=True)
    assert dest.stat().st_size<2_000_000
    row.update({"status":"PHYSICAL_MERCHANT_VARIANT_PHOTO_QA_SAVED_RETAIL_HOLD","filename":str(dest.relative_to(OUT)),
      "source_size":source_size,"source_sha256":sha(rr.content),"rendered_sha256":sha(dest.read_bytes()),
      "jpeg_bytes":dest.stat().st_size,"original_rgb_unchanged_other_than_fit":True})
   except Exception as exc:
    row.update({"status":"HOLD_SOURCE_FETCH_OR_VALIDATION","error":str(exc)[:175]})
   family["variants"].append(row)
 except Exception as e:
  family["source_product_status"]="HOLD_MERCHANT_ITEM_OR_ACCESS"
  family["error"]=str(e)[:260]
  if not family["variants"]:family["variants"]=[{"shade":s,"status":"HOLD_MERCHANT_ITEM_OR_ACCESS"} for s in req["shades"]]
 family["photos_saved"]=sum(bool(r.get("filename")) for r in family["variants"])
 family["release_allowed"]=False
 summary["families"].append(family)
summary["total_variant_QA_JPGs_saved"]=sum(x["photos_saved"] for x in summary["families"])
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda s,b=False:ImageFont.truetype(bold if b else font,s)
for fam in summary["families"]:
 contact=Image.new("RGB",(1690,830),"#f3f1ef");d=ImageDraw.Draw(contact)
 d.text((20,14),fam["id"]+" | CLIO gift-set stock 5 shades | QA-only photos",font=f(27,True),fill="#332e39")
 for j,rec in enumerate(fam["variants"]):
  x=22+(j%3)*552;y=64+(j//3)*390
  if rec.get("filename"):
   with Image.open(OUT/rec["filename"]) as src:preview=src.resize((326,326),Image.Resampling.LANCZOS)
   contact.paste(preview,(x,y))
  else:
   d.rectangle((x,y,x+326,y+326),outline="#ae9da3",width=3)
   d.text((x+23,y+150),"SHADE PHOTO HOLD",font=f(18,True),fill="#887b82")
  d.text((x,y+330),rec["shade"]+"  "+rec["status"][:25],font=f(16),fill="#423741")
 contact.save(OUT/fam["id"]/"v2851-five-shades-visual-QA.jpg","JPEG",quality=83,optimize=True)
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2851","saved":summary["total_variant_QA_JPGs_saved"],
 "families":[{"fid":f["id"],"merchant":f.get("merchant_title"),"title_status":f["source_product_status"],
  "saved":f["photos_saved"],"shades":{r["shade"]:r["status"] for r in f["variants"]}} for f in summary["families"]],
 "sale_approved_new":0},ensure_ascii=False))
