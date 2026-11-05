#!/usr/bin/env python3
"""v2883: MISSHA PDRN NAD+ Renew Peel Shot 25 existing source label audit.
Original product image visually reads 15mL/0.50fl oz; historic stock sheet
records 15G. Mass and volume units are NOT interchangeable without density.
No spreadsheet, existing five QA source photos, published sale image or
public URL modified. This run generates two new INTERNAL diagnostic JPGs,
one physical-inventory approval gate and updated immutable 30-family ledger.
Never describe a photographed merchant unit as the user's actual bottle.
"""
from pathlib import Path
from hashlib import sha1,sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,copy

R=Path("qa-review")
OUT=R/"v2883-missha-peelshot25-15G-vs-15mL-source-label-hold-QA"
OLD=R/"v2678-missha-clio-two-five-JPG-sets"/"pending-12"
PHOTO=R/"v2719-four-unprocessed-clio-missha-real-photo-cutouts"/"pending-12"/"01-actual-product-cutout-square-1080-QA.jpg"
STATE=R/"v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint"/"stock30-incremental-state-v2882.json"
assert not OUT.exists() and STATE.is_file() and PHOTO.is_file()
sha=lambda p:sha256(p.read_bytes()).hexdigest()
blob=lambda p:sha1(b"blob "+str(p.stat().st_size).encode()+b"\0"+p.read_bytes()).hexdigest()
assert blob(PHOTO)=="8ca92081ffa1157c766e88724f70947b40e50c30"
EXISTING=[
 "01-existing-original-slot01-unchanged-QA.jpg",
 "02-existing-original-slot02-unchanged-QA.jpg",
 "03-existing-original-slot03-unchanged-QA.jpg",
 "04-safe-original-info-QA.jpg",
 "05-safe-original-info-QA.jpg"]
sources=[OLD/f for f in EXISTING]
assert all(p.is_file() for p in sources)
assert blob(sources[1])=="a5b86aba9e5d6014c6189a6921967ff1df931199"
assert blob(sources[2])=="5266ba2323f3f954d8ded9d1de26f4c9d771364e"
locked={str(p):sha(p) for p in [PHOTO,*sources]}
with Image.open(PHOTO) as im:
 im.load()
 assert im.format=="JPEG" and im.size==(1080,1080)
 main=im.convert("RGB")
with Image.open(sources[2]) as im:
 im.load()
 assert im.format=="JPEG" and im.size==(1080,1080)
 second=im.convert("RGB")
