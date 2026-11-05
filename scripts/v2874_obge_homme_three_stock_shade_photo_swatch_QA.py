#!/usr/bin/env python3
"""v2874 OBgE Perfect Homme Cushion 15g, three actual-stock option references.
Reuse SHA256-locked v2511 CORRECT dark-brown rectangular product source photo
and original 3-shade chart. Never use the quarantined WRONG beige round case.
Source chart is physically photographed, NOT generated swatches; preserve
unaltered entire chart and only zoom a real shade row. User-owned 15g
physical packaging still needs inspection; no retail image rights yet.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
R=Path("qa-review")
EXT=Path("/tmp/v2874_obge_correct")
OUT=R/"v2874-obge-homme-15g-three-correct-shade-photo-qa"
assert EXT.is_dir() and not OUT.exists()
sha=lambda p:sha256(p.read_bytes()).hexdigest()
m=json.loads((EXT/"manifest.json").read_text())
assert m["family"]=="pending-10" and m["target"]=="OBgE Perfect Homme Cushion 15g"
assert m["old_5_jpgs"]=="QUARANTINE WRONG_BEIGE_ROUND_PERFECT_COVER_CUSHION"
original={x["filename"]:x for x in m["new_jpgs"]}
prod=EXT/"01-original-open-compact.jpg"
swatch=EXT/"04-original-3shade-chart.jpg"
assert prod.is_file() and swatch.is_file()
assert sha(prod)==original[prod.name]["sha256"]
assert sha(swatch)==original[swatch.name]["sha256"]
with Image.open(prod) as im:
 im.load(); assert im.format=="JPEG" and im.size==(1080,1080)
 p=im.convert("RGB")
with Image.open(swatch) as im:
 im.load(); assert im.format=="JPEG" and im.size==(1080,1080)
 s=im.convert("RGB")
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
SHADES=[
 ("1","IVORY",(261,210,822,440)),
 ("2","BEIGE",(261,446,822,661)),
 ("3","SAND",(261,660,822,900))]
OUT.mkdir(parents=True)
cards=[]
for number,name,crop in SHADES:
 img=Image.new("RGB",(1080,1080),"#F9F8F6")
 d=ImageDraw.Draw(img)
 d.rounded_rectangle((35,36,1045,1044),radius=24,outline="#E3DAD2",width=2)
 d.text((68,66),"OBgE  |  PERFECT HOMME CUSHION",font=ft(35,True),fill="#453B34")
 d.text((69,118),"CORRECT DARK RECTANGULAR 15g REFERENCE",font=ft(19),fill="#72675D")
 d.rounded_rectangle((798,139,1010,206),radius=14,fill="#EDE1D5")
 d.text((812,153),"#"+number+"  "+name,font=ft(23,True),fill="#554438")
 d.line((69,222,1012,222),fill="#DACBBF",width=3)
 product_panel=ImageOps.contain(p,(473,480),Image.Resampling.LANCZOS)
 img.paste(product_panel,(65+(473-product_panel.width)//2,240+(480-product_panel.height)//2))
 chart_panel=ImageOps.contain(s,(464,470),Image.Resampling.LANCZOS)
 img.paste(chart_panel,(548+(464-chart_panel.width)//2,244+(470-chart_panel.height)//2))
 d.text((69,717),"CORRECT 15g CASE PHOTO",font=ft(18,True),fill="#64564C")
 d.text((558,717),"ORIGINAL THREE-SHADE SOURCE",font=ft(17,True),fill="#64564C")
 focus=s.crop(crop)
 # Isolated region is only an unaltered photo crop for internal identity;
 # full original chart remains visible next to actual product case above.
 zoom=ImageOps.contain(focus,(855,126),Image.Resampling.LANCZOS)
 d.rounded_rectangle((74,770,1006,932),radius=17,fill="#FFFFFF",outline="#E2D7CD",width=2)
 img.paste(zoom,(100+(855-zoom.width)//2,784+(126-zoom.height)//2))
 d.text((78,955),"INTERNAL QA ONLY  |  REAL SOURCE SHADES, NO RECOLORING",font=ft(18,True),fill="#61554B")
 d.text((78,991),"Confirm exact owned set + licensed artwork before publishing.",font=ft(16),fill="#887A6E")
 card=OUT/f"OBgE-PerfectHomme-15g-No{number}-{name}-1080-option-QA.jpg"
 img.save(card,"JPEG",quality=94,subsampling=0,optimize=True)
 with Image.open(card) as check:
  check.load(); assert check.format=="JPEG" and check.size==(1080,1080)
 assert card.stat().st_size<2_000_000
 cards.append({"shade":number,"shade_label":name,"input_case_sha256":sha(prod),
               "input_shade_chart_sha256":sha(swatch),"original_chart_crop":list(crop),
               "new_option_card":str(card),"new_sha256":sha(card),"jpg_bytes":card.stat().st_size,
               "real_shade_RGB_recolored":False,"original_wrong_round_pack_reused":False,
               "photo_rights_granted":False,"physical_owned_unit_label_verified":False,
               "retail_approved":False})
assert len({c["new_sha256"] for c in cards})==3
contact=Image.new("RGB",(1580,600),"#F0ECE8")
d=ImageDraw.Draw(contact)
d.text((14,12),"v2874 OBgE PERFECT HOMME REAL 15g DARK-SQUARE / THREE VERIFIED PHOTO-REFERENCE SHADES | QA",font=ft(20,True),fill="#52433B")
for i,r in enumerate(cards):
 with Image.open(r["new_option_card"]) as im:
  frame=im.convert("RGB").resize((510,510),Image.Resampling.LANCZOS)
 contact.paste(frame,(15+i*525,55))
cp=OUT/"v2874-obge-homme-three-shade-original-source-comparison-QA.jpg"
contact.save(cp,"JPEG",quality=88,optimize=True)
assert sha(prod)==original[prod.name]["sha256"] and sha(swatch)==original[swatch.name]["sha256"]
manifest={
 "version":"v2874","baseline":"v2873","family":"pending-10",
 "product":"OBgE Perfect Homme Cushion 15g No1/2/3",
 "source_branch":"production-assets-v2511-obge-homme-15g-corrected",
 "legacy_incorrect_beige_round_case":"QUARANTINED_DO_NOT_USE",
 "three_shade_original_case_chart_reused":True,
 "new_1080_QA_option_JPGs":3,"input_original_JPGs_reencoded_or_overwritten":0,
 "new_swatch_photo_downloads":0,"new_fake_swatch_colors":0,
 "physical_inventory_15g_vs_prior_13g_conflict":"HOLD_ACTUAL_UNIT_LABEL",
 "verified_from_archived_merchant_sources":"15g square case, SPF50+ PA+++, No1 Ivory No2 Beige No3 Sand",
 "retail_photo_rights_verified":False,
 "authentic_original_MK_logo_verified":False,
 "sale_approvals":0,"new_public_URLs":0,
 "prior_11_approved_groups_preserved":True,
 "prior_55_public_urls_preserved":True,"final_spreadsheet_shared":False,
 "cards":cards,"contact":str(cp),"contact_sha256":sha(cp),
 "next":"Verify user's actual OBgE 15g physical box label and merchant photo rights. New three options are INTERNAL review only. Never reuse old wrong beige round-case photos or substitute generic shade colors."
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2874","new_JPGs":3,"source_bytes_unchanged":True,"sale_approved":0}))
