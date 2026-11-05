#!/usr/bin/env python3
"""v2870: recover missing legacy MISSHA M Perfect Cover BB 50mL #25 using
new CDN merchant source after v2869 BigW timeout + invalid fallback.
Do not retry old sources, manufacture 25 by recoloring #23, or use the
new 2026 US beige-bottom version. Reuse 21 and 23 byte-identically.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from hashlib import sha256
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
R=Path("qa-review")
BASE=R/"v2869-missha-legacy-gold-pump-21-23-25-exact-shade-photo-QA"
OUT=R/"v2870-missha-old-bb-25-new-cdn-source-and-three-shade-contact-QA"
assert BASE.is_dir() and not OUT.exists()
prior=json.loads((BASE/"manifest.json").read_text())
assert prior["version"]=="v2869" and prior["downloaded_new_original_shade_photos"]==1
shade21=next(r for r in prior["new_shade_source_rows"] if r["shade"]=="21")
shade25=next(r for r in prior["new_shade_source_rows"] if r["shade"]=="25")
assert shade21["status"].startswith("SOURCE_SAVED")
assert shade25["status"]=="HOLD_SOURCE_NOT_VERIFIED"
old23=Path(prior["old_23_existing_original"])
p21=Path(shade21["output_card"])
assert p21.is_file() and old23.is_file()
sha=lambda p:sha256(p.read_bytes()).hexdigest()
assert sha(p21)==shade21["output_sha256"] and sha(old23)==prior["old_23_sha256"]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
url="https://cdn.shopify.com/s/files/1/0850/0389/5090/files/missha-bb-cream-25-main_26ca2414-ad28-426b-a243-b51dd2312939.jpg?format=webp&v=1791791301&width=3840"
page="https://k-gallery.com/shop/products/missha-m-perfect-cover-bb-cream"
OUT.mkdir(parents=True)
record={"shade":"25","shade_name":"WARM BEIGE","source_url":url,"merchant_page":page,
 "source_type":"old gold-pump genuine retailer-photo candidate","status":"PENDING",
 "retail_approved":False,"photo_rights_verified":False,
 "physical_user_owned_packaging_verified":False}
try:
 with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/webp,image/jpeg,image/png,*/*"}),timeout=20) as r:raw=r.read(6_000_001)
 assert 12_000<len(raw)<=6_000_000
 with Image.open(BytesIO(raw)) as o:
  o.load()
  assert o.format in ("JPEG","WEBP","PNG") and min(o.size)>=600
  photo=o.convert("RGB")
  fmt=o.format
 rawpath=OUT/("MISSHA-No25-legacy-gold-pump-KGallery-original."+{"WEBP":"webp","JPEG":"jpg","PNG":"png"}[fmt])
 rawpath.write_bytes(raw)
 image=Image.new("RGB",(1080,1080),"#FAF9FA")
 d=ImageDraw.Draw(image)
 d.rounded_rectangle((40,40,1040,1040),radius=25,outline="#DDD0D4",width=2)
 d.text((80,68),"MISSHA M PERFECT COVER BB",font=ft(31,True),fill="#5B414A")
 d.text((80,132),"No.25  WARM BEIGE  |  50mL",font=ft(27,True),fill="#805860")
 d.line((78,191,1003,191),fill="#D9C6CE",width=3)
 fit=ImageOps.contain(photo,(930,736),Image.Resampling.LANCZOS)
 image.paste(fit,((1080-fit.width)//2,205+(736-fit.height)//2))
 d.line((79,958,1004,958),fill="#D9C6CE",width=2)
 d.text((79,965),"ORIGINAL MERCHANT PHOTO   |   QA ONLY",font=ft(18,True),fill="#6A5C63")
 d.text((79,999),"PHOTO RIGHTS / EXACT OWNED STOCK EDITION UNVERIFIED",font=ft(15),fill="#96868C")
 jpg=OUT/"MISSHA-No25-legacy-gold-pump-new-merchant-reference-1080-QA.jpg"
 image.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(jpg) as check:assert check.format=="JPEG" and check.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000
 record.update(status="SOURCE_SAVED_SHADE_NO25_LEGACY_PACKAGE_VISUAL_QA_HOLD",
  source_format=fmt,raw_original=str(rawpath),original_sha256=sha(rawpath),native_pixels=list(photo.size),
  reference_JPG=str(jpg),jpg_sha256=sha(jpg),jpg_bytes=jpg.stat().st_size)
except Exception as exc:
 record.update(status="HOLD_NEW_CDN_SOURCE_FETCH_FAILURE",error=type(exc).__name__+": "+str(exc)[:220])
 print("HOLD25",record["error"])
board=Image.new("RGB",(1580,610),"#F0ECEF")
d=ImageDraw.Draw(board)
d.text((15,9),"v2870 | NO21 / NO23 / NO25 LEGACY 50ml GOLD PUMP | QA ONLY",font=ft(23,True),fill="#514451")
inputs=[p21,old23,Path(record["reference_JPG"]) if "reference_JPG" in record else None]
for i,(label,p) in enumerate(zip(("21","23","25"),inputs)):
 if p is not None:
  with Image.open(p) as im:
   panel=im.convert("RGB").resize((505,505),Image.Resampling.LANCZOS)
 else:
  panel=Image.new("RGB",(505,505),"#E5E0E3")
 board.paste(panel,(19+520*i,55))
 d.text((24+520*i,571),"No."+label+(" / QA reference" if p else " / HOLD"),font=ft(18,True),fill="#57454B")
contact=OUT/"v2870-old-gold-pump-three-shade-review-QA.jpg"
board.save(contact,"JPEG",quality=87,optimize=True)
assert sha(p21)==shade21["output_sha256"] and sha(old23)==prior["old_23_sha256"]
result={
 "version":"v2870","baseline":"v2869","family":"pending-03","new_exact_shade_target":"No.25 Warm Beige 50ml old gold pump",
 "attempt_type":"new retailer Shopify CDN / do not retry failed BigW / invalid eBay link",
 "new_original_source_recovered":bool(record.get("reference_JPG")),
 "source_record":record,
 "old_21_reused_sha_unchanged":sha(p21),"old_23_reused_sha_unchanged":sha(old23),
 "native_21_23_originals_rewritten":False,
 "contact":str(contact),"contact_sha256":sha(contact),
 "manual_original_no25_print_check_required":True,
 "new_2026_US_red_white_tube_source_prohibited_for_this_old_stock":True,
 "third_party_merchant_photo_licensed":False,"stock_edition_confirmed":False,
 "original_MK_logo_authenticated":False,
 "v2868_adjacent_shade_labels_in_some_crop_QA_hold":True,
 "previous_11_published_groups_untouched":True,"previous_55_public_URLs_untouched":True,
 "new_sale_approvals":0,"new_public_URLs":0,"final_XLSX_shared":False,
 "next":"Visually compare 21/23/25 gold-pump labels, no reuse without source rights and physical owned generation; keep v2868 shade crops as group reference only, not standalone sale images. Then resume pending-02/10/12 specification gates without repeating completed artwork."
}
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2870","new_shade25_candidate":bool(record.get("reference_JPG")),"retail_approved":0},ensure_ascii=False))
