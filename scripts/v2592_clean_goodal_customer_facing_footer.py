#!/usr/bin/env python3
"""v2592 correct accidentally visible internal stock-QA wording on v2590 Goodal
factual JPG. Only lower footer band is changed. Do not approve, publish, or
regenerate the other 16 QA deltas.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat,ImageChops
import json,hashlib
ROOT=Path("v2592-facts")
OLD=Path("v2592-checkpoint")
OUT=Path("v2592-goodal-customer-facing-copy-cleanup");OUT.mkdir(exist_ok=True)
f=json.loads((ROOT/"manifest.json").read_text())
p=json.loads((OLD/"manifest.json").read_text())
assert f["version"]=="v2590" and p["version"]=="v2591" and p["all_QA_delta_count"]==17
old=ROOT/f["file"];assert old.is_file()
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
assert sha(old)==f["candidate_sha256"]
orig=Image.open(old);orig.load()
assert orig.format=="JPEG" and orig.size==(1080,1080)
new=orig.convert("RGB").copy()
draw=ImageDraw.Draw(new)
# Replace only footer region where internal instruction was accidentally
# rendered. Keep original factual product info above it intact.
draw.rectangle((62,921,1020,1011),fill="#fffefd")
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
draw.text((75,943),"100 mL  |  SERUM MIST",fill="#526954",font=font)
dest=OUT/"pending-20-slot05-fact-only-clean-footer-QA.jpg"
new.save(dest,"JPEG",quality=93,optimize=True,subsampling=0)
assert dest.stat().st_size<2_000_000 and Image.open(dest).size==(1080,1080)
a=orig.convert("RGB").crop((0,0,1080,920)).resize((270,230))
b=Image.open(dest).convert("RGB").crop((0,0,1080,920)).resize((270,230))
mae=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,4)
assert mae<3,mae
assert sha(dest)!=sha(old)
m={"version":"v2592","previous_checkpoint_run":41764248547,
 "old_Goodal_fact_JPG_run":41764148539,"new_candidate_count":1,
 "new_candidate_file":dest.name,"previous_sha256":sha(old),"new_sha256":sha(dest),
 "upper_920px_MAE":mae,"removed_internal_phrase":"Packaging version: confirm with stock.",
 "replacement_text":"100 mL | SERUM MIST",
 "other_16_previous_changes_preserved_without_reupload":True,
 "QA_overlay_count_unchanged":17,
 "human_rights_stock_packaging_logo_visual_final_approval":False,
 "commercial_release_approved":False,"old_public_55_URLs_unchanged":True,
 "xlsx_created_or_shared":False}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"corrected_JPG":1,"original_16_preserved":True,"top_photo_content_MAE":mae,
"new_checkpoint_QA_images":17,"no_public_release":True,"xlsx":False}))
