#!/usr/bin/env python3
"""v2828 assemble TWO photo-grounded five-scene commercial-QA candidate galleries
for CLIO original mini 5g shades 21C/21N, 10 physically saved JPGs total.
Every frame copies existing real source JPG bytes. 4 explicitly generic mini
product scenes are shared by both shade galleries WITHOUT inventing shade
associations. Frame 01 must use the independently verified shade cutout.

DO NOT RELEASE without owned-stock identity and original-photo commercial
redistribution permissions. No old approved file or URL changes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2828-clio-mini5g-21C-21N-five-real-photo-QA-sets"
assert not OUT.exists()
OUT.mkdir(parents=True)
GEN=ROOT/"v2826-clio-mini5g-common-photo-gallery-source-discovery"
COMMON=[
 ("02-EXACT-MINI-COMPACT-OPEN-COMMON-NO-SHADE-QA.jpg",
  "01-COMMON-NOT-SHADE-DODOSKIN-QA.jpg",
  "COMMON_PRODUCT_STRUCTURE","Single open mini compact; no shade assignment"),
 ("03-THREE-SHADE-COMPARISON-21C-21N-23N-QA.jpg",
  "03-COMMON-NOT-SHADE-DODOSKIN-QA.jpg",
  "THREE_SHADE_REFERENCE","21C, 21N and 23N comparison together, not one shade"),
 ("04-HANDHELD-MINI-SIZE-COMPARISON-COMMON-QA.jpg",
  "05-COMMON-NOT-SHADE-DODOSKIN-QA.jpg",
  "COMMON_SIZE_CONTEXT","Hand holding mini beside larger compact; NOT bundle contents"),
 ("05-MINI-VERSUS-ORIGINAL-SIZE-DETAIL-COMMON-QA.jpg",
  "06-COMMON-NOT-SHADE-DODOSKIN-QA.jpg",
  "COMMON_SIZE_COMPARISON","Shows mini beside full-size, do not imply both are shipped")
]
VARIANTS=[
 ("21C","21C Lingerie",
  ROOT/"v2825-clio-mini-5g-21C-21N-uncropped-top-edge-repair"/"21C"/"01-corrected-full-lid-1080-JPG-QA.jpg"),
 ("21N","21N Linen",
  ROOT/"v2827-clio-mini5g-21N-remaining-peach-halo-mask-QA"/"01-21N-real-photo-full-lid-no-peach-halo-1080-QA.jpg")
]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"version":"v2828","baseline":"v2827","family":"pending-05",
 "product":"CLIO Kill Cover Founwear The Original Mini Cushion 5g",
 "variants":[],"total_qa_jpg_copies":0,
 "distinct_shade_specific_hero_for_each_variant":True,
 "common_photos_reused_with_explicit_no_shade_metadata":True,
 "all_source_photograph_files_unchanged":True,
 "original_23N_existing_five_photo_gallery_unchanged":True,
 "existing_21C_21N_source_cutouts_unchanged":True,
 "old_11_approved_families_untouched":True,
 "old_55_published_urls_unchanged":True,
 "all_photo_redistribution_rights_verified":False,
 "stock_shade_and_genuine_package_verified":False,
 "original_MK_logo_authenticated":False,
 "new_retail_sale_approvals":0,"final_XLSX_shared":False}
board=Image.new("RGB",(1880,1150),"#f1f0ee")
draw=ImageDraw.Draw(board)
draw.text((17,14),"v2828 FIVE REAL PHOTOS / 21C & 21N / COMMON FRAMES MARKED / QA ONLY",font=ft(24,True),fill="#28282a")
for row_idx,(shade,shade_name,hero) in enumerate(VARIANTS):
 folder=OUT/shade
 folder.mkdir()
 assert hero.is_file(),hero
 destinations=[("01-EXACT-"+shade+"-REAL-ALPHA-HERO-QA.jpg",hero,"EXACT_SHADE_HERO","Physical photo linked to "+shade_name)]
 for basename,source_file,role,desc in COMMON:
  source=GEN/source_file
  assert source.is_file(),source
  destinations.append((basename,source,role,desc))
 frames=[]
 for i,(name,source,role,description) in enumerate(destinations,1):
  target=folder/name
  shutil.copy2(source,target)
  assert sha(target)==sha(source)
  with Image.open(target) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   thumbnail=im.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
  assert target.stat().st_size<2_000_000
  x=16+(i-1)*372;y=68+row_idx*515
  board.paste(thumbnail,(x,y))
  draw.text((x,y+351),f"{shade} #{i} "+("EXACT" if i==1 else "COMMON"),font=ft(19,True),fill="#282628")
  frames.append({"slot":i,"file":str(target.relative_to(OUT)),
    "sha256":sha(target),"bytes":target.stat().st_size,
    "source_file":str(source),"source_sha256":sha(source),
    "photo_source_role":role,"factual_note":description,
    "retail_approved":False})
 assert len(frames)==5 and len(set(x["sha256"] for x in frames))==5
 report["variants"].append({"shade":shade,"shade_label":shade_name,
  "actual_1080_JPG_count":5,"distinct_frame_source_SHA_count":5,
  "one_independent_shade_linked_hero":True,"four_shared_product_reference_scenes":True,
  "status":"FIVE_PHOTO_QA_SET_STAGED_STOCK_LICENSE_HOLD",
  "frames":frames})
 report["total_qa_jpg_copies"]+=5
draw.text((18,1090),"Product & size photos shared across variants are NOT shade-specific and do not imply multiple units shipped.",font=ft(19),fill="#525052")
proof=OUT/"v2828-21C-21N-five-photo-source-contact-QA.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2828-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
assert report["total_qa_jpg_copies"]==10
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2828","family":"pending-05","variants":2,
 "physically_saved_1080_JPG":10,"distinct_frame_sources_per_variant":5,
 "new_retail_approved":0}))
