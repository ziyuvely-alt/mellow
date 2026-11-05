#!/usr/bin/env python3
"""v2834 photo resolution recovery for ONLY CLIO Mesh Glow Essential Mini5g
21N Linen. Try untouched CDN original + shade-linked Shopify variants,
never synthesize color, upscale 480px and call it native high resolution,
or confuse CLIO Founwear with Mesh Glow Essential.

All candidate media is INTERNAL QA without redistribution permission.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import requests,hashlib,json,base64
OUT=Path("qa-review/v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe")
assert not OUT.exists()
OUT.mkdir(parents=True)
OLD=Path("qa-review/v2831-clio-mesh-glow-essential-mini-21C-21N-exact-shade-reference/21N-Linen-source-variant-labelled-photo-QA.jpg")
assert OLD.exists()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda sz,b=False:ImageFont.truetype(BOLD if b else FONT,sz)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
urlstem="https://bizweb.dktcdn.net/100/353/847/products/ava-san-pham-tren-website-25-3197fd52-4a2d-4b17-ae6b-96a905564ebf.jpg?v=1785052315773"
candidate_urls=[
("Tanpopo CDN unresized","EXACT_21N_ALREADY_VARIANT_LABELLED",urlstem),
("Tanpopo CDN 2048 mode","EXACT_21N_ALREADY_VARIANT_LABELLED",urlstem.replace("bizweb.dktcdn.net/","bizweb.dktcdn.net/thumb/2048x2048/"))
]
record={"version":"v2834","baseline":"v2833","family":"pending-04",
  "product":"CLIO Mesh Glow Essential Mini 5g","shade":"21N Linen",
  "prior_source_native_pixels":[480,480],
  "attempted_sources":[],"qualified_higher_native_reference_photos":[],
  "retail_approved":False,"photo_use_rights_verified":False,
  "actual_owned_stock_verified":False,"prior_photo_assets_modified":False,
  "older_11_retail_approved_families_unchanged":True,
  "original_55_published_urls_unchanged":True,"final_xlsx_shared":False}
HEAD={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/html,image/jpeg,image/png,image/webp,*/*"}
for merchant,shopify in [
 ("W Cosmetics Australia","https://wcosmetics.com.au/products/clio-kill-cover-mesh-glow-essential-cushion-mini.js"),
 ("La Cosmetique Australia","https://lacosmetique.com.au/products/kill-cover-mesh-glow-essential-cushion-mini-3-shades.js")
]:
 probe={"merchant":merchant,"url":shopify}
 try:
  r=requests.get(shopify,headers=HEAD,timeout=17);r.raise_for_status()
  j=r.json()
  title=str(j.get("title",""))
  if not ("mesh glow" in title.lower() and "mini" in title.lower()):
   raise ValueError(f"wrong CLIO cushion edition in merchant title: {title}")
  variants=[v for v in j.get("variants",[]) if "21n" in str(v.get("title","")).lower() or "linen" in str(v.get("title","")).lower()]
  probe["exact_21N_variants_found"]=len(variants)
  for v in variants:
   image=v.get("featured_image") or v.get("image")
   url=image.get("src","") if isinstance(image,dict) else (image if isinstance(image,str) else "")
   if url and url.startswith("//"):url="https:"+url
   if url:
    candidate_urls.append((merchant,"EXPLICIT_MERCHANT_21N_VARIANT_FEATURED_IMAGE",url))
  probe["status"]="SUCCESS" if variants else "NO_21N_VARIANT_FOUND"
 except Exception as ex:
  probe["status"]="HOLD_CATALOG_UNAVAILABLE_OR_WRONG_ITEM"
  probe["error"]=str(ex)[:240]
 record["attempted_sources"].append(probe)
seen=set()
for merchant,scope,url in candidate_urls:
 if url in seen:continue
 seen.add(url)
 entry={"merchant":merchant,"shade_scope":scope,"url":url}
 try:
  response=requests.get(url,headers=HEAD,timeout=17)
  response.raise_for_status()
  assert len(response.content)<8_000_000
  with Image.open(BytesIO(response.content)) as im:
   im.load()
   dims=list(im.size)
   rgb=ImageOps.exif_transpose(im).convert("RGB")
  entry["native_pixels"]=dims
  entry["native_larger_than_existing_480"]=min(dims)>480
  entry["native_adequate_for_1080_hero"]=min(dims)>=800
  if min(dims)>=800:
   target=Image.new("RGB",(1080,1080),"white")
   photo=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   target.paste(photo,((1080-photo.width)//2,(1080-photo.height)//2))
   dest=OUT/f"{len(record['qualified_higher_native_reference_photos'])+1:02d}-21N-high-native-source-QA.jpg"
   target.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
   assert dest.stat().st_size<2_000_000
   entry["file"]=dest.name
   entry["JPG_sha256"]=sha(dest)
   record["qualified_higher_native_reference_photos"].append(entry.copy())
   entry["status"]="HIGH_NATIVE_PHOTO_STORED_NEEDS_VISUAL_AND_SHADE_ID_QA"
  else:entry["status"]="NO_UPGRADE_LOW_NATIVE_RESOLUTION"
 except Exception as e:
  entry["status"]="HOLD_DOWNLOAD_OR_DECODE"
  entry["error"]=str(e)[:230]
 record["attempted_sources"].append(entry)
font=ft(24,True)
maxp=min(3,len(record["qualified_higher_native_reference_photos"]))
board=Image.new("RGB",(1550,610),"#efeeee")
d=ImageDraw.Draw(board)
d.text((14,12),"v2834 CLIO Mesh Glow Mini 5g 21N | REAL NATIVE RESOLUTION PROBE",font=font,fill="#292929")
with Image.open(OLD) as im:
 thumb=im.convert("RGB").resize((345,345),Image.Resampling.LANCZOS)
board.paste(thumb,(15,78))
d.text((15,437),"Existing 480px-native source",font=ft(19),fill="#292929")
for idx,p in enumerate(record["qualified_higher_native_reference_photos"][:3]):
 with Image.open(OUT/p["file"]) as im:
  thumb=im.convert("RGB").resize((345,345),Image.Resampling.LANCZOS)
 x=400+idx*383
 board.paste(thumb,(x,78))
 d.text((x,437),f"Native {p['native_pixels']} / QA",font=ft(18),fill="#292929")
if maxp==0:
 d.text((420,130),"No independently verified 800px+",font=ft(23,True),fill="#523e42")
 d.text((420,176),"21N source upgrade recovered.",font=ft(23),fill="#523e42")
 d.text((420,240),"Keep v2833 21N marked LOW-RES QA HOLD.",font=ft(18),fill="#574950")
d.text((15,555),"REFERENCE ONLY | Not licensed for Shopee publishing | No photo regeneration",font=ft(19),fill="#5d5257")
proof=OUT/"v2834-res-upgrade-review.jpg"
board.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2834-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
record["higher_native_source_count"]=len(record["qualified_higher_native_reference_photos"])
record["status"]="HIGHER_NATIVE_PHOTOS_REQUIRE_VISUAL_VERIFICATION" if record["higher_native_source_count"] else "HOLD_NO_HIGHER_RES_PHOTO_AVAILABLE"
(OUT/"manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2834","high_native_references":record["higher_native_source_count"],
 "status":record["status"],"retail_approved":0}))
