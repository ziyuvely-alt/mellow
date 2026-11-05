#!/usr/bin/env python3
"""v2868 | CLIO Founwear stock image project checkpoint.
From v2867's SHA-pinned genuine photographed cheek/forearm swatches,
crop only pre-existing labeled 21C and 21N source pixels, making two
DISTINCT reference cards per shade; QA only, with no invented colors.
Also snapshot the actual 30-family queue incrementally, reusing v2848
and immutable later manifests. Do not touch signed-off 11 groups/55 URLs,
source photos, existing QA, or spreadsheets.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json

R=Path("qa-review")
SRC=R/"v2867-founwear-21C-21N-real-swatch-source-evidence-QA"
OUT=R/"v2868-founwear-21C21N-two-real-source-crops-and-stock30-resume"
assert not OUT.exists()
m=json.loads((SRC/"manifest.json").read_text())
assert m["version"]=="v2867" and m["real_source_photos_saved"]==3
srcs={x["id"]:x for x in m["sources"]}
assert all(x["status"].startswith("SOURCE_ART_BYTES_SAVED") for x in srcs.values())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
fontroot="/usr/share/fonts/truetype/dejavu"
ft=lambda n,b=False:ImageFont.truetype(fontroot+("/DejaVuSans-Bold.ttf" if b else "/DejaVuSans.ttf"),n)
# Actual native resolution. All crops independently contain the printed source
# label and ACTUAL, non-recolored product smear. No artificial color-chip tiles.
crops=[
 {"shade":"21C","name":"LINGERIE","src":"merchant-cheek-five-labeled-shades",
  "crop":[410,560,978,888],"subject":"21C photographed cheek foundation swatch and native source label"},
 {"shade":"21C","name":"LINGERIE","src":"merchant-forearm-five-labeled-shades",
  "crop":[470,182,816,609],"subject":"21C photographed forearm foundation swatch and native source label"},
 {"shade":"21N","name":"LINEN","src":"merchant-cheek-five-labeled-shades",
  "crop":[500,765,1080,1066],"subject":"21N photographed cheek foundation swatch and native source label"},
 {"shade":"21N","name":"LINEN","src":"merchant-forearm-five-labeled-shades",
  "crop":[666,92,998,535],"subject":"21N photographed forearm foundation swatch and native source label"}
]
OUT.mkdir(parents=True)
rows=[]
for i,c in enumerate(crops,1):
 entry=srcs[c["src"]]
 p=Path(entry["raw_path"])
 assert p.is_file() and sha(p)==entry["raw_sha256"],"source SHA mismatch"
 with Image.open(p) as im:
  im.load()
  assert list(im.size)==entry["native_px"]
  original=im.convert("RGB")
 x0,y0,x1,y1=c["crop"]
 assert 0<=x0<x1<=original.width and 0<=y0<y1<=original.height
 crop=original.crop(c["crop"])
 assert min(crop.size)>=295
 canvas=Image.new("RGB",(1080,1080),"#FBFAF9")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((35,35,1045,1045),radius=23,outline="#E0DADC",width=2)
 d.text((74,69),"CLIO KILL COVER FOUNWEAR",font=ft(33,True),fill="#443940")
 d.text((74,134),f'{c["shade"]}  {c["name"]}   |   REAL SWATCH',font=ft(28,True),fill="#694D5C")
 d.line((74,193,1002,193),fill="#D9CCD5",width=3)
 fitted=ImageOps.contain(crop,(930,700),Image.Resampling.LANCZOS)
 canvas.paste(fitted,((1080-fitted.width)//2,210+(700-fitted.height)//2))
 d.line((74,928,1002,928),fill="#DED1D8",width=2)
 d.text((76,945),"UNALTERED SOURCE PHOTO CROP  |  INTERNAL QA",font=ft(19,True),fill="#66555E")
 d.text((76,992),"PHOTO RIGHTS AND EXACT STOCK EDITION NOT VERIFIED",font=ft(15),fill="#877884")
 fn=OUT/f'{i:02d}-CLIO-Founwear-{c["shade"]}-{c["src"].split("-")[1]}-labeled-swatch-1080-QA.jpg'
 canvas.save(fn,"JPEG",quality=95,optimize=True,subsampling=0)
 with Image.open(fn) as im:
  assert im.format=="JPEG" and im.size==(1080,1080)
 assert fn.stat().st_size<2_000_000
 assert sha(p)==entry["raw_sha256"]
 rows.append({**c,
  "original_source_path":str(p),
  "original_source_SHA256":entry["raw_sha256"],
  "original_source_native_px":entry["native_px"],
  "source_crop_coord_original_px":c["crop"],
  "output_JPG":str(fn),"output_sha256":sha(fn),"bytes":fn.stat().st_size,
  "photo_RGB_swatches_recolored":False,"new_photograph_fabricated":False,
  "source_modified":False,"native_label_requires_final_reader_check":True,
  "public_use_allowed":False})
assert len(rows)==4 and len({r["output_sha256"] for r in rows})==4
sheet=Image.new("RGB",(1580,1160),"#F0EEF0")
d=ImageDraw.Draw(sheet)
d.text((20,14),"v2868 FOUNWEAR | 21C vs 21N | CHEEK + FOREARM REAL SWATCH SOURCES | QA ONLY",
       font=ft(21,True),fill="#453B48")
for idx,row in enumerate(rows):
 with Image.open(row["output_JPG"]) as im:
  frame=im.convert("RGB").resize((750,510),Image.Resampling.LANCZOS)
 x=22+780*(idx%2);y=59+548*(idx//2)
 sheet.paste(frame,(x,y))
 d.text((x,y+513),row["shade"]+"   "+row["src"],font=ft(16,True),fill="#514450")
contact=OUT/"v2868-four-labeled-source-swatch-crops-QA.jpg"
sheet.save(contact,"JPEG",quality=87,optimize=True)
# Build review-only *state snapshot* from existing 30-family inventory + v2848.
# Never call stage-available "done": published is still 11 groups only.
baseline=R/"v2848-30-family-release-state-and-next-queue"/"manifest.json"
v2848=json.loads(baseline.read_text())
families=v2848["current_work"]["per_family"]
assert len(families)==30 and {x["id"] for x in families}=={"pending-"+str(i).zfill(2) for i in range(1,31)}
state={}
for f in families:
 state[f["id"]]={
   "product":f["product"],"release_status":"QA_ONLY_RELEASE_BLOCKED",
   "latest_photo_QA_checkpoint":None,
   "technical_QA_new_since_v2848":False,
   "needs_real_stock_and_photo_rights":True,
   "sale_approved":False}
state["pending-01"].update(latest_photo_QA_checkpoint="v2859: 4 MISSHA shades 21,23,25,27 reference photo cards",technical_QA_new_since_v2848=True)
state["pending-05"].update(latest_photo_QA_checkpoint="v2868: 3 white-puff true-alpha cards v2866 + 2 physical shade swatch labels x2 source photos v2868; 21C/21N compact still HOLD duplicate risk",technical_QA_new_since_v2848=True)
state["pending-06"].update(latest_photo_QA_checkpoint="v2861: 5-option gallery all 10 pairs near-duplicate; DO NOT PROMOTE shade-specific originals",technical_QA_new_since_v2848=True)
state["pending-07"].update(latest_photo_QA_checkpoint="v2861: CLIO Mesh Blur 19C/19N/21N 3 alpha QA option cards",technical_QA_new_since_v2848=True)
state["pending-13"].update(latest_photo_QA_checkpoint="v2865: serum 30mL dropper 795-pixel alpha trim, residual remains, HOLD new photo",technical_QA_new_since_v2848=True)
state["pending-22"].update(latest_photo_QA_checkpoint="v2857: intact OBgE 300mL candidate; high-res/halo review and rights remain HOLD",technical_QA_new_since_v2848=True)
updates={
 "version":"v2868","baseline":"v2867","checkpoint_scope":"Only successfully persisted GitHub QA art; never mark as approved",
 "QA_additions":{"pending-05":{"verified_swatches_from_2_distinct_sources":4,"source_original_RGB_files_changed":0,
  "swatch_shades":["21C","21N"],"compact_photos_21C_21N_still_blocked_by_similarity":True}},
 "families":state,
 "counts":{"pending_families":30,"technical_QA_progress_families_since_v2848":sum(v["technical_QA_new_since_v2848"] for v in state.values()),
           "technical_QA_done_not_equivalent_to_sale_approval":True,
           "new_sales_approved":0,"new_public_URLs":0},
 "preserve":{"existing_retail_groups":11,"public_URLs":55,"no_existing_files_overwritten":True},
 "remaining_blockers":["exact owned-stock edition and giftset components", "source commercial image usage rights", "original MK logo authenticated", "human visual sales QA"],
 "next_no_repeat":["Treat pending-05 19C/19N/23N v2866 source-cutout cards as ready for final rights/stock QA only",
  "21C/21N actual swatches now exist; exact-option product photography still unverified",
  "pending-06 five merchant photo files near duplicates: source truly distinct originals rather than reprocessing",
  "pending-02/03 Korean stock vs foreign edition must be verified prior to reusing regional image archive",
  "pending-10 OBgE 15g stock vs 13g hold; pending-12 MISSHA 15mL vs stock 15g hold",
  "Do not redo partial MISSHA 30mL serum cap alpha; obtain cleaner licensed original instead"]
}
resumepath=OUT/"stock30-immutable-delta-checkpoint.json"
resumepath.write_text(json.dumps(updates,ensure_ascii=False,indent=2)+"\n")
manifest={
 "version":"v2868","baseline":"v2867","family":"pending-05",
 "new_swatches":4,"new_source_photos_downloaded":0,
 "source_photos_original_bytes_preserved":True,
 "source_swatches_recolored":False,
 "native_user_owned_stock_confirmed":False,
 "user_has_commercial_photo_rights_verified":False,
 "new_sales_approved":0,"new_public_urls":0,
 "previous_11_signed_off_families_preserved":True,
 "previous_55_verified_public_URLs_preserved":True,
 "new_spreadsheet_created_or_shared":False,
 "items":rows,"contact":str(contact),"contact_SHA256":sha(contact),
 "stock30_checkpoint":str(resumepath),
 "next":"Use 21C/21N swatch crops as internal validation only. Need actual CLIO 15g+refill boxed set, rights and distinct shade-linked product photos before sale. Do not repeat near-duplicate generic photos."
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2868","four_photo_crops":4,"new_public_urls":0,
 "frozen_30_family_state":len(state),"real_QA_delta_families":updates["counts"]["technical_QA_progress_families_since_v2848"],
 "pending_05_retail_approved":False},ensure_ascii=False))
