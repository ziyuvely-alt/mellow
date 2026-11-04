#!/usr/bin/env python3
"""v2786 correct ONLY 2 visual crop errors from v2785:
- frame04 fragmented source copy intruding at top
- frame05 source headline fragment and opened jar bottom cut
No generative replacement, object editing, false claims, new photos,
published URLs or original QA source changes.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,shutil,base64
QA=Path("qa-review")
OLD=QA/"v2785-goodal-cream-alpha-fiveframe-photo-first-QA"
SOURCES=QA/"v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA"
OUT=QA/"v2786-goodal-cream-alpha-photo-crop-visual-fix-QA"
assert OLD.is_dir() and SOURCES.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
old=json.loads((OLD/"manifest.json").read_text())
src=json.loads((SOURCES/"manifest.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changes={
 4:{"source":SOURCES/src["curated_photos"][2]["file"],
    "crop":(275,448,905,823),
    "filename":"04-fullbleed-cream-hand-texture-no-ad-copy-QA.jpg",
    "reason":"Remove clipped tagline by selecting genuine hand/cream surface pixels"},
 5:{"source":SOURCES/src["curated_photos"][1]["file"],
    "crop":(360,445,1040,1050),
    "filename":"05-fullbleed-open-cream-jar-no-banner-QA.jpg",
    "reason":"Remove clipped results banner; show more real open jar bottom"}
}
frames=[]
for fr in old["frames"]:
 n=fr["slot"]
 if n not in changes:
  p=OLD/fr["file"];dest=OUT/fr["file"]
  shutil.copy2(p,dest)
  assert sha(p)==sha(dest)
  frames.append({**fr,"unchanged_byte_exact":True})
  continue
 conf=changes[n]
 with Image.open(conf["source"]) as image:
  image.load();assert image.format=="JPEG" and image.size==(1080,1080)
  raw=image.convert("RGB").crop(conf["crop"])
  corrected=ImageOps.fit(raw,(1080,1080),method=Image.Resampling.LANCZOS)
 dest=OUT/conf["filename"]
 corrected.save(dest,"JPEG",quality=94,optimize=True,subsampling=0)
 frames.append({"slot":n,"file":dest.name,"role":"REAL_SOURCE_PHOTO_CROP_NO_BANNER",
  "source":str(conf["source"]),"source_crop_xyxy":list(conf["crop"]),
  "correction_reason":conf["reason"],"sha256":sha(dest),
  "new_generated_product_pixels":False,"retail_status":"HOLD"})
for fr in frames:
 p=OUT/fr["file"]
 with Image.open(p) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert p.stat().st_size<2000000
 fr["bytes"]=p.stat().st_size
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
board=Image.new("RGB",(1815,488),"#f1f0ed")
d=ImageDraw.Draw(board)
d.text((15,14),"v2786 GOODAL ALPHA / FIVE TRUE PHOTO FRAMES / 2 TECHNICAL CROP FIXES",font=font,fill="#303030")
for i,fr in enumerate(frames):
 with Image.open(OUT/fr["file"]) as im:
  thumb=im.convert("RGB").resize((336,336),Image.Resampling.LANCZOS)
 xx=15+i*362
 board.paste(thumb,(xx,68))
 d.text((xx,414),f"FRAME {i+1:02d} "+("CROP REVISED" if i+1 in changes else "UNCHANGED"),font=font,fill="#303030")
preview=OUT/"v2786-final-crop-comparison-QA.jpg"
board.save(preview,"JPEG",quality=83,optimize=True)
(OUT/"v2786-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
report={"version":"v2786","family":"pending-19","baseline":"v2785",
 "five_1080x1080_JPGs_saved":True,"unchanged_v2785_sha_identical_frames":[1,2,3],
 "two_source_photo_crop_fixed_frames":[4,5],
 "pixels_synthetic":False,
 "independent_photo_exposures":4,
 "customer_ready_retail_approved":False,
 "old_original_sources_modified":False,
 "old_11_sale_approved_families_unchanged":True,
 "old_55_published_URLs_unchanged":True,
 "photo_rights_verified":False,
 "owned_stock_edition_verified":False,
 "original_MK_logo_available":False,
 "full_photo_frame_claim_and_edge_QA_status":"VISUAL_REVIEW_REQUIRED",
 "no_final_excel_shared":True,
 "frames":frames}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2786","images_saved":len(frames),"changed_only":[4,5],
 "original_JPGs_preserved":3,"sale_approved":0}))
