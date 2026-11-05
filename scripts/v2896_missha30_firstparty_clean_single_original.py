#!/usr/bin/env python3
"""v2896: Source clean official first-party 30ml MISSHA serum product photo.
Do not re-run the failed v2855/v2865 edge-mask cleanup; never edit prior JPG.
One new native photo only, one 1080 square review JPG, no retail approval.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from io import BytesIO
from hashlib import sha256
from PIL import Image, ImageOps
import json, copy

R=Path("qa-review")
PRE=R/"v2895-peripera20-lip-photo-ROI-similarity-check"/"stock30-incremental-state-v2895.json"
OUT=R/"v2896-missha30-new-clean-firstparty-native-photo-QA"
assert PRE.exists() and not OUT.exists()
state=json.loads(PRE.read_text())
assert state["version"]=="v2895" and len(state["families"])==30
assert state["families"]["pending-13"]["last_delta_version"]=="v2865"
URL="https://misshaus.com/cdn/shop/files/CopyofMS104056.png?v=1782920372&width=1600"
PAGE="https://misshaus.com/products/missha-official-pdrn-nad-firming-repair-serum"
OUT.mkdir(parents=True)
result="HOLD_OFFICIAL_SOURCE_DOWNLOAD_OR_TECHNICAL_CHECK"
exception=None
file=None; jpg=None; native=None; fetched_format=None; source_sha=None
try:
 request=Request(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/webp,image/jpeg,*/*"})
 with urlopen(request,timeout=18) as response:
  content=response.read(8_000_001)
 assert 1000<len(content)<=8_000_000,"native file empty or >8MB"
 with Image.open(BytesIO(content)) as verify:
  verify.verify()
 with Image.open(BytesIO(content)) as orig:
  orig.load()
  fmt=orig.format
  assert fmt in ("PNG","JPEG","WEBP"),"not a photographic file"
  native=list(orig.size)
  assert min(native)>=900,"source native resolution below 900px; no enlargement"
  assert max(native)/min(native)<2.5,"poster/banner, not product isolation"
  if orig.mode in ("RGBA","LA") or "transparency" in orig.info:
   rgba=orig.convert("RGBA")
   rgb=Image.new("RGB",orig.size,"white")
   rgb.paste(rgba,mask=rgba.getchannel("A"))
  else:
   rgb=orig.convert("RGB")
 source_sha=sha256(content).hexdigest()
 ext={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[fmt]
 file=OUT/("MISSHA-PDRN30ml-US-firstparty-original."+ext)
 file.write_bytes(content)
 out=Image.new("RGB",(1080,1080),"white")
 thumb=ImageOps.contain(rgb,(1040,1040),Image.Resampling.LANCZOS)
 out.paste(thumb,((1080-thumb.width)//2,(1080-thumb.height)//2))
 jpg=OUT/"MISSHA-PDRN-NAD-Serum30ml-firstparty-clean-1080-INTERNAL-QA.jpg"
 out.save(jpg,format="JPEG",quality=92,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2_000_000
 fetched_format=fmt
 result="SOURCE_AND_QA_JPG_SAVED_RETAIL_HOLD_VISUAL_STOCK_RIGHTS"
except Exception as e:
 exception=type(e).__name__+": "+str(e)[:350]
 # All previous approved and interim artifacts remain in place.
 if jpg and jpg.exists():jpg.unlink()
 if file and file.exists() and result!="SOURCE_AND_QA_JPG_SAVED_RETAIL_HOLD_VISUAL_STOCK_RIGHTS":file.unlink()
manifest={
 "version":"v2896","baseline":"v2895","family":"pending-13",
 "product":"MISSHA PDRN NAD+ Firming Repair Serum, 30mL",
 "prior_problem":"v2865 red decorative artifact on the right of white dropper cap; do not try same alpha mask again",
 "source":"MISSHA US official brand retail listing",
 "source_product_page":PAGE,"native_photo_url":URL,
 "result":result,"reason_if_hold":exception,"first_party_asset_for_internal_review_only":True,
 "native_px":native,"downloaded_format":fetched_format,
 "source_original":str(file) if file and file.exists() else None,
 "source_sha256":source_sha,
 "QA_jpg_1080":str(jpg) if jpg and jpg.exists() else None,
 "QA_jpg_sha256":sha256(jpg.read_bytes()).hexdigest() if jpg and jpg.exists() else None,
 "QA_jpg_bytes":jpg.stat().st_size if jpg and jpg.exists() else None,
 "photo_color_chips_synthesized":0,"old_5_frame_QA_images_modified":False,
 "product_label_and_edition_requires_human_review":True,
 "source_republication_rights_confirmed":False,
 "owned_product_exact_editions_confirmed":False,
 "authentic_original_MK_logo_confirmed":False,
 "new_approved_retail_families":0,"new_public_urls":0,
 "previous_11_approved_families_protected":True,
 "previous_55_published_urls_protected":True,
 "final_spreadsheet_shared":False
}
s=copy.deepcopy(state)
s["version"]="v2896";s["baseline"]="v2895"
s["families"]["pending-13"]["last_delta_version"]="v2896"
s["families"]["pending-13"]["release_status"]="NEW_FIRSTPARTY_CLEAN_PHOTO_CANDIDATE_QA_ONLY_RIGHTS_STOCK_HOLD" if jpg and jpg.exists() else "HOLD_SOURCE_ACCESS_NEW_METHOD_NEEDED"
s["families"]["pending-13"]["latest_photo_QA_checkpoint"]=(
  "v2896 fresh official MISSHA US source clean 30ml hero QA saved, no old red-fringe mask redo. Commercial usage rights/owned stock/MK logo HOLD"
  if jpg and jpg.exists() else
  "v2896 official firstparty source one-shot attempt failed; no old mask repeat; previous five photos preserved")
s["families"]["pending-13"]["new_firstparty_clean_originals"]=1 if file and file.exists() else 0
s["families"]["pending-13"]["new_clean_candidate_jpgs"]=1 if jpg and jpg.exists() else 0
s["v2896_existing_5frame_set_regenerated"]=0
s["new_sale_approvals"]=0;s["new_public_URLs"]=0
s["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2896.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2896","result":result,"native":native,"new_jpg":bool(jpg and jpg.exists()),
                  "old_images_recreated":0,"new_commercial_approvals":0,"error":exception},ensure_ascii=False))
