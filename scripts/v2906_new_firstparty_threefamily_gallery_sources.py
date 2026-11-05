#!/usr/bin/env python3
"""v2906 new official-source photo acquisition, never repaint existing QA or publish."""
from pathlib import Path
from io import BytesIO
import hashlib, json, re, time
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps

ROOT=Path("qa-review")
PRE=ROOT/"v2905-obge-finisher5g-five-official-no-unverified-MK-internal-QA"/"stock30-incremental-state-v2905.json"
OUT=ROOT/"v2906-two-goodal-obge-official-source-photo-recovery-QA"
assert PRE.is_file() and not OUT.exists()
state=json.loads(PRE.read_text())
assert state["version"]=="v2905" and len(state["families"])==30
requests_session=requests.Session()
requests_session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; QA original-image-source verification)"})
TARGETS=[
 {"family":"pending-21","product":"GOODAL Green Tangerine Vita C Eye Cream, silver cap edition unverified",
  "brand_page":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-dark-circle-eye-cream",
  "shopify_json":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-dark-circle-eye-cream.js",
  "first_party_fallback":["https://clubclio.shop/cdn/shop/files/1_30e9f92e-4405-4f2f-894f-b5d078b75cc5.jpg?v=1772779151"]},
 {"family":"pending-19","product":"GOODAL Green Tangerine Vita C Care Cream Advanced version, owned 25AD unverified",
  "brand_page":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-cream-advanced-ver",
  "shopify_json":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-cream-advanced-ver.js",
  "first_party_fallback":[]},
 {"family":"pending-22","product":"OBgE Max Waterful Sun Cream 300mL, owned bottle size unverified",
  "brand_page":"https://m.obge.co.kr/product/detail.html?product_no=1251",
  "shopify_json":None,
  "first_party_fallback":["https://m.obge.co.kr/web/product/small/202603/95c2bcbeb8bf7bfa5b3d3b055e3a87d9.png"]}
]
ALLOWED={"clubclio.shop","m.obge.co.kr","www.obge.co.kr"}
manifest={"version":"v2906","baseline":"v2905","reference_only":True,"run_timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
"new_verified_sales_approvals":0,"new_public_URLs":0,"new_marketing_images":0,"old_approved_11_families_untouched":True,"old_55_URLs_untouched":True,"prior_QA_files_untouched":True,"families":[]}
OUT.mkdir(parents=True)
distinct_sources=0
for target in TARGETS:
 family=target["family"]
 fdir=OUT/family
 items=[]
 errors=[]
 urls=[]
 if target["shopify_json"]:
  try:
   rr=requests_session.get(target["shopify_json"],timeout=12)
   rr.raise_for_status()
   data=rr.json()
   title=str(data.get("title",""))
   if not any(x in title.lower() for x in ("eye cream","vita c","tangerine","goodal")):
    raise ValueError("unexpected official product JSON title: "+title[:100])
   for im in data.get("images",[])[:8]:
    if isinstance(im,str):urls.append(im)
    elif isinstance(im,dict) and isinstance(im.get("src"),str):urls.append(im["src"])
  except Exception as exc:errors.append("JSON discovery unavailable: "+str(exc)[:200])
 urls=target["first_party_fallback"]+urls
 dedup=set()
 seen_dhash=[]
 for url in urls:
  if url.startswith("//"):url="https:"+url
  if not url.startswith("https://"):continue
  host=urlparse(url).hostname
  if host not in ALLOWED:continue
  clean_id=url.split("?")[0]
  if clean_id in dedup:continue
  dedup.add(clean_id)
  if len(items)>=4:break
  try:
   res=requests_session.get(url,timeout=13,allow_redirects=True)
   res.raise_for_status()
   if urlparse(res.url).hostname not in ALLOWED:raise ValueError("unexpected redirected host")
   b=res.content
   if len(b)>8_000_000 or len(b)<2048:raise ValueError("unexpected source byte count")
   raw=Image.open(BytesIO(b));raw.load()
   if raw.format not in ("JPEG","PNG","WEBP"):raise ValueError("nonimage download")
   rgb=ImageOps.exif_transpose(raw).convert("RGB")
   w,h=rgb.size
   if w<900 or h<900:
    errors.append("Native below 900: "+clean_id[:100]+" "+str([w,h]))
    continue
   tiny=rgb.resize((9,8))
   gray=tiny.convert("L")
   dhash=''.join("1" if gray.getpixel((x,y))>gray.getpixel((x+1,y)) else "0" for y in range(8) for x in range(8))
   if any(sum(a!=b for a,b in zip(dhash,old))<5 for old in seen_dhash):
    errors.append("near-duplicate gallery viewpoint excluded: "+clean_id[:95]);continue
   seen_dhash.append(dhash)
   index=len(items)+1
   stem=f"{index:02d}-firstparty-candidate"
   raw_ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[raw.format]
   fdir.mkdir(parents=True,exist_ok=True)
   raw_path=fdir/(stem+"-original"+raw_ext)
   raw_path.write_bytes(b)
   # Only for internal inspection: no edited package artwork, no badge, no fabricated product.
   canvas=Image.new("RGB",(1080,1080),"white")
   contained=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
   jpg_path=fdir/(stem+"-1080-reference-QA.jpg")
   canvas.save(jpg_path,quality=90,optimize=True,subsampling=0)
   assert jpg_path.stat().st_size<2_000_000
   with Image.open(jpg_path) as chk:assert chk.size==(1080,1080) and chk.format=="JPEG"
   items.append({"source_url":url,"brand_page":target["brand_page"],"raw_path":str(raw_path),"raw_sha256":hashlib.sha256(b).hexdigest(),
    "native_pixels":[w,h],"original_format":raw.format,"jpeg_reference":str(jpg_path),
    "jpeg_sha256":hashlib.sha256(jpg_path.read_bytes()).hexdigest(),"dhash":dhash,
    "claimed_distinct_original_photo_scene":False,"product_edition_visual_QA":False,
    "existing_2026_photo_derivative_check_required":True,
    "commercial_redistribution_rights_verified":False,"sale_ready":False})
   distinct_sources+=1
  except Exception as exc:errors.append("source skipped: "+clean_id[:85]+" "+str(exc)[:140])
 entry={"family":family,"product":target["product"],"official_page":target["brand_page"],
        "source_candidates_saved":len(items),"items":items,"errors":errors[:12],
        "next_action":"Inspect full 1080 references against exact owned package and prior photos; permission before any retail or public upload"}
 manifest["families"].append(entry)
 if items:
  state["families"][family]["last_delta_version"]="v2906"
  state["families"][family]["v2906_new_first_party_reference_count"]=len(items)
  state["families"][family]["release_status"]="NEW_BRAND_SOURCE_REFERENCES_ARCHIVED_ONLY_HOLD_EDITION_RIGHTS_VISUAL"
  state["families"][family]["latest_photo_QA_checkpoint"]=f"v2906 {len(items)} newly fetched first-party native >=900 references staged; independent scene/source vs prior gallery, physical owned edition and commercial use permission unverified."
manifest["new_source_photo_originals_downloaded"]=distinct_sources
manifest["new_1080_reference_JPGs"]=distinct_sources
manifest["raw_source_JPGs_are_sale_ready"]=False
manifest["final_excel_shared"]=False
if distinct_sources==0:raise RuntimeError("No genuinely new official native >=900 image acquired; do not write empty checkpoint")
state["version"]="v2906";state["baseline"]="v2905";state["new_sale_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2906.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2906","new_first_party_native_sources":distinct_sources,"by_family":{x["family"]:x["source_candidates_saved"] for x in manifest["families"]},"commercial_approvals":0},ensure_ascii=False))
