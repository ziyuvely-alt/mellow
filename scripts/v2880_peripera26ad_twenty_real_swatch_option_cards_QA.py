#!/usr/bin/env python3
"""v2880 Create 20 non-destructive high-resolution QA option proof cards from
v2879 SHA-verified Shopify variant-associated REAL 26AD lip swatch photographs
and one common 4g new-tube photograph.

Every image separately matches an exact shade number and expected shade
name, stock 01..20 ONLY. Never call shared tube shade-specific, recolor
swatches, invent variants, reuse old 'INK Mood Glowy Tint', publish commercial
assets without rights or rewrite any previous source.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
R=Path("qa-review")
SRC=R/"v2879-peripera26ad-direct-CDN-and-shopify-variant-QA"
OLD=R/"v2853-peripera-26AD-vs-legacy-20-option-block"/"manifest.json"
OUT=R/"v2880-peripera-26AD-twenty-original-lipswatch-plus-common-tube-QA"
assert SRC.is_dir() and not OUT.exists() and OLD.exists()
m=json.loads((SRC/"manifest.json").read_text())
prev=json.loads(OLD.read_text())
assert m["version"]=="v2879" and m["confirmed_variant_associated_photo_candidates"]==20
assert m["direct_CDN_sources_saved"]==2 and len(prev["rows"])==20
shade_old={r["shade"]:r for r in prev["rows"]}
all_sha=lambda p:sha256(p.read_bytes()).hexdigest()
variant_rows={x["shade"]:x for x in m["shopify"]["per_shade_photo_candidates"]}
assert set(variant_rows)=={f"{i:02d}" for i in range(1,21)}
common=next(x for x in m["cdn_assets"] if x["role"]=="common-real-new-tube-with-applicator")
C=Path(common["original_file"]);assert C.is_file() and all_sha(C)==common["raw_sha256"]
with Image.open(C) as im:
 im.load();assert im.size[0]>=700 and im.size[1]>=700
 common_img=im.convert("RGB")
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
OUT.mkdir(parents=True)
rows=[];thumbs=[]
for shade in sorted(variant_rows):
 v=variant_rows[shade];old=shade_old[shade]
 assert v["status"]=="CANDIDATE_VARIANT_LINKED_PHOTO_QA_HOLD"
 assert v["shade"]==shade and v["exact_assigned_variant"]
 assert v["source_sha256"] and v["qa_sha256"]
 raw=Path(v["source_photo"]);assert raw.exists() and all_sha(raw)==v["source_sha256"]
 with Image.open(raw) as swatch:
  swatch.load();assert min(swatch.size)>=700
  true_swatch=swatch.convert("RGB")
 en=next(r["expected_26AD_EN"] for r in m["stock_20_shades"] if r["shade"]==shade)
 ko=old["verified_clio_operated_retail_name"] or old["stock_name"]
 name_note=""
 if shade=="14":
  assert ko=="로지위시" and old["stock_name"]=="로지워시"
  name_note=" | ORIGINAL STOCK: 로지워시 [CHECK]"
 # Actual Korean text may not render with DejaVu fonts: rely on EN
 # and preserve Korean name only in JSON, not guessed/unrenderable glyphs.
 canvas=Image.new("RGB",(1080,1080),"#FAF9FB")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((36,37,1044,1044),radius=26,outline="#E2D9E6",width=2)
 d.text((69,62),"peripera",font=ft(52,True),fill="#483A4D")
 d.text((72,125),"MOOD GLOWY TINT  |  NEW 26AD  |  4g",font=ft(21,True),fill="#65566C")
 d.rounded_rectangle((72,180,1008,258),radius=18,fill="#F0E8F1")
 d.text((95,192),f"NO. {shade}",font=ft(37,True),fill="#493B51")
 d.text((320,209),en.upper(),font=ft(23,True),fill="#5F4F64")
 d.line((72,281,1008,281),fill="#D7CEDC",width=3)
 d.rounded_rectangle((63,314,514,842),radius=16,fill="white",outline="#E9E2EA",width=2)
 d.rounded_rectangle((537,314,1019,842),radius=16,fill="white",outline="#E9E2EA",width=2)
 tube=ImageOps.contain(common_img,(430,437),Image.Resampling.LANCZOS)
 canvas.paste(tube,(73+(430-tube.width)//2,350+(437-tube.height)//2))
 lip=ImageOps.contain(true_swatch,(463,437),Image.Resampling.LANCZOS)
 canvas.paste(lip,(546+(463-lip.width)//2,350+(437-lip.height)//2))
 d.text((77,795),"COMMON 4g TUBE PHOTO",font=ft(16,True),fill="#6E6172")
 d.text((556,795),"EXACT VARIANT LIP SWATCH",font=ft(16,True),fill="#6E6172")
 d.line((75,868,1006,868),fill="#DFD5E1",width=2)
 d.text((76,890),"EXACT SHOPIFY SHADE LINK + UNALTERED RGB",font=ft(21,True),fill="#55495C")
 d.text((76,936),"QA ONLY  |  stock edition and photo rights unverified",font=ft(17),fill="#776A7A")
 d.text((76,969),"No legacy INK photos. No synthetic color. No seller upload.",font=ft(17),fill="#776A7A")
 p=OUT/f"peripera-26AD-No{shade}-true-lipswatch-plus-4g-QA.jpg"
 canvas.save(p,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(p) as test:
  test.load();assert test.format=="JPEG" and test.size==(1080,1080)
 assert p.stat().st_size<2_000_000
 assert all_sha(raw)==v["source_sha256"] and all_sha(C)==common["raw_sha256"]
 row={"shade":shade,"name_EN":en,"brand_shade_name_KO":ko,
      "raw_stock_name_KO":old["stock_name"],"explicit_stock_name_mismatch":shade=="14",
      "oliveyoung_only":shade in {"04","06","07"},
      "source_photo":str(raw),"source_SHA256":v["source_sha256"],
      "source_variant_id":next((a["variant_id"] for a in m["shopify"]["detected_variants"] if a["shade"]==shade),None),
      "new_card_1080":str(p),"card_SHA256":all_sha(p),"bytes":p.stat().st_size,
      "shared_tube_not_shade_specific":True,
      "lip_swatch_from_own_exact_variant":True,
      "source_rgb_recolored":False,"photo_usage_license_granted":False,
      "retail_approved":False,"status":"TRUE_SHADE_SWATCH_PRODUCT_COMPARISON_QA_HOLD_RIGHTS"}
 rows.append(row);thumbs.append((shade,canvas))
assert len(rows)==20 and len(set(x["source_SHA256"] for x in rows))==20
assert len(set(x["card_SHA256"] for x in rows))==20
boards=[]
for offset in range(0,20,5):
 group=thumbs[offset:offset+5]
 board=Image.new("RGB",(2080,1500),"#F0ECF1")
 d=ImageDraw.Draw(board)
 d.text((24,14),f"v2880 PERIPERA 26AD real lip swatches | SHADES {group[0][0]}..{group[-1][0]} | QA ONLY",
        font=ft(29,True),fill="#4B3E4C")
 # 5 cards in 3x2 contact
 for i,(shade,im) in enumerate(group):
  thumb=im.resize((635,635),Image.Resampling.LANCZOS)
  x=20+(i%3)*685;y=65+(i//3)*700
  board.paste(thumb,(x,y))
  d.text((x+6,y+644),"NO."+shade+" / REAL VARIANT LIP PHOTO",font=ft(17,True),fill="#5D4C60")
 bp=OUT/f"v2880-contact-shades-{offset+1:02d}-to-{offset+5:02d}-QA.jpg"
 board.save(bp,"JPEG",quality=90,optimize=True)
 boards.append({"shades":[x[0] for x in group],"contact_path":str(bp),"SHA256":all_sha(bp)})
report={"version":"v2880","baseline":"v2879","family":"pending-08",
 "product":"peripera Mood Glowy Tint 26AD 4g 01..20 options",
 "new_photo_shade_option_QA_JPG_count":20,
 "new_true_26AD_source_RGB_photos_downloaded":0,
 "original_v2879_20_shade_lip_photos_reused":True,
 "original_v2879_new_tube_photo_reused":True,
 "unmodified_distinct_raw_shade_sha256":20,
 "option_cards_sha_unique":True,
 "actual_common_new_tube_photo_not_misrepresented_as_distinct_variant":True,
 "oliveyoung_04_06_07_retained":True,
 "stock_014_original_unchanged":True,
 "photo_rights_all_20_verified":False,"actual_owned_26AD_edition_verified":False,
 "previous_11_sales_approved_families_unchanged":True,
 "previous_55_public_urls_unchanged":True,
 "originals_and_legacy_QA_files_overwritten":0,
 "new_sales_approved":0,"new_public_urls":0,"spreadsheet_shared":False,
 "rows":rows,"four_visual_contact_sheets":boards,
 "next":"Human QA native swatches 01..20 vs exact retailer shade link. Obtain owner-stock physical edition and commercial photo rights before release; do not repeat old INK photos. Then resolve CLIO pending06 genuine five swatch rows and pending12 physical unit."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2880","new_option_JPGs":len(rows),"new_contact_sheets":len(boards),
                  "raw_SHA_unique":len(set(x["source_SHA256"] for x in rows)),"retail_approved":0}))
