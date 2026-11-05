#!/usr/bin/env python3
"""v2896 | MISSHA 30mL official CLEAN source alternative to v2865 cap fringe.
One bounded first-party source family, at most 2 URLs. Do not try the old
segmentation edge trim or alter old approved/saved QA images.
New photo is internal QA only without commercial-use rights or owned stock.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
from hashlib import sha256
from io import BytesIO
import json,copy

R=Path("qa-review")
STATE=R/"v2895-peripera20-lip-photo-ROI-similarity-check"/"stock30-incremental-state-v2895.json"
OLD=R/"v2865-missha30-dropper-right-red-fringe-isolated-local-QA"/"manifest.json"
OUT=R/"v2896-missha30-brand-official-clean-single-bottle-source"
assert STATE.is_file() and OLD.is_file() and not OUT.exists()
state=json.loads(STATE.read_text())
old=json.loads(OLD.read_text())
assert state["version"]=="v2895" and len(state["families"])==30
assert old["version"]=="v2865" and old["family"]=="pending-13"
URLS=[
 "https://misshaus.com/cdn/shop/files/CopyofMS104056.png?v=1782920372&width=1600",
 "https://misshaus.com/cdn/shop/files/CopyofMS104056_grande.png?v=1782920372&width=1600"
]
page="https://misshaus.com/products/missha-official-pdrn-nad-firming-repair-serum"
attempts=[]; chosen=None; payload=None; rgb=None; actual=None; fmt=None; orig_alpha=False
for url in URLS:
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/webp,image/jpeg,*/*"})
  with urlopen(req,timeout=12) as resp:
   raw=resp.read(8_000_001)
  assert 0<len(raw)<=8_000_000,"empty or >8MB"
  with Image.open(BytesIO(raw)) as im:
   im.load();assert im.format in ("PNG","WEBP","JPEG"),"invalid photo data"
   downloaded_format=im.format
   im=ImageOps.exif_transpose(im)
   w,h=im.size
   assert min(w,h)>=800 and max(w,h)/min(w,h)<=1.5,"low native size or wrong aspect"
   actual=[w,h]
   fmt=downloaded_format
   if im.mode in ("RGBA","LA") or ("transparency" in im.info):
    rgba=im.convert("RGBA"); lo,hi=rgba.getchannel("A").getextrema()
    orig_alpha=lo<255
    back=Image.new("RGB",rgba.size,"white")
    back.paste(rgba,(0,0),rgba.getchannel("A"))
    rgb=back
   else:rgb=im.convert("RGB")
  payload=raw;chosen=url
  attempts.append({"url":url,"result":"SAVED_VALID_NATIVE_SOURCE","native_px":actual})
  break
 except Exception as ex:
  attempts.append({"url":url,"result":"HOLD_SKIP_OTHER_SOURCE","reason":type(ex).__name__+": "+str(ex)[:220]})
OUT.mkdir(parents=True)
saved_original=None;saved_photo=None;photo_bytes=None
if payload is not None:
 saved_original=OUT/("MISSHA-US-brand-30ml-original."+fmt.lower().replace("jpeg","jpg"))
 saved_original.write_bytes(payload)
 image=Image.new("RGB",(1080,1080),"white")
 centered=ImageOps.contain(rgb,(1030,1030),Image.Resampling.LANCZOS)
 image.paste(centered,((1080-centered.width)//2,(1080-centered.height)//2))
 saved_photo=OUT/"MISSHA-30ml-brand-clean-white-source-1080-INTERNAL-QA.jpg"
 image.save(saved_photo,"JPEG",quality=93,subsampling=0,optimize=True)
 photo_bytes=saved_photo.stat().st_size
 assert photo_bytes<2_000_000,"staged jpeg over 2MB"
 verdict="NEW_OFFICIAL_SINGLE_BOTTLE_SOURCE_SAVED_NO_RETRO_ALPHA"
else:
 verdict="HOLD_OFFICIAL_SOURCE_FETCH_OR_NATIVE_NOT_ACCEPTABLE"
report={
 "version":"v2896","baseline":"v2895","family":"pending-13",
 "product":"MISSHA Camellia PDRN NAD+ Firming Repair Serum 30mL",
 "source_product_page":page,"official_source_candidates_attempted":attempts,
 "primary_official_image_url_selected":chosen,
 "new_firstparty_clean_reference_status":verdict,
 "new_original_native_px":actual,"source_native_format":fmt,
 "brand_source_has_real_transparency_alpha":orig_alpha,
 "original_saved":str(saved_original) if saved_original else None,
 "original_sha256":sha256(saved_original.read_bytes()).hexdigest() if saved_original else None,
 "source_white_background_JPG_1080":str(saved_photo) if saved_photo else None,
 "source_1080_sha256":sha256(saved_photo.read_bytes()).hexdigest() if saved_photo else None,
 "source_1080_bytes":photo_bytes,
 "source_RGB_recolored_or_ai_regenerated":False,
 "source_true_alpha_cutout_automatically_claimed":False,
 "source_needs_actual_human_packaging_edition_confirmation":True,
 "source_needs_license_for_commercial_use":True,
 "prior_v2865_redfringe_alpha_JPG_modified":False,
 "new_sale_approvals":0,"new_public_urls":0,
 "old_11_approved_groups_unchanged":True,
 "old_55_public_urls_unchanged":True,
 "MK_original_authenticated":False,"final_spreadsheet_shared":False,
 "next":"If clean source can replace red fringe for INTERNAL reference, still require physical stock and license. Do not repeat cap masking on v2865."
}
newstate=copy.deepcopy(state)
newstate["version"]="v2896";newstate["baseline"]="v2895"
newstate["families"]["pending-13"]["last_delta_version"]="v2896"
newstate["families"]["pending-13"]["latest_photo_QA_checkpoint"]="v2896 MISSHA US official 30ml clean single source scan "+verdict+"; prior flawed red-cap mask untouched. Owned stock and commercial photo rights HOLD"
newstate["families"]["pending-13"]["release_status"]="QA_CLEAN_OFFICIAL_REFERENCE_ONLY_HOLD_OWNED_EDITION_RIGHTS_MK"
newstate["v2896_new_brand_source_originals"]=int(chosen is not None)
newstate["v2896_new_JPGs"]=int(saved_photo is not None)
newstate["v2896_existing_JPGs_changed"]=0
newstate["new_sale_approvals"]=0
newstate["new_public_URLs"]=0
newstate["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2896.json").write_text(json.dumps(newstate,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2896","status":verdict,"native_px":actual,"candidate_count":len(attempts),"new_1080":int(saved_photo is not None),"new_retail_approvals":0},ensure_ascii=False))
