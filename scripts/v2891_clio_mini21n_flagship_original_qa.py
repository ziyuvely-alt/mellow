#!/usr/bin/env python3
"""v2891. Resume v2890, test ONE new 21N mini 5g merchant-linked native source.
Never upscale a previously rejected 480px image or re-render prior work.
This creates INTERNAL QA evidence only. No sale rights, logo or publish approval.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from io import BytesIO
from hashlib import sha1,sha256
from PIL import Image, ImageOps
import json,copy

R=Path("qa-review")
PRIOR=R/"v2890-69-option-existing-photo-crosswalk-QA"/"manifest.json"
HOLD=R/"v2889-goodal25ad-drg2022-two-edition-15photo-QA"/"stock30-incremental-state-v2889.json"
OUT=R/"v2891-clio-mini21n-new-flagship-native-source-QA"
assert PRIOR.is_file() and HOLD.is_file() and not OUT.exists()
prior=json.loads(PRIOR.read_text())
old=json.loads(HOLD.read_text())
assert prior["version"]=="v2890" and prior["counts"]["qa_photo_references_linked"]==68
assert old["version"]=="v2889" and len(old["families"])==30
matches=[r for r in prior["option_rows"] if r["source_index"]==15]
assert len(matches)==1 and matches[0]["family_id"]=="pending-04"
assert matches[0]["normalized_option"]=="21N" and not matches[0]["qa_existing_image_path"]
url="https://cdn-media.hktvmall.com/hktv-mms/HKTV/mms/uploadProductImage/70e6/a21a/c378/hXJlFXjnmx20260105161204_1200.png"
page="https://www.hktvmall.com/hktv/en/main/CLIO-Hong-Kong-Flagship-Store/s/B1538002/Skincare-%26-Makeup/Skincare-%26-Makeup/Face-Makeup/Cushion-Foundation/Kill-Cover-Mesh-Glow-Essential-Cushion-Mini-21N-Linen/p/B1538002_S_8800322103036"
OUT.mkdir(parents=True)
source={"url":url,"product_page":page,"seller_page_title":"CLIO | Kill Cover Mesh Glow Essential Cushion Mini - 21N Linen",
        "exact_claim_on_product_page":"mini 5g 21N Linen","single_attempt_only":True,
        "commercial_rights_not_granted":True,
        "owned_stock_edition_not_authenticated":True}
status="HOLD_NEW_SOURCE_UNAVAILABLE"
raw_path=None
qa_path=None
reason=None
raw_sha=None
native=None
size=None
try:
 req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ShopeeInternalImageQA/1.0; research-only)","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"})
 with urlopen(req,timeout=15) as res:
  payload=res.read(8_000_001)
 assert 0<len(payload)<=8_000_000, "zero or >8MB source"
 with Image.open(BytesIO(payload)) as im:
  im.load()
  assert im.format in ("PNG","JPEG","WEBP"),"not a valid product photograph"
  fmt=im.format
  im=ImageOps.exif_transpose(im)
  native=list(im.size)
  assert min(native)>=1000,"insufficient native pixels, not upscaling a 480px photo"
  assert max(native)/min(native)<2,"unexpected poster/banner shape"
  rgb=Image.new("RGB",im.size,"white")
  if im.mode in ("RGBA","LA") or "transparency" in im.info:
   rgba=im.convert("RGBA")
   rgb.paste(rgba,mask=rgba.getchannel("A"))
  else: rgb=im.convert("RGB")
 filename="hktvmall-CLIO-mini5g-21N-merchant-source-original."+fmt.lower().replace("jpeg","jpg")
 raw_path=OUT/filename
 raw_path.write_bytes(payload)
 raw_sha=sha256(payload).hexdigest()
 canvas=Image.new("RGB",(1080,1080),"white")
 fit=ImageOps.contain(rgb,(1030,1030),Image.Resampling.LANCZOS)
 canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
 qa_path=OUT/"CLIO-MeshGlow-Mini5g-21N-merch-native-photo-1080-INTERNAL-QA.jpg"
 canvas.save(qa_path,"JPEG",quality=92,optimize=True,subsampling=0)
 size=qa_path.stat().st_size
 assert size<2_000_000,"1080 JPG exceeds 2MB limit"
 status="SOURCE_ARCHIVED_INTERNAL_QA_VISUAL_IDENTITY_AND_LICENSE_HOLD"
except Exception as exc:
 status="HOLD_NEW_SOURCE_FETCH_OR_QUALITY_FAILED"
 reason=str(type(exc).__name__)+": "+str(exc)[:350]
 # Do not retry failed merchant endpoint or upscale old 480px images.
 assert raw_path is None or raw_path.exists()

def git_blob(p):
 b=p.read_bytes()
 return sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
newmap=copy.deepcopy(prior)
newmap["version"]="v2891"
newmap["baseline_qa_version"]="v2890"
newmap["source_probe"]=source
newmap["source_probe_result"]=status
newmap["source_probe_error"]=reason
newmap["qa_new_originals_saved"]=1 if status.startswith("SOURCE_ARCHIVED") else 0
newmap["qa_new_1080_JPGs_saved"]=1 if status.startswith("SOURCE_ARCHIVED") else 0
newmap["commercial_approvals_added"]=0
newmap["final_xlsx_shared"]=False
row=next(x for x in newmap["option_rows"] if x["source_index"]==15)
if status.startswith("SOURCE_ARCHIVED"):
 row["qa_existing_image_path"]=str(qa_path)
 row["qa_git_blob_sha"]=git_blob(qa_path)
 row["qa_image_bytes"]=qa_path.stat().st_size
 row["qa_image_kind"]="merchant_page_linked_21N_mini_photo_visual_QA_not_authentic_edition"
 row["option_image_reference_stage"]="INTERNAL_QA_IMAGE_LINKED_RETAIL_HOLD"
 row["blockers"]=[
  "Exact 21N 5g merchant page image found, product visible identity not yet human-verified",
  "Commercial right for merchant image not granted",
  "Physical owned mini5g 21N packaging generation not authenticated",
  "Original MK logo source absent"
 ]
 newmap["counts"]["qa_photo_references_linked"]=69
 newmap["counts"]["no_existing_photo_links"]=0
 newmap["counts"]["named_option_reference_links"]+=1
 newmap["counts"]["prior_source_JPG_reencoded"]=0
else:
 row["blockers"].append("new HK CLIO flagship 1200px filename candidate failed single bounded fetch; "+str(reason))
row["retail_approved"]=False
row["photo_commercial_permission_verified"]=False
row["exact_user_owned_packaging_verified"]=False
newmap["counts"]["release_approved_now"]=0
newmap["counts"]["additional_published_urls"]=0
newmap["old_11_approved_families_preserved"]=True
newmap["old_55_public_urls_preserved"]=True
st=copy.deepcopy(old)
st["version"]="v2891"
st["baseline"]="v2890"
st["new_sale_approvals"]=0
st["new_public_URLs"]=0
st["final_spreadsheet_shared"]=False
st["families"]["pending-04"]["last_delta_version"]="v2891"
st["families"]["pending-04"]["latest_photo_QA_checkpoint"]=( 
 "v2891 single fresh CLIO HK brand-flagship mini21N 1200px archive internal reference, true stock/rights HOLD" if status.startswith("SOURCE_ARCHIVED") else
 "v2891 single bounded HK flagship 1200px source attempt HOLD; do not retry failed vendor endpoint")
st["families"]["pending-04"]["release_status"]="QA_ONLY_RELEASE_BLOCKED"
st["families"]["pending-04"]["new_21N_reference_source_attempts_v2891"]=1
st["families"]["pending-04"]["new_21N_internal_photo_QA_v2891"]=int(status.startswith("SOURCE_ARCHIVED"))
st["v2891_single_source_status"]=status
manifest={
 "version":"v2891","baseline":"v2890","target_family":"pending-04","stock_source_index":15,
 "target_product":"CLIO Kill Cover Mesh Glow Essential Cushion MINI 5g",
 "target_shade":"21N Linen","source":source,
 "result":status,"error":reason,"original_native_pixels":native,
 "archived_original":str(raw_path) if raw_path and raw_path.exists() else None,
 "archived_original_sha256":raw_sha,
 "new_1080_internal_QA_JPG":str(qa_path) if qa_path and qa_path.exists() else None,
 "new_1080_JPG_sha256":sha256(qa_path.read_bytes()).hexdigest() if qa_path and qa_path.exists() else None,
 "new_1080_JPG_bytes":size,
 "merchant_source_variant_identity_not_manually_visual_approved":True,
 "photo_rights_verified":False,"physical_owned_stock_verified":False,
 "authentic_original_MK_logo_verified":False,"new_retail_approved":0,
 "prior_11_commercial_approved_families_preserved":True,
 "prior_55_existing_public_URLs_preserved":True,
 "old_JPG_overwrites":0,"new_public_URLs":0,
 "new_family_crosswalk":"qa-review/v2891-clio-mini21n-new-flagship-native-source-QA/69-option-crosswalk-v2891.json",
 "new_full_state":"qa-review/v2891-clio-mini21n-new-flagship-native-source-QA/stock30-incremental-state-v2891.json"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(OUT/"69-option-crosswalk-v2891.json").write_text(json.dumps(newmap,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2891.json").write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")
assert len(newmap["option_rows"])==69 and len(st["families"])==30
print(json.dumps({"v":"v2891","result":status,"native_px":native,"qa_links":newmap["counts"]["qa_photo_references_linked"],"new_retail_approved":0,"error":reason},ensure_ascii=False))
