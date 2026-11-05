#!/usr/bin/env python3
"""v2869 | Different-old-package photos for MISSHA M Perfect Cover BB 50ml.
v2702 newly redesigned red+white bottom packaging is NOT interchangeable
with existing gold-pump stock. Use true legacy gold pump source-photo
references for 21 and 25 ONLY; preserve already saved 23 source unmodified.
All web merchant photos are internal QA, no commercial usage license inferred.
"""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json

R=Path("qa-review")
OUT=R/"v2869-missha-legacy-gold-pump-21-23-25-exact-shade-photo-QA"
assert not OUT.exists()
REFERENCE=R/"v2780-four-unfinished-missha-obge-photo-first-QA/pending-03/01-real-product-cutout-prior-QA.jpg"
assert REFERENCE.is_file()
BASELINE=json.loads((R/"v2702-missha-M-perfect-cover-BB-official-photo-proof/manifest.json").read_text())
assert BASELINE["family"]=="pending-03"
assert "new" in BASELINE["page"]
sha=lambda p:sha256(p.read_bytes()).hexdigest()
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
# Source order: reused real old photo is stronger than any new-version US
# launch reference. No packages or color chips are fabricated.
SOURCES=[
 {"shade":"21","name":"LIGHT BEIGE","sources":[
  {"url":"https://c.scdn.gr/images/sku_main_images/055479/55479016/20240814151409_missha_m_perfect_cover_bb_21_light_beige_enydatiki_antigirantiki_krema_prosopou_imeras_me_spf42_me_yalouroniko_oxy_kollagono_50ml.jpeg",
   "merchant":"Skroutz Greece","expected":"No.21 50ml legacy gold-pump red dotted product"},
  {"url":"https://i.ebayimg.com/images/g/GZMAAeSwk7xpaV0f/s-l1200.webp",
   "merchant":"eBay UK","expected":"No.21 50ml legacy gold-pump red dotted product and box"}]},
 {"shade":"25","name":"WARM BEIGE","sources":[
  {"url":"https://www.bigw.com.au/medias/sys_master/images/images/h8b/h85/152631783784478.jpg",
   "merchant":"Big W Australia","expected":"No.25 50ml legacy gold-pump red dotted product"},
  {"url":"https://i.ebayimg.com/images/g/8KkAAOSwT4RjH95v/s-l1200.jpg",
   "merchant":"eBay fallback candidate unverified","expected":"No.25 if exact shade and gold pump after visual check"}]}
]
OUT.mkdir(parents=True)
records=[]
frames=[]
for item in SOURCES:
 shade=item["shade"]
 attempts=[]
 row={"shade":shade,"shade_name":item["name"],
      "target_edition":"legacy 50ml red dotted pack with gold pump, NOT 2026 US redesigned beige-bottom squeeze tube",
      "candidate_sources":item["sources"],"download_attempts":attempts,
      "status":"HOLD_SOURCE_NOT_VERIFIED","manual_shade_label_check_required":True,
      "physical_owned_stock_same_edition_verified":False,
      "merchant_redistribution_rights_verified":False,
      "sales_approved":False}
 for candidate in item["sources"]:
  try:
   with urlopen(Request(candidate["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/jpeg,image/webp,*/*"}),timeout=16) as stream:
    raw=stream.read(7_000_001)
   assert 8000<len(raw)<=7_000_000
   with Image.open(BytesIO(raw)) as orig:
    orig.load()
    assert orig.format in ("JPEG","PNG","WEBP") and min(orig.size)>=400
    photo=orig.convert("RGB")
    rawfmt=orig.format
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[rawfmt]
   rawpath=OUT/f"MISSHA-OLD-50ml-No{shade}-source-unaltered.{ext}"
   rawpath.write_bytes(raw)
   canvas=Image.new("RGB",(1080,1080),"#FCFAFA")
   d=ImageDraw.Draw(canvas)
   d.rounded_rectangle((39,39,1041,1041),radius=23,outline="#E3D6D8",width=2)
   d.text((74,65),"MISSHA M PERFECT COVER BB",font=ft(31,True),fill="#543B42")
   d.text((74,122),f'No.{shade}  {item["name"]}  |  50mL',font=ft(28,True),fill="#815760")
   d.line((74,187,1006,187),fill="#E0CCD0",width=3)
   fitted=ImageOps.contain(photo,(922,738),Image.Resampling.LANCZOS)
   canvas.paste(fitted,((1080-fitted.width)//2,204+(738-fitted.height)//2))
   d.line((74,955,1006,955),fill="#E0CCD0",width=2)
   d.text((74,966),"REAL GOLD-PUMP PHOTO SOURCE  |  QA ONLY",font=ft(18,True),fill="#79616A")
   d.text((74,997),"SOURCE LICENSE AND OWNED STOCK EDITION UNVERIFIED",font=ft(15),fill="#95828A")
   jpg=OUT/f"MISSHA-OLD-50ml-No{shade}-real-merchant-source-card-QA.jpg"
   canvas.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
   with Image.open(jpg) as ck:assert ck.format=="JPEG" and ck.size==(1080,1080)
   assert jpg.stat().st_size<2_000_000
   row.update(status="SOURCE_SAVED_INTERNAL_QA_SHADE_AND_EDITION_VISUAL_HOLD",
     used_url=candidate["url"],source_merchant=candidate["merchant"],source_expected=candidate["expected"],
     source_native_px=list(photo.size),source_bytes=len(raw),source_format=rawfmt,
     source_original=str(rawpath),source_sha256=sha(rawpath),
     output_card=str(jpg),output_sha256=sha(jpg),jpg_bytes=jpg.stat().st_size,
     source_rgb_color_recolored=False)
   frames.append((shade,canvas.copy()))
   attempts.append({"merchant":candidate["merchant"],"result":"DOWNLOADED_UNALTERED_REFERENCE"})
   break
  except Exception as exc:
   attempts.append({"merchant":candidate["merchant"],"result":"HOLD_FETCH_FAILED",
                    "reason":type(exc).__name__+": "+str(exc)[:180]})
 records.append(row)
# Existing old gold-pump #23 exact-photo QA is never overwritten or relabeled.
assert REFERENCE.is_file()
with Image.open(REFERENCE) as old:
 old.load()
 assert old.format=="JPEG" and old.size==(1080,1080)
 old23=old.convert("RGB")
contact=Image.new("RGB",(1575,615),"#EEE9EB")
d=ImageDraw.Draw(contact)
d.text((19,11),"v2869 | LEGACY GOLD-PUMP 50mL NO21 / NO23 / NO25 | SOURCE QA ONLY",font=ft(24,True),fill="#433840")
for i,shade in enumerate(("21","23","25")):
 if shade=="23":picture=old23
 else:
  match=[photo for s,photo in frames if s==shade]
  picture=match[0] if match else Image.new("RGB",(1080,1080),"#E4DEDF")
 thumb=picture.resize((505,505),Image.Resampling.LANCZOS)
 contact.paste(thumb,(15+520*i,59))
 d.text((21+520*i,571),"No."+shade+(" / SAVED" if shade=="23" else " / NEW QA OR HOLD"),font=ft(18,True),fill="#5B4E55")
cpath=OUT/"v2869-old-missha-21-23-25-gold-pump-photo-contact-QA.jpg"
contact.save(cpath,"JPEG",quality=87,optimize=True)
m={
 "version":"v2869","baseline":"v2868","family":"pending-03",
 "work":"Original legacy gold pump photos for previously incomplete 21/25 shades and existing unchanged 23",
 "old_23_existing_original":str(REFERENCE),"old_23_sha256":sha(REFERENCE),
 "attempted_new_shades":["21","25"],"downloaded_new_original_shade_photos":sum(x["status"].startswith("SOURCE_SAVED") for x in records),
 "new_1080_QA_card_count":sum("output_card" in x for x in records),
 "blocked_or_failed":sum("output_card" not in x for x in records),
 "new_version_US_photo_prohibited_as_old_version_substitute":True,
 "brand_same_generation_not_yet_confirmed_for_physical_stock":True,
 "new_source_use_rights_verified":False,"source_photos_recolored":False,
 "original_v2780_and_v2702_asset_bytes_preserved":True,
 "previous_11_approved_families_untouched":True,"previous_55_verified_public_URLs_untouched":True,
 "new_retail_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False,
 "new_shade_source_rows":records,"contact":str(cpath),"contact_sha256":sha(cpath),
 "next":"Check actual No21/No25 printed number + gold-pump 50mL old exact packaging visually. Keep all as internal QA until source rights and owned physical stock confirmed; do not use new beige-bottom US redesign for these old pump photos."
}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2869","new_old_version_shade_photo_sources":m["downloaded_new_original_shade_photos"],
 "failed":m["blocked_or_failed"],"existing23_reused":True,"retail_approved":0},ensure_ascii=False))
