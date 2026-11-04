#!/usr/bin/env python3
"""v2792 strict patch two CLIO 5g upper-white-margin speckle defects in v2791.

This is not mask-based inpainting. It applies a pure white top strip only where
the source is verified mostly achromatic/light; avoids a third repeat of the
previous flawed text-mask algorithm. Every row beyond top cutoff is pixel-
identical before final JPEG encoding. Eight of ten QA JPGs remain byte-for-byte
unchanged. Original sources, commercial photos and published 55 URLs untouched.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,hashlib,json,shutil,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2791-clio-mini-two-cropped-english-captions-corrected-QA"
OUT=ROOT/"v2792-clio-5g-blank-upper-margin-only-cleanup"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
manifest=json.loads((SRC/"manifest.json").read_text())
assert manifest["version"]=="v2791"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for fam in manifest["family_results"]:
 family=fam["family"]
 destination=OUT/family
 destination.mkdir()
 frame_rows=[]
 for entry in fam["frames"]:
  slot=entry["slot"];source=SRC/family/entry["filename"]
  assert source.is_file()
  if family=="pending-04" and slot in (1,2):
   with Image.open(source) as photo:
    photo.load();assert photo.size==(1080,1080) and photo.format=="JPEG"
    arr=np.asarray(photo.convert("RGB")).copy()
   cutoff=155
   upper=arr[:cutoff,30:1050,:].astype(np.int16)
   spread=upper.max(axis=2)-upper.min(axis=2)
   chromatic=np.logical_and(spread>40,upper.mean(axis=2)<247)
   share=float(np.mean(chromatic))
   if share>0.025:raise RuntimeError(f"Frame{slot} has too much non-white chromatic source object inside top border: {share:.5f}")
   # Remove only top clipped text remnants. Product case, puff and fingers
   # are below this upper border, and are restored exactly from old pixels.
   fix=arr.copy()
   fix[:cutoff,:,:]=255
   assert np.array_equal(fix[cutoff:],arr[cutoff:])
   outname=f"{slot:02d}-clean-white-top-border-no-truncated-english-QA.jpg"
   path=destination/outname
   Image.fromarray(fix).save(path,"JPEG",quality=94,optimize=True,subsampling=0)
   row={"slot":slot,"file":path.name,"change":"WHITEN_ONLY_0_TO_155_UPPER_EMPTY_BORDER",
        "previous_sha256":sha(source),"sha256":sha(path),
        "top_margin_chromatic_fraction":round(share,7),
        "product_pixels_unchanged_prior_encoding":True,
        "all_other_existing_source_assets_untouched":True}
  else:
   path=destination/source.name
   shutil.copy2(source,path)
   assert sha(source)==sha(path)
   row={"slot":slot,"file":path.name,"change":"PRESERVED_EXACT_SOURCE_BYTES",
        "sha256":sha(path)}
  with Image.open(path) as test:
   test.load();assert test.size==(1080,1080) and test.format=="JPEG"
  assert path.stat().st_size<2000000
  row["size_bytes"]=path.stat().st_size
  frame_rows.append(row)
 rows.append({"family":family,"frames":frame_rows})
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
for family in rows:
 board=Image.new("RGB",(1830,485),"#f0f0ef")
 draw=ImageDraw.Draw(board)
 draw.text((15,15),f"v2792 {family['family']} / 5 AUTHENTIC PHOTO QA FRAMES / NO CUSTOMER RELEASE",font=font,fill="#333333")
 for i,frame in enumerate(family["frames"]):
  with Image.open(OUT/family["family"]/frame["file"]) as image:
   tile=image.convert("RGB").resize((335,335),Image.Resampling.LANCZOS)
  x=15+362*i
  board.paste(tile,(x,66))
  draw.text((x,418),f"FRAME {i+1} | "+("TOP FIX" if frame["change"].startswith("WHITEN") else "PRESERVED"),font=font,fill="#303030")
 p=OUT/f"v2792-{family['family']}-contact.jpg"
 board.save(p,"JPEG",quality=83,optimize=True)
 (OUT/f"v2792-{family['family']}-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
report={
 "version":"v2792","baseline":"v2791","QA_product_families":2,
 "total_1080_JPG_files":10,"newly_fixed_CLIO_slots":[1,2],
 "other_previous_QA_frames_sha_preserved":8,
 "reason_previous_v2790_failed":"Inpainting modified pixels outside approved top header region; stopped and abandoned mask method",
 "strategy":"Opaque-white replacement only for <=155px verified empty top border, original product body pixels not changed before jpeg encoding",
 "successful_commercial_release":False,
 "unverified_photo_rights_still_held":True,
 "physical_owned_stock_option_generation_verified":False,
 "genuine_original_MK_logo_available":False,
 "existing_11_approved_families_untouched":True,
 "existing_55_public_photo_URLs_untouched":True,
 "older_v2789_and_v2791_JPG_sources_untouched":True,
 "final_spreadsheet_shared":False,
 "families":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2792","files":10,"changed_CLIO":2,
 "unchanged_other":8,"sales_approved":0}))
