#!/usr/bin/env python3
"""v2907 recover MISSHA US first-party source originals for two PDRN stock families.
Stage genuine photos for human QA. No commercial approval, no original asset changes.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageOps
import requests, json, hashlib, time

QA=Path("qa-review")
PRE=QA/"v2906-two-goodal-obge-official-source-photo-recovery-QA"/"stock30-incremental-state-v2906.json"
OUT=QA/"v2907-missha-pdrn-firstparty-twofamily-source-photo-QA"
assert PRE.exists() and not OUT.exists()
st=json.loads(PRE.read_text())
assert st["version"]=="v2906" and len(st["families"])==30
cases=[
 {"family":"pending-14","product":"MISSHA PDRN NAD+ Firming Repair Cream 70mL",
  "url":"https://misshaus.com/products/missha-official-pdrn-nad-firming-repair-cream",
  "known":["https://misshaus.com/cdn/shop/files/MS104031.png?v=1782920420&width=3840"],
  "stock_identity_note":"Official global and US photo reads 70mL; Japanese market calls 70g, do NOT copy JP units into KR listing."},
 {"family":"pending-13","product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
  "url":"https://misshaus.com/products/missha-official-pdrn-nad-firming-repair-serum",
  "known":["https://misshaus.com/cdn/shop/files/CopyofMS104056_grande.png?v=1782920372"],
  "stock_identity_note":"Official US photo reads 30mL; compare existing archived serum 30mL product generations and avoid source duplicates."}
]
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; manufacturer image QA)"})
OUT.mkdir(parents=True)
saved=0
records=[]
for case in cases:
 fdir=OUT/case["family"]; images=[]; errors=[]; discovered=list(case["known"])
 json_url=case["url"]+".js"
 try:
  rr=session.get(json_url,timeout=12);rr.raise_for_status()
  j=rr.json();title=str(j.get("title",""))
  if "pdrn" not in title.lower() and "firming repair" not in title.lower():raise ValueError("Product title mismatch")
  for pic in j.get("images",[])[:10]:
   raw=pic if isinstance(pic,str) else pic.get("src","")
   if isinstance(raw,str) and raw:discovered.append(raw)
 except Exception as e:errors.append("Shopify gallery JSON unavailable: "+str(e)[:155])
 used_url=set();fingerprints=[]
 for raw_url in discovered:
  if len(images)>=4:break
  url="https:"+raw_url if raw_url.startswith("//") else raw_url
  if not url.startswith("https://"):continue
  host=urlparse(url).hostname
  if host not in ("misshaus.com","www.misshaus.com"):continue
  key=url.split("?")[0]
  if key in used_url:continue
  used_url.add(key)
  try:
   resp=session.get(url,timeout=14);resp.raise_for_status()
   if urlparse(resp.url).hostname not in ("misshaus.com","www.misshaus.com"):raise ValueError("Redirect outside MISSHA US")
   b=resp.content
   if not 2000<len(b)<10_000_000:raise ValueError("Unexpected image bytes")
   photo=Image.open(BytesIO(b));photo.load()
   if photo.format not in ("PNG","JPEG","WEBP"):raise ValueError("Not product photograph")
   origformat=photo.format
   photo=ImageOps.exif_transpose(photo).convert("RGB")
   w,h=photo.size
   if min(w,h)<900:
    errors.append(f"Skipped low-native {w}x{h}: {key}")
    continue
   g=photo.resize((9,8),Image.Resampling.LANCZOS).convert("L")
   fingerprint="".join(str(int(g.getpixel((x,y))>g.getpixel((x+1,y)))) for y in range(8) for x in range(8))
   if any(sum(a!=b for a,b in zip(old,fingerprint))<5 for old in fingerprints):
    errors.append("Same visual gallery scene skipped: "+key);continue
   fingerprints.append(fingerprint)
   fdir.mkdir(exist_ok=True)
   ordinal=len(images)+1
   ex={"PNG":".png","JPEG":".jpg","WEBP":".webp"}[origformat]
   source=fdir/f"{ordinal:02d}-manufacturer-original{ex}";source.write_bytes(b)
   canvas=Image.new("RGB",(1080,1080),"white")
   scaled=ImageOps.contain(photo,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
   reference=fdir/f"{ordinal:02d}-manufacturer-1080-INTERNAL-QA.jpg"
   canvas.save(reference,"JPEG",quality=90,optimize=True,subsampling=0)
   assert reference.stat().st_size<2_000_000
   images.append({"source_url":url,"photo_page":case["url"],"original_path":str(source),
      "native_pixels":[w,h],"source_sha256":hashlib.sha256(b).hexdigest(),
      "reference_JPG":str(reference),"JPG_sha256":hashlib.sha256(reference.read_bytes()).hexdigest(),
      "scene_visual_check":"PENDING","stock_batch_match":"PENDING","original_MK_logo":"NOT_APPLIED","reuse_rights":"PENDING","retail_approved":False})
   saved+=1
  except Exception as e:errors.append("Attempt skipped: "+key+" "+str(e)[:180])
 entry={"family":case["family"],"product":case["product"],"manufacturer_page":case["url"],
       "photo_references_added":len(images),"original_images":images,"errors":errors,
       "physical_stock_note":case["stock_identity_note"],"release_status":"SOURCE_BYTES_INTERNAL_QA_ONLY"}
 records.append(entry)
 if images:
  s=st["families"][case["family"]]
  s["last_delta_version"]="v2907"
  s["release_status"]="MISSHA_FIRSTPARTY_SOURCE_CANDIDATES_SAVED_HOLD_VISUAL_STOCK_RIGHTS"
  s["latest_photo_QA_checkpoint"]=f"v2907 {len(images)} first-party high-native MISSHA US sources plus JPG internal references, stock edition and commercial rights hold."
if not saved:raise RuntimeError("MISSHA official source did not yield native >=900 bytes, preserve previous v2906, do not commit empty progress")
manifest={"version":"v2907","baseline":"v2906","new_original_image_count":saved,"new_1080_JPG_reference_count":saved,
 "reference_only":True,"old_11_published_families_unchanged":True,"verified_55_URLs_unchanged":True,
 "commercial_approval":False,"final_excel_shared":False,"cases":records}
st["version"]="v2907";st["baseline"]="v2906";st["new_sale_approvals"]=0;st["new_public_URLs"]=0;st["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2907.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2907","new_images":saved,"by_family":{x["family"]:x["photo_references_added"] for x in records}},ensure_ascii=False))
