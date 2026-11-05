#!/usr/bin/env python3
"""v2937: two genuinely new Goodal Serum Mist 100mL photo scenes, source-only QA.
Historic 3 photo bytes are unmodified. Only images from the confirmed 100mL
single-SKU Oceanbuy listing are fetched. All photos remain unlicensed INTERNAL QA.
"""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile,ZIP_STORED
from hashlib import sha256
from urllib.parse import urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,time

Q=Path("qa-review")
B=Q/"v2936-bioheal-serum-five-source-original-byte-QA-not-retail"
V20=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
OUT=Q/"v2937-goodal-serummist-100ml-two-unique-action-and-still-photo-source-QA"
assert not OUT.exists()
st=json.loads((B/"stock30-incremental-state-v2936.json").read_text(encoding="utf-8"))
s20=json.loads((V20/"manifest.json").read_text(encoding="utf-8"))
assert st["version"]=="v2936" and len(st["families"])==30
fam="pending-20"
previous=next(x for x in s20["results"] if x["family"]==fam)
assert previous["actual_original_source_jpgs_in_zip"]==3
sku_page="https://oceanbuy.ca/products/goodal-green-tangerine-vita-c-serum-mist-100ml"
photos=[
 {"role":"GOODAL_100ML_CITRUS_PRODUCT_STILL","source_url":"https://oceanbuy.ca/cdn/shop/products/goodal-goodal-green-tangerine-vita-c-serum-mist-100ml-154746.jpg?v=1745717232&width=1800",
  "visually_reviewed_subject":"One same-generation 100mL GOODAL mist bottle on yellow set with two cut/whole tangerines; no other products"},
 {"role":"GOODAL_100ML_FINGERTIP_MIST_USE","source_url":"https://oceanbuy.ca/cdn/shop/files/goodal-goodal-green-tangerine-vita-c-serum-mist-100ml-oceanbuy-beauty-592499.webp?v=1745785888&width=1080",
  "visually_reviewed_subject":"GOODAL 100mL spray nozzle pressed by hand against blue backdrop with mist dispersal, same yellow nozzle label"}]
def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def dhash(rgb):
 g=ImageOps.grayscale(ImageOps.fit(rgb,(9,8))).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def distance(x,y):return sum(a!=b for a,b in zip(x,y))
def frame(data):
 with Image.open(BytesIO(data)) as im:
  im.load()
  assert im.format in ("JPEG","PNG","WEBP")
  rgb=ImageOps.exif_transpose(im).convert("RGB")
  return rgb,im.format,list(im.size)
