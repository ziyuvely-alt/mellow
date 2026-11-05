#!/usr/bin/env python3
"""v2877: one-shot alternate CDN original endpoint for only missing
CLIO Mini 21N 5g source (v2876 thumb was 480px), plus genuine 30-family
resumption ledger delta grounded in prior real manifests.

DO NOT repeat successful 21C or 23N downloads or images.
DO NOT upgrade 480px source into purported native 1080 sales photo.
DO NOT edit any previous QA, approved 11 families, public 55 URLs,
or stock spreadsheet. If alternate fails, mark HOLD and advance queue.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
from hashlib import sha256
from urllib.request import Request,urlopen
from io import BytesIO
import json

R=Path("qa-review")
OUT=R/"v2877-mini-21N-alternate-original-and-30family-delta-QA"
assert not OUT.exists()
d2868=R/"v2868-founwear-21C21N-two-real-source-crops-and-stock30-resume"/"stock30-immutable-delta-checkpoint.json"
d2876=R/"v2876-clio-mini5g-three-independent-shade-photo-source-QA"/"manifest.json"
d2875=R/"v2875-clio-mini5g-obge-doublechamber-batch-identity-QA"/"manifest.json"
d2874=R/"v2874-obge-homme-15g-three-correct-shade-photo-qa"/"manifest.json"
d2873=R/"v2873-missha-moistup-two-shade-source-photo-swatch-QA"/"manifest.json"
d2872=R/"v2872-missha-bb-no25-background-ghost-geometry-alpha-QA"/"manifest.json"
d2869=R/"v2869-founwear-21c21n-option-photo-swatch-crosscheck-QA"/"manifest.json"
paths=[d2868,d2876,d2875,d2874,d2873,d2872,d2869]
assert all(x.is_file() for x in paths),[str(x) for x in paths if not x.is_file()]
sha=lambda p:sha256(p.read_bytes()).hexdigest()
prior,*data=[json.loads(x.read_text()) for x in paths]
v76,v75,v74,v73,v72,v69=data
assert [x["version"] for x in data]==["v2876","v2875","v2874","v2873","v2872","v2869"]
assert prior["counts"]["pending_families"]==30 and len(prior["families"])==30
assert v76["saved_originals"]==2 and v76["held_originals"]==1
assert next(x for x in v76["rows"] if x["shade"]=="21N")["status"].startswith("HOLD")
OUT.mkdir(parents=True)
# Source original alternate endpoint, not the lower-res thumb used in v2876.
url="https://bizweb.dktcdn.net/100/353/847/products/ava-san-pham-tren-website-25-3197fd52-4a2d-4b17-ae6b-96a905564ebf.jpg?v=1785052315773"
r21={"shade":"21N","label":"LINEN","source_page":"https://www.tanpopo.vn/phan-nuoc-2-loi-cang-bong-clio-kill-cover-mesh-glow-essential-cushion-spf50-5g",
    "source_fullres_url":url,"previous_failed":"v2876 retailer /thumb/1024x1024 endpoint returned only 480x480 WEBP",
    "status":"HOLD_FAILED_ALTERNATE_SOURCE", "retail_approved":False,
    "source_reuse_license_verified":False,"exact_inventory_package_verified":False}
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
try:
 with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/png,image/jpeg,*/*"}),timeout=14) as res:
  raw=res.read(8_000_001)
 assert 4000<len(raw)<8_000_000
 with Image.open(BytesIO(raw)) as im:
  im.load();fmt=im.format;size=im.size;picture=im.convert("RGB")
 assert fmt in ("JPEG","WEBP","PNG")
 r21.update(fetched_format=fmt,native_px=list(size))
 # Keep an original photo only if strictly larger than thumb result;
 # never call a rescaled 480px file a new high resolution source.
 if min(size)<550:raise ValueError("LOW_NATIVE_RESOLUTION_NOT_ACCEPTED: "+str(size))
 ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[fmt]
 native=OUT/("21N-LINEN-original-source-not-resized."+ext)
 native.write_bytes(raw)
 card=Image.new("RGB",(1080,1080),"#FBFAFC")
 d=ImageDraw.Draw(card)
 d.rounded_rectangle((45,46,1035,1033),radius=23,outline="#E3DAE6",width=2)
 d.text((77,74),"CLIO  /  MESH GLOW ESSENTIAL MINI 5g",font=ft(29,True),fill="#4D4253")
 d.rounded_rectangle((75,139,999,217),radius=15,fill="#F0E8F1")
 d.text((96,157),"21N LINEN   |   ORIGINAL MINI SOURCE PHOTO",font=ft(23,True),fill="#604F68")
 display=ImageOps.contain(picture,(925,727),Image.Resampling.LANCZOS)
 card.paste(display,((1080-display.width)//2,235+(727-display.height)//2))
 d.text((79,977),"MERCHANT PHOTO  /  INTERNAL QA ONLY  /  RIGHTS & EXACT STOCK ON HOLD",font=ft(16,True),fill="#746579")
 jpg=OUT/"21N-LINEN-mini-original-source-1080-QA.jpg"
 card.save(jpg,"JPEG",quality=93,subsampling=0,optimize=True)
 with Image.open(jpg) as verify:verify.load();assert verify.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000 and sha(native)==sha256(raw).hexdigest()
 r21.update(status="ALT_ORIGINAL_SOURCE_SAVED_AWAIT_VISUAL_AND_RIGHTS",
   original_file=str(native),original_sha256=sha(native),
   new_QA_jpg=str(jpg),jpg_sha256=sha(jpg),
   new_JPG_bytes=jpg.stat().st_size,photo_pixels_recolored=False)
except Exception as e:
 r21.update(status="HOLD_ALTERNATE_RESOLUTION_OR_ACCESS",reason=type(e).__name__+": "+str(e)[:220])
 print("HOLD 21N alternate:",str(e)[:180])

# One precise, portable, non-XLSX delta checkpoint. Use v2868 as
# immutable baseline, never make ungrounded jumps to sale approvals.
families=prior["families"]
for fid in families:
 f=families[fid]
 f["sale_approved"]=False
 f["release_status"]="QA_ONLY_RELEASE_BLOCKED"
 f["last_delta_version"]="v2868"
updates={
 "pending-02":("v2873",2,"2 QA shade photo+swatch comparisons, 21/23, commercial rights and Korean package edition HOLD"),
 "pending-03":("v2872",1,"No21/No25 old gold pump truealpha recovered v2871; No25 ghost trimmed v2872 but checker edge, rights and stock HOLD"),
 "pending-04":("v2877",2+(1 if r21["status"].startswith("ALT_ORIGINAL") else 0),
   "shared m/b original photo duplicates + v2711 broken alpha quarantined; distinct 21C/23N photos v2876; 21N "+r21["status"]),
 "pending-05":("v2869",2,"21C/21N real swatches linked to original merchant photos, exact 15g+refill and 21C/21N lookalike compact image HOLD"),
 "pending-10":("v2874",3,"correct dark-square 15g, 1 Ivory 2 Beige 3 Sand, original wrong round case quarantined; physical edition HOLD"),
 "pending-11":("v2875",1,"single 50mL+50mL dual-chamber bottle, NOT a 2-bottle set; old unverified MK-mark cards HOLD"),
 "pending-12":("v2783",0,"official brand 15mL vs owner inventory 15g requires physical label; DO NOT auto-convert")}
for fid,(version,count,note) in updates.items():
 assert fid in families
 families[fid].update(last_delta_version=version,
  latest_photo_QA_checkpoint=note, new_QA_files_since_v2868=count,
  open_blockers=["physical stock label/edition", "photo commercialization rights"],
  sale_approved=False)
# Preserve prior active state for families not revised; do not mark 5
# original JPGs as signed-off simply because they exist.
families["pending-13"]["latest_photo_QA_checkpoint"]="v2865: 30mL serum original RGB alpha correction residual red fringe still HOLD"
all_used={
 "v2873_pending02":str(d2873),"v2872_pending03":str(d2872),
 "v2876_pending04":str(d2876),"v2875_pending04_11":str(d2875),
 "v2869_pending05":str(d2869),"v2874_pending10":str(d2874)}
manifest={
 "version":"v2877","baseline":"v2876","num_original_existing_finished_groups":11,
 "num_original_verified_public_URLs":55,
 "num_pending_families":30,
 "retail_approvals_new":0,"new_public_urls":0,
 "final_excel_shared":False,
 "21N_alternative_source_result":r21,
 "new_21N_QA_JPGs":int("new_QA_jpg" in r21),
 "revisited_finished_shades_21C_23N":0,
 "new_source_photo_download_attempts":1,
 "input_previous_QA_manifests":all_used,
 "next":"Continue with incomplete pending-08 Peripera 20 shade canonical chart, pending-06 shade-specific real photo shortage, pending-12 physical label conflict, and other production blockers. Never redo completed 11/public55.",
 "old_published_images_modified":False,
 "old_QA_assets_modified":False,
 "commercial_rights_and_physical_lot_verified":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
state={
 "version":"v2877","baseline":"v2868","family_count":30,
 "previous_11_public_families_unchanged":True,"previous_55_public_urls_unchanged":True,
 "latest_7_family_delta_versions":{k:v[0] for k,v in updates.items()},
 "retail_release_approved_count":0,
 "sale_license_and_stock_identity_still_required":True,
 "families":families,
 "remaining_queue_without_regeneration":[
  {"family":"pending-08","action":"validate genuine Peripera 01..20 native photo swatches; 21..26AD excluded"},
  {"family":"pending-06","action":"source genuinely distinct CLIO Mesh Glow full 15g+refill shade photos, not 10 duplicate pairs"},
  {"family":"pending-12","action":"get actual MISSHA 15g vs brand 15mL unit label photo; no fake 1:1 conversion"},
  {"family":"pending-04","action":"visual source proof 21N alternative result and commercial rights hold"},
  {"family":"pending-13","action":"new clean rights-cleared droplet photo, not repeat failed local alpha"},
  {"family":"pending-03","action":"native mask quality and rights, no more v2872 geometry loops"}],
 "last_performed":"v2877 original-source single alternate and updated 30-family delta checkpoint"
}
(OUT/"stock30-delta-next-queue.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
assert len(state["families"])==30
assert all(not v["sale_approved"] for v in state["families"].values())
print(json.dumps({"v":"v2877","new_21N":int("new_QA_jpg" in r21),
 "21N_status":r21["status"],"pending_families":30,"sales_new":0}))
