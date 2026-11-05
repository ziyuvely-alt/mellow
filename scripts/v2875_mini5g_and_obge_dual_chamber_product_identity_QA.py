#!/usr/bin/env python3
"""v2875 | Non-destructive identity QA for two unfinished stock families.

pending-04 CLIO Mesh Glow Essential Cushion MINI is 5g with *3* stock
shades (21C, 21N, 23N), not the 5-shade full-size/gift set. Previously
saved two official-store image files show the SAME held pink mini scene.
Previous v2711 segmentation has an extraneous grey hand below the case
and is REJECTED for sales. No fake independent shade product photos.

pending-11 OBgE All in One Double Essence 50mL+50mL is ONE
dual-chamber physical bottle, not a 2-bottle bundle. Use already archived
product photo only, without the prior unverifiable MK badge.

No previous files, URL55, approved11, or spreadsheet are changed.
All new pictures remain INTERNAL QA only pending product and photo rights.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from hashlib import sha256
import numpy as np,json

R=Path("qa-review")
M=R/"v2788-goodal-new-source-texture-options-clio-mini-native"
MINI_OLD=R/"v2711-real-segmentation-four-source-product-heroes"
OBGE_OLD=R/"v2780-four-unfinished-missha-obge-photo-first-QA"/"pending-11"
OUT=R/"v2875-clio-mini5g-obge-doublechamber-batch-identity-QA"
assert not OUT.exists()
sha=lambda p:sha256(p.read_bytes()).hexdigest()
mini_m=json.loads((M/"manifest.json").read_text())["clio"]
alpha_m=json.loads((MINI_OLD/"manifest.json").read_text())
obge_m=json.loads((OBGE_OLD/"manifest.json").read_text())
assert mini_m["family"]=="pending-04"
assert mini_m["verified_official_product_net_weight"]=="5g"
assert obge_m["family"]=="pending-11"
assert obge_m["blocker"]=="HOLD_DUAL_CHAMBER_VS_BUNDLE_EDITION"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=lambda n,b=False:ImageFont.truetype(B if b else F,n)
def pic(path,expected=None):
 assert path.is_file(),str(path)
 if expected: assert sha(path)==expected,(str(path),"SHA mismatch")
 with Image.open(path) as im:
  im.load()
  assert im.size==(1080,1080) and im.format=="JPEG"
  return im.convert("RGB")
imgs=[]
for rec in mini_m["distinct_native_photo_sources"]:
 path=M/rec["file"]
 imgs.append({"path":str(path),"jpg_sha256":rec["jpg_sha256"],"image":pic(path,rec["jpg_sha256"])})
# Both files are exact official source candidates, not two separate product
# shots. The comparison is measured and reported, not coerced to look distinct.
def signature(im):
 v=np.asarray(im.convert("L").resize((32,32),Image.Resampling.LANCZOS),dtype=np.float32)
 return v[8:30,5:28]
v1,v2=[signature(x["image"]) for x in imgs]
sig_diff=round(float(np.mean(np.abs(v1-v2))),4)
# Use the higher-native resolution source (600px) once, not 3 times or 5.
pick=next(x for x in imgs if "/02-official-mini-b-gif-QA.jpg" in x["path"])
assert pick["image"].size==(1080,1080)
old_alpha=next(x for x in alpha_m["candidates"] if x["family"]=="pending-04")
old_alpha_path=MINI_OLD/old_alpha["white_hero_JPG"]
old_pic=pic(old_alpha_path,old_alpha["JPG_sha256"])
obge_hero=OBGE_OLD/"01-real-product-cutout-prior-QA.jpg"
obge_pic=pic(obge_hero)
# Preserve old original in place and never treat hero product shot as user
# physically verified, only a same-catalog external photographic reference.
OUT.mkdir(parents=True)
mini=Image.new("RGB",(1080,1080),"#FBF9FC")
d=ImageDraw.Draw(mini)
d.rounded_rectangle((38,38,1042,1042),radius=24,outline="#E7DDE7",width=2)
d.text((69,70),"CLIO",font=font(54,True),fill="#493B4E")
d.text((69,145),"KILL COVER MESH GLOW ESSENTIAL",font=font(25),fill="#65556C")
d.text((69,180),"MINI CUSHION  |  5g",font=font(26,True),fill="#5C4D64")
d.line((68,231,1012,231),fill="#D6C6D7",width=3)
base=ImageOps.contain(pick["image"],(650,620),Image.Resampling.LANCZOS)
mini.paste(base,((1080-base.width)//2,246+(620-base.height)//2))
d.rounded_rectangle((68,858,1012,956),radius=15,fill="#F0EBF1")
d.text((89,870),"ONLY THREE STOCK OPTIONS",font=font(22,True),fill="#524759")
d.text((89,911),"21C LINGERIE   /   21N LINEN   /   23N GINGER",font=font(20,True),fill="#5E5266")
d.text((70,987),"SHARED MINI PHOTO   |   INTERNAL QA   |   NOT FOR SALE",font=font(17,True),fill="#807287")
mp=OUT/"CLIO-mini5g-three-stock-shades-single-official-scene-QA.jpg"
mini.save(mp,"JPEG",quality=94,optimize=True,subsampling=0)
# OBgE: do not imply 2 products from 50+50ml; show a single physically
# photographed bottle. The original archived hero remains byte-identical.
ob=Image.new("RGB",(1080,1080),"#FAF9F6")
d=ImageDraw.Draw(ob)
d.rounded_rectangle((36,36,1044,1044),radius=25,outline="#DDD5C8",width=2)
d.text((73,70),"OBgE",font=font(52,True),fill="#3C342F")
d.text((73,150),"ALL IN ONE DOUBLE ESSENCE",font=font(26,True),fill="#5F534B")
d.line((73,207,1007,207),fill="#D6CBC3",width=3)
b=ImageOps.contain(obge_pic,(640,642),Image.Resampling.LANCZOS)
ob.paste(b,((1080-b.width)//2,215+(642-b.height)//2))
d.rounded_rectangle((73,857,1007,964),radius=18,fill="#ECE7E0")
d.text((91,869),"50mL + 50mL",font=font(31,True),fill="#51483E")
d.text((91,915),"ONE DUAL-CHAMBER BOTTLE / NOT A TWO-BOTTLE SET",font=font(18,True),fill="#635549")
d.text((74,992),"ACTUAL STOCK EDITION & PHOTO RIGHTS NOT VERIFIED",font=font(17),fill="#81766F")
op=OUT/"OBgE-double-essence-single-dual-chamber-50+50-QA.jpg"
ob.save(op,"JPEG",quality=94,optimize=True,subsampling=0)
# Source similarity / rejected original alpha proof, checker. This is
# a review-only contact, NOT additional independent sales scene.
board=Image.new("RGB",(1600,630),"#F2EDF1")
d=ImageDraw.Draw(board)
d.text((16,14),"v2875 CLIO MINI | SOURCE M/B VISUALLY DUPLICATE; OLD U2NET GHOST REJECT",font=font(24,True),fill="#463A49")
for i,im in enumerate([imgs[0]["image"],imgs[1]["image"],old_pic]):
 im=im.resize((505,505),Image.Resampling.LANCZOS)
 board.paste(im,(17+i*530,58))
d.text((22,580),f"Shared-scene low-res mean abs diff: {sig_diff} / 255; not distinct shade photos",font=font(17),fill="#66556A")
proof=OUT/"v2875-clio-mini-source-duplicate-and-bad-alpha-hold.jpg"
board.save(proof,"JPEG",quality=89,optimize=True)
for file in [mp,op]:
 with Image.open(file) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080)
 assert file.stat().st_size<2_000_000
# No source original modified or prior accepted product photos touched.
assert sha(Path(pick["path"]))==pick["jpg_sha256"]
assert sha(old_alpha_path)==old_alpha["JPG_sha256"]
report={
 "version":"v2875","baseline":"v2874",
 "execution":"Create two new evidence-based product-identity 1080 QA frames and one duplicate/rejected-mask proof; reconcile high-risk release blocks",
 "families":{
   "pending-04":{"product":"CLIO Kill Cover Mesh Glow Essential Cushion MINI 5g",
      "source_merchant":"CLIO brand official product page",
      "brand_official_page":"https://clubclio.co.kr/shop/goodsView/0000006954",
      "mini_in_stock_shades":["21C LINGERIE","21N LINEN","23N GINGER"],
      "full_size_five_shades_not_substituted":True,
      "reference_mini_photo_same_for_all_shades":True,
      "official_photo_files": [x["path"] for x in imgs],
      "perceptual_central_grayscale_diff":sig_diff,
      "per_option_original_photo_distinctness":"NOT PROVEN",
      "old_v2711_alpha_candidate_status":"REJECT_VISUAL_GREY_HAND_GHOST_AND_HALO",
      "old_v2711_alpha_candidate_path":str(old_alpha_path),
      "new_identity_QA":str(mp),"new_identity_sha256":sha(mp),
      "photo_reuse_rights_verified":False,"stock_edition_verified":False,
      "sales_approved":False},
   "pending-11":{"product":"OBgE All In One Double Essence 50mL+50mL",
      "stock_quantity_unit":"ONE 50mL+50mL DUAL-CHAMBER BOTTLE, NOT TWO BOTTLES",
      "source_hero":str(obge_hero),"source_hero_gitblob_shas":obge_m["frames"][0]["source_blob_sha1"],
      "new_identity_QA":str(op),"new_identity_sha256":sha(op),
      "legacy_frames_02_to_05_contain_unverified_MK_logo":True,
      "legacy_frames_02_to_05_status":"HOLD_NO_SALES_UNTIL_VERIFIED_MK",
      "physical_owned_packaging_verified":False,
      "photo_reuse_rights_verified":False,"sales_approved":False},
   "pending-12":{"product":"MISSHA PDRN NAD+ Renew Peel Shot 25",
      "stock_sheet_recorded_unit":"15G",
      "brand_owned_product_listing_unit":"15mL",
      "units_must_not_be_automatically_converted":True,
      "status":"HOLD_NEED_PHOTO_OF_ACTUAL_OWNED_UNIT_LABEL",
      "evidence":"evidence/v2783-missha-pdrn-peelshot25-official-15ml-source-vs-stock-15g-conflict-20261105.json",
      "existing_inventory_edit_performed":False,"sales_approved":False}
 },
 "new_1080_JPG_QA_count":2,"new_qa_comparison_count":1,
 "comparison":str(proof),"comparison_sha256":sha(proof),
 "old_11_published_approved_groups_preserved":True,
 "old_55_verified_public_URLs_preserved":True,
 "older_QA_assets_overwritten":0,
 "stock_sheet_edited":False,"final_excel_shared":False,
 "new_public_URLs":0,"new_retail_approvals":0,
 "next":"For pending-04 source independent exact 21C/21N/23N MINI shade photographs or verify packaging before seller upload; do not reuse three copies of same image as shade evidence. For pending-11 validate exact 50+50 owned bottle and original MK mark. For pending-12 verify 15mL/15g on physical stock; no assumed unit conversion."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2875","qa_new_1080":2,"qa_proof":1,"mini_source_diff":sig_diff,"new_sales_approved":0}))
