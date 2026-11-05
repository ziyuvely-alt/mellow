#!/usr/bin/env python3
"""v2879 direct Shopify-CDN 26AD source image recovery after v2878 Hwahae
product-HTML returned zero shade photos.

Only download already surfaced exact URLs from Ballagrio 4g 'Mood Glowy
Tint' (NOT 'Ink Mood Glowy Tint') and optionally crosswalk product variants
to actual variant featured image URL via live Shopify JSON. Never label an
unlinked gallery filename as a specific shade. No resynthesis, no
unverified source rights claims, no sales publication or original changes.
01..20 stock option scope, 04/06/07 keep, 14 Korean brand name '로지위시'
but raw stock '로지워시' is NOT edited.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
from hashlib import sha256
from io import BytesIO
from urllib.request import urlopen,Request
from urllib.parse import urlparse
import json, re

R=Path("qa-review")
OUT=R/"v2879-peripera26ad-direct-CDN-and-shopify-variant-QA"
prior=json.loads((R/"v2878-peripera-26AD-20-shade-exact-edition-original-photo-QA"/"manifest.json").read_text())
assert prior["version"]=="v2878" and prior["n_26AD_exact_edition_photo_candidates"]==0
assert prior["n_inventory_options"]==20 and not OUT.exists()
OUT.mkdir(parents=True)
PRODUCT="https://www.ballagrio.com/products/peripera-mood-glowy-tint-4g"
BASE="https://www.ballagrio.com/cdn/shop/files/"
SOURCES=[
 {"role":"common-real-new-tube-with-applicator",
  "url":BASE+"peripera-mood-glowy-tint-4g-01_1024x1024.jpg?v=1777339704",
  "source_page":PRODUCT,
  "spec":"Mood Glowy Tint 4g, embossed peripera cylindrical new tube; no specific numbered variant claim"},
 {"role":"real-8-shade-lip-swatches",
  "url":BASE+"peripera-mood-glowy-tint-4g-14.jpg?v=1777339704",
  "source_page":PRODUCT,
  "spec":"real labeled shade chart including 01 05 11 19 12 13 16 17; NOT standalone tube images"}
]
NAME_MAP={
 "01":"Tiny Strawberry","02":"Coral Chemistry","03":"Juicy Peach",
 "04":"Anyway Peach","05":"Baby Fairy","06":"Pink Youth",
 "07":"Plum Fizz","08":"Joking Pink","09":"Rose in Mind",
 "10":"Bare Pink","11":"Visual Pink","12":"Campus Queen",
 "13":"Mood Queen","14":"Rosy Wish","15":"My Pick Rose",
 "16":"Rose-pick","17":"Blush Fig","18":"Coral Influencer",
 "19":"Cherry So What","20":"Brown Yakgwa"}
U="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
def sha(p):return sha256(p.read_bytes()).hexdigest()
def get(url,limit=8_000_000):
 r=Request(url,headers={"User-Agent":U,"Accept":"image/webp,image/jpeg,image/png,application/json,*/*"})
 with urlopen(r,timeout=18) as s:
  b=s.read(limit+1)
 assert len(b)<=limit and len(b)>100
 return b
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
result=[];frames=[]
for src in SOURCES:
 row={"role":src["role"],"url":src["url"],"page":src["source_page"],
      "status":"HOLD_SOURCE_FETCH","linked_exact_stock_shade":None,
      "commercial_photo_rights_verified":False,"retail_approved":False}
 try:
  b=get(src["url"])
  with Image.open(BytesIO(b)) as p:
   p.load()
   assert p.format in ("JPEG","PNG","WEBP")
   assert min(p.size)>=480
   original=p.convert("RGB")
   size=list(p.size);form=p.format
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[form]
  stored=OUT/(src["role"]+"-original-source-unaltered."+ext)
  stored.write_bytes(b)
  c=Image.new("RGB",(1080,1080),"#FBFAFD")
  d=ImageDraw.Draw(c)
  d.rounded_rectangle((36,36,1044,1044),radius=24,outline="#E2D8E2",width=2)
  d.text((66,64),"peripera | MOOD GLOWY TINT 4g",font=ft(33,True),fill="#433847")
  d.text((66,121),"26AD MODEL REFERENCE  /  "+src["role"][:40],font=ft(20),fill="#62576A")
  d.line((65,161,1016,161),fill="#D6CCD8",width=3)
  shown=ImageOps.contain(original,(940,770),Image.Resampling.LANCZOS)
  c.paste(shown,((1080-shown.width)//2,183+(770-shown.height)//2))
  d.text((67,971),"ORIGINAL SOURCE PHOTO  |  SHADE LABEL NOT INFERRED",font=ft(18,True),fill="#746679")
  jpg=OUT/(src["role"]+"-1080-internal-QA.jpg")
  c.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  with Image.open(jpg) as p:
   p.load();assert p.size==(1080,1080) and p.format=="JPEG"
  assert jpg.stat().st_size<2_000_000
  row.update(status="ORIGINAL_NEW_EDITION_SOURCE_SAVED_GALLERY_ONLY",
    product_edition="Mood Glowy Tint 4g (26AD candidate)",
    original_file=str(stored),raw_sha256=sha(stored),native_size=size,
    img_format=form,qa_1080=str(jpg),qa_sha256=sha(jpg),
    pixels_recolored=False,merchant_version_visual_requires_review=True)
  frames.append((src["role"],c))
 except Exception as e:
  row.update(status="HOLD_DIRECT_CDN_UNAVAILABLE",reason=type(e).__name__+": "+str(e)[:220])
 result.append(row)
# Shopify product JSON, one endpoint only; no re-trying Javascript/HTML
# scraping after v2878. Restrict variant associations to actual assigned
# images and exact shade title, not a -01 filename in shared gallery.
PRODUCT_JSON=PRODUCT+".js"
shopify={"url":PRODUCT_JSON,"status":"HOLD_PRODUCT_JSON_UNAVAILABLE",
  "detected_variants":[],"per_shade_photo_candidates":[]}
try:
 d=json.loads(get(PRODUCT_JSON,2_300_000).decode("utf-8"))
 assert "variants" in d and "images" in d
 shopify["status"]="SHOPIFY_JSON_VERIFIED"
 shopify["product_title"]=str(d.get("title",""))[:200]
 assert "Mood Glowy Tint" in shopify["product_title"] and "Ink" not in shopify["product_title"],"WRONG_EDITION_SHOPIFY"
 images={str(i.get("id")):i for i in d.get("images",[]) if isinstance(i,dict)}
 shade_map={}
 for v in d["variants"]:
  t=str(v.get("title") or v.get("option1") or "")
  m=re.match(r"^\s*#?(\d{1,2})\s*[-. ]\s*(.+)$",t)
  shade=f"{int(m.group(1)):02d}" if m else None
  if shade not in NAME_MAP:continue
  expected=NAME_MAP[shade].replace("-","").lower().replace(" ","")
  candidate=(m.group(2) if m else "").replace("-","").lower().replace(" ","")
  match=expected in candidate or candidate in expected
  if not match: continue
  photo=v.get("featured_image") or {}
  if not isinstance(photo,dict):photo={}
  key=photo.get("id") or v.get("image_id")
  if not photo and key:photo=images.get(str(key),{})
  image_url=(photo.get("src") or "")
  shopify["detected_variants"].append({"shade":shade,"variant_id":v.get("id"),
     "title":t,"image_assigned":bool(image_url),
     "actual_associated_image_url":image_url or None})
  if image_url and shade not in shade_map:shade_map[shade]=image_url
 # Only actual associated photos, no gallery index/filename inference.
 for shade,u in shade_map.items():
  proof={"shade":shade,"source_url":u,"status":"HOLD_SOURCE",
      "retail_approved":False,"commercial_image_rights_verified":False}
  if len(shopify["per_shade_photo_candidates"])>=20:break
  try:
   assert urlparse(u).scheme=="https" and "cdn.shopify.com" in u or ("ballagrio.com" in u and u.startswith("https://"))
   raw=get(u)
   with Image.open(BytesIO(raw)) as im:
    im.load();assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=500
    ph=im.convert("RGB");nat=list(im.size);fmt=im.format
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[fmt]
   p=OUT/f"26AD-{shade}-actual-Shopify-variant-source.{ext}"
   p.write_bytes(raw)
   qa=Image.new("RGB",(1080,1080),"white")
   dd=ImageDraw.Draw(qa)
   dd.text((48,38),f"26AD No.{shade} {NAME_MAP[shade]} / VARIANT-PHOTO QA",font=ft(23,True),fill="#4D3F50")
   show=ImageOps.contain(ph,(960,910),Image.Resampling.LANCZOS)
   qa.paste(show,((1080-show.width)//2,96+(910-show.height)//2))
   out=OUT/f"26AD-{shade}-Shopify-variant-1080-QA.jpg"
   qa.save(out,"JPEG",quality=92,optimize=True)
   proof.update(status="CANDIDATE_VARIANT_LINKED_PHOTO_QA_HOLD",
      exact_assigned_variant=True,source_photo=str(p),source_sha256=sha(p),
      pixels_original_not_recolored=True,native_size=nat,qa_JPG=str(out),qa_sha256=sha(out))
  except Exception as e:proof.update(status="HOLD_IMAGE_UNAVAILABLE",reason=str(e)[:170])
  shopify["per_shade_photo_candidates"].append(proof)
except Exception as e:
 shopify.update(status="HOLD_SHOPIFY_JSON_UNAVAILABLE_NO_RETRY",reason=type(e).__name__+": "+str(e)[:250])
# Compare visual sources without treating swatch chart as isolated tubes.
if frames:
 board=Image.new("RGB",(1080*len(frames)+30,1140),"#F2EDF3")
 d=ImageDraw.Draw(board)
 d.text((20,13),"v2879 NEW MOOD GLOWY 4g | DIRECT CDN ORIGINALS | INTERNAL QA NOT SALES",font=ft(23,True),fill="#463847")
 for j,(label,img) in enumerate(frames):board.paste(img,(16+1080*j,53))
 cpath=OUT/"v2879-source-original-tube-and-real-swatch-contact-QA.jpg"
 board.save(cpath,"JPEG",quality=88,optimize=True)
else:cpath=None
# Preserve all 20 inventory options, no old alpha may be used.
per_shade=[]
for i in range(1,21):
 shade=f"{i:02d}"
 real=next((x for x in shopify.get("per_shade_photo_candidates",[])
            if x["shade"]==shade and x["status"].startswith("CANDIDATE")),None)
 per_shade.append({"shade":shade,"expected_26AD_EN":NAME_MAP[shade],
   "oliveyoung_exclusive_in_other_retailer":["04","06","07"].__contains__(shade),
   "verified_26AD_variant_photo":real,
   "status":"SHADE_PHOTO_CANDIDATE_HOLD_RIGHTS" if real else "NO_SHADE_LINKED_PRODUCT_IMAGE_YET",
   "never_use_legacy_ink_mood_photo":True})
assert len(per_shade)==20
m={"version":"v2879","baseline":"v2878","family":"pending-08",
   "product":"peripera Mood Glowy Tint 26AD 4g",
   "direct_CDN_photo_sources_attempted":len(SOURCES),
   "direct_CDN_sources_saved":sum(x["status"].startswith("ORIGINAL") for x in result),
   "confirmed_variant_associated_photo_candidates":sum(x["status"].startswith("CANDIDATE") for x in shopify["per_shade_photo_candidates"]),
   "cdn_assets":result,"shopify":shopify,
   "stock_20_shades":per_shade,"new_contact":str(cpath) if cpath else None,
   "legacy_ink_mood_twenty_photos_quarantined":True,
   "current_user_scope_01_to_20_unchanged":True,
   "stock_04_06_07_oliveyoung_exclusive_retained":True,
   "stock_14_name_raw_not_modified":True,
   "new_sales_approvals":0,"new_public_urls":0,
   "prior_11_completed_groups_unchanged":True,
   "prior_55_public_urls_unchanged":True,
   "all_source_RGB_unchanged":True,
   "external_photo_reuse_rights_verified":False,
   "user_owned_product_26AD_edition_proven":False,
   "final_spreadsheet_shared":False,
   "next":"Inspect exact Shopify source product and swatch chart at 100%. If variant-specific photos are assigned, verify shade labels by visual QA before use; 04/06/07 OliveYoung source separate. No legacy Ink photo substitution."
}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2879","new_CDN_sources":m["direct_CDN_sources_saved"],
    "associated_variant_photo_candidates":m["confirmed_variant_associated_photo_candidates"],
    "shopify_status":shopify["status"],"sales":0}))
