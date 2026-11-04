#!/usr/bin/env python3
"""v2802: derive exactly five visually different GOODAL Cream Alpha 50mL QA JPGs
from THREE authenticated 1080 JPG photographic source scenes (v2784).
The extra two are honestly labeled detail CROPS, not new independent photos.
Never invent packaging, swatches, efficacy claims, models or MK badge.
Original files and prior approved published 55 URLs stay unchanged.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat
import hashlib,json,base64,shutil
BASE=Path("qa-review")
PREVIOUS=BASE/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"
OUT=BASE/"v2802-goodal-alpha-three-authentic-scenes-two-explicit-detail-crops-QA"
assert PREVIOUS.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
previous=json.loads((PREVIOUS/"manifest.json").read_text())
assert previous["version"]=="v2784" and len(previous["curated_photos"])==3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
for obj in previous["curated_photos"]:
 p=PREVIOUS/obj["file"]
 assert p.is_file() and sha(p)==obj["sha256"]
 with Image.open(p) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
  photo=im.convert("RGB").copy()
 sources.append((p,photo))
# Role-first QA: not five invented independent photos.
# Crop away upper marketing slogans and bottom text when applicable.
SCENES=[
  {"slot":1,"src":0,"name":"single 50mL jar photo, byte unchanged","crop":None,"derived_crop":False},
  {"slot":2,"src":1,"name":"open jar with cream from official second photo","crop":(290,340,1065,921),"derived_crop":True},
  {"slot":3,"src":2,"name":"real cream texture on hand","crop":(8,280,1073,850),"derived_crop":True},
  {"slot":4,"src":0,"name":"actual jar branding and creamy texture close-up","crop":(168,288,956,891),"derived_crop":True},
  {"slot":5,"src":1,"name":"authentic open-jar capsule/cream texture macro","crop":(550,512,1054,950),"derived_crop":True},
]
files=[]
for item in SCENES:
 original,photo=sources[item["src"]]
 slot=item["slot"]
 filename=OUT/f"{slot:02d}-GOODAL-Alpha-real-photo-QA.jpg"
 if item["crop"] is None:
  shutil.copyfile(original,filename)
  assert sha(original)==sha(filename)
  dimensions=[1080,1080]
 else:
  box=item["crop"]
  assert 0<=box[0]<box[2]<=1080 and 0<=box[1]<box[3]<=1080
  crop=photo.crop(box)
  dimensions=list(crop.size)
  # No fake resolution: product photo crop inserted on 1080 white square.
  fitted=ImageOps.contain(crop,(1010,1010),Image.Resampling.LANCZOS)
  square=Image.new("RGB",(1080,1080),"white")
  square.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
  square.save(filename,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(filename) as chk:
  chk.load();assert chk.format=="JPEG" and chk.size==(1080,1080)
 assert filename.stat().st_size<2_000_000
 files.append({
  "slot":slot,"JPG":filename.name,"JPG_sha256":sha(filename),
  "JPG_bytes":filename.stat().st_size,
  "photograph_role":item["name"],
  "authentic_official_source_photo":str(original),
  "source_sha256_preserved":sha(original),
  "native_1080_photographic_pixels_preserved_unmodified":not item["derived_crop"],
  "is_derived_closeup_not_independent_photograph":item["derived_crop"],
  "source_region":list(item["crop"]) if item["crop"] else None,
  "actual_cropped_photo_resolution":dimensions,
  "new_product_pixels_fabricated":False,"retail_approved":False,
  "marketing_claim_cropped_region_requires_visual_review":True
 })
# One sheet with all five, genuinely viewable from manifest.
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=ImageFont.truetype(FONT,21)
board=Image.new("RGB",(1840,525),"#f2f1ef")
d=ImageDraw.Draw(board)
d.text((15,12),"v2802 GOODAL Vita C Alpha 50mL | 3 real photo sources + 2 detail crops | NOT RETAIL",font=ft,fill="#333333")
for i,item in enumerate(files):
 with Image.open(OUT/item["JPG"]) as p:
  thumb=p.convert("RGB").resize((325,325),Image.Resampling.LANCZOS)
 x=12+365*i
 board.paste(thumb,(x,53))
 d.text((x,393),f"{i+1} / source {SCENES[i]['src']+1}",font=ft,fill="#282828")
 d.text((x,420),"crop detail" if item["is_derived_closeup_not_independent_photograph"] else "original unmodified",font=ft,fill="#494949")
contact=OUT/"v2802-five-actual-photo-source-scenes-contact.jpg"
board.save(contact,"JPEG",quality=83,optimize=True)
(OUT/"v2802-contact.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
manifest={
 "version":"v2802","baseline":"v2801","family":"pending-19",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "five_physical_1080_JPG_files_saved":5,
 "independent_authentic_photo_sources":3,
 "additional_detail_crops_not_independent_photos":2,
 "all_unique_sha256":len({x["JPG_sha256"] for x in files})==5,
 "claim":"Five visual angles produced without inventing pixels; not five independent photographic source scenes",
 "original_all_three_photos_sha_preserved":True,
 "original_sources_reencoded":0,
 "brand_promotional_caption_verification":"HOLD_VISUAL_QA",
 "current_owner_physical_stock_generation_verified":False,
 "commercial_photo_redistribution_rights_verified":False,
 "original_authenticated_MK_logo_available":False,
 "new_retail_approval":0,
 "prior_11_approved_product_families_unchanged":True,
 "prior_55_public_urls_unchanged":True,
 "previous_QA_assets_unchanged":True,
 "final_excel_or_spreadsheet_shared":False,
 "frames":files
}
assert manifest["all_unique_sha256"]
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2802","saved":5,"authentic_original_photo_sources":3,
"detail_derivatives":2,"no_commercial_release":True}))
