#!/usr/bin/env python3
"""v2887 | Finish actual CLIO Mesh Blur pending-07 five-frame INTERNAL source
story without repeating existing v2860 option cutouts, v2861 option cards,
v2849 merchants or published sale imagery. Original photo bytes SHA-locked.

Three distinct merchant-variant-linked source photos: 19C, 19N, 21N.
Fourth: old CLIO official 6455 actual product + puff photo, SHA locked.
Fifth: archived retailer 'OliveYoung limited promotional gift' packaging
photo, NEVER construed as what the user's 15g x 2 owns. No auto-add gifts,
no fabricated swatches, no new shades, no authenticated MK logo.
"""
from pathlib import Path
from hashlib import sha1,sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,copy

R=Path("qa-review")
ALPHA=R/"v2860-clio-meshblur-three-truealpha-source-variants-QA"
OFF=R/"v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof"/"pending-07"/"01-official-6455-m-gif-REFERENCE.jpg"
GIFT=R/"v2667-original-photo-picks"/"original-photo-picks"/"pending-07-source-slot02-QA-ONLY.jpg"
STATE=R/"v2886-twenty-skipped-v2775-photos-only-append-perceptual-QA"/"stock30-incremental-state-v2886.json"
OUT=R/"v2887-clio-meshblur-three-stock-shade-and-five-source-QA"
assert not OUT.exists() and STATE.exists()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def gitblob(p):return sha1(b"blob "+str(p.stat().st_size).encode()+b"\x00"+p.read_bytes()).hexdigest()
assert gitblob(OFF)=="fe9668d9ed6237822271894b526fb1655f8972f7"
assert gitblob(GIFT)=="cc089ddb19f215886fa227943eb9ce7aa2c3fd75"
alpha_manifest=json.loads((ALPHA/"manifest.json").read_text())
assert alpha_manifest["version"]=="v2860" and len(alpha_manifest["per_shade"])==3
shade_rows={x["shade"]:x for x in alpha_manifest["per_shade"]}
assert set(shade_rows)=={"19C","19N","21N"}
state=json.loads(STATE.read_text())
assert state["version"]=="v2886" and len(state["families"])==30
assert state["families"]["pending-07"]["sale_approved"]==False
S={"19C":"LIGHT","19N":"PORCELAIN","21N":"LINEN"}
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BF="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(BF if b else F,n)
for x in shade_rows.values():
 path=Path(x["new_1080_JPG"])
 assert path.is_file() and sha(path)==x["jpg_sha256"]
 assert Path(x["original_PNG"]).is_file() and sha(Path(x["original_PNG"]))==x["png_sha256"]
with Image.open(OFF) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)
with Image.open(GIFT) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)