state=json.loads(STATE.read_text())
assert state["version"]=="v2882" and len(state["families"])==30
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda s,b=False:ImageFont.truetype(bold if b else font,s)
OUT.mkdir(parents=True)
# Deliberately full original-photo citation alongside enlarged *real* label.
# The native photo label is very small. Nearest upscale exposes true original
# pixels, not super-resolution or text invention. Text below is a separate
# paraphrase of verified official product description.
top=Image.new("RGB",(1080,1080),"#F9F6F6")
d=ImageDraw.Draw(top)
d.rounded_rectangle((34,36,1045,1044),radius=24,outline="#DDD6DA",width=2)
d.text((67,67),"MISSHA | RENEW PEEL SHOT 25",font=ft(34,True),fill="#463A41")
d.text((67,124),"ORIGINAL PHOTOGRAPH / PRODUCT LABEL INVESTIGATION",font=ft(19),fill="#67575F")
photo=ImageOps.contain(main,(620,690),Image.Resampling.LANCZOS)
top.paste(photo,(36+(620-photo.width)//2,172+(690-photo.height)//2))
# Native pixel coordinates of product bottle and printed 15mL. Width small.
label=main.crop((449,638,628,785))
zoom=ImageOps.contain(label,(356,413),Image.Resampling.NEAREST)
d.rounded_rectangle((676,244,1030,789),radius=12,fill="#FFFFFF",outline="#DFD9DF",width=2)
top.paste(zoom,(676+(354-zoom.width)//2,306+(413-zoom.height)//2))
d.text((687,262),"NATIVE LABEL CROP",font=ft(19,True),fill="#51414D")
d.text((687,741),"PIXEL ZOOM  |  NO AI FILL",font=ft(15),fill="#796E78")
d.line((66,870,1018,870),fill="#DFD3DD",width=2)
d.text((74,891),"BRAND SPECIFICATION: 15mL (volume)",font=ft(23,True),fill="#59434B")
d.text((74,945),"Original source photo kept unchanged. QA ONLY.",font=ft(18),fill="#71636B")
a=OUT/"01-MISSHA-peelshot-source-15mL-label-photo-1080-QA.jpg"
top.save(a,"JPEG",quality=94,subsampling=0,optimize=True)

# The decision gate is a clear diagnostic image, not a sale-friendly frame.
b=Image.new("RGB",(1080,1080),"#F9F7F8")
d=ImageDraw.Draw(b)
d.rounded_rectangle((40,36,1042,1045),radius=25,outline="#DDD3D8",width=2)
d.text((74,60),"MISSHA RENEW PEEL SHOT 25",font=ft(33,True),fill="#493B44")
d.text((74,121),"INVENTORY LABEL CONFLICT / QA HOLD",font=ft(22,True),fill="#67515E")
d.rounded_rectangle((70,181,1015,365),radius=18,fill="#EEE5EB")
d.text((99,204),"HISTORIC STOCK RECORD",font=ft(20),fill="#76606D")
d.text((100,250),"15G",font=ft(65,True),fill="#643B4F")
d.text((502,266),"vs",font=ft(39,True),fill="#7F6D79")
d.text((647,204),"BRAND / PHOTO LABEL",font=ft(20),fill="#76606D")
d.text((649,250),"15mL",font=ft(65,True),fill="#643B4F")
p=ImageOps.contain(second,(600,550),Image.Resampling.LANCZOS)
b.paste(p,((1080-p.width)//2,391+(550-p.height)//2))
d.line((80,948,997,948),fill="#D7CBD2",width=2)
d.text((81,964),"NO AUTOMATIC 15g -> 15mL CONVERSION",font=ft(20,True),fill="#584653")
d.text((81,1002),"Requires photograph of the user's actual box/bottle.",font=ft(15),fill="#796B74")
c=OUT/"02-MISSHA-peelshot-15G-vs-15mL-explicit-HOLD-1080-QA.jpg"
b.save(c,"JPEG",quality=94,subsampling=0,optimize=True)

for item in (a,c):
 with Image.open(item) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 assert item.stat().st_size<2_000_000
assert all(sha(Path(p))==h for p,h in locked.items())
families=copy.deepcopy(state["families"])
f=families["pending-12"]
f.update(last_delta_version="v2883",
 latest_photo_QA_checkpoint="v2883: original source native bottle label / official 15mL vs recorded 15G side-by-side diagnostic images; physical stock label missing; 5 existing JPG preserved",
 release_status="HOLD_PHYSICAL_LABEL_15G_VS_15ML",
 evidence_photo_review_complete=True,
 open_blockers=["User-owned actual package label must be photographed","Photo commercial usage permission missing"],
 source_brand_net_volume="15mL",stock_recorded_unit_raw="15G",
 units_not_auto_converted=True,sale_approved=False)
assert len(families)==30 and all(v.get("sale_approved") is False for v in families.values())
updated={**state, "version":"v2883","baseline":"v2882",
 "families":families,"next_work_queue":[
 {"family":"pending-12","status":"HOLD_PHYSICAL_LABEL","why":"Photo and official spec 15mL; raw stock 15G; requires user's physical unit photo"},
 *[x for x in state.get("next_work_queue",[]) if x.get("family")!="pending-12"]],
 "last_operation":"v2883 2 documentary label and contrast QA JPGs",
 "old_11_families_preserved":True,"old_55_URLs_preserved":True,
 "new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False}
checkpoint=OUT/"stock30-incremental-state-v2883.json"
checkpoint.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n")
manifest={"version":"v2883","baseline":"v2882","family":"pending-12",
 "item":"MISSHA PDRN NAD+ Renew Peel Shot 25",
 "historical_inventory_unit":"15G","brand_owned_official_spec":"15mL",
 "brand_Korean_listing":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236",
 "do_not_convert_mass_to_volume":True,
 "new_evidence_JPG_1080_count":2,"new_evidence":[
 {"type":"native_15mL_photo_label_zoom","path":str(a),"sha256":sha(a)},
 {"type":"original_stock_conflict_HOLD","path":str(c),"sha256":sha(c)}],
 "old_5_QA_JPGs_unchanged":True,"old_photo_SHA256":locked,
 "actual_owned_stock_label_photo_received":False,
 "exact_user_stock_edition_verified":False,
 "existing_11_commercial_groups_unchanged":True,
 "existing_55_public_urls_unchanged":True,
 "new_sale_approvals":0,"new_public_URLs":0,
 "next": "Do not render sales/product copy based on 15mL vs 15G until owned bottle and box label evidence. Move to pending22 edge check and pending21 edition, no old recreation.",
 "checkpoint":str(checkpoint),"final_spreadsheet_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2883","new_label_JPGs":2,"old_sources_modified":0,"pending_families":30,"public_URL_new":0}))
