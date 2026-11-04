#!/usr/bin/env python3
"""v2701 compose five physically preserved product JPGs for previously
one-photo MISSHA Moist Up family. Prior photo01 and regional photos01-04 remain
SHA-identical; never invent shade charts, logo or retail permissions.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("qa-review")
HIST=ROOT/"v2682-seven-remaining-five-JPG-reviews"/"pending-02"
REG=ROOT/"v2700-missha-moistup-regional-exact-product-photo-proofs"
OUT=ROOT/"v2701-missha-moistup-five-actual-product-photo-QA"
assert HIST.is_dir() and REG.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=list(HIST.glob("01-*.jpg"))
assert len(old)==1,old
source=[old[0]]+[REG/f"{n:02d}-Missha-regional-real-photo-reference.jpg" for n in range(1,5)]
assert len(source)==5 and all(p.exists() for p in source)
files=[]
for n,p in enumerate(source,1):
 name=f"{n:02d}-"+("KR-historical" if n==1 else f"regional-photo-{n-1:02d}")+"-byte-preserved-QA.jpg"
 dest=OUT/name
 shutil.copy2(p,dest)
 assert sha(dest)==sha(p)
 with Image.open(dest) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert dest.stat().st_size<2_000_000
 files.append({"slot":n,"file":dest.name,"origin":str(p),"sha256":sha(dest),"exact_bytes_preserved":True})
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",26)
board=Image.new("RGB",(1850,510),"#f3f1ef")
d=ImageDraw.Draw(board)
d.text((19,16),"v2701 MISSHA MOIST UP / FIVE REAL SOURCE PHOTOS / NOT RETAIL",font=font,fill="#232323")
for x in files:
 with Image.open(OUT/x["file"]) as photo:
  tile=photo.convert("RGB").resize((342,342),Image.Resampling.LANCZOS)
 xx=19+(x["slot"]-1)*368
 board.paste(tile,(xx,70))
 d.text((xx,421),f"FRAME {x['slot']:02d} PHOTO",font=font,fill="#232323")
preview=OUT/"v2701-5-photo-proof.jpg"
board.save(preview,"JPEG",quality=85,optimize=True)
(OUT/"v2701-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
manifest={
 "version":"v2701","base":"v2700","family":"pending-02",
 "product":"MISSHA Magic Cushion Moist Up",
 "five_actual_product_photo_JPGs_present":True,
 "source_JPGs_reencoded_or_regenerated":0,
 "prior_historical_real_JPGs_byte_preserved":1,
 "newly_integrated_regional_photo_JPGs_byte_preserved":4,
 "replaced_generic_information_cards_in_new_QA_revision":4,
 "previous_v2682_5frame_QA_set_untouched":True,
 "regional_shades_from_source_catalog":["NO.21","NO.23"],
 "actual_owned_stock_shades_and_Korean_edition_verified":False,
 "photo_commercial_rights_verified":False,
 "retail_approved":False,
 "old_11_approved_families_unchanged":True,
 "existing_55_verified_public_URLs_unchanged":True,
 "final_xlsx_shared":False,"frames":files}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2701","new_five_JPG_QA_set":True,"photo_frames":5,
"unchanged_historical_photos":1,"regional_photos_preserved":4,"retail_approved":0}))
