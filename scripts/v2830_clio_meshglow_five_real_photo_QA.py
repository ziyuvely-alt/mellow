#!/usr/bin/env python3
"""v2830: curate five distinct exact-product scene JPGs for pending-04
CLIO Mesh Glow Essential Cushion MINI 5g from v2829. This is a QA
reference set, NOT sales-approved and NOT verified per-shade marketing.

Only original archive bytes are copied. Frames 03/04 are consumer reviews
(usage rights not obtained), and frame 05 explicitly says 23N only.
No global source/URL mutations, no XLSX.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,json,hashlib,base64
R=Path("qa-review")
SRC=R/"v2829-clio-mesh-glow-essential-mini5g-exact-official-source-corpus"
OUT=R/"v2830-clio-meshglow-essential-mini5g-five-distinct-physical-photo-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
SELECT=[
 ("01-mini5g-pink-case-merchant-packshot-QA.jpg",
  "09-Fresh-Mask-EXACT-ITEM-REFERENCE-QA.jpg",
  "GENERIC_SINGLE_PRODUCT_PACKSHOT","Unknown variant; no shade claim",
  "MERCHANT_COPYRIGHT_UNVERIFIED"),
 ("02-mini5g-open-case-with-puff-merchant-QA.jpg",
  "11-Korecare-EXACT-ITEM-REFERENCE-QA.jpg",
  "GENERIC_SINGLE_PRODUCT_PACKSHOT","Open compact and puff; unknown shade",
  "MERCHANT_COPYRIGHT_UNVERIFIED"),
 ("03-closed-mini5g-on-palm-customer-source-QA.jpg",
  "01-CLIO-Korean-Official-EXACT-ITEM-REFERENCE-QA.jpg",
  "CUSTOMER_REVIEW_REFERENCE_ONLY","Consumer photograph on CLIO product page; photographer rights not established",
  "CUSTOMER_PHOTO_PERMISSION_UNVERIFIED"),
 ("04-open-mini5g-on-palm-customer-source-QA.jpg",
  "02-CLIO-Korean-Official-EXACT-ITEM-REFERENCE-QA.jpg",
  "CUSTOMER_REVIEW_REFERENCE_ONLY","Consumer photograph of opened compact; shade unknown",
  "CUSTOMER_PHOTO_PERMISSION_UNVERIFIED"),
 ("05-23N-Ginger-exact-mini5g-merchant-reference-QA.jpg",
  "10-Fresh-Mask-EXACT-ITEM-REFERENCE-QA.jpg",
  "23N_GINGER_EXACT_SHADE_ONLY","Printed 23N Ginger; never use for 21C or 21N",
  "MERCHANT_COPYRIGHT_AND_23N_STOCK_UNVERIFIED"),
]
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else REG,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seen=set();frames=[]
for slot,(name,source_name,role,description,rights) in enumerate(SELECT,1):
 source=SRC/source_name
 assert source.is_file(),source
 destination=OUT/name
 shutil.copy2(source,destination)
 checksum=sha(source)
 assert checksum==sha(destination) and checksum not in seen
 seen.add(checksum)
 with Image.open(destination) as img:
  img.load()
  assert img.format=="JPEG" and img.size==(1080,1080)
 assert destination.stat().st_size<2000000
 frames.append({"slot":slot,"JPG":destination.name,"source_JPG":str(source),
                "sha256":checksum,"bytes":destination.stat().st_size,
                "exact_source_bytes_preserved":True,"source_role":role,
                "description":description,"rights_hold":rights,
                "usable_for_21C_21N_exact_shade_hero":False,
                "usable_for_23N_exact_shade_hero":role=="23N_GINGER_EXACT_SHADE_ONLY",
                "retail_approved":False})
contact=Image.new("RGB",(1890,516),"#f1f0ed")
d=ImageDraw.Draw(contact)
d.text((17,15),"v2830 FIVE REAL PHOTO SOURCES | MESH GLOW ESSENTIAL MINI 5g | QA ONLY",font=ft(24,True),fill="#302d30")
for i,f in enumerate(frames):
 with Image.open(OUT/f["JPG"]) as img:
  tile=img.convert("RGB").resize((343,343),Image.Resampling.LANCZOS)
 x=15+i*378
 contact.paste(tile,(x,69))
 flag=["GENERIC","GENERIC","CUSTOMER RIGHTS HOLD","CUSTOMER RIGHTS HOLD","23N ONLY"][i]
 d.text((x,422),f"#{i+1} {flag}",font=ft(18,True),fill="#353136")
proof=OUT/"v2830-five-distinct-source-proof.jpg"
contact.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2830-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2830","baseline":"v2829","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion MINI 5g",
 "product_page":"https://clubclio.co.kr/shop/goodsView/0000006954",
 "actual_1080x1080_JPGs_saved":5,"distinct_original_sha256_count":len(seen),
 "source_media_reencoded":0,"source_media_overwritten":0,
 "explicit_23N_source_frames":1,
 "unverified_shade_generic_packshot_frames":2,
 "customer_review_only_not_licensed_frames":2,
 "21C_21N_exact_variant_hero_images_confirmed":False,
 "excluded_as_wrong_photo_or_not_item":["v2829 source 03..06 mixed-brand consumer kit photos",
   "v2829 source 07..08 shipping/payment UI"],
 "commercial_photo_use_permissions_confirmed":False,
 "actual_owned_5g_stock_edition_and_variants_confirmed":False,
 "original_MK_logo_authenticated":False,
 "new_retail_approvals":0,
 "prior_11_retail_approved_families_unchanged":True,
 "prior_55_verified_URLs_unchanged":True,
 "prior_p04_photographs_unchanged":True,
 "prior_p05_original_mini_21C_21N_23N_photos_unchanged":True,
 "final_xlsx_shared":False,
 "status":"FIVE_REAL_PHOTO_QA_REFERENCES_STAGED_NOT_SELLABLE",
 "frames":frames,
 "next_actions":[
  "Obtain authorized merchant-owned product packshots or independently licensed real photos for scenes 03-04",
  "Find exact 21C and 21N variant-linked Mesh Glow Essential Mini 5g packshots; do not reuse Founwear The Original Mini",
  "Confirm owned stock exact package/5g options before any retail approval",
  "No public URL creation until image rights, batch size and claim QA are satisfied"]
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2830","five_saved":len(frames),
 "photos_untouched":True,"new_retail_approved":0}))
