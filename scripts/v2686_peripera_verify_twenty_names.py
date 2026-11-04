#!/usr/bin/env python3
"""v2686: reconcile PERIPERA 001..020 to brand first-party Kakao announcement
and Olive Young exclusive-option listing. Correct previous v2685 false missing.
Create exactly one shade-name INDEX JPG, no fabricated color swatches.
Preserve old five historical JPGs as refs and never promote retail.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,base64
OUT=Path("qa-review/v2686-peripera-20-verified-name-index")
assert not OUT.exists()
OUT.mkdir(parents=True)
names=[
"딸기기니","쩡신차렷","말랑물복","저쩔복숭아","갓기요정",
"갓기천사","자두뿜뿜","핑토당토","맘찍로즈","내입술인척",
"비주얼센터","개강여신","분위기여신","로지위시","맘콕로즈",
"로즈콕","이로지무화과?","손웜수템","어쩔체리","당맛도리"]
assert len(names)==20 and len(set(names))==20
exclusive={4,6,7}
items=[{"no":f"{k:02d}","ko":name,"brand_official_verified":True,
        "olive_young_exclusive":k in exclusive,
        "photo_swatch_verified":False,
        "owned_stock_edition_verified":False} for k,name in enumerate(names,1)]
fontpaths=[
"/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
fontpath=next(x for x in fontpaths if Path(x).exists())
def font(n):return ImageFont.truetype(fontpath,n)
im=Image.new("RGB",(1080,1080),"#fffdfc")
d=ImageDraw.Draw(im)
d.rectangle((0,0,1080,20),fill="#e8c2cb")
d.text((60,50),"PERIPERA  |  MOOD GLOWY TINT",fill="#402933",font=font(40))
d.text((60,115),"20 OFFICIAL SHADE NAMES",fill="#46353c",font=font(32))
d.text((60,172),"01-20 / NAME INDEX / NO COLOR SWATCHES",fill="#796c72",font=font(24))
for i,item in enumerate(items):
 col=i//10; row=i%10
 x=52+col*506; y=235+row*74
 fill="#fbf0f2" if row%2==0 else "#ffffff"
 d.rounded_rectangle((x,y,x+485,y+68),radius=13,fill=fill)
 d.text((x+14,y+13),item["no"],fill="#693446",font=font(30))
 d.text((x+79,y+16),item["ko"],fill="#2f292c",font=font(27))
 if item["olive_young_exclusive"]:
  d.ellipse((x+451,y+24,x+468,y+41),fill="#cb647f")
d.ellipse((59,1011,76,1028),fill="#cb647f")
d.text((86,1003),"Olive Young exclusive: 04 / 06 / 07",fill="#6c5e63",font=font(22))
d.text((60,967),"REFERENCE ONLY / SHADE PHOTO AND STOCK EDITION NOT VERIFIED",fill="#77656c",font=font(18))
imagefile=OUT/"v2686-20-shade-names-no-swatches-QA.jpg"
im.save(imagefile,quality=91,optimize=True,subsampling=0)
assert imagefile.stat().st_size<2_000_000
with Image.open(imagefile) as valid:assert valid.format=="JPEG" and valid.size==(1080,1080)
(OUT/"v2686-name-index.b64.txt").write_text(base64.b64encode(imagefile.read_bytes()).decode())
evidence={
"version":"v2686","family":"pending-08","original_prior_claim_corrected":True,
"prior_v2685_error":"Treating missing from GS SHOP selector as absent from 26AD product range",
"correction":"04 저쩔복숭아, 06 갓기천사, 07 자두뿜뿜 are legitimate Olive Young-exclusive shades, not removed options",
"first_party_brand_channel":"https://pf.kakao.com/_SZjzG",
"retailer_exclusive_verification":"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000244834",
"first_party_01_20_names":items,
"count_source_verified_names":20,
"exclusive_source_verified_numbers":[4,6,7],
"complete_reference_name_index_JPG":imagefile.name,
"visual_color_swatches_approved":0,
"exact_user_owned_stock_edition_proven":False,
"actual_retailable_jpgs_approved":0,
"prior_v2685_historical_5_photos_preserved":True,
"prior_29_fiveframe_QA_drafts_unmodified":True,
"existing_11_published_families_unmodified":True,
"existing_55_urls_untouched":True,
"final_xlsx_not_shared":True,
"next":"Replace mistaken shade 04/06/07 exclude rule in future QC; require exact photo proof before generating swatches or 5-frame final image."}
(OUT/"v2686-evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"verified_names":20,"confirmed_olive_young_exclusive":[4,6,7],
"new_JPG_reference":1,"real_sale_ready":0},ensure_ascii=False))
