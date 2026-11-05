#!/usr/bin/env python3
"""v2897 | One fresh exact shade No.25 legacy 50mL photographic source.
Prior v2872 foreground cleanup left grey background ghost. Do not rerun alpha;
save an independent legacy No.25 image and a white-background QA hero only.
Never publish automatically or replace any archived image.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageOps
import json,copy

R=Path("qa-review")
PRE=R/"v2896-missha30-brand-official-clean-single-bottle-source"/"stock30-incremental-state-v2896.json"
OLD=R/"v2872-missha-bb-no25-background-ghost-geometry-alpha-QA"/"MISSHA-No25-legacy-ghost-clean-1080-QA.jpg"
OUT=R/"v2897-missha-bb25-legacy-goldpump-new-independent-source-QA"
assert PRE.is_file() and OLD.is_file() and not OUT.exists()
st=json.loads(PRE.read_text())
assert st["version"]=="v2896" and len(st["families"])==30
assert st["families"]["pending-03"]["last_delta_version"]=="v2872"

URL="https://cdn.kindlife.in/images/detailed/116/12013188-2094647897654345_1024x1024.webp?t=1692435542"
PAGE="https://www.kindlife.in/m-perfect-cover-bb-cream-spf42-pa-no.25-warm-beige-50ml/"
OUT.mkdir(parents=True)
result="HOLD_NEEDS_CLEAN_ALTERNATIVE_SOURCE"
reason=None; native=None; fmt=None; src=None; art=None; total=None
try:
 request=Request(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/png,image/jpeg,*/*"})
 with urlopen(request,timeout=17) as resp:
  raw=resp.read(8_000_001)
 assert 1000<len(raw)<=8_000_000,"source zero or >8MB"
 with Image.open(BytesIO(raw)) as check:check.verify()
 with Image.open(BytesIO(raw)) as im:
  im.load()
  fmt=im.format
  native=list(im.size)
  assert fmt in ("JPEG","WEBP","PNG"),"nonphoto source"
  assert min(native)>=900,"low native pixel source, no upscaling"
  assert max(native)/min(native)<1.4,"wrong aspect; potential multi-photo collage"
  if im.mode in ("RGBA","LA") or "transparency" in im.info:
   rgba=im.convert("RGBA")
   rgb=Image.new("RGB",im.size,"white")
   rgb.paste(rgba,mask=rgba.getchannel("A"))
  else:rgb=im.convert("RGB")
  # Keep actual product pixels unchanged. This is white-rectangle fit only.
  square=Image.new("RGB",(1080,1080),"white")
  resized=ImageOps.contain(rgb,(1024,1024),Image.Resampling.LANCZOS)
  square.paste(resized,((1080-resized.width)//2,(1080-resized.height)//2))
 ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[fmt]
 src=OUT/("MISSHA-original-legacy-No25-merchant-raw."+ext)
 src.write_bytes(raw)
 art=OUT/"MISSHA-old-goldpump-No25-clean-source-1080-INTERNAL-QA.jpg"
 square.save(art,"JPEG",quality=92,optimize=True,subsampling=0)
 total=art.stat().st_size
 assert total<2_000_000,"2MB limit"
 result="NEW_SOURCE_AND_1080_QA_CANDIDATE_SAVED_PENDING_IDENTITY_RIGHTS"
except Exception as e:
 reason=type(e).__name__+": "+str(e)[:300]
 if art and art.exists():art.unlink()
 if src and src.exists():src.unlink()
 art=None;src=None
print(json.dumps({"v":"v2897","result":result,"native":native,"error":reason,"new_JPG":bool(art)},ensure_ascii=False))
manifest={
 "version":"v2897","baseline":"v2896","family":"pending-03",
 "product":"MISSHA M Perfect Cover BB Cream 50mL legacy gold pump No25 Warm Beige",
 "exact_target_shade":"25","stock_old_index":10,
 "source_name":"Kindlife third-party merchant, stock label not authenticated",
 "merchant_product_page":PAGE,"merchant_image_url":URL,
 "source_result":result,"source_failure_reason":reason,
 "native_size_px":native,"original_format":fmt,
 "original":str(src) if src else None,
 "original_sha256":sha256(src.read_bytes()).hexdigest() if src else None,
 "new_internal_1080_JPG":str(art) if art else None,
 "new_internal_1080_JPG_sha256":sha256(art.read_bytes()).hexdigest() if art else None,
 "new_internal_1080_JPG_bytes":total if art else None,
 "old_v2872_ghost_ridden_JPG_untouched":True,
 "real_photo_alternative_to_repeating_mask_cleanup":True,
 "shade_label_must_be_confirmed_by_visual":True,
 "real_own_50ml_edition_package_verified":False,
 "external_merchant_photo_commercial_license_verified":False,
 "original_MK_logo_authenticated":False,
 "new_sale_approvals":0,"new_public_URLs":0,
 "original_11_approved_groups_preserved":True,
 "original_55_public_urls_preserved":True,
 "old_JPGs_reencoded":0,"final_spreadsheet_shared":False
}
newstate=copy.deepcopy(st)
newstate["version"]="v2897";newstate["baseline"]="v2896"
newstate["families"]["pending-03"]["last_delta_version"]="v2897"
newstate["families"]["pending-03"]["release_status"]="NEW_CLEAN_LEGACY_NO25_SOURCE_CANDIDATE_HOLD_STOCK_PHOTO_RIGHTS" if art else "HOLD_NEW_MERCHANT_SOURCE_UNAVAILABLE"
newstate["families"]["pending-03"]["latest_photo_QA_checkpoint"]=(
 "v2897 independent exact legacy No25 merchant source and 1080 internal hero; do not repeat ghost trim, physical stock/rights/MK HOLD"
 if art else
 "v2897 merchant image one-shot access failed, existing v2872 grey ghost not released; move to next pending family")
newstate["families"]["pending-03"]["new_legacy_25_source_downloaded"]=int(bool(src))
newstate["families"]["pending-03"]["new_No25_1080_internal_photo"]=int(bool(art))
newstate["v2897_old_v2872_JPG_overwrites"]=0
newstate["new_sale_approvals"]=0;newstate["new_public_URLs"]=0
newstate["final_spreadsheet_shared"]=False
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2897.json").write_text(json.dumps(newstate,ensure_ascii=False,indent=2)+"\n")
