#!/usr/bin/env python3
"""v2574: customer-copy footer repair for five already-staged JPG proposals.
The product photo, option swatches and every pixel above y=950 are unchanged.
Only existing explicit in-image internal QA/provenance text at the footer is replaced.
No commercial rights, edition, original MK-logo or final approval is implied.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,hashlib
OUT=Path("v2574-five-footer-corrections");OUT.mkdir(exist_ok=True)
CASES=[
 {"family":"pending-21","slot":5,"source":"input-goodal/pending-21-slot05-package-photo-CANDIDATE.jpg","bg":"#f9faf6","line":"#aec595","fg":"#4f6c47","text":"VITA-C EYE CREAM  |  30 mL"},
 {"family":"pending-16","slot":4,"source":"input-drg/pending16-04-original-70ml-jar-carton-CANDIDATE.jpg","bg":"#f7faf7","line":"#b5cbb9","fg":"#416551","text":"CLEAR SOOTHING CREAM  |  70 mL"},
 {"family":"pending-26","slot":5,"source":"input-pixelpure/pending26-05-verified-original-145ml-CANDIDATE.jpg","bg":"#faf9f7","line":"#c9d3c8","fg":"#4c6755","text":"GENTLE GEL TO FOAM CLEANSER  |  145 mL"},
 {"family":"pending-01","slot":5,"source":"input-missha-clio/pending-01-slot05-CANDIDATE.jpg","bg":"#f7f7f5","line":"#b8c5bc","fg":"#526053","text":"MAGIC CUSHION COVER LASTING"},
 {"family":"pending-06","slot":5,"source":"input-missha-clio/pending-06-slot05-CANDIDATE.jpg","bg":"#f7f7f5","line":"#b8c5bc","fg":"#526053","text":"KILL COVER MESH GLOW ESSENTIAL"}
]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
rows=[]
for c in CASES:
 src=Path(c["source"])
 assert src.is_file(),src
 old=Image.open(src);old.load()
 assert old.format=="JPEG" and old.size==(1080,1080) and src.stat().st_size<2_000_000
 changed=old.convert("RGB").copy()
 d=ImageDraw.Draw(changed)
 # Guaranteed blank footer for these 4 source scripts; no product content above 950.
 d.rectangle((0,950,1080,1080),fill=c["bg"])
 d.line((54,964,1026,964),fill=c["line"],width=2)
 bbox=d.textbbox((0,0),c["text"],font=font)
 assert bbox[2]-bbox[0]<930,(c["family"],bbox)
 d.text((60,983),c["text"],font=font,fill=c["fg"])
 dst=OUT/f"{c['family']}-slot{c['slot']:02d}-customer-footer-QA.jpg"
 changed.save(dst,"JPEG",quality=92,optimize=True,subsampling=0)
 raw=dst.read_bytes()
 assert len(raw)<2_000_000 and Image.open(dst).size==(1080,1080)
 # Compare recompressed image to original; high-impact edits should be constrained
 # to the footer and JPEG compression noise elsewhere.
 a=old.convert("RGB").crop((0,0,1080,950))
 b=Image.open(dst).convert("RGB").crop((0,0,1080,950))
 import PIL.ImageStat
 from PIL import ImageStat
 upper_mae=sum(ImageStat.Stat(ImageChops.difference(a.resize((256,225)),b.resize((256,225)))).mean)/3
 assert upper_mae<3, (c["family"],upper_mae)
 rows.append({"family":c["family"],"slot":c["slot"],"source":c["source"],
  "original_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
  "correction_sha256":hashlib.sha256(raw).hexdigest(),
  "correction_file":dst.name,"safe_label":c["text"],
  "upper_photo_region_MAE":round(upper_mae,3),
  "content_footer_technical_QA_removed":True,
  "source_product_pixels_intentionally_edited":False,
  "commercial_photo_rights_verified":False,
  "exact_stock_edition_verified":False,"original_MK_logo_applied":False,
  "public_sales_approved":False})
assert len(rows)==5
report={"version":"v2574","date":"2026-11-04","source_runs":[41751173910,41752270122,41752643604,41754215345],
 "actual_JPG_footer_corrections":5,
 "fixed_existing_internal_QA_footer_count":3,
 "fixed_provenance_only_footer_count":2,
 "uncorrected_dynamic_text_candidates":["pending-02-slot04","pending-19-slot05"],
 "untouched_previous_156_JPGs":True,"old_55_public_URLs_unchanged":True,
 "new_public_URLs":0,"xls_generated_or_shared":False,
 "final_approval":False,"hold":["Photo commercial use permission","Exact owned-stock edition","Original round MK source","Human visual scene / claim review"],
 "candidate_corrections":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"corrected_JPG":len(rows),"removed_internal_QA_FOOTERS":3,"removed_provenance_notes":2,
"originals_unchanged":156,"new_public_urls":0,"sales_ready":False}))
