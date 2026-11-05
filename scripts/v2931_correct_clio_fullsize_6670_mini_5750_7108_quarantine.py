#!/usr/bin/env python3
"""v2931: correct pending-05 CLIO original-source product mapping.
Prior v2793 '5750/7108' photo references are MINI 5g candidates, whereas
pending-05's currently named SKU is the regular Founwear Cushion SET.
Source exact manufacturer goodsView/0000006670, archive native files only,
quarantine mismatched mini sources for downstream use. NOT retail approval.
"""
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from urllib.parse import urlparse
import re,json,time,requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw,ImageFont

QA=Path("qa-review")
PRE=QA/"v2930-goodal-mist100-clubclio-official-gallery-native-photo-QA"
OLD=QA/"v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof"
V24=QA/"v2924-eight-unpacked-stock-family-3five-photo-20option-4clio-source-QA"
OUT=QA/"v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2930.json").read_text(encoding="utf-8"))
old=json.loads((OLD/"manifest.json").read_text(encoding="utf-8"))
v24=json.loads((V24/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2930" and len(state["families"])==30
assert old["version"]=="v2793" and v24["version"]=="v2924"
fam="pending-05"
item=next(z for z in v24["mixed_option_sources"] if z["family"]==fam)
prior=next(z for z in old["products"] if z["family"]==fam)
assert prior["candidates"]==[5750,7108] and prior["label"]=="CLIO Kill Cover Founwear Cushion Mini 5g"
assert len(prior["source_photo_candidates"])==4 and item["reference_count"]==5
assert "기획세트" in state["families"][fam]["product"]
# The official product page was linked from the manufacturer's CURRENT full-size product listing.
page="https://clubclio.co.kr/shop/goodsView/0000006670"
image_sources=[
 {"key":"M","url":"https://clubclio.co.kr/data/mall_data/images/product/00/00/00/66/70/m.gif"},
 {"key":"B","url":"https://clubclio.co.kr/data/mall_data/images/product/00/00/00/66/70/b.gif"}
]
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def d_hash(image):
 gray=ImageOps.grayscale(ImageOps.fit(image.convert("RGB"),(9,8))).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def picture(data):
 src=Image.open(BytesIO(data));src.load()
 if src.format not in ("GIF","JPEG","PNG","WEBP"):raise ValueError("unsupported official source format")
 if min(src.size)<400 or max(src.size)>9000:raise ValueError("native photo unsuitable")
 return ImageOps.exif_transpose(src.convert("RGBA")).convert("RGB"),src.format,list(src.size)
def card(new,mini):
 can=Image.new("RGB",(1080,1080),"#f5f5f7");draw=ImageDraw.Draw(can)
 draw.text((24,18),"CLIO | FULL-SIZE 6670 vs MINI 5750/7108",font=font(29),fill="#272727")
 draw.text((24,62),"SOURCE PRODUCT IDENTITY QA ONLY | NOT FOR UPLOAD",font=font(18),fill="#a33434")
 panels=[]
 for k in new:panels.append((k["image"],"CURRENT FULL-SIZE SET 6670 "+k["key"]))
 for k in mini[:2]:panels.append((k["image"],"PRIOR MINI 5g "+str(k["product_id"])))
 for i,(im,label) in enumerate(panels[:4]):
  col=i%2;row=i//2;x=23+col*523;y=108+row*447
  draw.rounded_rectangle((x,y,x+507,y+424),radius=12,fill="white",outline="#d2d2d2",width=2)
  thumb=ImageOps.contain(im,(490,340),Image.Resampling.LANCZOS)
  can.paste(thumb,(x+253-thumb.width//2,y+8+(340-thumb.height)//2))
  draw.text((x+12,y+359),label,font=font(15),fill="#963636" if i>=2 else "#245441")
  draw.text((x+12,y+393),"NOT RETAIL LICENSED",font=font(13),fill="#a33434")
 draw.text((26,1029),"5g MINI source photos must not be assigned to full-size main + refill set.",font=font(16),fill="#a33434")
 return can
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (CLIO product-gallery photo source integrity QA)"})
OUT.mkdir(parents=True)
errors=[];page_verified=False;page_title=None;page_text_excerpt=""
try:
 r=session.get(page,timeout=17);r.raise_for_status()
 soup=BeautifulSoup(r.text,"html.parser")
 page_text=soup.get_text(" ",strip=True)
 page_title=soup.title.get_text(" ",strip=True) if soup.title else None
 norm=re.sub(r"\s+","",page_text).lower()
 page_verified=("파운웨어쿠션기획세트" in norm and "본품+리필" in norm) or ("킬커버파운웨어쿠션" in norm and "기획세트" in norm and "본품+리필" in norm)
 if not page_verified:errors.append("The official page HTML did not sufficiently identify current full-size + refill set; do not adopt new sources")
 page_text_excerpt=page_text[:300]
except Exception as e:errors.append("current official product page: "+str(e)[:140])
new=[]
if page_verified:
 for source in image_sources:
  try:
   u=source["url"]
   assert urlparse(u).hostname=="clubclio.co.kr"
   r=session.get(u,timeout=16);r.raise_for_status()
   if urlparse(r.url).hostname!="clubclio.co.kr":raise ValueError("untrusted image redirect")
   b=r.content
   if not 4000<len(b)<7_000_000:raise ValueError("image too small/large")
   img,fmt,native=picture(b)
   idx=len(new)+1;sub=OUT/fam;sub.mkdir(exist_ok=True)
   raw=sub/f"{idx:02d}-6670-{source['key']}-official-unaltered.{fmt.lower()}"
   raw.write_bytes(b)
   out=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(img,(1080,1080),Image.Resampling.LANCZOS)
   out.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   preview=sub/f"{idx:02d}-6670-{source['key']}-1080-REFERENCE-NOT-RETAIL.jpg"
   out.save(preview,"JPEG",quality=91,optimize=True,subsampling=0)
   with Image.open(preview) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   assert preview.stat().st_size<2_000_000
   new.append({"key":source["key"],"image":img,"dhash":d_hash(img),
    "source_url":u,"native_format":fmt,"native_pixels":native,"native_high_res_900px":min(native)>=900,
    "source_path":str(raw),"source_sha256":sha256(b).hexdigest(),
    "preview_path":str(preview),"preview_sha256":sha256(preview.read_bytes()).hexdigest(),
    "retail_license_approved":False,"owned_stock_pack_verified":False,"retail_approved":False})
  except Exception as e:errors.append("official photo "+source["key"]+": "+str(e)[:190])
# Existing mini source refs are read-only and stay available for the actual mini SKU, not this set.
mini=[];quarantine=[]
for src in prior["source_photo_candidates"]:
 ref=OLD/src["file"]
 assert ref.is_file() and sha256(ref.read_bytes()).hexdigest()==src["jpg_hash"]
 if src["file"].startswith(("pending-05/01","pending-05/03")):
  mini.append({"product_id":src["product_id"],"image":picture(ref.read_bytes())[0]})
 quarantine.append({"source_file":str(ref),"source_sha256":src["jpg_hash"],"original_product_id":src["product_id"],
  "native_source_pixels":src["native_dimensions"],"reason":"MINI_5G_PRODUCT_REFERENCE_NOT_PROOF_OF_6670_FULLSIZE_MAIN_REFILL_SET",
  "approved_for_pending_05_fullsize":False,"immutable_original_preserved":True})
assert len(quarantine)==4 and all(x["original_product_id"] in (5750,7108) for x in quarantine)
distance=dist(new[0]["dhash"],new[1]["dhash"]) if len(new)==2 else None
contact=None
if new:
 contact=OUT/"pending-05-6670-fullsize-vs-old-mini-visual-INTERNAL-QA.jpg"
 card(new,mini).save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
 with Image.open(contact) as ck:assert ck.size==(1080,1080) and ck.format=="JPEG"
 assert contact.stat().st_size<2_000_000
state["families"][fam].update({"last_delta_version":"v2931",
 "release_status":"MINI_5G_4_WRONG_SOURCE_IDS_QUARANTINED_FROM_FULLSIZE_6670_SOURCE_MAPPING",
 "v2931_quarantined_mini_source_count":4,
 "v2931_correct_official_product_id":6670,
 "v2931_new_correct_product_reference_count":len(new),
 "v2931_current_correct_product_internal_contact":str(contact) if contact else None,
 "v2931_owned_stock_and_rights_status":"HOLD",
 "latest_photo_QA_checkpoint":f"v2931 quarantined 4 mini 5g IDs 5750/7108 from pending-05 full-size cushion set; verified current official 6670 page={page_verified}, archived {len(new)} official 6670 photo sources (native resolution low-res hold). Original files untouched.",
 "sale_approved":False})
report={"version":"v2931","baseline":"v2930","created_UTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family":fam,"pending_item":state["families"][fam]["product"],
 "old_incorrect_source_product_ids":[5750,7108],"quarantined_prior_mini_photo_references":len(quarantine),
 "correct_current_official_product_id":6670,"correct_official_product_page":page,
 "correct_official_page_confirmed":page_verified,"official_page_title":page_title,
 "new_correct_product_source_originals_archived":len(new),
 "new_photo_native_resolutions":[x["native_pixels"] for x in new],
 "photo_source_similarity_hamming":distance,
 "new_manufacturer_scenes_independent_identity_confirmed":False,
 "commercial_photo_rights_cleared":False,"user_stock_main_refill_edition_confirmed":False,
 "no_original_file_changed":True,"prior_11_approved_families_unchanged":True,"prior_55_verified_public_URLs_unchanged":True,
 "new_sales_approved":0,"new_public_URLs":0,"final_spreadsheet_shared":False,
 "revised_future_source_filter":{"pending-05":{"allow_unverified_ID_6670_sources_for_internal_QA":True,
    "disallow_IDs":[5750,7108],"never_use_mini_5g_image_for_fullsize_set":True,
    "existing_pending05_master_hero_still_edition_unverified":True,
    "photo_license_stock_variant_release":"HOLD"}},
 "new_fullsize_sources":[{k:v for k,v in x.items() if k not in ("image","dhash")} for x in new],
 "quarantined_mini_sources":quarantine,
 "contact":str(contact) if contact else None,"errors":errors}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2931";state["baseline"]="v2930";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2931.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2931","verified_current_official_product_page":page_verified,
 "wrong_mini_sources_quarantined":4,"new_correct_fullsize_originals":len(new),
 "new_images_native_px":[x["native_pixels"] for x in new],"errors":errors,"new_sales_approvals":0},ensure_ascii=False))
