#!/usr/bin/env python3
"""v2934 - append the one visually screened cream scene to 3 prior BIOHEAL QA JPGs.
Creates a fresh internal-only 4-photo ZIP + contact. Never edits previous photo bytes,
does not license seller use, and does not invent the fifth image.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_STORED
from io import BytesIO
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

Q=Path("qa-review")
B20=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
B32=Q/"v2932-bioheal-two-domestic-exact-sku-gallery-12source-QA"
B33=Q/"v2933-bioheal-twelve-source-visual-bundle-claim-and-scene-QA"
OUT=Q/"v2934-bioheal-cream-four-real-source-scene-QA-only"
assert not OUT.exists(),"Never re-run a completed checkpoint"
m20=json.loads((B20/"manifest.json").read_text(encoding="utf-8"))
m32=json.loads((B32/"manifest.json").read_text(encoding="utf-8"))
m33=json.loads((B33/"manifest.json").read_text(encoding="utf-8"))
state=json.loads((B33/"stock30-incremental-state-v2933.json").read_text(encoding="utf-8"))
assert m33["version"]==state["version"]=="v2933" and len(state["families"])==30
assert m33["clean_new_scene_candidates"]==1 and m33["old_55_verified_URLs_changed"]==0
fam="pending-25"
old=next(x for x in m20["results"] if x["family"]==fam)
screens=next(x for x in m33["results"] if x["family"]==fam)
gallery=next(x for x in m32["results"] if x["family"]==fam)
assert old["actual_original_source_jpgs_in_zip"]==3
chosen=[x for x in screens["visual_decisions"] if x["provisional_distinct_scene"]]
assert len(chosen)==1 and chosen[0]["slot"]==4 and chosen[0]["closest_prior_dhash_hamming"]>=6
c=gallery["new_gallery_photos"][3]
assert c["reference_1080"]==chosen[0]["gallery_photo"]
assert c["reference_sha256"]==chosen[0]["sha256"] and c["native"]==[1000,1000]
assert c["source_listing_sku"]=="A000000246299" and not c["commercial_reuse_rights_granted"]
def jpeg(data):
 with Image.open(BytesIO(data)) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and len(data)<2000000
  return ImageOps.exif_transpose(im).convert("RGB")
def font(size):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)
 except:return ImageFont.load_default()
oldzip=Path(old["zip_path"])
assert sha256(oldzip.read_bytes()).hexdigest()==old["zip_sha256"]
photos=[]
with ZipFile(oldzip) as f:
 assert len(f.namelist())==3 and f.testzip() is None
 for i,name in enumerate(f.namelist(),1):
  b=f.read(name)
  photos.append({"slot":i,"data":b,"image":jpeg(b),"sha256":sha256(b).hexdigest(),
    "from":str(oldzip)+":"+name,"native_pixels":[1080,1080]})
original=Path(c["raw_original"]).read_bytes()
assert sha256(original).hexdigest()==c["native_sha256"]
with Image.open(BytesIO(original)) as im:assert im.size==(1000,1000)
new_bytes=Path(c["reference_1080"]).read_bytes()
assert sha256(new_bytes).hexdigest()==c["reference_sha256"]
photos.append({"slot":4,"data":new_bytes,"image":jpeg(new_bytes),
 "sha256":sha256(new_bytes).hexdigest(),"from":c["reference_1080"],
 "native_pixels":[1000,1000],"true_native_source_sha256":c["native_sha256"]})
assert len({x["sha256"] for x in photos})==4
OUT.mkdir(parents=True)
output=OUT/"BIOHEAL_NAD-PRIZCELL_Glow-Boost-Cream_50mL_4OF5_INTERNAL.zip"
with ZipFile(output,"w",compression=ZIP_STORED) as f:
 for z in photos:f.writestr(f"{z['slot']:02d}-existing-source-no-modification.jpg",z["data"])
with ZipFile(output) as f:
 assert len(f.namelist())==4 and f.testzip() is None
 for z in photos:assert f.read(f"{z['slot']:02d}-existing-source-no-modification.jpg")==z["data"]
sheet=Image.new("RGB",(1080,1080),"#f4f5f7"); d=ImageDraw.Draw(sheet)
d.text((24,18),"BIOHEAL NAD PRIZCELL | 4/5 SOURCE SCENES",font=font(27),fill="#242424")
d.text((24,59),"Internal QA only, photo permission and exact stock edition unverified",font=font(17),fill="#9d3030")
for i,z in enumerate(photos):
 x=20+(i%2)*525;y=112+(i//2)*447
 d.rounded_rectangle((x,y,x+510,y+421),radius=12,fill="white",outline="#ccc",width=2)
 pic=ImageOps.contain(z["image"],(486,340),Image.Resampling.LANCZOS)
 sheet.paste(pic,(x+255-pic.width//2,y+9+(340-pic.height)//2))
 label="1000px native new cream scene" if i==3 else "Existing archived image"
 d.text((x+10,y+360),f"Photo {i+1}: {label}",font=font(16),fill="#333333")
 d.text((x+10,y+391),"NOT MARKETPLACE APPROVED",font=font(14),fill="#a03232")
d.text((24,1030),"Fifth distinct source image still missing. No existing approval / URL altered.",font=font(16),fill="#555")
contact=OUT/"BIOHEAL_GlowBoostCream_4source_contact_INTERNAL.jpg"
sheet.save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
with Image.open(contact) as im:assert im.format=="JPEG" and im.size==(1080,1080)
assert contact.stat().st_size<2000000
state["families"][fam].update({"last_delta_version":"v2934",
 "release_status":"FOUR_SHA_VERIFIED_SOURCE_REFERENCES_INTERNAL_ONLY_ONE_MISSING",
 "v2934_four_source_zip":str(output),"v2934_four_source_contact":str(contact),
 "v2934_remaining_to_five":1,"sale_approved":False,
 "latest_photo_QA_checkpoint":"v2934 four 1080 QA JPG bytes preserved: three prior archived + one independently visually screened retail reference (native 1000px). Fifth missing, license, physical batch and genuine MK remain HOLD."})
manifest={"version":"v2934","baseline":"v2933","generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family":fam,"existing_previous_sources":3,"added_previously_screened_scene":1,
 "byte_verified_source_references":4,"remaining_photo_slots":1,
 "original_new_photography":0,"commercial_license_verified":False,
 "stock_edition_verified":False,"new_retail_approvals":0,"new_public_urls":0,
 "old_55_public_urls_changed":0,"old_11_approved_families_changed":0,
 "prior_QA_modified":0,"final_spreadsheet_shared":False,
 "zip_path":str(output),"zip_sha256":sha256(output.read_bytes()).hexdigest(),
 "contact":str(contact),"source_records":[{"slot":p["slot"],"path":p["from"],
 "sha256":p["sha256"],"native_pixels":p["native_pixels"],
 "commercial_rights_granted":False,"retail_approved":False} for p in photos]}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2934";state["baseline"]="v2933";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2934.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2934","product":"BIOHEAL Glow Boost Cream","source_JPGs":4,
 "missing":1,"zip_crc_passed":True,"sale_approvals":0},ensure_ascii=False))
