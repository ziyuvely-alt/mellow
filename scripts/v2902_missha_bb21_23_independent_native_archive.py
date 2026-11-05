#!/usr/bin/env python3
"""Shopee v2902. One-shot archive of DIFFERENT merchant native 21/23 old gold-pump photos.
Do not repeat previous legacy mask-cleanup jobs or overwrite any old JPG.
Source-linked 1080-square white hero JPGs are INTERNAL QA, NOT licensed listings.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from hashlib import sha256
from PIL import Image, ImageOps, ImageStat
import json, copy

ROOT=Path("qa-review")
PRE=ROOT/"v2901-two-volume-source-conflict-claims-QA"/"stock30-incremental-state-v2901.json"
OUT=ROOT/"v2902-missha-BB-21-23-two-independent-native-merchants-QA"
assert PRE.exists() and not OUT.exists()
st=json.loads(PRE.read_text())
assert st["version"]=="v2901" and len(st["families"])==30
assert st["families"]["pending-03"]["last_delta_version"]=="v2900"
PRODUCTS=[
 {"shade":"21","label":"Light Beige","stock_source_index":8,"merchant":"Oceanbuy Canada",
  "page":"https://oceanbuy.ca/products/missha-m-perfect-cover-bb-cream-21-light-beige-50ml",
  "url":"https://oceanbuy.ca/cdn/shop/files/missha-missha-m-perfect-cover-bb-cream-50ml-no21-light-beige-oceanbuy-beauty-878751.jpg?v=1747722308&width=1600"},
 {"shade":"23","label":"Natural Beige","stock_source_index":9,"merchant":"M Beauty Plus",
  "page":"https://mbeautyplus.com/products/missha-p-cover-bb-cream-23-50ml",
  "url":"https://mbeautyplus.com/cdn/shop/files/23_568a6a08-e3fd-4576-9d9f-6ee43faebfe3.jpg?v=1783568163&width=1600"}
]
OUT.mkdir(parents=True)
r=[]
for item in PRODUCTS:
 row={**item,"one_attempt_only":True,"status":"HOLD_FAILED_NEW_MERCHANT_PHOTO",
      "original_src":None,"original_sha256":None,"qa_JPG_1080":None,
      "qa_JPG_sha256":None,"native_dimensions":None,"reason":None,
      "exact_owned_stock_generation_confirmed":False,
      "merchant_photo_commercial_reuse_rights_confirmed":False,
      "authentic_original_MK_logo_verified":False,
      "printed_shade_no_still_requires_human_visual_confirmation":True,
      "sale_approved":False}
 try:
  req=Request(item["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/png,image/jpeg,*/*"})
  with urlopen(req, timeout=18) as resp:
   payload=resp.read(8_000_001)
  assert 1000<len(payload)<=8_000_000,"source empty or exceeds 8MB"
  with Image.open(BytesIO(payload)) as check: check.verify()
  with Image.open(BytesIO(payload)) as original:
   original.load()
   fmt=original.format
   native=list(original.size)
   row["native_dimensions"]=native
   assert fmt in ("JPEG","PNG","WEBP"),"not a photo"
   assert min(native)>=850,"native product photo lower than 850, do not interpolate"
   assert max(native)/min(native)<1.5,"collage/odd aspect"
   if original.mode in ("RGBA","LA") or "transparency" in original.info:
    img=original.convert("RGBA")
    rgb=Image.new("RGB",original.size,"white")
    rgb.paste(img,mask=img.getchannel("A"))
   else:
    rgb=original.convert("RGB")
   outfile=OUT/f"MISSHA-legacy-goldpump-{item['shade']}-merchant-source-original.{ {'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt] }"
   outfile.write_bytes(payload)
   row["original_src"]=str(outfile)
   row["original_sha256"]=sha256(payload).hexdigest()
   square=Image.new("RGB",(1080,1080),"white")
   content=ImageOps.contain(rgb,(1024,1024),Image.Resampling.LANCZOS)
   square.paste(content,((1080-content.width)//2,(1080-content.height)//2))
   output=OUT/f"MISSHA-legacy-No{item['shade']}-goldpump-1080-INTERNAL-QA.jpg"
   square.save(output,"JPEG",quality=92,optimize=True,subsampling=0)
   assert output.stat().st_size<2_000_000
   row["qa_JPG_1080"]=str(output)
   row["qa_JPG_sha256"]=sha256(output.read_bytes()).hexdigest()
   row["qa_JPG_bytes"]=output.stat().st_size
   row["status"]="NEW_ALTERNATIVE_1080_HERO_SAVED_INTERNAL_QA_HOLD"
 except Exception as e:
  row["reason"]=type(e).__name__+": "+str(e)[:250]
  # Each failed item is isolated; the other photo is still checked.
 r.append(row)
assert len(r)==2
saved=sum(x["status"].startswith("NEW") for x in r)
manifest={
 "version":"v2902","baseline":"v2901","family":"pending-03",
 "product":"MISSHA M Perfect Cover BB Cream 50ml legacy red dotted/gold pump",
 "real_new_merchant_originals_saved":saved,"new_1080_internal_JPGs_saved":saved,
 "target_two_stock_rows":[8,9],
 "results":r,"old_v2871_No21_cutout_and_old_v2780_No23_hero_preserved":True,
 "No25_v2897_clean_hero_preserved":True,"old_11_sale_approved_groups_preserved":True,
 "old_55_public_urls_preserved":True,"commercial_photo_license_verified":False,
 "actual_physical_stock_21_23_pack_generation_verified":False,
 "new_approved_sale_images":0,"new_public_urls":0,
 "prior_JPGs_reprocessed":0,"final_XLSX_shared":False,
 "next":"Direct visual review of printed No.21 and No.23 plus gold pump, then decide if each NEW candidate replaces only previous QA link. Do not automatically approve."
}
new=copy.deepcopy(st)
new["version"]="v2902";new["baseline"]="v2901"
new["families"]["pending-03"]["last_delta_version"]="v2902"
new["families"]["pending-03"]["release_status"]="NEW_21_23_MERCHANT_OPTIONS_INTERNAL_QA_ONLY_HOLD_RIGHTS_OWNED_STOCK"
new["families"]["pending-03"]["latest_photo_QA_checkpoint"]="v2902 new independent 21/23 exact merchant candidates (one-shot each); old No25 clean source, existing scenes and public 55 URLs untouched. Physical shade/rights/MK HOLD."
new["families"]["pending-03"]["v2902_new_candidate_count"]=saved
new["v2902_photo_originals_saved"]=saved
new["v2902_photo_JPGs_saved"]=saved
new["new_sale_approvals"]=0;new["new_public_URLs"]=0
new["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2902.json").write_text(json.dumps(new,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2902","saved":saved,"results":[{"shade":x["shade"],"status":x["status"],"native":x["native_dimensions"],"reason":x["reason"]} for x in r],"retail_approved":0},ensure_ascii=False))
