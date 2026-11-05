#!/usr/bin/env python3
"""v2894 | Inspect ONLY 48 option-specific images, no image regeneration.

Previous v2885 deduped 115 common photo-led QA images; this audit avoids
those and checks 48 option-key-linked candidate JPGs for actual 1080x1080
JPEG integrity, dimensions, size, and same-family perceptual similarity.
Similarity is an internal visual-review flag, never auto release or rejection.
"""
from pathlib import Path
from PIL import Image, ImageOps
from hashlib import sha256
import json,copy,itertools

ROOT=Path("qa-review")
INPUT=ROOT/"v2892-recover-21N-preexisting-1200native-photo-QA"/"69-option-crosswalk-v2892.json"
PRESTATE=ROOT/"v2893-peripera26ad-20color-canonical-name-photo-qa"/"stock30-incremental-state-v2893.json"
OUT=ROOT/"v2894-only-48-option-specific-JPG-technical-QA"
assert INPUT.is_file() and PRESTATE.is_file() and not OUT.exists()
mapping=json.loads(INPUT.read_text())
state=json.loads(PRESTATE.read_text())
assert mapping["version"]=="v2892" and len(mapping["option_rows"])==69
assert state["version"]=="v2893" and len(state["families"])==30
chosen=[r for r in mapping["option_rows"] if r["qa_image_kind"]!="single_option_family_hero_reference"]
assert len(chosen)==48,"Only the 48 option-specific JPG references should be checked"
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dhash(im):
 gray=ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS)
 px=list(gray.getdata())
 bits=0
 for y in range(8):
  for x in range(8):
   bits=(bits<<1)|int(px[y*9+x]>px[y*9+x+1])
 return bits
results=[]
for r in chosen:
 p=Path(r["qa_existing_image_path"])
 info={"family":r["family_id"],"inventory_source_index":r["source_index"],
       "option":r["inventory_option_raw"],"existing_JPG":str(p),
       "source_asset_modified":False,"retail_approved":False}
 try:
  assert p.as_posix().startswith("qa-review/"),"outside protected QA archive"
  assert p.is_file(),"file missing"
  assert p.suffix.lower()==".jpg","not JPG"
  info["bytes"]=p.stat().st_size
  assert 0<info["bytes"]<2_000_000,"outside 2 MB limit"
  with Image.open(p) as im:
   im.verify()
  with Image.open(p) as im:
   im.load()
   info["format"]=im.format
   info["native_size"]=list(im.size)
   info["mode"]=im.mode
   info["sha256"]=sha(p)
   if im.format=="JPEG" and im.size==(1080,1080):
    info["dhash_hex"]=f"{dhash(im):016x}"
   else:
    info["dhash_hex"]=None
   assert im.format=="JPEG","non JPEG content"
   assert im.size==(1080,1080),"not 1080x1080"
   info["technical_status"]="PASS_JPEG_1080_UNDER_2MB"
 except Exception as e:
  info["technical_status"]="HOLD_TECHNICAL"
  info["error"]=type(e).__name__+": "+str(e)[:180]
 results.append(info)
# only compare within different stock-option entries of the SAME family.
near=[]
for a,b in itertools.combinations(results,2):
 if a["family"]!=b["family"]:continue
 if a.get("dhash_hex") is None or b.get("dhash_hex") is None:continue
 dist=(int(a["dhash_hex"],16)^int(b["dhash_hex"],16)).bit_count()
 if dist<=5:
  near.append({"family":a["family"],"source_indexes":[a["inventory_source_index"],b["inventory_source_index"]],
    "dhash_distance":dist,"exact_sha_identical":a["sha256"]==b["sha256"],
    "status":"CHECK_SHADE_SPECIFICITY_ONLY_DO_NOT_AUTOMATICALLY_REJECT_OR_RELEASE"})
technical_pass=sum(x["technical_status"].startswith("PASS") for x in results)
status={"version":"v2894","baseline":"v2893","work":"only 48 already existing option-linked JPGs technical QA, no pixel edits",
  "prior_common_photo_115_perceptual_QA_not_repeated":True,
  "chosen_candidate_count":len(results),"technical_1080_jpeg_pass":technical_pass,
  "technical_holds":len(results)-technical_pass,
  "same_family_near_dhash_pairs":len(near),
  "old_11_retail_families_preserved":True,"old_55_public_urls_preserved":True,
  "original_JPGs_changed":False,"new_generated_images":0,"new_retail_approved":0,
  "licensed_commercial_photo_reuse":False,"actual_owned_stock_edition_verified":False,
  "original_MK_logo_authenticated":False,
  "specification":"native image pixel size checks on existing staged JPGs; hash closeness is not shade identity proof",
  "holds":[x for x in results if x["technical_status"]=="HOLD_TECHNICAL"],
  "near_pairs":near,"results":results,"final_spreadsheet_shared":False}
state2=copy.deepcopy(state)
state2["version"]="v2894";state2["baseline"]="v2893"
state2["v2894_specific_48_option_photo_technical_QA_count"]=len(results)
state2["v2894_technical_JPG_pass"]=technical_pass
state2["v2894_same_family_near_similarity_pairs"]=len(near)
state2["v2894_source_JPGs_regenerated"]=0
state2["v2894_manifest"]=str(OUT/"manifest.json")
state2["new_sale_approvals"]=0;state2["new_public_URLs"]=0
state2["final_spreadsheet_shared"]=False
OUT.mkdir(parents=True)
(OUT/"manifest.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
(OUT/"stock30-incremental-state-v2894.json").write_text(json.dumps(state2,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2894","checked":len(results),"pass":technical_pass,
                  "holds":len(results)-technical_pass,"near_pairs":len(near),
                  "new_sale_approvals":0,"images_regenerated":0},ensure_ascii=False))
