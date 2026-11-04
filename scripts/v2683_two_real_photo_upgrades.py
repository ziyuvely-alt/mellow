#!/usr/bin/env python3
"""v2683 targeted real-product PHOTO upgrade for pending-23 / pending-27.
Replace exactly one sparse info card in each v2680 draft with an existing
distinct real same-SKU historical 1080px JPG. Never touch v2680 or approved assets.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,shutil,base64
SRC=Path("historical/review-JPG-by-family")
BASE=Path("qa-review/v2680-six-brand-five-JPG-photo-led-batch")
OUT=Path("qa-review/v2683-two-family-photo-content-upgrades")
assert BASE.exists() and not OUT.exists()
OUT.mkdir(parents=True)
specs=[{"family":"pending-23","new_source_slot":5,"replace_frame":5,
        "reason":"Original product pair photo replaces generic NET CONTENT placeholder"},
       {"family":"pending-27","new_source_slot":4,"replace_frame":5,
        "reason":"Actual product+packaging photo replaces generic NET CONTENT placeholder"}]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 pix=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if pix[y*9+x]>pix[y*9+x+1])
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
board=Image.new("RGB",(1840,1480),"#eef0ed");d=ImageDraw.Draw(board)
d.text((20,15),"v2683 TWO PRECISE PHOTO-BASED UPGRADES / 10 JPG QA FRAMES",font=font,fill="#252525")
results=[]
for row,config in enumerate(specs):
 fam=config["family"]
 old_dir=BASE/fam
 old_files=sorted(old_dir.glob("*.jpg"))
 assert len(old_files)==5,(fam,len(old_files))
 historical=list((SRC/fam).glob(f"{config['new_source_slot']:02d}*.jpg"))
 assert len(historical)==1,(fam,historical)
 photo=historical[0]
 dest=OUT/fam;dest.mkdir()
 replacements=[]
 old_hashes=[]
 for file in old_files:
  number=int(file.name[:2])
  if number==config["replace_frame"]:
   p=dest/f"{number:02d}-genuine-source-slot{config['new_source_slot']:02d}-unmodified-QA.jpg"
   shutil.copy2(photo,p)
   assert digest(photo)==digest(p)
   replacements.append(p)
  else:
   p=dest/file.name
   shutil.copy2(file,p)
   assert digest(file)==digest(p)
  with Image.open(p) as image:
   image.load()
   assert image.format=="JPEG" and image.size==(1080,1080)
   h=dhash(image.convert("RGB"))
   thumb=image.convert("RGB").resize((339,339),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  old_hashes.append((number,h))
  x=18+(number-1)*363;y=62+row*710
  board.paste(thumb,(x,y))
  d.text((x,y+345),fam+" / "+str(number).zfill(2),font=font,fill="#242424")
 assert len(replacements)==1
 new_h=dict(old_hashes)[config["replace_frame"]]
 minimum=min((new_h^h).bit_count() for number,h in old_hashes if number!=config["replace_frame"])
 # A genuine photo must be recognisably different from any other frame.
 assert minimum>=9,(fam,minimum)
 results.append({"family":fam,"photo_source_slot":config["new_source_slot"],
   "replaced_info_frame":config["replace_frame"],"new_photo_hash":digest(replacements[0]),
   "new_photo_vs_remaining_min_dhash":minimum,"prior_four_frames_sha_identical":True,
   "source_is_historical_edition_not_latest":True,"status":"QA_UPGRADED_NOT_RETAIL_APPROVED",
   "reason":config["reason"]})
proof=OUT/"v2683-two-upgraded-photo-families-contact.jpg"
board.save(proof,quality=84,optimize=True)
(OUT/"v2683-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2683","baseline":"v2680","new_photo_assets_created":0,
 "actual_source_photos_byte_preserved":2,"replaced_weak_info_frames":2,
 "source_frames_kept_unchanged":8,"family_count":2,"JPG_count":10,
 "families":results,"photo_rights_verified":False,
 "owned_stock_package_verified":False,"latest_v2647_compared":False,
 "retail_approved_new_families":0,"existing_11_approved_groups_unchanged":True,
 "existing_55_public_URLs_unchanged":True,"final_excel_not_shared":True}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photo_upgraded_families":2,"unchanged_frames":8,
 "genuine_replacement_photos":2,"min_dhash":[x["new_photo_vs_remaining_min_dhash"] for x in results],
 "sale_approved":0}))
