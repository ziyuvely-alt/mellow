#!/usr/bin/env python3
"""v2935 one-pass Shopify exact SKU original photo discovery, never merchant use approved.
GOODAL serum mist 100mL and BIOHEAL NAD Glow Power Serum 30mL only.
No source/gallery images are reused in marketplace without authorization.
"""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha256
from urllib.parse import urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,time
Q=Path("qa-review")
P=Q/"v2934-bioheal-cream-four-real-source-scene-QA-only"
P20=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
OUT=Q/"v2935-two-new-retailer-exact-SKU-image-native-source-check-QA"
assert not OUT.exists()
state=json.loads((P/"stock30-incremental-state-v2934.json").read_text(encoding="utf-8"))
old=json.loads((P20/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2934" and len(state["families"])==30
byold={x["family"]:x for x in old["results"]}
T=[
 {"family":"pending-20","title":"GOODAL Green Tangerine Vita C Serum Mist 100mL",
  "json":"https://cnccanada.com/products/goodal-green-tangerine-vita-c-serum-mist-100ml.js",
  "require":["goodal","100ml","serum","mist"],"source":"C&C Cosmetics Shopify product"},
 {"family":"pending-24","title":"BIOHEAL BOH NAD PRIZCELL Glow Power Serum 30mL",
  "json":"https://k-touch.us/products/bio-heal-boh-nad-prizcell-glow-power-serum-30ml.js",
  "require":["bio","nad","power","serum"],"source":"K-Touch Shopify product"}
]
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def dhash(im):
 g=ImageOps.grayscale(ImageOps.fit(im,(9,8))).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def hdist(a,b):return sum(x!=y for x,y in zip(a,b))
def refs(fam):
 m=byold[fam];zpath=Path(m["zip_path"]);assert sha256(zpath.read_bytes()).hexdigest()==m["zip_sha256"]
 hashes=set();per=[]
 with ZipFile(zpath) as z:
  assert z.testzip() is None and len(z.namelist())==m["actual_original_source_jpgs_in_zip"]
  for name in z.namelist():
   b=z.read(name);hashes.add(sha256(b).hexdigest())
   with Image.open(BytesIO(b)) as im:per.append(dhash(im.convert("RGB")))
 return hashes,per
def card(fam,images):
 can=Image.new("RGB",(1080,1080),"#f7f7f8");d=ImageDraw.Draw(can)
 d.text((25,16),fam.upper()+" | NEW RETAILER IMAGE SOURCE CHECK",font=font(27),fill="#262626")
 d.text((25,57),"Unlicensed source references; retailer photos NOT authorized for resale ads",font=font(16),fill="#a33c3c")
 for i,z in enumerate(images[:4]):
  x=22+(i%2)*526;y=105+(i//2)*441
  d.rounded_rectangle((x,y,x+505,y+414),radius=10,fill="white",outline="#ccc",width=2)
  pic=ImageOps.contain(z["img"],(485,337),Image.Resampling.LANCZOS)
  can.paste(pic,(x+252-pic.width//2,y+8+(337-pic.height)//2))
  d.text((x+12,y+360),f"SOURCE {i+1} | {z['native'][0]}x{z['native'][1]}",font=font(16),fill="#333")
  d.text((x+12,y+389),"NOT VALIDATED FOR COMMERCIAL USE",font=font(14),fill="#a33c3c")
 d.text((23,1028),"Physical owned stock and official exact product generation remain unconfirmed.",font=font(16),fill="#555")
 return can
OUT.mkdir(parents=True)
sess=requests.Session();sess.headers.update({"User-Agent":"Mozilla/5.0 (noncommercial-original-image-source-audit)"})
results=[]
for cfg in T:
 fam=cfg["family"];hashes,per=refs(fam);errors=[];verified=False;title=None;urls=[]
 try:
  r=sess.get(cfg["json"],timeout=18);r.raise_for_status()
  payload=r.json();title=str(payload.get("title","")).strip()
  norm="".join(title.lower().replace("-","").replace(" ","").split())
  verified=all(q.replace(" ","") in norm for q in cfg["require"])
  if not verified:raise ValueError("Unexpected product title, no image URLs adopted: "+title[:130])
  for photo in payload.get("images",[])[:12]:
   u=photo.get("src","") if isinstance(photo,dict) else str(photo)
   if u.startswith("//"):u="https:"+u
   if u.startswith("https://") and u not in urls:urls.append(u)
 except Exception as ex:errors.append("exact SKU JSON read: "+str(ex)[:160])
 new=[];duplicate=0
 for u in urls[:12]:
  if len(new)>=4:break
  try:
   url=urlparse(u);host=url.hostname or ""
   if url.scheme!="https" or not (host=="cdn.shopify.com" or host in ("cnccanada.com","k-touch.us") or host.endswith(".myshopify.com")):
    raise ValueError("image URL host not from retailer's Shopify storefront")
   r=sess.get(u,timeout=15);r.raise_for_status()
   if urlparse(r.url).hostname not in ("cdn.shopify.com","cnccanada.com","k-touch.us"):raise ValueError("untrusted redirect")
   b=r.content
   if not 4000<len(b)<10000000:raise ValueError("invalid product image bytes")
   source=Image.open(BytesIO(b));source.load()
   if source.format not in ("JPEG","PNG","WEBP"):raise ValueError("unsupported image file")
   rgb=ImageOps.exif_transpose(source).convert("RGB")
   native=list(rgb.size)
   if min(native)<900:raise ValueError(f"native min dimension below 900: {native}")
   if max(native)/min(native)>1.7:raise ValueError("tall promotional banner not a product photo")
   sha=sha256(b).hexdigest();p=dhash(rgb)
   near=min([hdist(p,x) for x in per+[z["dhash"] for z in new]],default=64)
   if sha in hashes or any(z["sha256"]==sha for z in new) or near<6:
    duplicate+=1;continue
   i=len(new)+1;sub=OUT/fam;sub.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[source.format]
   raw=sub/f"{i:02d}-retailer-SKU-gallery-source-REFERENCE-ONLY{ext}";raw.write_bytes(b)
   frame=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   frame.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   preview=sub/f"{i:02d}-source-1080-internal-visual-review.jpg"
   frame.save(preview,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(preview) as test:assert test.format=="JPEG" and test.size==(1080,1080)
   assert preview.stat().st_size<2000000
   new.append({"img":rgb,"dhash":p,"sha256":sha,"native":native,
    "retailer_original_url":u,"raw_path":str(raw),"preview_path":str(preview),
    "preview_sha256":sha256(preview.read_bytes()).hexdigest(),
    "nearest_existing_hamming":near,"photo_rights_to_reuse":False,
    "visual_claims_checked":False,"actual_inventory_edition_verified":False,"retail_approved":False})
  except Exception as ex:errors.append("image skipped "+u.split("/")[-1][:30]+": "+str(ex)[:145])
 contact=None
 if new:
  contact=OUT/(fam+"-unseen-shopify-native-source-QA.jpg")
  card(fam,new).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
 st=state["families"][fam]
 st.update({"last_delta_version":"v2935",
  "release_status":"UNLICENSED_RETAIL_GALLERY_NEW_SOURCE_QA_HOLD" if new else "RETAIL_PRODUCT_PAGE_CHECKED_NO_VALID_NEW_DISTINCT_SOURCE",
  "v2935_new_product_source_references":len(new),
  "v2935_source_visual_contact":str(contact) if contact else None,
  "latest_photo_QA_checkpoint":f"v2935 exact Shopify title verified={verified}; {len(new)} native image source candidates, {duplicate} duplicates, retailer commercial reuse rights, user physical stock edition and claims held.",
  "sale_approved":False})
 results.append({"family":fam,"source_page_json":cfg["json"],"title":title,
  "verified_product_name":verified,"urls_seen":len(urls),"new_source_photos":len(new),
  "near_duplicates_skipped":duplicate,
  "visual_contact":str(contact) if contact else None,
  "photos":[{k:v for k,v in z.items() if k not in ("img","dhash")} for z in new],
  "errors":errors[:12],"approved_for_marketplace":False})
manifest={"version":"v2935","baseline":"v2934","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "product_families_attempted":2,"new_unlicensed_native_product_refs":sum(x["new_source_photos"] for x in results),
 "old_11_families_changed":0,"old_55_verified_public_urls_changed":0,
 "original_images_changed":0,"retail_approvals":0,"new_public_urls":0,
 "final_spreadsheet_shared":False,"results":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2935";state["baseline"]="v2934";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2935.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"v":"v2935","new_candidate_photos":manifest["new_unlicensed_native_product_refs"],
 "by_family":{r["family"]:r["new_source_photos"] for r in results},"retail_approvals":0},ensure_ascii=False))
