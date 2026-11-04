#!/usr/bin/env python3
"""v2684 two exact-source photo substitutions, no resize or retail publication."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("historical/review-JPG-by-family")
PREV=Path("qa-review/v2680-six-brand-five-JPG-photo-led-batch")
OUT=Path("qa-review/v2684-two-BOH-photo-detail-substitutions")
assert PREV.exists() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im.resize((9,8),Image.Resampling.LANCZOS)).getdata())
 return sum(1<<(y*8+x) for y in range(8) for x in range(8) if p[y*9+x]>p[y*9+x+1])
cases=[
 ("pending-24",5,5,"Glow Power Serum 30mL", "Photo contains printed Slow Aging/NAD marketing labels: unverified"),
 ("pending-25",5,5,"Glow Boost Cream 50mL", "Photo contains printed Korean glow/anti-aging claim badges: unverified")
]
allrows=[]
board=Image.new("RGB",(1810,890),"#f4f2f1")
d=ImageDraw.Draw(board)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
for ri,(family,slot,replace,title,warn) in enumerate(cases):
 old=PREV/family
 assert old.is_dir()
 fs=sorted(old.glob("*.jpg"))
 assert len(fs)==5
 candidate=list((ROOT/family).glob(f"{slot:02d}*.jpg"))
 assert len(candidate)==1,(family,candidate)
 new=candidate[0]
 dst=OUT/family;dst.mkdir()
 rows=[];percepts=[]
 for prior in fs:
  n=int(prior.name[:2])
  if n==replace:
   path=dst/f"{n:02d}-original-source-slot{slot:02d}-byte-preserved-QA.jpg"
   shutil.copy2(new,path)
   assert sha(path)==sha(new)
   typ="NEW_REAL_SOURCE_PHOTO_UNCHANGED"
  else:
   path=dst/prior.name
   shutil.copy2(prior,path)
   assert sha(path)==sha(prior)
   typ="PREVIOUS_QA_JPG_EXACT_BYTES"
  with Image.open(path) as im:
   im.load()
   assert im.format=="JPEG" and im.size==(1080,1080)
   percepts.append((n,dhash(im.convert("RGB"))))
   thumb=im.convert("RGB").resize((320,320),Image.Resampling.LANCZOS)
  assert path.stat().st_size<2_000_000
  x=15+(n-1)*359;y=42+ri*423
  board.paste(thumb,(x,y))
  d.text((x,y+325),f"{family} / {n:02d}",fill="#222222",font=font)
  rows.append(dict(slot=n,filename=path.name,sha256=sha(path),status=typ))
 target=dict(percepts)[replace]
 min_distance=min((target^h).bit_count() for n,h in percepts if n!=replace)
 assert min_distance>10,(family,min_distance)
 allrows.append(dict(family=family,product=title,changed_slot=replace,
   historical_photo_source_slot=slot,min_internal_photo_difference=min_distance,
   source_text_marketing_claims_unverified=warn,
   unchanged_prior_images=4,one_real_photo_added=True,
   sale_release="HOLD_SOURCE_PHOTO_COMMERCIAL_RIGHTS_AND_OLD_LABEL_CLAIMS",
   files=rows))
preview=OUT/"v2684-two-BOH-photo-upgrades-review.jpg"
board.save(preview,quality=84,optimize=True)
(OUT/"v2684-photo-review.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
data=dict(version="v2684",base="v2683",new_retail_approved=0,
 affected_QA_families=2,physical_JPG_files=10,existing_QA_image_bytes_preserved=8,
 historically_sourced_photos_added_without_reencode=2,photographic_rights_verified=False,
 source_product_claims_verified=False,physical_stock_edition_verified=False,
 latest_v2647_binary_compared=False,brand_original_MK_verified=False,
 existing_11_approved_families_modified=False,existing_55_public_URLs_modified=False,
 final_spreadsheet_shared=False,results=allrows)
(OUT/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photo_upgrade_families":2,"reused_photo_files":2,
 "preserved_prior_frames":8,"perceptual_min_differences":[r["min_internal_photo_difference"] for r in allrows],
 "retail_approved":0}))
