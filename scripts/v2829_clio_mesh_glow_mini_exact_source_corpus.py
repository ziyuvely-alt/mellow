#!/usr/bin/env python3
"""v2829 NEW official exact-item photo sourcing for pending-04, CLIO KILL COVER
MESH GLOW ESSENTIAL CUSHION MINI 5g. DO NOT use pending-05 "THE ORIGINAL"
photos, full-size 15g gift sets, false MK logo, or old failed rectangular crops.

Append-only raw source photo candidates and contact sheets; no shade claim,
no publication, no final Excel. Official CLIO page goodsView/0000006954 is the
only Korean manufacturer 5g anchor. Merchant fallback must match exact product.
"""
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
import requests,json,re,hashlib,base64
from bs4 import BeautifulSoup
OUT=Path("qa-review/v2829-clio-mesh-glow-essential-mini5g-exact-official-source-corpus")
assert not OUT.exists();OUT.mkdir(parents=True)
SOURCES=[
 {"merchant":"CLIO Korean Official","url":"https://clubclio.co.kr/shop/goodsView/0000006954","type":"HTML","official":True},
 {"merchant":"Fresh Mask","url":"https://www.freshmask.ch/de/collections/clio/products/clio-kill-cover-mesh-glow-cushion-mini.js","type":"Shopify","official":False},
 {"merchant":"Korecare","url":"https://korecareglobal.com/products/clio-kill-cover-mesh-glow-cushion-mini.js","type":"Shopify","official":False},
]
HEAD={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0 Safari/537.36",
      "Accept":"text/html,application/json,image/avif,image/jpeg,image/png,*/*"}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(v,base):
 if not isinstance(v,str):return None
 v=v.replace(r"\/","/").strip().strip('"').strip("'")
 if v.startswith("//"):v="https:"+v
 if v.startswith("data:") or not v:return None
 if not v.startswith(("http:","https:","/")):return None
 u=urljoin(base,v)
 return u if urlsplit(u).scheme=="https" else None
def plausible(u):
 low=u.lower().split("?")[0]
 if any(s in low for s in ("icon","logo","sprite","badge","arrow","btn_","jquery","font","flags","payment","kakao")):return False
 return any(s in low for s in (".jpg",".jpeg",".png",".webp",".avif"))
report={"version":"v2829","baseline":"v2828","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g",
 "exact_clio_official_goods_id":"0000006954",
 "official_page":"https://clubclio.co.kr/shop/goodsView/0000006954",
 "official_5g_weight_source_verified":True,
 "expected_only_mini_options":["21C Lingerie","21N Linen","23N Ginger"],
 "do_not_use_full_size_19C_19N_as_mini_options":True,
 "merchant_probes":[],"photographs":[],
 "photo_reuse_rights_verified":False,"physical_owned_stock_edition_verified":False,
 "original_MK_logo_authenticated":False,
 "existing_11_approved_families_untouched":True,"existing_55_urls_untouched":True,
 "pending05_original_mini_shade_photos_unchanged":True,"prior_QA_photos_unchanged":True,
 "new_sales_approved":0,"final_excel_shared":False}
