#!/usr/bin/env python3
"""v2859: Four already-extracted MISSHA Cover Lasting stock shade candidate cards.
Re-use exact archived PNG bytes. No regenerated product photograph, no color swaps,
no edition assumptions, no changes to published or previously-approved assets.
The result is internal, watermarked, non-commercial QA artwork only.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from hashlib import sha256
import json

R = Path("qa-review")
OUT = R / "v2859-missha-coverlasting-four-shade-photo-cards-QA"
assert not OUT.exists()
SOURCES = {
 "21": ("v2748-missha-coverlasting-21-source01-round-compact-only/01-missha-N21-actual-compact-transparent-QA.png",
        "f3393f4b03398ff7b7e6768a26016df4b26df3bfbed0c60bd61309f1a59fa152"),
 "23": ("v2747-missha-coverlasting-23-source02-round-compact-qa/01-original-pink-compact-N23-transparent-QA.png",
        "21b28f5b922a1fa342f9699f858a7b06b59815b02dde10ac8f9290aba4f623e4"),
 "25": ("v2750-missha-N25-N27-distinct-official-photo-cutout-QA/shade-25/01-original-25-isnet-true-alpha-QA.png",
        "4a23eb709f3dc15e4b649ca02e3b12afd288af9f204937aa6c4588c79c63242b"),
 "27": ("v2750-missha-N25-N27-distinct-official-photo-cutout-QA/shade-27/01-original-27-isnet-true-alpha-QA.png",
        "730d090198e24e5872660abab54a4707097c6903d1ddb4708d4c7cf85641ba03"),
}
def digest(p): return sha256(p.read_bytes()).hexdigest()
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(size,b=False): return ImageFont.truetype(BOLD if b else FONT,size)
OUT.mkdir(parents=True)
records=[]
outputs=[]
for shade,(relative,expected) in SOURCES.items():
 src=R/relative
 assert src.is_file() and digest(src)==expected,("immutable source mismatch",src)
 with Image.open(src) as im:
  im.load()
  assert im.mode=="RGBA" and im.format=="PNG"
  original=im.copy()
 assert original.getchannel("A").getbbox() is not None
 assert all(original.getchannel("A").getpixel(p)==0 for p in
            ((0,0),(original.width-1,0),(0,original.height-1),(original.width-1,original.height-1)))
 # No product recoloring, synthetic swatch, changed packaging, or logo substitution.
 surface=Image.new("RGB",(1080,1080),"#FBFAF8")
 d=ImageDraw.Draw(surface)
 d.rounded_rectangle((55,51,1025,1025),radius=22,outline="#E5DCD9",width=2)
 d.text((92,84),"MISSHA",font=ft(46,True),fill="#493B3E")
 d.text((92,144),"MAGIC CUSHION COVER LASTING",font=ft(25),fill="#6D5A5B")
 d.line((92,194,986,194),fill="#D9C6C7",width=3)
 d.rounded_rectangle((805,96,976,174),radius=14,fill="#F3E9EB")
 d.text((832,110),"No. "+shade,font=ft(30,True),fill="#674E58")
 placed=ImageOps.contain(original,(824,740),Image.Resampling.LANCZOS)
 surface.paste(placed,((1080-placed.width)//2,210+(740-placed.height)//2),placed.getchannel("A"))
 d.line((92,949,988,949),fill="#E0D5D5",width=2)
 d.text((94,961),"OPTION PHOTO REFERENCE  |  QA ONLY",font=ft(21,True),fill="#88787B")
 d.text((94,990),"STOCK / IMAGE RIGHTS / MK MARK PENDING",font=ft(16),fill="#A08F92")
 dst=OUT/f"MISSHA-Cover-Lasting-No{shade}-1080-photo-option-QA.jpg"
 surface.save(dst,"JPEG",quality=93,subsampling=0,optimize=True)
 with Image.open(dst) as check:
  check.load()
  assert check.size==(1080,1080) and check.format=="JPEG"
 assert dst.stat().st_size<2_000_000
 assert digest(src)==expected
 outputs.append(dst)
 records.append({
  "shade":shade,"source":str(src),"original_png_sha256":expected,
  "source_native_dimensions_px":list(original.size),
  "rendered_1080_JPG":str(dst),"rendered_JPG_sha256":digest(dst),
  "jpg_bytes":dst.stat().st_size,
  "product_pixels_color_altered":False,"source_png_changed":False,
  "photo_is_source_upscaled":placed.width>original.width or placed.height>original.height,
  "stock_generation_verified":False,"commercial_photo_rights_verified":False,
  "authenticated_MK_logo_verified":False,"sales_approved":False,
  "note":"Option-specific candidate only; not evidence of a verified shade-specific swatch."})
# Construct contact QA proof without counting it as one of the four option JPEGs.
sheet=Image.new("RGB",(1560,1570),"#EEEAE8")
dd=ImageDraw.Draw(sheet)
dd.text((28,12),"v2859 | FOUR DISTINCT PRESERVED MISSHA OPTION PHOTOS | QA ONLY",font=ft(25,True),fill="#4B3B42")
for i,(shade,p) in enumerate(zip(SOURCES,outputs)):
 with Image.open(p) as pic: preview=pic.convert("RGB").resize((730,730),Image.Resampling.LANCZOS)
 x=25+(i%2)*780; y=60+(i//2)*755
 sheet.paste(preview,(x,y))
 dd.text((x+20,y+699),"No. "+shade+" / internal candidate",font=ft(20,True),fill="#59444E")
contact=OUT/"v2859-four-distinct-options-contact-QA.jpg"
sheet.save(contact,"JPEG",quality=86,optimize=True)
assert len({r["rendered_JPG_sha256"] for r in records})==4
manifest={
 "version":"v2859","baseline":"v2858","family":"pending-01",
 "product":"MISSHA Magic Cushion Cover Lasting","qa_only":True,
 "new_option_specific_internal_1080_JPGs":4,"shade_numbers":["21","23","25","27"],
 "new_source_photos_downloaded":0,"source_PNGs_modified":0,
 "previous_11_published_families_unchanged":True,
 "previous_55_verified_public_URLs_unchanged":True,
 "source_products_real_photographs_reused":True,
 "false_swatch_claims_generated":0,"original_logo_faked":False,
 "shade_21_eligibility_requires_inventory_recheck":True,
 "exact_owned_stock_packaging_verified":False,"photo_commercial_rights_verified":False,
 "new_public_sale_URLs":0,"new_sale_approved_images":0,
 "final_spreadsheet_shared":False,
 "QA_contact":str(contact),"QA_contact_sha256":digest(contact),
 "variants":records,
 "next":"Visually review all four option layouts and the actual owned-stock edition; hold release until image rights and authentic MK logo are supplied. Then move to pending-12 (15mL vs 15g) and pending-10 (13g vs 15g) rather than repeat photo segmentation."
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2859","four_option_JPGs":len(outputs),
 "bytes":[p.stat().st_size for p in outputs],"unique_sha":len(set(digest(p) for p in outputs)),
 "sales_approved":0,"preserve_old_55":True},ensure_ascii=False))
