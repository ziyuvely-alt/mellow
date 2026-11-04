#!/usr/bin/env python3
"""v2706 recover distinct saved old product-photo JPG compositions for six
under-photographed families in one batch. Copy original bytes exactly and do
not mislabel stamped MK candidate art as officially branded/sale approved.
Never overwrite v2705, v2701, original 11 published or public 55 URLs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64,re
ARCH=Path("old_assets/public/owned86/20261029")
OUT=Path("qa-review/v2706-six-archival-five-real-source-families")
assert ARCH.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
SPEC=[
 ("pending-04","clio-mesh-glow-essential-cushion-mini","CLIO Mesh Glow Essential Mini 5g"),
 ("pending-11","obge-double-essence50x2","OBgE Double Essence 50mL 2-formula"),
 ("pending-15","drg-green-mild-up-sun-plus-50ml","Dr.G Green Mild Up Sun Plus 50mL"),
 ("pending-18","drg-brightening-up-sun-plus-50ml","Dr.G Brightening Up Sun Plus 50mL"),
 ("pending-26","pixelpure-gentle-gel-to-foam-cleanser-145ml","PIXEL PURE Gel to Foam Cleanser 145mL"),
 ("pending-29","pixelpure-radiance-aqua-soothing-cream-50ml","PIXEL PURE Radiance Aqua Soothing Cream 50mL"),
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
rows=[]
for idx,(fid,slug,name) in enumerate(SPEC):
 srcs=sorted((ARCH/slug).glob('*.jpg'),key=lambda p:int(re.search(r'_(\d+)\.jpg$',p.name).group(1)))
 assert len(srcs)>=5,(fid,len(srcs))
 dst=OUT/fid;dst.mkdir()
 frames=[]
 for n,p in enumerate(srcs[:5],1):
  target=dst/f"{n:02d}-historical-real-art-photo-unchanged-QA.jpg"
  shutil.copy2(p,target)
  assert sha(p)==sha(target)
  with Image.open(target) as im:
   im.load()
   assert im.format=='JPEG' and im.size==(1080,1080)
  assert target.stat().st_size<2_000_000
  frames.append(dict(frame=n,source=str(p),file=target.name,
                     source_sha256=sha(p),saved_sha256=sha(target)))
 rows.append(dict(family=fid,product=name,original_JPGs=5,
                  original_source_bytes_unchanged=True,
                  retail_approval="HOLD_MK_BADGE_STOCK_EDITIONS_RIGHTS_VISUAL",
                  frames=frames))
for page in (0,1):
 subset=rows[page*3:(page+1)*3]
 board=Image.new('RGB',(1820,1290),'#f0f0ef')
 d=ImageDraw.Draw(board)
 d.text((20,12),f"v2706 REUSED REAL JPG SOURCES / PAGE {page+1} / NOT RETAIL",font=font,fill='#292929')
 for rowix,rec in enumerate(subset):
  for frame in rec["frames"]:
   p=OUT/rec["family"]/frame["file"]
   with Image.open(p) as im:thumb=im.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
   x=14+(frame["frame"]-1)*361;y=52+rowix*405
   board.paste(thumb,(x,y))
   d.text((x,y+330),rec["family"]+f" / {frame['frame']}",font=font,fill='#292929')
 proof=OUT/f"v2706-review-page-{page+1}.jpg"
 board.save(proof,quality=81,optimize=True)
 (OUT/f"v2706-review-page-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2706","baseline":"v2705",
 "source_commit":"b2b883b86f3e80b7723ccf39b3766dfe6f483da9",
 "six_real_archive_photo_groups":len(rows),"original_photo_JPGs_byte_preserved":30,
 "reencoded_existing_JPGs":0,"additional_product_image_rendered":0,
 "prior_11_approved_product_families_untouched":True,
 "existing_55_public_urls_untouched":True,
 "prior_saved_qa_artifacts_untouched":True,
 "source_license_proven":False,
 "original_MK_badge_verified":False,
 "owned_stock_edition_verified":False,
 "new_retail_approved":0,"final_xlsx_shared":False,
 "families":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"reviewed_product_families":len(rows),"real_JPGs":30,
"source_bytes_preserved":30,"retail_approved":0}))