scenes=[
 {"slot":1,"name":"19C LIGHT","kind":"VARIANT_SHADE_SOURCE","path":Path(shade_rows["19C"]["new_1080_JPG"]),
  "subtitle":"True original-source shade reference; no new alpha generation.","shade":"19C"},
 {"slot":2,"name":"19N PORCELAIN","kind":"VARIANT_SHADE_SOURCE","path":Path(shade_rows["19N"]["new_1080_JPG"]),
  "subtitle":"Variant-linked cream appearance; no artificial swatch recolor.","shade":"19N"},
 {"slot":3,"name":"21N LINEN","kind":"VARIANT_SHADE_SOURCE","path":Path(shade_rows["21N"]["new_1080_JPG"]),
  "subtitle":"Variant-linked shade photo; owned set not inspected.","shade":"21N"},
 {"slot":4,"name":"OFFICIAL PRODUCT / PUFF PHOTO","kind":"OFFICIAL_PRODUCT_SCENE","path":OFF,
  "subtitle":"Actual CLIO official product view, same exact-edition stock not proven.","shade":None},
 {"slot":5,"name":"LIMITED PROMOTIONAL PACKAGING","kind":"PROMO_GIFT_NOT_CONFIRMED","path":GIFT,
  "subtitle":"Promo photo shows extra gift. Never promise gift with user's stock.","shade":None}
]
OUT.mkdir(parents=True)
cards=[]
for scene in scenes:
 with Image.open(scene["path"]) as original:
  original.load();assert original.size==(1080,1080) and original.format=="JPEG"
  src=original.convert("RGB")
 canvas=Image.new("RGB",(1080,1080),"#FAF9FC")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((37,35,1043,1044),radius=24,outline="#E2DAE7",width=2)
 d.text((65,61),"CLIO  |  KILL COVER MESH BLUR",font=font(32,True),fill="#453B4E")
 d.text((69,112),"15g x 2  |  USER-STOCK SET NOT YET VERIFIED",font=font(19),fill="#726478")
 d.rounded_rectangle((68,161,1012,225),radius=14,fill="#F0EAF3")
 d.text((86,180),f"{scene['slot']:02d}  {scene['name']}",font=font(24,True),fill="#53475B")
 d.line((69,243,1009,243),fill="#D6C8D8",width=3)
 max_size=(850,689) if scene["slot"]!=5 else (777,689)
 display=ImageOps.contain(src,max_size,Image.Resampling.LANCZOS)
 canvas.paste(display,((1080-display.width)//2,253+(689-display.height)//2))
 d.line((77,948,1003,948),fill="#DACFDC",width=2)
 # User sees frank QA limitations within each card.
 d.text((77,965),scene["subtitle"],font=font(14),fill="#685B6D")
 d.text((77,997),"INTERNAL QA ONLY  |  PHOTO LICENSE / STOCK / MK UNVERIFIED",font=font(14,True),fill="#796C7E")
 dst=OUT/f"CLIO-meshblur-15g2-{scene['slot']:02d}-{scene['kind']}-QA.jpg"
 canvas.save(dst,"JPEG",quality=94,optimize=True,subsampling=0)
 with Image.open(dst) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 assert dst.stat().st_size<2_000_000
 if scene["shade"]:
  assert sha(scene["path"])==shade_rows[scene["shade"]]["jpg_sha256"]
 else:assert gitblob(scene["path"]) in {"fe9668d9ed6237822271894b526fb1655f8972f7","cc089ddb19f215886fa227943eb9ce7aa2c3fd75"}
 cards.append({"slot":scene["slot"],"scene":scene["name"],
   "kind":scene["kind"],"shade":scene["shade"],
   "reused_JPG_source":str(scene["path"]),
   "reused_source_SHA256":sha(scene["path"]),
   "new_QA_1080_JPG":str(dst),"new_sha256":sha(dst),
   "new_file_bytes":dst.stat().st_size,
   "source_photo_recolored":False,
   "user_owned_refill_15g_promotion_set_verified":False,
   "external_photo_rights_verified":False,"retail_approved":False})
assert len(cards)==5 and len({x["new_sha256"] for x in cards})==5
# A single visual check of five story slots without old source mutation.
contact=Image.new("RGB",(1660,1230),"#F1EDF3")
draw=ImageDraw.Draw(contact)
draw.text((20,11),"v2887 CLIO MESH BLUR / 3 REAL STOCK SHADES + OFFICIAL + PROMO | NOT SALES",
          font=font(23,True),fill="#443748")
for j,card in enumerate(cards):
 with Image.open(card["new_QA_1080_JPG"]) as im:
  thumb=im.convert("RGB").resize((510,510),Image.Resampling.LANCZOS)
 x=15+(j%3)*548;y=55+(j//3)*564
 contact.paste(thumb,(x,y))
 draw.text((x+7,y+515),f"{j+1:02d} {card['kind']}",font=font(14,True),fill="#66596C")
cp=OUT/"v2887-meshblur-three-stock-option-plus-two-source-contact-QA.jpg"
contact.save(cp,"JPEG",quality=89,optimize=True)

stock=copy.deepcopy(state)
stock["version"]="v2887";stock["baseline"]="v2886"
stock["last_operation"]="v2887 five CLIO Mesh Blur QA JPGs from existing three exact shade photos + official product and explicitly UNVERIFIED promotional bundle image"
family=stock["families"]["pending-07"]
family.update(last_delta_version="v2887",
 latest_photo_QA_checkpoint="v2887 5 QA source-scene cards completed, exactly three stock colors 19C/19N/21N from v2860; one official single-product scene and separately quarantined limited gift scene",
 new_five_source_QA_cards=5,exact_available_shade_photo_count=3,
 official_m_gif_source_verified=True,original_promo_gift_not_owed_to_customers=True,
 exact_user_owned_15g_x2_refill_or_free_gift_not_proven=True,
 photo_license_verified=False,authentic_MK_logo_verified=False,
 release_status="QA_REFERENCE_FIVE_SCENES_HOLD_OWNED_EDITION_RIGHTS",sale_approved=False)
assert len(stock["families"])==30 and all(x["sale_approved"] is False for x in stock["families"].values())
stock["new_sales_approvals"]=0;stock["new_public_URLs"]=0;stock["final_spreadsheet_shared"]=False
st=OUT/"stock30-incremental-state-v2887.json"
st.write_text(json.dumps(stock,ensure_ascii=False,indent=2)+"\n")
m={"version":"v2887","baseline":"v2886","family":"pending-07",
 "product":"CLIO Kill Cover Mesh Blur Cushion Set 15g x2",
 "inventory_shades":["19C Light","19N Porcelain","21N Linen"],
 "source_v2860_true_alpha_pngs_redone":0,
 "original_v2861_shade_cards_redone":0,
 "new_five_1080_JPG_QA":5,"new_source_photos_downloaded":0,
 "old_11_published_families_preserved":True,
 "old_55_public_URLs_unchanged":True,
 "new_sale_approvals":0,"new_public_URLs":0,
 "commercial_photo_usage_rights_confirmed":False,
 "actual_owned_15g_x2_bundle_verified":False,
 "promo_gift_in_reference_not_inferred_in_owned_stock":True,
 "original_round_MK_logo_not_verified":True,
 "photos":cards,"contact":str(cp),"contact_SHA256":sha(cp),
 "family_30_checkpoint":str(st),"final_spreadsheet_shared":False,
 "next":"Verify actual owned Mesh Blur refill set SKU/pack and any accessories; never advertise promo gift from archive. Keep 19C/19N/21N true-alpha candidate as QA only until photo-use rights. Then continue incomplete family releases with sources and owner physical photos."}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2887","new_1080_QA":5,"skipped_completed_alpha":3,"previous_115_audits_not_rerun":True,"new_sales_approved":0}))
