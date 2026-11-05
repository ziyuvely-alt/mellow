#!/usr/bin/env python3
"""v2889 | Batch photo-identity QA: GOODAL 25AD eye tube and two old Dr.G
50mL sunscreens. This is an IDENTITY RELEASE-GATE audit and a contact proof,
not a needless remake of the already-approved internal five-frame sets.

Hard read-only SHA / Git blob checks on all 15 previous source JPGs.
Green Sun Plus 2022 vs Brightening Sun Plus are visibly DIFFERENT editions,
and neither should be substituted for Moisture Sun. Goodal tube has silver
cap 2026 renewal photo but physically owned stock 25AD match unverified.
Dr.G prior info frames 02..05 contain UNAUTHENTICATED MK graphic.
No pixel recoloring, no sales/public URLs, no extra gifts inferred.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from hashlib import sha256, sha1
import json,copy,numpy as np
R=Path("qa-review")
PRESTATE=R/"v2888-obge300-highnative-official-merchant-source-candidates-QA"/"stock30-incremental-state-v2888.json"
GOODAL=R/"v2815-goodal-25ad-five-photo-set-silver-cap-crop-fixed"
DRG=R/"v2779-five-photo-first-product-groups-QA"
OUT=R/"v2889-goodal25ad-drg2022-two-edition-15photo-QA"
assert PRESTATE.is_file() and not OUT.exists()
state=json.loads(PRESTATE.read_text())
assert state["version"]=="v2888" and len(state["families"])==30
g=json.loads((GOODAL/"manifest.json").read_text())
a=json.loads((DRG/"pending-15"/"manifest.json").read_text())
b=json.loads((DRG/"pending-18"/"manifest.json").read_text())
assert g["version"]=="v2815" and g["family"]=="pending-21"
assert a["version"]==b["version"]=="v2779"
assert a["family"]=="pending-15" and b["family"]=="pending-18"
assert len(g["frames"])==len(a["frames"])==len(b["frames"])==5
sha=lambda p:sha256(p.read_bytes()).hexdigest()
blob=lambda p:sha1(b"blob "+str(p.stat().st_size).encode()+b"\x00"+p.read_bytes()).hexdigest()
rows=[];imagecache={}
for fam,folder,manifest,verification in [
 ("pending-21",GOODAL,g,"sha256"),("pending-15",DRG/"pending-15",a,"git_sha1"),
 ("pending-18",DRG/"pending-18",b,"git_sha1")
]:
 hashes=[]
 for r in manifest["frames"]:
  p=folder/(r["file"] if fam=="pending-21" else Path(r["path"]).name)
  assert p.exists(),str(p)
  expected=r["jpg_sha256"] if fam=="pending-21" else r["git_sha1"]
  assert (sha(p) if fam=="pending-21" else blob(p))==expected,(fam,r["slot"])
  assert p.stat().st_size<2_000_000
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   rgb=im.convert("RGB")
  imagecache[(fam,r["slot"])]=rgb
  hashes.append({"slot":r["slot"],"path":str(p),
    "immutable_git_blob":blob(p),"source_SHA256":sha(p),
    "size_bytes":p.stat().st_size,"native_staged_px":[1080,1080],
    "same_original_photo_scene_independently_proven":False})
 rows.append({"family":fam,"files":[*hashes],
  "frames_existing_total":5,"new_original_photographs_downloaded":0,
  "new_sale_approvals":0,"source_files_modified":False})
assert sum(len(x["files"]) for x in rows)==15

F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
# 1: DrG previous source photos show visibly different text and color bands.
# Source URLs and official editions remain unverified, so do not claim owned
# product year 2022 has been authenticated solely from historical art.
sun=Image.new("RGB",(1580,960),"#F4F2F4")
d=ImageDraw.Draw(sun)
d.text((18,16),"v2889 Dr.G 50mL | TWO DISTINCT TUBE PRODUCTS | REAL PHOTO QA ONLY",font=ft(23,True),fill="#463B49")
for i,(fid,head,sub) in enumerate([
 ("pending-15","GREEN MILD UP SUN+","Old white tube with GREEN band; stock marked 2022, edition NOT verified"),
 ("pending-18","BRIGHTENING UP SUN+","Old white tube with ORANGE band; do not substitute MOISTURE SUN")]):
 pic=ImageOps.contain(imagecache[(fid,1)],(720,725),Image.Resampling.LANCZOS)
 x=17+i*782
 sun.paste(pic,(x+(720-pic.width)//2,82+(725-pic.height)//2))
 d.text((x+13,815),head,font=ft(22,True),fill="#584A5B")
 d.text((x+13,857),sub,font=ft(12),fill="#766A79")
d.text((25,909),"UNVERIFIED MK ART IN OLD FRAMES 02..05  |  IMAGE USE LICENSE + OWNED BOX PENDING",font=ft(17,True),fill="#665B68")
sunpath=OUT/"v2889-DrG-Green-vs-Brightening-actual-source-two-identity-QA.jpg"
sun.save(sunpath,"JPEG",quality=91,optimize=True)
# 2: Goodal actual single-tube and raw skin-swatch from two sources,
# not FIVE independent shoots. The silver cap is correctly present.
eye=Image.new("RGB",(1580,960),"#F3F2F0")
d=ImageDraw.Draw(eye)
d.text((18,16),"v2889 GOODAL | 2026 RENEWAL TUBE / 25AD STOCK EDITION HOLD",font=ft(23,True),fill="#4B443E")
for i,(slot,heading) in enumerate([(1,"Genuine yellow tube & silver cap"),(3,"Actual tube + white cream texture")]):
 p=ImageOps.contain(imagecache[("pending-21",slot)],(720,731),Image.Resampling.LANCZOS)
 xx=18+i*782
 eye.paste(p,(xx+(720-p.width)//2,81+(731-p.height)//2))
 d.text((xx+17,830),heading,font=ft(17,True),fill="#5B4E47")
d.text((27,890),"5 QA JPGs from TWO independent real photos. Original stock generation & photo rights UNVERIFIED.",font=ft(17),fill="#71675C")
eyepath=OUT/"v2889-Goodal-renewal-yellow-tube-silver-cap-25ad-gate-QA.jpg"
eye.save(eyepath,"JPEG",quality=91,optimize=True)
for f in [sunpath,eyepath]:
 with Image.open(f) as test:
  test.load();assert test.format=="JPEG" and test.size==(1580,960)
 assert f.stat().st_size<2_000_000

# SHA verification AGAIN after card composition, demonstrate no mutation.
for entry in rows:
 for x in entry["files"]:
  assert sha(Path(x["path"]))==x["source_SHA256"]
families=copy.deepcopy(state["families"])
update={
 "pending-21":{
  "last_delta_version":"v2889",
  "latest_photo_QA_checkpoint":"v2815 5 preserved yellow 2026 silver-cap tube QA JPGs, only 2 independently sourced photographs, v2889 original 5/5 SHA verified and clear cap identity visual proof",
  "source_photo_five_existing_sha_verified":True,
  "five_frame_photo_count":5,"independent_actual_photo_sources":2,
  "no_unverified_gift_included":True,
  "release_status":"HOLD_STOCK_GENERATION_25AD_VS_2026_RIGHTS_MK"},
 "pending-15":{
  "last_delta_version":"v2889",
  "latest_photo_QA_checkpoint":"v2779 five existing 50mL Green Mild Sun Plus old package scenes, v2889 original 5/5 sha verified and green-band identity distinct from orange Brightening",
  "source_photo_five_existing_sha_verified":True,
  "old_2022_label_owner_confirmed":False,
  "release_status":"HOLD_OWNED_2022_PACKAGE_RIGHTS_MK"},
 "pending-18":{
  "last_delta_version":"v2889",
  "latest_photo_QA_checkpoint":"v2779 five existing 50mL Brightening Up Sun Plus old package scenes, v2889 original 5/5 sha verified and orange-band distinct from green Mild",
  "source_photo_five_existing_sha_verified":True,
  "brightness_not_moisture_product":True,
  "release_status":"HOLD_OWNED_EXACT_SUNPLUS_PACKAGE_RIGHTS_MK"}
}
for family,meta in update.items():
 families[family].update(meta)
 families[family]["sale_approved"]=False
 assert len(families[family]["latest_photo_QA_checkpoint"])>50
assert len(families)==30 and all(v.get("sale_approved") is False for v in families.values())
state.update(version="v2889",baseline="v2888",families=families,
 last_operation="Three-family 15 existing-photo SHA / physical generation QA gates and two new comparison board JPGs",
 old_11_published_groups_preserved=True,old_55_URLs_preserved=True,
 new_sales_approvals=0,new_public_URLs=0,final_spreadsheet_shared=False)
checkpoint=OUT/"stock30-incremental-state-v2889.json"
checkpoint.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
report={"version":"v2889","baseline":"v2888",
 "families":["pending-21","pending-15","pending-18"],
 "existing_source_JPGs_immutably_checked":15,
 "new_sale_artwork":0,"new_visual_QA_comparisons":2,
 "new_visual_JPGs":[{"file":str(sunpath),"sha256":sha(sunpath)},
                    {"file":str(eyepath),"sha256":sha(eyepath)}],
 "photo_rights_confirmed":False,"physical_owned_stock_packages_confirmed":False,
 "Goodal_25AD_in_same_physical_edition_as_2026_renewal":False,
 "DrG_owned_2022_packaging_exact_match_confirmed":False,
 "DrG_Brightening_vs_Moisture_are_not_interchangeable":True,
 "DrG_existing_frames2to5_source_MK_mark_unverified":True,
 "old_11_sales_groups_preserved":True,"old_55_published_urls_preserved":True,
 "old_photo_sources_changed":False,"new_retail_approved":0,"new_public_urls":0,
 "frame_provenance":rows,"checkpoint":str(checkpoint),"final_spreadsheet_shared":False,
 "next":"Pursue only outstanding owned-package photo labels and licensed imagery; do not regenerate already-preserved 5x3 scenes. Review outstanding families with no 5-frame QA set or missing photo source, and avoid repeating partial versions."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2889","families":3,"old_JPGs_checked":15,"new_QA_comparisons":2,"sales_approved":0}))