seen_uris=set();hashes=set()
for source in SOURCES:
 probe={"merchant":source["merchant"],"url":source["url"],"status":"HOLD_NO_IMAGES","images_saved":0}
 try:
  res=requests.get(source["url"],headers=HEAD,timeout=22)
  res.raise_for_status()
  urls=[]
  if source["type"]=="Shopify":
   data=res.json()
   title=str(data.get("title") or "")
   probe["title"]=title
   if not ("mesh glow" in title.lower() and "mini" in title.lower() and "cushion" in title.lower()):
    raise ValueError("Merchant product title does not match Mesh Glow Mini")
   if "5g" not in title.lower() and "5 g" not in title.lower():
    probe["title_lacks_5g"]="True; visual source QA cannot verify capacity"
   probe["variants"]=[str(x.get("title")) for x in data.get("variants",[])][:20]
   for item in data.get("images",[])[:35]:
    u=item if isinstance(item,str) else item.get("src") or item.get("url")
    v=normalize(u,source["url"])
    if v:urls.append(v)
  else:
   text=res.text
   title=(BeautifulSoup(text,"html.parser").title or {}).get_text(" ",strip=True) if "<title" in text.lower() else ""
   probe["title"]=title[:250]
   # Strong exact-title page anchor prevents full-size other product contamination.
   if "미니" not in text and "mini" not in text.lower():raise ValueError("Official page no longer identifies mini")
   if "5g" not in text.lower() and "5 g" not in text.lower():raise ValueError("Official page no longer advertises 5g")
   soup=BeautifulSoup(text,"html.parser")
   for elem in soup.select("meta[property='og:image'],meta[name='twitter:image'],img"):
    for attr in ("content","data-src","data-original","data-lazy-src","src","data-url"):
     value=elem.get(attr)
     if value:
      v=normalize(value,source["url"])
      if v:urls.append(v)
   # HTML JS may embed absolute images, dynamically escaped slashes included.
   urls+=re.findall(r'https?:(?://|\\/\\/)[^"\'\s<>]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\'\s<>]*)?',text,re.I)[:100]
  # Only images visibly from same product merchant page, never shade claim.
  urls=list(dict.fromkeys(u for x in urls if (u:=normalize(x,source["url"])) and plausible(u)))
  probe["discovered_urls"]=len(urls)
  for u in urls[:70]:
   if u in seen_uris:continue
   seen_uris.add(u)
   try:
    pic=requests.get(u,headers=HEAD,timeout=14)
    pic.raise_for_status()
    if len(pic.content)>12_000_000 or len(pic.content)<12000:continue
    with Image.open(BytesIO(pic.content)) as im:
     im.load()
     native=list(im.size)
     if min(native)<530:continue
     rgb=ImageOps.exif_transpose(im).convert("RGB")
    if native[0]>native[1]*3.5 or native[1]>native[0]*3.5:continue
    surface=Image.new("RGB",(1080,1080),"white")
    fit=ImageOps.contain(rgb,(1070,1070),Image.Resampling.LANCZOS)
    surface.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
    memory=BytesIO()
    surface.save(memory,"JPEG",quality=91,optimize=True,subsampling=0)
    binary=memory.getvalue()
    h=hashlib.sha256(binary).hexdigest()
    if h in hashes or len(binary)>=2_000_000:continue
    hashes.add(h)
    dst=OUT/f"{len(report['photographs'])+1:02d}-{source['merchant'].replace(' ','-')}-EXACT-ITEM-REFERENCE-QA.jpg"
    dst.write_bytes(binary)
    report["photographs"].append({"file":dst.name,"merchant":source["merchant"],
      "source_url":u,"native_dimensions":native,"sha256":h,
      "bytes":len(binary),"is_brand_official_source":source["official"],
      "shade_assignment":"NONE_BEFORE_MANUAL_VISUAL_QA",
      "image_looks_like_correct_5g_mini":"NOT_YET_VISUALLY_REVIEWED",
      "photo_licensed_for_shopee":"UNVERIFIED"})
    probe["images_saved"]+=1
    if probe["images_saved"]>=15:break
   except Exception as exc:
    probe.setdefault("skipped_download_examples",[])
    if len(probe["skipped_download_examples"])<4:probe["skipped_download_examples"].append(str(exc)[:135])
  probe["status"]="REFERENCE_PHOTOS_PERSISTED_VISUAL_QA_REQUIRED" if probe["images_saved"] else "HOLD_NO_HIGH_RES_PRODUCT_PHOTO"
 except Exception as err:
  probe["status"]="HOLD_ACCESS_OR_MISMATCH";probe["error"]=str(err)[:200]
 report["merchant_probes"].append(probe)
photos=report["photographs"]
for pg in range(max(1,(len(photos)+11)//12)):
 sub=photos[pg*12:(pg+1)*12]
 canvas=Image.new("RGB",(1750,76+max(1,(len(sub)+3)//4)*415),"#f1f1ef")
 d=ImageDraw.Draw(canvas)
 d.text((18,14),"v2829 CLIO MESH GLOW ESSENTIAL MINI 5g | UNFILTERED PHOTO PROOF | QA ONLY",font=ft(24,True),fill="#2e292f")
 for i,item in enumerate(sub):
  with Image.open(OUT/item["file"]) as im:
   tile=im.convert("RGB").resize((325,325),Image.Resampling.LANCZOS)
  x=16+(i%4)*437;y=59+(i//4)*415
  canvas.paste(tile,(x,y))
  d.text((x,y+333),f'{pg*12+i+1:02d} {item["merchant"][:18]}',font=ft(18),fill="#323032")
  d.text((x,y+357),"NO SHADE / RETAIL HOLD",font=ft(15),fill="#686365")
 proof=OUT/f"v2829-unfiltered-photo-source-proof-{pg+1}.jpg"
 canvas.save(proof,"JPEG",quality=83,optimize=True)
 (OUT/f"v2829-proof-{pg+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["new_distinct_encoded_photo_candidates"]=len(photos)
report["new_five_real_photo_sale_approved_sets"]=0
report["next_action"]="Inspect candidate product visuals; exclude full size, kit, old-generation, unrelated banners; retain exact miniature 5g-only scenes and never invent shade identity."
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2829","sources":len(SOURCES),
 "photo_candidates":len(photos),
 "merchants":[{"name":p["merchant"],"count":p["images_saved"],"state":p["status"]} for p in report["merchant_probes"]],
 "retail_approved":0}))
