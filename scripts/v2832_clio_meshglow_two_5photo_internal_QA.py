#!/usr/bin/env python3
"""v2832 two exact-shade 5-image INTERNAL QA bundles, source-SHA preserving.

The bundles are NOT sellable: 2 source frames in each come from customer
reviews and other merchant photos have no redistribution permission.
Shared images must never be claimed as the 21C/21N-specific shade, and 23N
is NEVER inserted into 21C or 21N options. No edits to prior images/URLs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,shutil,json,base64
R=Path("qa-review")
PREV=R/"v2830-clio-meshglow-essential-mini5g-five-distinct-physical-photo-QA"
NEW=R/"v2831-clio-mesh-glow-essential-mini-21C-21N-exact-shade-reference"
OUT=R/"v2832-meshglow-essential-mini5g-21C-21N-five-image-internal-QA"
assert PREV.is_dir() and NEW.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
old=json.loads((PREV/"manifest.json").read_text())
recent=json.loads((NEW/"manifest.json").read_text())
assert old["family"]==recent["family"]=="pending-04"
assert old["actual_1080x1080_JPGs_saved"]==5
assert recent["new_shade_labelled_reference_photos_saved"]==2
assert old["frames"][4]["source_role"]=="23N_GINGER_EXACT_SHADE_ONLY"
by_slot={int(row["slot"]):row for row in old["frames"]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda sz,b=False:ImageFont.truetype(BOLD if b else FONT,sz)
out_variants=[]
for shade,shade_name in (("21C","Lingerie"),("21N","Linen")):
  first=NEW/f"{shade}-{shade_name}-source-variant-labelled-photo-QA.jpg"
  assert first.is_file()
  # Exact label reference, two generic merchant image assets, two review-only.
  # The last two remain unlicensed references, NOT sale slots.
  sources=[
    (first,f"EXACT_{shade}_MERCHANT_SHADE_LABELLED","MERCHANT_COPYRIGHT_UNVERIFIED",
      "Shade printed in reference. Product appearance must be verified against actual stock.",True),
    (PREV/by_slot[1]["JPG"],"COMMON_UNASSIGNED_SHADE_PACKSHOT","MERCHANT_COPYRIGHT_UNVERIFIED",
      "Same 5g product family, no physical shade identity confirmed.",False),
    (PREV/by_slot[2]["JPG"],"COMMON_UNASSIGNED_SHADE_OPEN_COMPACT","MERCHANT_COPYRIGHT_UNVERIFIED",
      "Open compact and puff, shade not proven.",False),
    (PREV/by_slot[3]["JPG"],"REVIEW_ONLY_CLOSED_MINI_ON_HAND","CUSTOMER_REVIEW_PHOTO_PERMISSION_UNVERIFIED",
      "Photographer consent missing; cannot be a sale image.",False),
    (PREV/by_slot[4]["JPG"],"REVIEW_ONLY_OPEN_MINI_ON_HAND","CUSTOMER_REVIEW_PHOTO_PERMISSION_UNVERIFIED",
      "Photographer consent missing; cannot be a sale image.",False)
  ]
  dst=OUT/shade;dst.mkdir()
  saved=[]
  for slot,(source,role,permission,notes,shade_specific) in enumerate(sources,1):
    assert source.is_file()
    assert "23N-Ginger" not in source.name and "Founwear" not in source.name
    dest=dst/f"{slot:02d}-{role}-QA-REFERENCE.jpg"
    shutil.copy2(source,dest)
    assert sha(source)==sha(dest)
    with Image.open(dest) as im:
      im.load()
      assert im.format=="JPEG" and im.size==(1080,1080)
    assert dest.stat().st_size<2_000_000
    saved.append({
      "slot":slot,"file":str(dest.relative_to(OUT)),
      "source":str(source),"sha256":sha(dest),
      "exact_original_JPG_bytes_preserved":True,
      "photo_role":role,"shade_specific_identity_proven_by_source_label":shade_specific,
      "photo_redistribution_rights":permission,
      "permitted_for_sale_without_further_clearance":False,
      "notes":notes,"bytes":dest.stat().st_size
    })
  assert len({x["sha256"] for x in saved})==5
  out_variants.append({
    "shade":shade,"shade_label":shade_name,
    "physical_JPG_count":5,"different_sha_count":5,
    "shade_specific_reference_JPGs":1,"common_reference_JPGs":2,
    "customer_review_unlicensed_JPGs":2,
    "status":"QA_REFERENCE_ONLY_NO_SALES_APPROVAL",
    "frames":saved
  })
for variant in out_variants:
    shade=variant["shade"]
    board=Image.new("RGB",(1820,460),"#f1f0ee")
    d=ImageDraw.Draw(board)
    d.text((12,9),f"v2832 {shade} {variant['shade_label']} / five real-photo references / NOT FOR SALE",font=font(23,True),fill="#222222")
    for frame in variant["frames"]:
      src=OUT/frame["file"]
      with Image.open(src) as im:
        thumbnail=im.convert("RGB").resize((327,327),Image.Resampling.LANCZOS)
      x=10+(frame["slot"]-1)*361
      board.paste(thumbnail,(x,50))
      label="SHADE-LABEL" if frame["slot"]==1 else ("NO SHADE" if frame["slot"] in (2,3) else "REVIEW ONLY")
      d.text((x,386),label,font=font(20,True),fill="#333333")
      d.text((x,417),"License unverified",font=font(15),fill="#6e565a")
    proof=OUT/f"v2832-{shade}-five-photo-contact.jpg"
    board.save(proof,"JPEG",quality=82,optimize=True)
    (OUT/f"v2832-{shade}-five-photo-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2832","baseline":"v2831","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Mini Cushion 5g",
 "exact_21C_21N_five_photo_internal_QA_sets":2,
 "JPGs_copied_byte_identical":10,
 "physical_JPGs_per_shade":5,
 "unique_21C_21N_first_frame_source":True,
 "customer_review_frames_per_set_NOT_LICENSED":2,
 "merchant_licensed_for_redistribution":False,
 "commercially_usable_5image_set_confirmed":False,
 "stock_option_inventory_match_verified":False,
 "actual_original_MK_logo_authenticated":False,
 "excluded_23N_specific_image_from_21C_21N":True,
 "excluded_Founwear_Original_Mini_assets":True,
 "source_v2830_v2831_original_images_modified":False,
 "prior_11_approved_families_unchanged":True,
 "prior_55_verified_public_urls_unchanged":True,
 "additional_sale_approvals":0,"final_xlsx_shared":False,
 "variants":out_variants,
 "next_actions":[
    "Replace unlicensed customer photos (slots 4/5) with actual licensed merchandise source photography, do not crop customer photos to hide the origin.",
    "Confirm actual 5g packaging and shades 21C/21N from owner stock, rather than merely merchant label in reference.",
    "Do not release the two options until original MK logo and photo redistribution permission are documented."
 ]
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2832","physical_photo_JPGs":10,"option_QA_sets":2,
"customer_photo_rights_holds":4,"new_sales_approved":0}))
