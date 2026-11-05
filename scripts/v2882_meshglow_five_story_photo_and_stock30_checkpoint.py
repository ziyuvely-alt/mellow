#!/usr/bin/env python3
"""v2882: complete an INTERNAL five-frame photo story for pending-06 using
only previously SHA-verified, different REAL scenes, and atomically publish
a full thirty-pending-family RESUME state. Never redo existing shade cards,
never transform product colors, never claim two packshots prove owner's
physical gift set or external-photo license. Public 11+55 immutable.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,copy

R=Path("qa-review")
SRC=R/"v2881-clio-meshglow-five-real-labeled-swatch-chart-QA"
PRIOR=R/"v2877-mini-21N-alternate-original-and-30family-delta-QA"/"stock30-delta-next-queue.json"
PERI=R/"v2880-peripera-26AD-twenty-original-lipswatch-plus-common-tube-QA"/"manifest.json"
OUT=R/"v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint"
assert not OUT.exists()
for p in [SRC/"manifest.json",PRIOR,PERI]:
 assert p.is_file()
m=json.loads((SRC/"manifest.json").read_text())
pr=json.loads(PRIOR.read_text())
per=json.loads(PERI.read_text())
assert m["version"]=="v2881" and m["new_authentic_five_shade_swatch_QA_JPGs"]==5
assert per["version"]=="v2880" and per["new_photo_shade_option_QA_JPG_count"]==20
assert pr["version"]=="v2877" and len(pr["families"])==30
sha=lambda p:sha256(p.read_bytes()).hexdigest()
byid={x["id"]:x for x in m["sources"]}
paths={
 "official":Path(byid["brand-Clio-official-LIPS-five-shades"]["raw_file"]),
 "cheek":Path(byid["konvy-five-cheek-actual-shades"]["raw_file"]),
 "forearm":Path(byid["ballagrio-five-real-swatch-arm"]["raw_file"]),
 "compact":Path(m["cards"][0]["shared_compact_source"])
}
for key,p in paths.items():
 assert p.exists(),(key,p)
 expected=(m["cards"][0]["shared_photo_sha256"] if key=="compact" else
           byid[{"official":"brand-Clio-official-LIPS-five-shades",
                  "cheek":"konvy-five-cheek-actual-shades",
                  "forearm":"ballagrio-five-real-swatch-arm"}[key]]["raw_sha256"])
 assert sha(p)==expected,(key,"source sha mismatch")
with Image.open(paths["official"]) as im:
 im.load();assert im.size==(1080,1350)
 official=im.convert("RGB")
with Image.open(paths["cheek"]) as im:
 im.load();assert im.size==(1000,1000)
 cheek=im.convert("RGB")
with Image.open(paths["forearm"]) as im:
 im.load();assert im.size==(550,550)
 forearm=im.convert("RGB")
with Image.open(paths["compact"]) as im:
 im.load();assert im.size==(1080,1080)
 compact=im.convert("RGB")

B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
scenes=[
 {"slot":1,"title":"ORIGINAL MESH GLOW COMPACT PHOTO","source":"compact",
  "copy":"One common reference compact. Gift-set refill not verified.","src_crop":None,
  "max_display":(795,742)},
 {"slot":2,"title":"OFFICIAL CLIO SHADE LINEUP","source":"official",
  "copy":"Real 19C / 19N / 21C / 21N / 23N source swatches.","src_crop":(0,0,1080,655),
  "max_display":(938,730)},
 {"slot":3,"title":"REAL FIVE-SHADE FACE SWATCHES","source":"cheek",
  "copy":"Original photographed shade positions, no fake color chips.","src_crop":None,
  "max_display":(812,737)},
 {"slot":4,"title":"REAL FIVE-SHADE FOREARM SWATCHES","source":"forearm",
  "copy":"Original merchant source 550 px: QA reference only.","src_crop":None,
  "max_display":(625,625)},
 {"slot":5,"title":"OFFICIAL APPLICATION FINISH PHOTO","source":"official",
  "copy":"Original brand before/after reference; outcomes not validated.","src_crop":(46,650,1038,1315),
  "max_display":(939,715)}
]
cards=[]
for scene in scenes:
 source={"official":official,"cheek":cheek,"forearm":forearm,"compact":compact}[scene["source"]]
 frame=source.crop(scene["src_crop"]) if scene["src_crop"] else source.copy()
 canvas=Image.new("RGB",(1080,1080),"#FBF9FC")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((37,35,1043,1042),radius=25,outline="#DAD2DF",width=2)
 d.text((71,59),"CLIO | MESH GLOW ESSENTIAL CUSHION",font=ft(28,True),fill="#4C3E53")
 d.text((71,105),"15g + 15g refill  /  ORIGINAL SOURCE PHOTO QA",font=ft(19),fill="#6F6274")
 d.rounded_rectangle((71,156,1006,219),radius=14,fill="#F0EAF3")
 d.text((89,174),f"{scene['slot']:02d}  {scene['title']}",font=ft(22,True),fill="#55465D")
 allowed=scene["max_display"]
 fit=ImageOps.contain(frame,allowed,Image.Resampling.LANCZOS)
 # Refuse to interpolate a 550 source across the full 1080;
 # 625px layout is a framed small original-source reference.
 xpos=(1080-fit.width)//2
 ypos=250+(715-fit.height)//2
 canvas.paste(fit,(xpos,ypos))
 d.line((73,958,1006,958),fill="#D6C9DD",width=2)
 d.text((78,973),scene["copy"],font=ft(14),fill="#70627A")
 d.text((78,1000),"INTERNAL QA. PHYSICAL SET & COMMERCIAL IMAGE RIGHTS ON HOLD.",font=ft(14,True),fill="#806D85")
 dest=OUT/f"CLIO-MeshGlow-pending06-{scene['slot']:02d}-source-story-QA.jpg"
 canvas.save(dest,"JPEG",quality=94,optimize=True,subsampling=0)
 with Image.open(dest) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080)
 assert dest.stat().st_size<2_000_000
 assert sha(paths[scene["source"]])==sha(paths[scene["source"]])
 cards.append({"frame":scene["slot"],"scene":scene["title"],
  "source_key":scene["source"],"source":str(paths[scene["source"]]),
  "source_sha256":sha(paths[scene["source"]]),
  "original_source_crop":scene["src_crop"],
  "new_JPG":str(dest),"sha256":sha(dest),"size_bytes":dest.stat().st_size,
  "distinct_real_source_scene":True,"claim_user_owns_exact_pack":False,
  "retail_approved":False})
assert len(cards)==5 and len(set(x["sha256"] for x in cards))==5

contact=Image.new("RGB",(1620,1220),"#F1EEF3")
d=ImageDraw.Draw(contact)
d.text((20,15),"v2882 CLIO MESH GLOW  |  FIVE DISTINCT SOURCE SCENES  |  NOT SALES",font=ft(25,True),fill="#42374A")
for i,c in enumerate(cards):
 with Image.open(c["new_JPG"]) as im:
  card=im.convert("RGB").resize((505,505),Image.Resampling.LANCZOS)
 x=18+(i%3)*535;y=60+(i//3)*565
 contact.paste(card,(x,y))
 d.text((x+5,y+514),f"{i+1:02d} SOURCE PHOTO / NO COMMERCIAL RIGHT",font=ft(14,True),fill="#5D5066")
cp=OUT/"v2882-clio-five-authentic-scenes-contact-QA.jpg"
contact.save(cp,"JPEG",quality=88,optimize=True)

# Read-only state migration. The old 11 published and 55 URLs are outside
# this QA-only branch and never accessed for write.
families=copy.deepcopy(pr["families"])
updates={
 "pending-06":{"last_delta_version":"v2882","latest_photo_QA_checkpoint":"v2881: five labeled actual stock shade swatches, 3 source charts; v2882: 5 distinct source-photo scenes 1080 for internal QA only; true owned giftset and photo rights HOLD","new_story_frames":5,
    "new_shade_cards":5,
    "source_license_verified":False,"actual_stock_set_verified":False},
 "pending-08":{"last_delta_version":"v2880","latest_photo_QA_checkpoint":"v2879: all 20 exact linked real 26AD lip swatch source files; v2880: 20 shade-specific 1080 cards + four contacts; shared 4g tube; legacy INK photos quarantined","new_shade_cards":20,
    "stock_04_06_07_retained":True,"shade_14_spelling_difference_pending":True,
    "source_license_verified":False,"actual_stock_26ad_verified":False},
 "pending-04":{"last_delta_version":"v2877","latest_photo_QA_checkpoint":"21C + 23N native original mini photos from v2876; 21N alternate v2877 480px only HOLD; official shared scene v2875","unverified_shades":["21N"]},
 "pending-03":{"last_delta_version":"v2872","latest_photo_QA_checkpoint":"No21/25 U2Net v2871 and No25 ghost trim v2872; remaining hue on checker HOLD; do not run more mask loops"},
 "pending-13":{"last_delta_version":"v2865","latest_photo_QA_checkpoint":"30mL dropper red-fringe trim v2865; residual red remains HOLD; obtain new clean source only"},
 "pending-19":{"last_delta_version":"v2805","latest_photo_QA_checkpoint":"Existing Goodal Vita C Cream Alpha 50mL five real photo scenes v2805, reuse unchanged; commercial rights/25AD stock HOLD"}
}
for id,change in updates.items():
 assert id in families
 families[id].update(change)
 families[id]["release_status"]="QA_ONLY_RELEASE_BLOCKED"
 families[id]["sale_approved"]=False
for id,v in families.items():
 assert v["sale_approved"]==False,(id,v)
assert len(families)==30
state={
 "version":"v2882","baseline":"v2877","families":families,
 "num_pending_families":30,"finished_commercial_families_protected":11,
 "existing_public_URLs_protected":55,"existing_QA_JPGs_overwritten":0,
 "new_sales_approvals":0,"new_published_URLs":0,"final_spreadsheet_shared":False,
 "delta_families":list(updates),"delta_notes":updates,
 "next_work_queue":[
 {"family":"pending-12","status":"HOLD_NEED_PHYSICAL_PRODUCT_LABEL","blocker":"Owned stock 15G vs official 15mL, do not assume equivalent"},
 {"family":"pending-22","status":"TECHNICAL_QA_COMPLETE_SALES_HOLD","blocker":"OBgE 300mL low native 600px and image usage rights; do not regenerate v2857"},
 {"family":"pending-21","status":"TECHNICAL_QA_COMPLETE_SALES_HOLD","blocker":"Goodal eye cream original 25AD tube v2815 five photos; do not redo"},
 {"family":"pending-04","status":"HOLD_21N_NATIVE_PHOTO","blocker":"Two failed 480px source endpoints, no repeated fetch"},
 {"family":"pending-13","status":"HOLD_SOURCE_RED_FRINGE","blocker":"v2865 residual cap image, need clean photo not same alpha edits"},
 {"family":"pending-19","status":"PHOTO_QA_FIVE_FRAMES_READY","blocker":"v2805 source photo rights and exact 25AD user stock verification"},
 {"family":"pending-06","status":"PHOTO_QA_FIVE_FRAMES_AND_FIVE_SWATCHS_READY","blocker":"Actual 15g + refill user inventory package, rights, original MK"},
 {"family":"pending-08","status":"PHOTO_QA_TWENTY_SHADES_READY","blocker":"Photo rights and physical 26AD edition, stock shade14 typo"}],
 "source_versions":["v2877","v2880","v2881"],"created_by":"v2882_safely_new_folder_only"
}
(OUT/"stock30-incremental-state-v2882.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
manifest={"version":"v2882","baseline":"v2881","family":"pending-06",
 "source_only_photos":cards,"new_five_frame_1080_JPGs":len(cards),
 "photo_reuse_rights_confirmed":False,"owned_set_config_confirmed":False,
 "new_approved_sale_files":0,"new_published_URLs":0,
 "existing_11_families_unchanged":True,"existing_55_URLs_unchanged":True,
 "original_source_bytes_modified":0,"no_fake_swatches":True,
 "source_unique_photo_files":4,"distinct_visual_scenes":5,
 "contact":str(cp),"contact_SHA256":sha(cp),
 "full_30_family_checkpoint":str(OUT/"stock30-incremental-state-v2882.json"),
 "next":"Review these 5 scenes for actual 15g+refill pack; no commercial publication without permissions, physical unit, original MK. Continue pending12/22/21 status blockers without resynthesizing valid artwork."
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2882","new_fiveframe_JPGs":5,"new_QA_contacts":1,
                  "families_checkpointed":30,"retail_approved":0}))
