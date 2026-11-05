#!/usr/bin/env python3
"""v2918 merge two parallel v2917 QA deltas without overwrites; discover PixelPure manufacturer extra/big photos for pending-29/30.
All discovered images remain NON-COMMERCIAL visual references. Never overwrite approved 11 families, 55 public URLs or prior QA files.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from urllib.parse import urlparse,urljoin
from collections import OrderedDict
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,time,copy,re

QA=Path("qa-review")
A=QA/"v2917-threefamily-official-photo-visual-claim-review-QA"
B=QA/"v2917-goodal-cream-six-source-claims-and-eye-source-edition-QA"
OLD=QA/"v2913-pixelpure-four-exact-product-official-gallery-native-source-QA"
PREV=QA/"v2914-pixelpure-twelve-photo-visual-relevance-claims-and-duplicate-QA"
OUT=QA/"v2918-reconcile-parallel-v2917-and-pixelpure-extra-big-firstparty-QA"
assert not OUT.exists()
SA=json.loads((A/"stock30-incremental-state-v2917.json").read_text(encoding="utf-8"))
SB=json.loads((B/"stock30-incremental-state-v2917.json").read_text(encoding="utf-8"))
MA=json.loads((A/"manifest.json").read_text(encoding="utf-8"))
MB=json.loads((B/"manifest.json").read_text(encoding="utf-8"))
M13=json.loads((OLD/"manifest.json").read_text(encoding="utf-8"))
M14=json.loads((PREV/"manifest.json").read_text(encoding="utf-8"))
assert SA["version"]==SB["version"]=="v2917"
assert len(SA["families"])==len(SB["families"])==30
assert MA["new_public_URLs"]==MB["new_public_image_URLs"]==0
assert MA["existing_55_public_urls_preserved"] and MB["old_55_published_URLs_modified"]==0
assert {x["family"] for x in MA["results"]}=={"pending-19","pending-24","pending-25"}
assert MB["family_count"]==2 and "pending-21" in SB["families"]
# Preserve branch A's v2917 exact goodal and BIOHEAL outcomes, bring only NEW eye QA from B.
state=copy.deepcopy(SA)
for k in ["pending-21"]:
 for field,value in SB["families"][k].items():
  if field.startswith("v2917_") or field in ("release_status","last_delta_version","latest_photo_QA_checkpoint","sale_approved"):
   state["families"][k][field]=value
state["families"]["pending-19"]["v2917_secondary_eye_cream_comparison"]=MB["comparison_JPG"]
state["families"]["pending-19"]["v2917_consensus_result"]="1 clean cream product reference, 5 unsupported marketing/model/clinical frames held in both v2917 audits"

def font(sz):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
 except:return ImageFont.load_default()
def dhash(im):
 g=ImageOps.fit(ImageOps.grayscale(im),(9,8)).load()
 return "".join("1" if g[x,y]>g[x+1,y] else "0" for y in range(8) for x in range(8))
def ham(a,b):return sum(x!=y for x,y in zip(a,b))
def read_verified(path,expected):
 p=Path(path)
 assert p.is_file() and sha256(p.read_bytes()).hexdigest()==expected
 with Image.open(p) as z:
  z.load()
  return ImageOps.exif_transpose(z).convert("RGB")
def sheet(family,items):
 im=Image.new("RGB",(1080,1080),"#f6f6f7");d=ImageDraw.Draw(im)
 d.text((28,20),family.upper()+" | EXTRA FIRST-PARTY FULL-RES QA",font=font(27),fill="#333333")
 d.text((28,59),"Only new manufacturer image candidates; edition / rights / claims NOT cleared",font=font(17),fill="#993333")
 for i,z in enumerate(items[:4]):
  row,col=divmod(i,2);x=24+col*523;y=110+row*439
  d.rounded_rectangle((x,y,x+508,y+417),radius=11,fill="white",outline="#cccccc",width=2)
  thumb=ImageOps.contain(z["image"],(492,336),Image.Resampling.LANCZOS)
  im.paste(thumb,(x+254-thumb.width//2,y+8+(336-thumb.height)//2))
  d.text((x+12,y+358),f"SOURCE {i+1}  {z['native'][0]}x{z['native'][1]}",font=font(17),fill="#333333")
  d.text((x+12,y+387),"NEW IMAGE REFERENCE ONLY",font=font(15),fill="#8c3030")
 d.text((28,1030),"No existing photos were rebuilt, replaced or published.",font=font(18),fill="#555555")
 return im

TARGETS=[
 {"family":"pending-29","product_no":26,
  "title_must":["radiance","soothing","cream"],
  "official_detail_page":"https://eng.pixelpure.com/product/detail.html?product_no=26",
  "known_exact_official_extra_big":[
    "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/f8d51ba2fbbf7cb558808d00a2f1317a.jpg",
    "https://ecimg.cafe24img.com/pg1807b57130625078/pixelpure/web/product/extra/big/20250430/5695cce612cdac532a1aedacb62b3581.jpg"
  ]},
 {"family":"pending-30","product_no":25,
  "title_must":["aura","radiance","serum"],
  "official_detail_page":"https://eng.pixelpure.com/product/detail.html?product_no=25",
  "known_exact_official_extra_big":[]}
]
S=requests.Session();S.headers.update({"User-Agent":"Mozilla/5.0 (noncommercial original product photo source QA; Pixelpure official)"})
old_by={r["family"]:r for r in M13["results"]}
other_by={r["family"]:r for r in M14["results"]}
def product_gallery_candidates(soup,page):
 urls=OrderedDict()
 selectors=[".imgArea .listImg img",".imgArea .prdImg img",".listImg img",".prdImg img",".keyImg img",".thumbnail img"]
 for sel in selectors:
  for im in soup.select(sel)[:18]:
   for attr in ["data-src","src","data-original"]:
    raw=im.get(attr)
    if not raw:continue
    u=urljoin(page,raw).split("?")[0]
    parsed=urlparse(u)
    if parsed.hostname=="ecimg.cafe24img.com" and "/pixelpure/web/product/" in parsed.path and any(z in parsed.path for z in ["/extra/big/","/extra/small/","/big/"]):
     urls[u]=sel
 # Never scrape related-product galleries or user image reviews
 return urls
OUT.mkdir(parents=True)
reports=[]
for cfg in TARGETS:
 fam=cfg["family"]
 prior=old_by[fam]
 paths=prior["new_originals"]
 previous_selected=other_by[fam]["combined_clean_source_candidates"]
 oldsource_sha={p["raw_SHA256"] for p in paths}
 old_ref_shas={p["sha256"] for p in previous_selected}
 oldviews=[]
 for p in paths:
  ref=p["ref"];sig=p["ref_SHA256"]
  try:oldviews.append(dhash(read_verified(ref,sig)))
  except Exception:pass
 for p in previous_selected:
  try:oldviews.append(dhash(read_verified(p["source_path"],p["sha256"])))
  except Exception:pass
 urls=OrderedDict((x,"MANUALLY_VERIFIED_OFFICIAL_PRODUCT_EXTRA_BIG") for x in cfg["known_exact_official_extra_big"])
 errors=[];page_title=None;page_verified=False
 try:
  rr=S.get(cfg["official_detail_page"],timeout=15);rr.raise_for_status()
  soup=BeautifulSoup(rr.text,"html.parser")
  page_title=soup.title.get_text(" ",strip=True) if soup.title else ""
  title_compact="".join(page_title.lower().split())
  page_verified=all(x in title_compact for x in cfg["title_must"])
  if not page_verified:
   errors.append("official English product title does not match all expected tokens; no additional gallery added")
  else:
   for url,which in product_gallery_candidates(soup,cfg["official_detail_page"]).items():
    urls.setdefault(url,"OFFICIAL_PRODUCT_PAGE_GALLERY_"+which)
 except Exception as e:errors.append("official detail fetch "+str(e)[:150])
 new=[];hashes=set();near=[]
 for u,source_type in list(urls.items())[:20]:
  if len(new)>=4:break
  try:
   parsed=urlparse(u)
   if parsed.scheme!="https" or parsed.hostname!="ecimg.cafe24img.com" or "/pixelpure/web/product/" not in parsed.path:continue
   rq=S.get(u,timeout=16);rq.raise_for_status()
   if urlparse(rq.url).hostname!="ecimg.cafe24img.com":raise ValueError("untrusted image redirect")
   data=rq.content
   if not 4000<len(data)<12_000_000:raise ValueError("bytes outside allowed native photo band")
   raw=Image.open(BytesIO(data));raw.load()
   if raw.format not in ("JPEG","PNG","WEBP"):raise ValueError("unsupported source format")
   rgb=ImageOps.exif_transpose(raw).convert("RGB");native=rgb.size
   if min(native)<900:raise ValueError(f"native below 900px: {native}")
   digest=sha256(data).hexdigest()
   if digest in hashes or digest in oldsource_sha or digest in old_ref_shas:continue
   h=dhash(rgb)
   md=min([ham(h,z) for z in oldviews+[x["dhash"] for x in new]],default=64)
   if md<6:
    near.append({"url":u,"dhash_near_duplicate_distance":md})
    continue
   index=len(new)+1;sub=OUT/fam;sub.mkdir(exist_ok=True)
   ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}[raw.format]
   p=sub/f"{index:02d}-pixelpure-manufacturer-native{ext}";p.write_bytes(data)
   canvas=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
   canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   target=sub/f"{index:02d}-pixelpure-1080-reference-NOT-RETAIL.jpg"
   canvas.save(target,"JPEG",quality=90,optimize=True,subsampling=0)
   with Image.open(target) as z:assert z.format=="JPEG" and z.size==(1080,1080)
   assert target.stat().st_size<2000000
   new.append({"image":rgb,"dhash":h,"native":native,"source_url":u,"source_class":source_type,
     "raw_original":str(p),"raw_original_sha256":digest,
     "reference_jpg":str(target),"reference_sha256":sha256(target.read_bytes()).hexdigest(),
     "existing_source_min_dhash_distance":md,
     "exact_KR_stock_edition_verified":False,"scene_visual_claim_qa":"PENDING",
     "commercial_photo_rights_verified":False,"retail_approved":False})
   hashes.add(digest)
  except Exception as e:errors.append("download skipped "+u.split("/")[-1][:50]+": "+str(e)[:160])
 contact=None
 if new:
  contact=OUT/(fam+"-new-official-extra-gallery-INTERNAL-CONTACT.jpg")
  sheet(fam,new).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
  with Image.open(contact) as z:assert z.format=="JPEG" and z.size==(1080,1080)
  assert contact.stat().st_size<2000000
 st=state["families"][fam]
 st.update({"last_delta_version":"v2918",
  "release_status":"FIRSTPARTY_NEW_EXTRA_BIG_CANDIDATES_ARCHIVED_STOCK_RIGHTS_HOLD" if new else "OFFICIAL_EXTRA_BIG_GALLERY_CHECKED_NO_DISTINCT_NEW_SOURCE",
  "v2918_extra_firstparty_photo_originals":len(new),
  "v2918_new_extra_gallery_contact":str(contact) if contact else None,
  "latest_photo_QA_checkpoint":f"v2918 official PixelPure English page #{cfg['product_no']}: {len(new)} new native photo source(s), {len(near)} near-duplicates skipped; physical owned stock and commercial use rights HOLD.",
  "sale_approved":False})
 reports.append({"family":fam,"product_no":cfg["product_no"],"official_product_page":cfg["official_detail_page"],
  "official_page_title":page_title,"exact_page_title_match":page_verified,
  "additional_urls_examined":len(urls),"new_fullnative_originals":len(new),"new_contact":str(contact) if contact else None,
  "new_images":[{k:(list(v) if k=="native" else v) for k,v in x.items() if k not in ("image","dhash")} for x in new],
  "prior_near_duplicate_candidates_skipped":near,"errors":errors[:12],
  "retail_approved":False})
summary={"version":"v2918","baseline":"v2917_PAIR_RECONCILED","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "prior_v2917_manifest_paths":[str(A/"manifest.json"),str(B/"manifest.json")],
 "merged_delta_families":["pending-19","pending-21","pending-24","pending-25"],
 "goodal_six_claim_qa_consensus":True,"old_cream_eye_comparison_preserved":MB["comparison_JPG"],
 "new_pixelpure_originals_archived":sum(r["new_fullnative_originals"] for r in reports),
 "new_1080_reference_images":sum(r["new_fullnative_originals"] for r in reports),
 "new_pixelpure_internal_contacts":sum(bool(r["new_contact"]) for r in reports),
 "existing_11_published_families_unchanged":True,"old_55_public_urls_unchanged":True,
 "old_QA_files_modified":0,"new_retail_approvals":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,"pixelpure_results":reports}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2918";state["baseline"]="v2917_PAIR_RECONCILED";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2918.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2918","reconciled_2_v2917_branches":True,
 "new_manufacturer_Pixelpure_originals":summary["new_pixelpure_originals_archived"],
 "pixelpure_by_family":{r["family"]:r["new_fullnative_originals"] for r in reports},
 "new_sale_approvals":0},ensure_ascii=False))