def preview_image(photos):
 sheet=Image.new("RGB",(1080,1080),"#f7f7f8");draw=ImageDraw.Draw(sheet)
 draw.text((28,18),"GOODAL SERUM MIST 100mL | NEW SCENES v2937",font=font(26),fill="#222222")
 draw.text((28,57),"Original source photos only; existing three images and 55 URLs preserved",font=font(16),fill="#9e3333")
 for i,v in enumerate(photos):
  x=25+i*528;y=111
  draw.rounded_rectangle((x,y,x+505,y+830),radius=12,fill="white",outline="#ccc",width=2)
  item=ImageOps.contain(v["rgb"],(487,688),Image.Resampling.LANCZOS)
  sheet.paste(item,(x+252-item.width//2,y+18+(688-item.height)//2))
  draw.text((x+14,y+726),v["role"][:35],font=font(16),fill="#333333")
  draw.text((x+14,y+761),f"Original {v['native'][0]}x{v['native'][1]}",font=font(17),fill="#555555")
 draw.text((28,984),"Product/usage and exact owned stock generation must be checked before listing.",font=font(17),fill="#8c3333")
 draw.text((28,1024),"Retail image rights not granted • No original source edited",font=font(16),fill="#8c3333")
 return sheet
path=Path(previous["zip_path"])
assert sha256(path.read_bytes()).hexdigest()==previous["zip_sha256"]
oldhash=[];oldsha=set();oldbytes=[]
with ZipFile(path) as z:
 assert z.testzip() is None and len(z.namelist())==3
 for f in z.namelist():
  b=z.read(f);im,format,native=frame(b)
  assert format=="JPEG" and native==[1080,1080]
  oldbytes.append(b);oldsha.add(sha256(b).hexdigest());oldhash.append(dhash(im))
OUT.mkdir(parents=True)
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (source-photo-integrity-audit)"})
errors=[];sku_page_verified=False;listing_title=""
try:
 r=session.get(sku_page,timeout=16);r.raise_for_status()
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(r.text,"html.parser")
 listing_title=soup.title.get_text(" ",strip=True) if soup.title else ""
 norm="".join(listing_title.lower().replace("-"," ").split())
 sku_page_verified=all(x in norm for x in ("goodal","100ml","serummist"))
 if not sku_page_verified:errors.append("Shopify listing title mismatch; not adopting photos")
except Exception as e:errors.append("listing fetch error "+str(e)[:150])
new=[]
if sku_page_verified:
 for cfg in photos:
  try:
   u=cfg["source_url"];p=urlparse(u)
   if p.scheme!="https" or p.hostname!="oceanbuy.ca" or "/cdn/shop/" not in p.path:raise ValueError("source not from declared listing")
   r=session.get(u,timeout=16);r.raise_for_status()
   if urlparse(r.url).hostname not in ("oceanbuy.ca","cdn.shopify.com"):raise ValueError("untrusted CDN redirect")
   b=r.content
   if not 4000<len(b)<9_000_000:raise ValueError("invalid bytes")
   rgb,fmt,native=frame(b)
   if min(native)<900:raise ValueError(f"native photo below 900px: {native}")
   if max(native)/min(native)>1.5:raise ValueError("possible elongated marketing infographic")
   ph=dhash(rgb);digest=sha256(b)
   close=min([distance(ph,h) for h in oldhash]+[distance(ph,z["dhash"]) for z in new],default=64)
   if digest in oldsha or any(digest==z["original_sha256"] for z in new) or close<6:
    errors.append(cfg["role"]+" duplicate source: hamming="+str(close));continue
   i=len(new)+1;folder=OUT/fam;folder.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[fmt]
   orig=folder/f"{i:02d}-100ml-real-scene-original-source-UNLICENSED{ext}";orig.write_bytes(b)
   # exact original source bytes preserved separately; 1080 square is QA only
   ref=folder/f"{i:02d}-100ml-original-framed-1080-INTERNAL-QA.jpg"
   canvas=Image.new("RGB",(1080,1080),"white")
   scaled=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
   canvas.save(ref,"JPEG",quality=91,optimize=True,subsampling=0)
   with Image.open(ref) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   assert ref.stat().st_size<2_000_000
   new.append({"role":cfg["role"],"source_url":u,"visual_subject":cfg["visually_reviewed_subject"],
    "rgb":rgb,"dhash":ph,"native":native,"source_image_format":fmt,"original_source":str(orig),
    "original_sha256":digest,"QA_reference_JPG":str(ref),
    "QA_reference_sha256":sha256(ref.read_bytes()).hexdigest(),
    "difference_from_prior_min_dhash":close,
    "commercial_photo_rights_verified":False,"actual_25AD_stock_edition_verified":False,
    "retail_approved":False})
  except Exception as e:errors.append(cfg["role"]+": "+str(e)[:180])
output_zip=None;review=None
if new:
 review=OUT/"GOODAL-two-new-product-scenes-CONTACT-INTERNAL.jpg"
 preview_image(new).save(review,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(review) as ck:assert ck.size==(1080,1080)
if len(new)==2:
 output_zip=OUT/"GOODAL_SerumMist_100mL_5SOURCE_INTERNAL_ONLY.zip"
 originals=oldbytes+[Path(x["QA_reference_JPG"]).read_bytes() for x in new]
 assert len(originals)==5 and len({sha256(b).hexdigest() for b in originals})==5
 with ZipFile(output_zip,"w",compression=ZIP_STORED) as z:
  for i,b in enumerate(originals,1):z.writestr(f"{i:02d}-100ml-real-product-source-NOT-RETAIL.jpg",b)
 with ZipFile(output_zip) as z:
  assert z.testzip() is None and len(z.namelist())==5
  for i,b in enumerate(originals,1):assert z.read(f"{i:02d}-100ml-real-product-source-NOT-RETAIL.jpg")==b
state=st["families"][fam]
count=3+len(new)
state.update({"last_delta_version":"v2937",
 "release_status":"FIVE_REAL_SOURCE_SCENES_INTERNAL_QA_ONLY_RETAIL_RIGHTS_STOCK_HOLD" if count==5 else "UNLICENSED_SOURCE_SCAN_PARTIAL_REAL_PHOTOS_RIGHTS_HOLD",
 "v2937_new_source_photo_count":len(new),
 "v2937_total_product_scene_candidates":count,
 "v2937_internal_five_source_zip":str(output_zip) if output_zip else None,
 "v2937_remaining_photo_source_slots":max(0,5-count),
 "latest_photo_QA_checkpoint":f"v2937 checked exact Oceanbuy Goodal serum mist 100mL listing; new nonduplicate photo references={len(new)}, total source candidate scenes={count}/5; stock 25AD, rights and true MK logo not verified. Prior JPGs unchanged.",
 "sale_approved":False})
report={"version":"v2937","baseline":"v2936","generated_at_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family":fam,"product":state["product"],"source_listing":sku_page,"listing_title":listing_title,
 "exact_100ml_product_title_verified":sku_page_verified,
 "new_distinct_photo_candidates":len(new),"total_candidate_product_scenes":count,
 "missing_photo_sources_to_five":max(0,5-count),"actual_original_existing_photo_sources_reused":3,
 "new_photo_source_archive_paths":[x["original_source"] for x in new],
 "new_1080_QA_refs":[x["QA_reference_JPG"] for x in new],
 "new_internal_contact":str(review) if review else None,
 "new_five_source_QA_zip":str(output_zip) if output_zip else None,
 "new_five_source_zip_sha256":sha256(output_zip.read_bytes()).hexdigest() if output_zip else None,
 "new_retail_approvals":0,"new_public_urls":0,"retailer_photo_license_granted":False,
 "old_11_approved_families_unchanged":True,"old_55_public_URLs_unchanged":True,
 "old_QA_image_bytes_changed":0,"final_spreadsheet_shared":False,
 "new_source_records":[{k:v for k,v in r.items() if k not in ("rgb","dhash")} for r in new],
 "errors":errors}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
st["version"]="v2937";st["baseline"]="v2936";st["new_sales_approvals"]=0;st["new_public_URLs"]=0;st["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2937.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2937","new_scenes":len(new),"total":count,
 "new_internal_zip":bool(output_zip),"errors":errors,"retail_approved":0},ensure_ascii=False))
