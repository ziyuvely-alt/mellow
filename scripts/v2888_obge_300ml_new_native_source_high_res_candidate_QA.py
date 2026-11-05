#!/usr/bin/env python3
"""v2888: One bounded, non-destructive search of already identified
high-resolution original product IMAGE URLs for OBgE MAX WATERFUL SUN CREAM
300mL. Skip same native 600px picture; NO photos rerendered/segmented from
existing v2857 and NO sale rights claimed. Original stock sheet row
for pending-22 only says 'OBgE Max Waterful Sun Cream, SPF50+ PA++++'
WITHOUT volume, so the 300mL pictured unit is a package/stock verification
HOLD, not a proven exact-inventory sales image. User's existing published
55 URLs and completed 11 family images are untouched.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageFont,ImageDraw
from io import BytesIO
from hashlib import sha256
import json,copy
R=Path("qa-review")
OUT=R/"v2888-obge300-highnative-official-merchant-source-candidates-QA"
PRE=R/"v2857-obge300ml-official-beige-source-true-alpha-recovery-QA"
STATE=R/"v2887-clio-meshblur-three-stock-shade-and-five-source-QA"/"stock30-incremental-state-v2887.json"
assert not OUT.exists() and STATE.exists()
pre=json.loads((PRE/"manifest.json").read_text())
state=json.loads(STATE.read_text())
assert pre["version"]=="v2857" and state["version"]=="v2887"
assert len(state["families"])==30
sha=lambda p:sha256(p.read_bytes()).hexdigest()
old=PRE/pre["new_JPG"]
assert sha(old)==pre["JPG_sha256"]
with Image.open(old) as im:
 im.load();assert im.size==(1080,1080)
 old_photo=im.convert("RGB")
TARGETS=[
 {"name":"brand-official-Cafe24-big","category":"brand_official",
  "url":"https://m.obge.co.kr/web/product/big/202603/95c2bcbeb8bf7bfa5b3d3b055e3a87d9.png",
  "product_page":"https://m.obge.co.kr/product/detail.html?product_no=1251",
  "source_view":"official main bottle catalog image"},
 {"name":"SoonsuShopify-candid-angle","category":"third_party_retailer",
  "url":"https://soonsubeauty.com/cdn/shop/files/51159251039382615_585094099.jpg?v=1777131226",
  "product_page":"https://soonsubeauty.com/products/obge-max-waterful-sun-cream-300ml",
  "source_view":"diagonal pump bottle with shadow"},
 {"name":"MaPetiteCoree-shopify-angle","category":"third_party_retailer",
  "url":"https://mylittlekorea.com/cdn/shop/files/OBGE-Max-Waterfull-Sunscreen-300ml-Ma-Petite-Coree_1.png?v=1776485758",
  "product_page":"https://mylittlekorea.com/products/obge-max-waterfull-sunscreen-300ml",
  "source_view":"close-up bottle with dark gradient"}
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda s,b=False:ImageFont.truetype(BOLD if b else FONT,s)
headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,image/*,*/*"}
OUT.mkdir(parents=True)
checks=[];cards=[]
for spec in TARGETS:
 rec={**spec,"status":"HOLD_UNCHECKED","photo_rights_verified":False,
      "actual_user_stock_300mL_label_checked":False,
      "retail_approved":False}
 try:
  with urlopen(Request(spec["url"],headers=headers),timeout=16) as response:
   blob=response.read(12_000_001)
  assert 5000<len(blob)<=12_000_000
  with Image.open(BytesIO(blob)) as img:
   img.load();fmt=img.format;native=img.size
   assert fmt in ("JPEG","PNG","WEBP"),fmt
   pixel=img.convert("RGB")
  rec.update(original_pixels=list(native),original_format=fmt,
             raw_SHA256=sha256(blob).hexdigest())
  # Require at least 900 native px on both axes; when one axis is smaller
  # do not misrepresent an interpolation as superior to original 600 px.
  if min(native)<900:
   rec.update(status="HOLD_NATIVE_BELOW_900_NO_SAVE_OR_RECOMPOSITION")
  else:
   extension={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[fmt]
   source=OUT/(spec["name"]+"-native-original."+extension)
   source.write_bytes(blob)
   qa=Image.new("RGB",(1080,1080),"#F8F7F7")
   d=ImageDraw.Draw(qa)
   d.rounded_rectangle((36,36,1044,1044),radius=25,outline="#D9D2D9",width=2)
   d.text((67,64),"OBgE MAX WATERFUL SUN CREAM",font=ft(30,True),fill="#423A44")
   d.text((66,115),f"NATIVE {native[0]} x {native[1]}  |  SOURCE ONLY",font=ft(22),fill="#695E68")
   fit=ImageOps.contain(pixel,(939,808),Image.Resampling.LANCZOS)
   qa.paste(fit,((1080-fit.width)//2,159+(808-fit.height)//2))
   d.line((69,967,1011,967),fill="#DDD5E0",width=2)
   d.text((71,977),"QA PHOTO  |  STOCK 300mL MATCH AND PHOTO LICENSE NOT CHECKED",font=ft(15,True),fill="#6C5E6E")
   jpg=OUT/(spec["name"]+"-1080-source-QA.jpg")
   qa.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
   with Image.open(jpg) as verify:
    verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
   assert jpg.stat().st_size<2_000_000
   assert sha(source)==sha256(blob).hexdigest()
   rec.update(status="HIGH_NATIVE_SOURCE_SAVED_PENDING_PRODUCT_VISUAL_AND_RIGHTS",
    original=str(source),sha256=sha(source),
    QA_JPG=str(jpg),QA_JPG_SHA256=sha(jpg),QA_JPG_bytes=jpg.stat().st_size,
    original_RGB_not_recolored=True)
   cards.append((spec["name"],qa))
 except Exception as e:
  rec.update(status="HOLD_SOURCE_UNAVAILABLE_SKIP_NO_RETRY",
    error=type(e).__name__+": "+str(e)[:220])
 checks.append(rec)
board=Image.new("RGB",(1610,1180),"#F1EEF1")
d=ImageDraw.Draw(board)
d.text((20,13),"v2888 OBgE WATERFUL 300mL | TRUE NATIVE RESOLUTION COMPARISON | NOT SALES",
 font=ft(21,True),fill="#413744")
tiles=[("v2857 600px upscaled OLD QA",old_photo)]+cards
for i,(name,pic) in enumerate(tiles[:4]):
 fit=ImageOps.contain(pic,(755,505),Image.Resampling.LANCZOS)
 x=16+(i%2)*800;y=60+(i//2)*548
 board.paste(fit,(x+(755-fit.width)//2,y+(505-fit.height)//2))
 d.text((x+7,y+510),name[:46],font=ft(16,True),fill="#5B4F60")
cp=OUT/"v2888-native-photo-source-resolution-visual-compare-QA.jpg"
board.save(cp,"JPEG",quality=88,optimize=True)
# The Crosswalk originally recorded a sunscreen title + SPF option but did
# not include 300mL. The official seller confirms *product listing* 300mL,
# NOT what the user physically owns.
families=copy.deepcopy(state["families"])
family=families["pending-22"]
family.update(last_delta_version="v2888",
 latest_photo_QA_checkpoint="v2888 bounded exact-product external native-resolution scan; 300mL product page exists but raw owner inventory has no volume. Source rights/actual stock match HOLD.",
 native_highresolution_source_candidates=sum(x["status"].startswith("HIGH_NATIVE") for x in checks),
 source_high_native_paths=[x.get("original") for x in checks if x["status"].startswith("HIGH_NATIVE")],
 owner_inventory_raw_capacity_unspecified=True,
 source_product_page_states_300mL=True,
 owner_stock_volume_label_300mL_unverified=True,
 release_status="HOLD_STOCK_VOLUME_RIGHTS_NATIVE_PRODUCT_VISUAL",sale_approved=False)
assert len(families)==30 and all(x.get("sale_approved")==False for x in families.values())
latest={**state,"version":"v2888","baseline":"v2887","families":families,
 "last_operation":"bounded native image source scan for OBgE Max Waterful 300mL with no prior source regeneration",
 "new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False}
st=OUT/"stock30-incremental-state-v2888.json"
st.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+"\n")
report={"version":"v2888","baseline":"v2887","family":"pending-22",
 "product_page_brand_official":"https://m.obge.co.kr/product/detail.html?product_no=1251",
 "product_official_volume":"300mL",
 "owned_inventory_original_capacity":"NOT_RECORDED",
 "source_only_older_v2857_native":[600,600],
 "new_highnative_original_photo_count":len(cards),
 "candidates_attempted_once":len(TARGETS),"candidate_source_results":checks,
 "new_source_comparison":str(cp),"comparison_SHA256":sha(cp),
 "old_v2857_original_JPG_modified":False,"old_v2857_alpha_modified":False,
 "new_generated_sale_artwork":0,
 "new_sales_approvals":0,"new_public_URLs":0,
 "photo_license_granted":False,"exact_owned_stock_300mL_confirmed":False,
 "old_11_published_groups_preserved":True,
 "old_55_URLs_untouched":True,"final_spreadsheet_shared":False,
 "family_30_checkpoint":str(st),
 "next":"Review high-native candidate image packaging visually. Use only original source reference until owned stock 300mL is physically verified and image rights granted. If none native>=900, do not run another blind URL variation; skip to other families."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2888","source_attempted":3,"new_high_native":len(cards),
 "native_resolutions":[x.get("original_pixels") for x in checks],"sale_approved":0}))
